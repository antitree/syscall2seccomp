#!/usr/local/python
# Script to convert strace output to
# a docker seccomp JSON file format

import fileinput
import json
import argparse

SECCOMP_PROFILE_TEMPLATE_PATH = "seccomp.json"

def main(): 
    parser = argparse.ArgumentParser(
        description="Search for syscalls stored inside of an strace log and convert it to a Docker seccomp JSON profile" )
    parser.add_argument("strace", 
            help="Path to file containing the output from running strace on an application")
    #parser.add_argument("-o", help="Optional output path")
    args = parser.parse_args()
    syscalls = set()

    with fileinput.input(files=(args.strace)) as f:
        syscalls.update((x.split('(', 1)[0] for x in f if x[0].isalpha()))
    
    to_profile(syscalls)


def _load_template():
    try:
        with open(SECCOMP_PROFILE_TEMPLATE_PATH, 'r') as template:
            template = json.loads(template.read())
        return template
    except:
        print("Error importing template profile at: {}".format(SECCOMP_PROFILE_TEMPLATE_PATH))
        return False


def _syscall_template():
    return json.loads('{"name": "","action": "SCMP_ACT_ALLOW","args": []}')


def to_profile(syscalls):
    template = _load_template()  # load json as dict
    for call in syscalls:
        newsyscall = _syscall_template()
        newsyscall["name"] = call
        template["syscalls"].append(newsyscall)
    print(json.dumps(template, indent=4))
        
    
if __name__ == "__main__":
    main()
