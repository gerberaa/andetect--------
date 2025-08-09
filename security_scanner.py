#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль сканера безпеки для AnDetect Browser
Забезпечує захист від шкідливих веб-сайтів та загроз
"""

import os
import sys
import json
import hashlib
import requests
import socket
import ssl
import time
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Set, Optional, Tuple, Any
import threading
from enum import Enum

from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox


class ThreatLevel(Enum):
    """Рівні загроз"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Типи загроз"""
    MALWARE = "malware"
    PHISHING = "phishing"
    SPAM = "spam"
    SUSPICIOUS = "suspicious"
    TRACKING = "tracking"
    ADWARE = "adware"
    CRYPTOCURRENCY_MINING = "crypto_mining"
    FAKE_NEWS = "fake_news"


class URLAnalyzer:
    """Аналізатор URL на предмет загроз"""
    
    def __init__(self):
        self.suspicious_patterns = self.load_suspicious_patterns()
        self.malicious_domains = self.load_malicious_domains()
        self.phishing_keywords = self.load_phishing_keywords()
    
    def load_suspicious_patterns(self) -> List[str]:
        """Завантаження підозрілих патернів"""
        return [
            # URL shorteners
            r'bit\.ly', r'tinyurl\.com', r'goo\.gl', r't\.co',
            # Suspicious TLDs
            r'\.tk$', r'\.ml$', r'\.ga$', r'\.cf$',
            # Suspicious characters
            r'-[a-z]+-[a-z]+-', r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',
            # Homograph attacks
            r'[а-я]', r'[α-ω]', r'[а-я]',  # Cyrillic and Greek in Latin domains
            # Suspicious subdomains
            r'[a-z0-9]{20,}\.', r'www\d+\.', r'secure[0-9]*\.',
        ]
    
    def load_malicious_domains(self) -> Set[str]:
        """Завантаження списку шкідливих доменів"""
        # В реальному застосунку ці дані завантажуються з оновлюваних баз
        return {
            'malware-example.com',
            'phishing-site.net',
            'fake-bank.org',
            'crypto-stealer.info',
            # Додати більше доменів з реальних баз даних
        }
    
    def load_phishing_keywords(self) -> Set[str]:
        """Завантаження ключових слів фішингу"""
        return {
            'verify', 'account', 'suspended', 'urgent', 'immediate',
            'secure', 'update', 'confirm', 'login', 'password',
            'bank', 'paypal', 'amazon', 'microsoft', 'google',
            'winner', 'prize', 'lottery', 'congratulations',
            'click here', 'act now', 'limited time', 'expires today'
        }
    
    def analyze_url(self, url: str) -> Dict[str, Any]:
        """Аналіз URL на предмет загроз"""
        result = {
            'url': url,
            'threat_level': ThreatLevel.SAFE,
            'threat_types': [],
            'risk_score': 0,
            'warnings': [],
            'details': {}
        }
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            query = parsed.query.lower()
            
            # Перевірка домену
            domain_score = self.analyze_domain(domain, result)
            
            # Перевірка шляху та параметрів
            path_score = self.analyze_path_and_query(path, query, result)
            
            # Перевірка схеми
            scheme_score = self.analyze_scheme(parsed.scheme, result)
            
            # Розрахунок загального рівня ризику
            total_score = domain_score + path_score + scheme_score
            result['risk_score'] = min(total_score, 100)
            
            # Визначення рівня загрози
            if total_score >= 80:
                result['threat_level'] = ThreatLevel.CRITICAL
            elif total_score >= 60:
                result['threat_level'] = ThreatLevel.HIGH
            elif total_score >= 40:
                result['threat_level'] = ThreatLevel.MEDIUM
            elif total_score >= 20:
                result['threat_level'] = ThreatLevel.LOW
            
        except Exception as e:
            result['warnings'].append(f"Error analyzing URL: {str(e)}")
            result['threat_level'] = ThreatLevel.MEDIUM
            result['risk_score'] = 50
        
        return result
    
    def analyze_domain(self, domain: str, result: Dict[str, Any]) -> int:
        """Аналіз домену"""
        score = 0
        
        # Перевірка в чорному списку
        if domain in self.malicious_domains:
            score += 70
            result['threat_types'].append(ThreatType.MALWARE)
            result['warnings'].append("Domain found in malware blacklist")
        
        # Перевірка IP-адрес замість доменів
        if self.is_ip_address(domain):
            score += 30
            result['warnings'].append("Using IP address instead of domain name")
        
        # Перевірка підозрілих TLD
        if any(domain.endswith(tld) for tld in ['.tk', '.ml', '.ga', '.cf']):
            score += 20
            result['warnings'].append("Suspicious top-level domain")
        
        # Перевірка довжини домену
        if len(domain) > 50:
            score += 15
            result['warnings'].append("Unusually long domain name")
        
        # Перевірка кількості субдоменів
        subdomains = domain.split('.')
        if len(subdomains) > 4:
            score += 10
            result['warnings'].append("Multiple subdomains detected")
        
        # Перевірка на homograph attacks
        if self.contains_suspicious_characters(domain):
            score += 25
            result['threat_types'].append(ThreatType.PHISHING)
            result['warnings'].append("Domain contains suspicious characters")
        
        return score
    
    def analyze_path_and_query(self, path: str, query: str, result: Dict[str, Any]) -> int:
        """Аналіз шляху та параметрів запиту"""
        score = 0
        
        # Перевірка фішингових ключових слів
        text_to_check = (path + " " + query).lower()
        phishing_matches = [kw for kw in self.phishing_keywords if kw in text_to_check]
        
        if phishing_matches:
            score += len(phishing_matches) * 5
            result['threat_types'].append(ThreatType.PHISHING)
            result['warnings'].append(f"Phishing keywords detected: {', '.join(phishing_matches[:3])}")
        
        # Перевірка підозрілих параметрів
        suspicious_params = ['redirect', 'goto', 'url', 'link', 'ref']
        if any(param in query for param in suspicious_params):
            score += 15
            result['warnings'].append("Suspicious redirect parameters detected")
        
        # Перевірка дуже довгих URL
        if len(path + query) > 200:
            score += 10
            result['warnings'].append("Unusually long URL path")
        
        return score
    
    def analyze_scheme(self, scheme: str, result: Dict[str, Any]) -> int:
        """Аналіз схеми URL"""
        score = 0
        
        if scheme == 'http':
            score += 5
            result['warnings'].append("Unsecured HTTP connection")
        elif scheme not in ['http', 'https']:
            score += 15
            result['warnings'].append(f"Unusual URL scheme: {scheme}")
        
        return score
    
    def is_ip_address(self, domain: str) -> bool:
        """Перевірка чи є домен IP-адресою"""
        try:
            socket.inet_aton(domain)
            return True
        except socket.error:
            return False
    
    def contains_suspicious_characters(self, domain: str) -> bool:
        """Перевірка на підозрілі символи (homograph attacks)"""
        import re
        
        # Перевірка на кирилицю в латинських доменах
        cyrillic_pattern = r'[а-яё]'
        if re.search(cyrillic_pattern, domain, re.IGNORECASE):
            return True
        
        # Перевірка на грецькі символи
        greek_pattern = r'[α-ωΑ-Ω]'
        if re.search(greek_pattern, domain):
            return True
        
        # Перевірка на змішані алфавіти
        latin_count = len(re.findall(r'[a-zA-Z]', domain))
        non_latin_count = len(re.findall(r'[^\x00-\x7F]', domain))
        
        if latin_count > 0 and non_latin_count > 0:
            return True
        
        return False


class CertificateValidator:
    """Валідатор SSL сертифікатів"""
    
    def __init__(self):
        self.trusted_cas = self.load_trusted_cas()
    
    def load_trusted_cas(self) -> Set[str]:
        """Завантаження довірених центрів сертифікації"""
        # В реальному застосунку це список довірених CA
        return {
            'DigiCert', 'Symantec', 'GeoTrust', 'Thawte',
            'VeriSign', 'Comodo', 'GlobalSign', 'Entrust'
        }
    
    def validate_certificate(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """Валідація SSL сертифіката"""
        result = {
            'valid': False,
            'issues': [],
            'cert_info': {},
            'risk_score': 0
        }
        
        try:
            # Отримання сертифіката
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    if cert:
                        result['cert_info'] = cert
                        result['valid'] = True
                        
                        # Перевірка терміну дії
                        self.check_expiration(cert, result)
                        
                        # Перевірка видавця
                        self.check_issuer(cert, result)
                        
                        # Перевірка альтернативних імен
                        self.check_subject_alt_names(cert, hostname, result)
        
        except ssl.SSLError as e:
            result['issues'].append(f"SSL Error: {str(e)}")
            result['risk_score'] += 50
        except socket.timeout:
            result['issues'].append("Connection timeout")
            result['risk_score'] += 20
        except Exception as e:
            result['issues'].append(f"Certificate validation error: {str(e)}")
            result['risk_score'] += 30
        
        return result
    
    def check_expiration(self, cert: Dict[str, Any], result: Dict[str, Any]):
        """Перевірка терміну дії сертифіката"""
        try:
            not_after = cert.get('notAfter')
            if not_after:
                from datetime import datetime
                expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (expiry_date - datetime.now()).days
                
                if days_until_expiry < 0:
                    result['issues'].append("Certificate has expired")
                    result['risk_score'] += 70
                elif days_until_expiry < 30:
                    result['issues'].append(f"Certificate expires in {days_until_expiry} days")
                    result['risk_score'] += 20
        except Exception:
            result['issues'].append("Could not verify certificate expiration")
            result['risk_score'] += 10
    
    def check_issuer(self, cert: Dict[str, Any], result: Dict[str, Any]):
        """Перевірка видавця сертифіката"""
        try:
            issuer = dict(x[0] for x in cert.get('issuer', []))
            org_name = issuer.get('organizationName', '')
            
            if not any(ca in org_name for ca in self.trusted_cas):
                result['issues'].append(f"Unknown certificate authority: {org_name}")
                result['risk_score'] += 30
        except Exception:
            result['issues'].append("Could not verify certificate issuer")
            result['risk_score'] += 15
    
    def check_subject_alt_names(self, cert: Dict[str, Any], hostname: str, result: Dict[str, Any]):
        """Перевірка альтернативних імен сертифіката"""
        try:
            san_list = cert.get('subjectAltName', [])
            san_domains = [name[1] for name in san_list if name[0] == 'DNS']
            
            if hostname not in san_domains:
                subject = dict(x[0] for x in cert.get('subject', []))
                common_name = subject.get('commonName', '')
                
                if hostname != common_name:
                    result['issues'].append("Hostname doesn't match certificate")
                    result['risk_score'] += 40
        except Exception:
            result['issues'].append("Could not verify certificate subject")
            result['risk_score'] += 10


class MalwareScanner:
    """Сканер шкідливого ПЗ"""
    
    def __init__(self):
        self.malware_signatures = self.load_malware_signatures()
        self.suspicious_scripts = self.load_suspicious_scripts()
    
    def load_malware_signatures(self) -> List[str]:
        """Завантаження сигнатур шкідливого ПЗ"""
        return [
            # JavaScript malware patterns
            'eval(atob(',
            'document.write(unescape(',
            'String.fromCharCode(',
            'setTimeout("eval(',
            'location.href="data:text/html,',
            
            # Cryptocurrency mining
            'coinhive',
            'cryptoloot',
            'jsecoin',
            'mineralt',
            
            # Suspicious redirects
            'window.location.replace(',
            'top.location.href',
            'parent.location',
        ]
    
    def load_suspicious_scripts(self) -> List[str]:
        """Завантаження підозрілих скриптів"""
        return [
            'keylogger',
            'screenshot',
            'clipboard',
            'microphone',
            'camera',
            'geolocation',
            'download_file',
            'upload_file',
        ]
    
    def scan_content(self, content: str, url: str) -> Dict[str, Any]:
        """Сканування контенту на шкідливе ПЗ"""
        result = {
            'threats_found': [],
            'risk_score': 0,
            'recommendations': []
        }
        
        content_lower = content.lower()
        
        # Пошук сигнатур шкідливого ПЗ
        for signature in self.malware_signatures:
            if signature.lower() in content_lower:
                result['threats_found'].append({
                    'type': 'malware_signature',
                    'signature': signature,
                    'description': f'Malware signature detected: {signature}'
                })
                result['risk_score'] += 25
        
        # Пошук підозрілих скриптів
        for script_pattern in self.suspicious_scripts:
            if script_pattern in content_lower:
                result['threats_found'].append({
                    'type': 'suspicious_script',
                    'pattern': script_pattern,
                    'description': f'Suspicious script detected: {script_pattern}'
                })
                result['risk_score'] += 15
        
        # Перевірка на криптовалютний майнінг
        mining_indicators = ['worker', 'hash', 'difficulty', 'mining', 'pool']
        mining_count = sum(1 for indicator in mining_indicators if indicator in content_lower)
        
        if mining_count >= 3:
            result['threats_found'].append({
                'type': 'cryptocurrency_mining',
                'description': 'Possible cryptocurrency mining detected'
            })
            result['risk_score'] += 40
        
        # Генерація рекомендацій
        if result['risk_score'] > 50:
            result['recommendations'].append('Block this page immediately')
        elif result['risk_score'] > 25:
            result['recommendations'].append('Proceed with caution')
        
        return result


class SecurityScanner(QObject):
    """Головний клас сканера безпеки"""
    
    scan_completed = pyqtSignal(dict)
    threat_detected = pyqtSignal(str, dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.url_analyzer = URLAnalyzer()
        self.cert_validator = CertificateValidator()
        self.malware_scanner = MalwareScanner()
        
        self.scan_cache = {}
        self.cache_timeout = 3600  # 1 година
    
    def scan_url(self, url: str, content: str = "") -> Dict[str, Any]:
        """Комплексне сканування URL"""
        # Перевірка кешу
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in self.scan_cache:
            cached_result = self.scan_cache[cache_key]
            if time.time() - cached_result['timestamp'] < self.cache_timeout:
                return cached_result['result']
        
        result = {
            'url': url,
            'timestamp': time.time(),
            'url_analysis': {},
            'certificate_analysis': {},
            'malware_analysis': {},
            'overall_threat_level': ThreatLevel.SAFE,
            'overall_risk_score': 0,
            'recommendations': []
        }
        
        try:
            # Аналіз URL
            result['url_analysis'] = self.url_analyzer.analyze_url(url)
            
            # Аналіз сертифіката (тільки для HTTPS)
            parsed_url = urlparse(url)
            if parsed_url.scheme == 'https':
                result['certificate_analysis'] = self.cert_validator.validate_certificate(
                    parsed_url.netloc.split(':')[0]
                )
            
            # Сканування контенту (якщо надано)
            if content:
                result['malware_analysis'] = self.malware_scanner.scan_content(content, url)
            
            # Розрахунок загального рівня ризику
            url_score = result['url_analysis'].get('risk_score', 0)
            cert_score = result['certificate_analysis'].get('risk_score', 0)
            malware_score = result['malware_analysis'].get('risk_score', 0)
            
            result['overall_risk_score'] = min((url_score + cert_score + malware_score) / 3, 100)
            
            # Визначення загального рівня загрози
            if result['overall_risk_score'] >= 80:
                result['overall_threat_level'] = ThreatLevel.CRITICAL
            elif result['overall_risk_score'] >= 60:
                result['overall_threat_level'] = ThreatLevel.HIGH
            elif result['overall_risk_score'] >= 40:
                result['overall_threat_level'] = ThreatLevel.MEDIUM
            elif result['overall_risk_score'] >= 20:
                result['overall_threat_level'] = ThreatLevel.LOW
            
            # Генерація рекомендацій
            self.generate_recommendations(result)
            
            # Збереження в кеш
            self.scan_cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }
            
            # Емісія сигналу про завершення сканування
            self.scan_completed.emit(result)
            
            # Емісія сигналу про загрозу (якщо знайдено)
            if result['overall_threat_level'] in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                self.threat_detected.emit(url, result)
        
        except Exception as e:
            result['error'] = str(e)
            result['overall_threat_level'] = ThreatLevel.MEDIUM
            result['overall_risk_score'] = 50
        
        return result
    
    def generate_recommendations(self, result: Dict[str, Any]):
        """Генерація рекомендацій на основі результатів сканування"""
        recommendations = []
        
        threat_level = result['overall_threat_level']
        
        if threat_level == ThreatLevel.CRITICAL:
            recommendations.extend([
                'BLOCK ACCESS TO THIS SITE IMMEDIATELY',
                'Clear all browser data',
                'Run full system antivirus scan'
            ])
        elif threat_level == ThreatLevel.HIGH:
            recommendations.extend([
                'Do not enter personal information',
                'Do not download any files',
                'Close this page'
            ])
        elif threat_level == ThreatLevel.MEDIUM:
            recommendations.extend([
                'Proceed with caution',
                'Verify site authenticity',
                'Avoid entering sensitive information'
            ])
        elif threat_level == ThreatLevel.LOW:
            recommendations.append('Site appears safe, but stay vigilant')
        
        # Додаткові рекомендації на основі специфічних загроз
        url_analysis = result.get('url_analysis', {})
        cert_analysis = result.get('certificate_analysis', {})
        
        if ThreatType.PHISHING in url_analysis.get('threat_types', []):
            recommendations.append('Possible phishing attempt - verify URL carefully')
        
        if not cert_analysis.get('valid', True):
            recommendations.append('SSL certificate issues detected')
        
        result['recommendations'] = recommendations
    
    def clear_cache(self):
        """Очищення кешу сканування"""
        self.scan_cache.clear()
    
    def update_threat_databases(self):
        """Оновлення баз даних загроз"""
        # В реальному застосунку тут відбувається завантаження оновлень
        # з онлайн джерел безпеки
        try:
            # Приклад оновлення (заглушка)
            self.url_analyzer.malicious_domains.update([
                'new-malware-site.com',
                'another-threat.net'
            ])
            
            return True
        except Exception as e:
            print(f"Error updating threat databases: {e}")
            return False
