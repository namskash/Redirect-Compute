# Working Doc

## SSH alias setup

Added/updated local SSH config on the Linux orchestrator:

```text
~/.ssh/config
```

Purpose:

- Store the Mac as a named SSH host.
- Avoid typing `user@192.168.x.x` every time.
- Allow connecting with a short alias like:

```bash
ssh mac
```

Example entry:

```sshconfig
Host mac
  HostName 192.168.x.x
  User <mac-username>
```
