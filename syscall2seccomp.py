#!/usr/local/python
# Script to convert strace output to
# a docker seccomp JSON file format

import fileinput
import json
import argparse

import syscalls

# These syscalls are _required_ to start a container
# see https://github.com/moby/moby/issues/22252
BASE_SYSCALLS = syscalls.DOCKER

SECCOMP_PROFILE = ('{"defaultAction": "SCMP_ACT_ERRNO",'
    '"architectures": ['
    '"SCMP_ARCH_X86_64",'
    '"SCMP_ARCH_X86",'
    '"SCMP_ARCH_X32"],'
    '"syscalls": []}'
    )



def main(): 
    parser = argparse.ArgumentParser(
        description="Search for syscalls stored inside of an strace log and convert it to a Docker seccomp JSON profile" )
    parser.add_argument("strace", 
            help="Path to file containing the output from running strace on an application")
    #parser.add_argument("-o", help="Optional output path")
    parser.add_argument("-s", dest="sysdig", action="store_true", help="For handling sysdig output instead of strace")
    args = parser.parse_args()
    app_syscalls = set()

    with fileinput.input(files=(args.strace)) as f:
        if args.sysdig:
            for x in f:
                x=x.strip()
                if x:
                    app_syscalls.update(x.replace('>','<').split(' < ', 1)[1].split(' ')[0])
        else: 
            app_syscalls.update((x.split('(', 1)[0] for x in f if x[0].isalpha()))
    
    app_syscalls.intersection_update(syscalls.SYSCALLS) # validate syscalls actually exist
    to_profile(app_syscalls)


def _load_template():
    template = json.loads(SECCOMP_PROFILE)
    return template


def _syscall_template():
    return json.loads('{"name": "","action": "SCMP_ACT_ALLOW","args": []}')


def to_profile(syscalls):
    template = _load_template()  # load json as dict
    syscalls.update(BASE_SYSCALLS)  # required syscalls
    
    # calls each have a block
    """
    for call in syscalls:
        newsyscall = _syscall_template()
        newsyscall["names"] = call
        template["syscalls"].append(newsyscall)
    """

    # calls are in one block
    newsyscall = _syscall_template()
    newsyscall["names"] = list(syscalls)
    template["syscalls"].append(newsyscall)

    print(json.dumps(template, indent=4))
        
    
if __name__ == "__main__":
    main()
