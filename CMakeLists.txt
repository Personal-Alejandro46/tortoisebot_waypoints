cmake_minimum_required(VERSION 3.0.2)
project(tortoisebot_waypoints)
find_package(catkin REQUIRED COMPONENTS
  rospy
  actionlib
  actionlib_msgs
  geometry_msgs
  nav_msgs
)

add_action_files(
  FILES
  WaypointAction.action
)

generate_messages(
  DEPENDENCIES
  actionlib_msgs
  geometry_msgs
)

catkin_package(
  CATKIN_DEPENDS
    rospy
    actionlib
    actionlib_msgs
    geometry_msgs
    nav_msgs
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

if(CATKIN_ENABLE_TESTING)
  find_package(rostest REQUIRED)
  add_rostest(test/waypoints_test.test)
endif()

catkin_install_python(PROGRAMS
  scripts/tortoisebot_action_server.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)