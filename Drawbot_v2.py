#!/usr/bin/python

##HERE IS A TEST OF HOW TO USE MODULES AND CLASSES AND SHIT
#___________________________________
def main():
	#import necessary things
	import math
	import sys
	import time
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BCM)
	
	#This determines the movement of the plotter
	
	#I will be using pixdim in mm, and brightness in a 0-255 value.
	#base_speed is the lowest delay. line_dir is which direction your pixel line is going. 1 is up to the right.
	def plot_pixel(pixdim,brightness,base_speed,line_dir):
		#This is necessary for ideGPIO.setmode(GPIO.BCM)
		#Set the physical pin numbers
		StepPins_left=[18,27,20,21]
		StepPins_right=[17,22,23,24]
		StepPins_all = StepPins_left+StepPins_right
		#enable all the pins for writing and make sure they are off
		for pin in StepPins_all:
			GPIO.setup(pin,GPIO.OUT)
			GPIO.output(pin,False)
		# Specific motor steps
		Seq = [[1,0,0,1],
			[1,0,0,0],
			[1,1,0,0],
			[0,1,0,0],
			[0,1,1,0],
			[0,0,1,0],
			[0,0,1,1],
			[0,0,0,1]]
		StepCount = len(Seq)
		step=0
		#base_delay is the base speed in milliseconds for step-delay of the fast motor
		base_delay=base_speed/float(1000)
		#This is the pixel size determinant. When you are able to test it on a larger scale,
		#make this a more accurate value. I'm nominally starting with 1000 steps = 10 mm.
		steptotal = 100 * pixdim
		#The amplitude of the peaks
		pix = steptotal / 2
		#The number of lines within #######CHANGE THIS TONIGHT!!!!################
		squiggle = 260-brightness
		
		#Create all necessary lists
		StepCounter_left = 0
		StepCounter_right = 0
		PixelMasterDict = [(0,0,0)]
		while ( step < steptotal ) :
			print("start big step ",step)
			#This calculates the instantaneous velocity of the plotter
			#First, the speed and direction of the next step is determined. 
			#Then the motor which will be moving faster is scaled to a max velocity(base_delay) (adjustable)
			#The other motor is scaled by it's ratio to the faster motor.
			#The limiting factor is that one calculation is done for each microstep along a diagonal of the pixel.
			velocity = -((step-pix)*math.sin(3*math.pi*step/squiggle))/(math.sqrt((step-pix)**2)+0.00000001)-(3/squiggle)*math.pi*(math.sqrt((step-pix)**2)-pix)*math.cos(3*math.pi*step/squiggle)
			#If velocity is over 1, motor_left is faster, if it is under 1, motor_right is faster. The faster motor is scaled to base_delay.
			velocity_abs = abs(velocity)
			#I need a rounded value to determine the number of steps necessary
			print("vabs",velocity_abs)
			if velocity_abs > 1:
				velocity_abs_rnd = int(round(velocity_abs))
				print("velabsrnd",velocity_abs_rnd)
				#print(velocity_abs_rnd)
			#When slope is near zero, I get near divide by zero errors, so I just cut off everything over 50. (tunable)
			if velocity_abs < 0.05:
				velocity_abs_rnd = 1			
			if 0.05 <= velocity_abs <= 1:
				velocity_abs_rnd = int(round(1/velocity_abs,0))
			print("still",int(velocity_abs_rnd))
			#I now add the microsteps to their respective lists. The lists should eventually take the form of tuples.
			#print("vel ",velocity, "velabsrnd ",velocity_abs_rnd)
			for microstep in range(int(velocity_abs_rnd)):
				#print("starting microstep ",microstep)
				#print("abs vel rnd ", velocity_abs_rnd)
				if velocity < 0:
					left_dir = -1
				else:
					left_dir = 1
				if line_dir == 1:
					right_dir = 1
				else:
					right_dir = -1
				
				#print(PixelMasterDict)
				#Pull the previous steps out of the masterlist.
				leftstep = PixelMasterDict[-1][1]
				rightstep = PixelMasterDict[-1][2]
				#print("old ",leftstep,rightstep)
				#iterate over the steps and put them in the tuple
				if velocity_abs > 1:
					leftstep = leftstep + left_dir
					#rightstep = rightstep + int(round(right_dir*((microstep+1)/velocity_abs_rnd),0))
				if velocity_abs < 0.02:
					rightstep = rightstep + right_dir
				if 0.02 <= velocity_abs <= 1 :
					rightstep = rightstep + right_dir
					#leftstep = leftstep + int(round(left_dir*((microstep+1)/velocity_abs_rnd),0))
				if microstep == (velocity_abs_rnd-1):
					#print("last microstep")
					if velocity_abs > 1:
						rightstep += 1
					else:
						leftstep += 1
				#Create tuple and append to Master Dict
				#print("new ",leftstep,rightstep)
				microtuple = (PixelMasterDict[-1][0]+1,leftstep % 8,rightstep % 8)
				print(microtuple)
				PixelMasterDict.append(microtuple)
				
			###### DEFINE THE ACTUAL MOVEMENT FUNCTIONS
			
			def left_move(leftstep):
				StepCounter=leftstep
				for pin in range(0, 4):
					pin = StepPins_left[pin]
					if Seq[StepCounter][pin]!=0:
						GPIO.output(xpin, True)
					else:
						GPIO.output(xpin, False)
						
			def right_move(rightstep):
				StepCounter=rightstep
				for pin in range(0, 4):
					pin = StepPins_left[pin]
					if Seq[StepCounter][pin]!=0:
						GPIO.output(xpin, True)
					else:
						GPIO.output(xpin, False)
			
			#Iterate through the master list to do the steps one at a time.
						
			if velocity_abs < 1:
				step = step + velocity_abs_rnd
			else : 
				step = step + 1
		return PixelMasterDict		
	PixelMasterDict = plot_pixel(5,70,2,1)
			
	#dirlist_left, vellist_right = plot_pixel(5,200,1)
			
if __name__ == '__main__':
	main()