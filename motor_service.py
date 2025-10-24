#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from dynamixel_control.srv import SetPosition
from dynamixel_sdk import *  # Uses Dynamixel SDK library

# Motor configuration
DXL_ID = 1
BAUDRATE = 57600
DEVICENAME = '/dev/ttyUSB0'
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
PROTOCOL_VERSION = 2.0

class MotorService(Node):
    def __init__(self):
        super().__init__('motor_service')
        self.srv = self.create_service(SetPosition, 'set_position', self.set_position_callback)
        self.get_logger().info('Motor Service Ready.')

        # Initialize Dynamixel SDK
        self.portHandler = PortHandler(DEVICENAME)
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)
        if self.portHandler.openPort() and self.portHandler.setBaudRate(BAUDRATE):
            self.get_logger().info('Connected to Dynamixel motor.')
            self.packetHandler.write1ByteTxRx(self.portHandler, DXL_ID, ADDR_TORQUE_ENABLE, 1)
        else:
            self.get_logger().error('Failed to connect to Dynamixel.')

    def set_position_callback(self, request, response):
        position = request.position
        result, error = self.packetHandler.write4ByteTxRx(
            self.portHandler, DXL_ID, ADDR_GOAL_POSITION, position)
        if result == 0:
            response.message = f'Motor moved to position {position}'
        else:
            response.message = f'Failed to move motor. Error: {error}'
        self.get_logger().info(response.message)
        return response

def main(args=None):
    rclpy.init(args=args)
    node = MotorService()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
