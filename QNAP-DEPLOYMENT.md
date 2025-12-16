# QNAP TS-231P Deployment Guide

## Architecture Issue
Your QNAP TS-231P uses an **ARM CPU** (AnnapurnaLabs Alpine AL-212), but the Docker image built on your Windows machine is for **x86/amd64** architecture. Container Station will reject it due to architecture mismatch.

## Recommended Deployment Method

### Option 1: Build Directly on QNAP (Recommended)

This is the most reliable method for ARM-based QNAP NAS.

#### Step 1: Transfer Project Files to QNAP
1. Create a shared folder on your QNAP (e.g., `/share/Container/y2m`)
2. Transfer these files to your QNAP:
   - `Dockerfile`
   - `requirements.txt`
   - `app.py`
   - `descargar_audio.py`
   - `templates/` (entire folder)
   - `static/` (entire folder)
   - `docker-compose-nas.yml`

#### Step 2: SSH into QNAP
```bash
ssh admin@<your-nas-ip>
```

#### Step 3: Navigate to Project Directory
```bash
cd /share/Container/y2m
```

#### Step 4: Build the Image on QNAP
```bash
docker build -t y2m-downloader:latest .
```

This will build the image natively for ARM architecture.

#### Step 5: Create Required Directories
```bash
mkdir -p /share/Download/y2m-downloads
mkdir -p /share/Container/y2m-logs
```

#### Step 6: Deploy Using Docker Compose
```bash
docker-compose -f docker-compose-nas.yml up -d
```

### Option 2: Use Docker Hub (Alternative)

If you want to build on your Windows machine and deploy on QNAP:

#### On Windows Machine:
```powershell
# Tag the image for Docker Hub
docker tag y2m-downloader:latest <your-dockerhub-username>/y2m-downloader:latest

# Push to Docker Hub
docker push <your-dockerhub-username>/y2m-downloader:latest
```

#### On QNAP (via SSH):
```bash
# Pull the image
docker pull <your-dockerhub-username>/y2m-downloader:latest

# Tag it locally
docker tag <your-dockerhub-username>/y2m-downloader:latest y2m-downloader:latest

# Deploy with docker-compose
docker-compose -f docker-compose-nas.yml up -d
```

**Note**: This will still fail if the image is amd64. You need to build a multi-arch image or build directly on QNAP.

### Option 3: Container Station GUI

Once you have the image built on QNAP:

1. Open **Container Station**
2. Go to **Create** → **Create Application**
3. Paste the content of `docker-compose-nas.yml`
4. Adjust volume paths if needed (based on your QNAP folder structure)
5. Update `SECRET_KEY` environment variable
6. Click **Create**

## Configuration

### Volume Paths
Update these paths in `docker-compose-nas.yml` based on your QNAP structure:
- Downloads: `/share/Download/y2m-downloads` or `/share/Public/y2m-downloads`
- Logs: `/share/Container/y2m-logs`

To find your share paths, SSH into QNAP and run:
```bash
ls -la /share/
```

### Port Configuration
The application runs on port **5000**. Access it at:
```
http://<qnap-nas-ip>:5000
```

If port 5000 is in use, change it in `docker-compose-nas.yml`:
```yaml
ports:
  - "8080:5000"  # Maps host port 8080 to container port 5000
```

### Secret Key
Generate a secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Update the `SECRET_KEY` in `docker-compose-nas.yml`.

## Resource Limits

The TS-231P has limited resources (ARM dual-core CPU, typically 1GB RAM). The docker-compose file is configured with:
- CPU limit: 1 core max
- Memory limit: 512MB max
- Memory reservation: 256MB

Adjust these if needed based on your usage.

## Troubleshooting

### Check Container Logs
```bash
docker logs y2m-downloader
```

### Check Container Status
```bash
docker ps -a
```

### Restart Container
```bash
docker restart y2m-downloader
```

### Rebuild Image
```bash
docker-compose -f docker-compose-nas.yml down
docker rmi y2m-downloader:latest
docker build -t y2m-downloader:latest .
docker-compose -f docker-compose-nas.yml up -d
```

## Performance Notes

- The TS-231P has an ARM CPU, which may be slower for video processing
- ffmpeg will work but may take longer on ARM
- Consider limiting concurrent downloads to avoid overloading the NAS
- Monitor CPU and memory usage in QNAP's Resource Monitor

## Security Recommendations

1. Don't expose port 5000 directly to the internet
2. Use QNAP's reverse proxy or VPN for external access
3. Keep the Docker image and Container Station updated
4. Use strong SECRET_KEY value
5. Regularly backup your download directory
