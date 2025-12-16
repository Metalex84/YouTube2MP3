#!/bin/bash
# YouTube2MP3 NAS Installation Script
# This script automates the deployment of YouTube2MP3 on a NAS server

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/youtube2mp3"
LOG_DIR="/var/log/youtube2mp3"
APP_USER="www-data"
APP_GROUP="www-data"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}YouTube2MP3 NAS Installation Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo -e "${RED}Cannot detect OS. /etc/os-release not found.${NC}"
    exit 1
fi

echo -e "${GREEN}Detected OS: $OS $VERSION${NC}"
echo ""

# Function to install dependencies
install_dependencies() {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    
    case $OS in
        ubuntu|debian)
            apt update
            apt install -y python3 python3-pip python3-venv ffmpeg git curl
            ;;
        centos|rhel|fedora)
            dnf install -y epel-release || yum install -y epel-release
            dnf install -y python3 python3-pip ffmpeg git curl || \
            yum install -y python3 python3-pip ffmpeg git curl
            ;;
        *)
            echo -e "${RED}Unsupported OS: $OS${NC}"
            echo "Please install manually: python3, python3-pip, python3-venv, ffmpeg, git, curl"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Function to choose web server
choose_webserver() {
    echo ""
    echo -e "${YELLOW}Choose your web server:${NC}"
    echo "1) Apache (mod_wsgi + Gunicorn)"
    echo "2) Apache (Gunicorn reverse proxy - RECOMMENDED)"
    echo "3) Nginx (Gunicorn reverse proxy)"
    echo "4) Skip web server configuration (manual setup)"
    echo ""
    read -p "Enter choice [1-4]: " WEBSERVER_CHOICE
    
    case $WEBSERVER_CHOICE in
        1) WEBSERVER="apache-wsgi" ;;
        2) WEBSERVER="apache-gunicorn" ;;
        3) WEBSERVER="nginx" ;;
        4) WEBSERVER="none" ;;
        *) 
            echo -e "${RED}Invalid choice. Defaulting to Apache with Gunicorn.${NC}"
            WEBSERVER="apache-gunicorn"
            ;;
    esac
}

# Function to install web server
install_webserver() {
    if [ "$WEBSERVER" = "none" ]; then
        echo -e "${YELLOW}Skipping web server installation${NC}"
        return
    fi
    
    echo -e "${YELLOW}Installing web server...${NC}"
    
    case $WEBSERVER in
        apache-wsgi|apache-gunicorn)
            case $OS in
                ubuntu|debian)
                    apt install -y apache2 libapache2-mod-wsgi-py3
                    a2enmod proxy proxy_http proxy_wstunnel headers rewrite ssl
                    ;;
                centos|rhel|fedora)
                    dnf install -y httpd mod_wsgi mod_ssl || \
                    yum install -y httpd mod_wsgi mod_ssl
                    ;;
            esac
            ;;
        nginx)
            case $OS in
                ubuntu|debian)
                    apt install -y nginx
                    ;;
                centos|rhel|fedora)
                    dnf install -y nginx || yum install -y nginx
                    ;;
            esac
            ;;
    esac
    
    echo -e "${GREEN}✓ Web server installed${NC}"
}

# Function to create application directory
setup_app_directory() {
    echo -e "${YELLOW}Setting up application directory...${NC}"
    
    # Create directories
    mkdir -p "$APP_DIR"
    mkdir -p "$APP_DIR/downloads"
    mkdir -p "$LOG_DIR"
    
    # Copy application files
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    echo "Copying files from: $SCRIPT_DIR"
    
    cp -r "$SCRIPT_DIR"/* "$APP_DIR/"
    
    # Set ownership
    chown -R $APP_USER:$APP_GROUP "$APP_DIR"
    chown -R $APP_USER:$APP_GROUP "$LOG_DIR"
    
    # Set permissions
    chmod 755 "$APP_DIR"
    chmod 775 "$APP_DIR/downloads"
    chmod 755 "$LOG_DIR"
    
    echo -e "${GREEN}✓ Application directory created${NC}"
}

# Function to create virtual environment
setup_virtualenv() {
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    
    cd "$APP_DIR"
    
    # Create venv as app user
    sudo -u $APP_USER python3 -m venv venv
    
    # Install dependencies
    sudo -u $APP_USER "$APP_DIR/venv/bin/pip" install --upgrade pip
    sudo -u $APP_USER "$APP_DIR/venv/bin/pip" install -r requirements.txt
    
    echo -e "${GREEN}✓ Virtual environment created and dependencies installed${NC}"
}

# Function to configure environment variables
setup_env() {
    echo -e "${YELLOW}Configuring environment variables...${NC}"
    
    if [ ! -f "$APP_DIR/.env" ]; then
        if [ -f "$APP_DIR/.env.example" ]; then
            cp "$APP_DIR/.env.example" "$APP_DIR/.env"
        else
            # Create basic .env file
            cat > "$APP_DIR/.env" << EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DOWNLOAD_DIR=$APP_DIR/downloads
FFMPEG_LOCATION=/usr/bin
EOF
        fi
        
        chown $APP_USER:$APP_GROUP "$APP_DIR/.env"
        chmod 600 "$APP_DIR/.env"
        
        echo -e "${GREEN}✓ .env file created${NC}"
    else
        echo -e "${YELLOW}.env file already exists, skipping${NC}"
    fi
}

# Function to setup systemd service
setup_systemd() {
    echo -e "${YELLOW}Setting up systemd service...${NC}"
    
    cp "$APP_DIR/systemd/youtube2mp3.service" /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable service
    systemctl enable youtube2mp3
    
    # Start service
    systemctl start youtube2mp3
    
    # Check status
    sleep 2
    if systemctl is-active --quiet youtube2mp3; then
        echo -e "${GREEN}✓ Service is running${NC}"
    else
        echo -e "${RED}⚠ Service failed to start. Check logs: sudo journalctl -u youtube2mp3 -n 50${NC}"
    fi
}

# Function to configure web server
configure_webserver() {
    if [ "$WEBSERVER" = "none" ]; then
        return
    fi
    
    echo -e "${YELLOW}Configuring web server...${NC}"
    
    # Get hostname
    read -p "Enter your NAS hostname or IP (e.g., nas.local or 192.168.1.100): " NAS_HOSTNAME
    
    case $WEBSERVER in
        apache-wsgi)
            CONFIG_FILE="/etc/apache2/sites-available/youtube2mp3.conf"
            [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ] && \
                CONFIG_FILE="/etc/httpd/conf.d/youtube2mp3.conf"
            
            cp "$APP_DIR/apache-config/youtube2mp3.conf" "$CONFIG_FILE"
            sed -i "s/your-nas-hostname.local/$NAS_HOSTNAME/g" "$CONFIG_FILE"
            
            if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
                a2ensite youtube2mp3.conf
                systemctl reload apache2
            else
                systemctl restart httpd
            fi
            ;;
            
        apache-gunicorn)
            CONFIG_FILE="/etc/apache2/sites-available/youtube2mp3.conf"
            [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ] && \
                CONFIG_FILE="/etc/httpd/conf.d/youtube2mp3.conf"
            
            cp "$APP_DIR/apache-config/youtube2mp3-gunicorn.conf" "$CONFIG_FILE"
            sed -i "s/your-nas-hostname.local/$NAS_HOSTNAME/g" "$CONFIG_FILE"
            
            if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
                a2ensite youtube2mp3.conf
                systemctl reload apache2
            else
                systemctl restart httpd
            fi
            ;;
            
        nginx)
            CONFIG_FILE="/etc/nginx/sites-available/youtube2mp3"
            [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ] && \
                CONFIG_FILE="/etc/nginx/conf.d/youtube2mp3.conf"
            
            cp "$APP_DIR/nginx-config/youtube2mp3.conf" "$CONFIG_FILE"
            sed -i "s/your-nas-hostname.local/$NAS_HOSTNAME/g" "$CONFIG_FILE"
            
            if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
                ln -sf /etc/nginx/sites-available/youtube2mp3 /etc/nginx/sites-enabled/
            fi
            
            nginx -t && systemctl reload nginx
            ;;
    esac
    
    echo -e "${GREEN}✓ Web server configured${NC}"
}

# Function to configure firewall
configure_firewall() {
    echo -e "${YELLOW}Configuring firewall...${NC}"
    
    if command -v ufw &> /dev/null; then
        ufw allow 80/tcp
        ufw allow 443/tcp
        echo -e "${GREEN}✓ Firewall rules added (ufw)${NC}"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        echo -e "${GREEN}✓ Firewall rules added (firewalld)${NC}"
    else
        echo -e "${YELLOW}⚠ No firewall detected. Please manually allow ports 80 and 443${NC}"
    fi
}

# Main installation flow
main() {
    echo -e "${YELLOW}Starting installation...${NC}"
    echo ""
    
    # Install dependencies
    install_dependencies
    
    # Choose web server
    choose_webserver
    
    # Install web server
    install_webserver
    
    # Setup application
    setup_app_directory
    setup_virtualenv
    setup_env
    
    # Setup systemd service
    setup_systemd
    
    # Configure web server
    configure_webserver
    
    # Configure firewall
    configure_firewall
    
    # Final message
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Installation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${GREEN}Application is running at:${NC}"
    echo -e "  http://$NAS_HOSTNAME/"
    echo ""
    echo -e "${YELLOW}Useful commands:${NC}"
    echo "  View logs:        sudo journalctl -u youtube2mp3 -f"
    echo "  Restart service:  sudo systemctl restart youtube2mp3"
    echo "  Check status:     sudo systemctl status youtube2mp3"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Test the web interface"
    echo "  2. Configure SSL/HTTPS (see NAS-DEPLOYMENT.md)"
    echo "  3. Set up automatic cleanup of old downloads"
    echo ""
}

# Run main installation
main
