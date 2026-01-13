"""网络相关工具函数"""
import socket
import psutil

# 网卡识别规则：匹配关键字 -> 类型, 是否虚拟, 优先级
IFACE_RULES = [
    (['vmware', 'vmnet'],         'vmware',     True,  30),
    (['vbox', 'virtualbox'],      'virtualbox', True,  30),
    (['docker', 'wsl'],           'container',  True,  40),
    (['bluetooth'],               'bluetooth',  True,  60),
    (['ethernet', '以太网'],       'ethernet',   False, 10),
    (['wlan', 'wi-fi', '无线'],   'wifi',       False, 10),
    (['loopback'],                'loopback',   True,  100),
]


def detect_iface_type(iface: str):
    """
    根据网卡名称识别类型、虚拟状态和优先级。

    Args:
        iface (str): 网卡名称

    Returns:
        tuple:
            type (str): 网卡类型，如 'wifi', 'ethernet', 'vmware' 等
            virtual (bool): 是否虚拟网卡
            priority (int): 优先级，数值越小越推荐
    """
    lname = iface.lower()
    for keywords, t, virtual, prio in IFACE_RULES:
        if any(k in lname for k in keywords):
            return t, virtual, prio
    return 'unknown', False, 50


def get_private_networks(include_loopback: bool = False):
    """
    获取所有私有 IPv4 地址及网卡信息，并按优先级排序。

    排序后第一个元素通常是最推荐的局域网 IP。

    Args:
        include_loopback (bool): 是否包含回环地址（127.0.0.1）

    Returns:
        list[dict]: 每个元素为字典，包含：
            iface (str): 网卡名称
            ips (list[str]): 私有 IPv4 地址列表
            type (str): 网卡类型
            virtual (bool): 是否虚拟网卡
            priority (int): 网卡优先级
    """
    results = []
    interfaces = psutil.net_if_addrs()

    for iface, addrs in interfaces.items():
        ips = []
        iface_type, is_virtual, priority = detect_iface_type(iface)

        for addr in addrs:
            if addr.family != socket.AF_INET:
                continue  # 只处理 IPv4

            ip = addr.address

            # 排除非私有地址
            if ip.startswith('127.') and not include_loopback:
                continue  # 回环地址
            if ip.startswith('169.254.'):
                continue  # APIPA 地址
            if ip.startswith(('10.', '192.168.', '172.')):
                ips.append(ip)

        if ips:
            results.append({
                "iface": iface,
                "ips": ips,
                "type": iface_type,
                "virtual": is_virtual,
                "priority": priority
            })

    # 按优先级排序
    results.sort(key=lambda x: x['priority'])
    return results
