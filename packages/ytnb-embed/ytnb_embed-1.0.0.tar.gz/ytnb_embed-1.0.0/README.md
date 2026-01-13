# ytnb-embed

<div align="center">

[![PyPI version](https://badge.fury.io/py/ytnb-embed.svg)](https://badge.fury.io/py/ytnb-embed)
[![Python Version](https://img.shields.io/pypi/pyversions/ytnb-embed.svg)](https://pypi.org/project/ytnb-embed/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/ytnb-embed)](https://pepy.tech/project/ytnb-embed)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI](https://github.com/aatansen/ytnb-embed/workflows/CI/badge.svg)](https://github.com/aatansen/ytnb-embed/actions)

**A lightweight, privacy-focused Python package for embedding YouTube videos in Jupyter Notebooks**

[Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#usage) • [Contributing](#contributing)

</div>

---

## Overview

`ytnb-embed` provides a simple and elegant way to embed YouTube videos directly in Jupyter Notebooks. Built with privacy and simplicity in mind, it uses YouTube's privacy-enhanced mode (`youtube-nocookie.com`) to protect user privacy while maintaining full video functionality.

Perfect for data scientists, educators, and researchers who want to enrich their notebooks with video content without compromising on privacy or simplicity.

## ✨ Features

- 🎥 **One-line embedding** - Embed any YouTube video with a single function call
- 🔒 **Privacy-first** - Uses `youtube-nocookie.com` for enhanced privacy protection
- 📐 **Fully customizable** - Adjust video player dimensions to fit your needs
- 🛡️ **Smart URL parsing** - Handles all YouTube URL formats automatically
- 📝 **Built-in logging** - Comprehensive logging for debugging and monitoring
- ✅ **Type hints** - Full type annotation support for better IDE integration
- 🧪 **Well tested** - Includes unit and integration tests
- 🚀 **Lightweight** - Minimal dependencies, maximum performance

## Installation

Install `ytnb-embed` using pip:

  ```sh
  pip install ytnb-embed
  ```

### Requirements

- Python 3.13+
- IPython
- Jupyter Notebook or JupyterLab

## Quick Start

```py
from ytnb_embed import embed_yt

# Embed a YouTube video with default dimensions (780x440)
embed_yt("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Customize the video player size
embed_yt("https://www.youtube.com/watch?v=dQw4w9WgXcQ", width=640, height=360)
```

That's it! The video will be embedded directly in your Jupyter Notebook cell output.

## Usage

### Supported URL Formats

`ytnb-embed` intelligently parses all standard YouTube URL formats:

```py
from ytnb_embed import embed_yt

# Standard watch URL
embed_yt("https://www.youtube.com/watch?v=VIDEO_ID")

# Short URL
embed_yt("https://youtu.be/VIDEO_ID")

# Embed URL
embed_yt("https://www.youtube.com/embed/VIDEO_ID")

# Direct video URL
embed_yt("https://www.youtube.com/v/VIDEO_ID")

# URLs with timestamps and other parameters
embed_yt("https://www.youtube.com/watch?v=VIDEO_ID&t=30s")
```

### Custom Player Dimensions

Tailor the video player size to your notebook layout:

  ```py
  # Large player for presentations
  embed_yt("https://www.youtube.com/watch?v=VIDEO_ID", width=1024, height=576)

  # Standard 16:9 aspect ratio
  embed_yt("https://www.youtube.com/watch?v=VIDEO_ID", width=854, height=480)

  # Compact player for documentation
  embed_yt("https://www.youtube.com/watch?v=VIDEO_ID", width=560, height=315)
  ```

### Working Example

Here's a complete example demonstrating common use cases:

  ```py
  from ytnb_embed import embed_yt
  
  # Educational content
  print("📚 Python Tutorial:")
  embed_yt("https://www.youtube.com/watch?v=_uQrJ0TkZlc", width=800, height=450)
  
  # Conference talks
  print("\n🎤 Tech Talk:")
  embed_yt("https://youtu.be/cKPlPJyQrt4", width=900, height=506)

  # Quick demos
  print("\n⚡ Quick Demo:")
  embed_yt("https://www.youtube.com/watch?v=VIDEO_ID", width=640, height=360)
  ```

## 🔧 API Reference

### `embed_yt(url, width=780, height=440)`

Embeds a YouTube video in a Jupyter Notebook using an iframe.

#### Parameters

| Parameter | Type  | Default    | Description                              |
| --------- | ----- | ---------- | ---------------------------------------- |
| `url`     | `str` | *required* | YouTube video URL in any standard format |
| `width`   | `int` | `780`      | Width of the video player in pixels      |
| `height`  | `int` | `440`      | Height of the video player in pixels     |

#### Returns

- `str`: Returns `"success"` when the video is successfully embedded

#### Raises

- `InvalidURLException`: Raised when the provided URL is not a valid YouTube URL
- `Exception`: Raised for other unexpected errors during embedding

#### Example

```py
result = embed_yt("https://www.youtube.com/watch?v=VIDEO_ID", width=800, height=450)
# result == "success"
```

## 🔒 Privacy & Security

### Privacy-Enhanced Mode

`ytnb-embed` uses YouTube's privacy-enhanced mode by default. Videos are embedded from `youtube-nocookie.com`, which provides:

- **Reduced tracking** - YouTube doesn't store information about visitors unless they play the video
- **No third-party cookies** - Cookies are only set when the user interacts with the video
- **Same functionality** - All standard YouTube features remain available

### Security Features

- **URL validation** - Regex-based validation prevents injection attacks
- **Sandboxed iframe** - Videos load in isolated iframe contexts
- **Strict referrer policy** - `strict-origin-when-cross-origin` prevents data leakage

##  Contributing

Contributions are welcome and greatly appreciated! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Make** your changes
4. **Add** tests for new functionality
5. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
6. **Push** to the branch (`git push origin feature/AmazingFeature`)
7. **Open** a Pull Request

### Contribution Guidelines

- Write clear, descriptive commit messages
- Add tests for any new features or bug fixes
- Update documentation as needed
- Follow the existing code style (PEP 8)
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for full details.

## 👤 Author

- GitHub: [@aatansen](https://github.com/aatansen)
- Email: aatansen@gmail.com
- PyPI: [ytnb-embed](https://pypi.org/project/ytnb-embed/)

## 🙏 Acknowledgments

- Built for the Jupyter Notebook community
- Inspired by the need for simple, privacy-focused video embedding
- Thanks to all contributors who help improve this package

## 📮 Support

If you encounter any issues or have questions:

- 🐛 **Bug reports**: [GitHub Issues](https://github.com/aatansen/ytnb-embed/issues)
- 💡 **Feature requests**: [GitHub Issues](https://github.com/aatansen/ytnb-embed/issues)
- 📧 **Email**: aatansen@gmail.com

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/aatansen/ytnb-embed?style=social)
![GitHub forks](https://img.shields.io/github/forks/aatansen/ytnb-embed?style=social)
![GitHub issues](https://img.shields.io/github/issues/aatansen/ytnb-embed)
![GitHub pull requests](https://img.shields.io/github/issues-pr/aatansen/ytnb-embed)

<div align="center">

**Made with ❤️ for the Jupyter community**

If you find this package helpful, please consider giving it a ⭐ on [GitHub](https://github.com/aatansen/ytnb-embed)!

</div>