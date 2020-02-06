# syscall2seccomp

A tool to help build custom Docker seccomp profile by extracting
syscalls from various tools and outputting them to the [Docker custom seccomp profiles](https://docs.docker.com/engine/security/seccomp/) JSON format. 
In theory, this would  let you come up with a customized whitelist of only the required syscalls and
block/error/crash\* all other syscall attempts. 

Usage:

With [`sysdig`](https://www.sysdig.com/)

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

Seccomp BPF is a powerful tool to prevent potentially malicious system calls
from being sent insides your container. Minimizing the syscalls that should be
allowed minimizes the attack surface and could prevent a container breakout. 

That's the idea. 

Should you use custom seccomp profiles for each of your containers? Probably 
not. Managing so many custom profiles, deploying them consistently, and 
integrating it into unit testing is most likely more effort (and risk) than
it's worth. 

**So you don't recommend custom seccomp profiles, why make this tool?**

The use case is individuals that want to play with custom seccomp profiles
and apply it to a few of the Docker containers they run. In that scenario,
where they spend the time customizing the profile to be _more_ secure than
the default one, it adds some value. 

For enterprises with major deployments
and orchestration involved, I just wanted to make it as easy as possible to see how annoying it was 
to manage custom seccomp profiles. 

Maybe Docker will address this by letting you apply multiple seccomp profiles
(right now, the last profile to be applied, wins) or  aid in managing profiles
in Swarm but at this point, there's more
value in working to build custom AppArmor profiles. 

**Why do you add a bunch of syscals automatically?**

[Syscalls.py](https://github.com/antitree/syscall2seccomp/blob/master/syscalls.py#L321-L337) contains
a list of requisit syscalls by any container because reasons. See: https://github.com/moby/moby/issues/22252

**What about seccomp BPF arguments? Isn't that the point of BPF?**

Good luck with that. That would require real reviewing of strace output 
but this is at least a simple starting point. 

