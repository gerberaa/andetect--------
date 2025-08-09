<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Кастомна веб-сторінка з підтримкою маскування відбитків браузера
"""

from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile
from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
import random
import json


class FingerprintMasker:
    """Клас для маскування відбитків браузера"""
    
    @staticmethod
    def get_random_user_agent():
        """Генерація випадкового User-Agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]
        return random.choice(user_agents)
    
    @staticmethod
    def get_canvas_fingerprint_script():
        """JavaScript для маскування Canvas fingerprinting"""
        return """
        (function() {
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            
            // Додаємо шум до Canvas
            function addNoise(imageData) {
                const data = imageData.data;
                for (let i = 0; i < data.length; i += 4) {
                    if (Math.random() < 0.1) {
                        data[i] = Math.min(255, data[i] + Math.floor(Math.random() * 10) - 5);
                        data[i + 1] = Math.min(255, data[i + 1] + Math.floor(Math.random() * 10) - 5);
                        data[i + 2] = Math.min(255, data[i + 2] + Math.floor(Math.random() * 10) - 5);
                    }
                }
                return imageData;
            }
            
            CanvasRenderingContext2D.prototype.getImageData = function(...args) {
                return addNoise(originalGetImageData.apply(this, args));
            };
            
            HTMLCanvasElement.prototype.toDataURL = function(...args) {
                const context = this.getContext('2d');
                if (context) {
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    addNoise(imageData);
                    context.putImageData(imageData, 0, 0);
                }
                return originalToDataURL.apply(this, args);
            };
        })();
        """
    
    @staticmethod
    def get_webgl_fingerprint_script():
        """JavaScript для маскування WebGL fingerprinting"""
        return """
        (function() {
            const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
            const originalGetExtension = WebGLRenderingContext.prototype.getExtension;
            
            // Підміняємо WebGL параметри
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                const fakeParams = {
                    7936: 'Intel Inc.',  // VENDOR
                    7937: 'Intel(R) HD Graphics',  // RENDERER
                    35724: 'WebGL 1.0 (OpenGL ES 2.0 Chromium)',  // VERSION
                    34921: 'WEBGL_lose_context GL_OES_texture_float',  // EXTENSIONS
                };
                
                if (fakeParams.hasOwnProperty(parameter)) {
                    return fakeParams[parameter];
                }
                
                return originalGetParameter.call(this, parameter);
            };
            
            // Блокуємо деякі розширення
            WebGLRenderingContext.prototype.getExtension = function(name) {
                const blockedExtensions = [
                    'WEBGL_debug_renderer_info',
                    'WEBGL_debug_shaders'
                ];
                
                if (blockedExtensions.includes(name)) {
                    return null;
                }
                
                return originalGetExtension.call(this, name);
            };
        })();
        """
    
    @staticmethod
    def get_timezone_script():
        """JavaScript для маскування часового поясу"""
        return """
        (function() {
            const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
            
            Date.prototype.getTimezoneOffset = function() {
                return -120; // UTC+2 (Київ)
            };
            
            // Підміняємо Intl.DateTimeFormat
            if (window.Intl && window.Intl.DateTimeFormat) {
                const originalResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
                Intl.DateTimeFormat.prototype.resolvedOptions = function() {
                    const options = originalResolvedOptions.call(this);
                    options.timeZone = 'Europe/Kiev';
                    return options;
                };
            }
        })();
        """
    
    @staticmethod
    def get_screen_fingerprint_script():
        """JavaScript для маскування параметрів екрану"""
        return """
        (function() {
            const screenWidth = 1920;
            const screenHeight = 1080;
            const availWidth = 1920;
            const availHeight = 1040;
            
            Object.defineProperty(screen, 'width', {
                get: function() { return screenWidth; }
            });
            
            Object.defineProperty(screen, 'height', {
                get: function() { return screenHeight; }
            });
            
            Object.defineProperty(screen, 'availWidth', {
                get: function() { return availWidth; }
            });
            
            Object.defineProperty(screen, 'availHeight', {
                get: function() { return availHeight; }
            });
            
            Object.defineProperty(screen, 'colorDepth', {
                get: function() { return 24; }
            });
            
            Object.defineProperty(screen, 'pixelDepth', {
                get: function() { return 24; }
            });
        })();
        """

    @staticmethod
    def get_webrtc_block_script():
        """JavaScript для блокування WebRTC"""
        return """
        (function() {
            // Блокуємо WebRTC
            const noop = function() {};
            
            window.RTCPeerConnection = noop;
            window.RTCSessionDescription = noop;
            window.RTCIceCandidate = noop;
            window.webkitRTCPeerConnection = noop;
            window.mozRTCPeerConnection = noop;
            
            navigator.getUserMedia = noop;
            navigator.webkitGetUserMedia = noop;
            navigator.mozGetUserMedia = noop;
            navigator.mediaDevices = {
                getUserMedia: noop,
                enumerateDevices: function() { 
                    return Promise.resolve([]); 
                }
            };
        })();
        """


class UrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """Перехоплювач запитів для блокування трекерів"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blocked_domains = set([
            'google-analytics.com',
            'googletagmanager.com',
            'facebook.com/tr',
            'doubleclick.net',
            'googlesyndication.com',
            'amazon-adsystem.com',
            'adsystem.amazon.com'
        ])
    
    def interceptRequest(self, info):
        """Перехоплення та блокування запитів"""
        url = info.requestUrl().toString()
        
        # Блокуємо трекери
        for domain in self.blocked_domains:
            if domain in url:
                info.block(True)
                return


class AnDetectWebPage(QWebEnginePage):
    """Кастомна веб-сторінка з маскуванням відбитків"""
    
    def __init__(self, profile_data, parent=None):
        # Створюємо кастомний профіль
        web_profile = QWebEngineProfile(profile_data.name if profile_data else "default", parent)
        
        super().__init__(web_profile, parent)
        
        self.profile_data = profile_data
        self.masker = FingerprintMasker()
        
        # Встановлюємо User-Agent
        if profile_data and hasattr(profile_data, 'user_agent') and profile_data.user_agent:
            user_agent = profile_data.user_agent
        else:
            user_agent = self.masker.get_random_user_agent()
            
        web_profile.setHttpUserAgent(user_agent)
        
        # Налаштовуємо перехоплювач запитів
        self.interceptor = UrlRequestInterceptor(self)
        web_profile.setUrlRequestInterceptor(self.interceptor)
        
        # Вимикаємо WebRTC в налаштуваннях
        web_profile.settings().setAttribute(
            web_profile.settings().WebRTCPublicInterfacesOnly, True
        )
        
        # Підключаємо сигнали
        self.loadFinished.connect(self.inject_fingerprint_scripts)
        
    def inject_fingerprint_scripts(self, success):
        """Вбудовування скриптів маскування після завантаження сторінки"""
        if success:
            # Вбудовуємо всі скрипти маскування
            scripts = [
                self.masker.get_canvas_fingerprint_script(),
                self.masker.get_webgl_fingerprint_script(),
                self.masker.get_timezone_script(),
                self.masker.get_screen_fingerprint_script(),
                self.masker.get_webrtc_block_script()
            ]
            
            for script in scripts:
                self.runJavaScript(script)
                
    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        """Перевірка навігаційних запитів"""
        # Можна додати додаткову логіку фільтрації
        return super().acceptNavigationRequest(url, navigation_type, is_main_frame)
        
    def javaScriptAlert(self, security_origin, message):
        """Обробка JavaScript alert"""
        # Можна додати кастомну обробку
        super().javaScriptAlert(security_origin, message)
        
    def javaScriptConfirm(self, security_origin, message):
        """Обробка JavaScript confirm"""
        # Можна додати кастомну обробку
        return super().javaScriptConfirm(security_origin, message)
=======
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Кастомна веб-сторінка з підтримкою маскування відбитків браузера
"""

from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile
from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
import random
import json


class FingerprintMasker:
    """Клас для маскування відбитків браузера"""
    
    @staticmethod
    def get_random_user_agent():
        """Генерація випадкового User-Agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]
        return random.choice(user_agents)
    
    @staticmethod
    def get_canvas_fingerprint_script():
        """JavaScript для маскування Canvas fingerprinting"""
        return """
        (function() {
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            
            // Додаємо шум до Canvas
            function addNoise(imageData) {
                const data = imageData.data;
                for (let i = 0; i < data.length; i += 4) {
                    if (Math.random() < 0.1) {
                        data[i] = Math.min(255, data[i] + Math.floor(Math.random() * 10) - 5);
                        data[i + 1] = Math.min(255, data[i + 1] + Math.floor(Math.random() * 10) - 5);
                        data[i + 2] = Math.min(255, data[i + 2] + Math.floor(Math.random() * 10) - 5);
                    }
                }
                return imageData;
            }
            
            CanvasRenderingContext2D.prototype.getImageData = function(...args) {
                return addNoise(originalGetImageData.apply(this, args));
            };
            
            HTMLCanvasElement.prototype.toDataURL = function(...args) {
                const context = this.getContext('2d');
                if (context) {
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    addNoise(imageData);
                    context.putImageData(imageData, 0, 0);
                }
                return originalToDataURL.apply(this, args);
            };
        })();
        """
    
    @staticmethod
    def get_webgl_fingerprint_script():
        """JavaScript для маскування WebGL fingerprinting"""
        return """
        (function() {
            const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
            const originalGetExtension = WebGLRenderingContext.prototype.getExtension;
            
            // Підміняємо WebGL параметри
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                const fakeParams = {
                    7936: 'Intel Inc.',  // VENDOR
                    7937: 'Intel(R) HD Graphics',  // RENDERER
                    35724: 'WebGL 1.0 (OpenGL ES 2.0 Chromium)',  // VERSION
                    34921: 'WEBGL_lose_context GL_OES_texture_float',  // EXTENSIONS
                };
                
                if (fakeParams.hasOwnProperty(parameter)) {
                    return fakeParams[parameter];
                }
                
                return originalGetParameter.call(this, parameter);
            };
            
            // Блокуємо деякі розширення
            WebGLRenderingContext.prototype.getExtension = function(name) {
                const blockedExtensions = [
                    'WEBGL_debug_renderer_info',
                    'WEBGL_debug_shaders'
                ];
                
                if (blockedExtensions.includes(name)) {
                    return null;
                }
                
                return originalGetExtension.call(this, name);
            };
        })();
        """
    
    @staticmethod
    def get_timezone_script():
        """JavaScript для маскування часового поясу"""
        return """
        (function() {
            const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
            
            Date.prototype.getTimezoneOffset = function() {
                return -120; // UTC+2 (Київ)
            };
            
            // Підміняємо Intl.DateTimeFormat
            if (window.Intl && window.Intl.DateTimeFormat) {
                const originalResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
                Intl.DateTimeFormat.prototype.resolvedOptions = function() {
                    const options = originalResolvedOptions.call(this);
                    options.timeZone = 'Europe/Kiev';
                    return options;
                };
            }
        })();
        """
    
    @staticmethod
    def get_screen_fingerprint_script():
        """JavaScript для маскування параметрів екрану"""
        return """
        (function() {
            const screenWidth = 1920;
            const screenHeight = 1080;
            const availWidth = 1920;
            const availHeight = 1040;
            
            Object.defineProperty(screen, 'width', {
                get: function() { return screenWidth; }
            });
            
            Object.defineProperty(screen, 'height', {
                get: function() { return screenHeight; }
            });
            
            Object.defineProperty(screen, 'availWidth', {
                get: function() { return availWidth; }
            });
            
            Object.defineProperty(screen, 'availHeight', {
                get: function() { return availHeight; }
            });
            
            Object.defineProperty(screen, 'colorDepth', {
                get: function() { return 24; }
            });
            
            Object.defineProperty(screen, 'pixelDepth', {
                get: function() { return 24; }
            });
        })();
        """

    @staticmethod
    def get_webrtc_block_script():
        """JavaScript для блокування WebRTC"""
        return """
        (function() {
            // Блокуємо WebRTC
            const noop = function() {};
            
            window.RTCPeerConnection = noop;
            window.RTCSessionDescription = noop;
            window.RTCIceCandidate = noop;
            window.webkitRTCPeerConnection = noop;
            window.mozRTCPeerConnection = noop;
            
            navigator.getUserMedia = noop;
            navigator.webkitGetUserMedia = noop;
            navigator.mozGetUserMedia = noop;
            navigator.mediaDevices = {
                getUserMedia: noop,
                enumerateDevices: function() { 
                    return Promise.resolve([]); 
                }
            };
        })();
        """


class UrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """Перехоплювач запитів для блокування трекерів"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blocked_domains = set([
            'google-analytics.com',
            'googletagmanager.com',
            'facebook.com/tr',
            'doubleclick.net',
            'googlesyndication.com',
            'amazon-adsystem.com',
            'adsystem.amazon.com'
        ])
    
    def interceptRequest(self, info):
        """Перехоплення та блокування запитів"""
        url = info.requestUrl().toString()
        
        # Блокуємо трекери
        for domain in self.blocked_domains:
            if domain in url:
                info.block(True)
                return


class AnDetectWebPage(QWebEnginePage):
    """Кастомна веб-сторінка з маскуванням відбитків"""
    
    def __init__(self, profile_data, parent=None):
        # Створюємо кастомний профіль
        web_profile = QWebEngineProfile(profile_data.name if profile_data else "default", parent)
        
        super().__init__(web_profile, parent)
        
        self.profile_data = profile_data
        self.masker = FingerprintMasker()
        
        # Встановлюємо User-Agent
        if profile_data and hasattr(profile_data, 'user_agent') and profile_data.user_agent:
            user_agent = profile_data.user_agent
        else:
            user_agent = self.masker.get_random_user_agent()
            
        web_profile.setHttpUserAgent(user_agent)
        
        # Налаштовуємо перехоплювач запитів
        self.interceptor = UrlRequestInterceptor(self)
        web_profile.setUrlRequestInterceptor(self.interceptor)
        
        # Вимикаємо WebRTC в налаштуваннях
        web_profile.settings().setAttribute(
            web_profile.settings().WebRTCPublicInterfacesOnly, True
        )
        
        # Підключаємо сигнали
        self.loadFinished.connect(self.inject_fingerprint_scripts)
        
    def inject_fingerprint_scripts(self, success):
        """Вбудовування скриптів маскування після завантаження сторінки"""
        if success:
            # Вбудовуємо всі скрипти маскування
            scripts = [
                self.masker.get_canvas_fingerprint_script(),
                self.masker.get_webgl_fingerprint_script(),
                self.masker.get_timezone_script(),
                self.masker.get_screen_fingerprint_script(),
                self.masker.get_webrtc_block_script()
            ]
            
            for script in scripts:
                self.runJavaScript(script)
                
    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        """Перевірка навігаційних запитів"""
        # Можна додати додаткову логіку фільтрації
        return super().acceptNavigationRequest(url, navigation_type, is_main_frame)
        
    def javaScriptAlert(self, security_origin, message):
        """Обробка JavaScript alert"""
        # Можна додати кастомну обробку
        super().javaScriptAlert(security_origin, message)
        
    def javaScriptConfirm(self, security_origin, message):
        """Обробка JavaScript confirm"""
        # Можна додати кастомну обробку
        return super().javaScriptConfirm(security_origin, message)
>>>>>>> 5a38118ad408679126e5a17483fa7875264c621b
