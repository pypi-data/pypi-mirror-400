#!/usr/bin/env python3
"""
nwtools TUI界面 - 基于dialog的图形界面
支持鼠标点击操作，无需键盘输入
"""

import os
import sys
import subprocess
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from .core import NegativeOptimizer, IntensityLevel
from .utils import load_config, save_config
from colorama import init, Fore, Style

# 初始化colorama
init(autoreset=True)

class NWToolsTUI:
    """nwtools TUI界面类"""
    
    def __init__(self):
        self.optimizer = NegativeOptimizer()
        self.config = load_config()
        self.running = False
        
    def run_dialog(self, dialog_type: str, title: str, text: str, 
                  height: int = 15, width: int = 60, 
                  options: Optional[List[str]] = None,
                  menu_items: Optional[List[tuple]] = None) -> str:
        """
        运行dialog命令
        
        Args:
            dialog_type: dialog类型 (msgbox, menu, checklist, etc.)
            title: 对话框标题
            text: 对话框文本
            height: 高度
            width: 宽度
            options: 额外选项
            menu_items: 菜单项列表 [(标签, 描述)]
            
        Returns:
            用户选择的结果
        """
        cmd = ["dialog", "--title", title, "--" + dialog_type, text, 
               str(height), str(width)]
        
        if options:
            cmd.extend(options)
            
        if menu_items:
            for tag, item in menu_items:
                cmd.append(tag)
                cmd.append(item)
                
        try:
            result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
            return result.stderr.strip()
        except Exception as e:
            print(f"{Fore.RED}[TUI错误] 无法运行dialog: {e}")
            return ""
            
    def show_message(self, title: str, message: str):
        """显示消息对话框"""
        self.run_dialog("msgbox", title, message)
        
    def show_menu(self, title: str, text: str, menu_items: List[tuple]) -> str:
        """显示菜单对话框"""
        return self.run_dialog("menu", title, text, menu_items=menu_items)
        
    def show_yesno(self, title: str, text: str) -> bool:
        """显示是/否对话框"""
        result = self.run_dialog("yesno", title, text, height=10, width=40)
        return result == "0"  # 0表示是，1表示否
        
    def show_checklist(self, title: str, text: str, items: List[tuple]) -> List[str]:
        """显示复选框列表"""
        result = self.run_dialog("checklist", title, text, menu_items=items)
        return result.split() if result else []
        
    def show_gauge(self, title: str, text: str, percent: int):
        """显示进度条"""
        # 使用子进程显示进度条
        cmd = ["dialog", "--title", title, "--gauge", text, "10", "70", str(percent)]
        subprocess.run(cmd)
        
    def main_menu(self):
        """主菜单"""
        while True:
            choice = self.show_menu(
                "nwtools - 主菜单",
                "请选择操作（使用鼠标点击或方向键选择）:",
                [
                    ("1", "运行负优化"),
                    ("2", "停止所有优化"),
                    ("3", "查看系统状态"),
                    ("4", "配置设置"),
                    ("5", "关于nwtools"),
                    ("6", "退出")
                ]
            )
            
            if not choice:
                break
                
            if choice == "1":
                self.run_optimization_menu()
            elif choice == "2":
                self.stop_optimization()
            elif choice == "3":
                self.show_status()
            elif choice == "4":
                self.config_menu()
            elif choice == "5":
                self.show_about()
            elif choice == "6":
                if self.running:
                    if self.show_yesno("确认", "有优化正在运行，确定要退出吗？"):
                        self.optimizer.stop_all()
                        break
                else:
                    break
                    
    def run_optimization_menu(self):
        """运行优化菜单"""
        while True:
            choice = self.show_menu(
                "运行负优化",
                "选择要运行的优化类型:",
                [
                    ("1", "CPU优化"),
                    ("2", "内存优化"),
                    ("3", "磁盘优化"),
                    ("4", "网络优化"),
                    ("5", "进程优化"),
                    ("6", "全面优化"),
                    ("7", "返回主菜单")
                ]
            )
            
            if not choice or choice == "7":
                break
                
            if choice == "1":
                self.run_cpu_optimization()
            elif choice == "2":
                self.run_memory_optimization()
            elif choice == "3":
                self.run_disk_optimization()
            elif choice == "4":
                self.run_network_optimization()
            elif choice == "5":
                self.run_process_optimization()
            elif choice == "6":
                self.run_all_optimization()
                
    def run_cpu_optimization(self):
        """运行CPU优化"""
        # 选择强度
        intensity = self.select_intensity("CPU优化强度")
        if not intensity:
            return
            
        # 确认
        if self.show_yesno("确认", f"确定要运行CPU优化吗？\n强度: {intensity}"):
            self.optimizer.optimize_cpu(intensity=intensity)
            self.running = True
            self.show_message("成功", "CPU优化已启动！\n\n使用'停止所有优化'来停止。")
            
    def run_memory_optimization(self):
        """运行内存优化"""
        # 选择强度或自定义大小
        choice = self.show_menu(
            "内存优化",
            "选择内存大小:",
            [
                ("1", "低强度 (256MB)"),
                ("2", "中等强度 (512MB)"),
                ("3", "高强度 (1024MB)"),
                ("4", "自定义大小"),
                ("5", "返回")
            ]
        )
        
        if not choice or choice == "5":
            return
            
        size_mb = None
        if choice == "1":
            size_mb = 256
            intensity = "low"
        elif choice == "2":
            size_mb = 512
            intensity = "medium"
        elif choice == "3":
            size_mb = 1024
            intensity = "high"
        elif choice == "4":
            # 输入自定义大小
            result = subprocess.run(
                ["dialog", "--title", "自定义内存大小", "--inputbox", 
                 "请输入内存大小(MB):", "10", "40", "512"],
                stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                try:
                    size_mb = int(result.stderr.strip())
                    intensity = "custom"
                except ValueError:
                    self.show_message("错误", "请输入有效的数字！")
                    return
            else:
                return
                
        # 确认
        if self.show_yesno("确认", f"确定要运行内存优化吗？\n大小: {size_mb}MB"):
            self.optimizer.optimize_memory(size_mb=size_mb, intensity=intensity)
            self.running = True
            self.show_message("成功", f"内存优化已启动！\n分配大小: {size_mb}MB\n\n使用'停止所有优化'来停止。")
            
    def run_disk_optimization(self):
        """运行磁盘优化"""
        # 选择强度
        intensity = self.select_intensity("磁盘优化强度")
        if not intensity:
            return
            
        # 确认
        if self.show_yesno("确认", f"确定要运行磁盘优化吗？\n强度: {intensity}"):
            self.optimizer.optimize_disk(intensity=intensity)
            self.running = True
            self.show_message("成功", "磁盘优化已启动！\n\n使用'停止所有优化'来停止。")
            
    def run_network_optimization(self):
        """运行网络优化"""
        # 选择强度
        intensity = self.select_intensity("网络优化强度")
        if not intensity:
            return
            
        # 确认
        if self.show_yesno("确认", f"确定要运行网络优化吗？\n强度: {intensity}"):
            self.optimizer.optimize_network(intensity=intensity)
            self.running = True
            self.show_message("成功", "网络优化已启动！\n\n使用'停止所有优化'来停止。")
            
    def run_process_optimization(self):
        """运行进程优化"""
        # 选择强度
        intensity = self.select_intensity("进程优化强度")
        if not intensity:
            return
            
        # 确认
        if self.show_yesno("确认", f"确定要运行进程优化吗？\n强度: {intensity}"):
            self.optimizer.optimize_process(intensity=intensity)
            self.running = True
            self.show_message("成功", "进程优化已启动！\n\n使用'停止所有优化'来停止。")
            
    def run_all_optimization(self):
        """运行全面优化"""
        # 选择强度
        intensity = self.select_intensity("全面优化强度")
        if not intensity:
            return
            
        # 确认
        if self.show_yesno("确认", f"确定要运行全面优化吗？\n强度: {intensity}\n\n这将同时运行所有优化功能！"):
            self.optimizer.optimize_all(intensity=intensity)
            self.running = True
            self.show_message("成功", "全面优化已启动！\n\n使用'停止所有优化'来停止。")
            
    def select_intensity(self, title: str) -> Optional[str]:
        """选择强度级别"""
        choice = self.show_menu(
            title,
            "选择优化强度:",
            [
                ("low", "低强度 - 轻度影响"),
                ("medium", "中等强度 - 明显影响"),
                ("high", "高强度 - 严重影响"),
                ("extreme", "极限强度 - 最大影响")
            ]
        )
        return choice
        
    def stop_optimization(self):
        """停止所有优化"""
        if not self.running:
            self.show_message("信息", "当前没有优化在运行。")
            return
            
        if self.show_yesno("确认", "确定要停止所有优化吗？"):
            self.optimizer.stop_all()
            self.running = False
            self.show_message("成功", "所有优化已停止！")
            
    def show_status(self):
        """显示系统状态"""
        status = self.optimizer.get_system_status()
        
        if "error" in status:
            self.show_message("错误", f"无法获取系统状态: {status['error']}")
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
        
    def config_menu(self):
        """配置菜单"""
        while True:
            choice = self.show_menu(
                "配置设置",
                "选择要修改的配置:",
                [
                    ("1", "安全确认: " + ("开启" if self.config.get('require_confirmation', True) else "关闭")),
                    ("2", "自动清理: " + ("开启" if self.config.get('auto_cleanup', True) else "关闭")),
                    ("3", "最大内存限制: " + str(self.config.get('max_memory_mb', 2048)) + "MB"),
                    ("4", "保存配置"),
                    ("5", "返回主菜单")
                ]
            )
            
            if not choice or choice == "5":
                break
                
            if choice == "1":
                self.toggle_config('require_confirmation', "安全确认")
            elif choice == "2":
                self.toggle_config('auto_cleanup', "自动清理")
            elif choice == "3":
                self.set_memory_limit()
            elif choice == "4":
                save_config(self.config)
                self.show_message("成功", "配置已保存！")
                
    def toggle_config(self, key: str, name: str):
        """切换配置开关"""
        current = self.config.get(key, True)
        new_value = not current
        
        if self.show_yesno("确认", f"将{name}从{'开启' if current else '关闭'}改为{'开启' if new_value else '关闭'}？"):
            self.config[key] = new_value
            self.show_message("成功", f"{name}已{'开启' if new_value else '关闭'}")
            
    def set_memory_limit(self):
        """设置内存限制"""
        current = self.config.get('max_memory_mb', 2048)
        
        result = subprocess.run(
            ["dialog", "--title", "设置内存限制", "--inputbox", 
             f"请输入最大内存限制(MB):\n当前: {current}MB", "10", "40", str(current)],
            stderr=subprocess.PIPE, text=True
        )
        
        if result.returncode == 0:
            try:
                new_limit = int(result.stderr.strip())
                if new_limit > 0:
                    self.config['max_memory_mb'] = new_limit
                    self.show_message("成功", f"内存限制已设置为 {new_limit}MB")
                else:
                    self.show_message("错误", "内存限制必须大于0！")
            except ValueError:
                self.show_message("错误", "请输入有效的数字！")
                
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

特点:
• 图形化界面 (TUI)
• 鼠标点击操作
• 安全确认机制
• 资源限制保护

⚠️ 警告:
仅在测试环境或虚拟机中使用！
"""
        self.show_message("关于 nwtools", about_text)
        
    def run(self):
        """运行TUI界面"""
        try:
            # 检查dialog是否可用
            subprocess.run(["dialog", "--version"], capture_output=True, check=True)
            self.main_menu()
        except Exception as e:
            print(f"{Fore.RED}[错误] 无法启动TUI界面: {e}")
            print(f"{Fore.YELLOW}请确保已安装dialog工具:")
            print(f"{Fore.WHITE}  Termux: pkg install dialog")
            print(f"{Fore.WHITE}  Ubuntu/Debian: sudo apt install dialog")
            print(f"{Fore.WHITE}  CentOS/RHEL: sudo yum install dialog")


def main():
    """TUI主函数"""
    print(f"{Fore.CYAN}启动 nwtools TUI 界面...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}使用鼠标点击或方向键操作{Style.RESET_ALL}")
    
    tui = NWToolsTUI()
    tui.run()
    
    print(f"{Fore.GREEN}TUI界面已关闭{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
