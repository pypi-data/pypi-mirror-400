# GreenRefactor Python SDK

WS öncelikli, HTTP fallback’li Python istemcisi. `pycarbon.dashboard.server` ile konuşur.

## Kurulum (yerel pip)

```bash
cd /Users/aligokkaya/Desktop/Carbon/code-carbon/sdks/greenrefactor-python
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Bu sayede `greenrefactor` modülünü import edebilirsin.

## Örnekler

Tüm örnekler `examples/` altında. Ortak adımlar:

```bash
cd /Users/aligokkaya/Desktop/Carbon/code-carbon/sdks/greenrefactor-python/examples
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # -e .. içerir
```

### Basit Span (`simple_span.py`)

```bash
CARBON_HOST=127.0.0.1 python simple_span.py
```

Script `CarbonClient` ile bir session başlatır ve `@carbon_span` dekoratörüyle CPU-yoğun işi dashboard’a gönderir.

> SDK artık span başlangıç/bitiş mesajlarına otomatik olarak `ts` (timestamp) ekler ve decorator/context manager'lara `meta` sözlüğü geçebilirsin.

Örnek kullanım:

```python
from greenrefactor import carbon_span, send_heartbeat

send_heartbeat(
    agent="python-simple",
    version="1.0.0",
    interval=30,
    meta={"lang": "python", "env": "local"},
)

@carbon_span("python-demo.work", meta=lambda: {"phase": "warmup"})
def heavy_python_work():
    ...
```

`send_heartbeat` sadece HTTP üzerinden `/api/v1/heartbeat` çağırır; ws bağlantısı gerektirmez.

### Ağır Test (`demo.py`)

```bash
BURN_MINUTES=1 python demo.py
```

CPU, disk, bellek ve opsiyonel GPU/net yükleri oluşturur. Dashboard’da belirgin enerji artışı görürsün.

> Unutma: Önce backend’i aç (`python -m pycarbon.dashboard.server` veya Docker imajı).

