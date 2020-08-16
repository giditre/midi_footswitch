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

def gpio_setup(input_pin_list, output_pin_list, out_False):
  # set pin numbering to BOARD mode
  GPIO.setmode(GPIO.BOARD)
  # inputs
  GPIO.setup(input_pin_list, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  # outputs
  GPIO.setup(output_pin_list, GPIO.OUT, initial=out_False)

class MIDIController():

  def __init__(self):


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
    # create variables for input and output pins (in GPIO.BOARD mode)
    # footswitches
    self.fsw1 = 12
    self.fsw2 = 18
    self.fsw3 = 32
    # lever switch
    self.lsw1 = 13
    self.lsw2 = 11
    # LED in the top row
    self.led1 = 15
    self.led2 = 29
    self.led3 = 31
    # LED in the bottom row
    self.led4 = 7
    self.led5 = 16
    self.led6 = 22

    self.input_pin = {
      'FSW1': self.fsw1,
      'FSW2': self.fsw2,
      'FSW3': self.fsw3,
      'LSW1': self.lsw1,
      'LSW2': self.lsw2
    }
    self.output_pin = {
      'LED1': self.led1,
      'LED2': self.led2,
      'LED3': self.led3,
      'LED4': self.led4,
      'LED5': self.led5,
      'LED6': self.led6 
    }

    self.fsw_to_led = {
      1: self.led4,
      2: self.led5,
      3: self.led6
    }

    # map LOGICAL TRUE VALUE for INPUT to GPIO voltage level
    self.in_True = GPIO.LOW
    # the LOGICAL FALSE VALUE for INPUT is a consequence of the other logical value
    self.in_False = GPIO.LOW if self.in_True == GPIO.HIGH else GPIO.HIGH

    # map LOGICAL TRUE VALUE for OUTPUT to GPIO voltage level
    self.out_True = GPIO.HIGH
    # the LOGICAL FALSE VALUE for OUTPUT is a consequence of the other logical value
    self.out_False = GPIO.LOW if self.out_True == GPIO.HIGH else GPIO.HIGH

    ## configure pins
    #GPIO.setmode(GPIO.BOARD)
    ## inputs
    #GPIO.setup(list(self.input_pin.values()), GPIO.IN, pull_up_down=GPIO.PUD_UP)
    ## outputs
    #GPIO.setup(list(self.output_pin.values()), GPIO.OUT, initial=self.out_False)

    gpio_setup(list(self.input_pin.values()), list(self.output_pin.values()), self.out_False) 

    for g in list(self.output_pin.values()):
      GPIO.output(g, self.out_True)
    sleep(1)
    for g in list(self.output_pin.values()):
      GPIO.output(g, self.out_False)

    self.current_state = None
    self.demo_mode = False
    self.dev_port = None

  # read GPIO g
  def gin(self, g):
    return GPIO.input(g) == self.in_True
  
  # write value v on GPIO g
  def gout(self, g, v):
    if self.gin(g) != v:
      GPIO.output(g, v == self.out_True)
  
  # toggle output value of
  def gtog(self, g):
    self.gout(g, not self.gin(g))

  def read_inputs(self):
    return { name: self.gin(self.input_pin[name]) for name in self.input_pin }

  def wait_fsw_released(self, fsw_list=["FSW1", "FSW2", "FSW3"]):
    while any([self.gin(self.input_pin[fsw]) == self.in_True for fsw in fsw_list]):
      sleep(0.1)

  def blink(self, g, t=0.1, cycles=1, inverted=False):
    while cycles:
      self.gout(g, self.out_True if not inverted else self.out_False)
      sleep(t/2)
      self.gout(g, self.out_False if not inverted else self.out_True)
      sleep(t/2)
      cycles = cycles-1

  def all_leds_off(self):
    for g in self.output_pin.values():
      self.gout(g, self.out_False)

  def supercar(self, t):
    print("supercar")
    self.all_leds_off()
    for g in [self.led1, self.led2, self.led3, self.led4, self.led5, self.led6]:
      print(g)
      self.gout(g, True)
      sleep(t/6)
      self.gout(g, False)

  def circle(self, t):
    self.all_leds_off()
    for g in [self.led1, self.led2, self.led3, self.led6, self.led5, self.led4]:
      self.gout(g, self.out_True)
      sleep(t/6)
      self.gout(g, self.out_False)

  def zigzag(self, t):
    self.all_leds_off()
    for g in [self.led1, self.led4, self.led2, self.led5, self.led3, self.led6]:
      self.gout(g, self.out_True)
      sleep(t/6)
      self.gout(g, self.out_False)

  def lsw_pos(self):
    if self.gin(self.lsw1) == True and self.gin(self.lsw2) == False:
      return 1
    elif self.gin(self.lsw1) == False and self.gin(self.lsw2) == False:
      return 2
    elif self.gin(self.lsw1) == False and self.gin(self.lsw2) == True:
      return 3

  def mout(self, port, code):
    if not self.demo_mode:
      cmd = 'amidi -p ' + port + ' -S ' + code
      print(cmd)
      bash_cmd(cmd)

  def discover_device(self):
    dev_name = "HX Stomp"
    # do the following check periodically, until a device is found
    # check that the device is connected and on which port
    print('Start device discovery')
    while self.dev_port is None:
      # look for connected devices
      amidi_list = [line for line in bash_cmd('amidi -l').split('\n') if dev_name in line]
      if amidi_list:
        if len(amidi_list) == 1:
          self.dev_port = amidi_list[0].split()[1]
          dev = amidi_list[0].split(self.dev_port)[1].strip()
          print('Found device ' + dev + ' on port ' + self.dev_port)
        elif len(amidi_list) > 1:
          sys.exit("Connect only one {} device at a time!".format(dev_name))
      else:
        print("{} device not found. Wait some seconds before retrying".format(dev_name), end='')
        for i in range(3):
          print('.', end='')
          self.circle(1)
        print('')

# MAIN      

if __name__ == "__main__":

   
  # instantiate midi controller object
  mc = MIDIController()

  # print information on state of inputs
  print(mc.read_inputs())
 
  try:

    # check lever switch position
    lsw = mc.lsw_pos()

    print(lsw)

    if lsw == 1:
      mc.demo_mode = True

    elif lsw == 2:
      # do device discovery
      mc.discover_device()
      #print(mc.dev_port)

    elif lsw == 3:
      while True:
        mc.supercar(1)  

    ## check if any footswitch is pressed
    #fsw = 1 if gin(fsw1) == in_True else 2 if gin(fsw2) == in_True else 3 if gin(fsw3) == in_True else 0
    ## set current_state as explained in transition function
    #current_state = 10*lsw + fsw
    ## check if state has changed
    #if current_state != get_state(0):
    #  # update states dict
    #  set_state(current_state)
    #  # print(states)
    #  # apply the effects of the transition
    #  transition(current_state)
    #  # block until footswitch is not released
    #  mc.wait_fsw_released()

    # sleep some time before checking input again
    sleep(0.03)
  except KeyboardInterrupt:
    pass
  finally:
    print('\n\nClean up and exit.\n')
    #mout(dev_port, disable_edit_mode)
    GPIO.cleanup()

