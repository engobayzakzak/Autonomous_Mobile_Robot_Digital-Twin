import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
import math

class NavigationBenchmarker(Node):
    def __init__(self):
        super().__init__('navigation_benchmarker')
        
        # Subscriptions
        self.sub_odom = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.sub_goal = self.create_subscription(
            PoseStamped, '/goal_pose', self.goal_callback, 10)
        
        # Benchmark evaluation loop timer (1 Hz)
        self.timer = self.create_timer(1.0, self.benchmark_loop)
        
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        
        self.target_x = None
        self.target_y = None
        self.target_yaw = None
        self.has_active_goal = False
        self.goal_evaluated = False

        self.get_logger().info('=================================================')
        self.get_logger().info('  AMR DIGITAL TWIN BENCHMARK NODE ACTIVE        ')
        self.get_logger().info('  Waiting for 2D Nav2 Goal Pose from RViz2...   ')
        self.get_logger().info('=================================================')

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

    def goal_callback(self, msg):
        self.target_x = msg.pose.position.x
        self.target_y = msg.pose.position.y
        
        q = msg.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.target_yaw = math.atan2(siny_cosp, cosy_cosp)
        
        self.has_active_goal = True
        self.goal_evaluated = False
        
        self.get_logger().info(f'\n🎯 New Goal Captured: Target = ({self.target_x:.2f}, {self.target_y:.2f}) m')

    def benchmark_loop(self):
        if not self.has_active_goal or self.target_x is None:
            return

        error_x = self.target_x - self.current_x
        error_y = self.target_y - self.current_y
        error_dist = math.sqrt(error_x**2 + error_y**2)
        error_heading = abs(self.target_yaw - self.current_yaw)

        # Print live tracking progress
        self.get_logger().info(
            f'Tracking... Pose: ({self.current_x:.2f}, {self.current_y:.2f}) m | Dist to Goal: {error_dist * 100:.1f} cm'
        )

        # Evaluate and print results upon arrival (distance < 15 cm)
        if error_dist < 0.15 and not self.goal_evaluated:
            self.get_logger().info('\n-------------------------------------------------')
            self.get_logger().info('           BENCHMARK EVALUATION RESULT           ')
            self.get_logger().info('-------------------------------------------------')
            self.get_logger().info(f' Target Coordinate    : ({self.target_x:.2f}, {self.target_y:.2f}) m')
            self.get_logger().info(f' Final Actual Pose    : ({self.current_x:.2f}, {self.current_y:.2f}) m')
            self.get_logger().info(f' Position Error (e_xy): {error_dist * 100:.2f} cm')
            self.get_logger().info(f' Heading Error (e_th) : {math.degrees(error_heading):.2f} deg')
            self.get_logger().info(' RESULT: PASS (Arrival within Nav2 tolerance < 15cm)')
            self.get_logger().info('-------------------------------------------------\n')
            self.goal_evaluated = True
            self.has_active_goal = False

def main(args=None):
    rclpy.init(args=args)
    node = NavigationBenchmarker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
