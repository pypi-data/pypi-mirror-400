"""
nwtools工具模块 - 辅助功能
"""

import os
import sys
import platform
import json
from pathlib import Path
from typing import Dict, Any, Optional
from colorama import Fore, Style

# 尝试导入yaml，如果失败则设为None
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    yaml = None
    YAML_AVAILABLE = False

def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }
    
    # 尝试获取更多信息
    try:
        import psutil
        info["memory_total_mb"] = psutil.virtual_memory().total // (1024 * 1024)
        info["disk_total_gb"] = psutil.disk_usage('/').total // (1024 * 1024 * 1024)
    except ImportError:
        pass
        
    return info

def print_system_info():
    """打印系统信息"""
    info = get_system_info()
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== 系统信息 ===")
    for key, value in info.items():
        print(f"{Fore.WHITE}{key}: {Fore.GREEN}{value}")
    print()

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """加载配置文件"""
    default_config = {
        "defaults": {
            "intensity": "medium",
            "duration": 60,
            "auto_cleanup": True
        },
        "limits": {
            "max_cpu_percent": 80,
            "max_memory_mb": 2048,
            "max_disk_files": 100,
            "max_processes": 20
        },
        "safety": {
            "require_confirmation": True,
            "max_total_duration": 300
        }
    }
    
    if config_path is None:
        # 尝试从用户目录加载配置
        config_path = Path.home() / ".nwtools" / "config.yaml"
        
    if not config_path.exists():
        # 返回默认配置的副本，避免修改影响默认值
        return default_config.copy()
        
    try:
        if not YAML_AVAILABLE:
            print(f"{Fore.YELLOW}[配置警告] yaml模块未安装，使用默认配置")
            return default_config.copy()
            
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f)
            
        # 如果配置文件为空，返回默认配置
        if user_config is None:
            print(f"{Fore.YELLOW}[配置警告] 配置文件为空，使用默认配置")
            return default_config.copy()
            
        # 合并配置
        merged_config = default_config.copy()
        _deep_update(merged_config, user_config)
        return merged_config
        
    except FileNotFoundError:
        print(f"{Fore.YELLOW}[配置警告] 配置文件不存在，使用默认配置")
        return default_config.copy()
    except yaml.YAMLError as e:
        print(f"{Fore.RED}[配置错误] YAML解析失败: {e}")
        return default_config.copy()
    except Exception as e:
        print(f"{Fore.RED}[配置错误] 无法加载配置文件: {e}")
        return default_config.copy()

def save_config(config: Dict[str, Any], config_path: Optional[str] = None):
    """保存配置文件"""
    if config_path is None:
        config_dir = Path.home() / ".nwtools"
        config_dir.mkdir(exist_ok=True)
        config_path = config_dir / "config.yaml"
        
    try:
        if not YAML_AVAILABLE:
            print(f"{Fore.RED}[配置错误] yaml模块未安装，无法保存配置")
            return
            
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        print(f"{Fore.GREEN}[配置] 配置文件已保存: {config_path}")
    except Exception as e:
        print(f"{Fore.RED}[配置错误] 无法保存配置文件: {e}")

def _deep_update(base: Dict[str, Any], update: Dict[str, Any]) -> None:
    """深度更新字典"""
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_update(base[key], value)
        else:
            base[key] = value

def check_dependencies() -> bool:
    """检查依赖是否安装"""
    missing_deps = []
    
    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")
        
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
        
    try:
        import colorama
    except ImportError:
        missing_deps.append("colorama")
        
    try:
        import yaml
    except ImportError:
        missing_deps.append("pyyaml")
        
    if missing_deps:
        print(f"{Fore.RED}[依赖错误] 缺少以下依赖包:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print(f"\n{Fore.YELLOW}请使用以下命令安装:")
        print(f"pip install {' '.join(missing_deps)}")
        return False
        
    return True

def get_resource_usage() -> Dict[str, Any]:
    """获取资源使用情况"""
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 获取nwtools相关进程
        nwtools_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if 'nwtools' in proc.info['name'].lower() or 'python' in proc.info['name'].lower():
                    # 检查命令行参数
                    cmdline = ' '.join(proc.cmdline())
                    if 'nwtools' in cmdline:
                        nwtools_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent']
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_mb": memory.used // (1024 * 1024),
            "disk_percent": disk.percent,
            "nwtools_processes": nwtools_processes,
            "total_processes": len(psutil.pids())
        }
        
    except ImportError:
        return {"error": "psutil not installed"}
    except Exception as e:
        return {"error": str(e)}

def format_bytes(size: int) -> str:
    """格式化字节大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def print_resource_usage():
    """打印资源使用情况"""
    usage = get_resource_usage()
    
    if "error" in usage:
        print(f"{Fore.RED}[错误] 无法获取资源使用情况: {usage['error']}")
        return
        
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== 资源使用情况 ===")
    print(f"{Fore.WHITE}CPU使用率: {Fore.GREEN}{usage['cpu_percent']}%")
    print(f"{Fore.WHITE}内存使用率: {Fore.GREEN}{usage['memory_percent']}% ({usage['memory_used_mb']} MB)")
    print(f"{Fore.WHITE}磁盘使用率: {Fore.GREEN}{usage['disk_percent']}%")
    print(f"{Fore.WHITE}总进程数: {Fore.GREEN}{usage['total_processes']}")
    
    if usage['nwtools_processes']:
        print(f"\n{Fore.YELLOW}nwtools相关进程:")
        for proc in usage['nwtools_processes']:
            print(f"  PID {proc['pid']}: {proc['name']} - CPU: {proc['cpu_percent']}%, 内存: {proc['memory_percent']}%")
    else:
        print(f"\n{Fore.YELLOW}未找到nwtools相关进程")
