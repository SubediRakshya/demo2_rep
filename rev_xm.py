#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *

# Control table addresses
ADDR_MX_TORQUE_ENABLE      = 64
ADDR_MX_GOAL_POSITION      = 116
ADDR_MX_PRESENT_POSITION   = 132

# Protocol version
PROTOCOL_VERSION            = 2.0  # Changed for XM430

# Default settings
DXL_ID                      = 1
BAUDRATE                    = 57600
DEVICENAME                  = '/dev/ttyUSB0'

TORQUE_ENABLE               = 1
TORQUE_DISABLE              = 0
DXL_MOVING_STATUS_THRESHOLD = 20

# Revolutions settings
n_revolutions = 3
REVOLUTION_COUNT = 4096  # 1 revolution = 4096 position units

# Initialize port & packet handlers
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

if not portHandler.openPort():
    print("Failed to open the port")
    quit()
if not portHandler.setBaudRate(BAUDRATE):
    print("Failed to set baudrate")
    quit()
print("Port opened and baudrate set successfully")

# Enable Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
    portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print(packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print(packetHandler.getRxPacketError(dxl_error))
else:
    print("Torque enabled")

# Read current position
dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(
    portHandler, DXL_ID, ADDR_MX_PRESENT_POSITION)

# Compute CW and CCW goal positions
goal_cw = dxl_present_position + REVOLUTION_COUNT * n_revolutions
goal_ccw = dxl_present_position - REVOLUTION_COUNT * n_revolutions

# Rotate CW
print(f"Rotating CW for {n_revolutions} revolutions...")
dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
    portHandler, DXL_ID, ADDR_MX_GOAL_POSITION, goal_cw)
while True:
    dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(
        portHandler, DXL_ID, ADDR_MX_PRESENT_POSITION)
    print(f"Present: {dxl_present_position}")
    if abs(goal_cw - dxl_present_position) <= DXL_MOVING_STATUS_THRESHOLD:
        break

# Rotate CCW
print(f"Rotating CCW for {n_revolutions} revolutions...")
dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
    portHandler, DXL_ID, ADDR_MX_GOAL_POSITION, goal_ccw)
while True:
    dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(
        portHandler, DXL_ID, ADDR_MX_PRESENT_POSITION)
    print(f"Present: {dxl_present_position}")
    if abs(goal_ccw - dxl_present_position) <= DXL_MOVING_STATUS_THRESHOLD:
        break

# Disable Torque and close port
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
    portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
portHandler.closePort()
print("Torque disabled and port closed. Done!")
