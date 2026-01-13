# Kuasarr

Kuasarr connects JDownloader with Radarr, Sonarr and LazyLibrarian. It also decrypts links protected by CAPTCHAs.

### Features
- **Quasarr Fork**: Enhanced with additional hosters and an open download API.
- **Captcha Integration**: Automatic solving via DeathByCaptcha or 2Captcha.
- **Hoster Filtering**: Exclude unwanted mirrors directly via the Web UI.
- **PWA Support**: Installable as a standalone app on desktop and mobile.

## Installation

You can install Kuasarr via pip:

```bash
pip install kuasarr
```

## Quick Start

After installation, you can start Kuasarr using the command line:

```bash
kuasarr
```

By default, Kuasarr will listen on port `9999`. You can specify a different port:

```bash
kuasarr --port 8080
```

### Configuration

All configuration (Hostnames, FlareSolverr, API keys) can be managed via the Web UI or directly in the `kuasarr.ini` file located in your configuration directory.

## Links
- **GitHub**: [https://github.com/weedo078/Kuasarr](https://github.com/weedo078/Kuasarr)
- **Support**: [Matrix Chat](https://matrix.to/#/@kuasarr-support:envs.net)

## License
MIT
