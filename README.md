<p align="center">
  <strong>AI API key generation & validation tool for research and authorized testing</strong>
</p>

<p align="center">
  <a href="https://github.com/wlzbi-exe/Ai-API-tk-Scraper">
    <img src="https://img.shields.io/badge/GitHub-wlzbi--exe%2FAi--API--tk--Scraper-181717?style=for-the-badge&logo=github" alt="GitHub">
  </a>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/CLI-Rich-FF4B4B?style=for-the-badge" alt="CLI">
</p>

<p align="center">
  <a href="https://t.me/rejerks">
    <img src="https://img.shields.io/badge/Telegram-@rejerks-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  </a>
  <a href="https://t.me/wlzbi">
    <img src="https://img.shields.io/badge/Channel-@wlzbi-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Channel">
  </a>
</p>

Overview
AI API TK Scraper is a terminal-based Python tool that generates candidate API-key strings for supported AI providers and sends requests to their configured API endpoints to classify the responses.
The tool currently includes provider configurations for:
- Claude — Anthropic Messages API
- Kimi — Moonshot chat completions API
The terminal interface uses Rich for live provider panels, status information, response details, timing, and hit counts.
Important: Use this project only with APIs, accounts, keys, systems, and infrastructure that you own or are explicitly authorized to test. Do not use it to obtain, access, or abuse credentials belonging to other people or organizations.

Features
- Claude and Kimi provider configurations
- Random candidate API-key generation
- Configurable API key prefixes and lengths
- Randomized request headers
- Generated device/request fingerprints
- Optional proxy-file support
- Automatic request retries
- Response/status classification
- Rich terminal UI
- Live/dead result tracking
- Saves successful results to wlzbi-apis.json
- Avoids saving duplicate API keys already present in the output file
Supported Providers
Provider	Endpoint	Authentication
Claude	https://api.anthropic.com/v1/messages	x-api-key
Kimi	https://api.moonshot.ai/v1/chat/completions	Authorization: Bearer ...


The exact provider models and request payloads are defined directly in the script.
Requirements
- Python 3.x
- requests
- rich
Install the dependencies with:
pip install requests rich
Usage
Run the script:
python api-key-scrap.py
On startup, the tool asks whether you want to load proxies:
Load proxies? (y/n) >
If you select y, provide the path to your proxy list:
Proxy file path >
The proxy file is read line-by-line. Empty lines and lines beginning with # are ignored.
Supported proxy formats include entries with a scheme such as:
http://host:port
https://host:port
and entries containing credentials.
Output
Successful responses are collected and written to:
wlzbi-apis.json
Each saved result can contain information such as:
{
  "provider": "Kimi",
  "api_key": "...",
  "model": "...",
  "endpoint": "...",
  "auth_header": "Authorization",
  "auth_format": "Bearer {key}",
  "response": "...",
  "captured_at": "...",
  "response_ms": 123.4,
  "proxy": null,
  "user_agent": "...",
  "fingerprint": "...",
  "request_id": "..."
}
Existing API keys in the output file are checked before new results are appended.
Response Classification
The tool classifies common API responses including:
Status	Classification
200	200 OK / KEY LIVE
401	401 UNAUTH
403	403 FORBIDDEN
404	404
429	429 RATE
5xx	Server error
Timeout	TIMEOUT
Connection/DNS failure	NETWORK
Proxy failure	PROXY FAIL


A successful 200 response is recorded as a hit by the script.
Terminal Interface
The CLI displays separate panels for each provider with information such as:
- API key
- Current model
- Status
- Response
- Request time
- Number of attempts
- Live count
The terminal also displays the project byline:
BY @rejerks | WLZBI
Configuration
The main configuration values are defined near the top of api-key-scrap.py, including:
wlzbidelay = 0.5
wlzbikeylen = 48
wlzbliclaudelen = 95
wlzbiout = "wlzbi-apis.json"
wlzbiretries = 2
Provider-specific settings such as endpoints, prefixes, models, authentication headers, and payloads are also defined in the W configuration.
Project Structure
Ai-API-tk-Scraper/
├── api-key-scrap.py
└── README.md
The output file wlzbi-apis.json is generated when successful results are found.

Credits
GitHub: @wlzbi-exe
Telegram: @rejerks
Channel: @wlzbi


<p align="center">
  <strong style="color: black;">@rejerks | WLZBI</strong
