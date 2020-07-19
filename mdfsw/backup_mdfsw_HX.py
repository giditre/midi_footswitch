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

# bash command with real time (line-by-line) output
# in invokes callback on each line of output
# or prints the line if no callback specified
def bash_cmd_rto(cmd, callback=None):
  proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
  while True:
    # read a single line (until newline char) from the output of the command
    # strip it and decode it to string according to utf-8 scheme
    out = proc.stdout.readline().strip().decode('utf-8')
    # output will be empty when the command is done
    # and proc.poll() is not None only when command returns
    if out == '' and proc.poll() is not None:
      break
    if out:
      # if callback method specified, apply it on output
      # otherwise just print the output
      if callback:
        callback(out, cmd)
      else:
        print(out)
  # process.poll contains the return code of the process
  return proc.poll()

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

fsw_to_led = {
  1: led4,
  2: led5,
  3: led6
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

""" additional global variables """
demo = False
'''
state: a 2-digit number where
- the most significant digit is the LSW position
- the least significant digit is the FSW pressed (or 0 if no FSW is pressed)
'''
current_state = 0
previous_state = 0
# key 0: current state, key 1: previous state, key 2: previous state of previous state
states = {
  0: 0,
  1: 0,
  2: 0
}
dev_port = ''
current_patch = -1
# dictionary associating states to pedalboard patch
state_to_patch = {
  11: 0,
  12: 1,
  13: 2,
  21: 3,
  22: 4,
  23: 5,
  31: 6,
  32: 7,
  33: 8
}
# MIDI commands
#enable_edit_mode = 'F052005A50F7'
#disable_edit_mode = 'F052005A51F7'
#request_current_patch = 'F052005A33F7'
#request_info_current_patch = 'F052005A29F7'
state_to_midi_cmd = {
  10: None,
  11: None,
  12: None,
  13: None,
  20: None,
  21: ["B0 47 01", "B0 31 00", "B0 47 03"],
  22: "B04400",
  23: ["B0 47 01", "B0 32 00", "B0 47 03"],
  30: None,
  31: None,
  32: None,
  33: None
}
 
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

def blink(g, t=0.1, cycles=1, inverted=False):
  while cycles:
    gout(g, out_True if not inverted else out_False)
    sleep(t/2)
    gout(g, out_False if not inverted else out_True)
    sleep(t/2)
    cycles = cycles-1

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
    cmd = 'amidi -p ' + port + ' -S ' + code
    print(cmd)
    bash_cmd(cmd)

def discover():
  global demo
  global dev_port
  dev_name = "HX Stomp"
  # do the following check periodically, until a device is found or an input combination is met, starting demo mode
  # check that device is connected and on which port
  print('Start device discovery')
  while not dev_port:
    # check if user requests demo mode
    if lsw_pos() == 2 and gin(fsw1) == in_True and gin(fsw3) == in_True:
      print("Ignore {} device and continue in demo mode".format(dev_name))
      demo = True
      supercar(1)
      while gin(fsw1) == in_True or gin(fsw3) == in_True:
        sleep(0.2)
      # return after setting demo mode
      return
    # look for connected devices
    amidi_list = [line for line in bash_cmd('amidi -l').split('\n') if dev_name in line]
    if amidi_list:
      if len(amidi_list) == 1:
        dev_port = amidi_list[0].split()[1]
        dev = amidi_list[0].split(dev_port)[1].strip()
        print('Found device ' + dev + ' on port ' + dev_port)
      elif len(amidi_list) > 1:
        sys.exit("Connect only one {} device at a time!".format(dev_name))
    else:
      print("{} device not found. Wait some seconds before retrying".format(dev_name), end='')
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

def set_patch_to_state(s, p):
  global state_to_patch
  if s in [11, 12, 13, 21, 22, 23, 31, 32, 33]:
    # TODO also check is p is in boundaries of specific pedalboard
    state_to_patch[s] = p

def get_patch_from_state(s):
  global state_to_patch
  if s in [11, 12, 13, 21, 22, 23, 31, 32, 33]:
    return state_to_patch[s]
  elif s in [10, 20, 30]:
    return state_to_patch[s+1]

def get_midi_cmd_from_state(s):
  global state_to_midi_cmd
  if s in [11, 12, 13, 21, 22, 23, 31, 32, 33]:
    return state_to_midi_cmd[s]
  elif s in [10, 20, 30]:
    return None

def get_current_patch(port):
  global request_current_patch
  o = bash_cmd('amidi -d -t 0.1 -p {} -S {}'.format(port, request_current_patch))
  # print(o)
  o = o.split('\n')
  # print(o)
  o = o[len(o)-1].replace('C0 ', '')
  # print(o)
  o = int(o, 16)
  # print(o)
  p = chr(ord('a') + divmod(o, 10)[0]).upper() + str(divmod(o, 10)[1])
  print('Current patch is {}'.format(p))
  return o, p

def set_patch_mode(s):
  l, f = divmod(s, 10)  
  fsw = 1 if gin(fsw1) == in_True else 2 if gin(fsw2) == in_True else 3 if gin(fsw3) == in_True else 0
  # wait until no footswitch is pressed
  while fsw:
    sleep(0.1)
    fsw = 1 if gin(fsw1) == in_True else 2 if gin(fsw2) == in_True else 3 if gin(fsw3) == in_True else 0
  print('Select new patch on pedalboard and press FSW{} again to confirm'.format(f))
  while fsw != f:
    blink(fsw_to_led[f], inverted=True)
    fsw = 1 if gin(fsw1) == in_True else 2 if gin(fsw2) == in_True else 3 if gin(fsw3) == in_True else 0
  new_patch_number, new_patch_name = get_current_patch(dev_port)
  set_patch_to_state(s, new_patch_number)
  print('Associated state {} to patch {}, leaving set_patch_mode'.format(s, new_patch_name))

def transition(s):
  '''
  There are 9 possible states: [11,12,13,21,22,23,31,32,33]
  The first digit represents LSW position, the second digit represents last FSW pressed
  '''
  global dev_port
  global demo
  # store in l the LSW position and in f the last FSW pressed
  new_l, new_f = divmod(s, 10)
  old_l, old_f = divmod(get_state(-1), 10)
  older_l, older_f = divmod(get_state(-2), 10)
  if new_l == old_l and new_f == 0:
    # we reach here if the footswitch has been released after being pressed
    print("FSW{} released".format(str(old_f)))
    return
  #if new_l == older_l and new_f == older_f and new_f+old_f+older_f != 0:
  #  # we reach here if the same footswitch has been pressed again
  #  print("FSW{} pressed again, entering set_patch_mode".format(str(new_f)))
  #  set_patch_mode(s)
  #  return
  # we reach here if either the lever has been moved or a different footswitch has been pressed
  print("Transition to state {} [ LSW{}+FSW{} ]".format(str(s), str(new_l), str(new_f)))
  all_leds_off()
  # set led of first row based on lever position
  if new_l == 1:
    gout(led1, out_True)
  elif new_l == 2:
    gout(led2, out_True)
  elif new_l == 3:
    gout(led3, out_True)
  # set led of second row based on footswitch pressed
  if new_f == 1:
    gout(led4, out_True)
  elif new_f == 2:
    gout(led5, out_True)
  elif new_f == 3: 
    gout(led6, out_True)
  else:  # default preset for this bank
    gout(led4, out_True)
  # send out MIDI command 
  new_state_cmd = get_midi_cmd_from_state(s)
  if new_state_cmd is not None:
    if type(new_state_cmd) == str:
      mout(dev_port, new_state_cmd, demo)
    elif type(new_state_cmd) == list:
      for cmd in new_state_cmd:
        mout(dev_port, cmd, demo)

# MAIN      

try:
  # print information on state of inputs
  debug_print_inputs()
  # do device discovery
  discover()
  # enter infinite loop
  while True:
    # chech lever switch position
    lsw = lsw_pos()
    # check if any footswitch is pressed
    fsw = 1 if gin(fsw1) == in_True else 2 if gin(fsw2) == in_True else 3 if gin(fsw3) == in_True else 0
    # set current_state as explained in transition function
    current_state = 10*lsw + fsw
    # check if state has changed
    if current_state != get_state(0):
      # update states dict
      set_state(current_state)
      # print(states)
      # apply the effects of the transition
      transition(current_state)
      # block until footswitch is not released
      while fsw:
        fsw = 1 if gin(fsw1) == in_True else 2 if gin(fsw2) == in_True else 3 if gin(fsw3) == in_True else 0
        sleep(0.03)
    # sleep some time before checking input again
    sleep(0.03)
except KeyboardInterrupt:
  print('\n\nClean up and exit.\n')
  #mout(dev_port, disable_edit_mode)
  GPIO.cleanup()

