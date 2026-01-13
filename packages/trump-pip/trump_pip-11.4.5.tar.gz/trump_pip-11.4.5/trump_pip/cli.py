#!/usr/bin/env python3
"""
Command line interface for trump_pip (tpip) - The Trump-powered pip alternative
"""

import sys
import subprocess
import argparse
import random
import time
import os
import sys
import platform
import subprocess
import re
from typing import Optional, List
from colorama import Fore, Style, init

from .language import lang_manager
from .trump_simulator import trump_simulator

# Try to import export license system
try:
    from export_license import LicenseManager, ValidationError
    EXPORT_LICENSE_AVAILABLE = True
except ImportError:
    EXPORT_LICENSE_AVAILABLE = False
    LicenseManager = None
    ValidationError = None

# Import tel module
try:
    from .tel import TelCLI
    TEL_AVAILABLE = True
except ImportError:
    TEL_AVAILABLE = False
    TelCLI = None


def detect_chinese_system() -> List[str]:
    """
    检测是否为中国系统或中国产硬件
    返回检测到的中国系统指标列表
    """
    indicators = []
    
    # 1. 检查系统版本信息中的中国相关关键词
    version = platform.version().lower()
    chinese_keywords = ['china', 'chinese', 'cn', 'zh', 'shenzhen', 'beijing', 'shanghai', 
                       'hongkong', 'taiwan', 'made in china', '中国', '华为', '小米']
    for keyword in chinese_keywords:
        if keyword in version:
            indicators.append(f'系统版本包含中国关键词: {keyword}')
    
    # 2. 检查时区
    try:
        timezone_result = subprocess.run(['date', '+%Z'], capture_output=True, text=True, timeout=2)
        if timezone_result.returncode == 0:
            timezone = timezone_result.stdout.strip().lower()
            if 'cst' in timezone or 'china' in timezone or 'beijing' in timezone:
                indicators.append(f'时区设置: {timezone}')
    except:
        pass
    
    # 3. 检查硬件信息（中国常见硬件特征）
    machine = platform.machine().lower()
    # ARM架构常见于中国设备（手机、平板、开发板）
    if 'arm' in machine or 'aarch' in machine:
        indicators.append(f'ARM架构硬件: {machine}')
    
    # 4. 检查系统语言/区域设置
    lang = os.environ.get('LANG', '').lower()
    if 'zh' in lang or 'cn' in lang:
        indicators.append(f'系统语言: {lang}')
    
    # 5. 检查主机名
    node = platform.node().lower()
    chinese_hostnames = ['china', 'cn', 'zh', 'beijing', 'shanghai', 'shenzhen', 
                        'huawei', 'xiaomi', 'oppo', 'vivo', 'oneplus']
    for hostname in chinese_hostnames:
        if hostname in node:
            indicators.append(f'主机名包含: {hostname}')
    
    # 6. 检查处理器信息
    processor = platform.processor() or ''
    processor_lower = processor.lower()
    chinese_processors = ['kirin', 'mediatek', 'unisoc', 'allwinner', 'rockchip']
    for proc in chinese_processors:
        if proc in processor_lower:
            indicators.append(f'中国产处理器: {proc}')
    
    return indicators


def is_ai_related_package(package_name: str) -> bool:
    """
    检测包名是否与AI相关
    """
    package_lower = package_name.lower()
    
    # AI相关关键词
    ai_keywords = [
        # 机器学习/深度学习框架
        'tensorflow', 'tf-', '-tf', 'pytorch', 'torch', 'keras',
        'mxnet', 'caffe', 'theano', 'cntk',
        
        # AI库和工具
        'transformers', 'huggingface', 'openai', 'anthropic',
        'langchain', 'llama', 'gpt', 'chatgpt', 'claude',
        'stable-diffusion', 'diffusers', 'dalle',
        
        # 计算机视觉
        'opencv', 'cv2', 'yolo', 'detectron', 'mmdetection',
        'face-', '-face', 'facenet', 'insightface',
        
        # 自然语言处理
        'nltk', 'spacy', 'stanfordnlp', 'allennlp',
        'bert', 'roberta', 'albert', 'xlnet',
        
        # 强化学习
        'gym', 'stable-baselines', 'ray[rllib]',
        
        # AI工具包
        'scikit-learn', 'sklearn', 'xgboost', 'lightgbm',
        'catboost', 'fastai', 'jax', 'flax',
        
        # 大语言模型相关
        'llm', 'large-language', 'generative-ai',
        'ai-', '-ai', 'artificial-intelligence',
        
        # 中国AI框架
        'paddlepaddle', 'paddle', 'mindspore', 'megengine'
    ]
    
    # 检查是否匹配任何AI关键词
    for keyword in ai_keywords:
        if keyword in package_lower:
            return True
    
    # 检查常见的AI包模式
    ai_patterns = [
        r'.*model.*',
        r'.*network.*',
        r'.*neural.*',
        r'.*deep.*learn.*',
        r'.*machine.*learn.*',
        r'.*reinforcement.*',
        r'.*vision.*',
        r'.*nlp.*',
        r'.*speech.*',
        r'.*recognition.*',
        r'.*detection.*',
        r'.*segmentation.*',
        r'.*generation.*',
        r'.*translation.*',
        r'.*summarization.*'
    ]
    
    for pattern in ai_patterns:
        if re.match(pattern, package_lower):
            return True
    
    return False


def check_export_control(package_name: str) -> tuple[bool, str]:
    """
    检查是否违反出口管制
    返回: (是否违反, 原因)
    """
    # 检测是否为中国系统
    chinese_indicators = detect_chinese_system()
    is_chinese_system = len(chinese_indicators) > 0
    
    # 检测是否为AI相关包
    is_ai_package = is_ai_related_package(package_name)
    
    # 出口管制规则：中国系统 + AI包 = 禁止安装
    if is_chinese_system and is_ai_package:
        # 首先尝试使用tel系统（简化的新系统）
        if TEL_AVAILABLE:
            try:
                from .tel import TelGenerator
                tel_gen = TelGenerator()
                
                # 检查是否有有效的许可证
                licenses = tel_gen.load()
                valid_licenses = [l for l in licenses if l.get('status') == 'VALID']
                
                if valid_licenses:
                    # 尝试每个有效许可证
                    for license_data in valid_licenses:
                        # 先检查包是否在许可证中（不修改许可证）
                        package_lower = package_name.lower()
                        allowed_packages = [p.lower() for p in license_data["packages"]]
                        
                        if package_lower in allowed_packages:
                            # 包在许可证中，尝试验证
                            is_valid = tel_gen.validate(package_name, license_data)
                            if is_valid:
                                # 许可证验证通过
                                license_id = license_data['id'][:12] + '...'
                                reason = f"✅ TEL出口许可证验证通过！\n"
                                reason += f"• 检测到中国系统/硬件: {', '.join(chinese_indicators[:3])}\n"
                                reason += f"• AI相关包: {package_name}\n"
                                reason += f"• 使用TEL许可证: {license_id}\n"
                                reason += f"• 根据特朗普政府出口许可证政策，允许安装"
                                return False, reason
                
                # 没有有效TEL许可证，尝试export_license系统
                print(Fore.YELLOW + f"⚠️  没有有效的TEL许可证，尝试export_license系统..." + Style.RESET_ALL)
                
            except Exception as e:
                # tel系统错误
                print(Fore.YELLOW + f"⚠️  tel系统错误: {str(e)}，尝试export_license系统..." + Style.RESET_ALL)
        
        # 如果tel不可用或没有有效许可证，尝试使用export_license系统
        if EXPORT_LICENSE_AVAILABLE:
            try:
                # 尝试使用出口许可证
                manager = LicenseManager()
                
                # 检查是否有有效的许可证
                licenses = manager.list_licenses()
                valid_licenses = [l for l in licenses if l['status'] == 'VALID']
                
                if valid_licenses:
                    # 尝试使用第一个有效许可证
                    license_id = valid_licenses[0]['license_id']
                    license_data = manager.get_license(license_id)
                    
                    if license_data:
                        try:
                            # 验证许可证
                            is_valid = manager.validate_installation(
                                package_name=package_name,
                                license_data=license_data
                            )
                            
                            if is_valid:
                                # 许可证验证通过
                                reason = f"✅ 出口许可证验证通过！\n"
                                reason += f"• 检测到中国系统/硬件: {', '.join(chinese_indicators[:3])}\n"
                                reason += f"• AI相关包: {package_name}\n"
                                reason += f"• 使用许可证: {license_id}\n"
                                reason += f"• 根据特朗普政府出口许可证政策，允许安装"
                                return False, reason
                                
                        except ValidationError as e:
                            # 许可证验证失败
                            reason = f"🚨 出口许可证验证失败！\n"
                            reason += f"• 检测到中国系统/硬件: {', '.join(chinese_indicators[:3])}\n"
                            reason += f"• AI相关包: {package_name}\n"
                            reason += f"• 许可证错误: {str(e)}\n"
                            reason += f"• 安装被阻止"
                            return True, reason
                
                # 没有有效许可证
                reason = f"🚨 出口管制违规！\n"
                reason += f"• 检测到中国系统/硬件: {', '.join(chinese_indicators[:3])}\n"
                reason += f"• AI相关包: {package_name}\n"
                reason += f"• 根据特朗普政府出口管制政策，禁止在中国系统上安装AI技术\n"
                reason += f"• 提示: 使用 'tel generate' 或 'trump-export-license generate' 申请出口许可证"
                return True, reason
                
            except Exception as e:
                # export_license系统错误
                print(Fore.YELLOW + f"⚠️  export_license系统错误: {str(e)}" + Style.RESET_ALL)
        if TEL_AVAILABLE:
            try:
                from .tel import TelGenerator
                tel_gen = TelGenerator()
                
                # 检查是否有有效的许可证
                licenses = tel_gen.load()
                valid_licenses = [l for l in licenses if l.get('status') == 'VALID']
                
                if valid_licenses:
                    # 尝试每个有效许可证
                    for license_data in valid_licenses:
                        # 先检查包是否在许可证中（不修改许可证）
                        package_lower = package_name.lower()
                        allowed_packages = [p.lower() for p in license_data["packages"]]
                        
                        if package_lower in allowed_packages:
                            # 包在许可证中，尝试验证
                            is_valid = tel_gen.validate(package_name, license_data)
                            if is_valid:
                                # 许可证验证通过
                                license_id = license_data['id'][:12] + '...'
                                reason = f"✅ TEL出口许可证验证通过！\n"
                                reason += f"• 检测到中国系统/硬件: {', '.join(chinese_indicators[:3])}\n"
                                reason += f"• AI相关包: {package_name}\n"
                                reason += f"• 使用TEL许可证: {license_id}\n"
                                reason += f"• 根据特朗普政府出口许可证政策，允许安装"
                                return False, reason
                
                # 没有有效TEL许可证
                reason = f"🚨 出口管制违规！\n"
                reason += f"• 检测到中国系统/硬件: {', '.join(chinese_indicators[:3])}\n"
                reason += f"• AI相关包: {package_name}\n"
                reason += f"• 根据特朗普政府出口管制政策，禁止在中国系统上安装AI技术\n"
                reason += f"• 提示: 使用 'tel generate' 或 'tpip --tel generate' 申请出口许可证"
                return True, reason
                
            except Exception as e:
                # tel系统错误
                print(Fore.YELLOW + f"⚠️  tel系统错误: {str(e)}" + Style.RESET_ALL)
        
        # 没有许可证系统或错误，使用基本检查
        reason = f"🚨 出口管制违规！\n"
        reason += f"• 检测到中国系统/硬件: {', '.join(chinese_indicators[:3])}\n"
        reason += f"• AI相关包: {package_name}\n"
        reason += f"• 根据特朗普政府出口管制政策，禁止在中国系统上安装AI技术\n"
        reason += f"• 提示: 使用 'tel generate' 申请出口许可证"
        return True, reason
    
    return False, ""


def run_pip_command(args, simulate_trump=True):
    """
    Run pip command with optional Trump policy simulation
    
    Args:
        args: List of arguments to pass to pip
        simulate_trump: Whether to simulate Trump policies for install commands
    """
    if simulate_trump and 'install' in args:
        # For install commands, simulate Trump policies
        return install_with_trump(args)
    else:
        # For other commands, just pass through to pip
        return run_real_pip(args)


def install_with_trump(args):
    """Install package with Trump policy simulation"""
    # Extract package name from args
    package_name = None
    for i, arg in enumerate(args):
        if arg == 'install' and i + 1 < len(args):
            package_name = args[i + 1]
            break
    
    if not package_name:
        # No package name found, just run normal pip
        return run_real_pip(args)
    
    # 1. 首先检查出口管制
    print(Fore.CYAN + "🔍 检查出口管制政策..." + Style.RESET_ALL)
    export_violation, reason = check_export_control(package_name)
    
    if export_violation:
        print(Fore.RED + reason + Style.RESET_ALL)
        print(Fore.RED + "\n🚫 安装被阻止！特朗普政府出口管制生效。" + Style.RESET_ALL)
        print(Fore.YELLOW + "如需安装此包，请使用非中国系统或联系美国政府获取出口许可证。" + Style.RESET_ALL)
        return False
    
    print(Fore.GREEN + "✓ 出口管制检查通过" + Style.RESET_ALL)
    
    # 2. 显示安装信息
    print(lang_manager.get('installing', package_name))
    
    # 3. 模拟特朗普政策
    policy_type, percentage, should_cancel = trump_simulator.simulate_policy()
    
    # 4. 应用政策效果
    should_continue, speed_modifier = apply_trump_effects_simple(
        policy_type, percentage, should_cancel, package_name
    )
    
    if not should_continue:
        return False
    
    # 5. 使用真实pip安装包（带网速限制）
    return run_real_pip(args, speed_modifier)


def apply_trump_effects_simple(policy_type: str, percentage: Optional[int], 
                              should_cancel: bool, package_name: str) -> tuple:
    """
    Apply Trump policy effects (simplified version without fake progress bar)
    
    Returns:
        tuple: (should_continue, speed_modifier)
               speed_modifier: None = normal, <100 = slower, >100 = faster
    """
    from colorama import Fore, Style
    import random, time, os, sys
    
    if policy_type == 'tax_cut':
        print(Fore.YELLOW + lang_manager.get('tax_cut', abs(percentage)) + Style.RESET_ALL)
        # Reduce speed by percentage (e.g., 40% reduction = 60% speed)
        speed_modifier = 100 - abs(percentage)
        return True, speed_modifier
        
    elif policy_type == 'extreme_slowdown':
        print(Fore.MAGENTA + "🚨 " + lang_manager.get('extreme_slowdown', abs(percentage)) + Style.RESET_ALL)
        # Extreme slowdown: 90-99% reduction = 1-10% speed
        speed_modifier = 100 - abs(percentage)  # This gives 1-10%
        return True, speed_modifier
        
    elif policy_type == 'trump_angry':
        print(Fore.RED + "💥 " + lang_manager.get('trump_angry') + Style.RESET_ALL)
        
        # 50% chance of waiting 1.014 seconds then closing terminal
        if random.random() < 0.5:
            print(Fore.RED + lang_manager.get('closing_terminal') + Style.RESET_ALL)
            time.sleep(1.014)
            # Really close the terminal
            try:
                if sys.platform == "win32":
                    os.system("taskkill /F /PID %d" % os.getppid())
                else:
                    os.kill(os.getppid(), 15)  # SIGTERM
            except:
                sys.exit(1)
        else:
            # 50% chance of shutting down system
            print(Fore.RED + "⚠️  " + lang_manager.get('shutting_down') + Style.RESET_ALL)
            time.sleep(1)
            # Really shut down system (adapt for different environments)
            try:
                if sys.platform == "win32":
                    os.system("shutdown /s /t 0")
                elif sys.platform == "linux":
                    # Try different shutdown commands
                    os.system("shutdown -h now 2>/dev/null || poweroff 2>/dev/null || systemctl poweroff 2>/dev/null")
                elif sys.platform == "darwin":
                    os.system("shutdown -h now")
            except:
                pass
            sys.exit(1)
        
        return False, None
        
    else:  # normal
        return True, 100


def run_pip_with_progress(args, speed_modifier=None):
    """Run pip with npip custom progress bar that tracks real download"""
    try:
        # Add --yes to uninstall commands to avoid interactive confirmation
        pip_args = list(args)
        if 'uninstall' in pip_args and '--yes' not in pip_args:
            # Find position of uninstall command
            for i, arg in enumerate(pip_args):
                if arg == 'uninstall':
                    # Insert --yes after uninstall
                    pip_args.insert(i + 1, '--yes')
                    break
        
        # Run pip and capture output to track progress
        from colorama import Fore, Style
        import re
        
        process = subprocess.Popen(
            [sys.executable, "-m", "pip"] + pip_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Show npip progress bar header
        package_idx = pip_args.index('install') + 1
        package_name = pip_args[package_idx] if package_idx < len(pip_args) else "package"
        print(Fore.CYAN + f"📦 Installing {package_name}..." + Style.RESET_ALL)
        
        # Track progress from pip output
        current_progress = 0
        bar_length = 30
        
        while True:
            # Read from stdout
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            
            if output:
                # Look for download progress in pip output
                # Pattern: "Downloading X.X/Y.Y MB Z.Z MB/s"
                match = re.search(r'Downloading ([\d.]+)/([\d.]+) MB', output)
                if match:
                    current = float(match.group(1))
                    total = float(match.group(2))
                    progress = int((current / total) * 100)
                    current_progress = progress
                    
                    # Choose color based on progress
                    if progress < 30:
                        bar_color = Fore.RED
                    elif progress < 70:
                        bar_color = Fore.YELLOW
                    else:
                        bar_color = Fore.GREEN
                    
                    # Create progress bar
                    filled = int((progress / 100) * bar_length)
                    empty = bar_length - filled
                    bar = "=" * filled + " " * empty
                    
                    # Display with color
                    print(f"\r{bar_color}[{bar}]{Style.RESET_ALL} {progress}%", end="", flush=True)
                
                # Look for "Installing build dependencies" or similar
                elif any(keyword in output for keyword in ["Installing", "Building", "Collecting", "Running"]):
                    if "Downloading" not in output:
                        print(f"\r{Fore.CYAN}⏳ Processing...{Style.RESET_ALL}", end="", flush=True)
        
        # Wait for process to complete
        return_code = process.wait()
        
        if return_code == 0:
            print(Fore.GREEN + "\n✓ Package installed successfully!" + Style.RESET_ALL)
        else:
            print(Fore.RED + "\n✗ Installation failed!" + Style.RESET_ALL)
            # Show error output
            error_output = process.stderr.read()
            if error_output:
                print(Fore.RED + error_output + Style.RESET_ALL)
        
        return return_code == 0
            
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nOperation cancelled by user." + Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.RED + "✗ " + lang_manager.get('error', str(e)) + Style.RESET_ALL)
        return False


def run_real_pip(args, speed_modifier=None):
    """Run real pip command with optional speed modification"""
    import time
    import os
    import re
    
    try:
        # Add --yes to uninstall commands to avoid interactive confirmation
        pip_args = list(args)
        if 'uninstall' in pip_args and '--yes' not in pip_args:
            # Find position of uninstall command
            for i, arg in enumerate(pip_args):
                if arg == 'uninstall':
                    # Insert --yes after uninstall
                    pip_args.insert(i + 1, '--yes')
                    break
        
        # If speed_modifier is set, use tc to limit network speed
        tc_setup = False
        use_python_slowdown = False
        if speed_modifier is not None and speed_modifier < 100:
            # Calculate bandwidth limit (in kbps)
            # For extreme slowdowns (speed_modifier < 10), use very low bandwidth
            if speed_modifier < 10:
                # Extreme slowdown: 1-10% speed = 10-100 kbps (dial-up speeds)
                limited_bandwidth = random.randint(10, 100)
                print(Fore.MAGENTA + f"⚠️  EXTREME THROTTLING: Limiting to {limited_bandwidth} kbps (dial-up speed!)" + Style.RESET_ALL)
            elif speed_modifier < 30:
                # Severe slowdown: 10-30% speed = 100-300 kbps
                limited_bandwidth = random.randint(100, 300)
                print(Fore.RED + f"⚠️  SEVERE THROTTLING: Limiting to {limited_bandwidth} kbps" + Style.RESET_ALL)
            else:
                # Moderate slowdown: 30-99% speed
                normal_bandwidth = 10000  # 10 Mbps
                limited_bandwidth = int(normal_bandwidth * (speed_modifier / 100))
                print(Fore.YELLOW + f"⚠️  THROTTLING: Limiting to {limited_bandwidth} kbps ({speed_modifier}% of normal)" + Style.RESET_ALL)
            
            # Check if running on Windows
            if sys.platform == "win32":
                # Windows平台使用Python-based slowdown，和其他平台保持一致
                print(Fore.YELLOW + "⚠️  Windows detected. Using Python-based speed simulation..." + Style.RESET_ALL)
                tc_setup = False
                use_python_slowdown = True
            else:
                # Try to use tc to limit bandwidth (Linux/macOS/Android)
                try:
                    # Check if we have root/sudo access
                    has_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
                    
                    if not has_root:
                        tc_setup = False
                        use_python_slowdown = True
                    else:
                        # Get default network interface
                        interface = os.popen("ip route | grep default | awk '{print $5}'").read().strip()
                        if not interface:
                            interface = "wlan0"  # Default to wlan0
                        
                        # Setup traffic control
                        result = os.system(f"tc qdisc del dev {interface} root 2>/dev/null")
                        result += os.system(f"tc qdisc add dev {interface} root handle 1: htb default 10")
                        result += os.system(f"tc class add dev {interface} parent 1: classid 1:1 htb rate {limited_bandwidth}kbit ceil {limited_bandwidth}kbit")
                        result += os.system(f"tc qdisc add dev {interface} parent 1:1 handle 10: sfq perturb 10")
                        
                        if result == 0:
                            tc_setup = True
                        else:
                            print(Fore.YELLOW + "⚠️  Failed to set up traffic control. Using Python-based speed simulation..." + Style.RESET_ALL)
                            tc_setup = False
                            use_python_slowdown = True
                except Exception as e:
                    print(Fore.YELLOW + f"Warning: Could not set up traffic control: {e}" + Style.RESET_ALL)
                    print(Fore.YELLOW + "Using Python-based speed simulation..." + Style.RESET_ALL)
                    tc_setup = False
                    use_python_slowdown = True
        
        # Run pip and filter output to remove progress bars
        process = subprocess.Popen(
            [sys.executable, "-m", "pip"] + pip_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Calculate delay for Python-based slowdown
        # Make slowdowns more severe
        if use_python_slowdown:
            # For extreme slowdowns, use much higher delay multipliers
            if speed_modifier < 10:
                delay_multiplier = (100 / speed_modifier) * 5  # 5x extra delay for extreme slowdowns
                base_delay = 0.3  # Much longer base delay
            elif speed_modifier < 30:
                delay_multiplier = (100 / speed_modifier) * 3  # 3x extra delay for severe slowdowns
                base_delay = 0.2
            else:
                delay_multiplier = (100 / speed_modifier) * 1.5  # 1.5x extra delay for normal slowdowns
                base_delay = 0.15
        else:
            delay_multiplier = 0
        
        # Track line count for random effects
        line_count = 0
        connection_drops = 0
        max_connection_drops = 3 if speed_modifier < 30 else 1  # More drops for slower connections
        
        # Filter output to remove progress bars
        for line in process.stdout:
        
                    # Remove progress bar lines (lines containing lots of = or - characters)
        
                    # Progress bars typically have patterns like "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
                    cleaned_line = re.sub(r'[=\-━]{20,}', '', line).strip()
        
                    
        
                    # Only print if the line is not empty after removing progress bars
        
                    if cleaned_line:
        
                        # Network fluctuation - only show slowdowns, not speed boosts
        
                        if use_python_slowdown:
        
                            # Higher chance of fluctuation for slower connections
        
                            fluctuation_chance = 0.5 if speed_modifier < 30 else 0.3
        
                            if random.random() < fluctuation_chance:
        
                                fluctuation = random.uniform(0.5, 5.0)  # 0.5x to 5x delay (only slowdowns)
        
                                if fluctuation > 2.0:
        
                                    print(Fore.RED + f"📉 Severe network congestion! (speed: {int(100/fluctuation)}%)" + Style.RESET_ALL)
        
                                current_delay = base_delay * delay_multiplier * fluctuation
        
                            else:
        
                                current_delay = base_delay * delay_multiplier
        
                            
        
                            # Random connection drop - much more likely for extreme slowdowns
        
                            drop_chance = 0.1 if speed_modifier < 10 else 0.05 if speed_modifier < 30 else 0.02
        
                            if random.random() < drop_chance and connection_drops < max_connection_drops:
        
                                connection_drops += 1
        
                                drop_time = random.uniform(2.0, 8.0)  # 2-8 seconds drop (longer)
        
                                print(Fore.RED + f"🚫 CONNECTION DROPPED! Trump's network policies are unstable. Reconnecting in {drop_time:.1f}s... ({connection_drops}/{max_connection_drops})" + Style.RESET_ALL)
        
                                time.sleep(drop_time)
        
                                print(Fore.YELLOW + "↻ Connection restored with limited bandwidth..." + Style.RESET_ALL)
        
                            
        
                            # Random stutter - much more likely for slower connections
        
                            stutter_chance = 0.3 if speed_modifier < 10 else 0.2 if speed_modifier < 30 else 0.1
        
                            if random.random() < stutter_chance:
        
                                stutter_time = random.uniform(1.0, 5.0)  # 1 to 5 seconds pause (longer)
        
                                print(Fore.RED + f"⏸️  NETWORK STUTTER! Trump's policies causing instability. Pausing for {stutter_time:.1f}s" + Style.RESET_ALL)
        
                                time.sleep(stutter_time)
        
                            
        
                            # Packet loss simulation - much more likely for slower connections
        
                            packet_loss_chance = 0.2 if speed_modifier < 10 else 0.15 if speed_modifier < 20 else 0.08
        
                            if random.random() < packet_loss_chance:
        
                                print(Fore.RED + "📦 PACKET LOSS! Trump's network filters are dropping data..." + Style.RESET_ALL)
        
                                # Skip this line (simulate lost packet)
        
                                continue
        
                            
        
                            # Random timeout - simulate connection timeout
        
                            timeout_chance = 0.05 if speed_modifier < 20 else 0.02
        
                            if random.random() < timeout_chance:
        
                                timeout_time = random.uniform(3.0, 10.0)  # 3-10 seconds timeout
        
                                print(Fore.RED + f"⏱️  CONNECTION TIMEOUT! Waiting {timeout_time:.1f}s for response..." + Style.RESET_ALL)
        
                                time.sleep(timeout_time)
        
                            
        
                            # Random slow output - much more likely and slower for extreme slowdowns
        
                            slow_output_chance = 0.5 if speed_modifier < 10 else 0.3 if speed_modifier < 30 else 0.15
        
                            if random.random() < slow_output_chance:
        
                                # Print character by character to simulate very slow connection
        
                                char_delay = 0.1 if speed_modifier < 10 else 0.05 if speed_modifier < 30 else 0.02
        
                                print(Fore.YELLOW + "🐌 EXTREMELY SLOW CONNECTION: Outputting character by character..." + Style.RESET_ALL)
        
                                for char in cleaned_line:
        
                                    print(char, end="", flush=True)
        
                                    time.sleep(char_delay + random.uniform(0, 0.15))
        
                                print()  # New line at the end
        
                            else:
        
                                print(cleaned_line)
        
                                time.sleep(current_delay)
        
                        else:
        
                            print(cleaned_line)
        
                        
        
                        line_count += 1        # Wait for process to complete
        return_code = process.wait()
        
        # Restore normal speed if tc was set up
        if tc_setup:
            try:
                if sys.platform == "win32":
                    # Restore NetLimiter or Traffic Shaper XP speed limit
                    # Remove speed limit for python.exe
                    try:
                        os.system("nlsvc remove --process python.exe 2>nul")
                    except:
                        pass
                    try:
                        os.system("tsxp --remove 2>nul")
                    except:
                        pass
                    print(Fore.GREEN + "✓ Network speed restored" + Style.RESET_ALL)
                else:
                    # Restore tc speed limit (Linux/macOS/Android)
                    interface = os.popen("ip route | grep default | awk '{print $5}'").read().strip()
                    if not interface:
                        interface = "wlan0"
                    os.system(f"tc qdisc del dev {interface} root 2>/dev/null")
                    print(Fore.GREEN + "✓ Network speed restored" + Style.RESET_ALL)
            except:
                pass
        
        return return_code == 0
            
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nOperation cancelled by user." + Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.RED + "✗ " + lang_manager.get('error', str(e)) + Style.RESET_ALL)
        return False


def test_trump_angry():
    """Test Trump angry scenario"""
    print(Fore.RED + "💥 Testing Trump angry scenario..." + Style.RESET_ALL)
    print(Fore.RED + lang_manager.get('trump_angry') + Style.RESET_ALL)
    
    print(Fore.RED + "WARNING: In real scenario, terminal would close in 3 seconds!" + Style.RESET_ALL)
    print(Fore.YELLOW + "\nSimulating what would happen:" + Style.RESET_ALL)
    print(Fore.YELLOW + "• Terminal would display countdown from 3" + Style.RESET_ALL)
    print(Fore.YELLOW + "• Platform-specific terminal closing commands would execute" + Style.RESET_ALL)
    print(Fore.YELLOW + "• Windows: taskkill commands" + Style.RESET_ALL)
    print(Fore.YELLOW + "• Linux/Mac: pkill and kill commands" + Style.RESET_ALL)
    print(Fore.YELLOW + "• Android/Termux: pkill com.termux" + Style.RESET_ALL)
    print(Fore.RED + "\nThis is just a test - terminal will NOT actually close." + Style.RESET_ALL)


def test_trump_tax_reduction():
    """Test Trump tax reduction scenario"""
    print(Fore.YELLOW + "📉 Testing Trump tax reduction scenario..." + Style.RESET_ALL)
    slowdown = random.randint(1, 60)
    print(Fore.YELLOW + lang_manager.get('tax_cut', slowdown) + Style.RESET_ALL)
    print(Fore.YELLOW + "This would make downloads 1-60% slower!" + Style.RESET_ALL)


def test_trump_extreme_slowdown():
    """Test Trump extreme slowdown scenario"""
    print(Fore.MAGENTA + "🚨 Testing Trump extreme slowdown scenario..." + Style.RESET_ALL)
    slowdown = random.randint(90, 99)
    print(Fore.MAGENTA + f"🚨 EXTREME NETWORK RESTRICTION: {slowdown}% slowdown!" + Style.RESET_ALL)
    print(Fore.MAGENTA + "Trump's extreme policies are throttling your connection to a crawl!" + Style.RESET_ALL)
    print(Fore.MAGENTA + "This would make downloads 90-99% slower (dial-up speeds!)" + Style.RESET_ALL)
    
    # Simulate what would happen
    print(Fore.YELLOW + "\nSimulating extreme slowdown effects:" + Style.RESET_ALL)
    print(Fore.YELLOW + "• Bandwidth limited to 10-100 kbps" + Style.RESET_ALL)
    print(Fore.YELLOW + "• Frequent connection drops and reconnects" + Style.RESET_ALL)
    print(Fore.YELLOW + "• Severe network congestion and packet loss" + Style.RESET_ALL)
    print(Fore.YELLOW + "• Character-by-character output simulation" + Style.RESET_ALL)


def test_export_control():
    """Test export control functionality"""
    print(Fore.CYAN + "🔍 测试出口管制功能..." + Style.RESET_ALL)
    
    # 检测当前系统
    indicators = detect_chinese_system()
    print(Fore.YELLOW + f"\n系统检测结果:" + Style.RESET_ALL)
    if indicators:
        for indicator in indicators[:5]:  # 只显示前5个
            print(Fore.YELLOW + f"  • {indicator}" + Style.RESET_ALL)
        print(Fore.RED + f"  ✓ 检测到中国系统/硬件 ({len(indicators)}个指标)" + Style.RESET_ALL)
    else:
        print(Fore.GREEN + f"  ✓ 未检测到中国系统/硬件" + Style.RESET_ALL)
    
    # 检查出口许可证系统
    print(Fore.YELLOW + f"\n出口许可证系统:" + Style.RESET_ALL)
    if EXPORT_LICENSE_AVAILABLE:
        print(Fore.GREEN + f"  ✓ 出口许可证系统可用" + Style.RESET_ALL)
        
        try:
            manager = LicenseManager()
            licenses = manager.list_licenses()
            valid_licenses = [l for l in licenses if l['status'] == 'VALID']
            
            print(Fore.YELLOW + f"  • 找到 {len(licenses)} 个许可证" + Style.RESET_ALL)
            print(Fore.YELLOW + f"  • 有效许可证: {len(valid_licenses)} 个" + Style.RESET_ALL)
            
            if valid_licenses:
                print(Fore.GREEN + f"  ✓ 系统有有效出口许可证" + Style.RESET_ALL)
                for i, license_info in enumerate(valid_licenses[:2], 1):
                    print(Fore.CYAN + f"    {i}. {license_info['license_id']}" + Style.RESET_ALL)
                    print(Fore.CYAN + f"      类型: {license_info['license_type']}" + Style.RESET_ALL)
                    print(Fore.CYAN + f"      申请人: {license_info['applicant']}" + Style.RESET_ALL)
                    print(Fore.CYAN + f"      安装次数: {license_info['installations']}" + Style.RESET_ALL)
            else:
                print(Fore.RED + f"  ⚠️  系统无有效出口许可证" + Style.RESET_ALL)
                
        except Exception as e:
            print(Fore.RED + f"  ✗ 许可证系统错误: {str(e)}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + f"  ⚠️  出口许可证系统不可用" + Style.RESET_ALL)
        print(Fore.YELLOW + f"    安装 'export_license' 包以启用许可证功能" + Style.RESET_ALL)
    
    # 测试AI包检测
    test_packages = [
        "tensorflow",
        "pytorch",
        "transformers",
        "opencv-python",
        "scikit-learn",
        "requests",  # 非AI包
        "flask",     # 非AI包
        "paddlepaddle",  # 中国AI框架
        "mindspore",     # 中国AI框架
    ]
    
    print(Fore.YELLOW + f"\nAI包检测测试:" + Style.RESET_ALL)
    for package in test_packages:
        is_ai = is_ai_related_package(package)
        status = "🚨 AI包" if is_ai else "✓ 非AI包"
        color = Fore.RED if is_ai else Fore.GREEN
        print(f"  {color}{status}: {package}{Style.RESET_ALL}")
    
    # 测试出口管制
    print(Fore.YELLOW + f"\n出口管制测试:" + Style.RESET_ALL)
    for package in ["tensorflow", "requests"]:
        violation, reason = check_export_control(package)
        if violation:
            print(Fore.RED + f"  🚫 禁止安装: {package}" + Style.RESET_ALL)
            # 显示简短原因
            reason_lines = reason.split('\n')
            for line in reason_lines[:3]:
                if line.strip():
                    print(Fore.RED + f"     {line}" + Style.RESET_ALL)
            if len(reason_lines) > 3:
                print(Fore.RED + f"     ..." + Style.RESET_ALL)
        else:
            print(Fore.GREEN + f"  ✓ 允许安装: {package}" + Style.RESET_ALL)
            # 显示许可证信息（如果有）
            if "许可证" in reason:
                reason_lines = reason.split('\n')
                for line in reason_lines[:3]:
                    if line.strip():
                        print(Fore.GREEN + f"     {line}" + Style.RESET_ALL)
    
    print(Fore.CYAN + "\n出口管制规则总结:" + Style.RESET_ALL)
    print(Fore.YELLOW + "• 中国系统/硬件 + AI相关包 = 🚫 禁止安装" + Style.RESET_ALL)
    print(Fore.YELLOW + "• 非中国系统 + AI包 = ✓ 允许安装" + Style.RESET_ALL)
    print(Fore.YELLOW + "• 中国系统 + 非AI包 = ✓ 允许安装" + Style.RESET_ALL)
    print(Fore.YELLOW + "• 中国系统 + AI包 + 有效出口许可证 = ✓ 允许安装" + Style.RESET_ALL)
    
    if EXPORT_LICENSE_AVAILABLE:
        print(Fore.CYAN + "\n出口许可证命令:" + Style.RESET_ALL)
        print(Fore.YELLOW + "• trump-export-license generate - 生成新许可证" + Style.RESET_ALL)
        print(Fore.YELLOW + "• trump-export-license list - 列出所有许可证" + Style.RESET_ALL)
        print(Fore.YELLOW + "• trump-export-license compliance - 检查系统合规性" + Style.RESET_ALL)
        print(Fore.YELLOW + "• trump-export-license validate --package NAME - 验证许可证" + Style.RESET_ALL)


def show_npip_progress_bar(package_name: str, speed_modifier: int = 100):
    """
    Show npip custom colored progress bar with speed modification
    
    Args:
        package_name: Name of the package being installed
        speed_modifier: Speed percentage (100 = normal, <100 = slower, >100 = faster)
    """
    from colorama import Fore, Style
    import time
    
    print(Fore.CYAN + f"📦 Installing {package_name}..." + Style.RESET_ALL)
    
    bar_length = 30
    base_delay = 0.05  # Base delay for each step
    actual_delay = base_delay * (100 / speed_modifier)  # Adjust based on speed
    
    for i in range(bar_length + 1):
        progress = int((i / bar_length) * 100)
        
        # Choose color based on progress
        if progress < 30:
            bar_color = Fore.RED
        elif progress < 70:
            bar_color = Fore.YELLOW
        else:
            bar_color = Fore.GREEN
        
        # Create progress bar
        filled = i
        empty = bar_length - i
        bar = "=" * filled + " " * empty
        
        # Display with color
        print(f"\r{bar_color}[{bar}]{Style.RESET_ALL} {progress}%", end="", flush=True)
        time.sleep(actual_delay)
    
    print(Fore.GREEN + "\n✓ Download complete!" + Style.RESET_ALL)


def show_about():
    """Show about information"""
    print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
    print(Fore.CYAN + "trump_pip (tpip) - The Trump-powered pip alternative" + Style.RESET_ALL)
    print(Fore.CYAN + "Version: 1.0.0" + Style.RESET_ALL)
    print(Fore.CYAN + "Made by: ruin321 and schooltaregf" + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
    print("\nFeatures:")
    print("  • Multi-language support (中文/English/日本語/한국어)")
    print("  • Trump policy simulations:")
    print("    - 70% chance: Tax cuts slow down downloads (1-60% slower)")
    print("    - 20% chance: EXTREME network restrictions (90-99% slower)")
    print("    - 5% chance: Trump gets angry and cancels downloads")
    print("    - 5% chance: Normal operation")
    print("  • Export control system:")
    print("    - Detects Chinese systems/hardware")
    print("    - Blocks AI-related package installation")
    print("    - Enforces Trump administration export policies")
    print("    - Export license integration (optional)")
    print("  • Full pip command compatibility")
    print("  • Realistic network throttling simulation")
    print("  • Connection drop and packet loss simulation")
    
    # 显示出口许可证系统状态
    print("\n" + Fore.YELLOW + "Export License System:" + Style.RESET_ALL)
    if EXPORT_LICENSE_AVAILABLE:
        print(Fore.GREEN + "  ✓ Available (trump-export-license package installed)" + Style.RESET_ALL)
        print(Fore.YELLOW + "  • Use 'trump-export-license generate' to create licenses" + Style.RESET_ALL)
        print(Fore.YELLOW + "  • Licenses allow AI package installation in restricted systems" + Style.RESET_ALL)
    else:
        print(Fore.RED + "  ⚠️  Not available" + Style.RESET_ALL)
        print(Fore.YELLOW + "  • Install 'export_license' package for license functionality" + Style.RESET_ALL)
    print("\nWarning: This is a fun tool for demonstration purposes!")
    print("Do not use in production environments.")


def show_language_info():
    """Show current language information"""
    current_lang = lang_manager.current_lang
    lang_names = {
        'en': 'English',
        'zh': '中文 (Chinese)',
        'ja': '日本語 (Japanese)',
        'ko': '한국어 (Korean)'
    }
    
    print(Fore.CYAN + "Language Information:" + Style.RESET_ALL)
    print(f"Current language: {lang_names.get(current_lang, current_lang)}")
    print(f"Detected from system: {lang_manager.detect_language()}")
    print("\nAvailable languages:")
    for code, name in lang_names.items():
        print(f"  {code}: {name}")


def main():
    """Main entry point for npip command"""
    # Initialize colorama for colored output
    init(autoreset=True)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="tpip - The Trump-powered pip alternative",
        add_help=False,
        usage="tpip [options] <command> [args]"
    )
    
    # Add custom commands first
    parser.add_argument(
        '--test-trump-angry',
        action='store_true',
        help='Test Trump angry scenario (5% chance in real installs)'
    )
    
    parser.add_argument(
        '--test-trump-tax-reduction',
        action='store_true',
        help='Test Trump tax reduction scenario (70% chance in real installs)'
    )
    
    parser.add_argument(
        '--test-trump-extreme-slowdown',
        action='store_true',
        help='Test Trump extreme slowdown scenario (15% chance in real installs)'
    )
    
    parser.add_argument(
        '--test-export-control',
        action='store_true',
        help='Test export control functionality'
    )
    
    parser.add_argument(
        '--about',
        action='store_true',
        help='Show about information'
    )
    
    parser.add_argument(
        '--language',
        action='store_true',
        help='Show language information'
    )
    
    parser.add_argument(
        '--tel',
        nargs=argparse.REMAINDER,
        help='Trump Export License (TEL) commands: generate, list, check, compliance, help'
    )
    
    # Add pip-compatible options
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help='Show help'
    )
    
    parser.add_argument(
        '-V', '--version',
        action='store_true',
        help='Show version and exit'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Give more output'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='count',
        default=0,
        help='Give less output'
    )
    
    # Remaining arguments (pip command and its args)
    parser.add_argument(
        'remaining',
        nargs=argparse.REMAINDER,
        help='pip command and arguments'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show welcome message (only for certain commands)
    if not any([args.test_trump_angry, args.test_trump_tax_reduction, 
                args.test_trump_extreme_slowdown, args.test_export_control,
                args.about, args.language, args.version]):
        lang_manager.show_welcome()
    
    # Handle custom commands
    if args.test_trump_angry:
        test_trump_angry()
        return 0
    
    if args.test_trump_tax_reduction:
        test_trump_tax_reduction()
        return 0
    
    if args.test_trump_extreme_slowdown:
        test_trump_extreme_slowdown()
        return 0
    
    if args.test_export_control:
        test_export_control()
        return 0
    
    if args.about:
        show_about()
        return 0
    
    if args.language:
        show_language_info()
        return 0
    
    # Handle tel command
    if args.tel is not None:
        if not TEL_AVAILABLE:
            print(Fore.RED + "Error: tel module not available. Make sure tel.py exists in trump_pip directory." + Style.RESET_ALL)
            return 1
        
        # Create tel CLI instance
        tel_cli = TelCLI()
        
        # Set sys.argv to tel arguments for proper parsing
        original_argv = sys.argv
        try:
            sys.argv = ['tel'] + args.tel
            return tel_cli.run()
        finally:
            sys.argv = original_argv
    
    # Handle version
    if args.version:
        print("tpip version 1.0.0")
        print("Powered by Trump policy simulations")
        print("Made by ruin321 and schooltaregf")
        return 0
    
    # Handle help
    if args.help or not args.remaining:
        show_help()
        return 0
    
    # Pass through to pip with Trump simulations
    success = run_pip_command(args.remaining)
    return 0 if success else 1


def show_help():
    """Show comprehensive help message"""
    print(Fore.CYAN + "tpip - The Trump-powered pip alternative" + Style.RESET_ALL)
    print("Usage: tpip [options] <command> [args]")
    print("\n" + Fore.YELLOW + "Custom Commands:" + Style.RESET_ALL)
    print("  --test-trump-angry          Test Trump angry scenario")
    print("  --test-trump-tax-reduction  Test Trump tax reduction scenario")
    print("  --test-trump-extreme-slowdown Test Trump extreme slowdown scenario")
    print("  --test-export-control       Test export control functionality")
    print("  --about                     Show about information")
    print("  --language                  Show language information")
    print("  --tel                       Trump Export License (TEL) commands")
    
    print("\n" + Fore.YELLOW + "Pip Commands:" + Style.RESET_ALL)
    print("  install                     Install packages.")
    print("  lock                        Generate a lock file.")
    print("  download                    Download packages.")
    print("  uninstall                   Uninstall packages.")
    print("  freeze                      Output installed packages in requirements format.")
    print("  inspect                     Inspect the python environment.")
    print("  list                        List installed packages.")
    print("  show                        Show information about installed packages.")
    print("  check                       Verify installed packages have compatible dependencies.")
    print("  config                      Manage local and global configuration.")
    print("  search                      Search PyPI for packages.")
    print("  cache                       Inspect and manage pip's wheel cache.")
    print("  index                       Inspect information available from package indexes.")
    print("  wheel                       Build wheels from your requirements.")
    print("  hash                        Compute hashes of package archives.")
    print("  completion                  A helper command used for command completion.")
    print("  debug                       Show information useful for debugging.")
    print("  help                        Show help for commands.")
    
    print("\n" + Fore.YELLOW + "General Options:" + Style.RESET_ALL)
    print("  -h, --help                  Show help.")
    print("  --debug                     Let unhandled exceptions propagate.")
    print("  --isolated                  Run pip in an isolated mode.")
    print("  --require-virtualenv        Allow pip to only run in a virtual environment.")
    print("  --python <python>           Run pip with the specified Python interpreter.")
    print("  -v, --verbose               Give more output. Can be used up to 3 times.")
    print("  -V, --version               Show version and exit.")
    print("  -q, --quiet                 Give less output. Can be used up to 3 times.")
    print("  --log <path>                Path to a verbose appending log.")
    print("  --no-input                  Disable prompting for input.")
    print("  --keyring-provider <provider> Enable credential lookup via keyring.")
    print("  --proxy <proxy>             Specify a proxy.")
    print("  --retries <retries>         Maximum attempts to establish a new HTTP connection.")
    print("  --timeout <sec>             Set the socket timeout.")
    print("  --exists-action <action>    Default action when a path already exists.")
    print("  --trusted-host <hostname>   Mark this host as trusted.")
    print("  --cert <path>               Path to PEM-encoded CA certificate bundle.")
    print("  --client-cert <path>        Path to SSL client certificate.")
    print("  --cache-dir <dir>           Store the cache data in <dir>.")
    print("  --no-cache-dir              Disable the cache.")
    print("  --disable-pip-version-check Don't periodically check PyPI for new pip version.")
    print("  --no-color                  Suppress colored output.")
    print("  --use-feature <feature>     Enable new functionality.")
    print("  --use-deprecated <feature>  Enable deprecated functionality.")
    print("  --resume-retries <retries>  Maximum attempts to resume an incomplete download.")
    
    print("\n" + Fore.GREEN + "Examples:" + Style.RESET_ALL)
    print("  tpip install requests       Install a package with Trump simulations")
    print("  tpip list                   List installed packages")
    print("  tpip --test-trump-angry     Test the Trump angry scenario")
    print("  tpip --about                Show about information")
    
    print("\n" + Fore.MAGENTA + "Note: Trump policies only affect 'install' commands!" + Style.RESET_ALL)


if __name__ == "__main__":
    sys.exit(main())