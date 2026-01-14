import copy
import sys
import os

import requests
from requests.adapters import HTTPAdapter, Retry

from .pcidevice import PCIDevice


class GpuDevice:
    @property
    def base_name(self):  # pragma: nocover
        raise NotImplementedError('Missing required property')

    @property
    def tags(self):  # pragma: nocover
        raise NotImplementedError('Missing required property')

    @property
    def structured_tags(self):  # pragma: nocover
        raise NotImplementedError('Missing required property')

    def __str__(self):  # pragma: nocover
        raise NotImplementedError('Missing required property')

    @property
    def pciid(self):
        if hasattr(self, "pci_device") and self.pci_device:
            return str(self.pci_device)

    @property
    def unknown_fields(self):
        return set()

    def unbind(self):
        if hasattr(self, "pci_device") and self.pci_device:
            return self.pci_device.unbind()

        # TODO: Add support for all the other types of GPUs

        raise NotImplementedError('The GPU device cannot be unbound')

    def bind(self, module: str):
        if hasattr(self, "pci_device") and self.pci_device:
            return self.pci_device.bind(module)

        # TODO: Add support for all the other types of GPUs

        raise NotImplementedError('The GPU device cannot be bound')


class GpuDeviceDB:
    # Inherit from this class, and set DB_URL/DB_FILENAME as class parameters, or
    # override db_url()/db_filename()

    @classmethod
    def db_url(cls):
        return getattr(cls, 'DB_URL', None)

    @classmethod
    def db_filename(cls):
        return getattr(cls, 'DB_FILENAME', None)

    def __init__(self):
        self.is_up_to_date = False
        self.has_db = False

        # TODO: make self.devices a dictionary of lists so that we could have more
        # than one gpu with the same identifier
        self.devices = dict()

        if self._needs_db_file():
            try:
                db = open(self.db_cache_path, 'r').read()
            except FileNotFoundError:
                db = self.cache_db()
                if not db:
                    print(f"--> Most {self.db_name} GPUs won't be detected...")
                    db = ""

            if db:
                self.has_db = True
                self.parse_db(db)

        # Add all the static devices
        self.devices.update(self.static_devices)

    @property
    def static_devices(self):  # pragma: nocover
        return {}

    @classmethod
    def _needs_db_file(cls):
        return cls.db_filename() is not None

    @property
    def db_name(self):
        return self.__class__.__name__

    @property
    def __db_cache_folder(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "dbs")

    @property
    def db_cache_path(self):
        return os.path.join(self.__db_cache_folder, self.db_filename())

    @classmethod
    def _http_session(cls):
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    @classmethod
    def _http_get(cls, url):
        # Make the NVIDIA/fd.o servers happy by pretending to be cURL
        headers = {
            "User-Agent": "curl/8.15.0",
        }

        r = cls._http_session().get(url, headers=headers, timeout=30)
        r.raise_for_status()

        return r

    def cache_db(self):
        if not self._needs_db_file():  # pragma: nocover
            # Nothing to do
            return

        try:
            r = self._http_get(self.db_url())
        except Exception as e:
            print(f"ERROR: failed to download {self.db_url()}: {e}", file=sys.stderr)
            return

        # Save the DB, for future use
        try:
            os.makedirs(self.__db_cache_folder, exist_ok=True)
            open(self.db_cache_path, "w").write(r.text)
        except Exception as e:  # pragma: nocover
            print(f"WARNING: could not cache the database file {self.DB_FILENAME}: {e}")

        return r.text

    def update(self):
        if not self._needs_db_file():  # pragma: nocover
            # Nothing to do
            return False

        if not self.is_up_to_date:
            if db := self.cache_db():
                self.parse_db(db)
                self.has_db = True
                self.is_up_to_date = True

        return self.is_up_to_date

    def check_db(self):
        if not self._needs_db_file():
            return True

        if not self.has_db:
            print(f"ERROR: {self.db_name}'s GPU database is missing", file=sys.stderr)
            return False

        all_devices_complete = True
        for dev in self.devices.values():
            unknown_fields = dev.unknown_fields
            if len(unknown_fields) > 0:
                print(f"WARNING: The {self.db_name} device {dev.pci_device} ({dev.base_name}) has the following "
                      f"unknown fields: {unknown_fields}", file=sys.stderr)
                all_devices_complete = False

        # Ignore failures if asked to skip the DB completeness tests
        # NOTE: We still run the tests to keep the code coverage to 100%
        if 'GFXINFO_SKIP_DB_COMPLETENESS_CHECK' in os.environ:  # pragma: nocover
            print(f"NOTE: The {self.db_name} completeness test was skipped, as asked")
            return True
        else:  # pragma: nocover
            return all_devices_complete

    def from_pciid(self, pci_device):
        def find_gpu(pci_device):
            if d := self.devices.get(pci_device):
                return d

            # We did not find a device with the exact PCIID, let's drop the subsystem IDs and try again
            pci_device = PCIDevice(vendor_id=pci_device.vendor_id, product_id=pci_device.product_id,
                                   revision=pci_device.revision)
            if d := self.devices.get(pci_device):
                return d

            # We did not find a device with the exact PCIID, let's drop the revision and try again
            pci_device = PCIDevice(vendor_id=pci_device.vendor_id, product_id=pci_device.product_id,
                                   revision=0)
            if d := self.devices.get(pci_device):
                return d

        if gpu := find_gpu(pci_device):
            gpu = copy.deepcopy(gpu)
            gpu.pci_device.bus_addr = pci_device.bus_addr
            return gpu

    def from_driver_name(self, drm_device):  # pragma: nocover
        return None

    def parse_db(self):  # pragma: nocover
        raise NotImplementedError()
