#!/usr/bin/env python
#
# *********     Sync Write Example      *********
#
#
# Available SCServo model on this example : All models using Protocol SCS
# This example is tested with a SCServo(SCS), and an URT
#

import sys
import os

if os.name == 'nt':
    print('windows')
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

sys.path.append("..")
from scservo_sdk import *                      # Uses SCServo SDK library

# Default setting
BAUDRATE                    = 1000000           # SCServo default baudrate : 1000000
#DEVICENAME                  = '/dev/ttyUSB0'    # Check which port is being used on your controller
DEVICENAME                  = 'COM4'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

SCS_MINIMUM_POSITION_VALUE  = 10                # SCServo will rotate between this value
SCS_MAXIMUM_POSITION_VALUE  = 1000
SCS_MOVING_SPEED            = 2400              # SCServo moving speed

index = 0
scs_goal_position = [SCS_MINIMUM_POSITION_VALUE, SCS_MAXIMUM_POSITION_VALUE]         # Goal position

# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Get methods and members of Protocol
packetHandler = scscl(portHandler)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    quit()


# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    quit()

while 1:
    #print("Press read or write to continue! (or press ESC to quit!)")

    #operation=input('please in put \'w\'to write, \'r\' to read , \'s\' to status ')
    operation = 's'
    if operation=='w':
        print('input w write operation')
        SCS_ID=int(input('SCS_ID:'))
        target_position=int(input('scs_goal_position:'))
        scs_comm_result, scs_error = packetHandler.WritePos(SCS_ID,target_position, 0, SCS_MOVING_SPEED)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % packetHandler.getRxPacketError(scs_error))

    elif operation=='r':
        print('input r read operation')
        SCS_ID = int(input('SCS_ID:'))
        # Read SCServo present position
        scs_present_position, scs_present_speed, scs_comm_result, scs_error = packetHandler.ReadPosSpeed(SCS_ID)
        if scs_comm_result != COMM_SUCCESS:
            print(packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print(packetHandler.getRxPacketError(scs_error))

        # Read SCServo moving status
        moving, scs_comm_result, scs_error = packetHandler.ReadMoving(SCS_ID)
        if scs_comm_result != COMM_SUCCESS:
            print(packetHandler.getTxRxResult(scs_comm_result))
        else:
            print("[ID:%03d] GoalPos:%d PresPos:%d PresSpd:%d Moving:%d" % (
            SCS_ID, scs_goal_position[index], scs_present_position, scs_present_speed,moving))
        if scs_error != 0:
            print(packetHandler.getRxPacketError(scs_error))

    elif operation == 's':
        # print('input s read status')
        # SCS_ID = int(input('SCS_ID:'))
        SCS_ID = int(1)
        # Read SCServo present position
        scs_present_load2b,datastring, scs_comm_result, scs_error = packetHandler.ReadLoad(SCS_ID)
        if scs_comm_result != COMM_SUCCESS:
            print(packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print(packetHandler.getRxPacketError(scs_error))
        else:
            # print("load is : 2b: %d " % (scs_present_load2b),datastring)
            moving, scs_comm_result, scs_error = packetHandler.ReadMoving(SCS_ID)
            if abs(scs_present_load2b) >60 and moving==0:
                scs_present_currp2b, scs_comm_result, scs_error = packetHandler.ReadCurrPosition(SCS_ID)
                target_position = scs_present_currp2b
                print("load is :  %d ，curr position is：  %d , moving flag is: %d" % (scs_present_load2b,target_position,moving))
                MOVING_SPEED = 10
                MOVING_STEP=5
                if scs_present_load2b>0 and scs_present_currp2b in range(100, 900, 1):
                    target_position=scs_present_currp2b+MOVING_STEP
                elif scs_present_load2b<0 and scs_present_currp2b in range(100, 900, 1):
                    target_position = scs_present_currp2b - MOVING_STEP
                if target_position not in range(100, 900, 1):
                    print('position out of rage')
                    if scs_present_load2b > 0:
                        target_position = scs_present_currp2b + 80
                    elif scs_present_load2b < 0:
                        target_position = scs_present_currp2b - 80
                    scs_comm_result, scs_error = packetHandler.WritePos(SCS_ID, target_position, 0, 400)
                    scs_comm_result, scs_error = packetHandler.WritePos(SCS_ID, 511, 0, 100)
                elif target_position >= 100 and target_position <= 900:
                    scs_comm_result, scs_error = packetHandler.WritePos(SCS_ID, target_position, 0, MOVING_SPEED)
                    # print(target_position)



        '''
        scs_present_tmp4b, scs_present_tmp2b, scs_present_tmp1b, scs_comm_result, scs_error = packetHandler.ReadTmp(
            SCS_ID)
        if scs_comm_result != COMM_SUCCESS:
            print(packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print(packetHandler.getRxPacketError(scs_error))
        else:
            # print("temperature is :4b: %d 2b: %d 1b: %d" % (scs_present_tmp4b, scs_present_tmp2b, scs_present_tmp1b))
            print("temperature is : 1b: %d" % ( scs_present_tmp1b))

        scs_present_volt4b, scs_present_volt2b, scs_present_volt1b, scs_comm_result, scs_error = packetHandler.ReadVolt(
            SCS_ID)
        if scs_comm_result != COMM_SUCCESS:
            print(packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print(packetHandler.getRxPacketError(scs_error))
        else:
            # print("voltage is :4b: %d 2b: %d 1b: %d" % (scs_present_volt4b, scs_present_volt2b, scs_present_volt1b))
            print("voltage is: 1b: %d" % (scs_present_volt1b))

        scs_present_currp4b, scs_present_currp2b, scs_present_currp1b, scs_comm_result, scs_error = packetHandler.ReadCurrPosition(
            SCS_ID)
        if scs_comm_result != COMM_SUCCESS:
            print(packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print(packetHandler.getRxPacketError(scs_error))
        else:
            print("current position is :4b: %d 2b: %d 1b: %d" % (scs_present_currp4b, scs_present_currp2b, scs_present_currp1b))
            print("scs error",scs_error)
        '''




        '''
        if moving == 0:
            print('status not moveing')
        '''
    '''
    for scs_id in range(1, 11):
        # Add SCServo#1~10 goal position\moving speed\moving accc value to the Syncwrite parameter storage
        scs_addparam_result = packetHandler.SyncWritePos(scs_id, scs_goal_position[index], 0, SCS_MOVING_SPEED)
        if scs_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % scs_id)

    # Syncwrite goal position
    scs_comm_result = packetHandler.groupSyncWrite.txPacket()
    if scs_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(scs_comm_result))

    # Clear syncwrite parameter storage
    packetHandler.groupSyncWrite.clearParam()

    # Change goal position
    if index == 0:
        index = 1
    else:
        index = 0
    '''
# Close port
portHandler.closePort()
