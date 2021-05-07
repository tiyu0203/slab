import serial
import sys
import struct 
ser = serial.Serial(sys.argv[1], 115200, timeout=1)
#print(ser.name)
step_speed = int(sys.argv[2])
step_count = int(sys.argv[3]) # use multiple of n_steps otherwise will oscillate
dc_speed = int(sys.argv[4]) #use 255 or something
dc_millis = int(sys.argv[5])

print(step_speed, step_count, dc_speed, dc_millis)

#print(struct.pack('<i', step_speed))
#print(struct.pack('<h', step_count))
#print(struct.pack('<h', dc_speed))
#print(struct.pack('<h', dc_millis))

commands = struct.pack('<i', step_speed) + struct.pack('<h', step_count) + struct.pack('<h', dc_speed) + struct.pack('<H', dc_millis)
print(commands.hex())
checksum = sum(commands)
print(checksum)
checkbytes = struct.pack('<h', checksum)
print(checkbytes.hex())

print(ser.write(commands + checkbytes))
print("Response: " + str(ser.readline()))
print(ser.readline())
ser.close()
