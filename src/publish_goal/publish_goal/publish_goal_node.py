#!/usr/bin/env python3
import rclpy                          
from rclpy.node import Node             
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PointStamped




class GoalPublisher(Node):
    def __init__(self, name):
        super().__init__(name)                                  
        self.init_pose_sub = self.create_subscription(
            PointStamped, '/initial_pose', self.init_pose_callback, 10)    
        
        self.way_point_sub = self.create_subscription(
            PointStamped, '/way_point', self.waypoint_callback, 10)   

        # self.state_sub = self.create_subscription(
        #     Odometry, '/state_estimation', self.state_callback, 10)
        self.vel_sub = self.create_subscription(
            TwistStamped, '/cmd_vel', self.vel_callback, 100)

        
        self.goal_pub = self.create_publisher(
            PointStamped, '/goal_point', 10)         

        self.init_pose = None
        self.way_point = None
        self.explore_activate = True       
        self.stopped_time = None

        self.timer = self.create_timer(1.0, self.timer_callback)
      
                       
    def vel_callback(self, data:TwistStamped):
        v_x = data.twist.linear.x
        v_w = data.twist.angular.z

        if v_x < 0.01 and v_w < 0.01 and self.explore_activate is True:
            print(f'v:{v_x:.3f},w:{v_w:.3f}')
            if self.stopped_time is None:
                self.stopped_time = self.get_clock().now()
        if( v_x > 0.01 or v_w > 0.01) and self.stopped_time is not None:
            self.stopped_time = None
            self.get_logger().info("Robot is moving, stopped time reset")

    # def state_callback(self, data:Odometry):
        
    #     v_x = data.twist.twist.linear.x
    #     v_w = data.twist.twist.angular.z
    #     if v_x < 0.01 and v_w < 0.01 and self.explore_activate is True:
    #         print(f'v:{v_x:.3f},w:{v_w:.3f}')
    #         if self.stopped_time is None:
    #             self.stopped_time = self.get_clock().now()
    #     if( v_x > 0.01 or v_w > 0.01) and self.stopped_time is not None:
    #         self.stopped_time = None
    #         self.get_logger().info("Robot is moving, stopped time reset")
        
    def init_pose_callback(self, data:PointStamped):
        self.init_pose = data
        # print("Received initial pose:")
        if self.explore_activate is False and self.init_pose:
            self.goal_pub.publish(self.init_pose)

    def waypoint_callback(self, data:PointStamped):
        if self.init_pose is None:
            self.get_logger().warn("Initial pose not set, cannot publish way point")
            return
        # print("Received way point")
        # print(f'explore_activate: {self.explore_activate}')
        self.way_point = data
        if self.explore_activate and self.way_point:
            self.goal_pub.publish(self.way_point)
            # print(f'published way point: {self.way_point}')

    def timer_callback(self):
        if self.stopped_time is not None and self.init_pose is not None:
            elapsed_time = self.get_clock().now() - self.stopped_time
            self.get_logger().info(f"Robot stopped for {elapsed_time.nanoseconds / 1e9:.2f} seconds")
            if elapsed_time.nanoseconds / 1e9 >= 30.0:  # Check if stopped for 20 seconds
                self.goal_pub.publish(self.init_pose)
                self.get_logger().warn("Robot stopped for 20s, returning to initial pose")
                self.explore_activate = False




def main(args=None):                                       
    rclpy.init(args=args)                                   
    node = GoalPublisher("goal_node")              
    rclpy.spin(node)                                        
    node.destroy_node()                                    
    rclpy.shutdown()                                       

if __name__ == "__main__":
    main()
