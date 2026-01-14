from __future__ import annotations
import os, json, time, uuid, socket, platform
from functools import wraps
from typing import Callable

try:
    import psutil
    _PROCESS = psutil.Process()
except ImportError:
    psutil = None
    _PROCESS = None

# --- Config (ENV) ---
_WS_URL = os.getenv("CARBON_SERVER_WS", "ws://127.0.0.1:8124")
_HTTP_HOST = os.getenv("CARBON_HOST", "127.0.0.1")
_HTTP_PORT = int(os.getenv("CARBON_HTTP_PORT", "8123"))
_HTTP_TIMEOUT = float(os.getenv("CARBON_HTTP_TIMEOUT", "2.0"))
_HOSTNAME = socket.gethostname()
_PLATFORM = platform.system().lower()

def ws_url() -> str:
    return _WS_URL

def init(
    ws_url: str | None = None,
    http_host: str | None = None,
    http_port: int | None = None,
    http_timeout: float | None = None,
):
    """SDK runtime configini güncelle."""
    global _WS_URL, _HTTP_HOST, _HTTP_PORT, _HTTP_TIMEOUT
    if ws_url is not None:
        _WS_URL = ws_url
    if http_host is not None:
        _HTTP_HOST = http_host
    if http_port is not None:
        _HTTP_PORT = int(http_port)
    if http_timeout is not None:
        _HTTP_TIMEOUT = float(http_timeout)

# --- Transports: WS primary, HTTP fallback ---
try:
    import websocket  # websocket-client
except Exception:
    websocket = None

def _send_ws(payload: dict) -> bool:
    """WS gönder; başarılıysa True, aksi halde False döndür."""
    if websocket is None:
        return False
    try:
        ws = websocket.create_connection(_WS_URL, timeout=_HTTP_TIMEOUT)
        ws.send(json.dumps(payload))
        ws.close()
        return True
    except Exception:
        return False

def _post_http(path: str, obj: dict) -> bool:
    """HTTP fallback: /api/v1/span/* uçları."""
    import urllib.request
    url = f"http://{_HTTP_HOST}:{_HTTP_PORT}{path}"
    data = json.dumps(obj).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as r:
            # 2xx kabul
            return 200 <= r.status < 300
    except Exception:
        return False

def _normalize_meta(meta: dict | None | Callable[..., dict], *args, **kwargs) -> dict:
    candidate = meta
    if callable(candidate):
        try:
            candidate = candidate(*args, **kwargs)
        except Exception:
            candidate = {}
    return candidate if isinstance(candidate, dict) else {}

# --- Geolocation Cache ---
_GEO_CACHE: dict | None = None

def _detect_location() -> dict:
    """
    Detect server location via Env -> AWS IMDS -> IP Geo.
    Returns dict with lat, lon, region, provider.
    """
    global _GEO_CACHE
    if _GEO_CACHE is not None:
        return _GEO_CACHE
    
    # 1. Environment Variables
    env_lat = os.getenv("CARBON_LOCATION_LAT")
    env_lon = os.getenv("CARBON_LOCATION_LON")
    if env_lat and env_lon:
        _GEO_CACHE = {
            "lat": float(env_lat),
            "lon": float(env_lon),
            "source": "env"
        }
        return _GEO_CACHE

    import urllib.request
    
    # 2. AWS IMDS (Metadata Service)
    # Fast check for availability zone
    if "AWS_REGION" in os.environ or os.path.exists("/sys/hypervisor/uuid"):
        try:
            # Token (IMDSv2)
            req = urllib.request.Request(
                "http://169.254.169.254/latest/api/token", 
                headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"}, 
                method="PUT"
            )
            with urllib.request.urlopen(req, timeout=0.5) as r:
                token = r.read().decode("utf-8")
            
            # Region
            req = urllib.request.Request(
                "http://169.254.169.254/latest/meta-data/placement/region", 
                headers={"X-aws-ec2-metadata-token": token}
            )
            with urllib.request.urlopen(req, timeout=0.5) as r:
                region = r.read().decode("utf-8")
                
            _GEO_CACHE = {
                "provider": "aws",
                "region": region,
                "source": "imds"
            }
            return _GEO_CACHE
        except Exception:
            pass # Not AWS or IMDS blocked
            
    # 3. IP Geolocation (Universal Fallback)
    try:
        # Using free connection-based API (no key required for basic rate limit)
        # Service: ip-api.com (free for non-commercial/low volume)
        with urllib.request.urlopen("http://ip-api.com/json/?fields=status,lat,lon,regionName,isp", timeout=2.0) as r:
            data = json.loads(r.read().decode("utf-8"))
            if data.get("status") == "success":
                _GEO_CACHE = {
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "region": data.get("regionName"),
                    "provider": data.get("isp"),
                    "source": "ip-geo"
                }
                return _GEO_CACHE
    except Exception as e:
        print(f"DEBUG: IP Geo failed: {e}")
        pass
        
    _GEO_CACHE = {} # Cache empty result to avoid retrying
    return _GEO_CACHE

def _runtime_meta() -> dict:
    meta = {
        "pid": os.getpid(),
        "hostname": _HOSTNAME,
        "platform": _PLATFORM,
        "project_name": os.getenv("CARBON_PROJECT_NAME", "default-project")
    }
    
    # Add geolocation if available
    geo = _detect_location()
    if geo:
        meta["geo"] = geo
        
    return meta

def _with_runtime_meta(meta: dict | None) -> dict:
    payload = _runtime_meta()
    if isinstance(meta, dict):
        payload.update(meta)
    return payload

def _get_resource_snapshot() -> dict:
    """Capture current CPU and memory usage for this process."""
    if not psutil or not _PROCESS:
        return {}
    try:
        cpu_percent = _PROCESS.cpu_percent(interval=0.01)  # Non-blocking
        mem_info = _PROCESS.memory_info()
        return {
            "cpu_percent": cpu_percent,
            "memory_rss_mb": mem_info.rss / (1024 * 1024),
            "memory_vms_mb": mem_info.vms / (1024 * 1024),
        }
    except Exception:
        return {}

def _span_start(span_id: str, name: str, meta: dict | None = None) -> None:
    meta_obj = _with_runtime_meta(meta if isinstance(meta, dict) else _normalize_meta(meta))
    resources = _get_resource_snapshot()
    ts = time.time()
    msg = {
        "cmd": "span_start",
        "id": span_id,
        "name": name,
        "ts": ts,
        "meta": meta_obj,
        "resources": resources
    }
    if _send_ws(msg):
        return
    # WS başarısızsa HTTP fallback
    _post_http("/api/v1/span/start", {
        "id": span_id,
        "name": name,
        "ts": ts,
        "meta": meta_obj,
        "resources": resources
    })

def _span_end(span_id: str, meta: dict | None = None) -> None:
    meta_obj = _with_runtime_meta(meta if isinstance(meta, dict) else _normalize_meta(meta))
    resources = _get_resource_snapshot()
    ts = time.time()
    msg = {
        "cmd": "span_end",
        "id": span_id,
        "ts": ts,
        "meta": meta_obj,
        "resources": resources
    }
    if _send_ws(msg):
        return
    _post_http("/api/v1/span/end", {
        "id": span_id,
        "ts": ts,
        "meta": meta_obj,
        "resources": resources
    })

def send_heartbeat(
    agent: str,
    *,
    meta: dict | None = None,
    interval: float | None = None,
    version: str | None = None,
    hostname: str | None = None,
) -> bool:
    payload: dict[str, object] = {"agent": agent}
    if interval is not None:
        payload["interval"] = interval
    if version:
        payload["version"] = version
    payload["hostname"] = hostname or _HOSTNAME
    payload["platform"] = _PLATFORM
    payload["pid"] = os.getpid()
    meta_obj = _normalize_meta(meta)
    if meta_obj:
        payload["meta"] = meta_obj
    return _post_http("/api/v1/heartbeat", payload)

# --- Public API ---
class Span:
    """Context manager: manuel span kullanımı"""
    def __init__(self, name: str, sid: str | None = None, meta: dict | None = None):
        self.name = name
        self.id = sid or str(uuid.uuid4())
        self.meta = meta or {}

    def __enter__(self):
        _span_start(self.id, self.name, self.meta)
        return self

    def __exit__(self, exc_type, exc, tb):
        _span_end(self.id, self.meta)
        # exception'ı bastırma:
        return False

def with_span(name: str, fn, *args, **kwargs):
    with Span(name):
        return fn(*args, **kwargs)

def span(name: str, meta: dict | Callable[..., dict] | None = None):
    """Decorator: @span('step', meta={'lang': 'py'})"""
    def deco(fn):
        @wraps(fn)
        def wrap(*a, **kw):
            sid = str(uuid.uuid4())
            meta_obj = _normalize_meta(meta, *a, **kw)
            
            # Capture source code
            try:
                import inspect
                source = inspect.getsource(fn)
                meta_obj['code'] = source
                meta_obj['function_code'] = source
                meta_obj['file'] = inspect.getsourcefile(fn)
                meta_obj['line'] = inspect.getsourcelines(fn)[1]
            except Exception as e:
                print(f"[SDK DEBUG] Code capture failed: {e}")
                pass
                
            _span_start(sid, name, meta_obj)
            try:
                return fn(*a, **kw)
            finally:
                _span_end(sid, meta_obj)
        return wrap
    return deco

def carbon_span(name: str, meta: dict | Callable[..., dict] | None = None):
    return span(name, meta)

class CarbonClient:
    """Tüm test boyunca tek bir 'session' span'ı aç/kapat."""
    def __init__(self, name: str = "session", meta: dict | None = None):
        self.name = name
        self.meta = meta or {}
        self.id = str(uuid.uuid4())

    def __enter__(self):
        _span_start(self.id, self.name, self.meta)
        return self

    def __exit__(self, exc_type, exc, tb):
        _span_end(self.id, self.meta)
        return False

