"""
nwtools核心模块 - 负优化功能实现
"""

import os
import sys
import time
import threading
import multiprocessing
import random
import tempfile
import subprocess
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# Windows 兼容性：尝试导入第三方库，如果失败则提供友好的错误信息
try:
    import psutil
except ImportError:
    print("警告: psutil 模块未安装。请运行: pip install psutil")
    psutil = None

try:
    import requests
except ImportError:
    print("警告: requests 模块未安装。请运行: pip install requests")
    requests = None

try:
    from colorama import init, Fore, Style
except ImportError:
    print("警告: colorama 模块未安装。请运行: pip install colorama")
    # 创建虚拟的 Fore 和 Style 类以保持兼容性
    class DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = Style = DummyColor()
    init = lambda **kwargs: None

# 初始化colorama - Windows 兼容性
import platform
if platform.system() == 'Windows':
    # 在 Windows 上需要调用 init() 来启用 ANSI 转义序列支持
    init(autoreset=True, convert=True)
else:
    init(autoreset=True)

class IntensityLevel(Enum):
    """负优化强度级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

@dataclass
class OptimizationConfig:
    """负优化配置"""
    intensity: IntensityLevel = IntensityLevel.MEDIUM
    auto_cleanup: bool = True
    max_cpu_percent: int = 99  # 狂暴级别：99%
    max_memory_mb: int = 16384  # 狂暴级别：16GB
    max_disk_files: int = 5000  # 狂暴级别：5000个文件
    max_processes: int = 500   # 狂暴级别：500个进程
    require_confirmation: bool = True
    custom_level: Optional[int] = None  # 自定义等级数值（最高10000）

class NegativeOptimizer:
    """负优化器主类"""
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self._running = False
        self._threads: List[threading.Thread] = []
        self._processes: List[multiprocessing.Process] = []
        self._temp_files: List[str] = []
        self._start_time = None
        
    def optimize_cpu(self, intensity: Optional[Union[str, IntensityLevel]] = None,
                  custom_level: Optional[int] = None) -> None:
        """
        CPU负优化 - 创建大量计算任务消耗CPU资源

        Args:
            intensity: 强度级别
            custom_level: 自定义等级数值（最高10000）
        """
        if not self._check_safety("CPU优化"):
            return

        intensity_level = self._parse_intensity(intensity)

        # 如果提供了自定义等级，使用自定义等级
        if custom_level is not None:
            custom_level = min(custom_level, 10000)  # 限制最高为10000
            self.config.custom_level = custom_level
            thread_count = self._get_thread_count_from_custom_level(custom_level)
            print(f"{Fore.YELLOW}[CPU负优化] 开始运行，自定义等级: {custom_level}")
        else:
            thread_count = self._get_thread_count(intensity_level)
            print(f"{Fore.YELLOW}[CPU负优化] 开始运行，强度: {intensity_level.value}")

        print(f"{Fore.YELLOW}[注意] 将无限期运行直到调用stop_all()")

        # 创建CPU密集型任务线程
        for i in range(thread_count):
            thread = threading.Thread(
                target=self._cpu_intensive_task,
                args=(0,),  # duration参数不再使用，传递0作为占位符
                name=f"cpu_optimizer_{i}"
            )
            thread.daemon = True
            thread.start()
            self._threads.append(thread)

        print(f"{Fore.GREEN}[CPU负优化] 已启动 {thread_count} 个CPU密集型线程")
        
    def optimize_memory(self, size_mb: Optional[int] = None,
                       intensity: Optional[Union[str, IntensityLevel]] = None,
                       custom_level: Optional[int] = None) -> None:
        """
        内存负优化 - 分配大量内存但不释放

        Args:
            size_mb: 内存大小（MB）
            intensity: 强度级别
            custom_level: 自定义等级数值（最高10000）
        """
        if not self._check_safety("内存优化"):
            return

        intensity_level = self._parse_intensity(intensity)

        # 如果提供了自定义等级，使用自定义等级
        if custom_level is not None:
            custom_level = min(custom_level, 10000)  # 限制最高为10000
            self.config.custom_level = custom_level
            size_mb = self._get_memory_size_from_custom_level(custom_level)
            print(f"{Fore.YELLOW}[内存负优化] 开始运行，自定义等级: {custom_level}")
        else:
            # 根据强度确定内存大小
            if size_mb is None:
                size_mb = self._get_memory_size(intensity_level)
            print(f"{Fore.YELLOW}[内存负优化] 开始运行，强度: {intensity_level.value}")

        # 限制最大内存使用
        size_mb = min(size_mb, self.config.max_memory_mb)

        print(f"{Fore.YELLOW}分配内存: {size_mb}MB")
        print(f"{Fore.YELLOW}[注意] 将无限期运行直到调用stop_all()")

        # 创建内存密集型任务线程
        thread = threading.Thread(
            target=self._memory_intensive_task,
            args=(size_mb, 0),  # duration参数不再使用，传递0作为占位符
            name="memory_optimizer"
        )
        thread.daemon = True
        thread.start()
        self._threads.append(thread)
        
    def optimize_disk(self, num_files: Optional[int] = None,
                     file_size_kb: Optional[int] = None,
                     intensity: Optional[Union[str, IntensityLevel]] = None,
                     custom_level: Optional[int] = None) -> None:
        """
        磁盘负优化 - 频繁读写磁盘，创建大量临时文件

        Args:
            num_files: 文件数量
            file_size_kb: 文件大小（KB）
            intensity: 强度级别
            custom_level: 自定义等级数值（最高10000）
        """
        if not self._check_safety("磁盘优化"):
            return

        intensity_level = self._parse_intensity(intensity)

        # 如果提供了自定义等级，使用自定义等级
        if custom_level is not None:
            custom_level = min(custom_level, 10000)  # 限制最高为10000
            self.config.custom_level = custom_level
            num_files = self._get_file_count_from_custom_level(custom_level)
            file_size_kb = self._get_file_size_from_custom_level(custom_level)
            print(f"{Fore.YELLOW}[磁盘负优化] 开始运行，自定义等级: {custom_level}")
        else:
            # 根据强度确定参数
            if num_files is None:
                num_files = self._get_file_count(intensity_level)
            if file_size_kb is None:
                file_size_kb = self._get_file_size(intensity_level)
            print(f"{Fore.YELLOW}[磁盘负优化] 开始运行，强度: {intensity_level.value}")

        # 限制最大文件数
        num_files = min(num_files, self.config.max_disk_files)

        print(f"{Fore.YELLOW}创建文件: {num_files}个, 每个: {file_size_kb}KB")

        # 创建磁盘IO线程
        thread = threading.Thread(
            target=self._disk_intensive_task,
            args=(num_files, file_size_kb),
            name="disk_optimizer"
        )
        thread.daemon = True
        thread.start()
        self._threads.append(thread)
        
    def _get_public_test_servers(self) -> list:
        """
        获取公共测试服务器列表
        这些服务器专门用于测试网络性能，可以承受一定的压力
        """
        return [
            "https://www.google.com",
            "https://www.cloudflare.com",
            "https://www.github.com",
            "https://www.microsoft.com",
            "https://www.amazon.com",
            "https://www.apple.com",
            "https://httpbin.org/get",
            "https://jsonplaceholder.typicode.com/posts/1"
        ]
    
    def optimize_network(self, num_requests: Optional[int] = None,
                        target_url: Optional[str] = None,
                        intensity: Optional[Union[str, IntensityLevel]] = None,
                        custom_level: Optional[int] = None) -> None:
        """
        网络负优化 - 发送大量网络请求，测试当前网络（WiFi/移动网络）性能

        Args:
            num_requests: 请求数量
            target_url: 目标URL（如果为None，则使用公共测试服务器）
            intensity: 强度级别
            custom_level: 自定义等级数值（最高10000）
        """
        if not self._check_safety("网络优化"):
            return

        intensity_level = self._parse_intensity(intensity)

        # 如果提供了自定义等级，使用自定义等级
        if custom_level is not None:
            custom_level = min(custom_level, 10000)  # 限制最高为10000
            self.config.custom_level = custom_level
            num_requests = self._get_request_count_from_custom_level(custom_level)
            print(f"{Fore.YELLOW}[网络负优化] 开始运行，自定义等级: {custom_level}")
        else:
            # 根据强度确定请求数
            if num_requests is None:
                num_requests = self._get_request_count(intensity_level)
            print(f"{Fore.YELLOW}[网络负优化] 开始运行，强度: {intensity_level.value}")

        # 获取公共测试服务器列表
        public_servers = self._get_public_test_servers()
        
        # 如果没有指定URL，使用公共测试服务器
        if target_url is None:
            target_url = public_servers[0]
            print(f"{Fore.GREEN}[网络测试] 使用公共服务器进行真实网络压力测试")
            print(f"{Fore.CYAN}[测试目标] {target_url}")
        else:
            print(f"{Fore.CYAN}[测试目标] {target_url}")

        print(f"{Fore.YELLOW}发送请求: {num_requests}个")
        print(f"{Fore.CYAN}[说明] 这将测试你当前连接的网络（WiFi/移动网络）性能")

        # 创建网络请求线程
        thread = threading.Thread(
            target=self._network_intensive_task,
            args=(num_requests, target_url),
            name="network_optimizer"
        )
        thread.daemon = True
        thread.start()
        self._threads.append(thread)
        
    def optimize_process(self, num_processes: Optional[int] = None,
                        intensity: Optional[Union[str, IntensityLevel]] = None,
                        custom_level: Optional[int] = None) -> None:
        """
        进程负优化 - 创建大量子进程

        Args:
            num_processes: 进程数量
            intensity: 强度级别
            custom_level: 自定义等级数值（最高10000）
        """
        if not self._check_safety("进程优化"):
            return

        intensity_level = self._parse_intensity(intensity)

        # 如果提供了自定义等级，使用自定义等级
        if custom_level is not None:
            custom_level = min(custom_level, 10000)  # 限制最高为10000
            self.config.custom_level = custom_level
            num_processes = self._get_process_count_from_custom_level(custom_level)
            print(f"{Fore.YELLOW}[进程负优化] 开始运行，自定义等级: {custom_level}")
        else:
            # 根据强度确定进程数
            if num_processes is None:
                num_processes = self._get_process_count(intensity_level)
            print(f"{Fore.YELLOW}[进程负优化] 开始运行，强度: {intensity_level.value}")

        # 限制最大进程数
        num_processes = min(num_processes, self.config.max_processes)

        print(f"{Fore.YELLOW}创建进程: {num_processes}个")

        # 创建子进程
        for i in range(num_processes):
            process = multiprocessing.Process(
                target=self._process_intensive_task,
                args=(0,),  # 不再使用duration参数，传递0作为占位符
                name=f"process_optimizer_{i}"
            )
            process.daemon = True
            process.start()
            self._processes.append(process)
            
    def optimize_all(self, intensity: Optional[Union[str, IntensityLevel]] = None,
                  custom_level: Optional[int] = None) -> None:
        """
        运行所有负优化功能

        Args:
            intensity: 强度级别
            custom_level: 自定义等级数值（最高10000）
        """
        if not self._check_safety("全面优化"):
            return

        intensity_level = self._parse_intensity(intensity)

        if custom_level is not None:
            custom_level = min(custom_level, 10000)  # 限制最高为10000
            self.config.custom_level = custom_level
            print(f"{Fore.CYAN}[全面负优化] 开始运行所有优化功能，自定义等级: {custom_level}")
        else:
            print(f"{Fore.CYAN}[全面负优化] 开始运行所有优化功能，强度: {intensity_level.value}")

        print(f"{Fore.YELLOW}[注意] 将无限期运行直到调用stop_all()")

        # 记录开始时间
        self._start_time = time.time()
        self._running = True

        # 运行所有优化
        self.optimize_cpu(intensity_level, custom_level)
        self.optimize_memory(None, intensity_level, custom_level)
        self.optimize_disk(None, None, intensity_level, custom_level)
        self.optimize_network(None, None, intensity_level, custom_level)
        self.optimize_process(None, intensity_level, custom_level)

        print(f"{Fore.GREEN}[全面负优化] 所有优化功能已启动")
        
    def stop_all(self) -> None:
        """停止所有负优化任务"""
        print(f"{Fore.YELLOW}[停止] 正在停止所有优化任务...")
        
        # 清理临时文件
        if self.config.auto_cleanup:
            self._cleanup_temp_files()
            
        # 终止进程
        for process in self._processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                
        # 标记线程停止
        self._running = False
        
        # 等待线程结束
        for thread in self._threads:
            if thread.is_alive():
                thread.join(timeout=5)
                
        self._threads.clear()
        self._processes.clear()
        
        print(f"{Fore.GREEN}[停止] 所有优化任务已停止")
        
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Windows 兼容性：使用当前工作目录的根路径
            import platform
            if platform.system() == 'Windows':
                # Windows 上使用当前工作目录的根盘符
                import os
                root_path = os.path.splitdrive(os.getcwd())[0] + '\\'
            else:
                root_path = '/'
            
            disk = psutil.disk_usage(root_path)
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used // (1024 * 1024),
                "memory_total_mb": memory.total // (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used // (1024 * 1024 * 1024),
                "disk_total_gb": disk.total // (1024 * 1024 * 1024),
                "process_count": len(psutil.pids()) if hasattr(psutil, 'pids') else 0,
                "running_time": time.time() - self._start_time if self._start_time else 0,
                "is_running": self._running
            }
        except (PermissionError, AttributeError) as e:
            # Windows 上可能没有权限获取进程列表
            return {
                "cpu_percent": cpu_percent if 'cpu_percent' in locals() else 0,
                "memory_percent": memory.percent if 'memory' in locals() else 0,
                "memory_used_mb": memory.used // (1024 * 1024) if 'memory' in locals() else 0,
                "memory_total_mb": memory.total // (1024 * 1024) if 'memory' in locals() else 0,
                "disk_percent": disk.percent if 'disk' in locals() else 0,
                "disk_used_gb": disk.used // (1024 * 1024 * 1024) if 'disk' in locals() else 0,
                "disk_total_gb": disk.total // (1024 * 1024 * 1024) if 'disk' in locals() else 0,
                "process_count": 0,
                "running_time": time.time() - self._start_time if self._start_time else 0,
                "is_running": self._running,
                "warning": f"部分信息获取失败: {str(e)}"
            }
        except Exception as e:
            return {"error": str(e)}
    
    # 私有方法
    
    def _check_safety(self, operation: str) -> bool:
        """安全检查"""
        # 检查自定义等级数值是否超过150
        if self.config.custom_level is not None and self.config.custom_level > 150:
            print(f"{Fore.RED}{Style.BRIGHT}[严重警告] 自定义等级数值过高: {self.config.custom_level}")
            print(f"{Fore.RED}{Style.BRIGHT}这可能会导致电脑卡顿！")
            print(f"{Fore.RED}{Style.BRIGHT}是否继续？(输入y继续，其他任意键取消): ", end="")

            try:
                response = input().strip().lower()
                if response != 'y':
                    print(f"{Fore.YELLOW}[取消] 操作已取消")
                    return False
            except EOFError:
                print(f"{Fore.YELLOW}[取消] 操作已取消")
                return False

        if self.config.require_confirmation:
            print(f"{Fore.RED}[安全警告] 即将执行: {operation}")
            print(f"{Fore.RED}此操作可能会降低系统性能，是否继续？(y/N): ", end="")

            try:
                response = input().strip().lower()
                if response != 'y':
                    print(f"{Fore.YELLOW}[取消] 操作已取消")
                    return False
            except EOFError:
                print(f"{Fore.YELLOW}[取消] 操作已取消")
                return False

        return True
        
    def _parse_intensity(self, intensity: Optional[Union[str, IntensityLevel]]) -> IntensityLevel:
        """解析强度级别"""
        if intensity is None:
            return self.config.intensity
            
        if isinstance(intensity, IntensityLevel):
            return intensity
            
        try:
            return IntensityLevel(intensity.lower())
        except ValueError:
            return self.config.intensity
            
    def _get_thread_count(self, intensity: IntensityLevel) -> int:
        """根据强度获取线程数"""
        cpu_count = multiprocessing.cpu_count()
        if intensity == IntensityLevel.LOW:
            return max(4, cpu_count)
        elif intensity == IntensityLevel.MEDIUM:
            return cpu_count * 3
        elif intensity == IntensityLevel.HIGH:
            return cpu_count * 6
        else:  # EXTREME - 狂暴强度
            return cpu_count * 16  # 16倍CPU核心数！

    def _get_thread_count_from_custom_level(self, custom_level: int) -> int:
        """根据自定义等级数值获取线程数"""
        cpu_count = multiprocessing.cpu_count()
        # 等级数值1对应1个线程，等级数值10000对应100000个线程
        return max(1, custom_level * 10)
            
    def _get_memory_size(self, intensity: IntensityLevel) -> int:
        """根据强度获取内存大小（MB）"""
        if intensity == IntensityLevel.LOW:
            return 1024  # 狂暴低强度：1GB
        elif intensity == IntensityLevel.MEDIUM:
            return 4096  # 狂暴中强度：4GB
        elif intensity == IntensityLevel.HIGH:
            return 8192  # 狂暴高强度：8GB
        else:  # EXTREME - 狂暴强度
            return 16384  # 狂暴极限：16GB！

    def _get_memory_size_from_custom_level(self, custom_level: int) -> int:
        """根据自定义等级数值获取内存大小（MB）"""
        # 等级数值1对应1MB，等级数值10000对应10000MB（10GB）
        return max(1, custom_level)
            
    def _get_file_count(self, intensity: IntensityLevel) -> int:
        """根据强度获取文件数量"""
        if intensity == IntensityLevel.LOW:
            return 100  # 狂暴低强度：100个
        elif intensity == IntensityLevel.MEDIUM:
            return 500  # 狂暴中强度：500个
        elif intensity == IntensityLevel.HIGH:
            return 2000  # 狂暴高强度：2000个
        else:  # EXTREME - 狂暴强度
            return 5000  # 狂暴极限：5000个！

    def _get_file_count_from_custom_level(self, custom_level: int) -> int:
        """根据自定义等级数值获取文件数量"""
        # 等级数值1对应1个文件，等级数值10000对应10000个文件
        return max(1, custom_level)

    def _get_file_size(self, intensity: IntensityLevel) -> int:
        """根据强度获取文件大小（KB）"""
        if intensity == IntensityLevel.LOW:
            return 5120  # 狂暴低强度：5MB
        elif intensity == IntensityLevel.MEDIUM:
            return 20480  # 狂暴中强度：20MB
        elif intensity == IntensityLevel.HIGH:
            return 51200  # 狂暴高强度：50MB
        else:  # EXTREME - 狂暴强度
            return 102400  # 狂暴极限：100MB！

    def _get_file_size_from_custom_level(self, custom_level: int) -> int:
        """根据自定义等级数值获取文件大小（KB）"""
        # 等级数值1对应1KB，等级数值10000对应10000KB（10MB）
        return max(1, custom_level)

    def _get_request_count(self, intensity: IntensityLevel) -> int:
        """根据强度获取请求数量"""
        if intensity == IntensityLevel.LOW:
            return 200  # 狂暴低强度：200个
        elif intensity == IntensityLevel.MEDIUM:
            return 1000  # 狂暴中强度：1000个
        elif intensity == IntensityLevel.HIGH:
            return 5000  # 狂暴高强度：5000个
        else:  # EXTREME - 狂暴强度
            return 10000  # 狂暴极限：10000个！

    def _get_request_count_from_custom_level(self, custom_level: int) -> int:
        """根据自定义等级数值获取请求数量（增强版）"""
        # 等级数值1对应100个请求，等级数值10000对应1000000个请求（100万）
        # 增强网络压力功能
        return max(100, custom_level * 100)

    def _get_process_count(self, intensity: IntensityLevel) -> int:
        """根据强度获取进程数量"""
        if intensity == IntensityLevel.LOW:
            return 20  # 狂暴低强度：20个
        elif intensity == IntensityLevel.MEDIUM:
            return 50  # 狂暴中强度：50个
        elif intensity == IntensityLevel.HIGH:
            return 200  # 狂暴高强度：200个
        else:  # EXTREME - 狂暴强度
            return 500  # 狂暴极限：500个！

    def _get_process_count_from_custom_level(self, custom_level: int) -> int:
        """根据自定义等级数值获取进程数量"""
        # 等级数值1对应1个进程，等级数值10000对应10000个进程
        return max(1, custom_level)
            
    # 任务函数
    
    def _cpu_intensive_task(self, duration: int) -> None:
        """CPU密集型任务 - 狂暴版"""
        # 去除时间限制，无限期运行直到被停止
        while self._running:
            # 执行极度密集的计算操作
            # 使用多重嵌套循环和复杂数学运算
            result = 0
            for i in range(1000000):  # 增加循环次数
                # 极度复杂的数学计算
                for j in range(200):
                    # 多项式计算
                    result += (i ** 2) * (j ** 3) + (i + j) ** 4
                    # 三角函数计算
                    import math
                    result += math.sin(i) * math.cos(j) * 1000
                # 矩阵运算模拟
                for k in range(100):
                    for l in range(10):
                        result += (i * k * l) ** 0.7 + (k / (l + 1)) ** 1.5
                
    def _memory_intensive_task(self, size_mb: int, duration: int) -> None:
        """内存密集型任务 - 狂暴版"""
        try:
            # 分配内存 - 狂暴速度分配
            chunk_size = 1024 * 1024  # 1MB
            chunks = []
            
            # 超大批量分配，几乎无延迟
            batch_size = 100  # 每次分配100MB！
            for i in range(0, size_mb, batch_size):
                if not self._running:
                    break
                # 一次性分配batch_size MB内存
                batch_chunks = [bytearray(chunk_size) for _ in range(min(batch_size, size_mb - i))]
                chunks.extend(batch_chunks)
                # 极短等待时间
                time.sleep(0.001)
                
            # 去除时间限制，无限期保持内存分配直到被停止
            while self._running:
                time.sleep(1)
                
        finally:
            # 释放内存
            chunks.clear()
            
    def _disk_intensive_task(self, num_files: int, file_size_kb: int) -> None:
        """磁盘密集型任务"""
        try:
            temp_dir = tempfile.mkdtemp(prefix="nwtools_")
            
            for i in range(num_files):
                if not self._running:
                    break
                    
                # 创建临时文件
                file_path = os.path.join(temp_dir, f"temp_{i}.dat")
                self._temp_files.append(file_path)
                
                # 写入随机数据
                with open(file_path, 'wb') as f:
                    data = os.urandom(file_size_kb * 1024)
                    f.write(data)
                    
                # 频繁读写文件 - 增强磁盘压力
                # 写入更多数据
                with open(file_path, 'ab') as f:
                    f.write(os.urandom(1024 * 10))  # 额外写入10KB
                
                # 随机读取文件（更频繁）
                if random.random() > 0.3:  # 增加读取概率
                    with open(file_path, 'rb') as f:
                        # 读取整个文件，增加磁盘IO
                        data = f.read()
                        # 对数据进行一些处理，增加CPU使用
                        _ = sum(byte for byte in data[:1000])
                        
                time.sleep(0.05)  # 减少等待时间，增加磁盘压力
                
        except Exception as e:
            print(f"{Fore.RED}[磁盘错误] {e}")
            
def _network_intensive_task(self, num_requests: int, target_url: str) -> None:
        """执行网络密集型任务 - 测试真实网络性能"""
        import requests
        import random
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        success_count = 0
        fail_count = 0
        start_time = time.time()
        
        # 获取公共服务器列表
        public_servers = self._get_public_test_servers()
        
        # 确保目标URL在列表中
        if target_url not in public_servers:
            public_servers.insert(0, target_url)
        
        def send_request(url: str, request_id: int) -> tuple:
            """发送单个请求"""
            try:
                # 添加随机参数避免缓存
                url_with_param = f"{url}?t={random.randint(1, 1000000)}&id={request_id}"
                
                # 发送请求，设置合理的超时
                response = requests.get(
                    url_with_param,
                    timeout=10,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Network Stress Test)',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                    }
                )
                
                return (True, response.status_code)
            except Exception as e:
                return (False, str(e))
        
        # 使用线程池并发发送请求，提高网络压力
        max_workers = min(20, num_requests)  # 最多20个并发
        
        print(f"{Fore.CYAN}[并发设置] 使用 {max_workers} 个并发连接")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = []
            for i in range(num_requests):
                if not self._running:
                    break
                    
                # 随机选择服务器，避免对单一服务器造成过大压力
                server_url = random.choice(public_servers)
                future = executor.submit(send_request, server_url, i)
                futures.append(future)
                
                # 每100个任务显示一次进度
                if (i + 1) % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed if elapsed > 0 else 0
                    print(f"{Fore.GREEN}[网络进度] 已提交: {i + 1}/{num_requests}, "
                          f"当前速率: {rate:.2f} req/s")
            
            # 等待所有任务完成
            for i, future in enumerate(as_completed(futures), 1):
                if not self._running:
                    break
                    
                success, result = future.result()
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                
                # 每50个完成的请求显示一次进度
                if i % 50 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    print(f"{Fore.GREEN}[网络完成] 完成: {i}/{len(futures)}, "
                          f"成功: {success_count}, 失败: {fail_count}, "
                          f"速率: {rate:.2f} req/s")
        
        elapsed = time.time() - start_time
        if elapsed > 0:
            rate = len(futures) / elapsed
            print(f"{Fore.GREEN}[网络完成] 总计: {len(futures)}个请求, "
                  f"成功: {success_count}, 失败: {fail_count}, "
                  f"平均速率: {rate:.2f} req/s")
        else:
            print(f"{Fore.GREEN}[网络完成] 总计: {len(futures)}个请求, "
                  f"成功: {success_count}, 失败: {fail_count}")
            
        def _process_intensive_task(self, duration: int) -> None:
            """进程密集型任务 - 增强版"""
            # 添加_running标志检查，确保进程可以被正确停止
            while self._running:
                # 执行更密集的计算
                result = 0
                # 增加计算复杂度
                for i in range(200000):
                    result += i * i
                    # 额外的浮点运算
                    if i % 1000 == 0:
                        result += (i ** 0.5) * (result ** 0.3)
                # 减少休眠时间，增加CPU使用
                time.sleep(0.05)
            
        def _cleanup_temp_files(self) -> None:
            """清理临时文件"""
            cleanup_errors = []
            
            for file_path in self._temp_files:
                try:
                    if os.path.exists(file_path):
                        # 尝试删除文件
                        os.remove(file_path)
                        print(f"{Fore.GREEN}[清理] 已删除临时文件: {file_path}")
                    else:
                        print(f"{Fore.YELLOW}[清理警告] 文件不存在: {file_path}")
                except PermissionError as e:
                    cleanup_errors.append(f"权限错误: {file_path} - {str(e)}")
                    print(f"{Fore.RED}[清理错误] 权限不足，无法删除文件 {file_path}")
                except FileNotFoundError:
                    # 文件已经被删除，忽略此错误
                    pass
                except OSError as e:
                    cleanup_errors.append(f"系统错误: {file_path} - {str(e)}")
                    print(f"{Fore.RED}[清理错误] 系统错误，无法删除文件 {file_path}: {e}")
                except Exception as e:
                    cleanup_errors.append(f"未知错误: {file_path} - {str(e)}")
                    print(f"{Fore.RED}[清理错误] 未知错误，无法删除文件 {file_path}: {e}")
        
        # 清空临时文件列表
        self._temp_files.clear()
        
        # 如果有错误，汇总显示
        if cleanup_errors:
            print(f"{Fore.YELLOW}[清理总结] 共 {len(cleanup_errors)} 个文件清理失败")
            for error in cleanup_errors[:5]:  # 只显示前5个错误
                print(f"  - {error}")
            if len(cleanup_errors) > 5:
                print(f"  ... 还有 {len(cleanup_errors) - 5} 个错误未显示")
        else:
            print(f"{Fore.GREEN}[清理完成] 所有临时文件已清理")