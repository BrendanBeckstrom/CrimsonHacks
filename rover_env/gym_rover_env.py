import os, socket, struct, time
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import cv2
from ai.perception.seg_stub import obstacle_risk

HOST = os.getenv('ROVER_HOST', '127.0.0.1')
PORT = int(os.getenv('ROVER_PORT', '5555'))
FRAME_W = int(os.getenv('FRAME_W', '160'))
FRAME_H = int(os.getenv('FRAME_H', '120'))

class RoverEnv(gym.Env):
    metadata = {"render_modes": ["rgb_array"]}
    def __init__(self, discrete=True, latency_ms=0):
        super().__init__()
        self.discrete = discrete
        self.latency_ms = latency_ms
        self.sock = None
        self.observation_space = spaces.Box(low=0, high=255, shape=(FRAME_H, FRAME_W, 3), dtype=np.uint8)
        if discrete:
            self.action_space = spaces.Discrete(5)  # hard-left, left, fwd, right, hard-right
        else:
            self.action_space = spaces.Box(low=np.array([-4.0, -4.0]), high=np.array([4.0, 4.0]), dtype=np.float32)
        self.prev_progress = 0.0
        self.energy = 0.0
        self.collided = False

    def _connect(self):
        if self.sock: return
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        self.sock = s

    def _send_cmd(self, cmd:str):
        payload = cmd.encode('utf-8')
        self.sock.sendall(struct.pack('!I', len(payload)) + payload)

    def _get_frame(self):
        self._send_cmd('GET_FRAME')
        hdr = self.sock.recv(12)
        h, w, c = struct.unpack('!III', hdr)
        buf = b''
        expected = h*w*c
        while len(buf) < expected:
            buf += self.sock.recv(expected - len(buf))
        arr = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, c))
        return arr

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._connect()
        self._send_cmd('RESET')
        self.prev_progress = 0.0
        self.energy = 0.0
        self.collided = False
        frame = self._get_frame()
        return frame, {}

    def step(self, action):
        if self.discrete:
            # map to wheel velocities
            maps = {
                0: (-3.0,  3.0),
                1: ( 0.5,  2.0),
                2: ( 2.5,  2.5),
                3: ( 2.0,  0.5),
                4: ( 3.0, -3.0),
            }
            vl, vr = maps[int(action)]
        else:
            vl, vr = float(action[0]), float(action[1])

        if self.latency_ms > 0:
            time.sleep(self.latency_ms/1000.0)
        self._send_cmd(f"SET_V {vl} {vr}")
        frame = self._get_frame()

        # Perception -> risk
        l, c, r = obstacle_risk(frame)
        dprog = self._forward_progress(c)  # heuristic using center risk
        self.energy += abs(vl) + abs(vr)

        # TODO: collision heuristic (e.g., strong red mask or optical flow stall)
        collided = (c > 0.9)
        self.collided = self.collided or collided

        reward  = 5.0 * dprog
        reward -= 0.02 * (abs(vl) + abs(vr))
        reward -= 20.0 if collided else 0.0
        reward -= 0.01

        done = False  # set true on goal/collision timeout (left as exercise)
        info = dict(l=l, c=c, r=r, dprog=dprog, collided=collided)
        return frame, reward, done, False, info

    def _forward_progress(self, center_risk):
        # Simple: less center risk => assume open path => positive progress
        prog = max(0.0, 1.0 - center_risk)
        dp = prog - self.prev_progress
        self.prev_progress = prog
        return max(-0.1, dp)

    def render(self):
        return None
