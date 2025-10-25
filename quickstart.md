# CrimsonHacks Rover - Quickstart Guide

Get started with the Mars rover simulation and reinforcement learning project in minutes!

## Prerequisites

### 1. Install Webots

Download and install Webots (free, open-source robotics simulator):
- **Official Website**: https://cyberbotics.com/
- **macOS**: Install Webots.app to `/Applications/`
- **Linux**: Follow installation instructions for your distribution
- **Windows**: Run the installer

After installation, add Webots to your PATH:

**macOS:**
```bash
export WEBOTS_HOME="/Applications/Webots.app/Contents/MacOS"
export PATH="$WEBOTS_HOME:$PATH"
```
Add these lines to your `~/.zshrc` or `~/.bash_profile` to make them permanent.

**Linux:**
```bash
export PATH="/usr/local/webots:$PATH"
```

**Windows:**
Add Webots installation directory to your system PATH environment variable.

### 2. Install Python

- **Python 3.8+** is required
- Check your version: `python3 --version`

## Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd CrimsonHacks
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv .venv
```

Activate the virtual environment:

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install webots gymnasium stable-baselines3 opencv-python pygame streamlit numpy
```

### Step 4: Verify Installation

Check that Webots is accessible:
```bash
webots --version
```

If this fails, review the PATH setup in Prerequisites.

## Quick Start

### Option A: Run Autonomous Rover (Reflex Controller)

This runs the rover with simple obstacle avoidance using edge detection.

1. **Start the simulation:**
   ```bash
   ./scripts/run_webots.sh
   ```

   The Webots GUI will open and start the simulation. You should see:
   - A Mars-like terrain
   - The Sojourner rover
   - Randomly scattered rocks (obstacles)
   - The rover autonomously navigating and avoiding obstacles

2. **Watch the console output** for risk scores:
   ```
   [risk] L=0.123 C=0.045 R=0.089 -> vl=2.50 vr=2.50
   ```
   - L/C/R = left/center/right obstacle risk (0-1 scale)
   - vl/vr = left/right wheel velocities

### Option B: Manual Teleoperation

Control the rover yourself using keyboard controls.

1. **Start Webots** (if not already running):
   ```bash
   ./scripts/run_webots.sh
   ```

2. **In a new terminal**, activate the virtual environment and run teleop:
   ```bash
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   python -m apps.teleop
   ```

3. **Control the rover:**
   - `W` / `↑` - Forward
   - `A` / `←` - Turn left
   - `D` / `→` - Turn right
   - `Q` - Hard left turn (pivot)
   - `E` - Hard right turn (pivot)
   - `Space` / `S` / `↓` - Stop
   - `ESC` / `X` - Quit

### Option C: View Live Camera Feed + Risk Visualization

See what the rover sees and monitor obstacle detection in real-time.

1. **Start Webots** (if not already running)

2. **Switch the rover to a network-controlled mode** (if needed - this depends on your Webots controller setup)

3. **In a new terminal**, run the HUD:
   ```bash
   source .venv/bin/activate
   streamlit run apps/hud.py
   ```

4. **Open your browser** to the URL shown (usually http://localhost:8501)

You'll see:
- Left column: Live camera feed from the rover
- Right column: Bar chart showing left/center/right obstacle risk

## Next Steps

### Train Your Own AI Agent

Once you're comfortable with the simulation, train a reinforcement learning agent:

```bash
# Make sure Webots is running
python -m ai.agents.train_ppo --timesteps 10000
```

This will:
- Connect to the running Webots simulation
- Train a PPO agent using camera images as input
- Save the trained model to `ppo_rover.zip`

Training parameters:
- `--timesteps`: Number of training steps (default: 10000)
- For better results, use 50,000-100,000+ timesteps

### Customize the Environment

1. **Adjust obstacle density**: Edit `webots/controllers/world_supervisor/world_supervisor.py`
   - Change `ROCK_COUNT` (default: 40)

2. **Modify reward function**: Edit `rover_env/gym_rover_env.py`
   - Adjust reward weights at lines 88-91

3. **Improve perception**: Replace `ai/perception/seg_stub.py` with:
   - Semantic segmentation models
   - Depth-based obstacle detection
   - ML-based rock classification

## Troubleshooting

### "webots: command not found"

Webots is not in your PATH. Add it manually:
```bash
export PATH="/Applications/Webots.app/Contents/MacOS:$PATH"  # macOS
```

### "Connection refused" when running teleop/HUD

The Webots simulation isn't running or isn't listening on the socket. Make sure:
1. Webots is running with the correct world file
2. The rover_controller has initialized the socket server
3. Check `ROVER_HOST` and `ROVER_PORT` environment variables match

### Python import errors

Activate the virtual environment:
```bash
source .venv/bin/activate
```

Then reinstall dependencies:
```bash
pip install webots gymnasium stable-baselines3 opencv-python pygame streamlit numpy
```

### Rover doesn't move

1. Check that motors are properly initialized in Webots console
2. Verify wheel names match in `rover_controller.py`
3. Try resetting the simulation (Ctrl+Shift+T in Webots)

## Environment Variables

Customize behavior with environment variables:

```bash
export ROVER_HOST=127.0.0.1      # Rover socket host
export ROVER_PORT=5555           # Rover socket port
export FRAME_W=160               # Camera width
export FRAME_H=120               # Camera height
```

## What's Next?

- **Read CLAUDE.md** for detailed architecture information
- **Experiment with hyperparameters** in the PPO training script
- **Build your own perception module** to replace the stub
- **Create custom Webots worlds** with different terrains
- **Implement goal-seeking behavior** (currently just obstacle avoidance)

## Need Help?

- Check the console output for error messages
- Review the code in the relevant module (see CLAUDE.md for architecture)
- Ensure all dependencies are installed correctly
- Verify Webots version compatibility

Happy roving! 🚀🔴
