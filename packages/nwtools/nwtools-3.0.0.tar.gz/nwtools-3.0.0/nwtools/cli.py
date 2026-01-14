"""
nwtools命令行界面
"""

import argparse
import sys
import time
from typing import Optional
from colorama import init, Fore, Style

from .core import NegativeOptimizer, IntensityLevel, OptimizationConfig

# 初始化colorama
init(autoreset=True)

def print_banner():
    """打印横幅"""
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}
╔══════════════════════════════════════════════════════════╗
║                    nwtools v1.0.0                        ║
║      Negative Optimizer for Windows/Linux Systems        ║
╚══════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
{Fore.YELLOW}警告：请谨慎使用！仅在测试环境或虚拟机中使用！{Style.RESET_ALL}
"""
    print(banner)

def print_status(optimizer: NegativeOptimizer):
    """打印系统状态"""
    status = optimizer.get_system_status()
    
    if "error" in status:
        print(f"{Fore.RED}[错误] 无法获取系统状态: {status['error']}")
        return
        
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== 系统状态 ===")
    print(f"{Fore.WHITE}CPU使用率: {Fore.GREEN}{status['cpu_percent']}%")
    print(f"{Fore.WHITE}内存使用: {Fore.GREEN}{status['memory_used_mb']}MB / {status['memory_total_mb']}MB ({status['memory_percent']}%)")
    print(f"{Fore.WHITE}磁盘使用: {Fore.GREEN}{status['disk_used_gb']}GB / {status['disk_total_gb']}GB ({status['disk_percent']}%)")
    print(f"{Fore.WHITE}进程数量: {Fore.GREEN}{status['process_count']}")
    
    if status['is_running']:
        print(f"{Fore.WHITE}运行时间: {Fore.YELLOW}{status['running_time']:.1f}秒")
        print(f"{Fore.GREEN}[状态] 负优化正在运行")
    else:
        print(f"{Fore.YELLOW}[状态] 负优化未运行")

def run_cpu_optimizer(args, optimizer: NegativeOptimizer):
    """运行CPU负优化"""
    optimizer.optimize_cpu(
        intensity=args.intensity
    )
    
    print(f"{Fore.YELLOW}[注意] CPU优化将无限期运行，使用 'nwtools stop' 停止")

def run_memory_optimizer(args, optimizer: NegativeOptimizer):
    """运行内存负优化"""
    optimizer.optimize_memory(
        size_mb=args.size,
        intensity=args.intensity
    )
    
    print(f"{Fore.YELLOW}[注意] 内存优化将无限期运行，使用 'nwtools stop' 停止")

def run_disk_optimizer(args, optimizer: NegativeOptimizer):
    """运行磁盘负优化"""
    optimizer.optimize_disk(
        num_files=args.files,
        file_size_kb=args.size,
        intensity=args.intensity
    )
    
    # 磁盘优化不需要自动停止，它会自己完成

def run_network_optimizer(args, optimizer: NegativeOptimizer):
    """运行网络负优化"""
    optimizer.optimize_network(
        num_requests=args.requests,
        target_url=args.url,
        intensity=args.intensity
    )

def run_process_optimizer(args, optimizer: NegativeOptimizer):
    """运行进程负优化"""
    optimizer.optimize_process(
        num_processes=args.count,
        intensity=args.intensity
    )
    
    print(f"{Fore.YELLOW}[注意] 进程优化将无限期运行，使用 'nwtools stop' 停止")

def run_all_optimizer(args, optimizer: NegativeOptimizer):
    """运行所有负优化"""
    optimizer.optimize_all(
        intensity=args.intensity
    )
    
    print(f"{Fore.YELLOW}[注意] 所有优化将无限期运行，使用 'nwtools stop' 停止")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="nwtools - 系统负优化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  nwtools run                    # 运行所有负优化（无限期）
  nwtools cpu                    # 运行CPU优化（无限期）
  nwtools memory --size 1024     # 分配1024MB内存（无限期）
  nwtools disk --files 50        # 创建50个临时文件
  nwtools network --requests 100 # 测试当前网络性能（发送100个请求）
  nwtools process --count 10     # 创建10个子进程（无限期）
  nwtools stop                   # 停止所有优化
  nwtools status                 # 显示系统状态
        """
    )
    
    # 添加版本参数
    parser.add_argument(
        '--version',
        action='version',
        version='nwtools v1.0.0'
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # run命令 - 运行所有优化
    run_parser = subparsers.add_parser("run", help="运行所有负优化功能")
    run_parser.add_argument("--intensity", "-i",
                          choices=["low", "medium", "high", "extreme"],
                          default="medium",
                          help="优化强度")
    run_parser.add_argument("--custom-level", "-c", type=int,
                          help="自定义等级数值（1-10000），超过150会触发安全确认")

    # cpu命令
    cpu_parser = subparsers.add_parser("cpu", help="CPU负优化")
    cpu_parser.add_argument("--intensity", "-i",
                          choices=["low", "medium", "high", "extreme"],
                          default="medium",
                          help="优化强度")
    cpu_parser.add_argument("--custom-level", "-c", type=int,
                          help="自定义等级数值（1-10000），超过150会触发安全确认")

    # memory命令
    memory_parser = subparsers.add_parser("memory", help="内存负优化")
    memory_parser.add_argument("--intensity", "-i",
                             choices=["low", "medium", "high", "extreme"],
                             default="medium",
                             help="优化强度")
    memory_parser.add_argument("--size", "-s", type=int,
                             help="内存大小（MB）")
    memory_parser.add_argument("--custom-level", "-c", type=int,
                             help="自定义等级数值（1-10000），超过150会触发安全确认")

    # disk命令
    disk_parser = subparsers.add_parser("disk", help="磁盘负优化")
    disk_parser.add_argument("--intensity", "-i",
                           choices=["low", "medium", "high", "extreme"],
                           default="medium",
                           help="优化强度")
    disk_parser.add_argument("--files", "-f", type=int,
                           help="文件数量")
    disk_parser.add_argument("--size", "-s", type=int,
                           help="文件大小（KB）")
    disk_parser.add_argument("--custom-level", "-c", type=int,
                           help="自定义等级数值（1-10000），超过150会触发安全确认")

    # network命令
    network_parser = subparsers.add_parser("network", help="网络压力测试（测试当前WiFi/移动网络）")
    network_parser.add_argument("--intensity", "-i",
                              choices=["low", "medium", "high", "extreme"],
                              default="medium",
                              help="优化强度")
    network_parser.add_argument("--requests", "-r", type=int,
                              help="请求数量")
    network_parser.add_argument("--url", "-u", type=str,
                              help="目标URL（默认使用公共测试服务器）")
    network_parser.add_argument("--custom-level", "-c", type=int,
                              help="自定义等级数值（1-10000），超过150会触发安全确认")

    # process命令
    process_parser = subparsers.add_parser("process", help="进程负优化")
    process_parser.add_argument("--intensity", "-i",
                              choices=["low", "medium", "high", "extreme"],
                              default="medium",
                              help="优化强度")
    process_parser.add_argument("--count", "-c", type=int,
                              help="进程数量")
    process_parser.add_argument("--custom-level", "-l", type=int,
                              help="自定义等级数值（1-10000），超过150会触发安全确认")
    
    # stop命令
    subparsers.add_parser("stop", help="停止所有负优化")
    
    # status命令
    subparsers.add_parser("status", help="显示系统状态")
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        print_banner()
        parser.print_help()
        return
        
    args = parser.parse_args()
    
    # 创建优化器实例
    config = OptimizationConfig()
    optimizer = NegativeOptimizer(config)
    
    # 执行命令
    if args.command == "run":
        print_banner()
        run_all_optimizer(args, optimizer)
        
    elif args.command == "cpu":
        print_banner()
        run_cpu_optimizer(args, optimizer)
        
    elif args.command == "memory":
        print_banner()
        run_memory_optimizer(args, optimizer)
        
    elif args.command == "disk":
        print_banner()
        run_disk_optimizer(args, optimizer)
        
    elif args.command == "network":
        print_banner()
        run_network_optimizer(args, optimizer)
        
    elif args.command == "process":
        print_banner()
        run_process_optimizer(args, optimizer)
        
    elif args.command == "stop":
        print_banner()
        optimizer.stop_all()
        
    elif args.command == "status":
        print_banner()
        print_status(optimizer)
        
    else:
        print_banner()
        parser.print_help()

if __name__ == "__main__":
    main()
