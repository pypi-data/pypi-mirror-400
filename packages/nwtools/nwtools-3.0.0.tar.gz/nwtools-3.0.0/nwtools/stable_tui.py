#!/usr/bin/env python3
"""
nwtools 稳定TUI界面
作者: ruin321
"""

import os
import sys
import time
from typing import List, Dict, Optional, Callable

from .core import NegativeOptimizer, IntensityLevel
from .utils import load_config, save_config
from colorama import init, Fore, Style

# 初始化colorama
init(autoreset=True)

class StableTUI:
    """稳定TUI界面"""
    
    def __init__(self):
        # 加载配置并禁用安全确认，让优化可以直接运行
        self.config = load_config()
        self.config['require_confirmation'] = False  # 禁用安全确认
        
        # 创建优化器时使用修改后的配置
        from .core import OptimizationConfig
        from dataclasses import asdict
        
        # 从嵌套字典中提取需要的配置项
        intensity_value = 'medium'
        auto_cleanup = True
        max_cpu_percent = 80
        max_memory_mb = 2048
        max_disk_files = 100
        max_processes = 20
        require_confirmation = False
        
        # 尝试从defaults中获取默认值
        if 'defaults' in self.config:
            defaults = self.config['defaults']
            if 'intensity' in defaults:
                intensity_value = defaults['intensity']
            if 'auto_cleanup' in defaults:
                auto_cleanup = defaults['auto_cleanup']
        
        # 尝试从limits中获取限制值
        if 'limits' in self.config:
            limits = self.config['limits']
            if 'max_cpu_percent' in limits:
                max_cpu_percent = limits['max_cpu_percent']
            if 'max_memory_mb' in limits:
                max_memory_mb = limits['max_memory_mb']
            if 'max_disk_files' in limits:
                max_disk_files = limits['max_disk_files']
            if 'max_processes' in limits:
                max_processes = limits['max_processes']
        
        # 尝试从safety中获取安全配置
        if 'safety' in self.config:
            safety = self.config['safety']
            if 'require_confirmation' in safety:
                require_confirmation = safety['require_confirmation']
        
        # 也检查顶层配置（优先级更高）
        if 'intensity' in self.config:
            intensity_value = self.config['intensity']
        if 'auto_cleanup' in self.config:
            auto_cleanup = self.config['auto_cleanup']
        if 'max_cpu_percent' in self.config:
            max_cpu_percent = self.config['max_cpu_percent']
        if 'max_memory_mb' in self.config:
            max_memory_mb = self.config['max_memory_mb']
        if 'max_disk_files' in self.config:
            max_disk_files = self.config['max_disk_files']
        if 'max_processes' in self.config:
            max_processes = self.config['max_processes']
        if 'require_confirmation' in self.config:
            require_confirmation = self.config['require_confirmation']
        
        # 确保禁用确认
        require_confirmation = False
        
        # 创建配置对象，处理intensity的类型转换
        from .core import IntensityLevel
        
        try:
            # 如果intensity_value已经是IntensityLevel枚举类型，直接使用
            if isinstance(intensity_value, IntensityLevel):
                intensity_enum = intensity_value
            else:
                # 否则将字符串转换为IntensityLevel枚举
                intensity_enum = IntensityLevel(str(intensity_value).lower())
        except (ValueError, TypeError):
            # 如果转换失败，使用默认值
            print(f"{Fore.YELLOW}[配置警告] 强度值 '{intensity_value}' 无效，使用默认值 'medium'{Style.RESET_ALL}")
            intensity_enum = IntensityLevel.MEDIUM
        
        config_obj = OptimizationConfig(
            intensity=intensity_enum,
            auto_cleanup=bool(auto_cleanup),
            max_cpu_percent=int(max_cpu_percent),
            max_memory_mb=int(max_memory_mb),
            max_disk_files=int(max_disk_files),
            max_processes=int(max_processes),
            require_confirmation=bool(require_confirmation)
        )
        
        self.optimizer = NegativeOptimizer(config=config_obj)
        self.running = False
        
    def clear_screen(self):
        """清屏（跨平台）"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
    def print_menu(self, title: str, items: List[str], current_page: int = 1, total_pages: int = 1):
        """打印菜单"""
        self.clear_screen()
        self.print_header(title)
        
        # 显示页码（如果有分页）
        if total_pages > 1:
            print(f"{Fore.YELLOW}第 {current_page}/{total_pages} 页{Style.RESET_ALL}\n")
        
        # 显示菜单项
        for i, item in enumerate(items, 1):
            print(f"{Fore.GREEN}{i:2}. {Fore.WHITE}{item}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}{'─'*60}{Style.RESET_ALL}")
        
        # 操作提示
        print(f"{Fore.CYAN}操作说明:{Style.RESET_ALL}")
        print(f"  • 输入数字选择菜单项")
        print(f"  • 输入 {Fore.RED}0{Style.RESET_ALL} 返回上级")
        print(f"  • 输入 {Fore.RED}q{Style.RESET_ALL} 退出程序")
        
        if total_pages > 1:
            print(f"  • 输入 {Fore.YELLOW}p{Style.RESET_ALL} 上一页")
            print(f"  • 输入 {Fore.YELLOW}n{Style.RESET_ALL} 下一页")
        
        print()
        
    def get_choice(self, min_choice: int = 0, max_choice: int = 10) -> str:
        """获取用户选择"""
        while True:
            try:
                choice = input(f"{Fore.GREEN}请输入选择 [{min_choice}-{max_choice}]: {Style.RESET_ALL}").strip().lower()
                
                if choice == 'q':
                    return 'quit'
                elif choice == 'p':
                    return 'prev'
                elif choice == 'n':
                    return 'next'
                elif choice.isdigit():
                    num = int(choice)
                    if min_choice <= num <= max_choice:
                        return choice
                    else:
                        print(f"{Fore.RED}错误: 请输入 {min_choice}-{max_choice} 之间的数字{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}错误: 请输入有效的数字{Style.RESET_ALL}")
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}检测到中断，正在退出...{Style.RESET_ALL}")
                return 'quit'
            except EOFError:
                print(f"\n{Fore.YELLOW}检测到EOF，正在退出...{Style.RESET_ALL}")
                return 'quit'
                
    def show_message(self, title: str, message: str, wait: bool = True):
        """显示消息"""
        self.clear_screen()
        self.print_header(title)
        
        # 显示消息
        lines = message.split('\n')
        for line in lines:
            print(f"  {line}")
        
        print(f"\n{Fore.YELLOW}{'─'*60}{Style.RESET_ALL}")
        
        if wait:
            input(f"\n{Fore.CYAN}按回车键继续...{Style.RESET_ALL}")
            
    def show_confirm(self, title: str, message: str) -> bool:
        """显示确认对话框"""
        self.clear_screen()
        self.print_header(title)
        
        print(f"  {message}\n")
        print(f"{Fore.YELLOW}{'─'*60}{Style.RESET_ALL}")
        
        while True:
            choice = input(f"{Fore.GREEN}确认吗？(y/n): {Style.RESET_ALL}").strip().lower()
            
            if choice in ['y', 'yes', '是', '确认']:
                return True
            elif choice in ['n', 'no', '否', '取消']:
                return False
            elif choice == 'q':
                return False
            else:
                print(f"{Fore.RED}请输入 y(是) 或 n(否){Style.RESET_ALL}")
                
    def main_menu(self):
        """主菜单"""
        while True:
            menu_items = [
                "运行负优化",
                "停止所有优化", 
                "查看系统状态",
                "配置设置",
                "关于nwtools"
            ]
            
            self.print_menu("nwtools 主菜单", menu_items)
            choice = self.get_choice(0, len(menu_items))
            
            if choice == 'quit':
                if self.running:
                    if self.show_confirm("确认退出", "有优化正在运行，确定要退出吗？"):
                        self.optimizer.stop_all()
                        break
                else:
                    break
            elif choice == '0':
                break
            elif choice == '1':
                self.optimization_menu()
            elif choice == '2':
                self.stop_optimization()
            elif choice == '3':
                self.show_status()
            elif choice == '4':
                self.config_menu()
            elif choice == '5':
                self.show_about()
                
    def optimization_menu(self):
        """优化菜单"""
        while True:
            menu_items = [
                "CPU优化",
                "内存优化",
                "磁盘优化", 
                "网络优化",
                "进程优化",
                "全面优化"
            ]
            
            self.print_menu("运行负优化", menu_items)
            choice = self.get_choice(0, len(menu_items))
            
            if choice in ['quit', '0']:
                break
            elif choice == '1':
                self.run_cpu_optimization()
            elif choice == '2':
                self.run_memory_optimization()
            elif choice == '3':
                self.run_disk_optimization()
            elif choice == '4':
                self.run_network_optimization()
            elif choice == '5':
                self.run_process_optimization()
            elif choice == '6':
                self.run_all_optimization()
                
    def run_cpu_optimization(self):
        """运行CPU优化"""
        intensity = self.select_intensity("CPU优化强度")
        if intensity is None:
            return
            
        try:
            self.optimizer.optimize_cpu(intensity=intensity)
            self.running = True
            self.show_message("成功", "CPU优化已启动！\n\n注意: 优化将无限期运行\n使用'停止所有优化'来停止。")
        except Exception as e:
            self.show_message("错误", f"运行CPU优化失败:\n{str(e)}")
                
    def run_memory_optimization(self):
        """运行内存优化"""
        # 选择内存大小
        size_choice = self.select_memory_size()
        if size_choice is None:
            return
            
        size_mb, intensity = size_choice
        
        try:
            self.optimizer.optimize_memory(size_mb=size_mb, intensity=intensity)
            self.running = True
            self.show_message("成功", f"内存优化已启动！\n分配大小: {size_mb}MB\n\n注意: 优化将无限期运行\n使用'停止所有优化'来停止。")
        except Exception as e:
            self.show_message("错误", f"运行内存优化失败:\n{str(e)}")
                
    def run_disk_optimization(self):
        """运行磁盘优化"""
        intensity = self.select_intensity("磁盘优化强度")
        if intensity is None:
            return
            
        try:
            self.optimizer.optimize_disk(intensity=intensity)
            self.running = True
            self.show_message("成功", "磁盘优化已启动！\n\n注意: 优化将无限期运行\n使用'停止所有优化'来停止。")
        except Exception as e:
            self.show_message("错误", f"运行磁盘优化失败:\n{str(e)}")
                
    def run_network_optimization(self):
        """运行网络优化"""
        intensity = self.select_intensity("网络优化强度")
        if intensity is None:
            return
            
        try:
            self.optimizer.optimize_network(intensity=intensity)
            self.running = True
            self.show_message("成功", "网络优化已启动！\n\n注意: 优化将无限期运行\n使用'停止所有优化'来停止。")
        except Exception as e:
            self.show_message("错误", f"运行网络优化失败:\n{str(e)}")
                
    def run_process_optimization(self):
        """运行进程优化"""
        intensity = self.select_intensity("进程优化强度")
        if intensity is None:
            return
            
        try:
            self.optimizer.optimize_process(intensity=intensity)
            self.running = True
            self.show_message("成功", "进程优化已启动！\n\n注意: 优化将无限期运行\n使用'停止所有优化'来停止。")
        except Exception as e:
            self.show_message("错误", f"运行进程优化失败:\n{str(e)}")
                
    def run_all_optimization(self):
        """运行全面优化"""
        intensity = self.select_intensity("全面优化强度")
        if intensity is None:
            return
            
        try:
            self.optimizer.optimize_all(intensity=intensity)
            self.running = True
            self.show_message("成功", "全面优化已启动！\n\n注意: 优化将无限期运行\n使用'停止所有优化'来停止。")
        except Exception as e:
            self.show_message("错误", f"运行全面优化失败:\n{str(e)}")
                
    def select_intensity(self, title: str) -> Optional[str]:
        """选择强度级别"""
        menu_items = [
            "低强度 - 轻度影响",
            "中等强度 - 明显影响", 
            "高强度 - 严重影响",
            "极限强度 - 最大影响"
        ]
        
        intensity_map = {
            '1': 'low',
            '2': 'medium',
            '3': 'high',
            '4': 'extreme'
        }
        
        self.print_menu(title, menu_items)
        choice = self.get_choice(0, len(menu_items))
        
        if choice in ['quit', '0']:
            return None
            
        return intensity_map.get(choice)
        
    def select_memory_size(self) -> Optional[tuple]:
        """选择内存大小"""
        menu_items = [
            "1024MB (低强度)",
            "4096MB (中等强度)",
            "8192MB (高强度)",
            "16384MB (狂暴强度)",
            "自定义大小"
        ]
        
        size_map = {
            '1': (1024, 'low'),
            '2': (4096, 'medium'),
            '3': (8192, 'high'),
            '4': (16384, 'extreme')
        }
        
        self.print_menu("选择内存大小", menu_items)
        choice = self.get_choice(0, len(menu_items))
        
        if choice in ['quit', '0']:
            return None
            
        if choice == '5':
            # 自定义大小
            while True:
                try:
                    custom_size = input(f"{Fore.GREEN}请输入内存大小(MB): {Style.RESET_ALL}").strip()
                    if custom_size.lower() == 'q':
                        return None
                    
                    size_mb = int(custom_size)
                    if size_mb <= 0:
                        print(f"{Fore.RED}错误: 内存大小必须大于0{Style.RESET_ALL}")
                        continue
                        
                    # 选择强度
                    intensity = self.select_intensity("自定义内存的强度")
                    if intensity is None:
                        return None
                        
                    return (size_mb, intensity)
                    
                except ValueError:
                    print(f"{Fore.RED}错误: 请输入有效的数字{Style.RESET_ALL}")
                except KeyboardInterrupt:
                    return None
                    
        return size_map.get(choice)
        
    def stop_optimization(self):
        """停止所有优化"""
        if not self.running:
            self.show_message("信息", "当前没有优化在运行。")
            return
            
        if self.show_confirm("确认", "确定要停止所有优化吗？"):
            self.optimizer.stop_all()
            self.running = False
            self.show_message("成功", "所有优化已停止！")
            
    def show_status(self):
        """显示系统状态"""
        try:
            status = self.optimizer.get_system_status()
            
            if "error" in status:
                self.show_message("错误", f"无法获取系统状态:\n{status['error']}")
                return
                
            status_text = f"""
系统状态:
──────────────
CPU使用率: {status['cpu_percent']}%
内存使用: {status['memory_used_mb']}MB / {status['memory_total_mb']}MB ({status['memory_percent']}%)
磁盘使用: {status['disk_used_gb']}GB / {status['disk_total_gb']}GB ({status['disk_percent']}%)
进程数量: {status['process_count']}

运行状态: {'正在运行' if status['is_running'] else '未运行'}
"""
            if status['is_running']:
                status_text += f"运行时间: {status['running_time']:.1f}秒\n"
                
            self.show_message("系统状态", status_text)
            
        except Exception as e:
            self.show_message("错误", f"获取系统状态失败:\n{str(e)}")
            
    def config_menu(self):
        """配置菜单"""
        while True:
            require_confirm = self.config.get('require_confirmation', True)
            auto_cleanup = self.config.get('auto_cleanup', True)
            max_memory = self.config.get('max_memory_mb', 2048)
            
            menu_items = [
                f"安全确认: {'开启' if require_confirm else '关闭'}",
                f"自动清理: {'开启' if auto_cleanup else '关闭'}",
                f"最大内存限制: {max_memory}MB",
                "保存配置"
            ]
            
            self.print_menu("配置设置", menu_items)
            choice = self.get_choice(0, len(menu_items))
            
            if choice in ['quit', '0']:
                break
            elif choice == '1':
                self.toggle_config('require_confirmation', "安全确认")
            elif choice == '2':
                self.toggle_config('auto_cleanup', "自动清理")
            elif choice == '3':
                self.set_memory_limit()
            elif choice == '4':
                save_config(self.config)
                self.show_message("成功", "配置已保存！")
                
    def toggle_config(self, key: str, name: str):
        """切换配置开关"""
        current = self.config.get(key, True)
        new_value = not current
        
        if self.show_confirm("确认", f"将{name}从{'开启' if current else '关闭'}改为{'开启' if new_value else '关闭'}？"):
            self.config[key] = new_value
            self.show_message("成功", f"{name}已{'开启' if new_value else '关闭'}")
            
    def set_memory_limit(self):
        """设置内存限制"""
        current = self.config.get('max_memory_mb', 2048)
        
        while True:
            try:
                new_limit = input(f"{Fore.GREEN}请输入最大内存限制(MB) [当前: {current}]: {Style.RESET_ALL}").strip()
                
                if new_limit.lower() == 'q':
                    return
                    
                new_limit = int(new_limit)
                if new_limit <= 0:
                    print(f"{Fore.RED}错误: 内存限制必须大于0{Style.RESET_ALL}")
                    continue
                    
                self.config['max_memory_mb'] = new_limit
                self.show_message("成功", f"内存限制已设置为 {new_limit}MB")
                break
                
            except ValueError:
                print(f"{Fore.RED}错误: 请输入有效的数字{Style.RESET_ALL}")
            except KeyboardInterrupt:
                return
                
    def show_about(self):
        """显示关于信息"""
        about_text = """
nwtools v1.0.0
──────────────
系统负优化工具

功能:
• CPU负优化
• 内存负优化  
• 磁盘负优化
• 网络负优化
• 进程负优化

作者: ruin321

⚠️ 警告:
仅在测试环境或虚拟机中使用！
"""
        self.show_message("关于 nwtools", about_text)
        
    def run(self):
        """运行TUI界面"""
        try:
            print(f"{Fore.CYAN}启动 nwtools 稳定TUI 界面...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}作者: ruin321{Style.RESET_ALL}")
            time.sleep(1)
            
            self.main_menu()
            
            print(f"\n{Fore.GREEN}TUI界面已关闭{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"\n{Fore.RED}TUI界面错误: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}程序异常退出{Style.RESET_ALL}")


def stable_tui_main():
    """稳定TUI主函数"""
    tui = StableTUI()
    tui.run()


if __name__ == "__main__":
    stable_tui_main()