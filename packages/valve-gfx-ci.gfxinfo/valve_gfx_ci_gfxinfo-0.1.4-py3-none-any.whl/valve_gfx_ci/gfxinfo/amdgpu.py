from dataclasses import dataclass
import re

from . import PCIDevice
from .gpudb import GpuDevice, GpuDeviceDB


def host_cpu_name():
    for line in open("/proc/cpuinfo").readlines():
        fields = line.split(":")
        if fields[0].strip() == "model name":
            return fields[1].strip()

    return None  # pragma: nocover


@dataclass
class AMDGPU(GpuDevice):
    pci_device: PCIDevice
    asic_type: str
    is_APU: bool
    marketing_name: str

    @property
    def has_bad_marketing_name(self):
        return self.marketing_name in [
            "AMD Radeon(TM) Graphics",
            f"{hex(self.pci_device.product_id)}:f{hex(self.pci_device.revision)}".upper()
        ]

    @property
    def unknown_fields(self):
        missing = set()

        if self.architecture is None:
            missing.add("architecture")
        if self.gfx_version is None:
            missing.add("gfx_version")

        return missing

    def __post_init__(self):
        # Fixup any bad APU marketing name, if possible
        # BUG: we shouldn't replace all the bad names with the host's CPU name
        # as we may be trying to get information about another GPU than the one
        # found in the current machine.
        if self.is_APU and self.has_bad_marketing_name:
            if cpu_name := host_cpu_name():
                self.marketing_name = cpu_name

    @property
    def codename(self):
        codenames = {
            # Reference:
            # * https://www.techpowerup.com/
            # * https://gitlab.freedesktop.org/agd5f/linux/-/blob/amd-staging-drm-next/Documentation/gpu/amdgpu/dgpu-asic-info-table.csv  # noqa: E501
            # * https://gitlab.freedesktop.org/agd5f/linux/-/blob/amd-staging-drm-next/Documentation/gpu/amdgpu/apu-asic-info-table.csv   # noqa: E501

            # For backwards compatibility with the amdgpu naming
            "TAHITI_XT": "TAHITI",
            "TAHITI_PRO": "TAHITI",
            "CAPEVERDE_XT": "VERDE",
            "CAPEVERDE_PRO": "VERDE",
            "SPECTRE_LITE": "KAVERI",
            "SPECTRE": "KAVERI",
            "SPECTRE_SL": "KAVERI",
            "SPOOKY": "KAVERI",
            "KALINDI": "KABINI",
            "PITCAIRN_XT": "PITCAIRN",
            "PITCAIRN_PRO": "PITCAIRN",
            "ICELAND": "TOPAZ",
            "CARRIZO_EMB": "CARRIZO",
            "VEGAM1": "VEGAM",
            "VEGAM2": "VEGAM",

            # POLARIS
            "ELLESMERE": "POLARIS10",
            "BAFFIN": "POLARIS11",
            "GFX8_0_4": "POLARIS12",

            # VEGA
            "GFX9_0_0": "VEGA10",
            "GFX9_0_2": "RAVEN",
            "GFX9_0_4": "VEGA12",
            "GFX9_0_6": "VEGA20",
            "GFX9_0_A": "ALDEBARAN",
            "GFX9_0_C": "RENOIR",
            "GFX9_4_2": "AQUAVANJARAM",

            # NAVI1X
            "GFX10_1_0": "NAVI10",
            "GFX10_1_0_XL": "NAVI10",
            "GFX10_1_1": "NAVI12",
            "GFX10_1_2": "NAVI14",
            "GFX10_1_2": "NAVI14",
            "GFX10_1_2_X": "NAVI14",
            "GFX10_1_2_XT": "NAVI14",

            # NAVI2X
            "GFX10_3_0": "NAVI21",
            "GFX10_3_0_XT": "NAVI21",
            "GFX10_3_0_XTX": "NAVI21",
            "GFX10_3_1": "NAVI22",
            "GFX10_3_2": "NAVI23",
            "GFX10_3_2_XT": "NAVI23",
            "GFX10_3_3": "VANGOGH",
            "GFX10_3_4": "NAVI24",
            "GFX10_3_5": "REMBRANDT",
            "GFX10_3_6": "RAPHAEL",

            # NAVI3X
            "GFX11_0_0": "NAVI31",
            "GFX11_0_0_XT": "NAVI31",
            "GFX11_0_0_GRE": "NAVI31",
            "GFX11_0_0_M": "NAVI31",
            "GFX11_0_1": "NAVI32",
            "GFX11_0_1_XT": "NAVI32",
            "GFX11_0_2": "NAVI33",
            "GFX11_0_2_XT": "NAVI33",
            "GFX11_0_3": "PHOENIX1",
            "GFX11_0_3A": "PHOENIX1",
            "GFX11_0_3B": "PHOENIX2",
            "GFX11_5_0": "STRIXPOINT1",
            "GFX11_5_1": "STRIXHALO",
            "GFX11_5_2": "KRAKANPOINT",
            # Cut down variant (https://www.notebookcheck.net/AMD-Radeon-820M-Benchmarks-and-Specs.1059782.0.html)?
            "GFX11_5_3": "KRAKANPOINT",
            "GFX11_5_3A": "KRAKANPOINT",

            # NAVI4X
            "GFX12_0_0": "NAVI44",
            "GFX12_0_0_XT": "NAVI44",
            "GFX12_0_1": "NAVI48",
            "GFX12_0_1_XT": "NAVI48",
            "GFX12_0_1_GRE": "NAVI48",
        }

        return codenames.get(self.asic_type, self.asic_type)

    @property
    def family(self):
        families = {
            # Reference: https://gitlab.freedesktop.org/mesa/mesa/-/blob/main/src/amd/common/amd_family.h

            # SI
            "TAHITI": "SI",
            "PITCAIRN": "SI",
            "VERDE": "SI",
            "OLAND": "SI",
            "HAINAN": "SI",

            # CIK
            "BONAIRE": "CIK",
            "KAVERI": "CIK",
            "KABINI": "CIK",
            "HAWAII": "CIK",

            # VI
            "TONGA": "VI",
            "TOPAZ": "VI",
            "CARRIZO": "VI",
            "FIJI": "VI",
            "STONEY": "VI",
            "POLARIS10": "VI",
            "POLARIS11": "VI",
            "POLARIS12": "VI",
            "VEGAM": "VI",

            # AI
            "VEGA10": "AI",
            "VEGA12": "AI",
            "VEGA20": "AI",
            "ARCTURUS": "AI",
            "RAVEN": "AI",
            "RENOIR": "AI",
        }

        return families.get(self.codename)

    @property
    def architecture(self):
        architectures = {
            # GCN1
            "TAHITI": "GCN1",
            "PITCAIRN": "GCN1",
            "VERDE": "GCN1",
            "OLAND": "GCN1",
            "HAINAN": "GCN1",

            # GCN2
            "KAVERI": "GCN2",
            "BONAIRE": "GCN2",
            "HAWAII": "GCN2",
            "KABINI": "GCN2",
            "MULLINS": "GCN2",

            # GCN3
            "TOPAZ": "GCN3",
            "TONGA": "GCN3",
            "FIJI": "GCN3",
            "CARRIZO": "GCN3",
            "STONEY": "GCN3",

            # GCN4
            "POLARIS10": "GCN4",
            "POLARIS11": "GCN4",
            "POLARIS12": "GCN4",
            "VEGAM": "GCN4",

            # GCN5
            "VEGA10": "GCN5",
            "VEGA12": "GCN5",
            "RAVEN": "GCN5",

            # GCN5.1
            "VEGA20": "GCN5.1",
            "RENOIR": "GCN5.1",

            # CDNA
            "ARCTURUS": "CDNA",

            # CDNA2
            "ALDEBARAN": "CDNA2",

            # CDNA3
            "AQUAVANJARAM": "CDNA3",

            # Navi / RDNA1
            "NAVI10": "RDNA1",
            "NAVI12": "RDNA1",
            "NAVI14": "RDNA1",
            "CYAN_SKILLFISH": "RDNA1",

            # RDNA2
            "NAVI21": "RDNA2",
            "NAVI22": "RDNA2",
            "NAVI23": "RDNA2",
            "NAVI24": "RDNA2",
            "VANGOGH": "RDNA2",
            "REMBRANDT": "RDNA2",
            "RAPHAEL": "RDNA2",

            # RDNA3
            "NAVI31": "RDNA3",
            "NAVI32": "RDNA3",
            "NAVI33": "RDNA3",
            "PHOENIX1": "RDNA3",
            "PHOENIX2": "RDNA3",
            "STRIXPOINT1": "RDNA3",
            "STRIXHALO": "RDNA3",
            "KRAKANPOINT": "RDNA3",

            # RDNA4
            "NAVI44": "RDNA4",
            "NAVI48": "RDNA4",
        }

        return architectures.get(self.codename)

    @property
    def base_name(self):
        return f"gfx{self.gfx_version}-{self.codename}".lower()

    @property
    def gfx_version(self):
        versions = {
            # GFX7
            "GCN1": 6,

            # GFX7
            "GCN2": 7,

            # GFX8
            "GCN3": 8,
            "GCN4": 8,

            # GFX9
            "GCN5": 9,
            "GCN5.1": 9,
            "CDNA": 9,
            "CDNA2": 9,
            "CDNA3": 9,

            # GFX10
            "RDNA1": 10,
            "RDNA2": 10,

            # GFX11
            "RDNA3": 11,

            # GFX12
            "RDNA4": 12
        }

        return versions.get(self.architecture)

    @property
    def tags(self):
        tags = set()

        tags.add(f"amdgpu:pciid:{self.pciid}")
        tags.add(f"amdgpu:codename:{self.codename}")
        tags.add(f"amdgpu:architecture:{self.architecture}")
        tags.add(f"amdgpu:generation:{self.gfx_version}")
        tags.add(f"amdgpu:{'integrated' if self.is_APU else 'discrete'}")
        if self.family:
            tags.add(f"amdgpu:family:{self.family}")

        return tags

    @property
    def structured_tags(self):
        return {
            # Common fields between all GPUs
            "type": "amdgpu",
            "pciid": self.pciid,
            "codename": self.codename,
            "architecture": self.architecture,
            "generation": self.gfx_version,
            "marketing_name": self.marketing_name,
            "integrated": self.is_APU,

            # AMDGPU-specific fields
            "family": self.family,
            "gfxversion": f"gfx{self.gfx_version}",  # NOTE: deprecated, use `generation`
            "APU": self.is_APU,                      # NOTE: deprecated, use `integrated`
        }

    def __str__(self):
        return (f"<AMDGPU: PCIID {self.pciid} - {self.codename} - {self.family} - "
                f"{self.architecture} - gfx{self.gfx_version}>")


class AmdGpuDeviceDB(GpuDeviceDB):
    DB_URL = "https://raw.githubusercontent.com/GPUOpen-Tools/device_info/master/DeviceInfo.cpp"
    DB_FILENAME = "DeviceInfo.cpp"

    @property
    def static_devices(self):
        def add_device(product_id: int, revision: int, asic_type: str, is_APU: bool, marketing_name: str):
            pci_device = PCIDevice(vendor_id=0x1002, product_id=product_id, revision=revision)
            devices[pci_device] = AMDGPU(pci_device=pci_device, asic_type=asic_type,
                                         is_APU=is_APU, marketing_name=marketing_name)

        devices = {}
        add_device(product_id=0x163F, revision=0xAE, asic_type="GFX10_3_3",
                   is_APU=True, marketing_name="AMD Custom GPU 0405 / Steam Deck")
        add_device(product_id=0x164E, revision=0xC9, asic_type="GFX10_3_6",
                   is_APU=True, marketing_name=None)
        return devices

    def parse_db(self, db):
        self.devices = dict()

        # Expected format:
        # {GDT_GFX10_3_5, 0x164D, 0x00, GDT_HW_GENERATION_GFX103, true, "gfx1035", "AMD Radeon(TM) Graphics"},
        comp_re = re.compile(r"^\s*{\s*GDT_(?P<asic_type>[^,]+),\s*(?P<device_id>0x[\da-fA-F]+),"
                             r"\s*(?P<rev_id>0x[\da-fA-F]+),\s*(?P<generation>.+),\s*(?P<is_APU>true|false),"
                             r"\s*\"(?P<CAL_name>.*)\",\s*\"(?P<marketing_name>.*)\"},\s*$")

        started = False
        for line in db.splitlines():
            if not started:
                if line == "GDT_GfxCardInfo gs_cardInfo[] = {":
                    started = True
                    continue
            else:
                if line == "};":
                    break

                if m := comp_re.match(line):
                    try:
                        dev = m.groupdict()
                        pci_device = PCIDevice(vendor_id=0x1002, product_id=int(dev["device_id"], 16),
                                               revision=int(dev["rev_id"], 16))
                        self.devices[pci_device] = AMDGPU(pci_device=pci_device,
                                                          asic_type=dev["asic_type"],
                                                          is_APU=dev["is_APU"] == "true",
                                                          marketing_name=dev["marketing_name"])
                    except ValueError as e:  # pragma: nocover
                        print(f"WARNING: Failed to parse the AMDGPU line '{line}', got '{dev}' with exception: {e}")
                        continue
