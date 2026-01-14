from dataclasses import dataclass

from . import PCIDevice
from .gpudb import GpuDevice, GpuDeviceDB


@dataclass
class VirtGPU(GpuDevice):
    pci_device: PCIDevice

    @property
    def codename(self):
        return 'VIRTIO'

    @property
    def base_name(self):
        return self.codename.lower()

    @property
    def tags(self):
        return {
            f"virtio:pciid:{self.pciid}",
            f"virtio:family:{self.codename}",
            f"virtio:codename:{self.codename}",
        }

    @property
    def structured_tags(self):
        return {
            "type": "virtio",
            "pciid": self.pciid,
            "codename": self.codename,
            "architecture": self.codename,
            "generation": 1,
            "marketing_name": "VirtIO",
            "integrated": True,
        }

    def __str__(self):
        return f"<VirtGPU: PCIID {self.pciid}>"


class VirtIOGpuDeviceDB(GpuDeviceDB):
    @property
    def static_devices(self):
        pci_device = PCIDevice(vendor_id=0x1af4, product_id=0x1050, revision=0)
        return {pci_device: VirtGPU(pci_device=pci_device)}
