import serial
from time import sleep

robot = serial.Serial('COM5', 115200)
START_BYTE = 0xFF
END_BYTE = 0xFE

buffer = [' ' for i in range(6)]

buffer[0] = START_BYTE
buffer[1] = 1
buffer[2] = 250
buffer[3] = 1
buffer[4] = 250
buffer[5] = END_BYTE

print (buffer)

robot.write(buffer)
robot.close()
