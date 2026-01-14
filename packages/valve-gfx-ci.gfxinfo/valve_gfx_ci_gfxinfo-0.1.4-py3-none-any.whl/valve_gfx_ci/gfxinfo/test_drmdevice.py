from unittest.mock import patch

import ctypes
import unittest
import os

from gfxinfo import DrmDevice

from .drmdevice import version, IOCTL_VERSION


class DrmDeviceTests(unittest.TestCase):
    def test_non_exiting_device(self):
        """Test that opening a non-existing device raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            DrmDevice("/dev/dri/card0_non_existing")

    def test_non_drm_device(self):
        """Test that opening a non-DRM device raises an OSError."""
        with self.assertRaises(OSError):
            DrmDevice("/dev/null")

    @patch('fcntl.ioctl')
    @patch('os.open')
    @patch('os.close')
    def test_version(self, mock_close, mock_open, mock_ioctl):
        """Test that the device's version information is retrieved correctly."""
        # Mock open to return a file descriptor
        mock_open.return_value = 10  # Simulate fd 10 for /dev/dri/card0

        # Define the side effect for ioctl to simulate version struct behavior
        def mock_ioctl_side_effect(fd, nr, v):
            # Simulate populating version structure during first ioctl call
            if isinstance(v, version):
                v.name_len = 11
                v.date_len = 8
                v.desc_len = 6
                v.name = ctypes.c_char_p(b'driver_name')
                v.date = ctypes.c_char_p(b'20230920')
                v.desc = ctypes.c_char_p(b'device')
            return 0  # Simulate a successful ioctl

        mock_ioctl.side_effect = mock_ioctl_side_effect

        device = DrmDevice('/dev/dri/card0')
        self.assertEqual(str(device), 'driver_name')
        device.close()

        # Ensure the correct system calls were made
        mock_open.assert_called_once_with('/dev/dri/card0', os.O_RDWR)
        mock_ioctl.assert_called_with(10, IOCTL_VERSION, unittest.mock.ANY)
        mock_close.assert_called_once_with(10)
        self.assertEqual(device.fd, 10)
