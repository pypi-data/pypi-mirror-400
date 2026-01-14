from dataclasses import dataclass
from functools import cached_property
import re

from . import PCIDevice
from .gpudb import GpuDevice, GpuDeviceDB


@dataclass
class IntelGPU(GpuDevice):
    pci_device: PCIDevice
    raw_codename: str

    @cached_property
    def decoded_raw_codename(self):
        if m := re.match(r'(?P<short_architecture>[^_]+)(_(?P<variant>D|M\d*|ULX|ULT|U|S|H|G\d+|XT))?(_GT(?P<gt>\d))?',
                         self.raw_codename):
            d = m.groupdict()

            # Replaces ADL_P with ADL and P power class
            if d['short_architecture'][-1] in ['P', 'S', 'N', 'U'] and d['short_architecture'] not in ['ATS']:
                d['variant'] = d['short_architecture'][-1]
                d['short_architecture'] = d['short_architecture'][0:-1]

            d['short_architecture'] = {
                'PINEVIEW': 'PNV',
                'IRONLAKE': 'ILK',
            }.get(d['short_architecture'], d['short_architecture'])

            if d['gt']:
                d['gt'] = int(d['gt'])

            return d
        else:
            return {
                "short_architecture": self.raw_codename,
                "variant": None,
                "gt": None
            }

    @property
    def short_architecture(self):
        return self.decoded_raw_codename.get('short_architecture')

    @property
    def variant(self):
        return self.decoded_raw_codename.get('variant')

    @property
    def gt(self):
        return self.decoded_raw_codename.get('gt')

    # TODO: This should maybe be called SoC name or something
    def __gen_architecture(self, human=False):
        architectures = {
            'I810': 'Whitney',
            'I815': 'Solano',
            'I830': 'Almador',
            'I835': 'I835',  # No idea what this GPU is
            'I845G': 'Brookdale',
            'I85X': 'Montara',
            'I865G': 'Springdale',
            'I915G': 'Grantsdale',
            'I915GM': 'Alviso',
            'I945G': 'Lakeport',
            'I945GM': 'Calistoga',
            'I965G': 'Broadwater',
            'G33': 'Bearlake',
            'I965GM': 'Crestline',
            'GM45': 'Cantiga',
            'G45': 'Eagle Lake',
            'PNV': 'Pine View',
            'ILK': 'Iron Lake',
            'SNB': 'Sandy Bridge',
            'IVB': 'Ivy Bridge',
            'HSW': 'Haswell',
            'VLV': 'Valley View',
            'BDW': 'Broadwell',
            'CHV': 'Cherry View',
            'SKL': 'Sky Lake',
            'BXT': 'Broxton',
            'KBL': 'Kaby Lake',
            'AML': 'Amber Lake',
            'CML': 'Comet Lake',
            'CFL': 'Coffee Lake',
            'GLK': 'Gemini Lake',
            'WHL': 'Whisky Lake',
            'CNL': 'Cannon Lake',
            'ICL': 'Ice Lake',
            'EHL': 'Elkhart Lake',
            'JSL': 'Jasper Lake',
            'TGL': 'Tiger Lake',
            'RKL': 'Rocket Lake',
            'DG1': 'DG1',
            'ADL': 'Alder Lake',
            'RPL': 'Raptor Lake',
            'DG2': 'Alchemist',
            'ATS': 'Arctic Sound',
            'ARL': 'Arrow Lake',
            'MTL': 'Meteor Lake',
            'PVC': 'Ponte Vecchio',
            'LNL': 'Lunar Lake',
            'BMG': 'Battlemage',
            'PTL': 'Panther Lake',
            'WCL': 'Wildcat Lake',
            'NVL': 'Nova Lake',
            'CRI': 'Crescent Island',
        }

        if arch := architectures.get(self.short_architecture):
            if not human:
                arch = arch.replace(' ', '').upper()
            return arch

    @property
    def architecture(self):
        return self.__gen_architecture(human=False)

    # TODO: Make gen_version only for gen1-11. Gen12+ should move to per-block (media, gfx, and display)
    # See https://elixir.bootlin.com/linux/latest/source/drivers/gpu/drm/i915/intel_device_info.c#L345
    @property
    def gen_version(self):
        versions = {
            'I810': 1,
            'I815': 1,
            'I830': 2,
            'I835': 2,
            'I845G': 2,
            'I85X': 2,
            'I865G': 2,
            'I915G': 3,
            'I915GM': 3,
            'I945G': 3,
            'I945GM': 3,
            'I965G': 4,
            'G33': 3,
            'I965GM': 4,
            'GM45': 4,
            'G45': 4,
            'PNV': 3,
            'ILK': 5,
            'SNB': 6,
            'IVB': 7,
            'HSW': 7,
            'VLV': 7,
            'BDW': 8,
            'CHV': 8,
            'SKL': 9,
            'BXT': 9,
            'KBL': 9,
            'AML': 9,
            'CML': 9,
            'CFL': 9,
            'GLK': 9,
            'WHL': 9,
            'CNL': 10,
            'ICL': 11,
            'EHL': 11,
            'JSL': 11,
            # TODO: Starting from gen12, this is not very applicable
            'TGL': 12,
            'RKL': 12,
            'DG1': 12,
            'ADL': 12,
            'RPL': 12,
            'DG2': 12,
            'ATS': 12,
            'ARL': 12,
            'MTL': 12,
            'PVC': 12,

            # Xe2
            'LNL': 20,
            'BMG': 20,

            # Xe3
            'PTL': 30,
            'WCL': 30,
            'NVL': 30,
            'CRI': 30
        }

        return versions.get(self.short_architecture, None)

    def __gen_codename(self, short=False, human=False):
        if self.is_complete:
            codename = self.short_architecture if short else self.__gen_architecture(human=human)
            separator = ' ' if human else '-'

            if self.variant:
                codename = f"{codename}{separator}{self.variant}"
            if self.gt:
                codename = f"{codename}{separator}GT{self.gt}"

            return codename

    @property
    def codename(self):
        return self.__gen_codename(short=True, human=False)

    @property
    def is_integrated(self):
        return self.short_architecture not in ['DG1', 'DG2', 'ATS', 'CRI']

    @property
    def unknown_fields(self):
        missing = set()

        if self.gen_version is None:
            missing.add("gen_version")
        if self.architecture is None:
            missing.add("architecture")

        return missing

    @property
    def is_complete(self):
        return len(self.unknown_fields) == 0

    @property
    def base_name(self):
        if self.is_complete:
            return f'intel-gen{self.gen_version}-{self.__gen_codename(short=True)}'.lower()
        else:
            return f'intel-unk-{self.raw_codename}'.lower()

    @property
    def human_name(self):
        return self.__gen_codename(short=False, human=True)

    @property
    def tags(self):
        if self.is_complete:
            tags = {
                f"intelgpu:pciid:{self.pciid}",
                f"intelgpu:codename:{self.codename}",
                f"intelgpu:architecture:{self.architecture}",
                f"intelgpu:gen:{self.gen_version}",
                f'intelgpu:{"integrated" if self.is_integrated else "discrete"}'
            }
            if self.gt:
                tags.add(f'intelgpu:GT:{self.gt}')
        else:
            tags = {
                f"intelgpu:pciid:{self.pciid}",
                f"intelgpu:raw_codename:{self.raw_codename}",
            }

        return tags

    @property
    def structured_tags(self):
        if self.is_complete:
            return {
                # Common fields between all GPUs
                "type": "intelgpu",
                "pciid": self.pciid,
                "codename": self.codename,
                "architecture": self.architecture,
                "generation": self.gen_version,
                "marketing_name": self.human_name,
                "integrated": self.is_integrated,
            }
        else:
            return {
                "type": "intelgpu",
                "pciid": self.pciid,
                "raw_codename": self.raw_codename,
            }

    def __str__(self):
        name = self.__gen_codename(short=False, human=True)
        return f"<IntelGPU: PCIID {self.pciid} - gen{self.gen_version} - {name}>"


class IntelGpuDeviceDB(GpuDeviceDB):
    DB_URL = "https://gitlab.freedesktop.org/drm/tip/-/raw/drm-tip/include/drm/intel/pciids.h"
    DB_FILENAME = "pciids.h"

    SECTION_START_RE = r'^#define INTEL_(?P<codename>.+)_IDS'
    PRODUCT_RE = r'^	MACRO__\(0x(?P<device_id>[A-Za-z0-9]+),'

    def parse_db(self, db):
        self.devices = dict()

        section_start_re = re.compile(self.SECTION_START_RE)
        product_re = re.compile(self.PRODUCT_RE)

        cur_codename_section = None
        for line in db.splitlines():
            if m := section_start_re.match(line):
                cur_codename_section = m.groupdict()['codename']
            elif m := product_re.match(line):
                try:
                    dev = m.groupdict()
                    pci_device = PCIDevice(vendor_id=0x8086, product_id=int(dev["device_id"], 16),
                                           revision=0)
                    self.devices[pci_device] = IntelGPU(pci_device=pci_device, raw_codename=cur_codename_section)
                except ValueError as e:  # pragma: nocover
                    db_name = self.DB_FILENAME
                    print(f"WARNING: Failed to parse the {db_name} line '{line}', got '{dev}' with exception: {e}")
