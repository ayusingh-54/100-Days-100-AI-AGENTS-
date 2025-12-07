<div align="center">

# 🤖 AI-Powered Instagram DM Bot

<img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
<img src="https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg" alt="OpenAI">
<img src="https://img.shields.io/badge/Platform-Instagram-E4405F.svg" alt="Instagram">
<img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">

**An intelligent Instagram Direct Message bot that automatically responds to your DMs using OpenAI's GPT-4o-mini, creating natural, human-like conversations.**

[Features](#-features) •
[Installation](#-installation) •
[Configuration](#️-configuration) •
[Usage](#-usage) •
[How It Works](#-how-it-works) •
[Disclaimer](#️-disclaimer)

---

</div>

## 📸 Demo

```
Message from user: "Hey, what's up?"
Bot response: "not much, just chilling. you?"

Message from user: "How are you doing today?"
Bot response: "doing pretty good actually! hbu? 😊"
```

The bot responds naturally, like a real human texting on Instagram!

---

## ✨ Features

| Feature                     | Description                                                        |
| --------------------------- | ------------------------------------------------------------------ |
| 🧠 **AI-Powered Responses** | Uses OpenAI GPT-4o-mini for intelligent, context-aware replies     |
| 💬 **Human-Like Chat**      | Responds casually with natural language, emojis, and texting style |
| 🔄 **Auto-Reply**           | Continuously monitors and responds to new DMs automatically        |
| 🌍 **Multi-Language**       | Configure response language (English, Spanish, Hindi, etc.)        |
| 🔒 **Proxy Support**        | Optional proxy configuration for enhanced privacy                  |
| 👥 **Group Control**        | Enable/disable responses to group messages                         |
| ⚡ **Async Performance**    | Built with asyncio for efficient, non-blocking operations          |
| 🔐 **Secure Auth**          | Encrypted password handling and secure session management          |

---

## 📁 Project Structure

```
07 AI-Powered-Instagram-DM-Bot/
├── 📄 main.py                 # Entry point - runs the bot loop
├── 📄 config.json             # Bot configuration (credentials, settings)
├── 📄 .env                    # Environment variables (API keys)
├── 📄 proxies.txt             # Proxy list (optional)
├── 📄 requirements.txt        # Python dependencies
├── 📄 install.py              # Dependency installer
│
└── 📁 wezaxy/                 # Core bot modules
    ├── 📄 ai.py               # OpenAI GPT integration
    ├── 📄 login.py            # Instagram authentication
    ├── 📄 test.py             # DM monitoring & processing
    ├── 📄 sendmessage.py      # Message sending handler
    └── 📄 Authorization.json  # Session token storage
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
- Instagram account credentials

### Step 1: Clone the Repository

```bash
git clone https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-.git
cd "100-Days-100-AI-AGENTS-/07 AI-Powered-Instagram-DM-Bot"
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
pip install python-dotenv
```

Or use the installer:

```bash
python install.py
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

## ⚙️ Configuration

Edit the `config.json` file with your settings:

```json
{
  "username": "your_instagram_username",
  "password": "your_instagram_password",
  "language": "English",
  "use_proxy": false,
  "group_messages": false
}
```

### Configuration Options

| Option           | Type    | Description                                                     |
| ---------------- | ------- | --------------------------------------------------------------- |
| `username`       | string  | Your Instagram username                                         |
| `password`       | string  | Your Instagram password                                         |
| `language`       | string  | Language for AI responses (e.g., "English", "Spanish", "Hindi") |
| `use_proxy`      | boolean | Enable proxy usage (`true`/`false`)                             |
| `group_messages` | boolean | Reply to group DMs (`true`/`false`)                             |

### Proxy Setup (Optional)

If using proxies, add them to `proxies.txt`:

```
username:password@proxy_host:port
username:password@proxy_host:port
```

---

## 🎯 Usage

### Start the Bot

```bash
python main.py
```

### Expected Output

```
Login successful
Message from 123456789: Hey there!
message sent successfully
the last dm message that came in: None
```

### Stop the Bot

Press `Ctrl + C` to stop the bot.

---

## 🔄 How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   📱 User sends DM  ──►  🔍 Bot detects  ──►  🧠 OpenAI GPT    │
│                                                                 │
│                              ▼                                  │
│                                                                 │
│   📤 Bot replies   ◄──  💬 Human-like response generated       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Flow:

1. **Authentication**: Bot logs into Instagram using encrypted credentials
2. **Monitoring**: Continuously polls the DM inbox for new messages
3. **Processing**: New messages are sent to OpenAI GPT-4o-mini
4. **Response**: AI generates a casual, human-like reply
5. **Delivery**: Bot sends the response back to the user
6. **Loop**: Process repeats every 2 seconds

### AI Personality

The bot is configured to:

- ✅ Use casual, lowercase text
- ✅ Keep responses short (1-2 sentences)
- ✅ Include occasional emojis
- ✅ Match the conversation's energy
- ❌ Never reveal it's an AI
- ❌ Avoid formal language or bullet points

---

## 🛡️ Security

| Security Feature    | Implementation                                |
| ------------------- | --------------------------------------------- |
| Password Encryption | RSA + AES encryption before transmission      |
| API Key Protection  | Stored in `.env` file (gitignored)            |
| Session Management  | Tokens stored locally in `Authorization.json` |
| Proxy Support       | Optional anonymization layer                  |

---

## 📋 Requirements

```txt
pycryptodomex    # Password encryption
requests         # HTTP requests
aiohttp          # Async HTTP client
user-agent       # User agent generation
python-dotenv    # Environment variable loading
```

---

## ⚠️ Disclaimer

> **⚠️ Important**: This project is for **educational purposes only**.

- 🚫 Using bots may violate Instagram's Terms of Service
- 🚫 Your account could be rate-limited or suspended
- ✅ Use a secondary/test account, not your main account
- ✅ Be responsible and respect others' privacy
- ✅ The author is not responsible for any misuse or consequences

---

## 🐛 Troubleshooting

| Issue            | Solution                                 |
| ---------------- | ---------------------------------------- |
| Login failed     | Check username/password in `config.json` |
| Rate limited     | Wait 50+ seconds, consider using proxies |
| OpenAI error     | Verify API key in `.env` file            |
| Connection reset | Instagram rate limiting - wait and retry |
| No response      | Check if OpenAI API key has credits      |

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

## 👨‍💻 Author

**Ayush Singh**

[![Email](https://img.shields.io/badge/Email-Ayusingh693%40gmail.com-red?style=for-the-badge&logo=gmail)](mailto:Ayusingh693@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-ayusingh--54-black?style=for-the-badge&logo=github)](https://github.com/ayusingh-54)

---

⭐ **If you found this helpful, please star the repository!** ⭐

_Part of the **100 Days, 100 AI Agents** Challenge_ 🚀

</div>
