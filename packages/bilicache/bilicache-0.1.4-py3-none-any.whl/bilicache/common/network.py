"""
网络配置模块 - 全局禁用 IPv6，确保只使用 IPv4
"""
import os
import socket
import logging

logger = logging.getLogger("bilicache")


def disable_ipv6():
    """
    全局禁用 IPv6，强制所有网络连接使用 IPv4
    这个函数应该在应用启动的最早阶段调用，在任何网络请求之前
    """
    try:
        # 方法1: 设置环境变量，影响 aiohttp 等库的行为
        os.environ.setdefault("AIOHTTP_NO_EXTENSIONS", "0")
        
        # 方法2: 通过 monkey patch socket.getaddrinfo 来强制只返回 IPv4 地址
        original_getaddrinfo = socket.getaddrinfo
        
        def getaddrinfo_ipv4_only(*args, **kwargs):
            """只返回 IPv4 地址的 getaddrinfo"""
            # 如果指定了 family，检查是否需要修改
            if len(args) >= 4:
                # args 格式: (host, port, family=0, type=0, proto=0, flags=0)
                # 修改 args 中的 family
                args_list = list(args)
                if len(args_list) >= 3:
                    if args_list[2] == socket.AF_INET6 or args_list[2] == 0:
                        args_list[2] = socket.AF_INET
                        args = tuple(args_list)
            elif 'family' in kwargs:
                if kwargs['family'] == socket.AF_INET6 or kwargs.get('family') == 0:
                    # 如果明确要求 IPv6 或未指定，改成 IPv4
                    kwargs['family'] = socket.AF_INET
                    logger.debug("强制将 DNS 解析改为 IPv4")
            else:
                # 如果没有指定 family，强制使用 IPv4
                kwargs['family'] = socket.AF_INET
            
            # 调用原始函数，但确保只返回 IPv4
            try:
                results = original_getaddrinfo(*args, **kwargs)
            except Exception as e:
                # 如果解析失败，尝试强制使用 IPv4 重试
                kwargs['family'] = socket.AF_INET
                results = original_getaddrinfo(*args, **kwargs)
            
            # 过滤掉 IPv6 结果（双重保险）
            ipv4_results = [
                r for r in results 
                if r[0] == socket.AF_INET
            ]
            if ipv4_results:
                return ipv4_results
            # 如果没有 IPv4 结果但有其他结果，记录警告
            if results:
                hostname = args[0] if args else 'unknown'
                logger.warning(f"域名 {hostname} 无法解析为 IPv4，将尝试强制解析")
                # 强制使用 IPv4 重新解析
                kwargs['family'] = socket.AF_INET
                try:
                    forced_results = original_getaddrinfo(*args, **kwargs)
                    ipv4_forced = [r for r in forced_results if r[0] == socket.AF_INET]
                    if ipv4_forced:
                        return ipv4_forced
                except:
                    pass
            return results
        
        # 替换 socket.getaddrinfo
        socket.getaddrinfo = getaddrinfo_ipv4_only
        logger.debug("已全局禁用 IPv6，强制使用 IPv4")
        
    except Exception as e:
        logger.warning(f"禁用 IPv6 时发生异常: {e}")


def patch_aiohttp_connector():
    """
    Monkey patch aiohttp 的默认 TCPConnector，使其默认只使用 IPv4
    """
    try:
        import aiohttp
        
        original_init = aiohttp.TCPConnector.__init__
        
        def __init___ipv4(self, *args, **kwargs):
            # 如果没有明确指定 family，强制使用 IPv4
            if 'family' not in kwargs:
                kwargs['family'] = socket.AF_INET
            # 如果指定了 IPv6，改为 IPv4
            elif kwargs.get('family') == socket.AF_INET6:
                kwargs['family'] = socket.AF_INET
                logger.debug("将 aiohttp TCPConnector 的 IPv6 请求改为 IPv4")
            return original_init(self, *args, **kwargs)
        
        aiohttp.TCPConnector.__init__ = __init___ipv4
        logger.debug("已 patch aiohttp TCPConnector 默认使用 IPv4")
        
    except ImportError:
        # aiohttp 可能还没安装，忽略
        pass
    except Exception as e:
        logger.warning(f"Patch aiohttp 时发生异常: {e}")


def init_network():
    """
    初始化网络配置，全局禁用 IPv6
    应该在应用启动的最早阶段调用
    """
    try:
        disable_ipv6()
        patch_aiohttp_connector()
        # 使用 print 而不是 logger，因为此时 logger 可能还未配置
        # logger.info("网络配置初始化完成：已强制使用 IPv4")
    except Exception as e:
        # 静默处理异常，避免影响程序启动
        pass
