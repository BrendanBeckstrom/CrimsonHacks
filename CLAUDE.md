# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Mars rover simulation and reinforcement learning project that combines Webots robotics simulation with Gymnasium environments for training AI agents. The system allows both manual teleoperation and autonomous navigation using PPO (Proximal Policy Optimization).

## Architecture

### Core Components

1. **Webots Simulation Layer** (`webots/`)
   - `controllers/rover_controller/rover_controller.py`: Reflex-based autonomous controller that uses edge detection for hazard avoidance. Controls 6-wheel differential drive (3 left, 3 right wheels). Implements simple reactive steering based on left/center/right risk zones.
   - `controllers/world_supervisor/world_supervisor.py`: Supervisor that dynamically spawns rocks/obstacles at simulation start. Removes old rocks and creates new random obstacle fields.
   - `worlds/sojourner.wbt`: Webots world file defining the Mars terrain and Sojourner rover

2. **Gymnasium Environment** (`rover_env/`)
   - `gym_rover_env.py`: Custom Gym environment (`RoverEnv`) that bridges Webots simulation with RL frameworks
   - Connects to simulation via TCP socket (default: localhost:5555)
   - Supports both discrete (5 actions) and continuous (2D wheel velocities) action spaces
   - Observation space: 160x120 RGB camera frames
   - Reward function: progress reward + energy penalty + collision penalty
   - Uses `obstacle_risk()` from perception module to compute risk scores

3. **AI/Perception** (`ai/`)
   - `agents/train_ppo.py`: Training script using stable-baselines3 PPO with CNN policy
   - `perception/seg_stub.py`: Simple edge-based obstacle risk estimator. Divides camera view into left/center/right zones and returns risk score for each (0-1 scale based on edge density). This is a placeholder for more sophisticated semantic segmentation.

4. **Applications** (`apps/`)
   - `teleop.py`: Pygame-based manual control interface. Keyboard controls (WASD/arrows + Q/E for hard turns). Connects to rover via socket protocol.
   - `hud.py`: Streamlit real-time visualization dashboard showing camera feed and left/center/right risk bars

### Communication Protocol

The system uses a simple TCP socket protocol between the Gym environment/apps and Webots:
- Commands: `RESET`, `GET_FRAME`, `SET_V <left_vel> <right_vel>`
- Frame format: 12-byte header (height, width, channels as network-order ints) + raw BGR pixel data
- Default connection: `ROVER_HOST=127.0.0.1`, `ROVER_PORT=5555`

### Data Flow

```
Webots Simulation (rover_controller)
    ↕ (TCP socket)
RoverEnv / Teleop / HUD
    ↓ (camera frames)
obstacle_risk() perception
    ↓ (risk scores)
PPO Agent / Reward Calculation
```

## Development Commands

### Running the Simulation

```bash
# Start Webots simulation (macOS/Linux)
./scripts/run_webots.sh

# Windows
./scripts/run_webots.ps1
```

Note: Webots must be installed and in PATH. Edit the script to set `WEBOTS_HOME` if needed.

### Training RL Agent

```bash
# Train PPO agent (from project root)
python -m ai.agents.train_ppo --timesteps 10000

# Saved model location: ./ppo_rover.zip
```

The training script expects the Webots simulation to be running with a socket server active.

### Running Applications

```bash
# Manual teleoperation
python -m apps.teleop [--latency_ms 0]

# Live camera/risk visualization
streamlit run apps/hud.py
```

### Environment Variables

- `ROVER_HOST`: Rover socket host (default: 127.0.0.1)
- `ROVER_PORT`: Rover socket port (default: 5555)
- `FRAME_W`: Camera frame width (default: 160)
- `FRAME_H`: Camera frame height (default: 120)

## Python Environment

This project uses Python 3.x with a virtual environment at `.venv/`. Key dependencies:
- `webots` (Cyberbotics robotics simulator)
- `gymnasium` (RL environment interface)
- `stable-baselines3` (PPO implementation)
- `opencv-python` (image processing)
- `pygame` (teleoperation UI)
- `streamlit` (HUD dashboard)
- `numpy`

Activate the virtual environment before running Python code:
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

## Key Implementation Details

### Rover Control

The Sojourner rover uses differential drive with 6 wheels (3 per side). The rover_controller maps wheel names explicitly:
- Left: `FrontLeftWheel`, `MiddleLeftWheel`, `BackLeftWheel`
- Right: `FrontRightWheel`, `MiddleRightWheel`, `BackRightWheel`

Velocity mode is enabled by setting position to infinity, then setting velocities with 80% of max velocity as headroom.

### Perception Stub

The current `obstacle_risk()` function is intentionally simple (edge detection + zone averaging). It's designed to be replaced with proper semantic segmentation or depth-based obstacle detection. Returns 3 floats representing risk in left/center/right zones.

### Reward Shaping

The Gym environment reward function (rover_env/gym_rover_env.py:88-91):
- +5.0 × forward_progress (based on decreasing center risk)
- -0.02 × total wheel velocities (energy penalty)
- -20.0 for collisions (center risk > 0.9)
- -0.01 constant step penalty

### Discrete Action Mapping

The 5 discrete actions map to wheel velocities (rover_env/gym_rover_env.py:63-69):
- 0: Hard left (-3.0, 3.0)
- 1: Soft left (0.5, 2.0)
- 2: Forward (2.5, 2.5)
- 3: Soft right (2.0, 0.5)
- 4: Hard right (3.0, -3.0)
