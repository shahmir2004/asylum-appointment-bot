"""
Stealth module for asylum appointment booking bot.

This module provides comprehensive anti-detection capabilities including:
- Browser fingerprint randomization
- Proxy rotation and management
- Human behavior simulation
- CAPTCHA solving integration
- Advanced evasion techniques
"""

__version__ = "1.0.0"
__author__ = "Asylum Bot Development Team"

from .browser_stealth import BrowserStealth
from .behavior_simulator import BehaviorSimulator
# from .proxy_manager import ProxyManager
# from .captcha_solver import CaptchaSolver
# from .detection_evasion import DetectionEvasion

__all__ = [
    'BrowserStealth',
    'BehaviorSimulator',
    # 'ProxyManager', 
    # 'CaptchaSolver',
    # 'DetectionEvasion'
]
