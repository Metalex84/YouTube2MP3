# Docker Quick Start Guide 🚀

Get the YouTube2MP3 web interface running in Docker in under 5 minutes!

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

## Step 1: Build and Start

Open a terminal in the project directory and run:

```bash
docker-compose up -d
```

That's it! The application is now running.

## Step 2: Access the Web Interface

Open your browser and go to:

```
http://localhost:5000
```

You should see the YouTube2MP3 web interface!

## Step 3: Start Converting

1. **Single Download**: Paste a YouTube URL and click Download
2. **Batch Download**: Upload a CSV file or paste multiple URLs

Your downloaded MP3 files will appear in the `downloads/` folder.

## Managing the Container

### View logs
```bash
docker-compose logs -f
```

### Stop the container
```bash
docker-compose down
```

### Restart the container
```bash
docker-compose restart
```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

## Troubleshooting

### Port 5000 already in use?

Edit `docker-compose.yml` and change:
```yaml
ports:
  - "8080:5000"  # Now accessible on port 8080
```

### Can't see downloads?

Downloads are saved to `./downloads/` in your project directory. Check:
```bash
ls downloads/
```

### Check container status
```bash
docker ps
```

### View detailed logs
```bash
docker-compose logs youtube-mp3-web
```

## What's Inside?

The Docker container includes:
- Python 3.11
- FFmpeg (for audio conversion)
- Flask web server
- yt-dlp (YouTube downloader)
- All required Python packages

## Next Steps

For more detailed information, see:
- [README-Docker-Web.md](README-Docker-Web.md) - Complete Docker documentation
- [README-Web.md](README-Web.md) - Web interface and API documentation
- [README.md](README.md) - Main project documentation

---

**Happy downloading! 🎵**
