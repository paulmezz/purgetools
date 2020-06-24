#!/usr/bin/python3 -u

## -u is needed to avoid buffering stdout 

import argparse, pathlib, subprocess, configparser
import pprint, time
from collections import OrderedDict
import sys

# load config file settings
config = configparser.ConfigParser()
config.read(pathlib.Path(__file__).resolve().parent.joinpath('etc/buildlist.ini'))

def parse_args(args):
    #grab cli options
    parser = argparse.ArgumentParser(description='Collect each user purge candidates into a single list')
    parser.add_argument('--dryrun', help='Print list to scan and quit', action="store_true")
    parser.add_argument('--scanident', help='Unique identifier for scan from buildlist.py ', type=str, required=True)
    parser.add_argument('--cachelimit', help='Number of file hanels to hold open', type=int, default=100)
    args = parser.parse_args(args)
    return args


# get list of all files matching 'scanident'
def get_dir_paths(path=pathlib.Path.cwd(),
                 scanident=None):
     

     return list(path.glob(f'{scanident}*.txt'))

# format of files being parsed
# -rw-rw---- bvansade glotzer 232.791 KB Nov 21 2019 15:48 /scratch/sglotzer_root/sglotzer/bvansade/peng-kai/cycles_poly/.ipynb_checkpoints/integrator_energy_replicates-checkpoint.ipynb

# get the user from the format
def get_user(line):
    if line is None:
      raise TypeError

    line = line.split()
    return line[1]

#


# class that actually takes the strings and writes them to files
class UserSort:
   # cachelimit is number of open files to hold open
   # if you get to many open files lower this value default=100
   def __init__(self, cachelimit=100):
      self._handles = OrderedDict()
      self._cachelimit = cachelimit

   # returns handle if exists in _handles or creates a new one push end of list
   # if _handles.count() = cachelimit  pop front of list
   def _gethandle(self, lineuser):
       if lineuser in self._handles:
          return self._handles[lineuser]

       else:
           # check if we are at cached limit
           if len(self._handles) >= self._cachelimit:
              # already have maxed cached handles remove the first one created
              # this is overly simple and does not actaully do remove last recently accessed
              self._handles.popitem(last=False)

           # go ahead and create handle
           user_log = pathlib.Path.cwd() / f"{args.scanident}-{lineuser}.purge.txt"
           g = user_log.open("a")
           self._handles[lineuser] = g
           return self._handles[lineuser]
         
           

   # take user and line check if already have cache in 
   # _handles if so write otherwise create a new one
   def writeline(self, lineuser, line):
          handle = self._gethandle(lineuser)
          handle.write(line)


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    args = parse_args(sys.argv[1:])
          
    
    paths = get_dir_paths(scanident=args.scanident)
    
    pp.pprint(paths)
    
    if args.dryrun:
       print("--dryrun given exiting")
       exit(0)
    
    currentuser = ''
    
    sorter = UserSort(cachelimit=args.cachelimit)
    for path in paths:
       with path.open() as f:
          lines = f.readlines()
          for line in lines:
              lineuser = get_user(line)
              sorter.writeline(lineuser, line)
    
