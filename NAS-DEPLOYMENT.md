# NAS Deployment Guide for YouTube2MP3

This guide covers deploying YouTube2MP3 on a custom NAS server using Apache or Nginx as a production web server.

## 🎯 Overview

This deployment uses:
- **Gunicorn** as the WSGI application server (with eventlet for WebSocket support)
- **Apache or Nginx** as a reverse proxy web server
- **Systemd** for service management
- **Python virtual environment** for dependency isolation

## 📋 Prerequisites

### System Requirements
- Linux-based NAS (Debian, Ubuntu, CentOS, or similar)
- Python 3.7 or higher
- FFmpeg
- SSH access to your NAS
- Minimum 1GB RAM
- 5GB free disk space (for application + downloads)

### Install Dependencies

#### Debian/Ubuntu
```bash
# Update package list
sudo apt update

# Install required packages
sudo apt install -y python3 python3-pip python3-venv ffmpeg apache2 libapache2-mod-wsgi-py3

# Or for Nginx instead of Apache:
# sudo apt install -y python3 python3-pip python3-venv ffmpeg nginx
```

#### CentOS/RHEL/Fedora
```bash
# Install EPEL repository (for FFmpeg)
sudo dnf install -y epel-release

# Install required packages
sudo dnf install -y python3 python3-pip ffmpeg httpd mod_wsgi

# Or for Nginx:
# sudo dnf install -y python3 python3-pip ffmpeg nginx
```

## 🚀 Quick Installation

Use the automated installation script:

```bash
# Clone the repository (or upload files to NAS)
git clone <your-repo-url> /tmp/youtube2mp3
cd /tmp/youtube2mp3
git checkout nas

# Run installation script
sudo bash install-nas.sh
```

The script will:
1. Copy files to `/opt/youtube2mp3`
2. Create Python virtual environment
3. Install dependencies
4. Set up systemd service
5. Configure Apache/Nginx
6. Start the application

After installation, access the web interface at: `http://your-nas-ip/`

## 🔧 Manual Installation

If you prefer manual installation or the script doesn't work for your setup:

### Step 1: Prepare Application Directory

```bash
# Create application directory
sudo mkdir -p /opt/youtube2mp3
sudo mkdir -p /opt/youtube2mp3/downloads
sudo mkdir -p /var/log/youtube2mp3

# Copy application files
sudo cp -r /path/to/your/youtube2mp3/* /opt/youtube2mp3/

# Set ownership
sudo chown -R www-data:www-data /opt/youtube2mp3
sudo chown -R www-data:www-data /var/log/youtube2mp3
sudo chmod 755 /opt/youtube2mp3
sudo chmod 775 /opt/youtube2mp3/downloads
```

### Step 2: Create Python Virtual Environment

```bash
cd /opt/youtube2mp3

# Create virtual environment
sudo -u www-data python3 -m venv venv

# Activate and install dependencies
sudo -u www-data /opt/youtube2mp3/venv/bin/pip install --upgrade pip
sudo -u www-data /opt/youtube2mp3/venv/bin/pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
# Copy and edit .env file
sudo cp /opt/youtube2mp3/.env.example /opt/youtube2mp3/.env
sudo chown www-data:www-data /opt/youtube2mp3/.env
sudo nano /opt/youtube2mp3/.env
```

Edit `.env` file:
```bash
SECRET_KEY=your-secret-key-here-change-this
DOWNLOAD_DIR=/opt/youtube2mp3/downloads
FFMPEG_LOCATION=/usr/bin
```

Generate a secret key:
```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

### Step 4: Set Up Systemd Service

```bash
# Copy service file
sudo cp /opt/youtube2mp3/systemd/youtube2mp3.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable youtube2mp3

# Start service
sudo systemctl start youtube2mp3

# Check status
sudo systemctl status youtube2mp3
```

### Step 5: Configure Web Server

#### Option A: Apache (Recommended for mod_wsgi)

```bash
# Enable required Apache modules
sudo a2enmod proxy proxy_http proxy_wstunnel headers rewrite ssl

# Copy configuration file
sudo cp /opt/youtube2mp3/apache-config/youtube2mp3-gunicorn.conf \
    /etc/apache2/sites-available/youtube2mp3.conf

# Edit configuration - replace 'your-nas-hostname.local' with your actual hostname
sudo nano /etc/apache2/sites-available/youtube2mp3.conf

# Enable site
sudo a2ensite youtube2mp3.conf

# Disable default site (optional)
sudo a2dissite 000-default.conf

# Test configuration
sudo apache2ctl configtest

# Reload Apache
sudo systemctl reload apache2
```

#### Option B: Nginx (Lighter alternative)

```bash
# Copy configuration file
sudo cp /opt/youtube2mp3/nginx-config/youtube2mp3.conf \
    /etc/nginx/sites-available/youtube2mp3

# Edit configuration - replace 'your-nas-hostname.local' with your actual hostname
sudo nano /etc/nginx/sites-available/youtube2mp3

# Create symlink to enable site
sudo ln -s /etc/nginx/sites-available/youtube2mp3 \
    /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## 🔒 Security Configuration

### Firewall Setup

```bash
# For Apache (port 80 and 443)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# For Nginx (same ports)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### SSL/HTTPS Setup (Recommended)

#### Using Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-apache  # For Apache
# sudo apt install -y certbot python3-certbot-nginx  # For Nginx

# Obtain certificate (replace with your domain)
sudo certbot --apache -d your-domain.com  # For Apache
# sudo certbot --nginx -d your-domain.com  # For Nginx

# Auto-renewal is configured automatically
# Test renewal:
sudo certbot renew --dry-run
```

#### Using Self-Signed Certificate (for internal NAS)

```bash
# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/youtube2mp3.key \
    -out /etc/ssl/certs/youtube2mp3.crt

# Set permissions
sudo chmod 600 /etc/ssl/private/youtube2mp3.key

# Edit your Apache/Nginx config to use these certificates
# Then reload the web server
```

### File Permissions

```bash
# Application directory
sudo chown -R www-data:www-data /opt/youtube2mp3
sudo chmod -R 755 /opt/youtube2mp3

# Downloads directory (needs write access)
sudo chmod 775 /opt/youtube2mp3/downloads

# Log directory
sudo chown -R www-data:www-data /var/log/youtube2mp3
sudo chmod 755 /var/log/youtube2mp3
```

## 📊 Monitoring & Logs

### View Application Logs

```bash
# Real-time application logs
sudo journalctl -u youtube2mp3 -f

# Last 100 lines
sudo journalctl -u youtube2mp3 -n 100

# Application-specific logs
sudo tail -f /var/log/youtube2mp3/access.log
sudo tail -f /var/log/youtube2mp3/error.log
```

### View Web Server Logs

```bash
# Apache
sudo tail -f /var/log/apache2/youtube2mp3_access.log
sudo tail -f /var/log/apache2/youtube2mp3_error.log

# Nginx
sudo tail -f /var/log/nginx/youtube2mp3_access.log
sudo tail -f /var/log/nginx/youtube2mp3_error.log
```

## 🔧 Maintenance

### Restart Application

```bash
sudo systemctl restart youtube2mp3
```

### Update Application

```bash
# Stop application
sudo systemctl stop youtube2mp3

# Update code (pull from git or copy new files)
cd /opt/youtube2mp3
sudo -u www-data git pull origin nas

# Update dependencies if needed
sudo -u www-data /opt/youtube2mp3/venv/bin/pip install -r requirements.txt --upgrade

# Start application
sudo systemctl start youtube2mp3
```

### Clean Up Old Downloads

```bash
# Delete files older than 7 days
find /opt/youtube2mp3/downloads -type f -mtime +7 -delete

# Or create a cron job (edit with: sudo crontab -e)
# Run daily at 3 AM:
# 0 3 * * * find /opt/youtube2mp3/downloads -type f -mtime +7 -delete
```

## 🐛 Troubleshooting

### Application Won't Start

```bash
# Check service status
sudo systemctl status youtube2mp3

# Check logs
sudo journalctl -u youtube2mp3 -n 50

# Common issues:
# 1. Port 8000 already in use - check with: sudo netstat -tlnp | grep 8000
# 2. Permission issues - verify www-data owns /opt/youtube2mp3
# 3. Missing dependencies - reinstall with pip
```

### FFmpeg Not Found

```bash
# Check FFmpeg installation
which ffmpeg
ffmpeg -version

# Install if missing
sudo apt install -y ffmpeg  # Debian/Ubuntu
sudo dnf install -y ffmpeg  # CentOS/Fedora

# Update .env with correct path
FFMPEG_LOCATION=/usr/bin
```

### WebSocket Connection Issues

```bash
# For Apache: Ensure mod_proxy_wstunnel is enabled
sudo a2enmod proxy_wstunnel
sudo systemctl restart apache2

# For Nginx: Check configuration has websocket support
sudo nginx -t
```

### Permission Denied on Downloads

```bash
# Fix ownership and permissions
sudo chown -R www-data:www-data /opt/youtube2mp3/downloads
sudo chmod 775 /opt/youtube2mp3/downloads
```

## 🌐 Access Configuration

### Local Network Access

Access via: `http://your-nas-ip/` or `http://your-nas-hostname.local/`

### Remote Access (Outside Network)

Options:
1. **Port Forwarding**: Forward port 80/443 on your router to NAS
2. **VPN**: Use VPN to access NAS network securely (recommended)
3. **Reverse Proxy**: Use services like Cloudflare Tunnel or ngrok

⚠️ **Security Warning**: If exposing to internet, always use HTTPS and consider additional authentication.

## 📈 Performance Tuning

### Increase Worker Processes (for multiple downloads)

Edit `/etc/systemd/system/youtube2mp3.service`:
```ini
# Change from:
# -w 1

# To (for 4 workers):
# -w 4
```

Note: With multiple workers, WebSocket/SocketIO might have issues. Stick with 1 worker for best compatibility.

### Adjust Timeout for Long Downloads

Edit systemd service file:
```ini
# Increase timeout to 10 minutes
--timeout 600
```

## 🎉 Post-Installation

After successful installation:
1. Access web interface at `http://your-nas-ip/`
2. Test a simple YouTube download
3. Check logs for any errors
4. Set up SSL certificate for HTTPS
5. Configure automatic cleanup of old downloads

## 📚 Additional Resources

- [Apache mod_wsgi Documentation](https://modwsgi.readthedocs.io/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Systemd Service Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
