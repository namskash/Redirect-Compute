# FAQ

## What is ICMP?

ICMP is the network protocol used by tools like `ping`.

A failed ping does not always mean the machine is unreachable. Some networks block ICMP while still allowing other traffic like SSH.

## How can SSH work if ping fails?

SSH uses TCP, usually on port `22`, while ping uses ICMP.

So a network can block ping/ICMP but still allow SSH/TCP.

## Is this like SSH'ing into any remote computer?

Yes. It is standard SSH access to another computer.

In this case, the Mac is reachable over the local WiFi network instead of over the internet.

## Will SSH work if the Mac is asleep?

Usually no.

If the Mac is asleep, SSH connections generally will not work. For long jobs, use macOS power settings or run jobs with `caffeinate` so the Mac stays awake while computing.

## What does a `192.168.x.x` IP address mean?

A `192.168.x.x` address is a private LAN address assigned by the WiFi router.

It is only reachable inside the local network, not directly from the public internet.

## What if the Mac's IP address changes later?

SSH by IP may stop working or may show a host key warning.

Better options:

- Use the Mac hostname if `.local` discovery works.
- Create a DHCP reservation on the router.
- Set a static IP for the Mac.
- Reconnect using the new IP and update `~/.ssh/known_hosts` if needed.

## Why did SSH add entries to `known_hosts`?

SSH saves the Mac's host keys in `~/.ssh/known_hosts` so it can verify the Mac's identity next time.

If the key changes unexpectedly, SSH warns you because it might indicate that you are connecting to a different machine.

## What are `ssh-ed25519`, `ssh-rsa`, and `ecdsa-sha2-nistp256`?

They are different SSH host key algorithms used by the Mac to prove its identity.

- `ssh-ed25519`: modern preferred host key type.
- `ecdsa-sha2-nistp256`: elliptic-curve host key type, older but valid.
- `ssh-rsa`: legacy RSA host key type, generally less preferred today.

These are server identity keys, not your login keys.
