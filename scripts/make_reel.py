#!/usr/bin/env python3
"""make_reel.py -- draw the reel in docs/media from text: one card per step, no screen captures, no photographs.
Writes docs/media/frames/NN.png, docs/media/reel.mp4 (1280x720, h264), docs/media/reel.gif (860 px wide) and
docs/media/FRAMES.md (the text each frame is drawn from). Needs Pillow and ffmpeg. Run from the repository root:
    python3 scripts/make_reel.py
Every address below is from the documentation ranges (RFC 5737) and every MAC is a 02:00:00:00:00:xx placeholder."""
import hashlib
import os
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = os.path.join(ROOT, "docs", "media")
FRAMES_DIR = os.path.join(MEDIA, "frames")
W, H = 1280, 720
BG, PANEL, INK, DIM, ACCENT, GREEN, AMBER, RED = "#0b1220", "#121c30", "#e8eef8", "#8fa1bf", "#4f8cff", "#3ddc97", "#f5b942", "#ff6b6b"
F = "/usr/share/fonts/truetype/dejavu/"
font = lambda name, size: ImageFont.truetype(F + name, size)
TITLE, SUB, BODY, MONO, SMALL = font("DejaVuSans-Bold.ttf", 44), font("DejaVuSans.ttf", 26), font("DejaVuSans.ttf", 24), font("DejaVuSansMono.ttf", 22), font("DejaVuSans.ttf", 18)

# (title, kind, lines, seconds).  kind: "cards" = bullet card, "term" = terminal-style frame, "title" = title card.
FRAMES = [
    ("Lion UGREEN NAS", "title", [
        "A UGREEN NASync DXP4800 Pro, wiped of UGOS Pro,",
        "running Ubuntu Server 24.04 LTS",
        "",
        "Unofficial. Not affiliated with UGREEN. At your own risk."], 4.0),
    ("The hardware", "cards", [
        "4 bays, 2 M.2 slots, Intel Core i3-1315U, 8 GB RAM (7.7 GB usable)",
        "10 GbE port: Aquantia AQC113 (driver atlantic)",
        "2.5 GbE port: Intel I226-V (driver igc)",
        "Drives: bay 1 a 20 TB data drive; bay 2 a second 20 TB drive from 2026-10-16",
        "Done on this one model only: the DXP4800 Pro. Other DXP models are untested by us"], 5.0),
    ("Step 1: the USB installer  (image checked 2026-09-12)", "term", [
        "$ sha256sum -c SHA256SUMS --ignore-missing",
        "ubuntu-24.04.5-live-server-amd64.iso: OK",
        "$ lsblk                      # find the stick, check twice",
        "$ sudo dd if=ubuntu-24.04.5-live-server-amd64.iso of=/dev/sdX \\",
        "       bs=4M status=progress conv=fsync"], 5.0),
    ("Step 2: the BIOS watchdog  (2026-09-15)", "cards", [
        "UGOS feeds the hardware watchdog; anything else does not",
        "With it on, a non-UGOS system reboots every few minutes",
        "Disable it in the BIOS (look for Watchdog / WDT), put the USB stick first, save",
        "Ours has run Ubuntu through every session since, hours at a time"], 5.0),
    ("Step 3: the installer answers  (2026-09-15)", "cards", [
        "Ubuntu Server (not minimized)  ·  both ports on DHCP for now",
        "Storage: the internal 128 GB system SSD ONLY, never the data drives or the user M.2",
        "Tick: Install OpenSSH server  ·  no snaps",
        "Reboot, pull the stick, read the address off the login screen"], 5.0),
    ("Step 4: first boot over SSH  (2026-09-16)", "term", [
        "$ ssh-copy-id youruser@192.0.2.20",
        "$ ssh youruser@192.0.2.20",
        "$ sudo apt update && sudo apt full-upgrade -y",
        "$ sudo apt install -y nfs-kernel-server xfsprogs smartmontools ethtool",
        "# no keyboard or monitor needed from here on"], 5.0),
    ("Step 5: the two ports  (2026-09-16 / 09-19)", "cards", [
        "10 GbE  enp3s0   LAN only: an address, no default route, no DNS",
        "2.5 GbE enp6s0   the internet: default route and DNS",
        "First workaround for stalled downloads (2026-09-16); the cause was Step 6",
        "The split stayed: the fast port for the LAN, the other for the internet",
        "netplan: dhcp4-overrides  use-routes: false  use-dns: false  on the 10 GbE port"], 6.0),
    ("Step 6: the 10 GbE receive fix  (2026-09-17)", "term", [
        "$ iperf3 -c 192.0.2.10 -R      # receiving at the NAS",
        "  220 kbit/s                   # sending was 939 Mbit/s",
        "$ sudo ethtool -K enp3s0 lro off gro off",
        "$ sudo ip link set enp3s0 down && sudo ip link set enp3s0 up",
        "  941 Mbit/s                   # and 825 MB/s over SSH on the 10 GbE switch",
        "# persisted: a .link file (with NamePolicy=, see 09-30) + a one-shot service"], 7.0),
    ("Step 7: storage  (2026-09-16 / 10-16)", "cards", [
        "Drive 1: one GPT partition, XFS, mounted at /srv/data by UUID",
        "Drive 2: its own XFS, mounted INSIDE the export at /srv/data/Drive2",
        "nofail on the fstab line (ours: drive 2 only; put it on both)  ·  chattr +i  ·  crossmnt",
        "Independent drives, not a mirror: a dead drive loses only its own files",
        "Burn a new drive in: smartctl -t short, then -t long, then read -a"], 6.0),
    ("Step 8: NFS  (2026-09-16)", "term", [
        "# /etc/exports  -- read-only, to named clients, writes go over SSH",
        "/srv/data  192.0.2.10(ro,sync,no_subtree_check,crossmnt) \\",
        "           192.0.2.11(ro,sync,no_subtree_check,crossmnt)",
        "$ sudo exportfs -ra && sudo exportfs -v",
        "# client:  mount -t nfs -o ro,soft,nfsvers=4 192.0.2.20:/srv/data /mnt/nas"], 6.0),
    ("Step 9: Wake-on-LAN and a gated power-off  (2026-09-21 / 10-08)", "cards", [
        "Wake: a magic packet to each port's MAC; SSH answers about 25 s later",
        "Armed by the driver default; pin it with WakeOnLan=magic if you want it guaranteed",
        "Power off: one sudoers rule, one command: /usr/bin/systemctl poweroff",
        "Gate first: 0 NFS clients, 0 copy or download jobs, no indexer running",
        "The power-off goes INSIDE the gate's success branch (lesson of 2026-10-16)"], 6.0),
    ("Step 10: Docker Engine  (2026-11-12)", "cards", [
        "daemon.json FIRST: data-root on the data volume, /var/lib/docker never created",
        "Docker's apt repo: docker-ce 29.9.3, containerd.io 2.4.2, buildx, compose; 26 s",
        "hello-world clean, docker ps -a empty; the native services stay native",
        "The docker group is root without a password: know it, or use sudo docker",
        "The power-off gate gains a check: no container running"], 6.0),
    ("Known limits", "cards", [
        "RAM: one HTTPS download stream used ~2.5 GB; more than three stalled SSH",
        "MemoryHigh= per download service, vm.dirty_bytes 1 GB, downloads one at a time",
        "The 10 GbE port keeps LRO and GRO off, always",
        "Two independent drives, read-only NFS, power off only when idle"], 5.0),
    ("Timeline, 2026", "cards", [
        "09-12 UGOS set up, decision to reinstall, image checked",
        "09-15 watchdog off, Ubuntu Server installed from the stick",
        "09-16 first boot: XFS, NFS, two-port routing   ·   09-17 the 10 GbE receive fix",
        "09-19 10 GbE switch, 825 MB/s   ·   09-21 Wake-on-LAN and power-off cycled 3x",
        "09-30 NamePolicy in the .link file   ·   10-08 sudoers rule   ·   10-16 second drive",
        "11-12 this write-up: configuration re-read from the machine, history from notes",
        "",
        "github.com/sunnychase/lion-ugreen-nas   ·   MIT   ·   unofficial, not affiliated with UGREEN"], 6.0),
]


def card(idx, title, kind, lines):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # header strip
    d.rectangle([0, 0, W, 6], fill=ACCENT)
    logo = os.path.join(ROOT, "docs", "images", "logo.png")
    if os.path.exists(logo):
        lg = Image.open(logo).convert("RGBA").resize((56, 56))
        im.paste(lg, (48, 34), lg)
    d.text((120, 40), "Lion UGREEN NAS", font=SUB, fill=DIM)
    d.text((W - 48, 44), f"{idx + 1:02d} / {len(FRAMES):02d}", font=SMALL, fill=DIM, anchor="ra")
    if kind == "title":
        d.text((W // 2, 250), title, font=font("DejaVuSans-Bold.ttf", 64), fill=INK, anchor="mm")
        y = 330
        for ln in lines:
            d.text((W // 2, y), ln, font=SUB, fill=DIM if not ln.startswith("Unofficial") else AMBER, anchor="mm")
            y += 40
        return im
    tf = TITLE
    while d.textlength(title, font=tf) > W - 96 and tf.size > 26:      # shrink a long title to the card's width
        tf = font("DejaVuSans-Bold.ttf", tf.size - 2)
    d.text((48, 120), title, font=tf, fill=INK)
    d.rectangle([48, 190, W - 48, H - 60], fill=PANEL, outline="#1f2d4a")
    if kind == "term":
        d.rectangle([48, 190, W - 48, 226], fill="#1a2742")
        for i, c in enumerate((RED, AMBER, GREEN)):
            d.ellipse([66 + i * 26, 200, 82 + i * 26, 216], fill=c)
        y = 250
        for ln in lines:
            col = GREEN if ln.startswith("$") else (DIM if ln.startswith("#") else INK)
            d.text((80, y), ln, font=MONO, fill=col)
            y += 40
    else:
        y = 230
        for ln in lines:
            if ln:
                d.ellipse([80, y + 10, 92, y + 22], fill=ACCENT)
                d.text((112, y), ln, font=BODY, fill=INK)
            y += 50
    for ln in lines:                      # a line wider than the card fails the build instead of being cut off
        width = d.textlength(ln, font=MONO if kind == "term" else BODY) + (80 if kind == "term" else 112)
        assert width <= W - 48, f"card {idx + 1} line too wide ({width:.0f} px): {ln}"
    # progress bar
    d.rectangle([48, H - 40, W - 48, H - 36], fill="#1f2d4a")
    d.rectangle([48, H - 40, 48 + int((W - 96) * (idx + 1) / len(FRAMES)), H - 36], fill=ACCENT)
    return im


def main():
    if os.path.isdir(FRAMES_DIR):
        shutil.rmtree(FRAMES_DIR)
    os.makedirs(FRAMES_DIR)
    concat = []
    md = ["# The reel's frames", "", "Every frame of `reel.gif` / `reel.mp4` is drawn by `scripts/make_reel.py` from the text below;",
          "nothing is captured from a screen. Addresses are RFC 5737 documentation addresses; MACs are placeholders.", ""]
    for i, (title, kind, lines, secs) in enumerate(FRAMES):
        p = os.path.join(FRAMES_DIR, f"{i + 1:02d}.png")
        card(i, title, kind, lines).save(p)
        concat += [f"file '{p}'", f"duration {secs}"]
        md += [f"## {i + 1:02d}: {title} ({kind}, {secs:.0f} s)", ""] + [f"    {ln}" for ln in lines] + [""]
    concat += [f"file '{p}'"]          # ffmpeg concat: repeat the last file so its duration counts
    lst = os.path.join(FRAMES_DIR, "list.txt")
    open(lst, "w").write("\n".join(concat) + "\n")
    mp4, gif = os.path.join(MEDIA, "reel.mp4"), os.path.join(MEDIA, "reel.gif")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-vf", "fps=25,format=yuv420p",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-movflags", "+faststart", mp4], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf",
                    "fps=4,scale=860:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=3",
                    "-loop", "0", gif], check=True)
    os.remove(lst)
    for p in (mp4, gif):
        md.append(f"- `{os.path.relpath(p, ROOT)}` sha256 {hashlib.sha256(open(p, 'rb').read()).hexdigest()} ({os.path.getsize(p):,} bytes)")
    open(os.path.join(MEDIA, "FRAMES.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md[-2:]))


if __name__ == "__main__":
    main()
