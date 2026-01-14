import contextlib
import io
import unittest

from gfxinfo import DeviceTreeGPU


class DeviceTreeGPUTests(unittest.TestCase):
    def setUp(self):
        self.gpu = DeviceTreeGPU.from_compatible_str("brcm,bcm2711-vc5\0brcm,bcm2835-vc4\0")
        self.known_gpu = DeviceTreeGPU.from_compatible_str("qcom,adreno-43050a01\0qcom,adreno\0")
        self.imageon_gpu = DeviceTreeGPU.from_compatible_str("amd,imageon-200.0\0amd,imageon\0")

    def test_codename(self):
        self.assertIsNone(self.gpu.codename)
        self.assertEqual(self.known_gpu.codename, "a740")
        self.assertEqual(self.imageon_gpu.codename, "a200")

    def test_base_name(self):
        self.assertEqual(self.gpu.base_name, "brcm-bcm2711-vc5")
        self.assertEqual(self.known_gpu.base_name, "qcom-a740")
        self.assertEqual(self.imageon_gpu.base_name, "qcom-a200")

    def test_pciid(self):
        self.assertIsNone(self.gpu.pciid)
        self.assertIsNone(self.known_gpu.pciid)
        self.assertIsNone(self.imageon_gpu.pciid)

    def test_pci_device(self):
        self.assertIsNone(self.gpu.pci_device)
        self.assertIsNone(self.known_gpu.pci_device)
        self.assertIsNone(self.imageon_gpu.pci_device)

    def test_tags(self):
        self.assertEqual(self.gpu.tags, {"dt_gpu:vendor:brcm", "dt_gpu:model:bcm2711-vc5"})
        self.assertEqual(self.known_gpu.tags, {"dt_gpu:vendor:qcom", "dt_gpu:model:adreno-43050a01",
                                               "dt_gpu:codename:a740"})
        self.assertEqual(self.imageon_gpu.tags, {"dt_gpu:vendor:qcom", "dt_gpu:model:adreno-200.0",
                                                 "dt_gpu:codename:a200"})

    def test_structured_tags(self):
        self.assertEqual(self.gpu.structured_tags,
                         {"type": "devicetree",
                          "vendor": "brcm",
                          "model": "bcm2711-vc5"})

        self.assertEqual(self.known_gpu.structured_tags,
                         {"type": "devicetree",
                          "vendor": "qcom",
                          "model": "adreno-43050a01",
                          "codename": "a740"})

        self.assertEqual(self.imageon_gpu.structured_tags,
                         {"type": "devicetree",
                          "vendor": "qcom",
                          "model": "adreno-200.0",
                          "codename": "a200"})

    def test_str(self):
        self.assertEqual(str(self.gpu), "<DeviceTreeGPU: brcm/bcm2711-vc5>")
        self.assertEqual(str(self.known_gpu), "<DeviceTreeGPU: qcom/a740>")
        self.assertEqual(str(self.imageon_gpu), "<DeviceTreeGPU: qcom/a200>")

    def test_from_compatible_str(self):
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            self.assertIsNone(DeviceTreeGPU.from_compatible_str("brcm,bcm2711-vc5,extra"))

        self.assertEqual(f.getvalue(), ("ERROR: The compatible 'brcm,bcm2711-vc5,extra' is not "
                                        "following the expected format 'vendor,model'\n"))

    def test_imageon_mangle(self):
        self.assertEqual(DeviceTreeGPU.from_compatible_str("amd,imageon-200.0"),
                         DeviceTreeGPU.from_compatible_str("qcom,adreno-200.0"))

        self.assertEqual(DeviceTreeGPU.from_compatible_str("amd,imageon-200.1"),
                         DeviceTreeGPU.from_compatible_str("qcom,adreno-200.1"))

    def test_unknown_fields(self):
        self.assertEqual(self.gpu.unknown_fields, set())
