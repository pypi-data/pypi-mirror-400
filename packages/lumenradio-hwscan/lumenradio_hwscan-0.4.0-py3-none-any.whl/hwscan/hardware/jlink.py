#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detector for SEGGER J-Link debug probes."""

from pathlib import Path
from typing import Dict, Optional

from .util import by_id_links_for_devnode


def _read_text(path: Path) -> str:
    try:
        return path.read_text().strip()
    except Exception:
        return ""


def _first_serial_node(dev: Path) -> Optional[str]:
    """
    Return the first TTY node exposed by the USB composite device.
    J-Link probes typically enumerate as CDC ACM, but older firmware can show up
    as ttyUSB devices, so we check both names.
    """
    for pattern in ("ttyACM*", "ttyUSB*"):
        try:
            for node in dev.rglob(pattern):
                return f"/dev/{node.name}"
        except Exception:
            continue
    return None


def detect() -> Dict[str, dict]:
    """Detect connected SEGGER J-Link debug probes via sysfs."""
    VID = "1366"  # SEGGER
    PID = "1024"  # J-Link (CDC ACM)

    results: Dict[str, dict] = {}
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

            serial = _read_text(dev / "serial")
            if not serial:
                # Serial number is stable and used as the dict key
                continue

            product = _read_text(dev / "product") or "J-Link"
            manuf = _read_text(dev / "manufacturer") or "SEGGER"

            entry = {
                "type": "segger-jlink",
                "vendor_id": VID,
                "product_id": PID,
                "manufacturer": manuf,
                "product": product,
                "usb_path": dev.name,
                "serial": serial,
            }

            tty_node = _first_serial_node(dev)
            if tty_node:
                entry["tty"] = tty_node
                by_ids = by_id_links_for_devnode(tty_node)
                if by_ids:
                    entry["by_id"] = by_ids

            hid_nodes = []
            try:
                for hid in dev.rglob("hidraw*"):
                    hid_nodes.append(f"/dev/{hid.name}")
            except Exception:
                hid_nodes = []
            if hid_nodes:
                entry["hidraw"] = sorted(set(hid_nodes))

            results[serial] = entry
        except Exception:
            continue

    return results
