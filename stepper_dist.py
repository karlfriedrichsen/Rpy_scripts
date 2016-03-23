#!/usr/bin/python
#--------------------------------------
#    ___  ___  _ ____          
#   / _ \/ _ \(_) __/__  __ __ 
#  / , _/ ___/ /\ \/ _ \/ // / 
# /_/|_/_/  /_/___/ .__/\_, /  
#                /_/   /___/   
#
#    Stepper Motor Test
#
# A simple script to control
# a stepper motor.
#
# Author : Matt Hawkins
# Date   : 28/09/2015
#
# http://www.raspberrypi-spy.co.uk/
#
#--------------------------------------

# Import required libraries
import sys
import time
import RPi.GPIO as GPIO

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO signals to use
# Physical pins 11,15,16,18
# GPIO17,GPIO22,GPIO23,GPIO24
if (sys.argv[3]) == "L":
	StepPins = [18,27,20,21]
if (sys.argv[3]) == "R":
	StepPins=[17,22,23,24]

StepPins_L = [18,27,20,21]
StepPins_R = [17,22,23,24]
steptotal = int(sys.argv[4])	
StepPins_setup = StepPins_L+StepPins_R
	
# Set all pins as output
for pin in StepPins_setup:
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin, False)

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
StepDir = 1 # Set to 1 or 2 for clockwise
            # Set to -1 or -2 for anti-clockwise

# Read wait time from command line
if len(sys.argv)>1:
  WaitTime = int(sys.argv[1])/float(1000)
  StepDir = int(sys.argv[2])
else:
  WaitTime = 10/float(1000)

# Initialise variables
StepCounter = 0

# Start main loop
for i in range(0,steptotal):
  #print StepCounter,
  #print Seq[StepCounter]
	if (sys.argv[3]) == "B":
		for pin in range(0,4):
			xpin1 = StepPins_L[pin]
			xpin2 = StepPins_R[pin]
			if Seq[StepCounter][pin]!=0:
				#print " Enable GPIO %i" %(xpin)
				GPIO.output(xpin1, True)
				GPIO.output(xpin2, True)
			else:
				GPIO.output(xpin1, False)
				GPIO.output(xpin2, False)
	else:
		for pin in range(0, 4):
			xpin = StepPins[pin]
			if Seq[StepCounter][pin]!=0:
				#print " Enable GPIO %i" %(xpin)
				GPIO.output(xpin, True)
			else:
				GPIO.output(xpin, False)
	StepCounter += StepDir
	if (StepCounter>=StepCount):
		StepCounter = 0
	if (StepCounter<0):
		StepCounter = StepCount+StepDir
	time.sleep(WaitTime)
GPIO.cleanup()