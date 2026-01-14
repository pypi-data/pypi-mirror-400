from dataclasses import dataclass
import re

from . import PCIDevice
from .gpudb import GpuDevice, GpuDeviceDB


@dataclass
class RadeonGPU(GpuDevice):
    pci_device: PCIDevice
    codename: str
    is_mobility: bool
    is_IGP: bool

    @property
    def unknown_fields(self):
        missing = set()

        if self.architecture is None:
            missing.add("architecture")

        if self.gfx_version is None:
            missing.add("gfx_version")

        return missing

    @property
    def architecture(self):
        families = {
            # R100
            "R100": "R100",
            "RV100": "R100",
            "RV200": "R100",
            "RS100": "R100",
            "RS200": "R100",

            # R200
            "R200": "R200",
            "RV250": "R200",
            "RV280": "R200",
            "RS300": "R200",

            # R300
            "R300": "R300",
            "R350": "R300",
            "RV350": "R300",
            "RV380": "R300",
            "RS400": "R300",
            "RS480": "R300",

            # R400
            "RV410": "R400",
            "R423": "R400",
            "R420": "R400",
            "RS600": "R400",
            "RS690": "R400",
            "RS740": "R400",

            # R500
            "RV515": "R500",
            "R520": "R500",
            "RV530": "R500",
            "RV560": "R500",
            "RV570": "R500",
            "R580": "R500",

            # R600
            "R600": "R600",
            "RV610": "R600",
            "RV620": "R600",
            "RV630": "R600",
            "RV635": "R600",
            "RV670": "R600",
            "RS780": "R600",
            "RS880": "R600",

            # R700
            "RV710": "R700",
            "RV730": "R700",
            "RV740": "R700",
            "RV770": "R700",

            # Evergreen
            "CEDAR": "Evergreen",
            "REDWOOD": "Evergreen",
            "JUNIPER": "Evergreen",
            "CYPRESS": "Evergreen",
            "PALM": "Evergreen",
            "SUMO": "Evergreen",
            "SUMO2": "Evergreen",
            "HEMLOCK": "Evergreen",

            # Northern Islands
            "ARUBA": "NorthernIslands",
            "BARTS": "NorthernIslands",
            "TURKS": "NorthernIslands",
            "CAICOS": "NorthernIslands",
            "CAYMAN": "NorthernIslands",

            # Southern Islands
            "VERDE": "SouthernIslands",
            "PITCAIRN": "SouthernIslands",
            "TAHITI": "SouthernIslands",
            "OLAND": "SouthernIslands",
            "HAINAN": "SouthernIslands",

            # Sea Islands
            "BONAIRE": "SeaIslands",
            "KABINI": "SeaIslands",
            "MULLINS": "SeaIslands",
            "KAVERI": "SeaIslands",
            "HAWAII": "SeaIslands",
        }
        return families.get(self.codename)

    @property
    def gfx_version(self):
        versions = {
            # GFX1
            "R100": 1,
            "RV100": 1,
            "RV200": 1,
            "RS100": 1,
            "RS200": 1,
            "R200": 1,
            "RV250": 1,
            "RV280": 1,
            "RS300": 1,

            # GFX2
            "R300": 2,
            "R350": 2,
            "RV350": 2,
            "RV380": 2,
            "RS400": 2,
            "RS480": 2,
            "RV410": 2,
            "R423": 2,
            "R420": 2,
            "RS600": 2,
            "RS690": 2,
            "RS740": 2,
            "RV515": 2,
            "R520": 2,
            "RV530": 2,
            "RV560": 2,
            "RV570": 2,
            "R580": 2,

            # GFX3
            "R600": 3,
            "RV610": 3,
            "RV620": 3,
            "RV630": 3,
            "RV635": 3,
            "RV670": 3,
            "RS780": 3,
            "RS880": 3,
            "RV710": 3,
            "RV730": 3,
            "RV740": 3,
            "RV770": 3,

            # GFX4
            "CEDAR": 4,
            "REDWOOD": 4,
            "JUNIPER": 4,
            "CYPRESS": 4,
            "PALM": 4,
            "SUMO": 4,
            "SUMO2": 4,
            "HEMLOCK": 4,
            "BARTS": 4,
            "HEMPLOCK": 4,
            "TURKS": 4,
            "CAICOS": 4,

            # GFX5
            "ARUBA": 5,
            "CAYMAN": 5,

            # GFX6
            "VERDE": 6,
            "PITCAIRN": 6,
            "TAHITI": 6,
            "OLAND": 6,
            "HAINAN": 6,

            # GFX7
            "BONAIRE": 7,
            "KABINI": 7,
            "MULLINS": 7,
            "KAVERI": 7,
            "HAWAII": 7,
        }

        return versions.get(self.codename)

    @property
    def base_name(self):
        return f"gfx{self.gfx_version}-{self.codename}".lower()

    @property
    def tags(self):
        tags = set()

        tags.add(f"radeon:pciid:{self.pciid}")
        tags.add(f"radeon:codename:{self.codename}")
        tags.add(f"radeon:architecture:{self.architecture}")
        tags.add(f"radeon:generation:{self.gfx_version}")
        tags.add(f"radeon:{'integrated' if self.is_IGP or self.is_mobility else 'discrete'}")

        return tags

    @property
    def structured_tags(self):
        return {
            # Common fields between all GPUs
            "type": "radeon",
            "pciid": self.pciid,
            "architecture": self.architecture,
            "codename": self.codename,
            "generation": self.gfx_version,
            "integrated": self.is_IGP or self.is_mobility,
        }

    def __str__(self):
        return (f"<RadeonGPU: PCIID {self.pciid} - {self.codename} - {self.architecture} "
                f"- gfx{self.gfx_version}>")


class RadeonGpuDeviceDB(GpuDeviceDB):
    DB_URL = "https://gitlab.freedesktop.org/drm/tip/-/raw/drm-tip/include/drm/drm_pciids.h"
    DB_FILENAME = "drm_pciids.h"

    def parse_db(self, db):
        self.devices = dict()

        # Expected format:
        # {0x1002, 0x5b60, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_RV380|RADEON_NEW_MEMMAP}, \
        comp_re = re.compile(r"^\s*{0x1002, (?P<device_id>0x[\da-fA-F]+), "
                             r"PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_"
                             r"(?P<codename>[\dA-Z]+)"
                             r"(?P<properties>|.*)"
                             r"}, \\\s*$")

        started = False
        for line in db.splitlines():
            if not started:
                if line == "#define radeon_PCI_IDS \\":
                    started = True
                    continue
            else:
                if "{0, 0, 0}" in line:
                    break

                if m := comp_re.match(line):
                    try:
                        dev = m.groupdict()
                        pci_device = PCIDevice(vendor_id=0x1002, product_id=int(dev["device_id"], 16),
                                               revision=0)
                        self.devices[pci_device] = RadeonGPU(pci_device=pci_device,
                                                             codename=dev["codename"],
                                                             is_IGP="RADEON_IS_IGP" in dev["properties"],
                                                             is_mobility="RADEON_IS_MOBILITY" in dev["properties"])
                    except ValueError as e:  # pragma: nocover
                        print(f"WARNING: Failed to parse the RadeonGPU line '{line}', got '{dev}' with exception: {e}")
                        continue
