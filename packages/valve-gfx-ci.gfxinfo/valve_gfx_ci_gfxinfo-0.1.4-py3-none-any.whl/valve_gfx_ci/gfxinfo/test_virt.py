import unittest

from gfxinfo import PCIDevice

from .virt import VirtGPU


class VirtGPUTests(unittest.TestCase):
    def setUp(self):
        self.pci_device = PCIDevice(vendor_id=0x1af4, product_id=0x1050, revision=0)
        self.gpu = VirtGPU(pci_device=self.pci_device)

    def test_some_devices(self):
        self.assertEqual(self.gpu.base_name, "virtio")
        self.assertEqual(self.gpu.codename, "VIRTIO")
        self.assertEqual(self.gpu.tags, {'virtio:codename:VIRTIO', 'virtio:family:VIRTIO',
                                         'virtio:pciid:0x1af4:0x1050:0x0'})
        self.assertEqual(self.gpu.structured_tags, {
            'architecture': 'VIRTIO',
            'codename': 'VIRTIO',
            'generation': 1,
            'integrated': True,
            'marketing_name': "VirtIO",
            'pciid': '0x1af4:0x1050:0x0',
            'type': 'virtio'
        })
        self.assertEqual(str(self.gpu), "<VirtGPU: PCIID 0x1af4:0x1050:0x0>")
