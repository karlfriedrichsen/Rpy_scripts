#!/usr/bin/python

##HERE IS A TEST OF HOW TO USE MODULES AND CLASSES AND SHIT
#___________________________________
def main():
	#import necessary things
	import math
	import sys
	import time
	import RPi.GPIO as GPIO
	import csv
	GPIO.setmode(GPIO.BCM)
	#This determines the movement of the plotter
	#I will be using pixdim in mm, and brightness in a 0-255 value.
	def plot_pixel(pixdim, brightness,speed):
		#This is necessary for ideGPIO.setmode(GPIO.BCM)
		#Set the physical pin numbers
		StepPins_left=[18,27,20,21]
		StepPins_right=[17,22,23,24]
		StepPins_all = StepPins_left+StepPins_right
		#enable all the pins for writing and make sure they are off
		for pin in StepPins_all:
			GPIO.setup(pin,GPIO.OUT)
			GPIO.output(pin,False)
		# Define advanced sequence
		# as shown in manufacturers datasheet
		Seq = [[1,0,0,1],
			[1,0,0,0],
			[1,1,0,0],
			[0,1,0,0],
			[0,1,1,0],
			[0,0,1,0],
			[0,0,1,1],
			[0,0,0,1]]
		StepCount = len(Seq)
		
		#This determines the overall speed of the drawing process.
		speed_multiplier = 10**(4-speed)		
		
		#The plan is to take the brightness and use it to control the speed
		#While the amplitude of the squiggle motor is controled at a constant speed
				
		#This is the pixel size determinant. When you are able to test it on a larger scale,
		#make this a more accurate value. I'm nominally starting with 1000 steps = 10 mm.
		steptotal = 100 * pixdim
		#print(steptotal)
		#The amplitude of the peaks
		pix = steptotal / 2
		#The number of lines within #######CHANGE THIS TONIGHT!!!!################
		squiggle = 260-brightness
		#Speed for the left motor
		left_wait = speed_multiplier*5/float(1000)
		print(left_wait)
		dirlist_left = [0]
		vellist_right = [0]
		Steplist_left = [0]
		Steplist_right = [0]		
		
		#################### DEFINE THE MOVEMENT ########################
		
		def left_move(left_dir,left_wait,StepCounter_left):
			for pin in range(0, 4):
				lpin = StepPins_left[pin]
				if Seq[StepCounter_left][pin]!=0:
					GPIO.output(lpin, True)
				else:
					GPIO.output(lpin, False)
			StepCounter_left=StepCounter_left+left_dir
			time.sleep(left_wait)
			#return StepCounter_left
		
		def right_move(right_dir,right_wait,StepCounter_right):
			for pin in range(0, 4):
				rpin = StepPins_right[pin]
				if Seq[StepCounter_right][pin]!=0:
					GPIO.output(rpin, True)
				else:
					GPIO.output(rpin, False)
			StepCounter_right=StepCounter_right+right_dir
			time.sleep(right_wait)
			#return StepCounter_right
				
		################ DRAW A PIXEL ######################
		logfile = "pixel_plot.log"
		open(logfile, 'w')
		for step in range(steptotal):
			StepCounter_left=0
			StepCounter_right=0
			#print(range(steptotal))
			#print(step)
			#This calculates the instantaneous velocity of the plotter. I won't speed up the squiggle,
			#so I will inverse this to make the brightness motor slow down accordingly.
			velocity = -((step-pix)*math.sin(3*math.pi*step/squiggle))/(math.sqrt((step-pix)**2)+0.00000001)-(3/squiggle)*math.pi*(math.sqrt((step-pix)**2)-pix)*math.cos(3*math.pi*step/squiggle)
			right_wait = round(speed_multiplier*velocity/float(1000),6)
			#print(type(right_wait))
			if right_wait < 0 :
				right_wait=-right_wait
				left_dir=(-1)
			else:
				left_dir=1
			right_dir=1
			#print(round(velocity,5))
			#print(right_wait)
			dirlist_left.append(left_dir)
			vellist_right.append(right_wait)
			if Steplist_left[-1] > 7:
				Steplist_left[-1] = 0
			if Steplist_left[-1] < 0:
				Steplist_left[-1] = 7
			Steplist_left.append(Steplist_left[-1]+left_dir)
			Steplist_right.append(right_dir)
			#print(dirlist_left)
			#print(vellist_right)
			StepCounter_left=0
			StepCounter_right=0
			
		#print(dirlist_left)
		for i in range(steptotal):
			pass
			#print(dirlist_left[i],Steplist_left[i])
			#left_move(dirlist_left[i],left_wait,Steplist_left[i])
		listscsv = zip(Steplist_left,Steplist_right,dirlist_left,vellist_right)
		writer = csv.writer(logfile)
		for row in listscsv:
			writer.writerow(row)
			
		
	plot_pixel(20,100,3)
	GPIO.cleanup()
	#print(vellist_right,'\n',dirlist_left)
	#dirlist_left, vellist_right = plot_pixel(5,200,1)
			
if __name__ == '__main__':
	main()