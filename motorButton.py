import os
import RPi.GPIO as GPIO
import time

from dynamixel_sdk import * # Uses Dynamixel SDK library


MY_DXL = 'MX_SERIES'    # MX series with 2.0 firmware update.

ADDR_TORQUE_ENABLE          = 64
ADDR_GOAL_POSITION          = 116
ADDR_PRESENT_POSITION       = 132
DXL_MINIMUM_POSITION_VALUE  = 0        
DXL_MAXIMUM_POSITION_VALUE  = 4095     
BAUDRATE                    = 57600

PROTOCOL_VERSION            = 2.0

DXL_ID                      = 5

DEVICENAME                  = '/dev/ttyUSB0'

TORQUE_ENABLE               = 1     
TORQUE_DISABLE              = 0     
DXL_MOVING_STATUS_THRESHOLD = 20 

dxl_close_pos = DXL_MINIMUM_POSITION_VALUE
dxl_open_pos = DXL_MAXIMUM_POSITION_VALUE


# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    quit()


# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    quit()

# Enable Dynamixel Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("Dynamixel has been successfully connected")

# button code
#------------
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

button_pin = 12
shutdown_pin = 16

GPIO.setup(button_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(shutdown_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

# first, send to open position
# Write goal position
dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION, dxl_open_pos)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
while 1:
        # Read present position
        dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_ID, dxl_open_pos, dxl_present_position))

        if not abs(dxl_open_pos - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
            break

# Main loop
# ---------
print('Entering main loop')
while 1:
    # shutdown pi if button pressed
    if GPIO.input(shutdown_pin) == GPIO.HIGH:
        print("Shutdown pin pressed")
        # Disable Dynamixel Torque
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        # Close port
        portHandler.closePort()
        
        os.system('sudo shutdown -h now')
        time.sleep(0.05)
        GPIO.cleanup()

    # set goal postion based off button
    if GPIO.input(button_pin) == GPIO.HIGH:
        go_to_pos = dxl_close_pos
    else:
        go_to_pos = dxl_open_pos

    # if at the go_to_pos, just keep looping
    if not abs(go_to_pos - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
        continue

    # Write goal position
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION, go_to_pos)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    # Read present position
    dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_PRESENT_POSITION)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    print("GoalPos:%03d  PresPos:%03d" % (go_to_pos, dxl_present_position))  

# Disable Dynamixel Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))

# Close port
portHandler.closePort()
