import glob
import os
from pathlib import Path

from .pcidevice import PCIDevice
from .drmdevice import DrmDevice
from .amdgpu import AmdGpuDeviceDB
from .devicetree import DeviceTreeGPU
from .intel import IntelGpuDeviceDB
from .nvidia import NvidiaGpuDeviceDB
from .virt import VirtIOGpuDeviceDB
from .radeon import RadeonGpuDeviceDB
from .gfxinfo_vulkan import VulkanInfo
from .vivante import VivanteGpuDeviceDB
from .gpudb import GpuDevice


SUPPORTED_GPU_DBS = [AmdGpuDeviceDB(), IntelGpuDeviceDB(),
                     NvidiaGpuDeviceDB(), VirtIOGpuDeviceDB(), RadeonGpuDeviceDB(),
                     VivanteGpuDeviceDB()]


def pci_devices():
    def readfile(path, default=None):
        try:
            with open(path) as f:
                return f.read().strip()
        except Exception:
            return default

    pciids = []
    pci_dev_root = Path("/sys/bus/pci/devices/")
    if not pci_dev_root.exists():
        return pciids

    for pci_dev_path in pci_dev_root.iterdir():
        vendor = readfile(pci_dev_path / "vendor")
        device = readfile(pci_dev_path / "device")
        revision = readfile(pci_dev_path / "revision")
        subsystem_vendor = readfile(pci_dev_path / "subsystem_vendor", "0x0")
        subsystem_device = readfile(pci_dev_path / "subsystem_device", "0x0")

        if vendor and device and revision:
            pci_dev = PCIDevice(vendor_id=int(vendor, 16),
                                product_id=int(device, 16),
                                revision=int(revision, 16),
                                subsys_vendor_id=int(subsystem_vendor, 16),
                                subsys_product_id=int(subsystem_device, 16),
                                bus_addr=pci_dev_path.name)
            pciids.append(pci_dev)

    return pciids


def drm_devices():
    directory = os.path.join(os.path.sep, 'dev', 'dri')
    devices = []

    if not os.path.isdir(directory):
        return devices

    for name in os.listdir(directory):
        path = os.path.join(directory, name)

        if name.startswith('card'):
            try:
                device = DrmDevice(path)
                if device:
                    devices.append(device)
            except Exception as e:
                print(f"Failed to create DrmDevice for {path}: {e}")

    return devices


def __find_pci_gpus(allow_db_updates=True) -> list[GpuDevice]:
    def match_pciid(devices) -> list[GpuDevice]:
        gpus = list()
        for pci_device in devices:
            for gpu_db in SUPPORTED_GPU_DBS:
                if gpu := gpu_db.from_pciid(pci_device):
                    gpus.append(gpu)

                    # We've found a match for the driver, don't for for another match in a different DB
                    break
        return gpus

    devices = pci_devices()
    if gpus := match_pciid(devices):
        return gpus

    # We could not find the GPU in our databases, update them
    if allow_db_updates:
        for gpu_db in SUPPORTED_GPU_DBS:
            gpu_db.update()

        # Retry, now that we have updated our DBs
        if gpus := match_pciid(devices):
            return gpus


def __find_devicetree_gpu() -> GpuDevice:
    for path in glob.glob("/proc/device-tree/gpu*/compatible") + \
            glob.glob("/sys/bus/platform/devices/*gpu/of_node/compatible"):
        try:
            with open(path) as f:
                return DeviceTreeGPU.from_compatible_str(f.read())
        except OSError:
            pass


def __find_drm_node_gpu() -> GpuDevice:
    for drm_device in drm_devices():
        for gpu_db in SUPPORTED_GPU_DBS:
            if gpu := gpu_db.from_driver_name(drm_device):
                return gpu


def find_gpus(allow_db_updates=True) -> list[GpuDevice]:
    if gpus := __find_pci_gpus(allow_db_updates=allow_db_updates):
        return gpus
    elif gpu := __find_drm_node_gpu():
        return [gpu]
    elif gpu := __find_devicetree_gpu():
        return [gpu]
    else:
        return []


def find_gpu(allow_db_updates=True) -> GpuDevice:
    """ Pick the first gpu from the list of gpus, for backwards compatibility """
    if gpus := find_gpus(allow_db_updates=allow_db_updates):
        return gpus[0]
    else:
        return None


def cache_db():
    for gpu_db in SUPPORTED_GPU_DBS:
        gpu_db.cache_db()


def check_db():
    result = True
    for gpu_db in SUPPORTED_GPU_DBS:
        if not gpu_db.check_db():
            result = False
    return result


def find_gpu_from_pciid(pciid):
    for gpu_db in SUPPORTED_GPU_DBS:
        if gpu := gpu_db.from_pciid(pciid):
            return gpu

    # We could not find the GPU, retry with updated DBs
    for gpu_db in SUPPORTED_GPU_DBS:
        gpu_db.update()
        if gpu := gpu_db.from_pciid(pciid):
            return gpu


__all__ = ['pci_devices', 'find_gpu', 'cache_db', 'VulkanInfo']
