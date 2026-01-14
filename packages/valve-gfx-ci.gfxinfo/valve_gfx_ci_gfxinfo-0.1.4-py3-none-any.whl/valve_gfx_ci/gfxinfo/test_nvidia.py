from unittest.mock import patch, MagicMock
from urllib.parse import urlparse

import unittest

from gfxinfo import PCIDevice

from .nvidia import NvidiaGPU, NvidiaGpuDeviceDB


class NvidiaGPUTests(unittest.TestCase):
    def setUp(self):
        self.pci_device = PCIDevice(vendor_id=0x10de, product_id=0x2704, revision=0)
        self.rtx_4080 = NvidiaGPU(pci_device=self.pci_device, marketing_name="NVIDIA GeForce RTX 4080",
                                  vdpau="K")

    def test_db_url(self):
        # Check that failing to get the latest driver version reverts to a known existing version
        with patch('gfxinfo.gpudb.GpuDeviceDB._http_session') as session_mock:
            session_mock().get = MagicMock(side_effect=ValueError())

            # Make sure it is a valid URL
            url = urlparse(NvidiaGpuDeviceDB.db_url())

            # Make sure the url does not contain `//` which would indicate a missing version
            self.assertNotIn("//", url.path)

        # Check that we can actually get a valid URL
        url = urlparse(NvidiaGpuDeviceDB.db_url())
        self.assertNotIn("//", url.path)

    def test_raw_codenames(self):
        # RTX 4080
        self.assertEqual(self.rtx_4080.base_name, "ada-ad103")
        self.assertEqual(self.rtx_4080.codename, "AD103")
        self.assertEqual(self.rtx_4080.tags, {'nvidia:codename:AD103', 'nvidia:architecture:Ada',
                                              'nvidia:pciid:0x10de:0x2704:0x0', 'nvidia:discrete'})
        self.assertEqual(self.rtx_4080.structured_tags, {
            'architecture': 'Ada',
            'codename': 'AD103',
            'integrated': False,
            'marketing_name': "NVIDIA GeForce RTX 4080",
            'pciid': '0x10de:0x2704:0x0',
            'type': 'nvidia',
            'vdpau_features': 'K'
        })
        self.assertEqual(str(self.rtx_4080), "<NVIDIA: PCIID 0x10de:0x2704:0x0 - AD103 - Ada>")
        self.assertEqual(self.rtx_4080.unknown_fields, set())

        # Integrated GPU
        pci_device = PCIDevice(vendor_id=0x10de, product_id=0x7e0, revision=0)
        mcp73 = NvidiaGPU(pci_device=pci_device, marketing_name="GeForce 7150 / nForce 630i")
        self.assertEqual(mcp73.base_name, "curie-mcp73")
        self.assertEqual(mcp73.codename, "MCP73")
        self.assertEqual(mcp73.tags, {'nvidia:codename:MCP73', 'nvidia:architecture:Curie',
                                      'nvidia:pciid:0x10de:0x7e0:0x0', 'nvidia:integrated'})
        self.assertEqual(mcp73.structured_tags, {
            'architecture': "Curie",
            'codename': "MCP73",
            'integrated': True,
            'marketing_name': "GeForce 7150 / nForce 630i",
            'pciid': '0x10de:0x7e0:0x0',
            'type': 'nvidia',
            'vdpau_features': None
        })
        self.assertEqual(str(mcp73), "<NVIDIA: PCIID 0x10de:0x7e0:0x0 - MCP73 - Curie>")
        self.assertEqual(mcp73.unknown_fields, set())

        # Future GPU
        pci_device = PCIDevice(vendor_id=0x10de, product_id=0xffff, revision=0)
        unk_gpu = NvidiaGPU(pci_device=pci_device, marketing_name="NVIDIA GeForce RTX 9999", vdpau="Z")
        self.assertEqual(unk_gpu.base_name, "nv-unk")
        self.assertEqual(unk_gpu.codename, None)
        self.assertEqual(unk_gpu.tags, {'nvidia:codename:None', 'nvidia:architecture:None',
                                        'nvidia:pciid:0x10de:0xffff:0x0', 'nvidia:discrete'})
        self.assertEqual(unk_gpu.structured_tags, {
            'architecture': None,
            'codename': None,
            'integrated': None,
            'marketing_name': "NVIDIA GeForce RTX 9999",
            'pciid': '0x10de:0xffff:0x0',
            'type': 'nvidia',
            'vdpau_features': 'Z'
        })
        self.assertEqual(str(unk_gpu), "<NVIDIA: PCIID 0x10de:0xffff:0x0 - None - None>")
        self.assertEqual(unk_gpu.unknown_fields, {'architecture', 'codename'})


class TestNvidiaGpuDeviceDB(unittest.TestCase):
    def test_db_name(self):
        self.assertEqual(NvidiaGpuDeviceDB().db_name, "NvidiaGpuDeviceDB")

    def test_check_db(self):
        self.assertTrue(NvidiaGpuDeviceDB().check_db())

    def test_from_pciid(self):
        pci_device = PCIDevice(vendor_id=0x10de, product_id=0x2191, revision=0)
        dev = NvidiaGpuDeviceDB().from_pciid(pci_device)
        self.assertEqual(dev.pci_device, pci_device)
        self.assertEqual(dev.codename, "TU116")
        self.assertEqual(dev.marketing_name, "NVIDIA GeForce GTX 1660 Ti")

        # Make sure that in the presence of an unknown subsys, we revert to just vendor/product/rev
        pci_device2 = PCIDevice(vendor_id=0x10de, product_id=0x2191, revision=0,
                                subsys_vendor_id=0xdead, subsys_product_id=0xbeef)
        self.assertEqual(dev, NvidiaGpuDeviceDB().from_pciid(pci_device2))

        # Make sure that the marketing name is indeed updated when we use a correct subsys id
        pci_device3 = PCIDevice(vendor_id=0x10de, product_id=0x2191, revision=0,
                                subsys_vendor_id=0x1028, subsys_product_id=0x949)
        dev = NvidiaGpuDeviceDB().from_pciid(pci_device3)
        self.assertEqual(dev.codename, "TU116")
        self.assertEqual(dev.marketing_name, "NVIDIA GeForce GTX 1660 Ti with Max-Q Design")
