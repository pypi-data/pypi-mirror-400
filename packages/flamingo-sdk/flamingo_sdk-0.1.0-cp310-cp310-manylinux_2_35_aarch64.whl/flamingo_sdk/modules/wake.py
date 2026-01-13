import math
from flamingo_sdk import *


def wake(
    robot: Robot,
    T_PLAN_MIN: float = 4.0,
    T_PLAN_MAX: float = 5.0,
    MAX_DURATION_S: float = 10.0
):
    # ===== Tunables =====
    FINAL_Kp = [15, 15, 15, 15, 15, 15, 0, 0]
    FINAL_Kd = [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.25, 0.25]
    KP_BOSST = 1.5  # maximum: kp_final * KP_BOOST

    THRESHOLD_RAD = 0.075
    VEL_THRESHOLD_RAD_S = 0.15

    HZ = 50
    dt = 1.0 / HZ

    # (Strategy) Start more aggressively for small error/velocity; start more conservatively for large error/velocity.
    START_FRAC_FAST = 0.20
    START_FRAC_SLOW = 0.10

    # ===== Load / stiction compensation =====
    NEAR_GOAL_WINDOW_RAD = 0.20   # In this window (near the origin), sticking due to friction/load occurs frequently.
    MIN_TRACK_ERR_RAD = 0.02      # Force a minimum tracking error so the PD controller produces at least some torque.
    STUCK_VEL_EPS = 0.02          # Threshold for "near-zero" velocity.
    STUCK_POS_EPS = 0.0015        # Threshold for "near-zero" motion (Δq between frames).
    STUCK_TIME_S = 0.40           # Consider it stuck if the above persists for at least this long.

    KP_BOOST_MULT = 4.0           # Kp multiplier when stuck.
    KD_BOOST_MULT = 1.0           # Kd multiplier when stuck (often does not need large changes).

    KICK_GAIN = 0.5  # Scale factor applied to error (tune within ~0.3 to 0.8).
    KICK_MIN_RAD = 0.02  # Prevent kicks that are too small.
    KICK_MAX_RAD = 0.06  # Prevent kicks that are too large.

    # Safety caps (adjust to match your hardware/environment).
    KP_ABS_MAX = [25, 25, 25, 25, 25, 25, 0, 0]
    KD_ABS_MAX = [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.55, 0.55]

    # ===== Abort if stuck persists under high predicted torque =====
    TORQUE_ABORT_NM = 10.0        # "High torque" threshold (predicted), in N·m
    TORQUE_ABORT_TIME_S = 3    # Must persist this long before aborting

    # ---- sanity ----
    if T_PLAN_MIN > T_PLAN_MAX:
        T_PLAN_MIN, T_PLAN_MAX = T_PLAN_MAX, T_PLAN_MIN

    # ===== Read original gains =====
    gains = robot.get_gains()
    if isinstance(gains, dict):
        original_kp = list(gains.get("kp", []))
        original_kd = list(gains.get("kd", []))
    else:
        original_kp, original_kd = gains
        original_kp, original_kd = list(original_kp), list(original_kd)

    N = min(len(original_kp), len(original_kd))
    final_kp = (FINAL_Kp + [0.0] * N)[:N]
    final_kd = (FINAL_Kd + [0.0] * N)[:N]

    # ===== Snapshot initial state =====
    start_obs = robot.get_obs()
    q_init = list(start_obs.get("dof_pos", []))
    qd_init = list(start_obs.get("dof_vel", []))

    n_arm = 6
    q0 = [(q_init[i] if i < len(q_init) else 0.0) for i in range(n_arm)]
    v0 = [(qd_init[i] if i < len(qd_init) else 0.0) for i in range(n_arm)]
    wheel_v0 = [qd_init[6], qd_init[7]] if len(qd_init) >= 8 else [0.0, 0.0]

    qf = [0.0] * n_arm

    # ===== Plan duration strategy =====
    max_abs_err0 = max(abs(q0[i] - qf[i]) for i in range(n_arm)) if n_arm > 0 else 0.0
    max_abs_vel0 = max(abs(v0[i]) for i in range(n_arm)) if n_arm > 0 else 0.0

    ERR_SAT_RAD = max(THRESHOLD_RAD * 10.0, THRESHOLD_RAD)
    VEL_SAT_RAD_S = max(VEL_THRESHOLD_RAD_S * 10.0, VEL_THRESHOLD_RAD_S)

    ratio_err = max(0.0, min(1.0, max_abs_err0 / ERR_SAT_RAD))
    ratio_vel = max(0.0, min(1.0, max_abs_vel0 / VEL_SAT_RAD_S))
    ratio = max(ratio_err, ratio_vel)

    T_plan = T_PLAN_MIN + (T_PLAN_MAX - T_PLAN_MIN) * ratio

    if MAX_DURATION_S < T_plan:
        MAX_DURATION_S = T_plan + 1.0

    start_frac = START_FRAC_FAST + (START_FRAC_SLOW - START_FRAC_FAST) * ratio

    # If starting near the origin: starting with reduced gains can increase stiction risk → allow immediate final gains.
    near_origin_start = (max_abs_err0 < NEAR_GOAL_WINDOW_RAD) and (max_abs_vel0 < 0.05)
    if near_origin_start:
        start_frac = max(start_frac, 1.0)

    # ===== Precompute quintic trajectory coeffs =====
    coeffs = []
    T = T_plan
    for i in range(n_arm):
        a0 = q0[i]
        a1 = v0[i]
        a2 = 0.0
        dq = qf[i] - q0[i]
        a3 = (10.0 * dq - 6.0 * v0[i] * T) / (T**3)
        a4 = (15.0 * (-dq) + 8.0 * v0[i] * T) / (T**4)
        a5 = (6.0 * dq - 3.0 * v0[i] * T) / (T**5)
        coeffs.append((a0, a1, a2, a3, a4, a5))

    def eval_quintic(c, t):
        a0, a1, a2, a3, a4, a5 = c
        return a0 + a1*t + a2*(t**2) + a3*(t**3) + a4*(t**4) + a5*(t**5)

    def eval_quintic_dot(c, t):
        a0, a1, a2, a3, a4, a5 = c
        return a1 + 2.0*a2*t + 3.0*a3*(t**2) + 4.0*a4*(t**3) + 5.0*a5*(t**4)

    # ===== Safety-first gain logic =====
    start_kp = []
    start_kd = []
    for i in range(N):
        cap_kp = final_kp[i] * start_frac
        cap_kd = final_kd[i] * start_frac
        start_kp.append(min(original_kp[i], cap_kp))
        start_kd.append(min(original_kd[i], cap_kd))

    robot.set_gains(kp=start_kp, kd=start_kd)

    elapsed_s = 0.0

    # State for stiction/stuck detection
    stuck_t = [0.0] * n_arm
    q_prev = q0[:]  # previous q for Δq

    # State for aborting under high predicted torque
    high_tau_t = [0.0] * n_arm

    @control_rate(robot, hz=HZ)
    def wake_loop():
        nonlocal elapsed_s, stuck_t, q_prev, high_tau_t

        obs = robot.get_obs()
        q_now = list(obs.get("dof_pos", []))
        qd_now = list(obs.get("dof_vel", []))

        alpha = max(0.0, min(1.0, elapsed_s / T_plan))
        s = 10*alpha**3 - 15*alpha**4 + 6*alpha**5

        t = min(T_plan, elapsed_s)
        q_cmd = [eval_quintic(coeffs[i], t) for i in range(n_arm)]
        qd_cmd = [eval_quintic_dot(coeffs[i], t) for i in range(n_arm)]
        wheel_v_cmd = [(1.0 - s) * wheel_v0[0], (1.0 - s) * wheel_v0[1]]

        kp_cmd = [start_kp[i] + s * (final_kp[i] - start_kp[i]) for i in range(N)]
        kd_cmd = [start_kd[i] + s * (final_kd[i] - start_kd[i]) for i in range(N)]

        # ===== Compensation for cases where torque is insufficient near the origin =====
        for i in range(n_arm):
            qi = q_now[i] if i < len(q_now) else 0.0
            qdi = qd_now[i] if i < len(qd_now) else 0.0

            e_goal = qf[i] - qi
            abs_e_goal = abs(e_goal)

            # 1) Near the origin but still off-target: force a minimum error to ensure sufficient PD torque.
            if (abs_e_goal < NEAR_GOAL_WINDOW_RAD) and (abs_e_goal > THRESHOLD_RAD):
                e_track = q_cmd[i] - qi
                if abs(e_track) < MIN_TRACK_ERR_RAD:
                    q_cmd[i] = qi + math.copysign(MIN_TRACK_ERR_RAD, e_goal)

                # In the near-goal region, a small Kp boost can help overcome load-induced stiction.
                kp_cmd[i] = min(KP_ABS_MAX[i], kp_cmd[i] * KP_BOSST)

            # 2) Stuck detection: if Δq is small, velocity is small, and goal error remains, accumulate stuck timer.
            moved = abs(qi - q_prev[i])
            if (abs_e_goal > THRESHOLD_RAD) and (moved < STUCK_POS_EPS) and (abs(qdi) < STUCK_VEL_EPS):
                stuck_t[i] += dt
            else:
                stuck_t[i] = 0.0

            # 3) If stuck for long enough: apply a kick and boost Kp (and Kd if needed) to break static friction.
            if stuck_t[i] >= STUCK_TIME_S:
                kick = max(KICK_MIN_RAD, min(KICK_MAX_RAD, KICK_GAIN * abs_e_goal))
                q_cmd[i] = qi + math.copysign(kick, e_goal)
                kp_cmd[i] = min(KP_ABS_MAX[i], kp_cmd[i] * KP_BOOST_MULT)
                kd_cmd[i] = min(KD_ABS_MAX[i], kd_cmd[i] * KD_BOOST_MULT)

            # 4) If still stuck under high (predicted) torque demand, abort/stop (PD-only prediction).
            e = q_cmd[i] - qi
            edot = (qd_cmd[i] - qdi)
            tau_pred = kp_cmd[i] * e + kd_cmd[i] * edot

            if (stuck_t[i] >= STUCK_TIME_S) and (abs(tau_pred) >= TORQUE_ABORT_NM):
                high_tau_t[i] += dt
            else:
                high_tau_t[i] = 0.0

            if high_tau_t[i] >= TORQUE_ABORT_TIME_S:
                # Hold current arm pose and stop wheels before aborting.
                hold_action = [
                    (q_now[j] if j < len(q_now) else 0.0) for j in range(n_arm)
                ] + [0.0, 0.0]
                robot.do_action(action=hold_action, torque_ctrl=False)
                raise RuntimeError(
                    f"wake aborted: joint {i} stuck under high predicted torque "
                    f"(|tau|={abs(tau_pred):.1f} N·m)"
                )

        robot.set_gains(kp=kp_cmd, kd=kd_cmd)

        action = q_cmd + wheel_v_cmd
        robot.do_action(action=action, torque_ctrl=False)

        # ===== Termination conditions =====
        q_err = []
        qd_err = []
        for i in range(n_arm):
            qi = q_now[i] if i < len(q_now) else 0.0
            qdi = qd_now[i] if i < len(qd_now) else 0.0
            q_err.append(qi - qf[i])
            qd_err.append(qdi)

        max_abs_err = max(abs(x) for x in q_err) if q_err else 0.0
        max_abs_vel = max(abs(x) for x in qd_err) if qd_err else 0.0

        if elapsed_s >= MAX_DURATION_S:
            raise RuntimeError("wake failed: q did not reach threshold within timeout")

        if elapsed_s >= T_plan and (max_abs_err < THRESHOLD_RAD) and (max_abs_vel < VEL_THRESHOLD_RAD_S):
            robot.set_gains(kp=final_kp, kd=final_kd)
            return True

        # Update for stuck detection
        for i in range(n_arm):
            q_prev[i] = (q_now[i] if i < len(q_now) else q_prev[i])

        elapsed_s += dt

    wake_loop()
    return
