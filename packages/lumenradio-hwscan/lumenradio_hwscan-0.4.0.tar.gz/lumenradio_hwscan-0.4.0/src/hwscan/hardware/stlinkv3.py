#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# src/hwscan/hardware/stlinkv3.py

from pathlib import Path
import subprocess
from typing import Dict, Optional
from .util import by_id_links_for_devnode


def _blk_label(devnode: str) -> str:
    """Return filesystem label for a block dev (e.g., /dev/sda or /dev/sda1)."""
    try:
        out = subprocess.run(
            ["blkid", "-o", "value", "-s", "LABEL", devnode],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return out or ""
    except Exception:
        return ""


def _mountpoint_for(devnode: str) -> Optional[str]:
    """If devnode is mounted, return its first mountpoint. No sudo needed."""
    try:
        base = Path(devnode).resolve()
        with open("/proc/mounts", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    src, mnt = parts[0], parts[1]
                    try:
                        if Path(src).resolve() == base or src == str(base):
                            return mnt
                    except Exception:
                        pass
    except Exception:
        pass
    # Fallback to lsblk
    try:
        out = subprocess.run(
            ["lsblk", "-no", "MOUNTPOINT", devnode],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return out or None
    except Exception:
        return None


def _read_msd_info_if_mounted(devnode: str) -> Dict[str, str]:
    """Read small info files if the MSD is already mounted; never mounts."""
    info: Dict[str, str] = {}
    mnt = _mountpoint_for(devnode)
    if not mnt:
        return info
    try:
        mp = Path(mnt)
        for name in ("DETAILS.TXT", "STLINK.TXT", "MBED.HTM", "INFO_UF2.TXT"):
            p = mp / name
            if p.exists() and p.is_file() and p.stat().st_size < 64 * 1024:
                info[name] = p.read_text(errors="ignore")
    except Exception:
        pass
    return info


def _infer_board_model(label: str, info: Dict[str, str]) -> Optional[str]:
    """
    Normalize label + info contents to decide the exact board.
    Returns friendly model name or None.
    """
    text = (label or "") + "\n" + "\n".join(info.values())
    t = text.lower()
    # Prefer exact part matches if present
    if "h563zi" in t or "h563" in t:
        return "NUCLEO-H563ZI"
    if "h723zg" in t or "h723" in t:
        return "NUCLEO-H723ZG"
    return None


def detect():
    VID = "0483"
    PID = "374e"

    results = {}
    root = Path("/sys/bus/usb/devices")
    if not root.exists():
        return results

    for dev in root.iterdir():
        try:
            idv = dev / "idVendor"
            idp = dev / "idProduct"
            if not (idv.exists() and idp.exists()):
                continue
            if (
                idv.read_text().strip().lower() != VID
                or idp.read_text().strip().lower() != PID
            ):
                continue

            def rd(name):
                f = dev / name
                return f.read_text().strip() if f.exists() else ""

            serial = rd("serial")
            if not serial:
                continue
            product = rd("product") or "STLINK-V3"
            manuf = rd("manufacturer")

            entry = {
                "type": "stlink-v3",
                "vendor_id": VID,
                "product_id": PID,
                "manufacturer": manuf,
                "product": product,
                "usb_path": dev.name,
            }

            # CDC ACM node (e.g., /dev/ttyACM0)
            tty_node = None
            for p in dev.rglob("ttyACM*"):
                tty_node = f"/dev/{p.name}"
                break
            if tty_node:
                entry["tty"] = tty_node
                by_ids = by_id_links_for_devnode(tty_node)
                if by_ids:
                    entry["by_id"] = by_ids

            # Mass-storage nodes (whole disk and partitions)
            blocks = []
            for blk in dev.rglob("block/sd*"):
                blocks.append(f"/dev/{blk.name}")
            if blocks:
                entry["storage"] = sorted(set(blocks))

            # Derive board_model directly (no board_hint)
            label = ""
            details: Dict[str, str] = {}
            if "storage" in entry:
                for blk in entry["storage"]:
                    if not label:
                        label = _blk_label(blk)  # e.g., "NOD_H563ZI", "NUCLEO_H723ZG"
                    if not details:
                        details = _read_msd_info_if_mounted(blk)
                    if label and details:
                        break

            model = _infer_board_model(label, details)
            if model:
                entry["board_model"] = model

            results[serial] = entry
        except Exception:
            continue

    return results
