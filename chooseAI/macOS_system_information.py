# macOS_system_information.py
import platform
import psutil
import cpuinfo
import GPUtil
import shutil
import sys
from chooseAI.systemInfo import SystemInformation
from chooseAI.models.cpu import CPUInfo
from chooseAI.models.gpu import GPUInfo
from chooseAI.models.ram import RAMInfo
from chooseAI.models.storage import StorageInfo


class MacOSSystemInformation(SystemInformation):
    def get_cpu(self) -> CPUInfo:
        try:
            name = platform.processor() or cpuinfo.get_cpu_info().get("brand_raw", "Unknown")
            physical_cores = psutil.cpu_count(logical=False)
            logical_cores = psutil.cpu_count(logical=True)
            clock_speed_ghz = round(psutil.cpu_freq().max / 1000, 2) if psutil.cpu_freq() else 0.0

            return CPUInfo(
                name=name,
                physical_cores=physical_cores,
                logical_cores=logical_cores,
                clock_speed_ghz=clock_speed_ghz
            )
        except Exception as e:
            return CPUInfo(
                name="Unknown",
                physical_cores=0,
                logical_cores=0,
                clock_speed_ghz=0.0,
                error=f"Failed to retrieve CPU info: {str(e)}"
            )

    def get_gpu(self) -> GPUInfo:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return GPUInfo(
                    name=gpu.name,
                    vram_gb=round(gpu.memoryTotal / 1024, 2)
                )
            else:
                # Fallback for Apple Silicon or integrated GPUs
                gpu_name = "Apple Integrated GPU" if "arm" in platform.machine() else "No GPU detected"
                return GPUInfo(
                    name=gpu_name,
                    vram_gb=0.0
                )
        except Exception as e:
            return GPUInfo(
                name="Unknown",
                vram_gb=0.0,
                error=f"Failed to retrieve GPU info: {str(e)}"
            )

    def get_ram(self) -> RAMInfo:
        try:
            total_memory = psutil.virtual_memory().total
            return RAMInfo(
                total_gb=round(total_memory / (1024 ** 3), 2)
            )
        except Exception as e:
            return RAMInfo(
                total_gb=0.0,
                error=f"Failed to retrieve RAM info: {str(e)}"
            )

    def get_storage(self) -> StorageInfo:
        try:
            total, _, _ = shutil.disk_usage("/")
            return StorageInfo(
                total_gb=round(total / (1024 ** 3), 2)
            )
        except Exception as e:
            return StorageInfo(
                total_gb=0.0,
                error=f"Failed to retrieve storage info: {str(e)}"
            )