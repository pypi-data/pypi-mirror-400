import socket
import subprocess
import platform
import re
import os
from typing import Optional, List


def _check_command_exists(cmd: str) -> bool:
    """检查系统命令是否存在（跨平台）"""
    try:
        # Windows用where，Linux/macOS用which
        check_cmd = ["where", cmd] if platform.system() == "Windows" else ["which", cmd]
        subprocess.check_output(check_cmd, stderr=subprocess.STDOUT, timeout=5)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _get_linux_mac_address() -> Optional[str]:
    """Linux下鲁棒获取MAC地址（遍历网卡，跳过回环/虚拟网卡）"""
    try:
        # 遍历所有网卡目录
        net_path = "/sys/class/net/"
        if not os.path.exists(net_path):
            return None

        # 优先检查的网卡名（覆盖主流场景）
        priority_nics = ["eth0", "ens33", "ens160", "wlan0", "en0", "enp0s3"]
        all_nics = os.listdir(net_path)

        # 按优先级遍历网卡
        for nic in priority_nics + all_nics:
            nic_path = os.path.join(net_path, nic)
            addr_path = os.path.join(nic_path, "address")

            # 跳过回环网卡、虚拟网卡
            if nic == "lo" or not os.path.exists(addr_path):
                continue

            # 读取MAC地址
            with open(addr_path, "r", encoding="utf-8") as f:
                mac = f.read().strip().replace(":", "").upper()
            if len(mac) == 12 and re.match(r"^[0-9A-F]+$", mac):
                return mac
        return None
    except Exception:
        return None


def get_device_id() -> Optional[str]:
    """
    跨平台获取设备唯一ID（终极鲁棒版）
    特性：
    1. 编码完全兼容（Windows cp936/GBK，其他UTF-8）
    2. 命令超时保护（5秒）
    3. 命令存在性检查
    4. Linux网卡自适应（不依赖eth0）
    5. 多层降级方案（UUID→MAC→主机名）
    """
    system = platform.system()
    timeout = 5  # 所有命令超时5秒，避免卡死
    try:
        if system == "Windows":
            # 步骤1：检查wmic命令是否存在
            if not _check_command_exists("wmic"):
                # 降级：取C盘卷序列号（次优唯一标识）
                return _get_windows_drive_serial()

            # 步骤2：执行wmic获取UUID，先读字节再解码（兼容cp936/GBK）
            result = subprocess.check_output(
                ["wmic", "csproduct", "get", "UUID"],
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=timeout
            )
            # 解码：优先cp936（Windows默认），失败则忽略乱码
            try:
                result_str = result.decode("cp936").strip()
            except UnicodeDecodeError:
                result_str = result.decode("gbk", errors="ignore").strip()

            # 步骤3：清洗输出（移除表头、空行）
            lines = [line.strip() for line in result_str.splitlines() if line.strip()]
            uuid_lines = [line for line in lines if re.match(r"^[0-9A-Fa-f-]+$", line)]

            # 步骤4：匹配UUID（优先取非默认值，排除全0/全X的无效UUID）
            for line in uuid_lines:
                if re.match(r"([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})", line):
                    # 排除无效UUID（厂商未写入的默认值）
                    if line not in ["00000000-0000-0000-0000-000000000000", "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF"]:
                        return line.upper()
            print("Windows UUID无效，降级为磁盘序列号")
            return _get_windows_drive_serial()

        elif system == "Darwin":  # macOS
            if not _check_command_exists("system_profiler"):
                print("macOS缺少system_profiler命令，降级为MAC地址")
                return _get_macos_mac_address()

            result = subprocess.check_output(
                ["system_profiler", "SPHardwareDataType"],
                stderr=subprocess.STDOUT,
                timeout=timeout
            )
            result_str = result.decode("utf-8", errors="ignore").strip()

            # 宽松匹配Hardware UUID（兼容不同输出格式）
            match = re.search(r"Hardware UUID:\s*([0-9A-Fa-f-]{36})", result_str, re.IGNORECASE)
            if match and match.group(1).strip():
                return match.group(1).upper()

            print("macOS未找到Hardware UUID，降级为MAC地址")
            return _get_macos_mac_address()

        elif system == "Linux":
            # 步骤1：尝试dmidecode获取UUID（先检查命令是否存在）
            if _check_command_exists("dmidecode"):
                try:
                    result = subprocess.check_output(
                        ["dmidecode", "-s", "system-uuid"],  # 移除sudo，避免交互
                        stderr=subprocess.STDOUT,
                        timeout=timeout
                    )
                    result_str = result.decode("utf-8", errors="ignore").strip()
                    if re.match(r"^[0-9A-Fa-f-]{36}$", result_str):
                        return result_str.upper()
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    pass

            # 步骤2：降级获取MAC地址
            mac = _get_linux_mac_address()
            if mac:
                # 转为类UUID格式（保持返回结构一致）
                return f"{mac[:8]}-{mac[8:12]}-1000-8000-000000000000".upper()

            # 步骤3：最终降级为主机名
            print("Linux未找到UUID/MAC，降级为主机名")
            return platform.node().upper()

        else:
            print(f"暂不支持{system}系统")
            return None

    except subprocess.TimeoutExpired:
        print("获取设备ID超时（命令执行超过5秒）")
        return None
    except subprocess.CalledProcessError as e:
        error_output = e.output.decode("utf-8", errors="ignore") if isinstance(e.output, bytes) else str(e.output)
        print(f"命令执行失败：{error_output.strip()[:100]}...")
        return None
    except Exception as e:
        print(f"获取设备ID异常：{str(e)}")
        return None


def _get_windows_drive_serial() -> Optional[str]:
    """Windows降级方案：获取C盘卷序列号（唯一标识）"""
    try:
        result = subprocess.check_output(
            ["wmic", "logicaldisk", "where", "deviceid='C:'", "get", "VolumeSerialNumber"],
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=5
        )
        result_str = result.decode("cp936", errors="ignore").strip()
        lines = [line.strip() for line in result_str.splitlines() if line.strip()]
        if len(lines) >= 2:
            serial = lines[1]
            # 转为类UUID格式
            return f"{serial[:8]}-{serial[8:12]}-1000-8000-000000000000".upper()
        return None
    except Exception:
        return platform.node().upper()


def _get_macos_mac_address() -> Optional[str]:
    """macOS获取MAC地址（en0为主网卡）"""
    try:
        result = subprocess.check_output(
            ["ifconfig", "en0"],
            stderr=subprocess.STDOUT,
            timeout=5
        )
        result_str = result.decode("utf-8", errors="ignore")
        match = re.search(r"ether\s+([0-9a-f:]+)", result_str)
        if match:
            mac = match.group(1).replace(":", "").upper()
            return f"{mac[:8]}-{mac[8:12]}-1000-8000-000000000000".upper()
        return None
    except Exception:
        return platform.node().upper()


def get_local_ip() -> str:
    """鲁棒获取本地IP（多DNS兜底，避免访问失败）"""
    # 国内可访问的公共DNS列表（兜底）
    dns_servers = ["223.5.5.5", "114.114.114.114", "8.8.8.8"]
    for dns in dns_servers:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(3)
                s.connect((dns, 80))
                return s.getsockname()[0]
        except (socket.timeout, OSError):
            continue
    print("所有DNS均无法连接，返回回环地址")
    return "127.0.0.1"


def get_device_info() -> str:
    """获取设备信息（ID+IP），保证返回非空"""
    try:
        local_ip = get_local_ip()
        device_id = get_device_id() or "未知设备ID"
        return f"{device_id}|{local_ip}"
    except Exception as e:
        print(f"设备信息获取失败：{e}")
        return f"未知设备ID|127.0.0.1"
