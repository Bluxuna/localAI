# systemInfo.py
from abc import ABC, abstractmethod
from typing import Dict
from chooseAI.models.cpu import CPUInfo
from chooseAI.models.gpu import GPUInfo
from chooseAI.models.ram import RAMInfo
from chooseAI.models.storage import StorageInfo


class SystemInformation(ABC):
    @abstractmethod
    def get_cpu(self) -> CPUInfo:
        pass

    @abstractmethod
    def get_ram(self) -> RAMInfo:
        pass

    @abstractmethod
    def get_gpu(self) -> GPUInfo:
        pass

    @abstractmethod
    def get_storage(self) -> StorageInfo:
        pass

    def get_system_info(self) -> Dict:
        return {
            "cpu": self.get_cpu(),
            "gpu": self.get_gpu(),
            "ram": self.get_ram(),
            "storage": self.get_storage()
        }