import RPi.GPIO as GPIO
import threading
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


# GPIO SETUP
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

input_pin = {
  'FSW1': fsw1,
  'FSW2': fsw2,
  'FSW3': fsw3,
  'LSW1': lsw1,
  'LSW2': lsw2
}
output_pin = {
  'LED1': led1,
  'LED2': led2,
  'LED3': led3,
  'LED4': led4,
  'LED5': led5,
  'LED6': led6 
}

fsw_to_led = {
  1: led4,
  2: led5,
  3: led6
}

# map LOGICAL TRUE VALUE for INPUT to GPIO voltage level
in_True = GPIO.LOW
# the LOGICAL FALSE VALUE for INPUT is a consequence of the other logical value
in_False = GPIO.LOW if in_True == GPIO.HIGH else GPIO.HIGH

# map LOGICAL TRUE VALUE for OUTPUT to GPIO voltage level
out_True = GPIO.HIGH
# the LOGICAL FALSE VALUE for OUTPUT is a consequence of the other logical value
out_False = GPIO.LOW if out_True == GPIO.HIGH else GPIO.HIGH

# configure pins
GPIO.setmode(GPIO.BOARD)
# inputs
GPIO.setup(list(input_pin.values()), GPIO.IN, pull_up_down=GPIO.PUD_UP)
# outputs
GPIO.setup(list(output_pin.values()), GPIO.OUT, initial=out_False)

# read GPIO g
def gin(g):
  #print(g)
  return GPIO.input(g) == in_True

# write value v on GPIO g
def gout(g, v):
  ## check if positive logic...
  #if in_True == out_True:
  #  if gin(g) != v:
  #    GPIO.output(g, out_True if v else out_False)
  ## ...or negative logic
  #else:
  #  if gin(g) == v:
  #    GPIO.output(g, out_True if v else out_False)
  GPIO.output(g, out_True if v else out_False)
 
# lamp test
for g in list(output_pin.values()):
  gout(g, True)
sleep(1)
for g in list(output_pin.values()):
  gout(g, False)

class MIDIController(threading.Thread):

  def __init__(self):

    super().__init__()

    # modes
    # 1: presetdown-tuner-presetup
    # 2: undefined,
    # 3: undefined
    self.mode = -1

    # MIDI commands
    self.mode_to_fsw_midi_cmd = {
      1: {
        1: ["B0 47 01", "B0 31 00", "B0 47 03"],
        2: ["B04400"],
        3: ["B0 47 01", "B0 32 00", "B0 47 03"]
      }
    }

    self.dev_port = None

    self.stop_flag = False

 
  # toggle output value of
  def gtog(self, g):
    gout(g, not gin(g))

  def read_inputs(self):
    return { name: gin(input_pin[name]) for name in input_pin }

  def wait_fsw_released(self, fsw_list=["FSW1", "FSW2", "FSW3"]):
    while any([gin(input_pin[fsw]) == in_True for fsw in fsw_list]):
      sleep(0.1)

  def set_output(self, out_name, v):
    if out_name in output_pin:
      gout(output_pin[out_name], out_True if v else out_False)
    else:
      print("Output {} not defined".format(out_name))

  def blink(self, g, t=0.1, cycles=1, inverted=False):
    while cycles:
      gout(g, out_True if not inverted else out_False)
      sleep(t/2)
      gout(g, out_False if not inverted else out_True)
      sleep(t/2)
      cycles = cycles-1

  def all_leds_off(self):
    for g in output_pin.values():
      gout(g, out_False)

  def supercar(self, t):
    self.all_leds_off()
    for g in [led1, led2, led3, led4, led5, led6]:
      gout(g, True)
      sleep(t/6)
      gout(g, False)

  def circle(self, t):
    self.all_leds_off()
    for g in [led1, led2, led3, led6, led5, led4]:
      gout(g, out_True)
      sleep(t/6)
      gout(g, out_False)

  def zigzag(self, t):
    self.all_leds_off()
    for g in [led1, led4, led2, led5, led3, led6]:
      gout(g, out_True)
      sleep(t/6)
      gout(g, out_False)

  def lsw_pos(self):
    if gin(lsw1) == True and gin(lsw2) == False:
      return 1
    elif gin(lsw1) == False and gin(lsw2) == False:
      return 2
    elif gin(lsw1) == False and gin(lsw2) == True:
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
    #while self.dev_port is None:
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
      self.dev_port = None
      for i in range(3):
        print('.', end='')
        self.circle(1)
      print('')

  def get_dev_port(self):
    return self.dev_port

  def get_mode(self):
    return self.mode

  def set_mode(self, mode_n):
    print("Setting mode {}".format(mode_n))
    self.mode = mode_n

  def set_stop_flag(self):
    self.stop_flag = True

  def run(self):
    while not self.stop_flag:
      # update the mode based on lever switch position
      if self.lsw_pos() != self.get_mode():
        sleep(1)
        if self.lsw_pos() != self.get_mode():
          print("Mode changed from {} to {}".format(self.get_mode(), self.lsw_pos()))
          self.set_mode(self.lsw_pos())
      sleep(0.2)

# MAIN      

if __name__ == "__main__":

   
  # instantiate midi controller object
  mc = MIDIController()

  # print information on state of inputs
  print(mc.read_inputs())
 
  # set mode based on lever switch position
  mc.set_mode(mc.lsw_pos())

  mc.start()

  try:

    while True:
      while mc.get_mode() == 1:
        # do device discovery
        mc.discover_device()
        # if device found
        if mc.get_dev_port():
          mc.set_output("LED1", True)
          # check fsw
          while mc.get_mode() == 1:
            sleep(0.1)

      while mc.get_mode() == 2:
        mc.set_output("LED2", True)
        sleep(1)
        mc.supercar(1)  

      while mc.get_mode() == 3:
        mc.set_output("LED3", True)
        sleep(1)
        mc.supercar(1)  

    # mc.wait_fsw_released()

    # sleep some time before checking input again
    sleep(0.03)
  except KeyboardInterrupt:
    pass
  finally:
    print('\n\nClean up and exit.\n')
    #mout(dev_port, disable_edit_mode)
    mc.set_stop_flag()
    mc.join()
    GPIO.cleanup()

