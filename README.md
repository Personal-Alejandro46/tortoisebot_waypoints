# Tortoisebot Waypoints — Action Server

ROS action server that navigates the Tortoisebot to a 2D waypoint in Gazebo simulation. The robot corrects its yaw first, then moves in a straight line until it reaches the target position within a 5 cm tolerance.

---

## Requirements

- ROS Noetic
- Gazebo
- `tortoisebot_gazebo` and `tortoisebot_waypoints` packages built in `~/simulation_ws`

---

## Launch the Simulation

Open a terminal and run:

```bash
source /opt/ros/noetic/setup.bash
source ~/simulation_ws/devel/setup.bash
roslaunch tortoisebot_gazebo tortoisebot_playground.launch
```

Wait until Gazebo finishes loading before proceeding.

---

## Launch the Action Server

Open a second terminal and run:

```bash
source /opt/ros/noetic/setup.bash
cd ~/simulation_ws && catkin_make && source devel/setup.bash
rosrun tortoisebot_waypoints tortoisebot_action_server.py
```

You should see:

```
[INFO] Action server started
```

---

## Running the Tests

The test file is located at `test/waypoints_test.py`. It sends a single goal to the action server and verifies two conditions:

- `test_end_position` — robot reached within 0.1 m of the target
- `test_end_yaw` — robot is oriented toward the target within 15°

Run with:

```bash
rostest tortoisebot_waypoints waypoints_test.test
```

---

## How to Test — PASS Condition

In `test/waypoints_test.py`, set the target to coordinates the robot can reach:

```python
TARGET_X = -0.465
TARGET_Y = 0.34
```

The robot starts at `(0, 0)`, navigates to the target, and both tests should pass.

Expected output:

```
[ROSTEST] test_end_position ... ok
[ROSTEST] test_end_yaw      ... ok
```

---

## How to Test — FAIL Condition

Change the target to coordinates outside the simulation environment:

```python
TARGET_X = 99.0
TARGET_Y = 99.0
```

The action server will wait for `60 seconds` (the timeout defined in the test) and then the result will be collected without the robot having reached the goal. Both tests will fail:

```
[ROSTEST] test_end_position ... FAIL
[ROSTEST] test_end_yaw      ... FAIL
```

---

## Known Limitations

The current action server uses a simple bang-bang controller with fixed velocities:

- Angular velocity is always `±0.65 rad/s` regardless of yaw error magnitude
- Linear velocity is always `0.6 m/s` regardless of remaining distance
- The `while` loop exits on position only — yaw is not checked as an exit condition

This means the robot can stop with a yaw error larger than the internal `_yaw_precision` of `2°` if it reaches the position boundary while still correcting its heading. The test accounts for this with a `15°` yaw tolerance.

---

## Project Structure

```
tortoisebot_waypoints/
├── scripts/
│   └── tortoisebot_action_server.py   # action server
├── test/
│   │── waypoints_test.py              # integration tests
│   └── waypoints_test.test
├── action/
│   └── WaypointActionAction.action
└── CMakeLists.txt
```