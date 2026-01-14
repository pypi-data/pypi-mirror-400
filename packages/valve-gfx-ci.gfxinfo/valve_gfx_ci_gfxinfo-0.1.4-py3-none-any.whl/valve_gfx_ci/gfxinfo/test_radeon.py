import unittest

from gfxinfo import PCIDevice

from .radeon import RadeonGPU, RadeonGpuDeviceDB


class RadeonTests(unittest.TestCase):
    def setUp(self):
        self.pci_device = PCIDevice(vendor_id=0x1002, product_id=0x71C0, revision=0)
        self.gpu = RadeonGPU(pci_device=self.pci_device, codename="RV530",
                             is_mobility=False, is_IGP=False)

    def test_pciid(self):
        assert self.gpu.pciid == str(self.pci_device)

    def test_some_devices(self):
        self.assertEqual(self.gpu.codename, "RV530")
        self.assertEqual(self.gpu.architecture, "R500")
        self.assertEqual(self.gpu.gfx_version, 2)
        self.assertEqual(self.gpu.base_name, "gfx2-rv530")
        self.assertFalse(self.gpu.is_mobility)
        self.assertFalse(self.gpu.is_IGP)
        self.assertEqual(self.gpu.unknown_fields, set())
        self.assertEqual(self.gpu.tags, {'radeon:generation:2', 'radeon:codename:RV530',
                                         'radeon:architecture:R500', 'radeon:discrete',
                                         'radeon:pciid:0x1002:0x71c0:0x0'})
        self.assertEqual(self.gpu.structured_tags, {
            'codename': 'RV530',
            'architecture': 'R500',
            'generation': 2,
            'integrated': False,
            'pciid': '0x1002:0x71c0:0x0',
            'type': 'radeon'
        })

        sumo = RadeonGPU(pci_device=self.pci_device, codename="SUMO", is_IGP=True, is_mobility=False)
        self.assertEqual(sumo.codename, "SUMO")
        self.assertEqual(sumo.architecture, "Evergreen")
        self.assertTrue(sumo.is_IGP)
        self.assertFalse(sumo.is_mobility)
        self.assertEqual(sumo.unknown_fields, set())
        self.assertEqual(sumo.tags, {'radeon:generation:4', 'radeon:codename:SUMO',
                                     'radeon:architecture:Evergreen', 'radeon:integrated',
                                     'radeon:pciid:0x1002:0x71c0:0x0'})
        self.assertEqual(sumo.structured_tags, {
            'codename': 'SUMO',
            'architecture': "Evergreen",
            'generation': 4,
            'integrated': True,
            'pciid': '0x1002:0x71c0:0x0',
            'type': 'radeon'
        })
        self.assertEqual(str(sumo), "<RadeonGPU: PCIID 0x1002:0x71c0:0x0 - SUMO - Evergreen - gfx4>")

        r100 = RadeonGPU(pci_device=self.pci_device, codename="KAVERI", is_IGP=False, is_mobility=True)
        self.assertEqual(r100.codename, "KAVERI")
        self.assertEqual(r100.architecture, "SeaIslands")
        self.assertFalse(r100.is_IGP)
        self.assertTrue(r100.is_mobility)
        self.assertEqual(r100.unknown_fields, set())
        self.assertEqual(r100.tags, {'radeon:generation:7', 'radeon:codename:KAVERI',
                                     'radeon:architecture:SeaIslands', 'radeon:integrated',
                                     'radeon:pciid:0x1002:0x71c0:0x0'})
        self.assertEqual(r100.structured_tags, {
            'codename': 'KAVERI',
            'architecture': "SeaIslands",
            'generation': 7,
            'integrated': True,
            'pciid': '0x1002:0x71c0:0x0',
            'type': 'radeon'
        })
        self.assertEqual(str(r100), "<RadeonGPU: PCIID 0x1002:0x71c0:0x0 - KAVERI - SeaIslands - gfx7>")

        # Future GPU
        pci_device = PCIDevice(vendor_id=0x1002, product_id=0xffff, revision=0)
        unk_gpu = RadeonGPU(pci_device=pci_device, codename="GOODE", is_IGP=False, is_mobility=False)
        self.assertEqual(unk_gpu.base_name, "gfxnone-goode")
        self.assertEqual(unk_gpu.tags, {'radeon:codename:GOODE', 'radeon:architecture:None',
                                        'radeon:generation:None', 'radeon:pciid:0x1002:0xffff:0x0',
                                        'radeon:discrete'})
        self.assertEqual(unk_gpu.structured_tags, {
            'architecture': None,
            'codename': "GOODE",
            'generation': None,
            'integrated': False,
            'pciid': '0x1002:0xffff:0x0',
            'type': 'radeon',
        })
        self.assertEqual(str(unk_gpu), "<RadeonGPU: PCIID 0x1002:0xffff:0x0 - GOODE - None - gfxNone>")
        self.assertEqual(unk_gpu.unknown_fields, {'architecture', 'gfx_version'})


class RadeonGpuDeviceDBTests(unittest.TestCase):
    def test_db_name(self):
        self.assertEqual(RadeonGpuDeviceDB().db_name, "RadeonGpuDeviceDB")

    def test_cache_db(self):
        self.assertIsNotNone(RadeonGpuDeviceDB().cache_db())

    def test_update(self):
        self.assertTrue(RadeonGpuDeviceDB().update())

    def test_check_db(self):
        self.assertTrue(RadeonGpuDeviceDB().check_db())

    def test_from_pciid(self):
        pci_device = PCIDevice(vendor_id=0x1002, product_id=0x71C0, revision=0)
        dev = RadeonGpuDeviceDB().from_pciid(pci_device)

        self.assertEqual(dev.codename, "RV530")

        # Make sure that in the presence of an unknown revision, we only use the vendor_id/product_id
        pci_device2 = PCIDevice(vendor_id=0x1002, product_id=0x71C0, revision=42)
        self.assertEqual(dev, RadeonGpuDeviceDB().from_pciid(pci_device2))
