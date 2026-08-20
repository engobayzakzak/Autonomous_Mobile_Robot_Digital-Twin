import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_amr_description = get_package_share_directory('amr_description')
    pkg_amr_gazebo = get_package_share_directory('amr_gazebo')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Process Xacro
    xacro_file = os.path.join(pkg_amr_description, 'urdf', 'amr.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    params = {'robot_description': robot_description_config.toxml()}

    # Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    # Path to custom Gazebo world file with obstacles
    world_file = os.path.join(pkg_amr_gazebo, 'worlds', 'amr_world.sdf')

    # Gazebo Sim Node
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # Spawn AMR in Gazebo
    node_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description', '-name', 'amr', '-z', '0.1']
    )

    # ROS <-> Gazebo Topic Bridge
    node_ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{
            'config_file': os.path.join(
                pkg_amr_gazebo, 'config', 'ros_gz_bridge.yaml'
            )
        }]
    )

    return LaunchDescription([
        node_robot_state_publisher,
        gz_sim,
        node_spawn_entity,
        node_ros_gz_bridge
    ])
