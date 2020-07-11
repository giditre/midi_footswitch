import pygame
import serial      # Get the Serial library
import random
from random import *
ser=serial.Serial('/dev/ttyAMA0',31250)  # Set up the UART  
pygame.init()
clock = pygame.time.Clock()
channel=1
note_on=0x90 + channel -1   # Build the command byte
note_off=0x80 + channel -1   # Build the command byte
all_note_off=0xB0 + channel -1 # Build the command byte

dt = 0 
while True:     # set up a loop...
    accept=raw_input("  HOW MANY STEPS?  ")
    if accept > 0:    # Happy with this ?
 
        ## RESET MIDI CHANNEL AND SET TO PIANO  
        for channel in range(1,17):
            all_note_off=0xB0 + channel -1 # Build the command byte
            message = chr(all_note_off)+chr(123)+chr(0)  # all_note_off to reset
            ser.write(message)
            if channel <> 10:
                progchange=0xC0 + channel -1   # Build the command byte
                message = chr(progchange)+chr(randint(0,127))  # random instument
                ser.write(message)
        
        
        for x in range (1,int(accept)):
        
            channel = randint(1,16)
            note_on=0x90 + channel -1       # Build the note_on byte
            note_off=0x80 + channel -1      # Build the note_off byte
            progchange=0xC0 + channel -1     # Build the progchange byte
            pitchbend=0xE0 + channel -1     # Build the progchange byte
            
            
            value = randint(77,127)
            note = randint(0,127)
            
            message=chr(note_on) + chr(note) + chr(value) + chr(note_on) + chr(note+4-randint(0,2)) + chr(value) + chr(note_on) + chr(note+7) + chr(value)
            ser.write(message)   # then transmit the message
            dt = clock.tick(randint(1,20))
            print "Chord Step:"+ str(x) + " Channel:" + str(channel) +" Note:"+str(note)+" Velocity:"+str(value)+" Length:" + str(dt)
            
            if randint (1,10) > 3:
                message=chr(note_off) + chr(note) + chr(value)
                ser.write(message)   # then transmit the note off message
                print "Note off - Step:"+ str(x) + " Channel:" + str(channel) +" Note:"+str(note)+" Velocity:"+str(value)+" Length:" + str(dt)
                
            if randint (1,100) == 80:
                for d in range (1, randint(1,44),randint(1,10)):
                    message=chr(note_on) + chr(note+d) + chr(value)
                    ser.write(message) 
                    dt = clock.tick(randint(1,20))
                    message=chr(note_off) + chr(note+d) + chr(value)
                    print "Run up - Step:"+ str(x) + " Channel:" + str(channel) +" Note:"+str(note)+" Velocity:"+str(value)+" Length:" + str(dt)
                    ser.write(message)   # then transmit the note off message
            
            if randint (1,100) == 90:
                for c in range (randint(2,44),0,-randint(1,10)):
                    message=chr(note_on) + chr(note+c) + chr(value)
                    ser.write(message) 
                    dt = clock.tick(randint(1,20))
                    message=chr(note_off) + chr(note+c) + chr(value)
                    print "Run down - Step:"+ str(x) + " Channel:" + str(channel) +" Note:"+str(note)+" Velocity:"+str(value)+" Length:" + str(dt)
                    ser.write(message)   # then transmit the note off message
            
            if randint (1,100) > 98:
                print "SOLO - Step:"+ str(x) + " Channel:" + str(channel) +" Note:"+str(note)+" Velocity:"+str(value)+" Length:" + str(dt)
                for c in range (0,randint(30,150)):
                    mnote = randint(25,95)
                    value = randint(60,127)
                    message=chr(note_on) + chr(mnote) + chr(value) + chr(note_on) + chr(mnote+12) + chr(value)
                    ser.write(message) 
                    dt = clock.tick(randint(2,30))
                    message=chr(note_off) + chr(mnote) + chr(value) + chr(note_off) + chr(mnote+12) + chr(value)
                    ser.write(message)   # then transmit the note off message
            
            if randint (1,1000) < 10:
                print "~~~~~~~~~ All notes off - all channels ~~~~~~~~~"
                for channel in range(1,17):
                    all_note_off=0xB0 + channel -1 # Build the command byte
                    message = chr(all_note_off)+chr(123)+chr(0)  # all_note_off to reset
                    ser.write(message)        
            # Pitchbend    
            if randint (1,100) > 99:    
                print " ++++++++++++ Pitchbend Up +++++++++++++ " 
                for n in range (0,127):
                    dt = clock.tick(randint(50,100))
                    message=chr(pitchbend) + chr(n) + chr(n) 
                    ser.write(message)
                message = chr(all_note_off)+chr(121)+chr(0)  # all_note_off to reset
                ser.write(message)        
                
            if randint (1,100) > 99:    
                print " ++++++++++++ Pitchbend Down +++++++++++++ " 
                for n in range (127,0,-1):
                    dt = clock.tick(randint(50,100))
                    message=chr(pitchbend) + chr(n) + chr(n) 
                    ser.write(message)                      
                message = chr(all_note_off)+chr(121)+chr(0)  # all_note_off to reset
                ser.write(message)            
            
            if randint (1,10) > 9:
                print "All notes off - channel: " +str(channel)
                all_note_off=0xB0 + channel -1 
                message=chr(all_note_off) + chr(0) 
                ser.write(message)   # then transmit the note off message
            
            
            if randint(0,100) > 80 and channel <> 10: 
                message=chr(progchange) + chr(randint(1,127)) 
                ser.write(message)   # then transmit the note off message
                print ">>>>>  Progchange on channel: "+str(channel)+" to "+ str(note) 
            
            
            
        for channel in range(1,17):
            all_note_off=0xB0 + channel -1 # Build the command byte
            message = chr(all_note_off)+chr(123)+chr(0)  # all_note_off to reset
            ser.write(message)﻿