#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль захисту приватності для AnDetect Browser
Містить розширені методи захисту від трекінгу та fingerprinting
"""

import json
import random
import time
import hashlib
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineProfile


class TrackingBlocker:
    """Блокувальник трекерів та реклами"""
    
    def __init__(self):
        self.blocked_domains = set()
        self.tracking_patterns = []
        self.load_blocklists()
    
    def load_blocklists(self):
        """Завантаження списків блокування"""
        # Базові домени трекерів
        self.blocked_domains.update([
            'google-analytics.com',
            'googletagmanager.com',
            'facebook.com',
            'doubleclick.net',
            'googlesyndication.com',
            'amazon-adsystem.com',
            'googleadservices.com',
            'googletag.com',
            'adsystem.amazon.com',
            'scorecardresearch.com',
            'quantserve.com',
            'outbrain.com',
            'taboola.com',
            'addthis.com',
            'sharethrough.com'
        ])
        
        # Патерни для блокування
        self.tracking_patterns = [
            'track',
            'analytics',
            'pixel',
            'beacon',
            'telemetry',
            'metrics',
            'stats',
            'counter'
        ]
    
    def should_block(self, url: str) -> bool:
        """Перевірка чи потрібно блокувати URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Перевірка доменів
        for blocked_domain in self.blocked_domains:
            if blocked_domain in domain:
                return True
        
        # Перевірка патернів
        url_lower = url.lower()
        for pattern in self.tracking_patterns:
            if pattern in url_lower:
                return True
        
        return False


class FingerprintProtection:
    """Захист від fingerprinting"""
    
    def __init__(self):
        self.canvas_noise_enabled = True
        self.webgl_noise_enabled = True
        self.audio_noise_enabled = True
        self.timezone_spoofing = True
        self.language_spoofing = True
    
    def get_canvas_protection_script(self) -> str:
        """JavaScript код для захисту Canvas"""
        return """
        (function() {
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            
            // Функція для додавання шуму
            function addNoise(imageData) {
                const data = imageData.data;
                for (let i = 0; i < data.length; i += 4) {
                    // Додаємо випадковий шум до RGB каналів
                    data[i] += Math.floor(Math.random() * 3) - 1;     // R
                    data[i + 1] += Math.floor(Math.random() * 3) - 1; // G
                    data[i + 2] += Math.floor(Math.random() * 3) - 1; // B
                    // Alpha канал залишаємо незмінним
                }
                return imageData;
            }
            
            HTMLCanvasElement.prototype.getContext = function(type, attributes) {
                const context = originalGetContext.call(this, type, attributes);
                
                if (type === '2d' && context) {
                    context.getImageData = function() {
                        const imageData = originalGetImageData.apply(this, arguments);
                        return addNoise(imageData);
                    };
                }
                
                return context;
            };
            
            HTMLCanvasElement.prototype.toDataURL = function() {
                // Додаємо мікроскопічні зміни до canvas перед експортом
                const context = this.getContext('2d');
                if (context) {
                    const originalFillStyle = context.fillStyle;
                    context.fillStyle = `rgba(${Math.random()}, ${Math.random()}, ${Math.random()}, 0.001)`;
                    context.fillRect(0, 0, 1, 1);
                    context.fillStyle = originalFillStyle;
                }
                return originalToDataURL.apply(this, arguments);
            };
        })();
        """
    
    def get_webgl_protection_script(self) -> str:
        """JavaScript код для захисту WebGL"""
        return """
        (function() {
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            const getExtension = WebGLRenderingContext.prototype.getExtension;
            
            // Список параметрів для спуфінгу
            const spoofedParams = {
                37445: 'Intel Inc.',  // VENDOR
                37446: 'Intel(R) HD Graphics 620',  // RENDERER
                7936: 'WebGL 1.0',   // VERSION
                35724: 'WebGL GLSL ES 1.0'  // SHADING_LANGUAGE_VERSION
            };
            
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (spoofedParams[parameter]) {
                    return spoofedParams[parameter];
                }
                return getParameter.call(this, parameter);
            };
            
            // Блокування деяких розширень
            WebGLRenderingContext.prototype.getExtension = function(name) {
                const blockedExtensions = [
                    'WEBGL_debug_renderer_info',
                    'WEBGL_debug_shaders'
                ];
                
                if (blockedExtensions.includes(name)) {
                    return null;
                }
                
                return getExtension.call(this, name);
            };
        })();
        """
    
    def get_audio_protection_script(self) -> str:
        """JavaScript код для захисту від Audio fingerprinting"""
        return """
        (function() {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            
            if (AudioContext) {
                const OriginalAudioContext = AudioContext;
                
                function SpoofeAudioContext() {
                    const context = new OriginalAudioContext();
                    
                    const originalCreateOscillator = context.createOscillator;
                    context.createOscillator = function() {
                        const oscillator = originalCreateOscillator.call(this);
                        
                        const originalStart = oscillator.start;
                        oscillator.start = function(when) {
                            // Додаємо мікроскопічні зміни до частоти
                            oscillator.frequency.value += (Math.random() - 0.5) * 0.0001;
                            return originalStart.call(this, when);
                        };
                        
                        return oscillator;
                    };
                    
                    return context;
                }
                
                window.AudioContext = SpoofeAudioContext;
                if (window.webkitAudioContext) {
                    window.webkitAudioContext = SpoofeAudioContext;
                }
            }
        })();
        """
    
    def get_navigator_protection_script(self) -> str:
        """JavaScript код для спуфінгу navigator об'єкта"""
        return """
        (function() {
            // Спуфінг геолокації
            if (navigator.geolocation) {
                const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;
                navigator.geolocation.getCurrentPosition = function(success, error) {
                    if (error) {
                        error({
                            code: 1,
                            message: "User denied the request for Geolocation."
                        });
                    }
                };
                
                navigator.geolocation.watchPosition = function(success, error) {
                    return navigator.geolocation.getCurrentPosition(success, error);
                };
            }
            
            // Спуфінг часового поясу
            const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
            Date.prototype.getTimezoneOffset = function() {
                return 0; // UTC
            };
            
            // Спуфінг мови
            Object.defineProperty(navigator, 'language', {
                get: function() { return 'en-US'; }
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: function() { return ['en-US', 'en']; }
            });
            
            // Спуфінг платформи
            Object.defineProperty(navigator, 'platform', {
                get: function() { return 'Win32'; }
            });
            
            // Спуфінг кількості ядер CPU
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: function() { return 4; }
            });
            
            // Спуфінг пам'яті
            if (navigator.deviceMemory) {
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: function() { return 8; }
                });
            }
            
            // Блокування WebRTC
            if (window.RTCPeerConnection) {
                window.RTCPeerConnection = function() {
                    throw new Error('WebRTC is blocked for privacy');
                };
            }
            
            if (window.webkitRTCPeerConnection) {
                window.webkitRTCPeerConnection = function() {
                    throw new Error('WebRTC is blocked for privacy');
                };
            }
            
            if (window.mozRTCPeerConnection) {
                window.mozRTCPeerConnection = function() {
                    throw new Error('WebRTC is blocked for privacy');
                };
            }
        })();
        """
    
    def get_font_protection_script(self) -> str:
        """JavaScript код для захисту від Font fingerprinting"""
        return """
        (function() {
            // Список стандартних шрифтів
            const standardFonts = [
                'Arial', 'Arial Black', 'Arial Narrow', 'Arial Unicode MS',
                'Calibri', 'Cambria', 'Courier', 'Courier New',
                'Geneva', 'Georgia', 'Helvetica', 'Helvetica Neue',
                'Impact', 'Lucida Console', 'Lucida Grande', 'Lucida Sans Unicode',
                'Microsoft Sans Serif', 'Monaco', 'Palatino', 'Tahoma',
                'Times', 'Times New Roman', 'Trebuchet MS', 'Verdana'
            ];
            
            // Перевизначення методів перевірки шрифтів
            if (document.fonts && document.fonts.check) {
                const originalCheck = document.fonts.check;
                document.fonts.check = function(font) {
                    const fontFamily = font.split(' ').pop().replace(/['"]/g, '');
                    return standardFonts.includes(fontFamily);
                };
            }
            
            // Блокування FontFace API
            if (window.FontFace) {
                window.FontFace = function() {
                    throw new Error('FontFace API blocked for privacy');
                };
            }
        })();
        """
    
    def get_screen_protection_script(self) -> str:
        """JavaScript код для спуфінгу інформації про екран"""
        return """
        (function() {
            // Стандартні розміри екрану
            const commonResolutions = [
                {width: 1920, height: 1080},
                {width: 1366, height: 768},
                {width: 1280, height: 1024},
                {width: 1440, height: 900},
                {width: 1680, height: 1050}
            ];
            
            const selectedResolution = commonResolutions[Math.floor(Math.random() * commonResolutions.length)];
            
            Object.defineProperty(screen, 'width', {
                get: function() { return selectedResolution.width; }
            });
            
            Object.defineProperty(screen, 'height', {
                get: function() { return selectedResolution.height; }
            });
            
            Object.defineProperty(screen, 'availWidth', {
                get: function() { return selectedResolution.width; }
            });
            
            Object.defineProperty(screen, 'availHeight', {
                get: function() { return selectedResolution.height - 40; }
            });
            
            Object.defineProperty(screen, 'colorDepth', {
                get: function() { return 24; }
            });
            
            Object.defineProperty(screen, 'pixelDepth', {
                get: function() { return 24; }
            });
        })();
        """
    
    def get_complete_protection_script(self) -> str:
        """Повний JavaScript код захисту"""
        scripts = [
            self.get_canvas_protection_script(),
            self.get_webgl_protection_script(),
            self.get_audio_protection_script(),
            self.get_navigator_protection_script(),
            self.get_font_protection_script(),
            self.get_screen_protection_script()
        ]
        
        return '\n'.join(scripts)


class UserAgentGenerator:
    """Генератор випадкових User-Agent строк"""
    
    def __init__(self):
        self.chrome_versions = ['119.0.0.0', '118.0.0.0', '117.0.0.0', '116.0.0.0']
        self.windows_versions = ['10.0', '11.0']
        self.webkit_versions = ['537.36']
    
    def generate_chrome_ua(self) -> str:
        """Генерація Chrome User-Agent"""
        chrome_version = random.choice(self.chrome_versions)
        windows_version = random.choice(self.windows_versions)
        webkit_version = random.choice(self.webkit_versions)
        
        return (
            f"Mozilla/5.0 (Windows NT {windows_version}; Win64; x64) "
            f"AppleWebKit/{webkit_version} (KHTML, like Gecko) "
            f"Chrome/{chrome_version} Safari/{webkit_version}"
        )
    
    def generate_firefox_ua(self) -> str:
        """Генерація Firefox User-Agent"""
        firefox_version = random.randint(110, 120)
        
        return (
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{firefox_version}.0) "
            f"Gecko/20100101 Firefox/{firefox_version}.0"
        )
    
    def generate_edge_ua(self) -> str:
        """Генерація Edge User-Agent"""
        edge_version = random.choice(['119.0.0.0', '118.0.0.0'])
        
        return (
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{edge_version} Safari/537.36 Edg/{edge_version}"
        )
    
    def get_random_ua(self) -> str:
        """Отримання випадкового User-Agent"""
        generators = [
            self.generate_chrome_ua,
            self.generate_firefox_ua,
            self.generate_edge_ua
        ]
        
        return random.choice(generators)()


class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    """Перехоплювач запитів для блокування трекерів"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tracker_blocker = TrackingBlocker()
        self.blocked_count = 0
    
    def interceptRequest(self, info):
        """Перехоплення та фільтрація запитів"""
        url = info.requestUrl().toString()
        
        if self.tracker_blocker.should_block(url):
            info.block(True)
            self.blocked_count += 1
            print(f"Blocked tracker: {url}")
    
    def get_blocked_count(self) -> int:
        """Отримання кількості заблокованих запитів"""
        return self.blocked_count
    
    def reset_blocked_count(self):
        """Скидання лічильника заблокованих запитів"""
        self.blocked_count = 0


class PrivacyManager(QObject):
    """Менеджер приватності"""
    
    privacy_level_changed = pyqtSignal(str)
    trackers_blocked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fingerprint_protection = FingerprintProtection()
        self.ua_generator = UserAgentGenerator()
        self.request_interceptor = RequestInterceptor()
        
        # Таймер для оновлення статистики
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(5000)  # Кожні 5 секунд
    
    def setup_profile_privacy(self, profile: QWebEngineProfile, settings: Dict[str, Any]):
        """Налаштування приватності профілю"""
        # Налаштування кешу
        if settings.get('private_mode', True):
            profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        
        # Налаштування User-Agent
        if settings.get('randomize_user_agent', True):
            profile.setHttpUserAgent(self.ua_generator.get_random_ua())
        
        # Встановлення перехоплювача запитів
        profile.setUrlRequestInterceptor(self.request_interceptor)
        
        # Налаштування заголовків
        profile.setHttpAcceptLanguage("en-US,en;q=0.9")
    
    def inject_protection_scripts(self, page):
        """Інжекція скриптів захисту"""
        if self.fingerprint_protection.canvas_noise_enabled:
            page.runJavaScript(self.fingerprint_protection.get_complete_protection_script())
    
    def update_stats(self):
        """Оновлення статистики"""
        blocked_count = self.request_interceptor.get_blocked_count()
        self.trackers_blocked.emit(blocked_count)
    
    def clear_tracking_data(self, profile: QWebEngineProfile):
        """Очищення даних трекінгу"""
        profile.clearAllVisitedLinks()
        profile.clearHttpCache()
        self.request_interceptor.reset_blocked_count()
    
    def get_privacy_level(self, settings: Dict[str, Any]) -> str:
        """Визначення рівня приватності"""
        score = 0
        
        if settings.get('tor_enabled', False):
            score += 30
        if settings.get('proxy_enabled', False):
            score += 20
        if settings.get('anti_fingerprint', True):
            score += 20
        if settings.get('block_webrtc', True):
            score += 10
        if settings.get('randomize_user_agent', True):
            score += 10
        if settings.get('clear_on_exit', True):
            score += 10
        
        if score >= 70:
            return "Висока"
        elif score >= 40:
            return "Середня"
        else:
            return "Низька"
