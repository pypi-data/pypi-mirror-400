from unittest.mock import MagicMock

import unittest

from gfxinfo import PCIDevice


class PCIDeviceTests(unittest.TestCase):
    def setUp(self):
        self.pcidev = PCIDevice(0x1234, 0x5678, 0x9a, bus_addr="0000:0d:00.4")

    def test_sysfs_path(self):
        self.assertEqual(str(self.pcidev.sysfs_path()),
                         "/sys/bus/pci/devices/0000:0d:00.4")

        with self.assertRaisesRegex(ValueError, "The bus address is not set"):
            PCIDevice(0x1234, 0x5678, 0x9a).sysfs_path()

    def test_unbind_path(self):
        self.assertEqual(str(self.pcidev.unbind_path()),
                         "/sys/bus/pci/devices/0000:0d:00.4/driver/unbind")

        with self.assertRaisesRegex(ValueError, "The bus address is not set"):
            PCIDevice(0x1234, 0x5678, 0x9a).unbind_path()

    def test_unbind(self):
        unbind_path_mock = MagicMock(is_file=MagicMock(return_value=False))
        unbind_path_mock.parent.is_dir.return_value = False
        unbind_path_mock.parent.parent.is_dir.return_value = False
        self.pcidev.unbind_path = MagicMock(return_value=unbind_path_mock)

        # Missing driver and parent folders: complain that the device isn't present
        with self.assertRaisesRegex(ValueError, r"The PCI device at '.*' does not exist"):
            self.pcidev.unbind()
        unbind_path_mock.write_text.assert_not_called()

        # Missing driver folder but parent exists: Do nothing!
        unbind_path_mock.parent.parent.is_dir.return_value = True
        self.pcidev.unbind()
        unbind_path_mock.write_text.assert_not_called()

        # Missing unbind file
        unbind_path_mock.parent.is_dir.return_value = True
        with self.assertRaisesRegex(ValueError, r"The unbind path '.*' does not exist"):
            self.pcidev.unbind()
        unbind_path_mock.write_text.assert_not_called()

        # Unbind with success
        unbind_path_mock.is_file.return_value = True
        self.pcidev.unbind()
        unbind_path_mock.write_text.assert_called_once_with(f"{self.pcidev.bus_addr}\n")

    def test_bind_path(self):
        self.assertEqual(str(self.pcidev.bind_path("amdgpu")),
                         "/sys/bus/pci/drivers/amdgpu/bind")

        with self.assertRaisesRegex(ValueError, "The bus address is not set"):
            PCIDevice(0x1234, 0x5678, 0x9a).bind_path("amdgpu")

    def test_bind(self):
        bind_path_mock = MagicMock(is_file=MagicMock(return_value=False))
        bind_path_mock.parent.is_dir.return_value = True
        self.pcidev.bind_path = MagicMock(return_value=bind_path_mock)

        # Missing bind file
        with self.assertRaisesRegex(ValueError, r"The bind path '.*' does not exist"):
            self.pcidev.bind("amdgpu")
        self.pcidev.bind_path.assert_called_with("amdgpu")
        bind_path_mock.write_text.assert_not_called()

        # Missing driver folder
        bind_path_mock.parent.is_dir.return_value = False
        with self.assertRaisesRegex(ValueError, "The driver 'nouveau' is not currently loaded"):
            self.pcidev.bind("nouveau")
        self.pcidev.bind_path.assert_called_with("nouveau")
        bind_path_mock.write_text.assert_not_called()

        # bind with success
        bind_path_mock.is_file.return_value = True
        self.pcidev.bind("i915")
        self.pcidev.bind_path.assert_called_with("i915")
        bind_path_mock.write_text.assert_called_once_with(f"{self.pcidev.bus_addr}\n")

    def test_hash(self):
        self.assertEqual(hash(PCIDevice(0x1234, 0x5678, 0x9a)),
                         hash((0x1234, 0x5678, 0x9a, 0, 0)))

        self.assertEqual(hash(PCIDevice(0x1234, 0x5678, 0x9a, 0xbcde, 0xf012)),
                         hash((0x1234, 0x5678, 0x9a, 0xbcde, 0xf012)))

    def test_str(self):
        self.assertEqual(str(PCIDevice(0x1234, 0x5678, 0x9a)), "0x1234:0x5678:0x9a")
        self.assertEqual(str(PCIDevice(0x1234, 0x5678, 0x9a, 0xbcde, 0xf012)),
                         "0x1234:0x5678:0x9a:0xbcde:0xf012")

    def test_from_str(self):
        self.assertEqual(PCIDevice.from_str("1234:5678:9a"), PCIDevice(0x1234, 0x5678, 0x9a))
        self.assertEqual(PCIDevice.from_str("0x1234:0x5678:0x9a"), PCIDevice(0x1234, 0x5678, 0x9a))

        self.assertEqual(PCIDevice.from_str("0x1234:5678"), PCIDevice(0x1234, 0x5678, 0x0))

        with self.assertRaises(ValueError):
            self.assertEqual(PCIDevice.from_str("0x1234:5678:0x12:045"), PCIDevice(0x1234, 0x5678, 0x0))
