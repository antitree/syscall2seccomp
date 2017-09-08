# strace2seccomp

The goal of this script is to help take the output from `strace` and 
convert it to the new(ish) 
[Docker custom seccomp profiles](https://docs.docker.com/engine/security/seccomp/) JSON format 
to be used with your container configuration. In theory, this would 
let you come up with a whitelist of only the required syscalls and
block/error/crash\* all other syscall attempts.  

Usage:

```
python3 ./strace2seccomp.py path-to-strace-output
```

## Example
Run strace on an application and save the output: 

```
strace -o wget.strace wget https://www.antitree.com 
```

Convert output to a Docker profile:

```
python3 ./strace2seccomp.py wget.strace > wget.seccomp
```

*NOTE: I've omitted the step of spending 2-300 hours of debugging why strace didn't
include one of the syscalls you needed.*

Start a docker container with the custom profile applied:

```
docker run -it \
       --security-opt seccomp=$PWD/wget.seccomp \
       busybox wget https://www.antitree.com
```

## FAQ
**I ran through the example and it says "operation not permitted"**

Right. By using a custom seccomp profile, you're also removing the default
seccomp profile and there's no guarantee that you've got every single
syscall that the application made. That's the nature of the beast. Or 
there's just a problem with this script. 

**Why use a custom seccomp profile?**

Great question. You'll need to look at your environment and see if overriding
the Docker default profile is worth it to you. In most cases, this adds a
major amount of overhead and testing with minimal results in terms 
limiting the attack surface. 

**What about the arguments?**

Good luck with that. That would require real reviewing of strace output 
but this is at least a simple starting point. 
