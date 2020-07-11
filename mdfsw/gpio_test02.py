import RPi.GPIO as GPIO
from time import sleep
from os import system
from subprocess import Popen, PIPE


def bash_cmd(cmd, cmd_print=False, out_print=False):
  if cmd_print:
    print('Executing command:\n' + cmd)
  proc = Popen(cmd.split(), stdout=PIPE)
  out, err = proc.communicate()
  out = str(out,'utf-8')
  if out_print:
    print('Command output:\n' + out)
  return out


# TODO: if previous configuration found, ask if ok to erase it

GPIO.setmode(GPIO.BOARD)

# create variables for inputs and outputs
# inputs and outputs diagram
'''
 ____________________________________________________________
|                                                            |
|   (lsw1)--O  (lsw2)      (led1)     (led2)     (led3)      |
|                                                            |
|         (led4)         (led5)         (led6)               |
|              (fsw1)         (fsw2)         (fsw3)          |
|____________________________________________________________|

'''
# footswitches
fsw1 = 12
fsw2 = 18
fsw3 = 32
# lever switch
lsw1 = 13
lsw2 = 11
# LED in the top row
led1 = 15
led2 = 29
led3 = 31
# LED in the bottom row
led4 = 7
led5 = 16
led6 = 22

inputs = {
  fsw1: 'FSW1',
  fsw2: 'FSW2',
  fsw3: 'FSW3',
  lsw1: 'LSW1',
  lsw2: 'LSW2'
}
outputs = {
  led1: 'LED1',
  led2: 'LED2',
  led3: 'LED3',
  led4: 'LED4',
  led5: 'LED5',
  led6: 'LED6'
}

# configure inputs
GPIO.setup(list(inputs.keys()), GPIO.IN, pull_up_down=GPIO.PUD_UP)
# configure outputs
GPIO.setup(list(outputs.keys()), GPIO.OUT, initial=GPIO.LOW)

# map LOGICAL TRUE VALUE for INPUT to GPIO voltage level
in_True = GPIO.LOW
# the LOGICAL FALSE VALUE for INPUT is a consequence of the other logical value
in_False = GPIO.LOW if in_True == GPIO.HIGH else GPIO.HIGH

# map LOGICAL TRUE VALUE for OUTPUT to GPIO voltage level
out_True = GPIO.HIGH
# the LOGICAL FALSE VALUE for OUTPUT is a consequence of the other logical value
out_False = GPIO.LOW if out_True == GPIO.HIGH else GPIO.HIGH

# read GPIO g
def gin(g):
  return GPIO.input(g)

# write value v on GPIO g
def gout(g, v):
  #if GPIO.gpio_function(g) == GPIO.OUT:
  GPIO.output(g,v)

# toggle output value of 
def gtog(g):
  #if GPIO.gpio_function(g) == GPIO.OUT:
  gout(g, not gin(g))

def supercar(t):
  for g in outputs:
    gout(g, out_False)
  for g in [led1, led2, led3, led4, led5, led6]:
    gout(g, out_True)
    sleep(t/6)
    gout(g, out_False)

def circle(t):
  for g in outputs:
    gout(g, out_False)
  for g in [led1, led2, led3, led6, led5, led4]:
    gout(g, out_True)
    sleep(t/6)
    gout(g, out_False)

def zigzag(t):
  for g in outputs:
    gout(g, out_False)
  for g in [led1, led4, led2, led5, led3, led6]:
    gout(g, out_True)
    sleep(t/6)
    gout(g, out_False)

def lsw_pos():
  if gin(lsw1) == in_True and gin(lsw2) == in_False:
    return 1
  elif gin(lsw1) == in_False and gin(lsw2) == in_False:
    return 2
  elif gin(lsw1) == in_False and gin(lsw2) == in_True:
    return 3

def debug_print_inputs():
  print('[DEBUG] input:state -> ', end='')
  for i in inputs.keys():
    print(inputs[i] + ':{} '.format('TRUE' if gin(i) == in_True else 'FALSE'), end='')
  print('')
      

debug_print_inputs()

print('Press FSW2 to continue...')
gout(led5, out_False)
while gin(fsw2) == in_False:
  gtog(led5)
  sleep(0.25)
  if gin(fsw2) == in_True:
    gout(led5, out_False) 
    break
while gin(fsw2) == in_True:
  sleep(0.25)
 

# do the following check periodically, until a ZOOM device is found or an input combination is met, starting demo mode
# check that ZOOM is connected and on which port
dev_port = ''
demo = False
print('Start device discovery')
while not dev_port:
  # check if user requests demo mode
  if lsw_pos() == 2 and gin(fsw1) == in_True and gin(fsw3) == in_True:
    print('Ignore ZOOM device and continue in demo mode')
    demo = True
    supercar(1)
    while gin(fsw1) == in_True or gin(fsw3) == in_True:
      sleep(0.2)
    break
  # look for connected ZOOM devices
  amidi_list = [line for line in bash_cmd('amidi -l').split('\n') if 'ZOOM' in line]
  if amidi_list:
    if len(amidi_list) == 1:
      dev_port = amidi_list[0].split()[1]
      dev_name = amidi_list[0].split(dev_port)[1].strip()
      print('Found device ' + dev_name + ' on port ' + dev_port)
    elif len(amidi_list) > 1:
      sys.exit('Connect only one ZOOM device at a time!')
  else:
    print('ZOOM device not found. Wait some seconds before retrying', end='')
    for i in range(3):
      print('.', end='')
      sleep(1)
    print('')
    
try:
  while True:
    lsw = lsw_pos()
    if lsw == 1:
      if gin(fsw1) == in_True:
        print('LSW1+FSW1')
        gout(led1, out_True)
        gout(led4, out_True)
        system('amidi --port="hw:1,0,0" -S C000')
        while gin(fsw1) == in_True:
          sleep(0.01)
      elif gin(fsw2) == in_True:
        print('LSW1+FSW2')
        gout(led1, out_True)
        gout(led5, out_True)
        system('amidi --port="hw:1,0,0" -S C001')
        while gin(fsw2) == in_True:
          sleep(0.01)
      elif gin(fsw3) == in_True: 
        print('LSW1+FSW3')
        gout(led1, out_True)
        gout(led6, out_True)
        system('amidi --port="hw:1,0,0" -S C002')
        while gin(fsw3) == in_True:
          sleep(0.01)
    elif lsw == 2:
      if gin(fsw1) == in_True:
        print('LSW2+FSW1')
        gout(led2, out_True)
        gout(led4, out_True)
        system('amidi --port="hw:1,0,0" -S C003')
        while gin(fsw1) == in_True:
          sleep(0.01)
      elif gin(fsw2) == in_True:
        print('LSW2+FSW2')
        gout(led2, out_True)
        gout(led5, out_True)
        system('amidi --port="hw:1,0,0" -S C004')
        while gin(fsw2) == in_True:
          sleep(0.01)
      elif gin(fsw3) == in_True:
        print('LSW2+FSW3')
        gout(led2, out_True)
        gout(led6, out_True)
        system('amidi --port="hw:1,0,0" -S C005')
        while gin(fsw3) == in_True:
          sleep(0.01)
    elif lsw == 3:
      if gin(fsw1) == in_True:
        print('LSW3+FSW1')
        gout(led3, out_True)
        gout(led4, out_True)
        system('amidi --port="hw:1,0,0" -S C006')
        while gin(fsw1) == in_True:
          sleep(0.01)
      elif gin(fsw2) == in_True:
        print('LSW3+FSW2')
        gout(led3, out_True)
        gout(led5, out_True)
        system('amidi --port="hw:1,0,0" -S C007')
        while gin(fsw2) == in_True:
          sleep(0.01)
      elif gin(fsw3) == in_True:
        print('LSW3+FSW3')
        gout(led3, out_True)
        gout(led6, out_True)
        system('amidi --port="hw:1,0,0" -S C008')
        while gin(fsw3) == in_True:
          sleep(0.01)
    # wait before scanning inputs again
    sleep(0.01)
except:
  print('\n\nClean up and exit.\n')
  GPIO.cleanup()

