# nwtools 🐌

一个用于"负优化"你的Windows/Linux系统性能的Python包。这个包主要用于演示、测试和教育目的，展示如何降低系统性能的各种方法。

**警告：请谨慎使用！仅在测试环境或虚拟机中使用！**

## 功能特性

- **CPU负优化**：创建大量计算密集型任务消耗CPU资源
- **内存负优化**：分配大量内存但不释放
- **磁盘负优化**：频繁读写磁盘，创建大量临时文件
- **网络负优化**：发送大量网络请求，消耗带宽
- **进程负优化**：创建大量子进程
- **UI干扰**：干扰用户界面（如闪烁窗口、移动鼠标等）
- **安全模式**：所有操作都是可逆的，有安全限制

## 安装

```bash
pip install nwtools
```

或者从源代码安装：

```bash
git clone https://github.com/yourusername/nwtools.git
cd nwtools
pip install -e .
```

## 使用方法

### 命令行界面

```bash
# 显示帮助信息
nwtools --help

# 运行所有负优化功能（默认强度）
nwtools run

# 运行特定强度的负优化
nwtools run --intensity high

# 只运行CPU负优化
nwtools cpu --duration 30

# 运行内存负优化
nwtools memory --size 1024

# 运行磁盘负优化
nwtools disk --files 100

# 运行网络负优化
nwtools network --requests 50

# 运行进程负优化
nwtools process --count 20

# 停止所有负优化任务
nwtools stop

# 显示系统状态
nwtools status
```

### Python API

```python
from nwtools import NegativeOptimizer

# 创建优化器实例
optimizer = NegativeOptimizer()

# 运行CPU负优化
optimizer.optimize_cpu(duration=30, intensity="medium")

# 运行内存负优化
optimizer.optimize_memory(size_mb=512, duration=60)

# 运行磁盘负优化
optimizer.optimize_disk(num_files=50, file_size_kb=1024)

# 运行网络负优化
optimizer.optimize_network(num_requests=100, target_url="http://example.com")

# 运行进程负优化
optimizer.optimize_process(num_processes=10)

# 停止所有优化
optimizer.stop_all()

# 获取系统状态
status = optimizer.get_system_status()
print(f"CPU使用率: {status['cpu_percent']}%")
print(f"内存使用率: {status['memory_percent']}%")
```

## TUI界面（稳定跨平台）

nwtools提供了三种TUI界面，**推荐使用稳定TUI**：

### 🎯 1. 稳定TUI界面（推荐 - 跨平台稳定）
```bash
# 运行稳定TUI界面
nwtools-stable-tui
```
**特点**：
- ✅ 纯Python实现，无任何外部依赖
- ✅ 跨平台支持（Windows/Linux/Termux/macOS）
- ✅ 不会崩溃，稳定可靠
- ✅ 数字选择菜单，操作简单
- ✅ 支持所有nwtools功能

### 2. 基于dialog的TUI界面（仅Linux）
```bash
# 安装dialog工具
pkg install dialog  # Termux
sudo apt install dialog  # Ubuntu/Debian

# 运行TUI界面
nwtools-tui
```
**特点**：
- 使用dialog工具创建图形对话框
- 支持真正的鼠标点击
- ❌ Windows不支持

### 3. 简单TUI界面（实验性）
```bash
# 运行简单TUI界面
nwtools-simple-tui
```
**特点**：
- 使用curses库
- ❌ 在Termux上可能不稳定
- ❌ 在Windows上需要额外配置

**推荐使用稳定TUI**，因为它：
1. 在所有平台上都能工作
2. 不会崩溃
3. 无需安装额外工具
4. 操作简单直观

## 安全特性

1. **资源限制**：默认有资源使用上限
2. **超时保护**：所有操作都有超时限制
3. **可逆操作**：所有创建的文件和进程都可以清理
4. **确认提示**：危险操作前需要确认
5. **强度控制**：可以控制负优化的强度

## 配置

创建配置文件 `~/.nwtools/config.yaml`：

```yaml
defaults:
  intensity: medium
  duration: 60
  auto_cleanup: true
  
limits:
  max_cpu_percent: 80
  max_memory_mb: 2048
  max_disk_files: 100
  max_processes: 20
  
safety:
  require_confirmation: true
  max_total_duration: 300
```

## 许可证

MIT License

## 免责声明

本软件仅供测试、演示和教育目的使用。作者不对使用本软件造成的任何损害负责。请勿在生产环境或重要系统上使用。

**使用风险自负！**