from controller import Robot, Camera, Motor
import numpy as np
import cv2

TIME_STEP = 64

def clip(x, lo, hi):
    return max(lo, min(hi, x))

def enable_camera(robot, timestep):
    cam = None
    for i in range(robot.getNumberOfDevices()):
        dev = robot.getDeviceByIndex(i)
        if isinstance(dev, Camera):
            cam = dev
            break
    if cam:
        cam.enable(timestep)
        print(f"[ctrl] Camera: {cam.getName()} {cam.getWidth()}x{cam.getHeight()}", flush=True)
    else:
        print("[ctrl] WARNING: no camera found", flush=True)
    return cam

def get_bgr(cam):
    img = cam.getImage()
    w, h = cam.getWidth(), cam.getHeight()
    # Webots camera buffer is BGRA; convert to BGR
    rgba = np.frombuffer(img, dtype=np.uint8).reshape((h, w, 4))
    return rgba[:, :, :3]  # BGR already (BGRA without alpha)

def hazard_mask(bgr):
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=2)
    # binary mask
    _, mask = cv2.threshold(edges, 1, 255, cv2.THRESH_BINARY)
    # remove tiny blobs
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = np.zeros_like(mask)
    for c in cnts:
        if cv2.contourArea(c) > 150:  # tune threshold
            cv2.drawContours(out, [c], -1, 255, -1)
    return out  # uint8 {0,255}

def main():
    print("[rover_controller] reflex hazard avoider", flush=True)
    robot = Robot()

    # ----- Wheels: explicit Sojourner mapping (6 wheels) -----
    name_left  = ["FrontLeftWheel", "MiddleLeftWheel", "BackLeftWheel"]
    name_right = ["FrontRightWheel", "MiddleRightWheel", "BackRightWheel"]

    left, right = [], []
    for i in range(robot.getNumberOfDevices()):
        dev = robot.getDeviceByIndex(i)
        if isinstance(dev, Motor):
            n = dev.getName()
            if n in name_left + name_right:
                dev.setPosition(float('inf'))  # velocity control mode
                dev.setVelocity(0.0)
                (left if n in name_left else right).append(dev)

    maxL = [m.getMaxVelocity() for m in left]
    maxR = [m.getMaxVelocity() for m in right]
    print(f"[ctrl] L wheels: {[m.getName() for m in left]} max={maxL}", flush=True)
    print(f"[ctrl] R wheels: {[m.getName() for m in right]} max={maxR}", flush=True)

    def set_left(v):
        for m, mv in zip(left, maxL):
            m.setVelocity(clip(v, -0.8*mv, 0.8*mv))  # 80% headroom
    def set_right(v):
        for m, mv in zip(right, maxR):
            m.setVelocity(clip(v, -0.8*mv, 0.8*mv))

    # ----- Camera -----
    cam = enable_camera(robot, TIME_STEP)

    # ----- Reflex params -----
    FWD = 0.42                 # safe forward speed (<= ~0.48 from your max 0.6)
    TURN = 0.32                # pivot speed
    RISK_TURN_THRESHOLD = 0.08 # fraction of pixels considered "risky" to trigger a turn
    CENTER_BIAS = 0.6          # prefer clearing center before going straight again

    t = 0.0
    while robot.step(TIME_STEP) != -1:
        t += TIME_STEP / 1000.0

        # default: go straight
        vl, vr = FWD, FWD

        if cam:
            bgr = get_bgr(cam)
            mask = hazard_mask(bgr)

            # compute risk in left/center/right thirds
            h, w = mask.shape
            third = w // 3
            L = np.count_nonzero(mask[:, :third])          / (h*third)
            C = np.count_nonzero(mask[:, third:2*third])   / (h*third)
            R = np.count_nonzero(mask[:, 2*third:])        / (h*(w-2*third))

            # Reflex steering:
            # 1) if center is risky, slow/turn more aggressively
            if C > RISK_TURN_THRESHOLD * CENTER_BIAS:
                if L > R:  # obstacle more on left-center -> turn right
                    vl, vr = +TURN, -TURN
                else:
                    vl, vr = -TURN, +TURN
            else:
                # 2) if side is risky, gentle steer away
                if L > RISK_TURN_THRESHOLD and L > R:
                    vl, vr = +FWD*0.6, +FWD  # drift right
                elif R > RISK_TURN_THRESHOLD and R > L:
                    vl, vr = +FWD, +FWD*0.6  # drift left
                else:
                    vl, vr = FWD, FWD

            if int(t*2) % 10 == 0:  # occasional log (every ~5s)
                print(f"[risk] L={L:.3f} C={C:.3f} R={R:.3f} -> vl={vl:.2f} vr={vr:.2f}", flush=True)

        # apply clamped velocities
        set_left(vl)
        set_right(vr)

if __name__ == "__main__":
    main()
