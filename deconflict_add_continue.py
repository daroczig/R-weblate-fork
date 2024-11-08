#!/usr/local/bin/python

import re
import subprocess
import sys


def get_git_status_output():
    result = subprocess.run(["git", "status"], capture_output=True, check=True)
    return result.stdout.decode("utf-8").split("\n")


def find_both_added_file(status_lines):
    ii = 0

    while not status_lines[ii].startswith("Unmerged paths:"):
        ii += 1
        if ii == len(status_lines):
            return None

    while True:
        match = re.search("both (?:added|modified): *([^ ]+)$", status_lines[ii])
        if match is None:
            ii += 1
        else:
            break

    return match.group(1)


def deconflict(file, which):
    # search for conflict markers without reading it directly (might fail with character encoding issues)
    grep_result = subprocess.run(
        ["grep", "-E", "(<<<<|====|>>>>)", file], capture_output=True
    )
    if grep_result.returncode == 1:
        print(f"No conflict markers found in {file}")
        return

    with open(file) as f:
        contents = f.read()

    lines = contents.split("\n")

    n_conflicts = sum([l.startswith("<<<<") for l in lines])

    keep = True
    outfile = []

    if which == "left" or which == "svn":
        start_drop = "===="
        start_keep = ">>>>"
        keep_skip = "<<<<"
    elif which == "right" or which == "weblate":
        start_drop = "<<<<"
        start_keep = "===="
        keep_skip = ">>>>"
    else:
        raise ValueError('Unrecognized value of which "{}"'.format(which))

    for line in lines:
        if line.startswith(start_drop):
            keep = False
        elif line.startswith(start_keep):
            keep = True
        elif keep and not line.startswith(keep_skip):
            outfile.append(line)

    conflicts_markers_remaining = sum(
        [
            l.startswith("<<<<") or l.startswith("====") or l.startswith(">>>>")
            for l in outfile
        ]
    )
    if conflicts_markers_remaining:
        raise ValueError(
            "Still {} conflict markers remaining!".format(conflict_markers_remaining)
        )

    print(
        "Removed {} lines and {} conflicts".format(
            (len(lines) - len(outfile)), n_conflicts
        )
    )

    with open(file, "w") as f:
        for line in outfile:
            _ = f.write(line + "\n")


which = sys.argv[1]

while (file := find_both_added_file(get_git_status_output())) is not None:
    print(f"De-conflicting {file} by using the edits from {which}")
    deconflict(file, which)
    subprocess.call(["git", "add", file])

subprocess.call(["git", "rebase", "--continue"])
print("Step complete!\n\nNew status:")
subprocess.call(["git", "status"])
