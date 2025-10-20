#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dynamixel_sdk import *  # Dynamixel SDK library

# Control table addresses (for XM430)
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
ADDR_OPERATING_MODE = 11

PROTOCOL_VERSION = 2.0
BAUDRATE = 57600
DEVICENAME = '/dev/ttyUSB0'

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
EXTENDED_POSITION_MODE = 4
REVOLUTION_COUNT = 4096

# Motor IDs
dxl_ids = [1, 2, 3]

# Revolutions (n, m, p)
n = 2   # Motor 1
m = -1  # Motor 2
p = 3   # Motor 3

# Initialize PortHandler & PacketHandler
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

if not portHandler.openPort():
    quit("Failed to open port")
if not portHandler.setBaudRate(BAUDRATE):
    quit("Failed to set baudrate")

print("Port opened and baudrate set")

# Set Extended Position Mode
for dxl_id in dxl_ids:
    packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_OPERATING_MODE, EXTENDED_POSITION_MODE)

# Enable torque
for dxl_id in dxl_ids:
    packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)

# Read current positions
present_positions = {}
for dxl_id in dxl_ids:
    pos, _, _ = packetHandler.read4ByteTxRx(portHandler, dxl_id, ADDR_PRESENT_POSITION)
    present_positions[dxl_id] = pos
    print(f"Motor {dxl_id} start position: {pos}")

# Calculate goal positions (add multi-turn increments)
goal_positions = {
    1: present_positions[1] + n * REVOLUTION_COUNT,
    2: present_positions[2] + m * REVOLUTION_COUNT,
    3: present_positions[3] + p * REVOLUTION_COUNT,
}

# GroupSyncWrite for simultaneous movement
groupSyncWrite = GroupSyncWrite(portHandler, packetHandler, ADDR_GOAL_POSITION, 4)

for dxl_id, goal in goal_positions.items():
    param_goal = [
        DXL_LOBYTE(DXL_LOWORD(goal)),
        DXL_HIBYTE(DXL_LOWORD(goal)),
        DXL_LOBYTE(DXL_HIWORD(goal)),
        DXL_HIBYTE(DXL_HIWORD(goal))
    ]
    groupSyncWrite.addParam(dxl_id, param_goal)

# Transmit all goal positions
groupSyncWrite.txPacket()
groupSyncWrite.clearParam()

print("Motors moving...")

# Wait until all motors reach their goal
threshold = 20
while True:
    reached = True
    for dxl_id, goal in goal_positions.items():
        pos, _, _ = packetHandler.read4ByteTxRx(portHandler, dxl_id, ADDR_PRESENT_POSITION)
        diff = abs(goal - pos)
        print(f"Motor {dxl_id} Pos: {pos} (Δ={diff})")
        if diff > threshold:
            reached = False
    if reached:
        break

print("All motors reached their goal")

# Disable torque and close port
for dxl_id in dxl_ids:
    packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)

portHandler.closePort()
print("Torque disabled and port closed.")
