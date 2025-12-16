# YouTube2MP3 - Docker Web Interface 🐳

This is the Dockerized version of the YouTube2MP3 Web Application, allowing you to run the complete web interface in a container without needing to install Python, FFmpeg, or any dependencies on your host system.

## 🚀 Quick Start

### Prerequisites
- Docker installed on your system
- Docker Compose (usually included with Docker Desktop)

### 1. Build and Start the Container

```bash
docker-compose up -d
```

This single command will:
- Build the Docker image with all dependencies
- Start the web server on port 5000
- Mount volumes for persistent downloads and logs

### 2. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

### 3. Stop the Container

```bash
docker-compose down
```

## 📋 Features

- ✅ **Complete Web Interface** - Modern, responsive UI
- ✅ **Real-time Progress** - WebSocket updates for downloads
- ✅ **Batch Downloads** - Process multiple URLs or CSV files
- ✅ **Persistent Storage** - Downloads and logs persist between container restarts
- ✅ **No Local Dependencies** - Everything runs in the container
- ✅ **Easy Updates** - Simply rebuild the image

## 🔧 Docker Commands

### Build the Image
```bash
docker-compose build
```

### Start in Background (Detached Mode)
```bash
docker-compose up -d
```

### Start with Console Output
```bash
docker-compose up
```

### Stop the Container
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

### Restart the Container
```bash
docker-compose restart
```

### Rebuild and Restart
```bash
docker-compose up -d --build
```

## 📁 Directory Structure

When running with Docker, the following directories are mounted:

```
YouTube2MP3/
├── downloads/          # Downloaded MP3 files (persistent)
├── logs/              # Application logs (persistent)
├── Dockerfile         # Container configuration
└── docker-compose.yml # Docker Compose configuration
```

## 🌐 Using the Web Interface

### Single Download
1. Navigate to **"📎 Descarga Simple"** tab
2. Paste a YouTube URL
3. Click **"🚀 Descargar"**
4. Watch real-time progress
5. Download the MP3 when complete

### Batch Download
1. Navigate to **"📋 Descarga en Lote"** tab
2. Either:
   - Upload a CSV file with URLs, OR
   - Paste URLs (one per line) in the text area
3. Click **"🚀 Procesar"**
4. Monitor all downloads in real-time
5. Download all as ZIP or individually

## 🔌 API Access

The REST API is accessible at `http://localhost:5000/api/`

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Start Download
```bash
curl -X POST http://localhost:5000/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

### List Downloads
```bash
curl http://localhost:5000/api/downloads
```

See [README-Web.md](README-Web.md) for complete API documentation.

## ⚙️ Configuration

### Environment Variables

Edit `docker-compose.yml` to customize:

```yaml
environment:
  - DOWNLOAD_DIR=/app/downloads
  - LOGS_DIR=/app/logs
  - PYTHONUNBUFFERED=1
```

### Port Configuration

To use a different port, edit `docker-compose.yml`:

```yaml
ports:
  - "8080:5000"  # Access on port 8080 instead
```

### Resource Limits

Adjust memory and CPU limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 2G      # Increase memory
      cpus: '4.0'     # Use 4 CPUs
```

## 🔍 Troubleshooting

### Container Won't Start

Check logs:
```bash
docker-compose logs
```

### Port Already in Use

Either:
- Stop the application using port 5000
- Change the port in `docker-compose.yml`

### Downloads Not Persisting

Ensure the `downloads` directory has correct permissions:
```bash
# Linux/Mac
chmod -R 777 downloads/

# Windows (PowerShell as Admin)
icacls downloads /grant Everyone:F /T
```

### FFmpeg Errors

FFmpeg is included in the Docker image. If issues occur:
1. Rebuild the image: `docker-compose build --no-cache`
2. Check logs: `docker-compose logs`

### Can't Access from Other Devices

The server binds to `0.0.0.0` inside the container, but you need to:
1. Ensure your firewall allows port 5000
2. Access using your machine's IP: `http://192.168.1.x:5000`

### WebSocket Not Connecting

1. Check browser console (F12) for errors
2. Ensure no proxy is blocking WebSocket connections
3. Try accessing via `http://localhost:5000` instead of `127.0.0.1`

## 🐳 Advanced Docker Usage

### Using Docker Without Compose

Build the image:
```bash
docker build -t youtube2mp3-web .
```

Run the container:
```bash
docker run -d \
  --name youtube2mp3-web \
  -p 5000:5000 \
  -v "$(pwd)/downloads:/app/downloads" \
  -v "$(pwd)/logs:/app/logs" \
  youtube2mp3-web
```

Stop and remove:
```bash
docker stop youtube2mp3-web
docker rm youtube2mp3-web
```

### View Container Details
```bash
docker ps
docker inspect youtube2mp3-web
```

### Execute Commands Inside Container
```bash
docker exec -it youtube2mp3-web bash
```

### Copy Files From Container
```bash
docker cp youtube2mp3-web:/app/downloads/song.mp3 ./
```

## 🔐 Security Notes

### For Production Use

If deploying to production:

1. **Change the SECRET_KEY** in `app.py`
2. **Use HTTPS** with a reverse proxy (nginx, Traefik)
3. **Add Authentication** if publicly accessible
4. **Implement Rate Limiting**
5. **Use Environment Variables** for secrets (not hardcoded)
6. **Regular Updates** to dependencies

Example nginx reverse proxy config:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring

### View Resource Usage
```bash
docker stats youtube2mp3-web
```

### Check Disk Space
```bash
docker system df
```

### Clean Up Old Images
```bash
docker system prune -a
```

## 🔄 Updates and Maintenance

### Update the Application

1. Pull latest code (if from git):
   ```bash
   git pull origin web
   ```

2. Rebuild and restart:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### Backup Downloads

Downloads are stored in `./downloads/` on your host system and persist between container restarts.

To backup:
```bash
# Linux/Mac
tar -czf youtube2mp3-backup-$(date +%Y%m%d).tar.gz downloads/

# Windows (PowerShell)
Compress-Archive -Path downloads -DestinationPath "youtube2mp3-backup-$(Get-Date -Format 'yyyyMMdd').zip"
```

## 🌟 Advantages of Docker Version

- ✅ **No Python Installation** - Everything is containerized
- ✅ **No FFmpeg Setup** - Pre-installed in the image
- ✅ **Consistent Environment** - Works the same everywhere
- ✅ **Easy Updates** - Just rebuild the image
- ✅ **Isolation** - Doesn't affect your host system
- ✅ **Portability** - Run on any system with Docker
- ✅ **Easy Deployment** - One command to start

## 📖 Additional Resources

- [Web Interface Documentation](README-Web.md)
- [Main Project README](README.md)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 📄 License

This project is open source. Use responsibly and respect YouTube's Terms of Service.

---

**Enjoy converting your favorite YouTube videos to MP3 with Docker! 🎵**
