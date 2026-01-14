import socket
import subprocess
import platform
import re
from typing import Optional

def get_local_ip():
    try:
        # 创建UDP Socket（无需实际发送数据，仅用于获取本地地址）
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # 连接到外部服务器（如Google DNS：8.8.8.8，端口任意）
            # 不要求实际连通，仅用于触发本地IP绑定
            s.connect(("8.8.8.8", 80))
            # 获取本地Socket绑定的IP地址（元组第一个元素）
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        print(f"获取IP失败：{e}")
        return "127.0.0.1"  # 失败时返回回环地址


def get_device_id() -> Optional[str]:
    """
    跨平台获取设备唯一ID（基于系统/主板UUID）
    :return: 设备ID（UUID格式），失败时返回None
    """
    system = platform.system()  # 获取系统类型（Windows/macOS/Linux）
    
    try:
        if system == "Windows":
            # Windows：通过wmic获取系统UUID（来自主板/BIOS）
            # 命令说明：csproduct是"计算机产品"，UUID是厂商固化的设备标识
            result = subprocess.check_output(
                ["wmic", "csproduct", "get", "UUID"],
                encoding="utf-8",
                shell=True,
                stderr=subprocess.STDOUT  # 合并错误输出
            )
            # 匹配UUID格式（8-4-4-4-12位十六进制）
            match = re.search(r"([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})", result)
        
        elif system == "Darwin":  # macOS
            # macOS：通过system_profiler获取硬件UUID（系统级唯一标识）
            # 命令说明：SPHardwareDataType包含硬件信息，Hardware UUID是设备唯一标识
            result = subprocess.check_output(
                ["system_profiler", "SPHardwareDataType"],
                encoding="utf-8",
                stderr=subprocess.STDOUT
            )
            # 提取Hardware UUID
            match = re.search(r"Hardware UUID:\s+([0-9A-Fa-f-]+)", result)
        
        elif system == "Linux":
            # Linux：通过dmidecode获取系统UUID（需root权限，部分系统可能无此命令）
            # 命令说明：dmidecode -s system-uuid 直接返回系统UUID
            result = subprocess.check_output(
                ["sudo", "dmidecode", "-s", "system-uuid"],  # sudo确保权限
                encoding="utf-8",
                stderr=subprocess.STDOUT
            )
            # 匹配UUID格式（Linux输出可能带空格，需strip）
            match = re.search(r"([0-9A-Fa-f-]+)", result.strip())
        
        else:
            # 其他系统（如FreeBSD等）暂不支持
            print(f"暂不支持{system}系统")
            return None

        # 提取并返回UUID（忽略大小写，统一转为大写）
        if match:
            return match.group(1).upper()
        else:
            print(f"{system}系统未找到设备ID（输出：{result.strip()}）")
            return None

    except subprocess.CalledProcessError as e:
        # 命令执行失败（如权限不足、命令不存在）
        if system == "Linux" and "permission denied" in e.output.lower():
            print("Linux系统获取设备ID需要root权限（请用sudo运行）")
        else:
            print(f"命令执行失败：{e.output.strip()}")
        return None
    except Exception as e:
        # 其他异常（如正则匹配失败）
        print(f"获取设备ID异常：{str(e)}")
        return None


# 测试
if __name__ == "__main__":
    device_id = get_device_id()
    ip=get_local_ip()
    device_info=f"{device_id}|{ip}"
    # 测试
    if device_info:
        print(f"设备ID：{device_info}")
    else:
        print("获取设备ID失败")

