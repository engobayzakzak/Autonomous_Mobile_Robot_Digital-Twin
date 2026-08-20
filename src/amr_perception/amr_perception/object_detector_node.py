import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from visualization_msgs.msg import Marker
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np

class ObjectDetectorNode(Node):
    def __init__(self):
        super().__init__('object_detector_node')
        
        self.bridge = CvBridge()
        
        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        
        # Publishers
        self.image_pub = self.create_publisher(
            Image,
            '/camera/image_detected',
            10
        )
        self.marker_pub = self.create_publisher(
            Marker,
            '/visualization_marker',
            10
        )
        
        self.get_logger().info('AMR Perception Vision Node Initialized successfully.')

    def image_callback(self, msg):
        try:
            # Convert ROS Image message to OpenCV BGR image
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f'cv_bridge exception: {e}')
            return

        # Convert to HSV color space for robust color thresholding
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # Red color range mask
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
        mask = mask1 | mask2

        # Morphological filtering
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find Contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Minimum area noise threshold
                x, y, w, h = cv2.boundingRect(contour)
                
                # Draw bounding box on image feed
                cv2.rectangle(cv_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(cv_image, 'RED TARGET', (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Estimate 3D spatial marker position
                cx = x + w / 2.0
                image_width = cv_image.shape[1]
                offset_x = (cx - image_width / 2.0) / (image_width / 2.0)

                self.publish_3d_marker(offset_x)

        # Publish annotated OpenCV frame back to ROS 2
        try:
            annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
            self.image_pub.publish(annotated_msg)
        except CvBridgeError as e:
            self.get_logger().error(f'cv_bridge publish error: {e}')

    def publish_3d_marker(self, offset_x):
        marker = Marker()
        marker.header.frame_id = 'camera_link_optical'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'detected_objects'
        marker.id = 0
        marker.type = Marker.CUBE
        marker.action = Marker.ADD

        # Estimated position relative to camera link optical frame
        marker.pose.position.x = float(offset_x * 0.5)
        marker.pose.position.y = 0.0
        marker.pose.position.z = 1.2  # Estimated depth
        
        marker.pose.orientation.w = 1.0

        # Size of the 3D marker cube in RViz
        marker.scale.x = 0.2
        marker.scale.y = 0.2
        marker.scale.z = 0.5

        # Green color for RViz 3D marker
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        marker.color.a = 0.8

        self.marker_pub.publish(marker)

def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
