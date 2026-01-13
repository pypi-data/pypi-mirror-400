"""
Trump policy simulator for none_pip
"""

import random
import time
import os
import sys
from typing import Optional, Tuple
from .language import lang_manager


class TrumpSimulator:
    """Simulate Trump's unpredictable policies"""
    
    def __init__(self):
        self.chances = {
            'tax_cut': 0.70,       # 70% chance of tax cuts slowing download (1-60%)
            'extreme_slowdown': 0.20,  # 20% chance of extreme slowdown (90-99%)
            'trump_angry': 0.05,    # 5% chance of Trump getting angry
            'normal': 0.05,         # 5% chance of normal operation
        }
    
    def simulate_policy(self) -> Tuple[str, Optional[int], Optional[bool]]:
        """
        Simulate a Trump policy event
        
        Returns:
            Tuple of (policy_type, percentage_change, should_cancel)
        """
        rand = random.random()
        cumulative = 0
        
        for policy, chance in self.chances.items():
            cumulative += chance
            if rand <= cumulative:
                if policy == 'tax_cut':
                    # 1-60% random slowdown
                    slowdown = random.randint(1, 60)
                    return 'tax_cut', -slowdown, False
                
                elif policy == 'extreme_slowdown':
                    # 90-99% extreme slowdown
                    slowdown = random.randint(90, 99)
                    return 'extreme_slowdown', -slowdown, False
                
                elif policy == 'trump_angry':
                    # Trump gets angry!
                    return 'trump_angry', None, True
                
                else:  # normal
                    return 'normal', 0, False
        
        # Fallback
        return 'normal', 0, False
    
    def apply_policy_effects(self, policy_type: str, percentage: Optional[int], 
                            should_cancel: bool, package_name: str) -> bool:
        """
        Apply the policy effects and show appropriate messages
        
        Returns:
            bool: True if installation should continue, False if cancelled
        """
        from colorama import Fore, Style, init
        init()  # Initialize colorama
        
        if policy_type == 'tax_cut':
            print(Fore.YELLOW + lang_manager.get('tax_cut', abs(percentage)) + Style.RESET_ALL)
            # Simulate slowdown with progress bar
            self._show_progress_bar(100 + percentage)  # percentage is negative
            return True
            
        elif policy_type == 'extreme_slowdown':
            print(Fore.MAGENTA + "🚨 " + lang_manager.get('extreme_slowdown', abs(percentage)) + Style.RESET_ALL)
            # Simulate extreme slowdown with progress bar
            self._show_progress_bar(100 + percentage)  # percentage is negative (e.g., -95%)
            return True
            
        elif policy_type == 'trump_angry':
            print(Fore.RED + "💥 " + lang_manager.get('trump_angry') + Style.RESET_ALL)
            
            # 70% chance of closing terminal immediately
            if random.random() < 0.7:
                print(Fore.RED + "🚨 TRUMP IS FURIOUS! Terminal will close in 3 seconds..." + Style.RESET_ALL)
                time.sleep(3)
                
                # Try to close terminal (platform specific)
                self._close_terminal()
            else:
                # 30% chance of simulated system shutdown
                print(Fore.RED + "⚠️  SYSTEM SHUTDOWN INITIATED BY TRUMP!" + Style.RESET_ALL)
                print(Fore.RED + "Initiating emergency shutdown sequence..." + Style.RESET_ALL)
                
                # Simulate shutdown sequence
                for i in range(5, 0, -1):
                    print(Fore.RED + f"Shutting down in {i}..." + Style.RESET_ALL)
                    time.sleep(1)
                
                print(Fore.RED + "💀 SYSTEM SHUTDOWN COMPLETE. Terminal closing..." + Style.RESET_ALL)
                time.sleep(2)
                
                # Close terminal
                self._close_terminal()
            
            return False
            
        else:  # normal
            # Normal installation with progress bar
            self._show_progress_bar(100)
            return True
    
    def _show_progress_bar(self, speed_percentage: int):
        """Show a fake progress bar with simulated speed"""
        import time
        
        print("Downloading: [", end="")
        bar_length = 20
        
        # Calculate delay based on speed percentage
        # 100% = normal speed, <100% = slower, >100% = faster
        base_delay = 0.1
        actual_delay = base_delay * (100 / speed_percentage)
        
        for i in range(bar_length + 1):
            progress = i * 5  # 0-100%
            bar = "=" * i + " " * (bar_length - i)
            print(f"\rDownloading: [{bar}] {progress}%", end="", flush=True)
            time.sleep(actual_delay)
        
        print("] Done!")
    
    def _close_terminal(self):
        """Attempt to close the terminal (platform specific) - More aggressive approach"""
        print(Fore.RED + "🚨 TRUMP IS ANGRY! Closing terminal in 3... 2... 1..." + Style.RESET_ALL)
        time.sleep(3)
        
        try:
            if sys.platform == "win32":
                # Windows - multiple methods
                print(Fore.RED + "Closing Windows terminal..." + Style.RESET_ALL)
                # Method 1: taskkill current process tree
                os.system("taskkill /F /PID %d /T" % os.getpid())
                # Method 2: taskkill parent process (terminal)
                os.system("taskkill /F /PID %d /T" % os.getppid())
                # Method 3: exit with extreme prejudice
                os._exit(1)
                
            elif sys.platform == "darwin":
                # macOS
                print(Fore.RED + "Closing macOS terminal..." + Style.RESET_ALL)
                # Method 1: Kill terminal app
                os.system("pkill -f Terminal")
                os.system("pkill -f iTerm")
                # Method 2: Kill parent process
                os.kill(os.getppid(), 9)  # SIGKILL
                # Method 3: Force exit
                os._exit(1)
                
            elif "android" in sys.platform.lower() or "termux" in sys.platform.lower():
                # Android/Termux
                print(Fore.RED + "Closing Termux terminal..." + Style.RESET_ALL)
                # Method 1: Kill Termux session
                os.system("pkill -9 com.termux")
                # Method 2: Kill parent process
                os.kill(os.getppid(), 9)  # SIGKILL
                # Method 3: Force exit
                os._exit(1)
                
            else:
                # Linux and other Unix-like systems
                print(Fore.RED + "Closing Linux terminal..." + Style.RESET_ALL)
                # Method 1: Kill terminal emulator
                os.system("pkill -9 gnome-terminal")
                os.system("pkill -9 konsole")
                os.system("pkill -9 xterm")
                os.system("pkill -9 urxvt")
                # Method 2: Kill parent process with SIGKILL
                os.kill(os.getppid(), 9)  # SIGKILL
                # Method 3: Kill entire process group
                os.killpg(os.getpgid(os.getpid()), 9)
                # Method 4: Nuclear option
                os._exit(1)
                
        except Exception as e:
            print(Fore.YELLOW + f"Terminal close attempt failed: {e}" + Style.RESET_ALL)
            print(Fore.RED + "Using emergency exit..." + Style.RESET_ALL)
            # Last resort: force exit
            os._exit(1)


# Global simulator instance
trump_simulator = TrumpSimulator()