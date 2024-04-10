#!/usr/local/bin/python

import sys

def show_conflicts(file):
  with open(file) as f:
    contents=f.read()

  lines = contents.split('\n')

  n_conflicts = sum([l.startswith('<<<<') for l in lines])
  print('Showing {} conflicts'.format(n_conflicts))

  show=False
  counter=0

  for line in lines:
    if line.startswith('<<<<'):
      show=True
      counter+=1
      print('%%% \033[33mConflict #{}\033[0m'.format(counter))
      line=line[:8] + '[\033[31mSVN\033[0m]'
    elif line.startswith('>>>>'):
      show=False
      print(line[:8] + '[\033[32mWEBLATE\033[0m]')

    if show:
      print(line)

if len(sys.argv) == 2:
  file = sys.argv[1]
else:
  pkg = sys.argv[1]
  lang = sys.argv[2]
  file = f'{pkg}/po/{lang}.po'
show_conflicts(file)
