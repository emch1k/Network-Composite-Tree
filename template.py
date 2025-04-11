from abc import ABC, abstractmethod
from typing import List
from io import StringIO

# Абстрактный базовый класс — все объекты должны уметь печататься и клонироваться
class Printable(ABC):
    @abstractmethod
    def print_me(self, os, prefix="", is_last=False):
        pass

    @abstractmethod
    def clone(self):
        pass

    def __str__(self):
        buf = StringIO()
        self.print_me(buf, is_last=True)
        return buf.getvalue().strip()

# Базовый класс для коллекций (списков) с возможностью добавления и поиска
class BasicCollection(Printable):
    def __init__(self):
        self.items = []

    def add(self, elem):
        self.items.append(elem)
        return self

    def find(self, elem):
        for item in self.items:
            if item == elem:
                return item
        return None

    def clone(self):
        new_collection = self.__class__()
        new_collection.items = [item.clone() for item in self.items]
        return new_collection

    def print_me(self, os, prefix="", is_last=False):
        for i, item in enumerate(self.items):
            item.print_me(os, prefix, i == len(self.items) - 1)

# Абстрактный базовый класс для компонентов компьютера
class Component(Printable, ABC):
    def __init__(self, numeric_val=0):
        self.numeric_val = numeric_val

# IP-адрес
class Address(Printable):
    def __init__(self, addr):
        self.address = addr

    def print_me(self, os, prefix="", is_last=False):
        connector = "\\-" if is_last else "+-"
        os.write(f"{prefix}{connector}{self.address}\n")

    def clone(self):
        return Address(self.address)

# Класс раздела диска
class Partition(Printable):
    def __init__(self, size, name):
        self.size = size
        self.name = name

    def print_me(self, os, prefix="", is_last=False):
        connector = "\\-" if is_last else "+-"
        os.write(f"{prefix}{connector}[{self.name}]: {self.size} GiB\n")

    def clone(self):
        return Partition(self.size, self.name)

# Жесткий диск (HDD или SSD) с разделами
class Disk(Component):
    SSD = 0
    MAGNETIC = 1

    def __init__(self, storage_type, size):
        super().__init__(size)
        self.storage_type = storage_type
        self.partitions = []

    def add_partition(self, size, name):
        self.partitions.append((size, name))
        return self

    def print_me(self, os, prefix="", is_last=False):
        type_str = "SSD" if self.storage_type == Disk.SSD else "HDD"
        connector = "\\-" if is_last else "+-"
        os.write(f"{prefix}{connector}{type_str}, {self.numeric_val} GiB\n")
        for i, (size, name) in enumerate(self.partitions):
            last = i == len(self.partitions) - 1
            new_prefix = prefix + ("  " if is_last else "| ")
            sub_connector = "\\-" if last else "+-"
            os.write(f"{new_prefix}{sub_connector}[{i}]: {size} GiB, {name}\n")

    def clone(self):
        new_disk = Disk(self.storage_type, self.numeric_val)
        for part in self.partitions:
            new_disk.add_partition(*part)
        return new_disk

# Процессор (CPU)
class CPU(Component):
    def __init__(self, cores, mhz):
        super().__init__(mhz)
        self.cores = cores

    def print_me(self, os, prefix="", is_last=False):
        connector = "\\-" if is_last else "+-"
        os.write(f"{prefix}{connector}CPU, {self.cores} cores @ {self.numeric_val}MHz\n")

    def clone(self):
        return CPU(self.cores, self.numeric_val)

# Оперативная память
class Memory(Component):
    def __init__(self, size):
        super().__init__(size)

    def print_me(self, os, prefix="", is_last=False):
        connector = "\\-" if is_last else "+-"
        os.write(f"{prefix}{connector}Memory, {self.numeric_val} MiB\n")

    def clone(self):
        return Memory(self.numeric_val)

# Компьютер: содержит адреса и компоненты
class Computer(Printable):
    def __init__(self, name):
        self.name = name
        self.addresses: List[Address] = []
        self.components: List[Component] = []

    def add_address(self, addr):
        if isinstance(addr, str):
            addr = Address(addr)
        self.addresses.append(addr)
        return self

    def add_component(self, comp):
        self.components.append(comp)
        return self

    def print_me(self, os, prefix="", is_last=False):
        connector = "\\-" if is_last else "+-"
        os.write(f"{prefix}{connector}Host: {self.name}\n")
        new_prefix = prefix + ("  " if is_last else "| ")
        items = self.addresses + self.components
        for i, item in enumerate(items):
            item.print_me(os, new_prefix, i == len(items) - 1)

    def clone(self):
        new_comp = Computer(self.name)
        new_comp.addresses = [addr.clone() for addr in self.addresses]
        new_comp.components = [comp.clone() for comp in self.components]
        return new_comp

# Сеть: содержит список компьютеров, умеет искать, копироваться и выводиться
class Network(Printable):
    def __init__(self, name):
        self.name = name
        self.computers: List[Computer] = []

    def add_computer(self, comp):
        self.computers.append(comp)
        return self

    def find_computer(self, name):
        for comp in self.computers:
            if comp.name == name:
                return comp
        return None

    def print_me(self, os, prefix="", is_last=False):
        os.write(f"Network: {self.name}\n")
        for i, comp in enumerate(self.computers):
            comp.print_me(os, "", i == len(self.computers) - 1)

    def clone(self):
        new_net = Network(self.name)
        new_net.computers = [comp.clone() for comp in self.computers]
        return new_net

# 🧪 Пример использования и тестирования
def main():
    # Создаем сеть MISIS
    n = Network("MISIS network")

    # Первый компьютер с адресом, CPU и памятью
    n.add_computer(
        Computer("server1.misis.ru")
        .add_address("192.168.1.1")
        .add_component(CPU(4, 2500))
        .add_component(Memory(16000))
    )

    # Второй компьютер с адресом, CPU и диском с разделами
    n.add_computer(
        Computer("server2.misis.ru")
        .add_address("10.0.0.1")
        .add_component(CPU(8, 3200))
        .add_component(
            Disk(Disk.MAGNETIC, 2000)
            .add_partition(500, "system")
            .add_partition(1500, "data")
        )
    )

    # Выводим иерархию
    print("=== Сеть MISIS ===")
    print(n)

if __name__ == "__main__":
    main()
