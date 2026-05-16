#!/usr/bin/env python
import unittest
import rospy
import actionlib
import math
from tortoisebot_waypoints.msg import WaypointActionAction, WaypointActionGoal
from nav_msgs.msg import Odometry
from gazebo_msgs.srv import SetModelState
from gazebo_msgs.msg import ModelState
from tf import transformations

TARGET_X = -0.465
TARGET_Y = 0.34
PKG = 'tortoisebot_waypoints'

class TestWaypoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rospy.init_node('test_waypoints', anonymous=True)
        cls.current_x = 0.0
        cls.current_y = 0.0
        cls.current_yaw = 0.0
        cls.first_time = True

        # Reset UMA ÚNICA VEZ para (0,0)
        rospy.wait_for_service('/gazebo/set_model_state')
        set_state = rospy.ServiceProxy('/gazebo/set_model_state', SetModelState)
        state = ModelState()
        state.model_name = 'tortoisebot'
        state.pose.position.x = 0.0
        state.pose.position.y = 0.0
        state.pose.orientation.w = 1.0
        set_state(state)
        rospy.sleep(0.5)

        rospy.Subscriber('/odom', Odometry, cls._odom_callback)

        # Aguarda primeiro dado do /odom
        while cls.first_time:
            rospy.sleep(0.05)

        # Envia goal UMA ÚNICA VEZ
        client = actionlib.SimpleActionClient('tortoisebot_as', WaypointActionAction)
        client.wait_for_server(timeout=rospy.Duration(10))

        goal = WaypointActionGoal()
        goal.position.x = TARGET_X
        goal.position.y = TARGET_Y
        client.send_goal(goal)
        client.wait_for_result(timeout=rospy.Duration(60))

        # Guarda resultado final — ambos os testes usam estes valores
        cls.final_x   = cls.current_x
        cls.final_y   = cls.current_y
        cls.final_yaw = cls.current_yaw

        rospy.loginfo("=== RESULTADO FINAL ===")
        rospy.loginfo("final_x  : %.4f m" % cls.final_x)
        rospy.loginfo("final_y  : %.4f m" % cls.final_y)
        rospy.loginfo("final_yaw: %.4f rad (%.2f deg)" % (cls.final_yaw, math.degrees(cls.final_yaw)))
        rospy.loginfo("=======================")

    @classmethod
    def _odom_callback(cls, msg):
        cls.current_x = msg.pose.pose.position.x
        cls.current_y = msg.pose.pose.position.y
        quaternion = (
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w)
        euler = transformations.euler_from_quaternion(quaternion)
        cls.current_yaw = euler[2]
        if cls.first_time:
            cls.start_pose_x = cls.current_x
            cls.start_pose_y = cls.current_y
            cls.first_time = False
            rospy.loginfo("Start position X: %.4f | Y: %.4f" % (cls.start_pose_x, cls.start_pose_y))

    def test_end_position(self):
        err_pos = math.sqrt(pow(TARGET_Y - self.final_y, 2) + pow(TARGET_X - self.final_x, 2))
        self.assertAlmostEqual(err_pos, 0, delta=0.1,
            msg="Position error: %.4f m (max 0.1 m)" % err_pos)

    def test_end_yaw(self):
        expected_yaw = math.atan2(TARGET_Y - self.start_pose_y, TARGET_X - self.start_pose_x)
        diff = expected_yaw - self.final_yaw
        msg = (
            f"final_yaw={math.degrees(self.final_yaw):.1f}deg ({self.final_yaw:.4f}rad) "
            f"expected_yaw={math.degrees(expected_yaw):.1f}deg ({expected_yaw:.4f}rad) "
            f"diff={math.degrees(diff):.1f}deg ({diff:.4f}rad)"
        )
        self.assertAlmostEqual(self.final_yaw, expected_yaw, delta=0.45, msg=msg) # 15° = 0.2618 rad

if __name__ == '__main__':
    import rostest
    rostest.rosrun(PKG, 'test_waypoints', TestWaypoints)