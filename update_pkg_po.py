#!/usr/local/bin/python

import os
import subprocess

def find_pot_file(po_file):
  """
  Finds the associated .pot file for a given .po file based on the naming convention.

  Args:
      po_file: Path to the .po file.

  Returns:
      Path to the associated .pot file.
  """
  po_dir, po_file = os.path.split(po_file)
  pkg_dir, _ = os.path.split(po_dir)
  pkg = os.path.basename(pkg_dir)
  if po_file.startswith("R-"):
    pot_filename = f"R-{pkg}.pot"
  elif po_file.startswith("RGui-"):
    pot_filename = "RGui.pot"
  elif pkg == 'base':
    pot_filename = "R.pot"
  else:
    pot_filename = f"{pkg}.pot"
  pot_path = os.path.join(po_dir, pot_filename)
  if not os.path.exists(pot_path):
    raise ValueError(f".pot path {pot_path} associated with .po file {po_file} does not exist")
  return pot_path

def update_po_files(base_dir):
  """
  Iterates over all .po files in the base directory and its subdirectories,
  finds the associated .pot file, and runs msgmerge with the appropriate options.

  Args:
      base_dir: Path to the base directory containing subdirectories.
  """
  for root, _, files in os.walk(base_dir):
    for file in files:
      if not file.endswith(".po"):
        continue
      po_file = os.path.join(root, file)
      pot_file = find_pot_file(po_file)
      print(f"Updating {file} from {os.path.basename(pot_file)}")
      subprocess.call(["msgmerge", "--update", "--no-wrap", po_file, pot_file])

update_po_files("src/library")
