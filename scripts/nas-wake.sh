#!/usr/bin/env bash
# nas-wake.sh MAC [MAC...]  -- wake the NAS with Wake-on-LAN magic packets, sent to every MAC given (one per port),
# on UDP ports 7 and 9, to the limited broadcast and to the LAN broadcast. Needs: both NAS ports with Wake-on: g
# (`sudo ethtool enp3s0 | grep Wake-on`). Our NAS answers ssh about 25 s after the packet (measured 2026-09-21).
#   ./nas-wake.sh 02:00:00:00:00:01 02:00:00:00:00:02
# The LAN broadcast address is read from the first default-route interface; set LAN_BCAST to override.
set -u
[ $# -ge 1 ] || { echo "usage: $0 MAC [MAC...]"; exit 2; }
BCAST="${LAN_BCAST:-$(ip -4 -o addr show "$(ip route show default | awk '{print $5; exit}')" | awk '{print $6; exit}')}"
python3 - "$BCAST" "$@" <<'PY'
import socket, sys
bcast, macs = sys.argv[1], sys.argv[2:]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
for mac in macs:
    raw = bytes.fromhex(mac.replace(":", "").replace("-", ""))
    if len(raw) != 6:
        sys.exit(f"not a MAC: {mac}")
    pkt = b"\xff" * 6 + raw * 16
    for port in (7, 9):
        s.sendto(pkt, ("255.255.255.255", port))
        if bcast:
            s.sendto(pkt, (bcast, port))
    print(f"magic packet sent to {mac}")
PY
echo "wait about 25-60 s, then ssh to the NAS"
