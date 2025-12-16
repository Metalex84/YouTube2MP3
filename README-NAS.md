# YouTube2MP3 - NAS Deployment Branch

This branch (`nas`) contains production-ready configuration for deploying YouTube2MP3 on custom NAS servers using Apache or Nginx.

## 🎯 What's Different in This Branch?

This branch adds enterprise-grade deployment capabilities:

- **Production WSGI Entry Point** (`wsgi.py`) for Apache mod_wsgi and Gunicorn
- **Apache Configurations** - Two options:
  - Direct mod_wsgi deployment
  - Gunicorn reverse proxy (recommended for WebSocket support)
- **Nginx Configuration** - Lightweight alternative to Apache
- **Systemd Service** - Run as a system service with automatic restart
- **Automated Installation** - One-command deployment script
- **Comprehensive Documentation** - Step-by-step deployment guide

## 🚀 Quick Start

### Option 1: Automated Installation (Recommended)

```bash
# On your NAS server
git clone <your-repo-url> /tmp/youtube2mp3
cd /tmp/youtube2mp3
git checkout nas
sudo bash install-nas.sh
```

The script will guide you through:
1. Dependency installation
2. Web server selection (Apache or Nginx)
3. Application setup
4. Service configuration

### Option 2: Manual Installation

Follow the detailed guide in [NAS-DEPLOYMENT.md](NAS-DEPLOYMENT.md)

## 📂 New Files in This Branch

```
YouTube2MP3/
├── wsgi.py                              # WSGI entry point
├── install-nas.sh                       # Automated installer
├── NAS-DEPLOYMENT.md                    # Complete deployment guide
├── apache-config/
│   ├── youtube2mp3.conf                 # Apache + mod_wsgi
│   └── youtube2mp3-gunicorn.conf        # Apache + Gunicorn (recommended)
├── nginx-config/
│   └── youtube2mp3.conf                 # Nginx + Gunicorn
└── systemd/
    └── youtube2mp3.service              # Systemd service file
```

## 🏗️ Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP/HTTPS
       ↓
┌─────────────────────────────────┐
│  Apache or Nginx (Port 80/443) │  ← Reverse Proxy
└────────────┬────────────────────┘
             │ Proxy
             ↓
┌────────────────────────────┐
│  Gunicorn (Port 8000)      │  ← WSGI Server
│  + Eventlet Worker         │     (WebSocket support)
└────────────┬───────────────┘
             │
             ↓
┌────────────────────────────┐
│  Flask + SocketIO App      │  ← Your Application
│  + yt-dlp + FFmpeg         │
└────────────────────────────┘
```

## 🔧 Supported Configurations

| Web Server | WSGI Server | WebSocket | Recommended |
|------------|-------------|-----------|-------------|
| Apache + mod_wsgi | mod_wsgi | ❌ | Good for basic usage |
| Apache + Gunicorn | Gunicorn + eventlet | ✅ | **Recommended** |
| Nginx + Gunicorn | Gunicorn + eventlet | ✅ | **Best performance** |

## 📋 System Requirements

- **OS**: Linux (Debian/Ubuntu/CentOS/RHEL/Fedora)
- **Python**: 3.7+
- **FFmpeg**: Latest version
- **RAM**: Minimum 1GB
- **Storage**: 5GB+ (for app + downloads)
- **Network**: Port 80 and 443 accessible

## 🌐 Access After Installation

- **Local Network**: `http://your-nas-ip/` or `http://your-nas-hostname.local/`
- **Remote Access**: Configure port forwarding, VPN, or reverse proxy tunnel

## 🔒 Security Features

- ✅ Secure systemd service with restricted permissions
- ✅ Security headers (HSTS, XSS Protection, etc.)
- ✅ SSL/HTTPS support (manual configuration required)
- ✅ File type restrictions on downloads directory
- ✅ Non-root user execution (www-data)
- ✅ Request size limits (16MB)
- ✅ Firewall configuration included

## 🛠️ Management Commands

```bash
# Service management
sudo systemctl start youtube2mp3
sudo systemctl stop youtube2mp3
sudo systemctl restart youtube2mp3
sudo systemctl status youtube2mp3

# View logs
sudo journalctl -u youtube2mp3 -f

# Update application
cd /opt/youtube2mp3
sudo systemctl stop youtube2mp3
sudo -u www-data git pull origin nas
sudo -u www-data /opt/youtube2mp3/venv/bin/pip install -r requirements.txt --upgrade
sudo systemctl start youtube2mp3
```

## 📊 Monitoring

Application logs are available in:
- Systemd journal: `sudo journalctl -u youtube2mp3`
- Application logs: `/var/log/youtube2mp3/`
- Web server logs:
  - Apache: `/var/log/apache2/youtube2mp3_*.log`
  - Nginx: `/var/log/nginx/youtube2mp3_*.log`

## 🧹 Maintenance

### Automatic Cleanup of Old Downloads

Add to crontab (`sudo crontab -e`):
```bash
# Delete downloads older than 7 days, every day at 3 AM
0 3 * * * find /opt/youtube2mp3/downloads -type f -mtime +7 -delete
```

### Backup Configuration

```bash
# Backup application and configuration
sudo tar -czf youtube2mp3-backup-$(date +%Y%m%d).tar.gz \
    /opt/youtube2mp3 \
    /etc/systemd/system/youtube2mp3.service \
    /etc/apache2/sites-available/youtube2mp3.conf
```

## 🐛 Troubleshooting

### Service won't start
```bash
sudo systemctl status youtube2mp3
sudo journalctl -u youtube2mp3 -n 50
```

### WebSocket not working
```bash
# Apache: Enable proxy modules
sudo a2enmod proxy_wstunnel
sudo systemctl restart apache2

# Nginx: Check config
sudo nginx -t
```

### Permission errors
```bash
sudo chown -R www-data:www-data /opt/youtube2mp3
sudo chmod 775 /opt/youtube2mp3/downloads
```

## 📚 Documentation

- **[NAS-DEPLOYMENT.md](NAS-DEPLOYMENT.md)** - Complete deployment guide
- **[README.md](README.md)** - General project information
- **[README-Web.md](README-Web.md)** - Web interface features
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Cloud deployment (Render, Vercel)

## 🔄 Switching Between Branches

```bash
# Switch to web branch (for Render/Vercel)
git checkout web

# Switch to main branch (CLI only)
git checkout main

# Switch back to NAS branch
git checkout nas
```

## 💡 Tips

1. **Use Nginx** for best performance on resource-constrained NAS devices
2. **Set up SSL** using Let's Encrypt for secure access
3. **Configure automatic cleanup** to prevent disk space issues
4. **Monitor logs** regularly for errors
5. **Use VPN** for secure remote access instead of port forwarding

## 🆘 Need Help?

Check these resources:
- Full deployment guide: [NAS-DEPLOYMENT.md](NAS-DEPLOYMENT.md)
- Systemd logs: `sudo journalctl -u youtube2mp3 -f`
- Test Gunicorn directly: `/opt/youtube2mp3/venv/bin/gunicorn --check-config wsgi:application`

## 📄 License

Same as main project - see [LICENSE](LICENSE)
