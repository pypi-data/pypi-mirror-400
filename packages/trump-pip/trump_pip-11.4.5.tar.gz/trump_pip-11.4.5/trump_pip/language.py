"""
Language detection and internationalization support for none_pip
"""

import os
import locale
import random
from typing import Dict, Tuple


class LanguageManager:
    """Manage language detection and translations"""
    
    def __init__(self):
        self.current_lang = self.detect_language()
        self.translations = self._load_translations()
    
    def detect_language(self) -> str:
        """Detect system language"""
        try:
            # Try to get system language
            lang, _ = locale.getdefaultlocale()
            if lang:
                lang = lang.lower()
                if 'zh' in lang:
                    return 'zh'
                elif 'ja' in lang:
                    return 'ja'
                elif 'ko' in lang:
                    return 'ko'
        except:
            pass
        
        # Check environment variables
        env_lang = os.environ.get('LANG', '').lower()
        if 'zh' in env_lang:
            return 'zh'
        elif 'ja' in env_lang:
            return 'ja'
        elif 'ko' in env_lang:
            return 'ko'
        
        # Default to English
        return 'en'
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load all translations"""
        return {
            'en': {
                'welcome': "Welcome to npip - The Trump-powered pip!",
                'installing': "Installing package: {}",
                'success': "Package installed successfully!",
                'tax_cut': "Due to Trump's tax cuts, your download speed decreased by {}%",
                'extreme_slowdown': "EXTREME NETWORK RESTRICTION: {}% slowdown! Trump's policies throttled your connection!",
                'tax_increase': "Due to Trump's tax increases, your download speed increased by {}%",
                'trump_angry': "Trump got angry and slapped you! Download cancelled.",
                'closing_terminal': "Closing terminal in 1.014 seconds...",
                'shutting_down': "System shutting down due to Trump's anger!",
                'error': "Error: {}",
                'help': "Usage: npip install <package_name>",
                'made_by': "Made by ruin321 and schooltaregf",
            },
            'zh': {
                'welcome': "欢迎使用 npip - 特朗普驱动的pip！",
                'installing': "正在安装包: {}",
                'success': "包安装成功！",
                'tax_cut': "由于特朗普的减税，你的下载速度降低了 {}%",
                'extreme_slowdown': "极端网络限制：{}% 减速！特朗普的政策严重限制了你的网络连接！",
                'tax_increase': "由于特朗普的增税，你的下载速度提升了 {}%",
                'trump_angry': "特朗普生气了，一巴掌把你扇死了！下载取消。",
                'closing_terminal': "1.014秒后关闭终端...",
                'shutting_down': "由于特朗普的愤怒，系统正在关闭！",
                'error': "错误: {}",
                'help': "用法: npip install <包名>",
                'made_by': "制作者: ruin321 和 schooltaregf",
            },
            'ja': {
                'welcome': "npipへようこそ - トランプが動かすpip！",
                'installing': "パッケージをインストール中: {}",
                'success': "パッケージのインストールが成功しました！",
                'tax_cut': "トランプの減税により、ダウンロード速度が {}% 低下しました",
                'extreme_slowdown': "極端なネットワーク制限：{}% 速度低下！トランプの政策が接続を大幅に制限しました！",
                'tax_increase': "トランプの増税により、ダウンロード速度が {}% 向上しました",
                'trump_angry': "トランプが怒ってあなたを平手打ちしました！ダウンロードをキャンセルします。",
                'closing_terminal': "1.014秒後にターミナルを閉じます...",
                'shutting_down': "トランプの怒りのため、システムをシャットダウンします！",
                'error': "エラー: {}",
                'help': "使用方法: npip install <パッケージ名>",
                'made_by': "製作者: ruin321 と schooltaregf",
            },
            'ko': {
                'welcome': "npip에 오신 것을 환영합니다 - 트럼프가 구동하는 pip!",
                'installing': "패키지 설치 중: {}",
                'success': "패키지 설치 성공!",
                'tax_cut': "트럼프의 감세로 인해 다운로드 속도가 {}% 감소했습니다",
                'extreme_slowdown': "극단적인 네트워크 제한: {}% 속도 저하! 트럼프의 정책이 연결을 심각하게 제한했습니다!",
                'tax_increase': "트럼프의 증세로 인해 다운로드 속도가 {}% 증가했습니다",
                'trump_angry': "트럼프가 화나서 당신을 때렸습니다! 다운로드가 취소되었습니다.",
                'closing_terminal': "1.014초 후에 터미널을 닫습니다...",
                'shutting_down': "트럼프의 분노로 인해 시스템을 종료합니다!",
                'error': "오류: {}",
                'help': "사용법: npip install <패키지명>",
                'made_by': "제작자: ruin321 및 schooltaregf",
            }
        }
    
    def get(self, key: str, *args) -> str:
        """Get translated string with formatting"""
        translation = self.translations.get(self.current_lang, self.translations['en'])
        text = translation.get(key, key)
        
        if args:
            try:
                return text.format(*args)
            except:
                return text
        return text
    
    def show_welcome(self):
        """Show welcome message"""
        print(self.get('welcome'))
        print(self.get('made_by'))
        print()


# Global language manager instance
lang_manager = LanguageManager()