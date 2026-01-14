# Usefy SDK

Real-time cost control for AI & API platforms. Prevent budget overruns with pre-flight checks and automatic enforcement.

## Features

- 🛡️ **Budget Enforcement** - Block requests before they cost you money
- ⚡ **12ms Latency** - Minimal performance impact
- 🔄 **Fail-Open** - Your app keeps running if Usefy is down
- 📊 **Real-time Dashboard** - Monitor usage and savings
- 🔑 **API Key Management** - Secure authentication
- 🎯 **Flexible Policies** - Per-project, per-user, or custom scopes

## Quick Start

### 1. Sign Up

Get your API key at [usefy.ai/signup](https://usefy.ai/signup)

### 2. Install

**Python:**
```bash
pip install usefy
```

**JavaScript:**
```bash
npm install usefy
```

### 3. Use

**Python:**
```python
from usefy import UsefyClient
from openai import OpenAI

# Initialize
guard = UsefyClient(api_key="us_live_your_key_here", project_id="your_project")

# Wrap your client
client = guard.wrap_openai(OpenAI(api_key="your_openai_key"))

# Use normally - budgets enforced automatically
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**JavaScript:**
```javascript
import { UsefyClient } from 'usefy';
import OpenAI from 'openai';

const guard = new UsefyClient({
    apiKey: 'us_live_your_key_here',
    projectId: 'your_project'
});

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const client = guard.wrapOpenAI(openai);

const response = await client.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: 'Hello!' }]
});
```

## Supported Providers

- ✅ OpenAI (GPT-4, GPT-3.5, etc.)
- ✅ Google Gemini (Pro, Flash, etc.)
- ✅ Anthropic Claude
- ✅ Azure OpenAI
- ✅ And more...

## Documentation

- [Quick Start Guide](https://usefy.ai/docs)
- [Dashboard](https://usefy.ai/dashboard)

## Architecture

```
┌─────────────┐
│  Your App   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   Usefy SDK     │  ← Pre-flight check
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

## Pricing

- **Free:** 10,000 requests/month
- **Pro:** $29/month - 100,000 requests
- **Enterprise:** Custom pricing

[Sign up now](https://usefy.ai/signup)

## Support

- **Email:** support@usefy.ai
- **GitHub:** [github.com/sherlocq61/usefy](https://github.com/sherlocq61/usefy)

## License

MIT License - USEFY LTD
