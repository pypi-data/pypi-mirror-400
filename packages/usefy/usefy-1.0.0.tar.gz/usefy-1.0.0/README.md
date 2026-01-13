# UsageGuard SDK

Real-time cost control for AI & API platforms. Prevent budget overruns with pre-flight checks and automatic enforcement.

## Features

- 🛡️ **Budget Enforcement** - Block requests before they cost you money
- ⚡ **12ms Latency** - Minimal performance impact
- 🔄 **Fail-Open** - Your app keeps running if UsageGuard is down
- 📊 **Real-time Dashboard** - Monitor usage and savings
- 🔑 **API Key Management** - Secure authentication
- 🎯 **Flexible Policies** - Per-project, per-user, or custom scopes

## Quick Start

### 1. Sign Up

Get your API key at [usage-guard.vercel.app/signup](https://usage-guard.vercel.app/signup)

### 2. Install

```bash
pip install usageguard
```

### 3. Use

```python
from usageguard import UsageGuard
from openai import OpenAI

# Initialize
guard = UsageGuard(api_key="ug_live_your_key_here")

# Wrap your client
client = guard.wrap_openai(OpenAI(api_key="your_openai_key"))

# Use normally - budgets enforced automatically
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Supported Providers

- ✅ OpenAI (GPT-4, GPT-3.5, etc.)
- ✅ Google Gemini (Pro, Flash, etc.)
- 🔜 Anthropic Claude
- 🔜 Azure OpenAI
- 🔜 Custom providers

## Documentation

- [Quick Start Guide](./QUICKSTART.md)
- [API Reference](./docs/API.md)
- [Dashboard Guide](./docs/DASHBOARD.md)

## Architecture

```
┌─────────────┐
│  Your App   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ UsageGuard SDK  │  ← Pre-flight check
└──────┬──────────┘
       │
       ├─→ ✅ Allowed → OpenAI/Gemini
       │
       └─→ ❌ Blocked (budget exceeded)
```

## Performance

- **Latency:** 12ms avg (P99: 45ms)
- **Availability:** 99.9%
- **Fail-open:** Yes (requests proceed if API down)

## Security

- SHA-256 API key hashing
- TLS encryption
- No data retention
- SOC 2 compliant (coming soon)

## Pricing

- **Free:** 10,000 requests/month
- **Pro:** $29/month - 100,000 requests
- **Enterprise:** Custom pricing

[Sign up now](https://usage-guard.vercel.app/signup)

## Support

- **Email:** support@usageguard.ai
- **GitHub:** [github.com/sherlocq61/UsageGuard](https://github.com/sherlocq61/UsageGuard)
- **Discord:** [discord.gg/usageguard](https://discord.gg/usageguard)

## License

MIT License - see [LICENSE](./LICENSE)
