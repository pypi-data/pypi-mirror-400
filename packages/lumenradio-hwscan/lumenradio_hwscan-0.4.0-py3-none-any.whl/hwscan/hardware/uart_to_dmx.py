#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from .util import by_id_links_for_devnode


def _read(dev: Path, name: str) -> str:
    f = dev / name
    return f.read_text().strip() if f.exists() else ""


def _first_tty_usb(dev: Path):
    for p in dev.rglob("ttyUSB*"):
        return f"/dev/{p.name}"
    return None


def detect():
    """Detect LumenRadio USB-to-DMX FTDI bridges (VID=0403, PID=6015)."""
    VID = "0403"
    PID = "6015"

    results = {}
    root = Path("/sys/bus/usb/devices")
    if not root.exists():
        return results

    for dev in root.iterdir():
        try:
            idv_p = dev / "idVendor"
            idp_p = dev / "idProduct"
            if not (idv_p.exists() and idp_p.exists()):
                continue

            vid = _read(dev, "idVendor").lower()
            pid = _read(dev, "idProduct").lower()
            if vid != VID or pid != PID:
                continue

            product = _read(dev, "product")
            manufacturer = _read(dev, "manufacturer")
            serial = _read(dev, "serial")

            prod_l = product.lower() if product else ""
            manuf_l = manufacturer.lower() if manufacturer else ""
            if "lumenradio" not in manuf_l and "dmx" not in prod_l:
                continue

            tty_node = _first_tty_usb(dev)
            if not tty_node:
                continue

            entry = {
                "type": "uart-to-dmx",
                "vendor_id": VID,
                "product_id": PID,
                "manufacturer": manufacturer or "LumenRadio",
                "product": product or "USB to DMX",
                "usb_path": dev.name,
                "tty": tty_node,
                "serial": serial or dev.name,
            }

            links = by_id_links_for_devnode(tty_node)
            if links:
                entry["by_id"] = links

            key = serial or dev.name
            results[key] = entry

        except Exception:
            continue

    return results
