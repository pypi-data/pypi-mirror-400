from launch_ros.actions import Node


def get_camera_bridge(topic_name, condition=None):
    """Create gazebo /ros2 topic bridge for a camera topic"""
    camera_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            f"{topic_name}@sensor_msgs/msg/Image@gz.msgs.Image",
        ],
        output="screen",
        condition=condition,
    )
    return camera_bridge
