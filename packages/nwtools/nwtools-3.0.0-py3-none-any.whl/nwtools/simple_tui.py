#!/usr/bin/env python3
"""
nwtools 简单TUI界面 - 纯Python实现
支持鼠标点击和键盘操作
"""

import sys
import curses
import time
from typing import List, Tuple, Optional
from enum import Enum

from .core import NegativeOptimizer, IntensityLevel
from .utils import load_config
from colorama import init, Fore, Style

# 初始化colorama
init(autoreset=True)

class MenuItem:
    """菜单项"""
    
    def __init__(self, text: str, action=None, submenu=None):
        self.text = text
        self.action = action  # 回调函数
        self.submenu = submenu  # 子菜单
        self.selected = False
        
class SimpleTUI:
    """简单TUI界面"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.optimizer = NegativeOptimizer()
        self.config = load_config()
        self.current_menu = []
        self.menu_history = []
        self.selected_index = 0
        self.running = False
        
        # 初始化curses
        curses.curs_set(0)  # 隐藏光标
        self.stdscr.keypad(True)  # 启用特殊键
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        
        # 颜色对
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # 标题
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # 选中项
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 普通项
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # 警告
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)  # 错误
        
        # 初始化主菜单
        self.init_main_menu()
        
    def init_main_menu(self):
        """初始化主菜单"""
        self.current_menu = [
            MenuItem("运行负优化", submenu=self.create_optimization_menu),
            MenuItem("停止所有优化", action=self.stop_optimization),
            MenuItem("查看系统状态", action=self.show_status),
            MenuItem("配置设置", submenu=self.create_config_menu),
            MenuItem("关于nwtools", action=self.show_about),
            MenuItem("退出", action=self.exit_program)
        ]
        self.selected_index = 0
        
    def create_optimization_menu(self):
        """创建优化菜单"""
        return [
            MenuItem("CPU优化", action=lambda: self.run_optimization("cpu")),
            MenuItem("内存优化", action=lambda: self.run_optimization("memory")),
            MenuItem("磁盘优化", action=lambda: self.run_optimization("disk")),
            MenuItem("网络优化", action=lambda: self.run_optimization("network")),
            MenuItem("进程优化", action=lambda: self.run_optimization("process")),
            MenuItem("全面优化", action=lambda: self.run_optimization("all")),
            MenuItem("返回主菜单", action=self.back_to_main)
        ]
        
    def create_config_menu(self):
        """创建配置菜单"""
        return [
            MenuItem(f"安全确认: {'开启' if self.config.get('require_confirmation', True) else '关闭'}",
                    action=self.toggle_confirmation),
            MenuItem(f"自动清理: {'开启' if self.config.get('auto_cleanup', True) else '关闭'}",
                    action=self.toggle_cleanup),
            MenuItem("返回主菜单", action=self.back_to_main)
        ]
        
    def draw_menu(self):
        """绘制菜单"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        # 绘制标题
        title = "nwtools TUI 界面"
        title_x = (width - len(title)) // 2
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(1, title_x, title)
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        
        # 绘制分隔线
        self.stdscr.addstr(2, 0, "=" * width)
        
        # 绘制菜单项
        start_y = 4
        for i, item in enumerate(self.current_menu):
            y = start_y + i
            
            # 检查是否在屏幕范围内
            if y >= height - 2:
                break
                
            # 准备文本
            text = f" {item.text} "
            if item.selected:
                text = f"> {item.text} <"
                
            # 计算位置
            x = (width - len(text)) // 2
            
            # 绘制菜单项
            if i == self.selected_index:
                self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                self.stdscr.addstr(y, x, text)
                self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.attron(curses.color_pair(3))
                self.stdscr.addstr(y, x, text)
                self.stdscr.attroff(curses.color_pair(3))
        
        # 绘制说明
        instructions = [
            "使用说明:",
            "• 鼠标点击选择项目",
            "• 方向键上下导航",
            "• 回车键确认选择",
            "• Q键退出"
        ]
        
        instr_y = height - len(instructions) - 1
        for i, instr in enumerate(instructions):
            if instr_y + i < height:
                self.stdscr.addstr(instr_y + i, 2, instr)
        
        self.stdscr.refresh()
        
    def show_message(self, title: str, message: str):
        """显示消息对话框"""
        height, width = self.stdscr.getmaxyx()
        
        # 计算对话框大小
        dialog_height = min(15, height - 4)
        dialog_width = min(60, width - 4)
        
        # 计算位置
        start_y = (height - dialog_height) // 2
        start_x = (width - dialog_width) // 2
        
        # 绘制对话框边框
        self.stdscr.attron(curses.color_pair(1))
        for y in range(start_y, start_y + dialog_height):
            for x in range(start_x, start_x + dialog_width):
                if y == start_y or y == start_y + dialog_height - 1:
                    self.stdscr.addch(y, x, curses.ACS_HLINE)
                elif x == start_x or x == start_x + dialog_width - 1:
                    self.stdscr.addch(y, x, curses.ACS_VLINE)
        
        # 绘制角落
        self.stdscr.addch(start_y, start_x, curses.ACS_ULCORNER)
        self.stdscr.addch(start_y, start_x + dialog_width - 1, curses.ACS_URCORNER)
        self.stdscr.addch(start_y + dialog_height - 1, start_x, curses.ACS_LLCORNER)
        self.stdscr.addch(start_y + dialog_height - 1, start_x + dialog_width - 1, curses.ACS_LRCORNER)
        self.stdscr.attroff(curses.color_pair(1))
        
        # 绘制标题
        title_x = start_x + (dialog_width - len(title)) // 2
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(start_y, title_x, f" {title} ")
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        
        # 绘制消息
        lines = message.split('\n')
        for i, line in enumerate(lines):
            if i >= dialog_height - 4:
                break
            line_x = start_x + (dialog_width - len(line)) // 2
            self.stdscr.addstr(start_y + 2 + i, line_x, line)
        
        # 绘制确定按钮
        ok_text = " 确定 (点击或按任意键) "
        ok_x = start_x + (dialog_width - len(ok_text)) // 2
        ok_y = start_y + dialog_height - 3
        
        self.stdscr.attron(curses.color_pair(2))
        self.stdscr.addstr(ok_y, ok_x, ok_text)
        self.stdscr.attroff(curses.color_pair(2))
        
        self.stdscr.refresh()
        
        # 等待用户响应
        while True:
            key = self.stdscr.getch()
            if key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, _ = curses.getmouse()
                    if (ok_y <= my < ok_y + 1 and 
                        ok_x <= mx < ok_x + len(ok_text)):
                        break
                except:
                    pass
            elif key != -1:
                break
                
    def show_confirm(self, title: str, message: str) -> bool:
        """显示确认对话框"""
        height, width = self.stdscr.getmaxyx()
        
        dialog_height = min(12, height - 4)
        dialog_width = min(50, width - 4)
        
        start_y = (height - dialog_height) // 2
        start_x = (width - dialog_width) // 2
        
        # 绘制对话框
        self.stdscr.attron(curses.color_pair(1))
        for y in range(start_y, start_y + dialog_height):
            for x in range(start_x, start_x + dialog_width):
                if y == start_y or y == start_y + dialog_height - 1:
                    self.stdscr.addch(y, x, curses.ACS_HLINE)
                elif x == start_x or x == start_x + dialog_width - 1:
                    self.stdscr.addch(y, x, curses.ACS_VLINE)
        
        self.stdscr.addch(start_y, start_x, curses.ACS_ULCORNER)
        self.stdscr.addch(start_y, start_x + dialog_width - 1, curses.ACS_URCORNER)
        self.stdscr.addch(start_y + dialog_height - 1, start_x, curses.ACS_LLCORNER)
        self.stdscr.addch(start_y + dialog_height - 1, start_x + dialog_width - 1, curses.ACS_LRCORNER)
        self.stdscr.attroff(curses.color_pair(1))
        
        # 标题
        title_x = start_x + (dialog_width - len(title)) // 2
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(start_y, title_x, f" {title} ")
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        
        # 消息
        lines = message.split('\n')
        for i, line in enumerate(lines):
            if i >= dialog_height - 5:
                break
            line_x = start_x + (dialog_width - len(line)) // 2
            self.stdscr.addstr(start_y + 2 + i, line_x, line)
        
        # 按钮
        yes_text = " 是(Y) "
        no_text = " 否(N) "
        
        buttons_y = start_y + dialog_height - 3
        yes_x = start_x + dialog_width // 2 - len(yes_text) - 2
        no_x = start_x + dialog_width // 2 + 2
        
        selected_button = 0  # 0:是, 1:否
        
        while True:
            # 绘制按钮
            if selected_button == 0:
                self.stdscr.attron(curses.color_pair(2))
                self.stdscr.addstr(buttons_y, yes_x, yes_text)
                self.stdscr.attroff(curses.color_pair(2))
                
                self.stdscr.attron(curses.color_pair(3))
                self.stdscr.addstr(buttons_y, no_x, no_text)
                self.stdscr.attroff(curses.color_pair(3))
            else:
                self.stdscr.attron(curses.color_pair(3))
                self.stdscr.addstr(buttons_y, yes_x, yes_text)
                self.stdscr.attroff(curses.color_pair(3))
                
                self.stdscr.attron(curses.color_pair(2))
                self.stdscr.addstr(buttons_y, no_x, no_text)
                self.stdscr.attroff(curses.color_pair(2))
            
            self.stdscr.refresh()
            
            # 获取输入
            key = self.stdscr.getch()
            
            if key == ord('y') or key == ord('Y'):
                return True
            elif key == ord('n') or key == ord('N'):
                return False
            elif key == curses.KEY_LEFT or key == curses.KEY_RIGHT:
                selected_button = 1 - selected_button  # 切换按钮
            elif key == ord('\n') or key == ord(' '):  # 回车或空格
                return selected_button == 0
            elif key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, _ = curses.getmouse()
                    if (buttons_y <= my < buttons_y + 1):
                        if yes_x <= mx < yes_x + len(yes_text):
                            return True
                        elif no_x <= mx < no_x + len(no_text):
                            return False
                except:
                    pass
            elif key == 27:  # ESC
                return False
                
    def run_optimization(self, opt_type: str):
        """运行优化"""
        intensity_map = {
            "low": "低强度",
            "medium": "中等强度", 
            "high": "高强度",
            "extreme": "极限强度"
        }
        
        # 选择强度
        intensity_choice = self.show_choice_dialog(
            "选择强度",
            "请选择优化强度:",
            ["低强度", "中等强度", "高强度", "极限强度"]
        )
        
        if intensity_choice is None:
            return
            
        intensity = list(intensity_map.keys())[intensity_choice]
        
        # 确认
        if self.show_confirm("确认", f"确定要运行{opt_type}优化吗？\n强度: {intensity_map[intensity]}"):
            try:
                if opt_type == "cpu":
                    self.optimizer.optimize_cpu(intensity=intensity)
                elif opt_type == "memory":
                    # 对于内存优化，需要选择大小
                    size_choice = self.show_choice_dialog(
                        "内存大小",
                        "选择内存大小:",
                        ["256MB", "512MB", "1024MB", "2048MB"]
                    )
                    if size_choice is not None:
                        sizes = [256, 512, 1024, 2048]
                        self.optimizer.optimize_memory(size_mb=sizes[size_choice], intensity=intensity)
                    else:
                        return
                elif opt_type == "disk":
                    self.optimizer.optimize_disk(intensity=intensity)
                elif opt_type == "network":
                    self.optimizer.optimize_network(intensity=intensity)
                elif opt_type == "process":
                    self.optimizer.optimize_process(intensity=intensity)
                elif opt_type == "all":
                    self.optimizer.optimize_all(intensity=intensity)
                    
                self.running = True
                self.show_message("成功", f"{opt_type}优化已启动！\n\n使用'停止所有优化'来停止。")
            except Exception as e:
                self.show_message("错误", f"运行优化失败: {str(e)}")
                
    def show_choice_dialog(self, title: str, message: str, choices: List[str]) -> Optional[int]:
        """显示选择对话框"""
        height, width = self.stdscr.getmaxyx()
        
        dialog_height = min(15, height - 4)
        dialog_width = min(50, width - 4)
        
        start_y = (height - dialog_height) // 2
        start_x = (width - dialog_width) // 2
        
        # 绘制对话框
        self.stdscr.attron(curses.color_pair(1))
        for y in range(start_y, start_y + dialog_height):
            for x in range(start_x, start_x + dialog_width):
                if y == start_y or y == start_y + dialog_height - 1:
                    self.stdscr.addch(y, x, curses.ACS_HLINE)
                elif x == start_x or x == start_x + dialog_width - 1:
                    self.stdscr.addch(y, x, curses.ACS_VLINE)
        
        self.stdscr.addch(start_y, start_x, curses.ACS_ULCORNER)
        self.stdscr.addch(start_y, start_x + dialog_width - 1, curses.ACS_URCORNER)
        self.stdscr.addch(start_y + dialog_height - 1, start_x, curses.ACS_LLCORNER)
        self.stdscr.addch(start_y + dialog_height - 1, start_x + dialog_width - 1, curses.ACS_LRCORNER)
        self.stdscr.attroff(curses.color_pair(1))
        
        # 标题
        title_x = start_x + (dialog_width - len(title)) // 2
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(start_y, title_x, f" {title} ")
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        
        # 消息
        msg_x = start_x + (dialog_width - len(message)) // 2
        self.stdscr.addstr(start_y + 2, msg_x, message)
        
        # 选项
        selected_index = 0
        while True:
            # 绘制选项
            for i, choice in enumerate(choices):
                y = start_y + 4 + i
                if y >= start_y + dialog_height - 2:
                    break
                    
                text = f" {choice} "
                if i == selected_index:
                    text = f"> {choice} <"
                    
                choice_x = start_x + (dialog_width - len(text)) // 2
                
                if i == selected_index:
                    self.stdscr.attron(curses.color_pair(2))
                    self.stdscr.addstr(y, choice_x, text)
                    self.stdscr.attroff(curses.color_pair(2))
                else:
                    self.stdscr.attron(curses.color_pair(3))
                    self.stdscr.addstr(y, choice_x, text)
                    self.stdscr.attroff(curses.color_pair(3))
            
            # 确定按钮
            ok_text = " 确定 "
            ok_x = start_x + (dialog_width - len(ok_text)) // 2
            ok_y = start_y + dialog_height - 3
            
            self.stdscr.attron(curses.color_pair(2) if selected_index == len(choices) else curses.color_pair(3))
            self.stdscr.addstr(ok_y, ok_x, ok_text)
            self.stdscr.attroff(curses.color_pair(2) if selected_index == len(choices) else curses.color_pair(3))
            
            self.stdscr.refresh()
            
            # 获取输入
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP:
                selected_index = max(0, selected_index - 1)
            elif key == curses.KEY_DOWN:
                selected_index = min(len(choices), selected_index + 1)
            elif key == ord('\n') or key == ord(' '):
                if selected_index == len(choices):
                    return None  # 取消
                return selected_index
            elif key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, _ = curses.getmouse()
                    # 检查选项点击
                    for i in range(len(choices)):
                        y = start_y + 4 + i
                        if y <= my < y + 1:
                            text = f" {choices[i]} "
                            choice_x = start_x + (dialog_width - len(text)) // 2
                            if choice_x <= mx < choice_x + len(text):
                                return i
                    # 检查确定按钮点击
                    if ok_y <= my < ok_y + 1 and ok_x <= mx < ok_x + len(ok_text):
                        return selected_index if selected_index < len(choices) else None
                except:
                    pass
            elif key == 27:  # ESC
                return None
                
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
        
    def toggle_confirmation(self):
        """切换安全确认"""
        current = self.config.get('require_confirmation', True)
        self.config['require_confirmation'] = not current
        self.show_message("成功", f"安全确认已{'开启' if not current else '关闭'}")
        
    def toggle_cleanup(self):
        """切换自动清理"""
        current = self.config.get('auto_cleanup', True)
        self.config['auto_cleanup'] = not current
        self.show_message("成功", f"自动清理已{'开启' if not current else '关闭'}")
        
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

界面特点:
• 纯Python实现
• 支持鼠标点击
• 支持键盘操作
• 图形化对话框

⚠️ 警告:
仅在测试环境或虚拟机中使用！
"""
        self.show_message("关于 nwtools", about_text)
        
    def back_to_main(self):
        """返回主菜单"""
        self.init_main_menu()
        
    def exit_program(self):
        """退出程序"""
        if self.running:
            if self.show_confirm("确认", "有优化正在运行，确定要退出吗？"):
                self.optimizer.stop_all()
                raise SystemExit
        else:
            raise SystemExit
            
    def handle_mouse_click(self, y: int, x: int):
        """处理鼠标点击"""
        height, width = self.stdscr.getmaxyx()
        start_y = 4
        menu_height = len(self.current_menu)
        
        # 检查是否点击了菜单项
        for i in range(menu_height):
            item_y = start_y + i
            if item_y >= height - 2:
                break
                
            item = self.current_menu[i]
            text = f" {item.text} "
            if item.selected:
                text = f"> {item.text} <"
                
            item_x = (width - len(text)) // 2
            
            if (item_y <= y < item_y + 1 and 
                item_x <= x < item_x + len(text)):
                self.selected_index = i
                self.execute_menu_item(item)
                return True
                
        return False
        
    def execute_menu_item(self, item: MenuItem):
        """执行菜单项"""
        if item.action:
            item.action()
        elif item.submenu:
            self.menu_history.append((self.current_menu, self.selected_index))
            self.current_menu = item.submenu()
            self.selected_index = 0
            
    def run(self):
        """运行TUI主循环"""
        while True:
            try:
                self.draw_menu()
                key = self.stdscr.getch()
                
                if key == curses.KEY_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                elif key == curses.KEY_DOWN:
                    self.selected_index = min(len(self.current_menu) - 1, self.selected_index + 1)
                elif key == ord('\n') or key == ord(' '):  # 回车或空格
                    if self.current_menu:
                        self.execute_menu_item(self.current_menu[self.selected_index])
                elif key == curses.KEY_MOUSE:
                    try:
                        _, x, y, _, _ = curses.getmouse()
                        self.handle_mouse_click(y, x)
                    except:
                        pass
                elif key == ord('q') or key == ord('Q') or key == 27:  # Q或ESC
                    self.exit_program()
                elif key == ord('b') or key == ord('B'):  # 返回
                    if self.menu_history:
                        self.current_menu, self.selected_index = self.menu_history.pop()
                        
            except SystemExit:
                break
            except Exception as e:
                self.show_message("错误", f"程序错误: {str(e)}")
                break


def simple_tui_main():
    """简单TUI主函数"""
    try:
        # 检查终端大小
        import shutil
        size = shutil.get_terminal_size()
        if size.columns < 40 or size.lines < 20:
            print(f"{Fore.RED}错误: 终端窗口太小！")
            print(f"{Fore.YELLOW}请调整终端大小至少为 40x20")
            return
            
        print(f"{Fore.CYAN}启动 nwtools 简单TUI 界面...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}支持鼠标点击和键盘操作{Style.RESET_ALL}")
        print(f"{Fore.WHITE}按任意键继续...{Style.RESET_ALL}")
        input()
        
        curses.wrapper(lambda stdscr: SimpleTUI(stdscr).run())
        
        print(f"{Fore.GREEN}TUI界面已关闭{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}启动TUI失败: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}请确保终端支持curses和鼠标{Style.RESET_ALL}")


if __name__ == "__main__":
    simple_tui_main()