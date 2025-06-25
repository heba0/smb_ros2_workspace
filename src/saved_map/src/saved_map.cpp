#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <geometry_msgs/msg/point_stamped.hpp>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/io/pcd_io.h>
#include <ament_index_cpp/get_package_share_directory.hpp>
#include <filesystem>
#include <libgen.h> 

class MapSubscriber : public rclcpp::Node {
public:
  MapSubscriber() : Node("saved_map_node") {
    // Subscriptions
   
    map_sub_ = create_subscription<sensor_msgs::msg::PointCloud2>(
        "/open3d/assembled_map", 10,
        std::bind(&MapSubscriber::map_callback, this, std::placeholders::_1));

   
    // Timer for map publishing
    timer_ = create_wall_timer(std::chrono::seconds(5),
                              std::bind(&MapSubscriber::map_publisher, this));

    RCLCPP_INFO(this->get_logger(), "MapSubscriber node initialized");
  }

private:
 

  void map_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg) {
    global_map_ = msg;
    // No further processing needed here, just store the message
  }

  void map_publisher() {
    if (!global_map_) {
      RCLCPP_WARN(this->get_logger(), "No point cloud map received yet, skipping save.");
      return;
    }

    // Optional PCL processing (commented out as in your Python code)

    try {
      pcl::PointCloud<pcl::PointXYZ>::Ptr pcl_cloud(new pcl::PointCloud<pcl::PointXYZ>);
      pcl::fromROSMsg(*global_map_, *pcl_cloud);

      if (pcl_cloud->empty()) {
        RCLCPP_WARN(this->get_logger(), "Empty point cloud, skipping save.");
        return;
      }

      // Get the directory of the current source file
      std::string source_file = __FILE__;
      std::string source_dir;
      {
        char *source_file_copy = strdup(source_file.c_str());
        source_dir = dirname(source_file_copy);
        free(source_file_copy);
      }

      // Construct path to the data directory in the package's source directory
      std::string data_directory = source_dir + "/../data";

      // Create data directory if it doesn't exist
      std::filesystem::create_directories(data_directory);

      // Save PCD file
      std::string filename = data_directory + "/assemble_map.pcd";
      pcl::io::savePCDFileASCII(filename, *pcl_cloud);
      RCLCPP_INFO(this->get_logger(), "Saved point cloud to %s", filename.c_str());
    } catch (const std::exception &e) {
      RCLCPP_ERROR(this->get_logger(), "Failed to save point cloud: %s", e.what());
    }

  }

  // Member variables
  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr map_sub_;
  rclcpp::TimerBase::SharedPtr timer_;
  sensor_msgs::msg::PointCloud2::SharedPtr global_map_;
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<MapSubscriber>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}