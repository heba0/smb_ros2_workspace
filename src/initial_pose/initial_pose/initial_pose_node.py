#!/usr/bin/env python3
import rclpy                          
from rclpy.node import Node             
from nav_msgs.msg import Odometry
from sensor_msgs.msg import PointCloud2
from geometry_msgs.msg import PointStamped

import sensor_msgs_py.point_cloud2 as pc2
# import pcl                 


class odomSubscriber(Node):
    def __init__(self, name):
        super().__init__(name)                                  
        self.odom_sub = self.create_subscription(
            Odometry, '/state_estimation', self.odom_callback, 10)    
        
        self.odom_pub = self.create_publisher(
            PointStamped, '/initial_pose', 10)          
        self.initial_pose = None         
      
                       


    def odom_callback(self, data):
        if self.initial_pose is None:  
            # self.get_logger().info("Received odometry data")
            self.initial_pose = PointStamped()
            self.initial_pose.header = data.header
            self.initial_pose.point.x = data.pose.pose.position.x
            self.initial_pose.point.y = data.pose.pose.position.y
            self.initial_pose.point.z = data.pose.pose.position.z
        self.odom_pub.publish(self.initial_pose)
        # self.get_logger().info(f"Published initial pose: {self.initial_pose.point.x}, {self.initial_pose.point.y}, {self.initial_pose.point.z}")





def main(args=None):                                       
    rclpy.init(args=args)                                   
    node = odomSubscriber("odom_sub_node")              
    rclpy.spin(node)                                        
    node.destroy_node()                                    
    rclpy.shutdown()                                       

if __name__ == "__main__":
    main()
