# import necessary packages
import time

class PID:
	def __init__(self, kP=1, kI=0, kD=0):
		# initialize gains
		self.kP = kP
		self.kI = kI
		self.kD = kD
		
		self.prevError = 0
		self.prevTime = None
		
		self.cP = 0
		self.cI = 0
		self.cD = 0

	def reset(self):
		# intialize the current and previous time
		self.prevTime = None
		self.prevError = 0
		
		self.cP = 0
		self.cI = 0
		self.cD = 0
		

	def update(self, error):
		currTime = time.time()
		if self.prevTime is not None:
			deltaTime = currTime - self.prevTime
			deltaError = error - self.prevError
			
			# proportional term
			self.cP = error
			# integral term
			self.cI += error * deltaTime
			# derivative term and prevent divide by zero
			self.cD = (deltaError / deltaTime) if deltaTime > 0 else 0
		# save previous time and error for the next update
		self.prevTime = currTime
		self.prevError = error
		# sum the terms and return
		return sum([
			self.kP * self.cP,
			self.kI * self.cI,
			self.kD * self.cD]) 
