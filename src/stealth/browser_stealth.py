"""
Advanced browser stealth capabilities for bypassing detection.

This module implements comprehensive browser fingerprinting protection and stealth
features to avoid detection by government sites and anti-bot systems.
"""

import random
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from playwright.async_api import Page, BrowserContext, Browser

logger = logging.getLogger(__name__)

@dataclass
class StealthProfile:
    """Configuration profile for stealth operation"""
    user_agent: str
    viewport: Dict[str, int]
    screen: Dict[str, int]
    timezone: str
    locale: str
    platform: str
    webgl_vendor: str
    webgl_renderer: str
    canvas_noise: bool = True
    webrtc_leak_protection: bool = True
    fonts: List[str] = field(default_factory=list)

class BrowserStealth:
    """Advanced browser stealth implementation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_profile = None
        
        # Realistic user agents for Spanish users
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        
        # Common viewport sizes
        self.viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1536, 'height': 864},
            {'width': 1440, 'height': 900},
            {'width': 1366, 'height': 768},
            {'width': 1280, 'height': 720},
            {'width': 1024, 'height': 768},
        ]
        
        # Spanish timezones and locales
        self.timezones = [
            'Europe/Madrid',
            'Europe/Barcelona', 
            'Atlantic/Canary'
        ]
        
        self.locales = [
            'es-ES',
            'es-ES,es;q=0.9,en;q=0.8',
            'es-ES,es;q=0.9,ca;q=0.8,en;q=0.7'
        ]
        
        # Common Spanish fonts
        self.font_families = [
            'Arial, sans-serif',
            'Helvetica, Arial, sans-serif', 
            'Times New Roman, serif',
            'Verdana, sans-serif',
            'Georgia, serif',
            'Segoe UI, Arial, sans-serif'
        ]
        
    def generate_stealth_profile(self) -> StealthProfile:
        """Generate a randomized stealth profile"""
        
        # Select random user agent
        user_agent = random.choice(self.user_agents)
        
        # Extract platform from user agent
        if 'Windows' in user_agent:
            platform = 'Win32'
            screen_scaling = random.choice([1.0, 1.25, 1.5])
        elif 'Mac' in user_agent:
            platform = 'MacIntel'
            screen_scaling = random.choice([1.0, 2.0])
        else:
            platform = 'Linux x86_64'
            screen_scaling = 1.0
            
        # Select viewport and calculate screen resolution
        viewport = random.choice(self.viewports)
        screen_width = int(viewport['width'] * screen_scaling)
        screen_height = int(viewport['height'] * screen_scaling)
        
        profile = StealthProfile(
            user_agent=user_agent,
            viewport=viewport,
            screen={
                'width': screen_width,
                'height': screen_height,
                'availWidth': screen_width,
                'availHeight': screen_height - 40,  # Account for taskbar
                'colorDepth': 24,
                'pixelDepth': 24
            },
            timezone=random.choice(self.timezones),
            locale=random.choice(self.locales),
            platform=platform,
            webgl_vendor='Google Inc. (Intel)',
            webgl_renderer=f'ANGLE (Intel, Intel(R) HD Graphics {random.randint(4000, 6000)})',
            fonts=random.sample(self.font_families, k=random.randint(3, 5))
        )
        
        self.current_profile = profile
        self.logger.info(f"Generated stealth profile: {platform}, {viewport['width']}x{viewport['height']}")
        return profile
    
    async def apply_stealth_to_context(self, context: BrowserContext, profile: StealthProfile = None) -> None:
        """Apply stealth measures to a browser context"""
        
        if profile is None:
            profile = self.generate_stealth_profile()
            
        try:
            # Apply JavaScript overrides to hide automation
            stealth_script = self._generate_stealth_script(profile)
            await context.add_init_script(stealth_script)
            
            self.logger.info("Applied stealth script to browser context")
            
        except Exception as e:
            self.logger.error(f"Failed to apply stealth to context: {e}")
            
    async def apply_stealth_to_page(self, page: Page, profile: StealthProfile = None) -> None:
        """Apply additional stealth measures to a specific page"""
        
        if profile is None:
            profile = self.current_profile or self.generate_stealth_profile()
            
        try:
            # Override navigator properties
            await page.evaluate(f'''() => {{
                Object.defineProperty(navigator, 'webdriver', {{
                    get: () => undefined,
                }});
                
                Object.defineProperty(navigator, 'plugins', {{
                    get: () => [1, 2, 3, 4, 5],
                }});
                
                Object.defineProperty(navigator, 'languages', {{
                    get: () => ['{profile.locale.split(',')[0]}'],
                }});
                
                Object.defineProperty(screen, 'width', {{
                    get: () => {profile.screen['width']},
                }});
                
                Object.defineProperty(screen, 'height', {{
                    get: () => {profile.screen['height']},
                }});
                
                // Canvas fingerprint noise
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(...args) {{
                    const context = this.getContext('2d');
                    if (context) {{
                        // Add subtle noise to canvas fingerprint
                        const imageData = context.getImageData(0, 0, this.width, this.height);
                        for (let i = 0; i < imageData.data.length; i += 4) {{
                            imageData.data[i] += Math.floor(Math.random() * 3) - 1;
                        }}
                        context.putImageData(imageData, 0, 0);
                    }}
                    return originalToDataURL.apply(this, args);
                }};
                
                // WebGL fingerprint randomization
                const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    if (parameter === 37445) {{
                        return '{profile.webgl_vendor}';
                    }}
                    if (parameter === 37446) {{
                        return '{profile.webgl_renderer}';
                    }}
                    return originalGetParameter.apply(this, arguments);
                }};
            }}''')
            
            # Add random delays to make behavior more human-like
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            self.logger.info("Applied page-level stealth measures")
            
        except Exception as e:
            self.logger.error(f"Failed to apply page stealth: {e}")
    
    def _generate_stealth_script(self, profile: StealthProfile) -> str:
        """Generate JavaScript code for stealth initialization"""
        
        return f'''
        // Hide webdriver property
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => undefined,
        }});
        
        // Override permissions API
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({{ state: Notification.permission }}) :
                originalQuery(parameters)
        );
        
        // Hide Chrome runtime
        if (window.chrome) {{
            Object.defineProperty(window.chrome, 'runtime', {{
                get: () => undefined,
            }});
        }}
        
        // Plugin array spoofing
        Object.defineProperty(navigator, 'plugins', {{
            get: () => [
                {{
                    0: {{ type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: {{}}}},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                }},
                {{
                    0: {{ type: "application/pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: {{}}}},
                    description: "Portable Document Format", 
                    filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                    length: 1,
                    name: "Chrome PDF Viewer"
                }}
            ],
        }});
        
        // Languages spoofing
        Object.defineProperty(navigator, 'languages', {{
            get: () => ['{profile.locale.split(',')[0]}'],
        }});
        
        // Platform spoofing
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{profile.platform}',
        }});
        
        // Timezone spoofing
        Date.prototype.getTimezoneOffset = function() {{
            return -{self._get_timezone_offset(profile.timezone)};
        }};
        
        // WebRTC leak protection
        if (window.RTCPeerConnection) {{
            const originalCreateDataChannel = window.RTCPeerConnection.prototype.createDataChannel;
            window.RTCPeerConnection.prototype.createDataChannel = function(...args) {{
                return originalCreateDataChannel.apply(this, args);
            }};
        }}
        
        // Audio context fingerprint randomization
        if (window.AudioContext || window.webkitAudioContext) {{
            const OriginalAudioContext = window.AudioContext || window.webkitAudioContext;
            window.AudioContext = function(...args) {{
                const audioContext = new OriginalAudioContext(...args);
                const originalCreateOscillator = audioContext.createOscillator;
                audioContext.createOscillator = function() {{
                    const oscillator = originalCreateOscillator.apply(this);
                    const originalFrequency = oscillator.frequency.value;
                    oscillator.frequency.value = originalFrequency + Math.random() * 0.001;
                    return oscillator;
                }};
                return audioContext;
            }};
        }}
        '''
    
    def _get_timezone_offset(self, timezone: str) -> int:
        """Get timezone offset in minutes for spoofing"""
        timezone_offsets = {
            'Europe/Madrid': -60,  # UTC+1 in winter, UTC+2 in summer
            'Europe/Barcelona': -60,
            'Atlantic/Canary': 0,   # UTC+0 in winter, UTC+1 in summer
        }
        return timezone_offsets.get(timezone, -60)
    
    async def rotate_profile(self, context: BrowserContext) -> StealthProfile:
        """Generate and apply a new stealth profile"""
        
        profile = self.generate_stealth_profile()
        await self.apply_stealth_to_context(context, profile)
        
        self.logger.info("Rotated to new stealth profile")
        return profile
    
    def get_current_profile(self) -> Optional[StealthProfile]:
        """Get the currently active stealth profile"""
        return self.current_profile
