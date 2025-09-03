from chooseAI.windows_system_information import WindowsSystemInformation
from chooseAI.systemInfo import SystemInformation

windows_info = WindowsSystemInformation()
cpu_info = windows_info.get_cpu()
print(f"CPU: {cpu_info.name} - {cpu_info.logical_cores} cores")
if cpu_info.error:
    print(f"Error: {cpu_info.error}")