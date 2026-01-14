from dataclasses import dataclass

from .drmdevice import DrmDevice, IOWR
from .gpudb import GpuDevice, GpuDeviceDB

import ctypes


class drm_etnaviv_param(ctypes.Structure):
    _fields_ = [
        ('pipe', ctypes.c_uint32),
        ('param', ctypes.c_uint32),
        ('value', ctypes.c_uint64),
    ]


IOCTL_ETNAVIV_GET_PARAM = IOWR(0x40 + 0x0, drm_etnaviv_param)


@dataclass
class VivanteGPU(GpuDevice):
    drm_device: DrmDevice = None
    model: str = None
    revision: str = None

    @property
    def unknown_fields(self):
        # This is not applicable for Vivante GPUs.
        return set()

    @property
    def codename(self):
        return f"gc{self.model}-r{self.revision}".lower()

    @property
    def base_name(self):
        return f"vivante-{self.codename}"

    @property
    def pci_device(self):
        # FIXME: Unhardcode None when PCI-based GPUs become supported by etnaviv
        return None

    @property
    def tags(self):
        tags = set()

        tags.add("vivante:integrated")
        tags.add(f"vivante:model:{self.model}")
        tags.add(f"vivante:revision:{self.revision}")

        return tags

    @property
    def structured_tags(self):
        tags = {
            "type": "vivante",
        }

        tags["integrated"] = True
        tags["model"] = self.model
        tags["revision"] = self.revision

        return tags

    def __str__(self):
        if self.drm_device:
            dev = self.drm_device.path
            return (f"<VivanteGPU: {dev} - {self.codename}>")
        else:
            return (f"<VivanteGPU: {self.codename}>")


class VivanteGpuDeviceDB(GpuDeviceDB):
    def from_driver_name(self, drm_device):
        if drm_device.driver != "etnaviv":  # pragma: nocover
            return None

        args = drm_etnaviv_param()

        # TODO: no multi-pipe support yet - only 3D pipe
        args.pipe = 0

        args.param = 0x01
        drm_device.ioctl(IOCTL_ETNAVIV_GET_PARAM, args)
        model = '{:X}'.format(args.value)

        args.param = 0x02
        drm_device.ioctl(IOCTL_ETNAVIV_GET_PARAM, args)
        revision = '{:X}'.format(args.value)

        return VivanteGPU(drm_device=drm_device, model=model, revision=revision)
