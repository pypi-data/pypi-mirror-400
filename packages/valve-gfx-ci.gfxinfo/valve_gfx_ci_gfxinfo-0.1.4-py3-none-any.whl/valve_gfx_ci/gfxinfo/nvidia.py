from dataclasses import dataclass
import re

from . import PCIDevice
from .gpudb import GpuDevice, GpuDeviceDB


@dataclass
class NvidiaGPU(GpuDevice):
    pci_device: PCIDevice
    marketing_name: str
    vdpau: str = None

    @property
    def unknown_fields(self):
        missing = set()

        if self.codename is None:
            missing.add("codename")
        if self.architecture is None:
            missing.add("architecture")

        return missing

    @property
    def codename(self):
        dev_id = self.pci_device.product_id

        # Powered by https://www.techpowerup.com/gpu-specs/?generation=GeForce%20MX&sort=generation#GeForce%20RTX%202070
        # WARNING: Nvidia routinely uses different chipsets for the same marketing name, so use the above link to
        # figure out all the possible chipsets used... and remember that neither database is complete! So, trust your
        # gut and try to find pciid-ranges where possible.
        if dev_id == 0x20:
            return "NV04"
        elif dev_id in [0x28, 0x29, 0x2c, 0x2d]:
            return "NV05"
        elif dev_id == 0xa0:
            return "NV0A"
        elif dev_id in [0x100, 0x101, 0x103]:
            return "NV10"
        elif dev_id in [0x110, 0x111, 0x112, 0x113]:
            return "NV11"
        elif dev_id in [0x150, 0x151, 0x152, 0x153]:
            return "NV15"
        elif dev_id >= 0x170 and dev_id <= 0x17d:
            return "NV17"
        elif dev_id >= 0x181 and dev_id <= 0x18c:
            return "NV18"
        elif dev_id == 0x1a0:
            return "NV1A"
        elif dev_id == 0x1f0:
            return "NV1F"
        elif dev_id in [0x200, 0x201, 0x202, 0x203]:
            return "NV20"
        elif dev_id >= 0x250 and dev_id <= 0x25b:
            return "NV25"
        elif dev_id >= 0x280 and dev_id <= 0x28c:
            return "NV28"
        elif dev_id in [0x0fa]:
            return "NV39"
        elif dev_id in [0x0fb]:
            return "NV35"
        elif dev_id in [0x0fc]:
            return "NV37"
        elif dev_id in [0x0fd]:
            return "NV34"
        elif dev_id in [0x0fe]:
            return "NV38"
        elif dev_id in [0x301, 0x302, 0x308, 0x309]:
            return "NV30"
        elif dev_id in [0x311, 0x312, 0x314, 0x31a, 0x31b, 0x31c]:
            return "NV31"
        elif dev_id >= 0x320 and dev_id <= 0x32d:
            return "NV32"
        elif dev_id in [0x330, 0x331, 0x332, 0x333, 0x334, 0x338, 0x33f]:
            return "NV33"
        elif dev_id >= 0x341 and dev_id <= 0x34e:
            return "NV36"
        elif dev_id >= 0x040 and dev_id <= 0x04e:
            return "NV40"
        elif dev_id in [0x0f6, 0x218] or (dev_id >= 0xc0 and dev_id <= 0xce):
            return "NV41"
        elif dev_id in [0x0f1, 0x0f2, 0x0f3, 0x0f4] or (dev_id >= 0x140 and dev_id <= 0x14f):
            return "NV43"
        elif dev_id in [0x221, 0x222] or (dev_id >= 0x160 and dev_id <= 0x16a):
            return "NV44"
        elif dev_id in [0x0f8, 0x0f9]:
            return "NV45"
        elif dev_id in [0x211, 0x212, 0x215, 0x218]:
            return "NV48"
        elif dev_id in [0x0f5] or (dev_id >= 0x090 and dev_id <= 0x09d):
            return "G70"
        elif dev_id in [0x2e3, 0x2e4] or (dev_id >= 0x290 and dev_id <= 0x29f):
            return "G71"
        elif dev_id >= 0x1d0 and dev_id <= 0x1df:
            return "G72"
        elif dev_id in [0x2e0, 0x2e1, 0x2e2] or (dev_id >= 0x38b and dev_id <= 0x39e):
            return "G73"
        elif dev_id >= 0x240 and dev_id <= 0x247:
            return "MCP51"
        elif dev_id in [0x3d0, 0x3d1, 0x3d2, 0x3d5]:
            return "MCP61"
        elif dev_id in [0x3d6, 0x53a, 0x53b, 0x53e]:
            return "MCP68"
        elif dev_id in [0x531, 0x533]:
            return "MCP67"
        elif dev_id >= 0x7e0 and dev_id <= 0x7e5:
            return "MCP73"
        elif dev_id >= 0x191 and dev_id <= 0x19e:
            return "G80"
        elif dev_id >= 0x400 and dev_id <= 0x40f:
            return "G84"
        elif dev_id >= 0x420 and dev_id <= 0x42f:
            return "G86"
        elif dev_id in [0x410] or (dev_id >= 0x600 and dev_id <= 0x61f):
            return "G92"
        elif dev_id >= 0x621 and dev_id <= 0x63a:
            return "G94"
        elif dev_id >= 0x640 and dev_id <= 0x65c:
            return "G96"
        elif dev_id >= 0x6e0 and dev_id <= 0x6ff:
            return "G98"
        elif dev_id in [0x844, 0x845]:
            return "MCP77"
        elif dev_id in [0x840] or (dev_id >= 0x846 and dev_id <= 0x84f):
            return "MCP78"
        elif dev_id >= 0x860 and dev_id <= 0x87f:
            return "MCP79"
        elif dev_id >= 0x8a0 and dev_id <= 0x8a5:
            return "MCP89"
        elif dev_id >= 0x5e0 and dev_id <= 0x5ff:
            return "GT200"
        elif dev_id >= 0xca0 and dev_id <= 0xcbc:
            return "GT215"
        elif dev_id >= 0xa20 and dev_id <= 0xa3c:
            return "GT216"
        elif (dev_id >= 0xa60 and dev_id <= 0xa7c) or (dev_id >= 0x10c0 and dev_id <= 0x10d8):
            return "GT218"
        elif dev_id >= 0x6c0 and dev_id <= 0x6df:
            return "GF100"
        elif dev_id >= 0xe22 and dev_id <= 0xe3b:
            return "GF104"
        elif dev_id in [0xdd8, 0xdda]:
            return "GF106"
        elif (dev_id in [0xf00, 0xf01, 0x0f02] or
              (dev_id >= 0xdc0 and dev_id <= 0xdd6) or
              (dev_id >= 0xde0 and dev_id <= 0xdfc)):
            return "GF108"
        elif dev_id >= 0x1080 and dev_id <= 0x109b:
            return "GF110"
        elif dev_id >= 0x1200 and dev_id <= 0x1213:
            return "GF114"
        elif dev_id >= 0x1241 and dev_id <= 0x1251:
            return "GF116"
        elif dev_id in [0x1140]:
            return "GF117"
        elif dev_id in [0xf03] or (dev_id >= 0x1040 and dev_id <= 0x107d):
            return "GF119"
        elif dev_id >= 0x1180 and dev_id <= 0x11bf:
            return "GK104"
        elif dev_id >= 0x11c0 and dev_id <= 0x11fc:
            return "GK106"
        elif dev_id >= 0x0fc6 and dev_id <= 0xfff:
            return "GK107"
        elif dev_id in [0x103a, 0x103c] or (dev_id >= 0x1001 and dev_id <= 0x102A):
            return "GK110"
        elif dev_id in [0xfc9, 0x12b9, 0x12ba] or (dev_id >= 0x1280 and dev_id <= 0x129a):
            return "GK208"
        elif dev_id in [0x102d]:
            return "GK210"
        elif dev_id >= 0x1340 and dev_id <= 0x137d:
            return "GM108"
        elif dev_id >= 0x1380 and dev_id <= 0x13bc:
            return "GM107"
        elif (dev_id in [0x1617, 0x1618, 0x1619, 0x161a, 0x1667] or
              (dev_id >= 0x13c0 and dev_id <= 0x13fb)):
            return "GM204"
        elif dev_id >= 0x1401 and dev_id <= 0x1436:
            return "GM206"
        elif dev_id in [0x174d, 0x174e, 0x179c]:
            return "GM108"
        elif dev_id in [0x17c2, 0x17c8, 0x17f0, 0x17f1, 0x17fd]:
            return "GM200"
        elif dev_id >= 0x15f0 and dev_id <= 0x15f9:
            return "GP100"
        elif dev_id >= 0x1b00 and dev_id <= 0x1b38:
            return "GP102"
        elif dev_id >= 0x1b80 and dev_id <= 0x1be1:
            return "GP104"
        elif dev_id >= 0x1c02 and dev_id <= 0x1c60:  # The 1c60 is surprising
            return "GP106"
        elif (dev_id >= 0x1c61 and dev_id <= 0x1c8f) or (dev_id >= 0x1c90 and dev_id <= 0x1cfb):
            return "GP107"
        elif dev_id >= 0x1d01 and dev_id <= 0x1d52:
            return "GP108"
        elif dev_id >= 0x1d81 and dev_id <= 0x1df6:
            return "GV100"
        elif dev_id >= 0x1d81 and dev_id <= 0x1e78:
            return "TU102"
        elif dev_id >= 0x1e81 and dev_id <= 0x1ef5:
            return "TU104"
        elif dev_id >= 0x1f02 and dev_id <= 0x1f76:
            return "TU106"
        elif dev_id >= 0x1f82 and dev_id <= 0x1ff9:
            return "TU117"
        elif dev_id >= 0x20b0 and dev_id <= 0x20fd:
            return "GA100"
        elif dev_id >= 0x2182 and dev_id <= 0x21d1:
            return "TU116"
        elif dev_id >= 0x2203 and dev_id <= 0x2238:
            return "GA102"
        elif dev_id in [0x230e, 0x2329, 0x232c]:
            return "GH20"
        elif dev_id >= 0x2321 and dev_id <= 0x233b:
            return "GH100"
        elif dev_id >= 0x2342 and dev_id <= 0x2348:
            return "GH200"
        elif dev_id >= 0x2482 and dev_id <= 0x24fa:
            return "GA104"
        elif dev_id in [0x2414, 0x2420, 0x2438, 0x2460]:
            return "GA103"
        elif dev_id >= 0x2503 and dev_id <= 0x2584:
            return "GA106"
        elif dev_id >= 0x25a0 and dev_id <= 0x25fb:
            return "GA107"
        elif dev_id >= 0x2684 and dev_id <= 0x26ba:
            return "AD102"
        elif dev_id >= 0x2702 and dev_id <= 0x2770:
            return "AD103"
        elif dev_id >= 0x2782 and dev_id <= 0x27fb:
            return "AD104"
        elif dev_id >= 0x2803 and dev_id <= 0x2882:
            return "AD106"
        elif dev_id >= 0x28a0 and dev_id <= 0x28f8:
            return "AD107"
        elif dev_id == 0x2901:
            return "GB100"
        elif dev_id == 0x2941:
            return "GB200"
        elif dev_id == 0x29bb:
            return "P2021"  # ??? What the heck is that?
        elif dev_id >= 0x2b85 and dev_id <= 0x2bb9:
            return "GB202"
        elif dev_id >= 0x2c02 and dev_id <= 0x2c79:
            return "GB203"
        elif dev_id == 0x2e12:
            return "GB20A"
        elif dev_id >= 0x2f04 and dev_id <= 0x2f58:
            return "GB205"
        elif dev_id >= 0x2d04 and dev_id <= 0x2df9:
            return "GB206"
        elif dev_id == 0x3182:
            return "B300"
        elif dev_id == 0x31c2:
            return "GB300"

        return None

    @property
    def architecture(self):
        # NOTE: Taken from https://nouveau.freedesktop.org/CodeNames.html

        if self.codename in ["NV04", "NV05", "NV0A"]:
            return "Fahrenheit"
        elif self.codename in ["NV10", "NV11", "NV15", "NV17", "NV18", "NV1A", "NV1F"]:
            return "Celcius"
        elif self.codename in ["NV20", "NV25", "NV28", "NV2A"]:
            return "Kelvin"
        elif self.codename in ["NV30", "NV31", "NV32", "NV33", "NV34", "NV35", "NV36", "NV37", "NV38", "NV39"]:
            return "Rankine"
        elif self.codename in ["NV40", "NV41", "NV42", "NV43", "NV44", "NV45", "NV48", "G72", "G70", "G71", "NV4A",
                               "G73", "MCP51", "MCP61", "MCP67", "MCP68", "MCP73"]:
            return "Curie"
        elif self.codename in ["G80", "G84", "G86", "G92", "G94", "G96", "G98", "GT200", "GT215", "GT216", "GT218",
                               "MCP77", "MCP78", "MCP79", "MCP7A", "MCP89"]:
            return "Tesla"
        elif self.codename in ["GF100", "GF108", "GF106", "GF104", "GF110", "GF114", "GF116", "GF117", "GF119"]:
            return "Fermi"
        elif self.codename in ["GK104", "GK106", "GK107", "GK110", "GK208", "GK210", "GK20A"]:
            return "Kepler"
        elif self.codename in ["GM107", "GM108", "GM200", "GM204", "GM206", "GM20B"]:
            return "Maxwell"
        elif self.codename in ["GP100", "GP102", "GP104", "GP106", "GP107", "GP108"]:
            return "Pascal"
        elif self.codename in ["GV100"]:
            return "Volta"
        elif self.codename in ["TU102", "TU104", "TU106", "TU116", "TU117"]:
            return "Turing"
        elif self.codename in ["GA100", "GA102", "GA103", "GA104", "GA106", "GA107", "GA10B"]:
            return "Ampere"
        elif self.codename in ["GH20", "GH100", "GH200"]:
            return "Hopper"
        elif self.codename in ["AD102", "AD103", "AD104", "AD106", "AD107"]:
            return "Ada"
        elif self.codename in ["GB100", "GB200", "P2021", "GB202", "GB203", "GB205", "GB206", "GB20A", "B300", "GB300"]:
            return "Blackwell"

        return None

    @property
    def is_integrated(self):
        if self.codename is not None:
            if self.codename.startswith("MCP") or self.codename in ["NV0A", "NV1A", "NV1F", "GK20A", "GM20B", "GA10B"]:
                return True
            else:
                return False
        else:
            return None

    @property
    def base_name(self):
        if self.architecture and self.codename:
            return f"{self.architecture}-{self.codename}".lower()
        else:
            return "nv-unk"

    @property
    def tags(self):
        return {
            f"nvidia:pciid:{self.pciid}",
            f"nvidia:codename:{self.codename}",
            f"nvidia:architecture:{self.architecture}",
            f"nvidia:{'integrated' if self.is_integrated else 'discrete'}",
        }

    @property
    def structured_tags(self):
        return {
            # Common fields between all GPUs
            "type": "nvidia",
            "pciid": self.pciid,
            "codename": self.codename,
            "architecture": self.architecture,
            "marketing_name": self.marketing_name,
            "integrated": self.is_integrated,

            # NVIDIA-specific
            "vdpau_features": self.vdpau,
        }

    def __str__(self):
        return (f"<NVIDIA: PCIID {self.pciid} - {self.codename} - {self.architecture}>")


class NvidiaGpuDeviceDB(GpuDeviceDB):
    DB_FILENAME = "nvidia-supportedchips.html"

    LATEST_KNOWN_VERSION = "590.48.01"

    @classmethod
    def db_url(cls):
        print("Fetching the version of the latest nvidia driver release")

        # Expected format: `535.86.05 535.86.05/NVIDIA-Linux-x86_64-535.86.05.run`
        try:
            r = cls._http_get("https://download.nvidia.com/XFree86/Linux-x86_64/latest.txt")
            fields = r.text.split()

            version = fields[0]
            if len(fields) == 2:
                # Because the folder may not match the version, use the path to the run file
                folder = fields[1].split('/')[0]
            else:  # pragma: nocover
                # The format changed, let's hope the first field is still the version and that it will match the folder'
                folder = version

            # NVIDIA seems to have forgotten to update latest.txt for some time, so let's force-use the latest-known
            # version until they remember to update latest.txt
            if folder == "580.105.08":  # pragma: nocover
                folder = cls.LATEST_KNOWN_VERSION

            print(f" => Found version {version}")
        except Exception as e:
            folder = cls.LATEST_KNOWN_VERSION
            print(f" => WARNING: Failed to get the latest version: {e}")
            print(f" => Defaulting to {folder}")

        return f"https://download.nvidia.com/XFree86/Linux-x86_64/{folder}/README/supportedchips.html"

    def parse_db(self, db):
        def gen_PCIDevice(v):
            # Expected format: "26B1 17AA 16A1" or "25FB"
            # NOTE: If three IDs are listed, the first is the PCI Device ID,
            #       the second is the PCI Subsystem Vendor ID
            #       and the third is the PCI Subsystem Device ID.

            subsys_vendor_id = subsys_product_id = 0

            fields = v.split()
            if len(fields) == 0:  # pragma: nocover
                print(f"WARNING: Can't parse the PCI Device ID '{v}'")
                return None

            product_id = int(fields[0], 16)
            if len(fields) == 3:
                subsys_vendor_id = int(fields[1], 16)
                subsys_product_id = int(fields[2], 16)

            return PCIDevice(vendor_id=0x10de, product_id=product_id, revision=0,
                             subsys_vendor_id=subsys_vendor_id, subsys_product_id=subsys_product_id)

        self.devices = dict()

        row_start_re = re.compile(r'<tr id="devid[0-9A-F_]+">')
        row_end_re = re.compile(r'</tr>')
        col_re = re.compile(r'<td>(.*)</td>')

        # Contains all the columns
        device_cols = []
        in_table_row = False
        for line in db.splitlines():
            if not in_table_row:
                if row_start_re.match(line):
                    in_table_row = True
            else:
                if row_end_re.match(line):
                    if len(device_cols) in [2, 3]:
                        try:
                            if pci_device := gen_PCIDevice(device_cols[1]):
                                vdpau = device_cols[2] if len(device_cols) == 3 else None
                                self.devices[pci_device] = NvidiaGPU(pci_device=pci_device,
                                                                     marketing_name=device_cols[0],
                                                                     vdpau=vdpau)
                        except ValueError as e:  # pragma: nocover
                            print(f"WARNING: Failed to parse the Nvidia device: {device_cols}: {e}")
                    else:  # pragma: nocover
                        print(f"WARNING: Unexpected amount of fields for the Nvidia device: {device_cols}")

                    # Reset the state
                    device_cols = []
                    in_table_row = False
                elif m := col_re.match(line):
                    device_cols.append(m.group(1))
