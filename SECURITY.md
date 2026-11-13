# Security

## Reporting a problem

Please report security problems **privately**, through **Report a vulnerability** in this repository's **Security** tab
(GitHub private vulnerability reporting). Do not open a public issue. Remove your own addresses, host names and any
private data from logs before you send them.

## What this repository is

Text, example configuration files and three small scripts. Nothing here runs as a service and nothing phones home. Read
every file before you use it; the examples are meant to be edited, not applied as they are.

## What the setup it describes is built for

A NAS on **one private LAN**, administered over SSH, serving files to a few known machines. Keep these boundaries:

- **NFS has no login.** The export is read-only and limited to the client addresses you list; anyone who can spoof one of
  those addresses on your LAN can read the share. Do not export to a range you do not control, and never to the internet.
- **SSH is the door.** Keys only; disable password logins once your key works. The NAS is not reachable from outside your
  LAN unless you make it so.
- **The power-off rule in `sudoers` grants exactly one command** (`/usr/bin/systemctl poweroff`) without a password, so a
  machine on the LAN can switch the NAS off after an idle check. Keep it to that one command.
- **Wake-on-LAN packets carry no authentication.** Anyone on the LAN can wake the NAS. That is harmless for a file server
  that boots to a login prompt.
- **Docker** (on ours since 2026-11-12) adds the Docker socket, which is root on the machine. Members of the `docker` group
  reach it without a password. We put our user in it: the account already held `sudo` with its password, and the group
  removes the password from that step. Be deliberate about who is in that group, or use `sudo docker`. Bind container ports to `127.0.0.1` or to the LAN address only.
- **No secrets in this repository.** Tokens, passwords and key files never belong in these files or in your fork of them.
