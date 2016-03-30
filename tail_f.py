#!/usr/bin/python
import os , sys , time
# this function implements the unix/linux command tail -f on a file , so that
# we can monitor the file in python for new lines , such as a log file

def tail_f(file):
  interval = 1.0
  while True:
    where = file.tell()
    line = file.readline()
    if not line:
      time.sleep(interval)
      file.seek(where)
    else:
      yield line

#Which then allows you to write code like:

for line in tail_f(open(sys.argv[1])):
  print line,
