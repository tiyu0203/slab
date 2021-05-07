import serial
import struct 
class Controller:
	def __init__(self, port):
		self.ser = serial.Serial(port, 115200, timeout=1) 
		#what do if timeout? 
	
	def send(self, tilt_speed, tilt_steps, pan_speed, pan_ms):
		commands = struct.pack('<i', int(tilt_speed)) + \
				   struct.pack('<h', int(tilt_steps)) + \
				   struct.pack('<h', int(pan_speed)) + \
				   struct.pack('<H', int(pan_ms))
		checksum = struct.pack('<h', sum(commands))
		#print(commands)
		self.ser.write(commands + checksum)
	
