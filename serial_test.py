import serial
import sys
import struct 
ser = serial.Serial(sys.argv[1], 115200, timeout=1)
#print(ser.name)
step_speed = int(sys.argv[2])
step_count = int(sys.argv[3]) # use multiple of n_steps otherwise will oscillate
dc_speed = int(sys.argv[4]) #use 255 or something
dc_millis = int(sys.argv[5])

#print(struct.pack('<i', step_speed))
#print(struct.pack('<h', step_count))
#print(struct.pack('<h', dc_speed))
#print(struct.pack('<h', dc_millis))

commands = struct.pack('<i', step_speed) + struct.pack('<h', step_count) + struct.pack('<h', dc_speed) + struct.pack('<h', dc_millis)
print(commands)
checksum = sum(commands)
print(struct.pack('<h', checksum))

ser.write(commands + struct.pack('<h', checksum))
print("Response: " + str(ser.readline()))
print(ser.readline())
ser.close()
