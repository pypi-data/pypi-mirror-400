# trump-pip

[English](#idk) | [中文](#你知道吗 其实你可以往下滑滑呢)

---

## English

A pip-like tool with Trump policy simulations. Sometimes fast, sometimes slow, always unpredictable!

### Installation

Install from PyPI:

```bash
pip install trump-pip
```

### Usage

After installation, use `tpip` command:

```bash
tpip install package_name
```

### Features

- Multi-language support (Chinese, English, Japanese, Korean)
- Trump policy simulations:
  - 60% chance: Tax cuts slow down your download
  - 30% chance: Tax increases speed up your download
  - 2% chance: Trump gets angry and cancels your download (may even close your terminal or system!)
- Export control system (TEL - Trump Export License):
  - AI package restriction on Chinese systems
  - Export license generation and validation
  - Hardware binding and digital signatures
  - Installation quota management

### Examples

```bash
# Install a package with Trump simulations
tpip install requests

# List installed packages
tpip list

# Test the Trump angry scenario
tpip --test-trump-angry

# Show about information
tpip --about

# Show language information
tpip --language

# Trump Export License (TEL) commands
tpip --tel help                    # Show tel help
tpip --tel compliance              # Check system compliance
tpip --tel generate --applicant "My Company" --packages tensorflow,pytorch  # Generate license
tpip --tel list                    # List all licenses
tpip --tel check --package tensorflow  # Check license for a package

# Or use tel command directly (after installation)
tel help
tel compliance
tel generate --applicant "My Company" --packages tensorflow,pytorch
tel list
tel check --package tensorflow
```

### Trump Export License (TEL)

TEL is a simplified export license system that simulates Trump's export control policies for AI packages:

#### Key Features:
- **AI Package Detection**: Automatically detects AI-related packages (tensorflow, pytorch, transformers, etc.)
- **Chinese System Detection**: Detects Chinese systems based on timezone, hardware, and language
- **Export License Generation**: Creates digital-signed export licenses for AI packages
- **Hardware Binding**: Licenses are bound to specific hardware to prevent sharing
- **Installation Quota**: Limits the number of installations per license
- **Digital Signatures**: Uses SHA256 signatures to prevent tampering

#### How it works:
1. When installing packages on Chinese systems, tpip checks if the package is AI-related
2. If it's an AI package, it requires a valid export license
3. The license must be valid, not expired, and have available installation quota
4. If no valid license exists, the installation is blocked

#### License Types:
- **TEL-BASIC**: Standard license for individual developers
- Valid for 30 days by default
- Supports up to 50 installations
- Can be extended with additional days

#### Commands:
- `tel generate`: Generate a new export license
- `tel list`: List all licenses
- `tel check`: Check license for a specific package
- `tel compliance`: Check system compliance status
- `tel help`: Show help information

#### How to download TEL?
```
//use this command:
pip install trump-export-license
```
### Warning

This is a fun tool for demonstration purposes. Do not use in production environments!

---

## 中文

一个带有特朗普政策模拟的pip工具。有时快，有时慢，总是不可预测！

### 安装

从PyPI安装：

```bash
pip install trump-pip
```

### 使用方法

安装后，使用 `tpip` 命令：

```bash
tpip install package_name
```

### 功能特性

- 多语言支持（中文、英语、日语、韩语）
- 特朗普政策模拟：
  - 60% 几率：减税政策会减慢你的下载速度
  - 30% 几率：增税政策会加快你的下载速度
  - 2% 几率：特朗普生气了，会取消你的下载（甚至可能关闭你的终端或系统！）
- 出口管制系统（TEL - 特朗普出口许可证）：
  - 在中国系统上限制AI包的安装
  - 出口许可证生成和验证
  - 硬件绑定和数字签名
  - 安装配额管理

### 示例

```bash
# 安装带有特朗普模拟效果的包
tpip install requests

# 列出已安装的包
tpip list

# 测试特朗普生气场景
tpip --test-trump-angry

# 显示关于信息
tpip --about

# 显示语言信息
tpip --language

# 特朗普出口许可证（TEL）命令
tpip --tel help                    # 显示tel帮助
tpip --tel compliance              # 检查系统合规性
tpip --tel generate --applicant "我的公司" --packages tensorflow,pytorch  # 生成许可证
tpip --tel list                    # 列出所有许可证
tpip --tel check --package tensorflow  # 检查包的许可证

# 或者直接使用tel命令（安装后）
tel help
tel compliance
tel generate --applicant "我的公司" --packages tensorflow,pytorch
tel list
tel check --package tensorflow
```

### 特朗普出口许可证（TEL）

TEL是一个简化的出口许可证系统，模拟特朗普政府对AI包的出口管制政策：

#### 主要功能：
- **AI包检测**：自动检测AI相关包（tensorflow、pytorch、transformers等）
- **中国系统检测**：基于时区、硬件和语言检测中国系统
- **出口许可证生成**：为AI包创建数字签名的出口许可证
- **硬件绑定**：许可证绑定到特定硬件，防止共享
- **安装配额**：限制每个许可证的安装次数
- **数字签名**：使用SHA256签名防止篡改

#### 工作原理：
1. 在中国系统上安装包时，tpip会检查包是否是AI相关的
2. 如果是AI包，需要有效的出口许可证
3. 许可证必须有效、未过期且有可用的安装配额
4. 如果没有有效的许可证，安装将被阻止

#### 许可证类型：
- **TEL-BASIC**：个人开发者的标准许可证
- 默认有效期为30天
- 最多支持50次安装
- 可以延长有效期

#### 命令：
- `tel generate`：生成新的出口许可证
- `tel list`：列出所有许可证
- `tel check`：检查特定包的许可证
- `tel compliance`：检查系统合规状态
- `tel help`：显示帮助信息
#### 怎么下载TEL？
```
//用这个命令安装：
pip install trump-export-license
```

### 警告

这是一个仅供演示的有趣工具。不要在生产环境中使用！

---

### License

MIT License
