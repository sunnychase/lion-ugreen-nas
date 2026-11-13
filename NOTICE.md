# Notices

**Lion UGREEN NAS.** Created by [Sunny Chase](https://github.com/sunnychase) in collaboration with Claude (Anthropic).
Copyright (c) 2026 Sunny Chase (https://github.com/sunnychase) · Lion UGREEN NAS.

All text, example configuration files and scripts in this repository were written for it and are under the MIT licence
([LICENSE](LICENSE)).

## Not affiliated with UGREEN

This is an unofficial, independent write-up of what one owner did with one UGREEN NASync DXP4800 Pro. It is not made,
endorsed, reviewed or supported by UGREEN. "UGREEN" and "NASync" are UGREEN's names, used here only to say which machine
this is about; no UGREEN logo, artwork, firmware, software or documentation is included. UGOS Pro, the system the NAS
ships with, is UGREEN's product and is not included or redistributed here.

Replacing the vendor's operating system is done at your own risk. Read [Before you start](README.md#before-you-start) and
check UGREEN's current policy on third-party operating systems and on your warranty before you do anything.

## What it uses (not included in this repository)

| Software | Licence | Used for |
|---|---|---|
| [Ubuntu Server 24.04 LTS](https://ubuntu.com/server) | various (Ubuntu's own terms) | the operating system installed on the NAS |
| XFS, NFS (`nfs-kernel-server`), netplan, systemd, ethtool, smartmontools | GPL and others, as packaged by Ubuntu | storage, file sharing, network, power, disk health |
| nginx, [File Browser](https://filebrowser.org/), Cockpit, avahi | BSD-2, Apache-2.0, LGPL-2.1, LGPL-2.1 | the small native services beside the file server |
| [Docker Engine](https://docs.docker.com/engine/) with containerd, Buildx and Compose | Apache-2.0 | installed 2026-11-12 from Docker's own repository; data root on the data volume (Step 10) |
| [ugreen_leds_controller](https://github.com/miskcoo/ugreen_leds_controller) (`led_ugreen` module) | GPL-2.0 | the front LEDs under Ubuntu |
| Python 3 (standard library only) | PSF | the Wake-on-LAN script and the reel generator |
| Pillow and ffmpeg (only `scripts/make_reel.py`) | MIT-CMU, LGPL/GPL | drawing and encoding the reel in `docs/media` |

## The reel and the examples

Every frame in `docs/media` is drawn from text by `scripts/make_reel.py`; there are no screen captures and no photographs.
Every address in this repository is from the ranges reserved for documentation (RFC 5737: 192.0.2.0/24, 198.51.100.0/24,
203.0.113.0/24), every MAC address is a locally administered placeholder, and every host name, user name, label and UUID is a made-up
example value to replace with your own. The paths `/srv/data` and `/srv/data/Drive2` and the interface names `enp3s0` /
`enp6s0` are the ones on our NAS.

## Disclaimer

The software and text are provided "as is", without warranty of any kind (see the licence). Nothing here is advice from
UGREEN, Canonical, Docker or anyone else.
