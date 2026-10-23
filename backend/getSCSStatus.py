#!/usr/bin/env python
#
# *********     Sync Write Example      *********
#   update servo status in Database input search
#   to get all alive servo write status in database
#
# Available SCSServo model on this example : All models using Protocol SCS
# This example is tested with a SCServo(SCS), and an URT
#
#
import sys
import os
# import pymysql
import sqlite3  # 仅新增导入

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
from SCServo_Python.scservo_sdk import *                      # Uses SCServo SDK library

# Default setting
BAUDRATE                    = 115200           # SCServo default baudrate : 1000000
#DEVICENAME                  = '/dev/ttyAMA0'    # Check which port is being used on your controller
# DEVICENAME                  = '/dev/ttyUSB0'
DEVICENAME                  = 'COM5'    # Check which port is being used on your controller
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
sts_packetHandler =sms_sts(portHandler)

# Open port
# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    quit()


# Set port baudrate
# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    quit()

while 1:
    #print("Press read or write to continue! (or press ESC to quit!)")

    operation=input('please in put \'w\'to write, \'r\' to read , \'p\' ping range status ,\'s\' to range status , \'search\' to status update database:')
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
        # Read SCSServo present position
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


        
    elif operation == 'p':
        print('input s read status')
        ID_start = int(input('ID_start:'))
        ID_end = int(input('ID_end:'))
       
        for servo_ID in range(ID_start, ID_end):
            scs_model_number, scs_comm_result, scs_error = packetHandler.ping(servo_ID)
            if scs_comm_result == COMM_SUCCESS:
                if scs_model_number == 1284:
                    servo_type='scs'
                elif scs_model_number == 2307:
                    servo_type='sts'
                else:
                    servo_type='unknown'
                print("[ID:%03d] ping Succeeded. Servo model number: %d. ServoType: %s" % (servo_ID, scs_model_number,servo_type))
                # 保持原有的获取逻辑和变量名称
                if servo_type == 'scs':
                #scs servo 
                    scs_present_tmp1b, _, _ = packetHandler.ReadTmp(servo_ID)
                    scs_present_volt1b, _, _ = packetHandler.ReadVolt(servo_ID)
                    scs_present_load2b, _, _ ,_ = packetHandler.ReadLoad(servo_ID)
                    moving, _, _ = packetHandler.ReadMoving(servo_ID)
                    scs_present_currp2b, _, _ = packetHandler.ReadCurrPosition(servo_ID)
                    print("load is :  %d ，curr position is：  %d , moving flag is: %d, temperature is: %d, vlotage is: %d" % (scs_present_load2b, scs_present_currp2b, moving,scs_present_tmp1b,scs_present_volt1b))
                elif servo_type == 'sts':
                #sts servo
                    sts_present_tmp1b, _, _ = sts_packetHandler.ReadTmp(servo_ID)
                    sts_present_volt1b, _, _ = sts_packetHandler.ReadVolt(servo_ID)
                    sts_present_load2b, _, _ ,_ = sts_packetHandler.ReadLoad(servo_ID)
                    moving, _, _ = sts_packetHandler.ReadMoving(servo_ID)
                    sts_present_currp2b, _, _ = sts_packetHandler.ReadCurrPosition(servo_ID)
                    print("load is :  %d ，curr position is：  %d , moving flag is: %d, temperature is: %d, vlotage is: %d" % (sts_present_load2b, sts_present_currp2b, moving,sts_present_tmp1b,sts_present_volt1b))
           
        

    elif operation == 's':
        # print('input s read status')
        SCS_ID_start = int(input('SCS_ID_start:'))
        SCS_ID_end = int(input('SCS_ID_end:'))
        for SCS_ID in range(SCS_ID_start, SCS_ID_end):
            # SCS_ID = int(1)
            # Read SCSServo present position
            scs_present_load2b,datastring, scs_comm_result, scs_error = packetHandler.ReadLoad(SCS_ID)
            if scs_comm_result != COMM_SUCCESS:
                print('curr SCSID:',SCS_ID,'comm_error msg:',packetHandler.getTxRxResult(scs_comm_result))
            elif scs_error != 0:
                print('curr SCSID:',SCS_ID,'scs_error msg:',packetHandler.getRxPacketError(scs_error))
            else:
                # print("load is : 2b: %d " % (scs_present_load2b),datastring)
                moving, scs_comm_result, scs_error = packetHandler.ReadMoving(SCS_ID)
                if abs(scs_present_load2b) >60 and moving==0:
                    scs_present_currp2b, scs_comm_result, scs_error = packetHandler.ReadCurrPosition(SCS_ID)
                    target_position = scs_present_currp2b
                    print("curr SCSID:",SCS_ID,"load is :  %d ，curr position is：  %d , moving flag is: %d" % (scs_present_load2b,target_position,moving))
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

    elif operation == 'search':
        print('search')

        # --- SQLite 逻辑 ---
        conn = sqlite3.connect('ml.db')
        cursor = conn.cursor()

        # 确保表存在，结构保持不变
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servo_info (
                SERVOID INTEGER PRIMARY KEY,
                SERVO_DESC TEXT DEFAULT '',
                SERVO_TYPE TEXT,
                CURR_POSITION INTEGER,
                SLOAD INTEGER,
                VOLTAGE INTEGER,
                TEMPERATURE INTEGER,
                min_position INTEGER DEFAULT NULL,
                max_position INTEGER DEFAULT NULL,
                max_load INTEGER DEFAULT NULL
            )
        ''')

        for SERVO_ID in range(1, 55):
            scs_model_number, scs_comm_result, scs_error = packetHandler.ping(SERVO_ID)
            if scs_comm_result == COMM_SUCCESS:
                # 1. 判断 Servo 类型
                if scs_model_number == 1284:
                    servo_type = 'scs'
                elif scs_model_number == 2307:
                    servo_type = 'sts'
                else:
                    servo_type = 'unknown'

                print("[ID:%03d] ping Succeeded. Servo model number: %d. ServoType: %s" % (SERVO_ID,scs_model_number, servo_type))

                # 初始化变量
                tmp = 0
                volt = 0
                load = 0
                moving = 0
                curr_pos = 0
                # 默认描述为空字符串
                servo_desc = ""

                # 2. 根据类型选择不同的 Handler 获取数据
                if servo_type == 'scs':
                    tmp, _, _ = packetHandler.ReadTmp(SERVO_ID)
                    volt, _, _ = packetHandler.ReadVolt(SERVO_ID)
                    load, _, _, _ = packetHandler.ReadLoad(SERVO_ID)
                    moving, _, _ = packetHandler.ReadMoving(SERVO_ID)
                    curr_pos, _, _ = packetHandler.ReadCurrPosition(SERVO_ID)
                elif servo_type == 'sts':
                    tmp, _, _ = sts_packetHandler.ReadTmp(SERVO_ID)
                    volt, _, _ = sts_packetHandler.ReadVolt(SERVO_ID)
                    load, _, _, _ = sts_packetHandler.ReadLoad(SERVO_ID)
                    moving, _, _ = sts_packetHandler.ReadMoving(SERVO_ID)
                    curr_pos, _, _ = sts_packetHandler.ReadCurrPosition(SERVO_ID)
                else:
                    pass

                print("load is :  %d ，curr position is：  %d , moving flag is: %d, temperature is: %d, voltage is:  %d" % (load, curr_pos, moving, tmp, volt))

                # 3. 执行 SQL 写入
                # 注意：在 DO UPDATE SET 中去掉了 SERVO_DESC，确保它是静态描述，不会被覆盖
                sql = """
                INSERT INTO servo_info (SERVOID, SERVO_DESC, SERVO_TYPE, CURR_POSITION, SLOAD, VOLTAGE, TEMPERATURE) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(SERVOID) DO UPDATE SET
                    SERVO_TYPE=excluded.SERVO_TYPE,
                    CURR_POSITION=excluded.CURR_POSITION,
                    SLOAD=excluded.SLOAD,
                    VOLTAGE=excluded.VOLTAGE,
                    TEMPERATURE=excluded.TEMPERATURE;
                """

                # 数据元组顺序：SERVOID, SERVO_DESC, SERVO_TYPE, CURR_POSITION, SLOAD, VOLTAGE, TEMPERATURE
                data = (SERVO_ID, servo_desc, servo_type, curr_pos, load, volt, tmp)
                print(data)
                cursor.execute(sql, data)

        conn.commit()
        cursor.close()
        conn.close()
