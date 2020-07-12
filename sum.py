from psutil import net_io_counters as io
from subprocess import call
import json
import os
import glob
import signal
import time

def load_config():
  with open('./config.json', 'r') as file:
    contents = file.read()
    file.close()
    config = json.loads(contents)
    return config

# Load configuration. This must be done before functions that use
# variables in the json config file.
config = load_config()
check_interval_seconds = config['global']['check_interval_seconds']
measurement_unit = config['global']['measurement_unit']
event_total_value = config['events']['total']['value']
event_total_type = config['events']['total']['type']
event_total_execute = config['events']['total']['execute']

def convert_value(value):
  return value/1024./1024.*8/measurement_unit

def execute_bash_script(script_location):
  shell_script = call("./test.sh", shell=True)
  return shell_script

def handler(signum, frame):
  print('\n')
  exit (0)

#
# Start
#

# Initalise timer, set graceful sigkill, and set io offsets.
timer_start = time.time()
signal.signal(signal.SIGINT, handler)
recv_initial_value = io().bytes_recv
sent_initial_value = io().bytes_sent

while True:
  recv_value = convert_value(io().bytes_recv - recv_initial_value)
  sent_value = convert_value(io().bytes_sent - sent_initial_value)
  total_value = recv_value + sent_value

  timer_elapsed_seconds = int(time.time() - timer_start)

  # Event on total data transfer
  if total_value >= event_total_value and 'event_total_value_triggered' not in locals():
    event_total_value_triggered = True
    bash_exit_code = execute_bash_script(event_total_execute)


  print("Recv: %.2fM | " % recv_value + \
        "Sent: %.2fM | " % sent_value + \
        "Total: %.2fM | " % total_value + \
        "Elapssed: {} seconds".format(timer_elapsed_seconds), end='\r')

  time.sleep(check_interval_seconds)
