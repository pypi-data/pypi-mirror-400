import ctypes
import fcntl
import os

IOC_WRITE = 1
IOC_READ = 2

IOC_DIR_SHIFT = 30
IOC_SIZE_SHIFT = 16
IOC_TYPE_SHIFT = 8
IOC_NR_SHIFT = 0


def _IOC(dir, type, nr, size):
    return dir << IOC_DIR_SHIFT | size << IOC_SIZE_SHIFT | type << IOC_TYPE_SHIFT | nr << IOC_NR_SHIFT


def _IOWR(type, nr, size):
    return _IOC(IOC_READ | IOC_WRITE, type, nr, size)


IOCTL_BASE = ord('d')


def IOWR(nr, type):
    return _IOWR(IOCTL_BASE, nr, ctypes.sizeof(type))


class version(ctypes.Structure):
    _fields_ = [
        ('version_major', ctypes.c_int),
        ('version_minor', ctypes.c_int),
        ('version_patchlevel', ctypes.c_int),
        ('name_len', ctypes.c_ulong),
        ('name', ctypes.c_char_p),
        ('date_len', ctypes.c_ulong),
        ('date', ctypes.c_char_p),
        ('desc_len', ctypes.c_ulong),
        ('desc', ctypes.c_char_p)
    ]


IOCTL_VERSION = IOWR(0x00, version)


class DrmDevice:
    def __init__(self, path):
        self.fd = os.open(path, os.O_RDWR)
        self.path = path
        self.driver = self._driver()

    def __str__(self):
        return self.driver

    def close(self):
        os.close(self.fd)

    def ioctl(self, nr, args):
        return fcntl.ioctl(self.fd, nr, args)

    def _driver(self):
        v = version()

        self.ioctl(IOCTL_VERSION, v)

        name = bytes(v.name_len)
        date = bytes(v.date_len)
        desc = bytes(v.desc_len)

        v.name = ctypes.c_char_p(name)
        v.date = ctypes.c_char_p(date)
        v.desc = ctypes.c_char_p(desc)

        self.ioctl(IOCTL_VERSION, v)

        return v.name.decode('ascii')
