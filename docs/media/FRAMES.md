# The reel's frames

Every frame of `reel.gif` / `reel.mp4` is drawn by `scripts/make_reel.py` from the text below;
nothing is captured from a screen. Addresses are RFC 5737 documentation addresses; MACs are placeholders.

## 01: Lion UGREEN NAS (title, 4 s)

    A UGREEN NASync DXP4800 Pro, wiped of UGOS Pro,
    running Ubuntu Server 24.04 LTS
    
    Unofficial. Not affiliated with UGREEN. At your own risk.

## 02: The hardware (cards, 5 s)

    4 bays, 2 M.2 slots, Intel Core i3-1315U, 8 GB RAM (7.7 GB usable)
    10 GbE port: Aquantia AQC113 (driver atlantic)
    2.5 GbE port: Intel I226-V (driver igc)
    Drives: bay 1 a 20 TB data drive; bay 2 a second 20 TB drive from 2026-10-16
    Done on this one model only: the DXP4800 Pro. Other DXP models are untested by us

## 03: Step 1: the USB installer  (image checked 2026-09-12) (term, 5 s)

    $ sha256sum -c SHA256SUMS --ignore-missing
    ubuntu-24.04.5-live-server-amd64.iso: OK
    $ lsblk                      # find the stick, check twice
    $ sudo dd if=ubuntu-24.04.5-live-server-amd64.iso of=/dev/sdX \
           bs=4M status=progress conv=fsync

## 04: Step 2: the BIOS watchdog  (2026-09-15) (cards, 5 s)

    UGOS feeds the hardware watchdog; anything else does not
    With it on, a non-UGOS system reboots every few minutes
    Disable it in the BIOS (look for Watchdog / WDT), put the USB stick first, save
    Ours has run Ubuntu through every session since, hours at a time

## 05: Step 3: the installer answers  (2026-09-15) (cards, 5 s)

    Ubuntu Server (not minimized)  ·  both ports on DHCP for now
    Storage: the internal 128 GB system SSD ONLY, never the data drives or the user M.2
    Tick: Install OpenSSH server  ·  no snaps
    Reboot, pull the stick, read the address off the login screen

## 06: Step 4: first boot over SSH  (2026-09-16) (term, 5 s)

    $ ssh-copy-id youruser@192.0.2.20
    $ ssh youruser@192.0.2.20
    $ sudo apt update && sudo apt full-upgrade -y
    $ sudo apt install -y nfs-kernel-server xfsprogs smartmontools ethtool
    # no keyboard or monitor needed from here on

## 07: Step 5: the two ports  (2026-09-16 / 09-19) (cards, 6 s)

    10 GbE  enp3s0   LAN only: an address, no default route, no DNS
    2.5 GbE enp6s0   the internet: default route and DNS
    First workaround for stalled downloads (2026-09-16); the cause was Step 6
    The split stayed: the fast port for the LAN, the other for the internet
    netplan: dhcp4-overrides  use-routes: false  use-dns: false  on the 10 GbE port

## 08: Step 6: the 10 GbE receive fix  (2026-09-17) (term, 7 s)

    $ iperf3 -c 192.0.2.10 -R      # receiving at the NAS
      220 kbit/s                   # sending was 939 Mbit/s
    $ sudo ethtool -K enp3s0 lro off gro off
    $ sudo ip link set enp3s0 down && sudo ip link set enp3s0 up
      941 Mbit/s                   # and 825 MB/s over SSH on the 10 GbE switch
    # persisted: a .link file (with NamePolicy=, see 09-30) + a one-shot service

## 09: Step 7: storage  (2026-09-16 / 10-16) (cards, 6 s)

    Drive 1: one GPT partition, XFS, mounted at /srv/data by UUID
    Drive 2: its own XFS, mounted INSIDE the export at /srv/data/Drive2
    nofail on the fstab line (ours: drive 2 only; put it on both)  ·  chattr +i  ·  crossmnt
    Independent drives, not a mirror: a dead drive loses only its own files
    Burn a new drive in: smartctl -t short, then -t long, then read -a

## 10: Step 8: NFS  (2026-09-16) (term, 6 s)

    # /etc/exports  -- read-only, to named clients, writes go over SSH
    /srv/data  192.0.2.10(ro,sync,no_subtree_check,crossmnt) \
               192.0.2.11(ro,sync,no_subtree_check,crossmnt)
    $ sudo exportfs -ra && sudo exportfs -v
    # client:  mount -t nfs -o ro,soft,nfsvers=4 192.0.2.20:/srv/data /mnt/nas

## 11: Step 9: Wake-on-LAN and a gated power-off  (2026-09-21 / 10-08) (cards, 6 s)

    Wake: a magic packet to each port's MAC; SSH answers about 25 s later
    Armed by the driver default; pin it with WakeOnLan=magic if you want it guaranteed
    Power off: one sudoers rule, one command: /usr/bin/systemctl poweroff
    Gate first: 0 NFS clients, 0 copy or download jobs, no indexer running
    The power-off goes INSIDE the gate's success branch (lesson of 2026-10-16)

## 12: Step 10: Docker Engine  (2026-11-12) (cards, 6 s)

    daemon.json FIRST: data-root on the data volume, /var/lib/docker never created
    Docker's apt repo: docker-ce 29.9.3, containerd.io 2.4.2, buildx, compose; 26 s
    hello-world clean, docker ps -a empty; the native services stay native
    The docker group is root without a password: know it, or use sudo docker
    The power-off gate gains a check: no container running

## 13: Known limits (cards, 5 s)

    RAM: one HTTPS download stream used ~2.5 GB; more than three stalled SSH
    MemoryHigh= per download service, vm.dirty_bytes 1 GB, downloads one at a time
    The 10 GbE port keeps LRO and GRO off, always
    Two independent drives, read-only NFS, power off only when idle

## 14: Timeline, 2026 (cards, 6 s)

    09-12 UGOS set up, decision to reinstall, image checked
    09-15 watchdog off, Ubuntu Server installed from the stick
    09-16 first boot: XFS, NFS, two-port routing   ·   09-17 the 10 GbE receive fix
    09-19 10 GbE switch, 825 MB/s   ·   09-21 Wake-on-LAN and power-off cycled 3x
    09-30 NamePolicy in the .link file   ·   10-08 sudoers rule   ·   10-16 second drive
    11-12 this write-up: configuration re-read from the machine, history from notes
    
    github.com/sunnychase/lion-ugreen-nas   ·   MIT   ·   unofficial, not affiliated with UGREEN

- `docs/media/reel.mp4` sha256 07bef3ec826426e771d7fa5a8ff0d53b35a615c0a26221d961cc3295b41727cd (734,455 bytes)
- `docs/media/reel.gif` sha256 e7dad9b244a81b41e4a086d34c985ba27c6b30ef41382ece2c123e9cd9b51811 (847,046 bytes)
