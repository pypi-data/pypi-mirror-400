from unittest.mock import patch

import ctypes
import unittest
import os

from gfxinfo import DrmDevice

from .drmdevice import version
from .vivante import VivanteGPU, VivanteGpuDeviceDB, drm_etnaviv_param


class VivanteGPUTests(unittest.TestCase):
    def test_properties(self):
        gpu = VivanteGPU(None, "7000", "12345")

        self.assertEqual(gpu.unknown_fields, set())
        self.assertEqual(gpu.codename, "gc7000-r12345")
        self.assertEqual(gpu.base_name, "vivante-gc7000-r12345")
        self.assertIsNone(gpu.pci_device)

        self.assertEqual(gpu.tags, {
            'vivante:integrated',
            'vivante:revision:12345',
            'vivante:model:7000'
        })

        self.assertEqual(gpu.structured_tags, {
            'integrated': True,
            'model': '7000',
            'revision': '12345',
            'type': 'vivante',
        })

        self.assertEqual(str(gpu), '<VivanteGPU: gc7000-r12345>')


class VivanteGpuDeviceDBTests(unittest.TestCase):
    @patch('fcntl.ioctl')
    @patch('os.open')
    @patch('os.close')
    def test_from_driver_name(self, mock_close, mock_open, mock_ioctl):
        mock_open.return_value = 10

        def mock_ioctl_side_effect(fd, nr, v):
            if isinstance(v, version):
                v.name_len = 7
                v.date_len = 8
                v.desc_len = 6
                v.name = ctypes.c_char_p(b'etnaviv')
                v.date = ctypes.c_char_p(b'20230920')
                v.desc = ctypes.c_char_p(b'device')

                return 0  # Simulate a successful ioctl

            elif isinstance(v, drm_etnaviv_param):
                if v.param == 0x01:
                    v.value = 0x7000
                elif v.param == 0x02:
                    v.value = 0x12345

                return 0  # Simulate a successful ioctl

        mock_ioctl.side_effect = mock_ioctl_side_effect

        drm_device = DrmDevice('/dev/dri/renderD128')
        gpu = VivanteGpuDeviceDB().from_driver_name(drm_device)
        self.assertIsNotNone(gpu)

        drm_device.close()

        mock_open.assert_called_once_with('/dev/dri/renderD128', os.O_RDWR)
        mock_close.assert_called_once_with(10)
        self.assertEqual(drm_device.fd, 10)

        self.assertEqual(gpu.unknown_fields, set())
        self.assertEqual(gpu.codename, "gc7000-r12345")
        self.assertEqual(gpu.base_name, "vivante-gc7000-r12345")

        self.assertEqual(gpu.tags, {
            'vivante:integrated',
            'vivante:revision:12345',
            'vivante:model:7000'
        })

        self.assertEqual(gpu.structured_tags, {
            'integrated': True,
            'model': '7000',
            'revision': '12345',
            'type': 'vivante',
        })

        self.assertEqual(str(gpu), '<VivanteGPU: /dev/dri/renderD128 - gc7000-r12345>')
