import unittest

from gfxinfo import PCIDevice

from .intel import IntelGPU, IntelGpuDeviceDB


class IntelGpuTests(unittest.TestCase):
    def test_raw_codenames(self):
        pci_device = PCIDevice(vendor_id=0x1002, product_id=0x0001, revision=0x42)

        unsupported_format = IntelGPU(pci_device=pci_device, raw_codename="_IDONTEXIST")
        self.assertEqual(unsupported_format.short_architecture, "_IDONTEXIST")
        self.assertIsNone(unsupported_format.variant)
        self.assertIsNone(unsupported_format.gt)
        self.assertIsNone(unsupported_format.human_name)
        self.assertTrue(unsupported_format.is_integrated)
        self.assertEqual(unsupported_format.unknown_fields, {"gen_version", "architecture"})
        self.assertEqual(unsupported_format.base_name, 'intel-unk-_idontexist')
        self.assertEqual(unsupported_format.tags, {'intelgpu:pciid:0x1002:0x1:0x42',
                                                   'intelgpu:raw_codename:_IDONTEXIST'})
        self.assertEqual(unsupported_format.structured_tags, {'pciid': '0x1002:0x1:0x42', 'raw_codename': '_IDONTEXIST',
                                                              'type': 'intelgpu'})

        ats_m75 = IntelGPU(pci_device=pci_device, raw_codename="ATS_M75")
        self.assertEqual(ats_m75.short_architecture, "ATS")
        self.assertEqual(ats_m75.variant, "M75")
        self.assertIsNone(ats_m75.gt)
        self.assertEqual(ats_m75.human_name, "Arctic Sound M75")
        self.assertEqual(ats_m75.architecture, "ARCTICSOUND")
        self.assertFalse(ats_m75.is_integrated)
        self.assertEqual(ats_m75.base_name, 'intel-gen12-ats-m75')
        self.assertEqual(ats_m75.tags, {'intelgpu:pciid:0x1002:0x1:0x42', 'intelgpu:gen:12',
                                        'intelgpu:codename:ATS-M75', 'intelgpu:discrete',
                                        'intelgpu:architecture:ARCTICSOUND'})

        adlp = IntelGPU(pci_device=pci_device, raw_codename="ADLP")
        self.assertEqual(adlp.short_architecture, "ADL")
        self.assertEqual(adlp.variant, "P")
        self.assertIsNone(adlp.gt)
        self.assertEqual(adlp.human_name, "Alder Lake P")
        self.assertEqual(adlp.architecture, "ALDERLAKE")
        self.assertTrue(adlp.is_integrated)
        self.assertEqual(adlp.base_name, 'intel-gen12-adl-p')
        self.assertEqual(adlp.structured_tags, {'architecture': 'ALDERLAKE', 'codename': 'ADL-P', 'generation': 12,
                                                'integrated': True, 'marketing_name': 'Alder Lake P',
                                                'pciid': '0x1002:0x1:0x42', 'type': 'intelgpu'})

        whl_u_gt2 = IntelGPU(pci_device=pci_device, raw_codename="WHL_U_GT2")
        self.assertEqual(whl_u_gt2.short_architecture, "WHL")
        self.assertEqual(whl_u_gt2.variant, "U")
        self.assertEqual(whl_u_gt2.gt, 2)
        self.assertEqual(whl_u_gt2.human_name, "Whisky Lake U GT2")
        self.assertEqual(whl_u_gt2.architecture, "WHISKYLAKE")
        self.assertTrue(whl_u_gt2.is_integrated)
        self.assertEqual(whl_u_gt2.base_name, 'intel-gen9-whl-u-gt2')
        self.assertEqual(str(whl_u_gt2), "<IntelGPU: PCIID 0x1002:0x1:0x42 - gen9 - Whisky Lake U GT2>")

        bdw_gt1 = IntelGPU(pci_device=pci_device, raw_codename="BDW_GT1")
        self.assertEqual(bdw_gt1.short_architecture, "BDW")
        self.assertIsNone(bdw_gt1.variant)
        self.assertEqual(bdw_gt1.gt, 1)
        self.assertEqual(bdw_gt1.human_name, "Broadwell GT1")
        self.assertEqual(bdw_gt1.architecture, "BROADWELL")
        self.assertTrue(bdw_gt1.is_integrated)
        self.assertEqual(bdw_gt1.base_name, 'intel-gen8-bdw-gt1')
        self.assertEqual(bdw_gt1.tags, {'intelgpu:pciid:0x1002:0x1:0x42', 'intelgpu:gen:8',
                                        'intelgpu:codename:BDW-GT1', 'intelgpu:integrated',
                                        'intelgpu:architecture:BROADWELL', 'intelgpu:GT:1'})

        vlv = IntelGPU(pci_device=pci_device, raw_codename="VLV")
        self.assertEqual(vlv.short_architecture, "VLV")
        self.assertIsNone(vlv.variant)
        self.assertIsNone(vlv.gt)
        self.assertEqual(vlv.human_name, "Valley View")
        self.assertEqual(vlv.architecture, "VALLEYVIEW")
        self.assertTrue(vlv.is_integrated)
        self.assertEqual(vlv.base_name, 'intel-gen7-vlv')
        self.assertEqual(str(vlv), "<IntelGPU: PCIID 0x1002:0x1:0x42 - gen7 - Valley View>")


class IntelGpuDeviceDBTests(unittest.TestCase):
    def test_db_name(self):
        self.assertEqual(IntelGpuDeviceDB().db_name, "IntelGpuDeviceDB")

    def test_cache_db(self):
        self.assertIsNotNone(IntelGpuDeviceDB().cache_db())

    def test_update(self):
        self.assertTrue(IntelGpuDeviceDB().update())

    def test_check_db(self):
        self.assertTrue(IntelGpuDeviceDB().check_db())

    def test_from_pciid(self):
        pci_device = PCIDevice(vendor_id=0x8086, product_id=0x3e9b, revision=0)
        dev = IntelGpuDeviceDB().from_pciid(pci_device)

        self.assertEqual(dev.codename, "CFL-H-GT2")

        # Make sure that in the presence of an unknown revision, we only use the vendor_id/product_id
        pci_device2 = PCIDevice(vendor_id=0x8086, product_id=0x3e9b, revision=42)
        self.assertEqual(dev, IntelGpuDeviceDB().from_pciid(pci_device2))
