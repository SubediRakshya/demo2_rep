#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from dynamixel_control.srv import SetPosition
from dynamixel_sdk import PortHandler, PacketHandler

ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
PROTOCOL_VERSION = 2.0
DXL_ID = 1
BAUDRATE = 57600
DEVICENAME = '/dev/ttyUSB0'
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
MOVING_STATUS_THRESHOLD = 20

class MotorService(Node):
    def __init__(self):
        super().__init__('motor_service')
        self.srv = self.create_service(SetPosition, 'set_position', self.set_position_callback)
        self.portHandler = PortHandler(DEVICENAME)
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)

        if not self.portHandler.openPort():
            self.get_logger().error('Failed to open port')
        if not self.portHandler.setBaudRate(BAUDRATE):
            self.get_logger().error('Failed to set baudrate')

        # Enable Torque
        self.packetHandler.write1ByteTxRx(self.portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        self.get_logger().info('Motor ready for commands.')

    def set_position_callback(self, request, response):
        goal = request.position
        self.get_logger().info(f'Moving motor to position {goal}')

        # Write target position
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
            self.portHandler, DXL_ID, ADDR_GOAL_POSITION, goal
        )

        if dxl_comm_result != 0 or dxl_error != 0:
            response.success = False
            response.message = 'Failed to move motor'
            return response

        # Wait until goal reached
        while True:
            dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
                self.portHandler, DXL_ID, ADDR_PRESENT_POSITION
            )
            if abs(goal - dxl_present_position) <= MOVING_STATUS_THRESHOLD:
                break

        response.success = True
        response.message = f'Motor moved to {goal}'
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
