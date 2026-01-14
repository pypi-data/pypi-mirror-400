<div align="center">
  <img src="assets/logo.svg" width="200" height="200" alt="Beam Logo">
  
  # Beam
  
  **Cross-device clipboard.**
  
  [![PyPI version](https://badge.fury.io/py/beam-clipboard.svg)](https://pypi.org/project/beam-clipboard/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  
  [中文文档](README_CN.md)
  
  Command-line tool for cross-device text sharing via cloud API.
  
  **Just 2 commands: `bm c` (copy) and `bm p` (paste)**
</div>

## Quick Start

```bash
# Install (basic)
pip install beam-clipboard

# Install with clipboard support (recommended)
pip install beam-clipboard[clipboard]

# First time: set your personal key
bm c "hello world"
# Prompt: No key configured. Please enter your personal key:
# Enter your key (recommend 20+ characters)

# Daily use
bm c "copy this"    # copy to cloud
bm p                # paste from cloud
```

## Features

- ✨ **Minimalist** - Just `bm c` and `bm p`
- 🚀 **Zero config** - Auto setup on first use
- 🔄 **Cross-device** - Mac, Linux, Windows, iPhone browser
- 📦 **Pure Python** - No external dependencies
- 🔐 **Encrypted** - Content encrypted before upload
- 🗜️ **Compressed** - Reduce transfer size (~60% for code)
- 🔓 **Open source** - MIT License

## Usage

### Copy & Paste

```bash
# Copy text directly
bm c "hello world"

# Copy from stdin (all platforms)
echo "hello" | bm c
cat file.txt | bm c

# Copy from system clipboard (requires pyperclip)
bm c

# Platform-specific clipboard commands (alternative without pyperclip)
pbpaste | bm c           # macOS
xclip -o | bm c          # Linux X11
wl-paste | bm c          # Linux Wayland
Get-Clipboard | bm c     # Windows PowerShell

# Plain text mode (for browser viewing on mobile devices)
bm c --plain "hello world"

# Paste text
bm p
```

### Edit Key & Password

```bash
# Interactive edit (server + key + password)
bm e

# Set new key directly
bm e mynewkey

# Set custom server URL
bm e -s https://your-domain.com

# Set encryption password
bm e -p mypassword
```

### Alternative Usage

```bash
python -m beam c "hello world"
python -m beam p
```

## Use Cases

### 💻 Computer Sync

```bash
# computer A
bm c "some data"

# computer B
bm p
```

### 📱 Computer & Mobile

**Computer to Mobile (view in browser)**

```bash
# on computer
bm c --plain "hello world"

# on mobile browser
# visit: https://textdb.online/yourkey
```

**Mobile to Computer (input in browser)**

```bash
# on mobile browser
# visit: https://textdb.online/yourkey
# input your text directly

# on computer
bm p
```

## API Details

Based on [TextDB.online](https://textdb.online/) free service:

- **Create/Update**: `https://api.textdb.online/update/?key={key}&value={text}`
- **Read**: `https://textdb.online/{key}`
- **Delete**: `https://api.textdb.online/update/?key={key}&value=`

Key requirements:
- Length: 6-60 characters
- No slashes (/)
- Recommend 20+ chars for security

### Service Limitations

TextDB.online is a free public service with the following characteristics:

- ✅ **Free to use** - No registration required
- ✅ **Unlimited reads** - No limit on data retrieval
- ⚠️ **500 writes/day/IP** - Combined create/update/delete operations
- ⚠️ **Testing recommended** - Not guaranteed for production use
- ⚠️ **1-year retention** - Data auto-deleted after 1 year of inactivity
- ⚠️ **No password protection** - Use long keys (20+ chars) to avoid collisions

**Important**: This tool is designed for convenient text sharing between your own devices, not for storing critical or highly sensitive data. The encryption provides basic privacy protection but should not be relied upon for confidential information.

### Private Deployment

For production use or higher reliability, you can deploy your own TextDB server:

1. **Get the offline version**: TextDB.online offers a [private deployment version](https://demo.textdb.online/) 
2. **Configure Beam to use your server**:
   ```bash
   bm e -s https://your-domain.com
   ```
3. **Benefits of private deployment**:
   - Higher stability and performance
   - No rate limits
   - Full data control
   - Better security

For custom API server implementations, ensure they follow the TextDB API format:
- Write endpoint: `{api_base}/update/?key={key}&value={text}`
- Read endpoint: `{read_base}/{key}`

## Configuration

Config file location: `~/.config/beam/config.json`

```json
{
  "api_base": "https://api.textdb.online",
  "read_base": "https://textdb.online",
  "key": "your_personal_key",
  "password": "your_encryption_password"
}
```

- `api_base`: API server URL for write operations (default: `https://api.textdb.online`)
- `read_base`: Server URL for read operations (default: `https://textdb.online`)
- `key`: Your personal key for TextDB API
- `password`: Encryption password (default: `123456`)

### Using Private Deployment

If you deploy your own TextDB server, configure it with:

```bash
bm e -s https://your-domain.com
```

Or edit the config file directly to set `api_base` and `read_base`.

## Security

All content is **compressed** (zlib) and **encrypted** (XOR + SHA256) before upload:

```
Your text → Compress → Encrypt → Base64 → Upload
```

The server only sees encrypted data like `BM2:xxxxx...`, unable to read your content.

Use `--plain` option to skip compression and encryption for non-sensitive content that needs to be viewed in a browser on mobile devices.

> ⚠️ This is lightweight encryption for convenience, not for highly sensitive data.

## Requirements

- Python 3.6+
- pyperclip (optional, for clipboard support)

To install with clipboard support:

```bash
pip install beam-clipboard[clipboard]
```

## Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

## License

MIT License

## Author

[vw2x](https://github.com/vwww-droid)

---

**Star ⭐ this repo if you find it useful!**
