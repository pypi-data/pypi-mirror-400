from unittest.mock import MagicMock

import unittest

from gfxinfo import SUPPORTED_GPU_DBS

from .gpudb import GpuDevice


class DatabaseTests(unittest.TestCase):
    def test_check_db(self):
        for gpu_db in SUPPORTED_GPU_DBS:
            with self.subTest(GPU_DB=type(gpu_db).__name__):
                self.assertTrue(gpu_db.check_db())


class GpuDeviceTests(unittest.TestCase):
    def test_unbind(self):
        dev = GpuDevice()

        with self.assertRaisesRegex(NotImplementedError, "The GPU device cannot be unbound"):
            dev.unbind()

        dev.pci_device = MagicMock()
        dev.unbind()
        dev.pci_device.unbind.assert_called_once_with()

    def test_bind(self):
        dev = GpuDevice()

        with self.assertRaisesRegex(NotImplementedError, "The GPU device cannot be bound"):
            dev.bind("amdgpu")

        dev.pci_device = MagicMock()
        dev.bind("amdgpu")
        dev.pci_device.bind.assert_called_once_with("amdgpu")
