# Multi-stage production container for ROS 2 Jazzy AMR Digital Twin
FROM osrf/ros:jazzy-desktop-full

# System environment setup
ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=jazzy
ENV AMENT_PREFIX_PATH=/opt/ros/jazzy

# Install core system dependencies & perception libraries
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-slam-toolbox \
    ros-jazzy-cv-bridge \
    python3-opencv \
    ros-jazzy-teleop-twist-keyboard \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory structure
WORKDIR /root/amr_ws
COPY src /root/amr_ws/src

# Build workspace packages
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build --symlink-install"

# Auto-source workspace in container bash sessions
RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc
RUN echo "source /root/amr_ws/install/setup.bash" >> /root/.bashrc

# Set default entrypoint command
CMD ["/bin/bash", "-c", "source /root/amr_ws/install/setup.bash && ros2 launch amr_gazebo gazebo.launch.py"]
