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

# additional global variabled
demo = False
current_state = 0
previous_state = 0
states = {
  0: 0,
  1: 0,
  2: 0
}
dev_port = ''
 
# read GPIO g
def gin(g):
  return GPIO.input(g)

# write value v on GPIO g
def gout(g, v):
  #if GPIO.gpio_function(g) == GPIO.OUT:
  if gin(g) != v:
    GPIO.output(g,v)

# toggle output value of 
def gtog(g):
  #if GPIO.gpio_function(g) == GPIO.OUT:
  gout(g, not gin(g))

def all_leds_off():
  for g in outputs:
    gout(g, out_False)

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

def mout(port, code, demo=False):
  if not demo:
    bash_cmd('amidi -p ' + port + ' -S ' + code)

def discover():
  global demo
  global dev_port
  # do the following check periodically, until a ZOOM device is found or an input combination is met, starting demo mode
  # check that ZOOM is connected and on which port
  print('Start device discovery')
  while not dev_port:
    # check if user requests demo mode
    if lsw_pos() == 2 and gin(fsw1) == in_True and gin(fsw3) == in_True:
      print('Ignore ZOOM device and continue in demo mode')
      demo = True
      supercar(1)
      while gin(fsw1) == in_True or gin(fsw3) == in_True:
        sleep(0.2)
      # return after setting demo mode
      return
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
        circle(1)
      print('')

def set_state(s):
  global states
  states[2] = states[1]
  states[1] = states[0]
  states[0] = s
    
def get_state(i):
  global states
  if i in [0, -1, -2]:
    i = i*(-1)
    return states[i]

def transition(s):
  '''
  There are 9 possible states: [11,12,13,21,22,23,31,32,33]
  The first digit represents LSW position, the second digit represents last FSW pressed
  '''
  global dev_port
  global demo
  global states
  # update states dict
  set_state(s)
  # store in l the LSW position and in f the last FSW pressed
  new_l, new_f = divmod(s, 10)
  old_l, old_f = divmod(get_state(-1), 10)
  older_l, older_f = divmod(get_state(-2), 10)
  if new_l == old_l and new_f == 0:
    # we reach here if the footswitch has been released after being pressed
    print("FSW{} released".format(str(old_f)))
    return
  if new_l == older_l and new_f == older_f:
    # we reach here if the same footswitch has been pressed again
    print("FSW{} pressed again".format(str(new_f)))
    return
  # we reach here if either the lever has been moved or a different footswitch has been pressed
  print("Transition to state {} [ LSW{}+FSW{} ]".format(str(s), str(new_l), str(new_f)))
  all_leds_off()
  if new_l == 1:
    gout(led1, out_True)
    if new_f == 1:
      gout(led4, out_True)
      mout(dev_port, 'C000', demo)
    elif new_f == 2:
      gout(led5, out_True)
      mout(dev_port, 'C001', demo)
    elif new_f == 3: 
      gout(led6, out_True)
      mout(dev_port, 'C002', demo)
    else:  # default preset for this bank
      gout(led4, out_True)
      mout(dev_port, 'C000', demo)
  elif new_l == 2:
    gout(led2, out_True)
    if new_f == 1:
      gout(led4, out_True)
      mout(dev_port, 'C003', demo)
    elif new_f == 2:
      gout(led5, out_True)
      mout(dev_port, 'C004', demo)
    elif new_f == 3:
      gout(led6, out_True)
      mout(dev_port, 'C005', demo)
    else:  # default preset for this bank
      gout(led4, out_True)
      mout(dev_port, 'C003', demo)
  elif new_l == 3:
    gout(led3, out_True)
    if new_f == 1:
      gout(led4, out_True)
      mout(dev_port, 'C006', demo)
    elif new_f == 2:
      gout(led5, out_True)
      mout(dev_port, 'C007', demo)
    elif new_f == 3:
      gout(led6, out_True)
      mout(dev_port, 'C008', demo)
    else:  # default preset for this bank
      gout(led4, out_True)
      mout(dev_port, 'C006', demo)

# MAIN      

# print information on state of inputs
debug_print_inputs()
# do device discovery
discover()
# enter infinite loop
try:
  while True:
    # chech lever switch position
    lsw = lsw_pos()
    # check if any footswitch is pressed
    fsw = 1 if gin(fsw1) == in_True else 2 if gin(fsw2) == in_True else 3 if gin(fsw3) == in_True else 0
    # set current_state as explained in transition function
    current_state = 10*lsw + fsw
    # check if state has changed
    if current_state != get_state(0):
      # apply the effects of the transition and update previous_state for next check
      transition(current_state)
      # print(states)
      # block until footswitch is not released
      while fsw:
        fsw = 1 if gin(fsw1) == in_True else 2 if gin(fsw2) == in_True else 3 if gin(fsw3) == in_True else 0
        sleep(0.03)
    # sleep some time before checking input again
    sleep(0.03)
except KeyboardInterrupt:
  print('\n\nClean up and exit.\n')
  GPIO.cleanup()

