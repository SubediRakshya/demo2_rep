#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from dynamixel_control.srv import SetPosition

class MotorClient(Node):
    def __init__(self):
        super().__init__('motor_client')
        self.cli = self.create_client(SetPosition, 'set_position')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')
        self.req = SetPosition.Request()

    def send_request(self, position):
        self.req.position = position
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main(args=None):
    rclpy.init(args=args)
    node = MotorClient()
    pos = int(input("Enter motor position: "))
    response = node.send_request(pos)
    node.get_logger().info(f'Result: {response.message}')
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
