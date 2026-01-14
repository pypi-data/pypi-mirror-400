from dataclasses import dataclass
from pathlib import Path


@dataclass
class PCIDevice:
    vendor_id: int
    product_id: int
    revision: int

    subsys_vendor_id: int = 0
    subsys_product_id: int = 0

    bus_addr: str = None

    def sysfs_path(self):
        if not self.bus_addr:
            raise ValueError("The bus address is not set")
        return Path("/sys/bus/pci/devices") / self.bus_addr

    def unbind_path(self):
        if not self.bus_addr:
            raise ValueError("The bus address is not set")
        return self.sysfs_path() / "driver" / "unbind"

    def unbind(self):
        if not self.unbind_path().is_file():
            driver_path = self.unbind_path().parent
            pci_dev_path = driver_path.parent

            if pci_dev_path.is_dir() and not driver_path.is_dir():
                # The pci device is not bound, so nothing to do!
                return
            elif not pci_dev_path.is_dir():
                raise ValueError(f"The PCI device at '{pci_dev_path}' does not exist")
            else:
                raise ValueError(f"The unbind path '{self.unbind_path()}' does not exist")

        self.unbind_path().write_text(f"{self.bus_addr}\n")

    def bind_path(self, module: str):
        if not self.bus_addr:
            raise ValueError("The bus address is not set")
        return Path("/sys/bus/pci/drivers") / module / "bind"

    def bind(self, module: str):
        bind_path = self.bind_path(module)
        if not bind_path.is_file():
            driver_path = bind_path.parent
            if not driver_path.is_dir():
                raise ValueError(f"The driver '{module}' is not currently loaded")
            else:
                raise ValueError(f"The bind path '{bind_path}' does not exist")

        bind_path.write_text(f"{self.bus_addr}\n")

    def __hash__(self):
        return hash((self.vendor_id, self.product_id, self.revision, self.subsys_vendor_id, self.subsys_product_id))

    def __str__(self):
        s = f"{hex(self.vendor_id)}:{hex(self.product_id)}:{hex(self.revision)}"
        if self.subsys_vendor_id > 0 or self.subsys_product_id > 0:
            s += f":{hex(self.subsys_vendor_id)}:{hex(self.subsys_product_id)}"
        return s

    @classmethod
    def from_str(cls, pciid):
        fields = pciid.split(":")
        if len(fields) not in [2, 3, 5]:
            raise ValueError("The pciid '{pciid}' is invalid. Format: xxxx:xxxx[:xx] or xxxx:xxxx:xx:xxxx:xxxx]")

        revision = 0 if len(fields) < 3 else int(fields[2], 16)
        subsys_vendor_id = 0 if len(fields) < 5 else int(fields[3], 16)
        subsys_product_id = 0 if len(fields) < 5 else int(fields[4], 16)

        return cls(vendor_id=int(fields[0], 16),
                   product_id=int(fields[1], 16),
                   revision=revision,
                   subsys_vendor_id=subsys_vendor_id,
                   subsys_product_id=subsys_product_id)
