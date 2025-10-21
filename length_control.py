#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dynamixel_sdk import *

# Control Table Addresses
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
ADDR_OPERATING_MODE = 11

PROTOCOL_VERSION = 2.0
BAUDRATE = 57600
DEVICENAME = '/dev/ttyUSB0'
#I wrote something so it is easier to commit
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
EXTENDED_POSITION_MODE = 4
REVOLUTION_COUNT = 4096  # Encoder counts per revolution

# Motor Configuration
dxl_ids = [0, 1, 2]  # Motor IDs
cm_per_rev = 5.4     # Linear displacement per revolution (cm)

# Initialize Port and Packet Handlers
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

if not portHandler.openPort():
    quit("Failed to open port")
if not portHandler.setBaudRate(BAUDRATE):
    quit("Failed to set baudrate")

print("Port opened and baudrate set")

# Set Extended Position Mode
for dxl_id in dxl_ids:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
        portHandler, dxl_id, ADDR_OPERATING_MODE, EXTENDED_POSITION_MODE)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set mode for Motor {dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"Motor {dxl_id} error: {packetHandler.getRxPacketError(dxl_error)}")

# Enable Torque
for dxl_id in dxl_ids:
    packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)

print("Torque enabled for all motors")

def move_motors(L_des_cm):
    """
    Move motors based on desired linear displacements (cm).

    Parameters:
        L_des_cm: list or tuple of 3 floats [L0, L1, L2]
    """
    assert len(L_des_cm) == 3, "Input must be a list of three lengths"

    # Read current positions
    present_positions = {}
    for dxl_id in dxl_ids:
        pos, _, _ = packetHandler.read4ByteTxRx(portHandler, dxl_id, ADDR_PRESENT_POSITION)
        present_positions[dxl_id] = pos
        print(f"Motor {dxl_id} start position: {pos}")

    # Convert length to revolutions
    def cm_to_revolutions(cm):
        return cm / cm_per_rev

    revs = [cm_to_revolutions(L) for L in L_des_cm]

    # Compute goal positions
    goal_positions = {}
    for i, dxl_id in enumerate(dxl_ids):
        goal_positions[dxl_id] = int(present_positions[dxl_id] + revs[i] * REVOLUTION_COUNT)

    # GroupSyncWrite for simultaneous motion
    groupSyncWrite = GroupSyncWrite(portHandler, packetHandler, ADDR_GOAL_POSITION, 4)
    for dxl_id, goal in goal_positions.items():
        param_goal = [
            DXL_LOBYTE(DXL_LOWORD(goal)),
            DXL_HIBYTE(DXL_LOWORD(goal)),
            DXL_LOBYTE(DXL_HIWORD(goal)),
            DXL_HIBYTE(DXL_HIWORD(goal))
        ]
        groupSyncWrite.addParam(dxl_id, param_goal)

    groupSyncWrite.txPacket()
    groupSyncWrite.clearParam()

    print("Motors moving...")

    # Wait until all motors reach goal
    threshold = 20
    while True:
        all_reached = True
        for dxl_id, goal in goal_positions.items():
            pos, _, _ = packetHandler.read4ByteTxRx(portHandler, dxl_id, ADDR_PRESENT_POSITION)
            diff = abs(goal - pos)
            print(f"Motor {dxl_id} | Current: {pos} | Goal: {goal} | dif={diff}")
            if diff > threshold:
                all_reached = False
        if all_reached:
            break

    print("All motors reached their goal\n")

if __name__ == "__main__":
    # Example desired movements in cm (relative)
    L0, L1, L2 = 10.8, -5.4, 2.7
    move_motors([L0, L1, L2])

    # Disable torque and close port
    for dxl_id in dxl_ids:
        packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
    portHandler.closePort()
    print("Torque disabled and port closed.")
