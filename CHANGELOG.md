# Changelog

Dated entries, newest first. There are no version numbers; `main` is the current version.

## 2026-11-12: first draft

- The write-up of one UGREEN NASync DXP4800 Pro taken from UGOS Pro to Ubuntu Server 24.04 LTS between 2026-09-12 and
  2026-10-16: USB installer, BIOS watchdog, installer answers, first boot over SSH, the two-port network layout, the 10 GbE
  receive fix (Aquantia AQC113: LRO and GRO off), the XFS data volume and a second drive mounted inside the export,
  the read-only NFS export, Wake-on-LAN, the gated power-off, Docker Engine, known limits. The configuration re-read from
  the machine on 2026-11-12; the history from our dated notes.
- Docker Engine 29.9.3 installed on the NAS the same evening (2026-11-12) from Docker's own repository, `daemon.json` written
  before the install so the data root is on the data volume from the first start; the power-off gate gains a no-container
  check (`scripts/nas-poweroff-gated.sh`).
- Example files in `examples/`, the scrub check in `scripts/scrub_check.sh`, the reel generator in `scripts/make_reel.py`.
