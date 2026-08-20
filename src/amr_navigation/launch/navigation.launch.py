import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_amr_navigation = get_package_share_directory('amr_navigation')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # Default paths
    default_map = os.path.join(pkg_amr_navigation, 'maps', 'amr_world_map.yaml')
    default_params = os.path.join(pkg_amr_navigation, 'config', 'nav2_params.yaml')
    default_rviz_config = os.path.join(pkg_nav2_bringup, 'rviz', 'nav2_default_view.rviz')

    # Launch Configurations
    map_yaml_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Declare arguments
    declare_map_cmd = DeclareLaunchArgument(
        'map',
        default_value=default_map,
        description='Full path to map yaml file to load'
    )

    declare_params_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=default_params,
        description='Full path to the ROS2 parameters file to use for all launched nodes'
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # Include Nav2 Bringup Launch
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_yaml_file,
            'params_file': params_file,
            'use_sim_time': use_sim_time,
            'autostart': 'true'
        }.items()
    )

    # RViz2 Node with official Nav2 default configuration
    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', default_rviz_config],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        declare_map_cmd,
        declare_params_cmd,
        declare_use_sim_time_cmd,
        nav2_bringup_launch,
        node_rviz
    ])
