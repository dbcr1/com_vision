import serial
from time import sleep

robot = serial.Serial('/dev/ttyACM0', 115200)
START_BYTE = 0xFF
END_BYTE = 0xFE

buffer = [' ' for i in range(6)]

buffer[0] = START_BYTE

buffer[5] = END_BYTE
while 1:
    key = input('KEY')
    if key == 'u':
        buffer[1] = 1
        buffer[2] = 0
        buffer[3] = 1
        buffer[4] = 0
        break
    if key == 'w':
        buffer[1] = 1
        buffer[2] = 150
        buffer[3] = 1
        buffer[4] = 150
    if key == 's':
        buffer[1] = 0
        buffer[2] = 150
        buffer[3] = 0
        buffer[4] = 150
    if key == 'd':
        buffer[1] = 0
        buffer[2] = 150
        buffer[3] = 1
        buffer[4] = 150
    if key == 'a':
        buffer[1] = 1
        buffer[2] = 150
        buffer[3] = 0
        buffer[4] = 150
    if key == 'r':
        buffer[1] = 1
        buffer[2] = 0
        buffer[3] = 1
        buffer[4] = 0
    robot.write(buffer)
    print (buffer)

robot.close()