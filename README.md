# strace2seccomp

This tool tries to help build custom Docker seccomp profile by collecting
syscalls from various tools and outputting them to the [Docker custom seccomp profiles](https://docs.docker.com/engine/security/seccomp/) JSON format. 
In theory, this would  let you come up with a customized whitelist of only the required syscalls and
block/error/crash\* all other syscall attempts. 

Usage:

With [`sysdig`](https://www.sysdig.org/)

```
python3 ./syscall2seccomp.py -s path-to-sysdig-output
```

With `strace`

```
python3 ./strace2seccomp.py path-to-strace-output
```


## Example with Sysdig

Start `sysdig`

```
sudo sysdig container.name=myawesomecontainer > myawesomecontainer.sysdig
```

Start your container

```
docker run --name myawesomecontainer nginx
```

Perform all the normal activities of the container and then shut it down. 

Convert the output to a seccomp profile

```
python3 syscall2seccomp.py -s myawesomecontainer.sysdig > myawesomecontainer.json
```
Start your container with the seccomp filtering enabled

```
docker run \
       --security-opt seccomp=$PWD/myawesomecontainer.json \
       nginx
```


## Example with Strace
Run strace on an application and save the output: 

```
strace -o wget.strace wget https://www.antitree.com 
```

Convert output to a Docker profile:

```
python3 ./syscall2seccomp.py wget.strace > wget.seccomp
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
**Sysdig or Strace?**
Sysdig is rad for containers. [Go check it out](https://www.sysdig.org/). 

**I ran through the example and it says "operation not permitted"**

Right. By using a custom seccomp profile, you're also removing the default
seccomp profile and there's no guarantee that you've got every single
syscall that the application made. That's the nature of the beast. In 
practice I've found that `sysdig` is better at catching container-level
syscalls besides the syscalls that your application needs after starting.

**Why use a custom seccomp profile?**

Great question. You'll need to look at your environment and see if overriding
the Docker default profile is worth it to you. In most cases, this adds a
major amount of overhead and testing with minimal results in terms 
limiting the attack surface. 

**Why do you add a bunch of syscals automatically?**

[Syscalls.py](https://github.com/antitree/syscall2seccomp/blob/master/syscalls.py#L321-L337) contains
a list of requisit syscalls by any container. See: https://github.com/moby/moby/issues/22252

**What about seccomp BPF arguments? Isn't that the point of BPF?**

Good luck with that. That would require real reviewing of strace output 
but this is at least a simple starting point. 

