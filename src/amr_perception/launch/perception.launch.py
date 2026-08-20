from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    node_perception = Node(
        package='amr_perception',
        executable='object_detector_node',
        name='object_detector_node',
        output='screen'
    )

    return LaunchDescription([
        node_perception
    ])
