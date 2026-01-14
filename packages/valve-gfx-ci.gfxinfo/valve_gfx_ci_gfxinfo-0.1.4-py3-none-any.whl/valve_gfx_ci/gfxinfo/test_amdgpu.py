from unittest.mock import patch, MagicMock

import unittest
import os

from gfxinfo import PCIDevice

from .amdgpu import AMDGPU, AmdGpuDeviceDB


class AMDGPUTests(unittest.TestCase):
    def setUp(self):
        self.pci_device = PCIDevice(vendor_id=0x1002, product_id=0x163F, revision=0xAE)
        self.gpu = AMDGPU(pci_device=self.pci_device, asic_type="GFX10_3_3",
                          is_APU=True, marketing_name="AMD Custom GPU 0405 / Steam Deck")

    def test_pciid(self):
        assert self.gpu.pciid == str(self.pci_device)

    def test_some_devices(self):
        self.assertEqual(self.gpu.codename, "VANGOGH")
        self.assertIsNone(self.gpu.family)
        self.assertEqual(self.gpu.architecture, "RDNA2")
        self.assertEqual(self.gpu.base_name, "gfx10-vangogh")
        self.assertTrue(self.gpu.is_APU)
        self.assertEqual(self.gpu.unknown_fields, set())
        self.assertEqual(self.gpu.tags, {'amdgpu:generation:10', 'amdgpu:architecture:RDNA2',
                                         'amdgpu:codename:VANGOGH', 'amdgpu:pciid:0x1002:0x163f:0xae',
                                         'amdgpu:integrated'})
        self.assertEqual(self.gpu.structured_tags, {
            'APU': True,
            'architecture': 'RDNA2',
            'codename': 'VANGOGH',
            'family': None,
            'generation': 10,
            'gfxversion': 'gfx10',
            'integrated': True,
            'marketing_name': "AMD Custom GPU 0405 / Steam Deck",
            'pciid': '0x1002:0x163f:0xae',
            'type': 'amdgpu'
        })

        renoir = AMDGPU(pci_device=self.pci_device, asic_type="GFX9_0_C", is_APU=True, marketing_name="Marketing name")
        self.assertEqual(renoir.codename, "RENOIR")
        self.assertEqual(renoir.family, "AI")
        self.assertEqual(renoir.architecture, "GCN5.1")
        self.assertEqual(renoir.base_name, "gfx9-renoir")
        self.assertTrue(renoir.is_APU)
        self.assertEqual(renoir.unknown_fields, set())
        self.assertEqual(renoir.tags, {'amdgpu:generation:9', 'amdgpu:architecture:GCN5.1',
                                       'amdgpu:codename:RENOIR', 'amdgpu:pciid:0x1002:0x163f:0xae',
                                       'amdgpu:integrated', 'amdgpu:family:AI'})
        self.assertEqual(renoir.structured_tags, {
            'APU': True,
            'architecture': 'GCN5.1',
            'codename': 'RENOIR',
            'family': "AI",
            'generation': 9,
            'gfxversion': 'gfx9',
            'integrated': True,
            'marketing_name': 'Marketing name',
            'pciid': '0x1002:0x163f:0xae',
            'type': 'amdgpu'
        })
        self.assertEqual(str(renoir), "<AMDGPU: PCIID 0x1002:0x163f:0xae - RENOIR - AI - GCN5.1 - gfx9>")

        navi31 = AMDGPU(pci_device=self.pci_device, asic_type="GFX11_0_0", is_APU=False,
                        marketing_name="AMD Radeon RX 7900 XTX")
        self.assertEqual(navi31.codename, "NAVI31")
        self.assertEqual(navi31.family, None)
        self.assertEqual(navi31.architecture, "RDNA3")
        self.assertEqual(navi31.base_name, "gfx11-navi31")
        self.assertFalse(navi31.is_APU)
        self.assertEqual(navi31.unknown_fields, set())
        self.assertEqual(navi31.tags, {'amdgpu:generation:11', 'amdgpu:architecture:RDNA3',
                                       'amdgpu:codename:NAVI31', 'amdgpu:discrete',
                                       'amdgpu:pciid:0x1002:0x163f:0xae'})
        self.assertEqual(navi31.structured_tags, {
            'APU': False,
            'architecture': 'RDNA3',
            'codename': 'NAVI31',
            'generation': 11,
            'gfxversion': 'gfx11',
            'integrated': False,
            'marketing_name': 'AMD Radeon RX 7900 XTX',
            'pciid': '0x1002:0x163f:0xae',
            'type': 'amdgpu',
            'family': None,
        })
        self.assertEqual(str(navi31), "<AMDGPU: PCIID 0x1002:0x163f:0xae - NAVI31 - None - RDNA3 - gfx11>")


class AmdGpuDeviceDBTests(unittest.TestCase):
    @patch('builtins.open')
    def test_db_missing(self, open_mock):
        def side_effect(*args, **kwargs):
            if len(args) > 0:
                file = args[0]
            else:  # pragma: nocover
                file = kwargs['file']
            if file == '/proc/cpuinfo':
                mock_cpuinfo = MagicMock()
                mock_cpuinfo.readlines = lambda: ['model name : foo bar']
                return mock_cpuinfo
            raise FileNotFoundError
        open_mock.side_effect = side_effect

        # DB missing, but download works
        db = AmdGpuDeviceDB()
        self.assertGreater(len(db.devices), 1)
        self.assertTrue(db.check_db())

        # DB missing, and URL failed
        with patch('gfxinfo.gpudb.GpuDeviceDB._http_session') as session_mock:
            session_mock().get = MagicMock(side_effect=ValueError())
            db = AmdGpuDeviceDB()
            self.assertGreater(len(db.devices), 0)
            self.assertFalse(db.check_db())

    def test_update(self):
        db = AmdGpuDeviceDB()
        db.cache_db = MagicMock()

        # Check that the DB is marked as not up to date by default
        self.assertFalse(db.is_up_to_date)

        # Check that calling update() calls cache_db() and marks the DB as up to date
        self.assertTrue(db.update())
        db.cache_db.assert_called_once_with()
        self.assertTrue(db.is_up_to_date)

        # Check that further update() calls don't lead to more calls to cache_db()
        self.assertTrue(db.update())
        db.cache_db.assert_called_once_with()

    def test_check_db(self):
        db = AmdGpuDeviceDB()

        # Check that the DB is complete by default
        self.assertTrue(db.check_db())

        # Add an incomplete GPU, if we did not disable the completeness check
        pci_device = PCIDevice(vendor_id=0x1002, product_id=0x0001, revision=0x42)
        db.devices[pci_device] = AMDGPU(pci_device=pci_device, asic_type="GFX10_3_42",
                                        is_APU=True, marketing_name="GPU with non-existant architecture")
        ret = db.check_db()
        if 'GFXINFO_SKIP_DB_COMPLETENESS_CHECK' not in os.environ:  # pragma: nocover
            # NOTE: Ignore the check when the DB completeness checks are disabled, as it would otherwise return True
            self.assertFalse(ret)

    def test_db_name(self):
        self.assertEqual(AmdGpuDeviceDB().db_name, "AmdGpuDeviceDB")
