import serial
from time import sleep

robot = serial.Serial('COM4', 115200)
START_BYTE = 0xFF
END_BYTE = 0xFE

buffer = [' ' for i in range(6)]

buffer[0] = START_BYTE
buffer[1] = 1
buffer[2] = 0
buffer[3] = 1
buffer[4] = 0
buffer[5] = END_BYTE

sleep(3)
print (buffer)
robot.write(buffer)
robot.close()
