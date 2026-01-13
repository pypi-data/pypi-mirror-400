import time, random, os, json, asyncio
from datetime import datetime
from curl_cffi import requests as crequests
from curl_cffi.requests import AsyncSession
from urllib.parse import urlparse, quote_plus

# --- PROTECTION LAYERS ---
LOWER_LAYER = ['identity', 'jitter']
MEDIUM_LAYER = ['identity', 'ghost', 'jitter', 'header_order']
MAX_LAYER = ['identity', 'ghost', 'jitter', 'header_order', 'canvas', 'cookie_warmup', 'search_click']
NUCLEAR_LAYER = MAX_LAYER + ['nuclear']

# --- NOISE & REFERRER POOLS ---
NOISE_URLS = [
    "https://www.wikipedia.org", "https://www.reddit.com", "https://stackoverflow.com",
    "https://www.bbc.com", "https://www.cnn.com", "https://github.com"
]

REFERRERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://www.facebook.com/",
    "https://t.co/",
    "https://www.reddit.com/"
]


class Bequests:
    def __init__(self, proxies=None, use_tor=False, logged=True, auto_load=True, hooks=None, response_hooks=None, timeout=30):
        # Network Config
        self.proxies_list = proxies if proxies else []
        self.current_proxy_idx = 0
        self.use_tor = use_tor
        self.tor_proxy = "socks5h://127.0.0.1:9050"
        self.timeout = timeout
        
        # Behavior Control
        self.logged = logged
        self.auto_rotate = True
        self.recon_waf_active = True
        self.detect_captcha_active = True
        self.save_on_success = True
        self.vault_file = "bequests_vault.json"
        
        # Hooks System
        self.hooks = hooks if hooks else []
        self.response_hooks = response_hooks if response_hooks else []
        
        # Bot State
        self.active_layers = MEDIUM_LAYER
        self.imitation_mode = False
        self.engine = random.choice(["chrome120", "safari15_5"])
        self.jitter_range = (1.0, 3.0)
        
        # Statistics & Monitoring
        self.stats = {
            "requests": 0,
            "success": 0,
            "failed": 0,
            "blocked": 0,
            "captcha": 0,
            "start_time": time.time()
        }
        self.request_history = []
        self.max_history = 100
        
        # Rate Limiting
        self.rate_limit = None  # Format: (requests, per_seconds)
        self.rate_timestamps = []
        
        # Domain Management
        self.domain_whitelist = []
        self.domain_blacklist = []
        
        # Advanced Features
        self.retry_config = {
            "max_retries": 3,
            "backoff_factor": 2,
            "backoff_max": 60
        }
        self.response_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Session Init
        self.session = crequests.Session()
        
        if auto_load:
            self.load_cookies()

        if not os.path.exists("downloads"):
            os.makedirs("downloads")

    def _log(self, status, msg):
        if self.logged:
            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] [Bequests:{status}] {msg}")
            
            # Log to file if debug mode
            if hasattr(self, 'debug_log_file'):
                with open(self.debug_log_file, 'a') as f:
                    f.write(f"[{timestamp}] [{status}] {msg}\n")

    # --- CONFIGURATION (CHAINABLE) ---
    def add_hook(self, func):
        """Adds a function to execute BEFORE the request."""
        self.hooks.append(func)
        return self

    def add_response_hook(self, func):
        """Adds a function to execute AFTER the request (receives the response object)."""
        self.response_hooks.append(func)
        return self

    def layers(self, layers_list):
        self.active_layers = layers_list
        return self

    def imit_nav(self, status: bool):
        self.imitation_mode = status
        return self

    def set_speed(self, min_d, max_d):
        self.jitter_range = (min_d, max_d)
        return self

    def set_engine(self, engine_name):
        """Manually select the TLS fingerprint (e.g., chrome120, safari15_5)."""
        self.engine = engine_name
        return self

    def toggle_tor(self, status: bool):
        self.use_tor = status
        return self

    def toggle_auto_rotate(self, status: bool):
        self.auto_rotate = status
        return self

    def set_rate_limit(self, requests, per_seconds):
        """Set rate limiting: e.g. (10, 60) = 10 requests per 60 seconds"""
        self.rate_limit = (requests, per_seconds)
        self._log("CONFIG", f"Rate limit set to {requests} req/{per_seconds}s")
        return self

    def set_retry_config(self, max_retries=3, backoff_factor=2, backoff_max=60):
        """Configure exponential backoff retry strategy"""
        self.retry_config = {
            "max_retries": max_retries,
            "backoff_factor": backoff_factor,
            "backoff_max": backoff_max
        }
        return self

    def whitelist_domains(self, domains):
        """Only allow requests to these domains"""
        self.domain_whitelist = domains if isinstance(domains, list) else [domains]
        self._log("FILTER", f"Whitelisted {len(self.domain_whitelist)} domains")
        return self

    def blacklist_domains(self, domains):
        """Block requests to these domains"""
        self.domain_blacklist = domains if isinstance(domains, list) else [domains]
        self._log("FILTER", f"Blacklisted {len(self.domain_blacklist)} domains")
        return self

    def enable_cache(self, ttl=300):
        """Enable response caching with TTL in seconds"""
        self.cache_ttl = ttl
        self._log("CACHE", f"Response cache enabled (TTL: {ttl}s)")
        return self

    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        self._log("CACHE", "Cache cleared")
        return self

    def enable_debug_log(self, filepath="bequests_debug.log"):
        """Enable detailed logging to file"""
        self.debug_log_file = filepath
        self._log("DEBUG", f"Debug logging enabled: {filepath}")
        return self

    # --- STORAGE & NOISE ---
    def generate_noise(self, count=3):
        """Visits random neutral websites to build a realistic cookie history."""
        self._log("NOISE", f"Generating traffic on {count} neutral sites...")
        targets = random.sample(NOISE_URLS, k=min(count, len(NOISE_URLS)))
        
        prev_log = self.logged
        self.logged = False
        
        for url in targets:
            try:
                self.session.get(url, impersonate=self.engine, timeout=10)
                time.sleep(random.uniform(1, 3))
            except: 
                pass
            
        self.logged = prev_log
        self._log("NOISE", "History warmup complete.")
        self.save_cookies()
        return self

    def load_cookies(self, path=None):
        target = path if path else self.vault_file
        if os.path.exists(target):
            try:
                with open(target, 'r') as f:
                    self.session.cookies.update(json.load(f))
                self._log("STORAGE", f"Cookies loaded from {target}")
            except Exception as e:
                self._log("ERROR", f"Failed to load cookies: {e}")
        return self

    def save_cookies(self, path=None):
        target = path if path else self.vault_file
        with open(target, 'w') as f:
            json.dump(self.session.cookies.get_dict(), f)
        self._log("STORAGE", f"Cookies saved in {target}")
        return self

    def set_cookies(self, cookie_dict):
        self.session.cookies.update(cookie_dict)
        return self

    def get_cookies(self):
        return self.session.cookies.get_dict()

    def clear_vault(self):
        """Clears cookies from memory and disk."""
        self.session.cookies.clear()
        if os.path.exists(self.vault_file):
            os.remove(self.vault_file)
        self._log("CLEANER", "Vault and session reset.")
        return self

    def reset_session(self):
        """Re-creates a fresh TLS session (New JA3 fingerprint)."""
        self.session = crequests.Session()
        self._log("ENGINE", "TLS session completely reset.")
        return self

    # --- INTELLIGENCE & STEALTH ---
    def check_stealth(self):
        """Checks if the bot is detected by an external probe."""
        self._log("CHECK", "Checking TLS/UA fingerprint...")
        try:
            resp = self.get("https://httpbin.org/get", timeout=10)
            if resp and resp.status_code == 200:
                self._log("HEALTH", f"Stealth Validated ({self.engine})")
                return True
        except: 
            pass
        self._log("HEALTH", "Warning: Suspicious fingerprint or blocked network.")
        return False

    def _recon_waf(self, resp):
        """[WAF-RECON] Identifies the firewall protection."""
        if not self.recon_waf_active: 
            return "DISABLED"
        h = resp.headers
        server = h.get("Server", "").lower()
        
        if "cloudflare" in server or "cf-ray" in h: 
            return "CLOUDFLARE"
        if "akamai" in server or "x-akamai-edge" in h: 
            return "AKAMAI"
        if "incapsula" in h or "visid_incap" in h: 
            return "IMPERVA/INCAPSULA"
        if "awselb" in h or "aws" in server: 
            return "AWS WAF"
        if resp.status_code == 403 and "perimetre" in resp.text.lower(): 
            return "DATADOME"
        
        return "UNKNOWN WAF"

    def _simulate_dom_loading(self, url):
        """[DOM-SIMULATOR] Fetches secondary assets."""
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        assets = ["/favicon.ico", "/robots.txt", "/sitemap.xml"]
        for asset in random.sample(assets, k=random.randint(1, 2)):
            try:
                self.session.get(f"{base}{asset}", impersonate=self.engine, timeout=2)
                self._log("DOM-SIM", f"Loading asset: {asset}")
            except: 
                pass

    def _cookie_warmup_routine(self, url):
        """[COOKIE_WARMUP] Pre-visits assets to establish TCP/TLS connection."""
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        try:
            self.session.get(f"{base}/favicon.ico", impersonate=self.engine, timeout=2)
            self._log("WARMUP", "TCP/TLS Handshake warmed up.")
        except: 
            pass

    def _detect_captcha(self, html):
        """[CAPTCHA-GHOST] Silent challenge detection."""
        if not self.detect_captcha_active: 
            return False
        indicators = ["g-recaptcha", "hcaptcha", "turnstile", "cf-challenge", "captcha-delivery"]
        for ind in indicators:
            if ind in html.lower():
                self._log("GHOST", f"Challenge '{ind}' detected in the page!")
                self.stats["captcha"] += 1
                return True
        return False

    def _build_headers(self, layers, persona):
        """Constructs headers based on layers and engine consistency."""
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "Referer": persona["ref"]
        }

        if 'identity' in layers:
            headers["User-Agent"] = persona["ua"]

        if 'header_order' in layers and "chrome" in self.engine:
            headers["Sec-CH-UA"] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
            headers["Sec-CH-UA-Mobile"] = "?0"
            headers["Sec-CH-UA-Platform"] = '"Windows"' if "Windows" in persona["ua"] else '"macOS"'
            headers["Sec-Fetch-Dest"] = "document"
            headers["Sec-Fetch-Mode"] = "navigate"
            headers["Sec-Fetch-Site"] = "cross-site"
            headers["Sec-Fetch-User"] = "?1"

        if 'canvas' in layers:
            headers["Viewport-Width"] = str(random.choice([1920, 1366, 1440]))
            headers["Device-Memory"] = str(random.choice([8, 16, 32]))
            headers["DPR"] = str(random.choice([1, 1.5, 2]))

        return headers

    def _check_rate_limit(self):
        """Check if rate limit is exceeded"""
        if not self.rate_limit:
            return True
            
        max_requests, time_window = self.rate_limit
        current_time = time.time()
        
        # Clean old timestamps
        self.rate_timestamps = [t for t in self.rate_timestamps if current_time - t < time_window]
        
        if len(self.rate_timestamps) >= max_requests:
            wait_time = time_window - (current_time - self.rate_timestamps[0])
            self._log("RATE-LIMIT", f"Rate limit reached. Waiting {wait_time:.2f}s...")
            time.sleep(wait_time)
            self.rate_timestamps = []
        
        self.rate_timestamps.append(current_time)
        return True

    def _check_domain_filters(self, url):
        """Check if domain is allowed"""
        domain = urlparse(url).netloc
        
        if self.domain_blacklist and domain in self.domain_blacklist:
            self._log("FILTER", f"Domain {domain} is blacklisted. Request blocked.")
            return False
            
        if self.domain_whitelist and domain not in self.domain_whitelist:
            self._log("FILTER", f"Domain {domain} not in whitelist. Request blocked.")
            return False
            
        return True

    def _get_cache_key(self, method, url, **kwargs):
        """Generate cache key for request"""
        key_parts = [method, url]
        if 'params' in kwargs:
            key_parts.append(json.dumps(kwargs['params'], sort_keys=True))
        return "|".join(key_parts)

    def _get_from_cache(self, cache_key):
        """Retrieve response from cache if valid"""
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            if time.time() - cached['timestamp'] < self.cache_ttl:
                self._log("CACHE", "Cache HIT")
                return cached['response']
            else:
                del self.response_cache[cache_key]
        return None

    def _save_to_cache(self, cache_key, response):
        """Save response to cache"""
        self.response_cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }

    def _update_stats(self, success=True, blocked=False):
        """Update request statistics"""
        self.stats["requests"] += 1
        if success:
            self.stats["success"] += 1
        else:
            self.stats["failed"] += 1
        if blocked:
            self.stats["blocked"] += 1

    def _record_request(self, method, url, status_code, duration):
        """Record request in history"""
        if len(self.request_history) >= self.max_history:
            self.request_history.pop(0)
        
        self.request_history.append({
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "url": url,
            "status_code": status_code,
            "duration": duration
        })

    def get_stats(self):
        """Get current session statistics"""
        uptime = time.time() - self.stats["start_time"]
        return {
            **self.stats,
            "uptime": uptime,
            "success_rate": (self.stats["success"] / max(self.stats["requests"], 1)) * 100
        }

    def export_stats(self, filepath="bequests_stats.json"):
        """Export statistics to JSON file"""
        stats = self.get_stats()
        stats["history"] = self.request_history
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)
        self._log("EXPORT", f"Stats exported to {filepath}")
        return self

    # --- NETWORK ---
    def _get_active_proxies(self):
        if self.use_tor:
            return {"http": self.tor_proxy, "https": self.tor_proxy}
        if self.proxies_list:
            p = self.proxies_list[self.current_proxy_idx]
            return {"http": p, "https": p}
        return None

    def rotate_proxy(self):
        if self.proxies_list:
            self.current_proxy_idx = (self.current_proxy_idx + 1) % len(self.proxies_list)
            self._log("PROXY", f"Rotation to IP index {self.current_proxy_idx}")
        return self

    # --- CORE ENGINE ---
    def request(self, method, url, retry_count=0, **kwargs):
        # Domain filtering
        if not self._check_domain_filters(url):
            return None
        
        # Rate limiting
        self._check_rate_limit()
        
        # Cache check
        if method.upper() == "GET" and self.cache_ttl > 0:
            cache_key = self._get_cache_key(method, url, **kwargs)
            cached_resp = self._get_from_cache(cache_key)
            if cached_resp:
                return cached_resp
        
        start_time = time.time()
        
        # Persona Generation
        ua_map = {
            "chrome120": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "safari15_5": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15"
        }
        ref = random.choice(REFERRERS)
        
        # Search Click Layer
        target_url = url
        if 'search_click' in self.active_layers and 'nuclear' not in self.active_layers:
            domain = urlparse(url).netloc
            ref = f"https://www.google.com/search?q={quote_plus(domain)}"
            target_url += ("&" if "?" in target_url else "?") + f"ved=0ahUKEwi{random.randint(1000,9999)}"

        # Nuclear Layer
        if 'nuclear' in self.active_layers:
            self._log("NUCLEAR", "Routing via Google Cache...")
            target_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"

        persona = {"id": self.engine, "ua": ua_map.get(self.engine, self.engine), "ref": ref}

        # Build Headers
        gen_headers = self._build_headers(self.active_layers, persona)
        
        # Merge User Data
        user_headers = kwargs.pop('headers', {})
        if 'json' in kwargs: 
            gen_headers["Content-Type"] = "application/json"
        elif 'data' in kwargs: 
            gen_headers["Content-Type"] = "application/x-www-form-urlencoded"
        gen_headers.update(user_headers)

        # Pre-Request Hooks
        for process in self.hooks:
            try:
                result = process(target_url, gen_headers, kwargs)
                if result is not None and isinstance(result, tuple) and len(result) == 3:
                    target_url, gen_headers, kwargs = result
                else:
                    self._log("HOOK-WARN", f"Hook '{process.__name__}' ignored (Did not return url, headers, kwargs).")
            except Exception as e:
                self._log("HOOK-ERROR", str(e))

        # Behavioral Simulation
        if (self.imitation_mode or 'cookie_warmup' in self.active_layers) and retry_count == 0:
            self._cookie_warmup_routine(url)
            if self.imitation_mode:
                self._simulate_dom_loading(url)

        # Jitter
        if 'jitter' in self.active_layers:
            time.sleep(random.uniform(*self.jitter_range))

        proxies = kwargs.pop('proxies', self._get_active_proxies())
        timeout = kwargs.pop('timeout', self.timeout)

        try:
            self._log("DEPLOY", f"[{method.upper()}] {urlparse(target_url).netloc}")
            resp = self.session.request(
                method=method.upper(), 
                url=target_url, 
                headers=gen_headers,
                impersonate=self.engine, 
                proxies=proxies,
                http_version=2,
                timeout=timeout,
                **kwargs
            )

            duration = time.time() - start_time
            self._record_request(method, url, resp.status_code, duration)

            # Post-Request Hooks
            for hook in self.response_hooks:
                try: 
                    hook(resp)
                except Exception as e: 
                    self._log("RESP-HOOK-ERROR", str(e))

            # Failure Logic with Exponential Backoff
            if resp.status_code in [403, 429] and retry_count < self.retry_config["max_retries"] and 'nuclear' not in self.active_layers:
                waf = self._recon_waf(resp)
                self._log("BLOCKED", f"Wall {waf} detected. Attempting to pivot...")
                self._update_stats(success=False, blocked=True)
                
                # Exponential backoff
                backoff_time = min(
                    self.retry_config["backoff_factor"] ** retry_count,
                    self.retry_config["backoff_max"]
                )
                self._log("RETRY", f"Waiting {backoff_time}s before retry...")
                time.sleep(backoff_time)
                
                if self.auto_rotate: 
                    self.rotate_proxy()
                
                self.engine = "safari15_5" if self.engine == "chrome120" else "chrome120"
                self.layers(NUCLEAR_LAYER)
                return self.request(method, url, retry_count=retry_count+1, **kwargs)

            # Success Logic
            if resp.status_code == 200:
                self._detect_captcha(resp.text)
                if self.save_on_success: 
                    self.save_cookies()
                self._update_stats(success=True)
                
                # Cache successful GET requests
                if method.upper() == "GET" and self.cache_ttl > 0:
                    cache_key = self._get_cache_key(method, url, **kwargs)
                    self._save_to_cache(cache_key, resp)
            else:
                self._update_stats(success=False)
                
            return resp

        except Exception as e:
            self._log("CRASH", f"Critical Error: {e}")
            self._update_stats(success=False)
            
            if retry_count < self.retry_config["max_retries"] and self.proxies_list:
                backoff_time = min(
                    self.retry_config["backoff_factor"] ** retry_count,
                    self.retry_config["backoff_max"]
                )
                time.sleep(backoff_time)
                self.rotate_proxy()
                return self.request(method, url, retry_count=retry_count+1, **kwargs)
            return None

    # HTTP Method Shortcuts
    def get(self, url, **kwargs): 
        return self.request("GET", url, **kwargs)
    
    def post(self, url, **kwargs): 
        return self.request("POST", url, **kwargs)
    
    def put(self, url, **kwargs): 
        return self.request("PUT", url, **kwargs)
    
    def delete(self, url, **kwargs): 
        return self.request("DELETE", url, **kwargs)
    
    def head(self, url, **kwargs): 
        return self.request("HEAD", url, **kwargs)
    
    def options(self, url, **kwargs): 
        return self.request("OPTIONS", url, **kwargs)
    
    def patch(self, url, **kwargs): 
        return self.request("PATCH", url, **kwargs)
    
    def trace(self, url, **kwargs): 
        return self.request("TRACE", url, **kwargs)
    
    def connect(self, url, **kwargs): 
        return self.request("CONNECT", url, **kwargs)
    
    def smart_json(self, url, **kwargs):
        """Fetch JSON with proper error handling."""
        r = self.get(url, **kwargs)
        try: 
            return r.json() if r else None
        except:
            self._log("ERROR", "The response is not valid JSON.")
            return None

    # Advanced Download Feature
    def download(self, url, filename=None, show_progress=True, **kwargs):
        """Download file with optional progress indicator"""
        if not filename:
            filename = os.path.join("downloads", url.split("/")[-1])
        
        self._log("DOWNLOAD", f"Starting download: {url}")
        
        try:
            resp = self.get(url, stream=True, **kwargs)
            if not resp or resp.status_code != 200:
                self._log("ERROR", f"Download failed: HTTP {resp.status_code if resp else 'None'}")
                return False
            
            total_size = int(resp.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filename, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if show_progress and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rProgress: {progress:.1f}%", end='', flush=True)
            
            if show_progress:
                print()  # New line after progress
            
            self._log("DOWNLOAD", f"Complete: {filename}")
            return True
            
        except Exception as e:
            self._log("ERROR", f"Download error: {e}")
            return False


class AsyncBequests:
    def __init__(self, proxies=None, use_tor=False, logged=True, auto_load=True, hooks=None, response_hooks=None, timeout=30):
        self.proxies_list = proxies if proxies else []
        self.current_proxy_idx = 0
        self.use_tor = use_tor
        self.tor_proxy = "socks5h://127.0.0.1:9050"
        self.timeout = timeout
        
        self.logged = logged
        self.auto_rotate = True
        self.recon_waf_active = True
        self.detect_captcha_active = True
        self.save_on_success = True
        self.vault_file = "bequests_vault.json"
        
        self.hooks = hooks if hooks else []
        self.response_hooks = response_hooks if response_hooks else []
        
        self.active_layers = MEDIUM_LAYER
        self.imitation_mode = False
        self.engine = random.choice(["chrome120", "safari15_5"])
        self.jitter_range = (0.5, 1.5)
        
        # Statistics
        self.stats = {
            "requests": 0,
            "success": 0,
            "failed": 0,
            "blocked": 0,
            "captcha": 0,
            "start_time": time.time()
        }
        
        # Advanced Features
        self.retry_config = {
            "max_retries": 3,
            "backoff_factor": 2,
            "backoff_max": 60
        }
        
        self.session = AsyncSession()
        
        if auto_load:
            self._load_cookies_sync()

        if not os.path.exists("downloads"):
            os.makedirs("downloads")

    def _log(self, status, msg):
        if self.logged:
            print(f"[{time.strftime('%H:%M:%S')}] [AsyncBequests:{status}] {msg}")

    # Config Methods
    def add_hook(self, func): 
        self.hooks.append(func)
        return self
    
    def add_response_hook(self, func): 
        self.response_hooks.append(func)
        return self
    
    def layers(self, layers_list): 
        self.active_layers = layers_list
        return self
    
    def imit_nav(self, status: bool): 
        self.imitation_mode = status
        return self
    
    def set_speed(self, min_d, max_d): 
        self.jitter_range = (min_d, max_d)
        return self
    
    def set_engine(self, engine_name): 
        self.engine = engine_name
        return self
    
    def toggle_tor(self, status: bool): 
        self.use_tor = status
        return self

    def toggle_auto_rotate(self, status: bool):
        self.auto_rotate = status
        return self

    def set_retry_config(self, max_retries=3, backoff_factor=2, backoff_max=60):
        self.retry_config = {
            "max_retries": max_retries,
            "backoff_factor": backoff_factor,
            "backoff_max": backoff_max
        }
        return self

    # Storage
    def _load_cookies_sync(self):
        if os.path.exists(self.vault_file):
            try:
                with open(self.vault_file, 'r') as f:
                    self.session.cookies.update(json.load(f))
            except: 
                pass

    def save_cookies(self):
        with open(self.vault_file, 'w') as f:
            json.dump(self.session.cookies.get_dict(), f)
        return self

    def set_cookies(self, cookie_dict):
        self.session.cookies.update(cookie_dict)
        return self

    def get_cookies(self):
        return self.session.cookies.get_dict()

    def clear_vault(self):
        self.session.cookies.clear()
        if os.path.exists(self.vault_file):
            os.remove(self.vault_file)
        self._log("CLEANER", "Vault reset.")
        return self

    def get_stats(self):
        uptime = time.time() - self.stats["start_time"]
        return {
            **self.stats,
            "uptime": uptime,
            "success_rate": (self.stats["success"] / max(self.stats["requests"], 1)) * 100
        }
    
    # Noise & Stealth
    async def generate_noise(self, count=3):
        self._log("NOISE", f"Generating traffic on {count} sites...")
        targets = random.sample(NOISE_URLS, k=min(count, len(NOISE_URLS)))
        prev_log = self.logged
        self.logged = False
        
        for url in targets:
            try:
                await self.session.get(url, impersonate=self.engine, timeout=10)
                await asyncio.sleep(random.uniform(0.5, 2))
            except: 
                pass
            
        self.logged = prev_log
        self._log("NOISE", "History warmup complete.")
        return self

    async def check_stealth(self):
        self._log("CHECK", "TLS Async Verification...")
        try:
            resp = await self.get("https://httpbin.org/get", timeout=10)
            return resp.status_code == 200 if resp else False
        except: 
            return False

    def _recon_waf(self, resp):
        h = resp.headers
        server = h.get("Server", "").lower()
        if "cloudflare" in server or "cf-ray" in h: 
            return "CLOUDFLARE"
        if "akamai" in server or "x-akamai-edge" in h: 
            return "AKAMAI"
        if "incapsula" in h or "visid_incap" in h: 
            return "IMPERVA/INCAPSULA"
        if "awselb" in h or "aws" in server: 
            return "AWS WAF"
        if resp.status_code == 403 and "perimetre" in resp.text.lower(): 
            return "DATADOME"
        return "UNKNOWN WAF"

    async def _simulate_dom_loading(self, url):
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        assets = ["/favicon.ico", "/robots.txt", "/sitemap.xml"]
        for asset in random.sample(assets, k=random.randint(1, 2)):
            try:
                await self.session.get(f"{base}{asset}", impersonate=self.engine, timeout=2)
            except: 
                pass

    async def _cookie_warmup_routine(self, url):
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        try:
            await self.session.get(f"{base}/favicon.ico", impersonate=self.engine, timeout=2)
            self._log("WARMUP", "Async TCP/TLS Handshake.")
        except: 
            pass

    def _build_headers(self, layers, persona):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "Referer": persona["ref"]
        }
        
        if 'identity' in layers: 
            headers["User-Agent"] = persona["ua"]
        
        if 'header_order' in layers and "chrome" in self.engine:
            headers["Sec-CH-UA"] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
            headers["Sec-CH-UA-Mobile"] = "?0"
            headers["Sec-CH-UA-Platform"] = '"Windows"' if "Windows" in persona["ua"] else '"macOS"'
            headers["Sec-Fetch-Dest"] = "document"
            headers["Sec-Fetch-Mode"] = "navigate"
            headers["Sec-Fetch-Site"] = "cross-site"
            headers["Sec-Fetch-User"] = "?1"

        if 'canvas' in layers:
            headers["Viewport-Width"] = str(random.choice([1920, 1366, 1440]))
            headers["Device-Memory"] = str(random.choice([8, 16, 32]))
            headers["DPR"] = str(random.choice([1, 1.5, 2]))
            
        return headers

    def rotate_proxy(self):
        if self.proxies_list:
            self.current_proxy_idx = (self.current_proxy_idx + 1) % len(self.proxies_list)
            self._log("PROXY", f"Async rotation to IP {self.current_proxy_idx}")
        return self

    def _update_stats(self, success=True, blocked=False):
        self.stats["requests"] += 1
        if success:
            self.stats["success"] += 1
        else:
            self.stats["failed"] += 1
        if blocked:
            self.stats["blocked"] += 1

    # Core Request
    async def request(self, method, url, retry_count=0, **kwargs):
        ua_map = {
            "chrome120": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "safari15_5": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15"
        }
        ref = random.choice(REFERRERS)
        target_url = url
        
        if 'search_click' in self.active_layers and 'nuclear' not in self.active_layers:
            domain = urlparse(url).netloc
            ref = f"https://www.google.com/search?q={quote_plus(domain)}"
            target_url += ("&" if "?" in target_url else "?") + f"ved=0ahUKEwi{random.randint(1000,9999)}"

        if 'nuclear' in self.active_layers:
            self._log("NUCLEAR", "Using Google Cache pivot...")
            target_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"

        persona = {"id": self.engine, "ua": ua_map.get(self.engine, self.engine), "ref": ref}
        gen_headers = self._build_headers(self.active_layers, persona)
        
        user_headers = kwargs.pop('headers', {})
        if 'json' in kwargs: 
            gen_headers["Content-Type"] = "application/json"
        elif 'data' in kwargs: 
            gen_headers["Content-Type"] = "application/x-www-form-urlencoded"
        gen_headers.update(user_headers)

        # Hooks
        for process in self.hooks:
            try:
                if asyncio.iscoroutinefunction(process):
                    result = await process(target_url, gen_headers, kwargs)
                else:
                    result = process(target_url, gen_headers, kwargs)

                if result and isinstance(result, tuple) and len(result) == 3:
                    target_url, gen_headers, kwargs = result
                else:
                    self._log("HOOK-WARN", f"Hook '{process.__name__}' ignored (Invalid return format).")
            except Exception as e:
                self._log("HOOK-ERROR", f"Error in {process.__name__}: {e}")

        if (self.imitation_mode or 'cookie_warmup' in self.active_layers) and retry_count == 0:
            await self._cookie_warmup_routine(url)
            if self.imitation_mode:
                await self._simulate_dom_loading(url)

        if 'jitter' in self.active_layers:
            await asyncio.sleep(random.uniform(*self.jitter_range))

        proxies = kwargs.pop('proxies', None)
        if not proxies:
            if self.use_tor: 
                proxies = {"http": self.tor_proxy, "https": self.tor_proxy}
            elif self.proxies_list:
                p = self.proxies_list[self.current_proxy_idx]
                proxies = {"http": p, "https": p}
        
        timeout = kwargs.pop('timeout', self.timeout)

        try:
            self._log("DEPLOY", f"[{method.upper()}] {urlparse(target_url).netloc}")
            resp = await self.session.request(
                method=method.upper(), 
                url=target_url, 
                headers=gen_headers,
                impersonate=self.engine, 
                proxies=proxies, 
                http_version=2,
                timeout=timeout, 
                **kwargs
            )

            # Post-Request Hooks
            for hook in self.response_hooks:
                try:
                    if asyncio.iscoroutinefunction(hook): 
                        await hook(resp)
                    else: 
                        hook(resp)
                except Exception as e: 
                    self._log("RESP-HOOK-ERROR", str(e))

            # Retry logic with exponential backoff
            if resp.status_code in [403, 429] and retry_count < self.retry_config["max_retries"] and 'nuclear' not in self.active_layers:
                self._log("BLOCKED", f"WAF {self._recon_waf(resp)} detected. Retry...")
                self._update_stats(success=False, blocked=True)
                
                backoff_time = min(
                    self.retry_config["backoff_factor"] ** retry_count,
                    self.retry_config["backoff_max"]
                )
                await asyncio.sleep(backoff_time)
                
                if self.auto_rotate and self.proxies_list: 
                    self.rotate_proxy()
                self.engine = "safari15_5" if "chrome" in self.engine else "chrome120"
                self.active_layers = NUCLEAR_LAYER
                return await self.request(method, url, retry_count=retry_count+1, **kwargs)

            if resp.status_code == 200:
                self._update_stats(success=True)
                if self.save_on_success:
                    self.save_cookies()
            else:
                self._update_stats(success=False)

            return resp

        except Exception as e:
            self._log("CRASH", str(e))
            self._update_stats(success=False)
            
            if retry_count < self.retry_config["max_retries"] and self.proxies_list:
                backoff_time = min(
                    self.retry_config["backoff_factor"] ** retry_count,
                    self.retry_config["backoff_max"]
                )
                await asyncio.sleep(backoff_time)
                self.rotate_proxy()
                return await self.request(method, url, retry_count=retry_count+1, **kwargs)
            return None

    # HTTP Methods
    async def get(self, url, **kwargs): 
        return await self.request("GET", url, **kwargs)
    
    async def post(self, url, **kwargs): 
        return await self.request("POST", url, **kwargs)
    
    async def put(self, url, **kwargs): 
        return await self.request("PUT", url, **kwargs)
    
    async def delete(self, url, **kwargs): 
        return await self.request("DELETE", url, **kwargs)
    
    async def head(self, url, **kwargs): 
        return await self.request("HEAD", url, **kwargs)
    
    async def options(self, url, **kwargs): 
        return await self.request("OPTIONS", url, **kwargs)
    
    async def patch(self, url, **kwargs): 
        return await self.request("PATCH", url, **kwargs)
    
    async def trace(self, url, **kwargs): 
        return await self.request("TRACE", url, **kwargs)
    
    async def connect(self, url, **kwargs): 
        return await self.request("CONNECT", url, **kwargs)
    
    async def smart_json(self, url, **kwargs):
        r = await self.get(url, **kwargs)
        try: 
            return r.json() if r else None
        except:
            self._log("ERROR", "The response is not valid JSON.")
            return None