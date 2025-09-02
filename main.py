from chooseAI.linux_system_information import LinuxSystemInformation
from chooseAI.systemInfo import SystemInformation

linux_info = LinuxSystemInformation()
cpu_info = linux_info.get_cpu()
print(f"CPU: {cpu_info.name} - {cpu_info.logical_cores} cores")
if cpu_info.error:
    print(f"Error: {cpu_info.error}")