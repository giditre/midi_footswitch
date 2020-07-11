import subprocess
from time import sleep

def bash_cmd(cmd):
  proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
  out, err = proc.communicate()
  return out.decode('utf-8')

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

enable_edit_mode = 'F052005A50F7'
disable_edit_mode = 'F052005A51F7'
request_current_patch = 'F052005A33F7'
request_info_current_patch = 'F052005A29F7'

bash_cmd('amidi -p hw:1,0,0 -S {}'.format(enable_edit_mode))

try:
  while True:
    input('Press Enter to get patch...')
    o = bash_cmd('amidi -d -t 0.1 -p hw:1,0,0 -S {}'.format(request_current_patch))
    # print(o)
    o = o.split('\n')
    # print(o)
    o = o[len(o)-1].replace('C0 ', '')
    # print(o)
    o = int(o, 16)
    # print(o)
    o = chr(ord('a') + divmod(o, 10)[0]).upper() + str(divmod(o, 10)[1])
    print('Current patch is {}'.format(o))
except KeyboardInterrupt:
  print('\nDisable edit mode and exit\n\n')
  bash_cmd('amidi -p hw:1,0,0 -S {}'.format(disable_edit_mode))

