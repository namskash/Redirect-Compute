# Cleanup IP From SSH Plan

## Goal

Remove the Mac's LAN IP from local SSH records if needed.

## Files to check

```text
~/.ssh/known_hosts
~/.ssh/known_hosts.old
~/.ssh/config
```

## Recommended removal

Use SSH's built-in cleanup command:

```bash
ssh-keygen -R <mac-ip>
```

Example:

```bash
ssh-keygen -R 192.168.1.42
```

## Verify

Search for remaining references:

```bash
grep '<mac-ip>' ~/.ssh/known_hosts ~/.ssh/known_hosts.old ~/.ssh/config
```

## Notes

- `known_hosts` stores saved host keys.
- `known_hosts.old` may contain backups/previous entries.
- `~/.ssh/config` may contain an alias using the IP as `HostName`.
