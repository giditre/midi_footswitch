import RPi.GPIO as GPIO
from time import sleep
from os import system

# TODO: if previous configuration found, ask if ok to erase it

GPIO.setmode(GPIO.BOARD)

# TODO: create variables input and output lists
# TODO: create dictionary associating symbolic name of button/LED with pin number

# setting inputs
GPIO.setup([12,18,32,11,13], GPIO.IN, pull_up_down=GPIO.PUD_UP)
# setting output
GPIO.setup([7,16,22,15,29,31], GPIO.OUT, initial=GPIO.LOW)

# TODO: check that ZOOM is connected and on which port

try:
    while True:
        for i in [12,18,32,11,13]:
            # TODO: debounce
            if GPIO.input(i) == GPIO.LOW:
                print('Pin ' + str(i) + ' is LOW.')
                # TODO: act on ZOOM via amidi
                if i == 12:
                    GPIO.output(7, 1)
                    system('amidi --port="hw:1,0,0" -S C020')
                elif i == 18:
                    GPIO.output(16, 1)
                    system('amidi --port="hw:1,0,0" -S C021')               
                elif i == 32:
                    GPIO.output(22, 1)
                    system('amidi --port="hw:1,0,0" -S C022')               
                while GPIO.input(i) == GPIO.LOW:
                    sleep(0.01)
        sleep(0.01)
except:
    print('\n\nClean up and exit.\n')
    GPIO.cleanup()
