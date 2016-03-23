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
	
	###########################################################################
	# THIS WILL PROCESS THE IMAGE
	###########################################################################
	
	def image_proc(imagefilename,xdimension,ydimension):
		from wand.image import Image
		import PIL
		from PIL import Image as Image2
		#imagefilename = 'Simple-Landscape.png'
		with Image(filename=imagefilename) as img:
			img.type = 'grayscale'
			img.resize(xdimension,ydimension)
			img.save(filename=imagefilename[:-4]+"_gray.jpg")
			#img.depth=1
			xdim, ydim = img.size
		img = Image2.open(imagefilename[:-4]+"_gray.jpg")
		pix = img.load()
		xpix = 1
		ypix = 1
		pixcounter = 1
		plotlist = [(0,0)]
		diaglengthlist = list(range(0,xdim))
		topcorner = [xdim]
		print(diaglengthlist)
		diaglengthlist = diaglengthlist[:-2] + diaglengthlist[::-1]
		print(diaglengthlist)
		####### Here is the building of the brightness list ##########
		for diaglength in diaglengthlist:

			print(diaglength)
			#UPRIGHT
			if int(diaglength) % 2 == 1:
				direction=1
				print("upright")
				xpix = 1
				ypix = diaglength
				xpixadd = 1
				ypixadd = -1
			#DOWNLEFT
			if int(diaglength) % 2 == 0:
				direction=-1
				print("downleft")
				ypix = 1
				xpix = diaglength
				xpixadd = -1
				ypixadd = 1
				
			for diagpos in range(0,diaglength):
				print(pixcounter,":",xpix, ypix)
				brightness=(pix[xpix,ypix])
				xpix = xpix + xpixadd
				ypix = ypix + ypixadd
				pixcounter = pixcounter + 1
				brightdirtuple = (brightness,direction)
				plotlist.append(brightdirtuple)
		
			#UPRIGHT
			if int(diaglength) % 2 == 1:
				uptup = ('DOWN',0)
				plotlist.append(uptup)
			#DOWNLEFT
			if int(diaglength) % 2 == 0:
				downtup = ('RIGHT',0)
				plotlist.append(downtup)
			pixcounter = pixcounter + 1
		
		#WRITE TO THE LOG FILE WHAT YOU DID
		with open('logfile_img.csv', 'w', newline='') as logfile_img:
			wr = csv.writer(logfile_img, quoting=csv.QUOTE_ALL )
			wr.writerow(plotlist)
			
		return plotlist
				
	###########################################################################
	# DEFINE THE ACTUAL MOVEMENT FUNCTIONS
	###########################################################################
	def left_move(leftstep):
		Seq = [[1,0,0,1],
			[1,0,0,0],
			[1,1,0,0],
			[0,1,0,0],
			[0,1,1,0],
			[0,0,1,0],
			[0,0,1,1],
			[0,0,0,1]]
		StepPins_left=[18,27,20,21]
		StepPins_right=[17,22,23,24]
		StepCounter=int(leftstep)
		for pin in range(0, 4):
			xpin = StepPins_left[pin]
			if Seq[StepCounter][pin]!=0:
				GPIO.output(xpin, True)
			else:
				GPIO.output(xpin, False)
				
	def right_move(rightstep):
		Seq = [[1,0,0,1],
			[1,0,0,0],
			[1,1,0,0],
			[0,1,0,0],
			[0,1,1,0],
			[0,0,1,0],
			[0,0,1,1],
			[0,0,0,1]]
		StepPins_left=[18,27,20,21]
		StepPins_right=[17,22,23,24]
		StepCounter=int(rightstep)
		for pin in range(0, 4):
			xpin = StepPins_right[pin]
			if Seq[StepCounter][pin]!=0:
				GPIO.output(xpin, True)
			else:
				GPIO.output(xpin, False)
	
	###########################################################################
	#This determines the movement of the plotter
	###########################################################################
	
	#I will be using pixdim in mm, and brightness in a 0-255 value.
	#base_speed is the lowest delay. line_dir is which direction your pixel line is going. 1 is up to the right.
	def plot_pixel(pixdim,brightness,base_speed,line_dir):
		#This is necessary for ideGPIO.setmode(GPIO.BCM)
		#Set the physical pin numbers
		GPIO.setmode(GPIO.BCM)
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
		Lefttracker=0
		Righttracker=0
		#base_delay is the base speed in milliseconds for step-delay of the fast motor
		base_delay=base_speed/float(1000)
		#This is the pixel size determinant. When you are able to test it on a larger scale,
		#make this a more accurate value. I'm nominally starting with 1000 steps = 10 mm.
		steptotal = 100 * pixdim
		#The amplitude of the peaks
		pix = steptotal / 2
		#The number of lines within #######CHANGE THIS TONIGHT!!!!################
		squiggle = ((brightness/255)*.65*steptotal)+(0.1*steptotal)		
		#Create all necessary lists
		StepCounter_left = 0
		StepCounter_right = 0
		PixelMasterDict = [(0,0,0)]
		while ( step < steptotal ) :
			#print("start big step ",step)
			#This calculates the instantaneous velocity of the plotter
			#First, the speed and direction of the next step is determined. 
			#Then the motor which will be moving faster is scaled to a max velocity(base_delay) (adjustable)
			#The other motor is scaled by it's ratio to the faster motor.
			#The limiting factor is that one calculation is done for each microstep along a diagonal of the pixel.
			velocity = -((step-pix)*math.sin(3*math.pi*step/squiggle))/(math.sqrt((step-pix)**2)+0.00000001)-(3/squiggle)*math.pi*(math.sqrt((step-pix)**2)-pix)*math.cos(3*math.pi*step/squiggle)
			#If velocity is over 1, motor_left is faster, if it is under 1, motor_right is faster. The faster motor is scaled to base_delay.
			velocity_abs = abs(velocity)
			#I need a rounded value to determine the number of steps necessary
			#print("vabs",velocity_abs)
			if velocity_abs > 1:
				velocity_abs_rnd = int(round(velocity_abs))
				#print("velabsrnd",velocity_abs_rnd)
				#print(velocity_abs_rnd)
			#When slope is near zero, I get near divide by zero errors, so I just cut off everything over 50. (tunable)
			if velocity_abs < 0.05:
				velocity_abs_rnd = 1			
			if 0.05 <= velocity_abs <= 1:
				velocity_abs_rnd = int(round(1/velocity_abs,0))
			#print("still",int(velocity_abs_rnd))
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
					#print("GOING DOWN")
					right_dir = -1
				
				#print(PixelMasterDict)
				#Pull the previous steps out of the masterlist.
				leftstep = PixelMasterDict[-1][1]
				rightstep = PixelMasterDict[-1][2]
				#print("old ",leftstep,rightstep)
				#iterate over the steps and put them in the tuple
				if velocity_abs > 1:
					leftstep = leftstep + left_dir
					Lefttracker += left_dir
					#rightstep = rightstep + int(round(right_dir*((microstep+1)/velocity_abs_rnd),0))
				if velocity_abs < 0.02:
					rightstep = rightstep + right_dir
				if 0.02 <= velocity_abs <= 1 :
					rightstep = rightstep + right_dir
					Righttracker += right_dir
					#leftstep = leftstep + int(round(left_dir*((microstep+1)/velocity_abs_rnd),0))
				if microstep == (velocity_abs_rnd-1):
					#print("last microstep")
					if velocity_abs > 1:
						rightstep = rightstep + right_dir
						Righttracker += right_dir
					else:
						leftstep = leftstep + left_dir
						Lefttracker += left_dir
				#Create tuple and append to Master Dict
				#print("new ",leftstep,rightstep)
				microtuple = (PixelMasterDict[-1][0]+1,leftstep % 8,rightstep % 8)
				#print(rightstep)
				#print(rightstep%8)
				#print(microtuple)
				PixelMasterDict.append(microtuple)
				
		
			#Iterate through the master list to do the steps one at a time.
						
			if velocity_abs < 1:
				step = step + velocity_abs_rnd
			else : 
				step = step + 1
		
		for step in PixelMasterDict:
			#print(step)
			left_move(int(step[1]))
			right_move(int(step[2]))
			#print(step[1],step[2])
			time.sleep(base_delay)
		#print(leftstep)
		#print(Lefttracker)
		print("Left Error = ",Lefttracker)
		print("Right Error = ",abs(Righttracker)-steptotal)
		
		if Lefttracker > 0:
			for step in range(1,Lefttracker):
				# #print("correcting...")
				left_move(int(7-(step%8)))
				time.sleep(base_delay)
		else:
			for step in range(1,-Lefttracker):
				left_move(int(step%8))
				time.sleep(base_delay)
		
		Rightcorrect = abs(Righttracker)-steptotal
		if Rightcorrect < 0:
			if Righttracker < 0:
				for step in range(1,abs(Rightcorrect)):
					right_move(int(7-(step%8)))
					time.sleep(base_delay)
			else:
				for step in range(1,abs(Rightcorrect)):
					right_move(int(step%8))
					time.sleep(base_delay)
		else:
			if Righttracker < 0:
				for step in range(1,abs(Rightcorrect)):
					right_move(int(step%8))
					time.sleep(base_delay)
			else:
				for step in range(1,abs(Rightcorrect)):
					left_move(int(7-(step%8)))
					time.sleep(base_delay)
		GPIO.cleanup()
		return PixelMasterDict
		
		
	########################################################
	#      HERE IS THE DROPPER FOR THE END OF THE LINE 
	########################################################
	
	####The direction is given in plain text caps "RIGHT" "DOWN"
	def move_pointer(pixdim,dir):
		#This is necessary for ideGPIO.setmode(GPIO.BCM)
		#Set the physical pin numbers
		GPIO.setmode(GPIO.BCM)
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
		leftstep=0
		rightstep=0
		#base_delay is the base speed in milliseconds for step-delay of the fast motor
		base_delay = 2/float(1000)
		dropdim = int(round(pixdim/math.sqrt(2))*100)
		leftstep=dropdim
		rightstep=dropdim
		if dir == "DOWN":
			for step in range(1,dropdim):
				#print(leftstep%8)
				#print(rightstep%8)
				left_move(leftstep%8)
				right_move(rightstep%8)
				leftstep = leftstep - 1
				rightstep = rightstep - 1
				step = step - 1
				time.sleep(base_delay)
		if dir == "RIGHT":
			for step in range(1,dropdim):
				#print(leftstep%8)
				#print(rightstep%8)
				left_move(leftstep%8)
				right_move(rightstep%8)
				leftstep = leftstep - 1
				rightstep = rightstep + 1
				step = step - 1
				time.sleep(base_delay)
				
	################################################
				
	plotlist = image_proc('TestRose2.jpg',10,10)
	#print(plotlist[-10:])
	for step in range(0,len(plotlist)):
		brightness = plotlist[int(step)][0]
		direction = plotlist[int(step)][1]
		print(plotlist[step])
		if brightness == 'RIGHT':
			print("RIGHT")
			move_pointer(5,"RIGHT")
		if brightness == 'DOWN':
			print("DOWN")
			move_pointer(5,"DOWN")
		else:
			print(direction)
			plot_pixel(5,step,1,direction)
	
	################################################
	
	#for i in range(10,160,25):
	#	PixelMasterDict = plot_pixel(10,i,1,-1)
	#move_pointer(12,"E")
	#move_pointer(12,"S")
	#for i in range(50,150,50):
	# for i in range(0,25):
		# if i % 2 == 1:
			# direction = 1
		# else:
			# direction = -1
		# bright=i*10
		# PixelMasterDict = plot_pixel(5,bright,1,direction)
	
if __name__ == '__main__':
	main()