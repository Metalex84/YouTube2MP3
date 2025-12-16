# Deployment Guide for YouTube2MP3

This guide will walk you through deploying the YouTube2MP3 application to Render.com.

## Why Render?

Render is the recommended platform for this application because:
- ✅ **WebSocket Support**: Full support for Flask-SocketIO and real-time updates
- ✅ **Long-running Processes**: Supports video downloads that take time
- ✅ **FFmpeg Support**: Easy to install FFmpeg via native packages
- ✅ **Persistent Connections**: Maintains WebSocket connections for progress updates
- ✅ **Simple Configuration**: Blueprint files for infrastructure-as-code

## Prerequisites

1. A [Render account](https://render.com) (free tier available)
2. Your YouTube2MP3 code in a Git repository (GitHub, GitLab, or Bitbucket)
3. Basic familiarity with Git

## Deployment Steps

### Option 1: Deploy via render.yaml (Recommended)

This method uses the included `render.yaml` blueprint file for automatic configuration.

1. **Push your code to a Git repository** (if not already done)
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Go to Render Dashboard**
   - Visit [https://dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Blueprint"

3. **Connect your repository**
   - Select your Git provider (GitHub, GitLab, or Bitbucket)
   - Authorize Render to access your repositories
   - Select the YouTube2MP3 repository

4. **Deploy the blueprint**
   - Render will automatically detect the `render.yaml` file
   - Review the service configuration
   - Click "Apply" to create the service

5. **Install FFmpeg**
   - After the service is created, go to your service settings
   - Under "Environment", click "Add Environment Variable"
   - Add: `APT_PACKAGES` = `ffmpeg`
   - Click "Save Changes" - this will trigger a rebuild with FFmpeg

6. **Wait for deployment**
   - The build and deployment process takes 3-5 minutes
   - Watch the logs for any errors
   - Your app will be live at `https://your-app-name.onrender.com`

### Option 2: Manual Deployment

If you prefer manual configuration:

1. **Create a new Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your repository

2. **Configure the service**
   - **Name**: `youtube2mp3` (or your preferred name)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app`
   - **Instance Type**: Choose your plan (Free tier works for testing)

3. **Add Environment Variables**
   Click "Advanced" and add these environment variables:
   
   | Key | Value | Description |
   |-----|-------|-------------|
   | `SECRET_KEY` | (Generate a secure key) | Required for Flask sessions |
   | `PYTHON_VERSION` | `3.11.9` | Python version to use |
   | `DOWNLOAD_DIR` | `/tmp/downloads` | Temporary storage for downloads |
   | `LOGS_DIR` | `/tmp/logs` | Temporary storage for logs |
   | `APT_PACKAGES` | `ffmpeg` | Install FFmpeg system package |

   **Generate a SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for the build and deployment to complete
   - Your app will be live at your Render URL

## Post-Deployment Configuration

### Custom Domain (Optional)

1. Go to your service settings in Render
2. Click "Custom Domain"
3. Follow the instructions to add your domain
4. Update your DNS records as instructed

### Monitoring and Logs

- **View Logs**: Click on your service → "Logs" tab
- **Metrics**: View CPU, memory usage, and request metrics in the dashboard
- **Alerts**: Set up alerts for service failures or high resource usage

## Important Considerations

### 🚨 Ephemeral File Storage

Render uses **ephemeral storage**, meaning:
- Files stored on the filesystem (like downloaded MP3s) are temporary
- Files are deleted when the service restarts or redeploys
- Users should download files immediately after conversion

**For Production**: Consider using cloud storage:
- AWS S3
- Cloudinary
- Google Cloud Storage
- Upload files to storage and provide download links

### 💰 Free Tier Limitations

Render's free tier includes:
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes 30+ seconds (cold start)
- 750 hours/month of runtime (enough for one service)

**For better performance**: Upgrade to a paid plan ($7+/month)

### 🔒 Security Recommendations

1. **Always set a strong SECRET_KEY** in production
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** (automatic on Render)
4. **Consider rate limiting** for the download API
5. **Add authentication** if the app will be public

### 📊 Performance Tips

1. **Monitor resource usage** in Render dashboard
2. **Upgrade instance type** if experiencing slowdowns
3. **Consider background workers** for heavy download loads
4. **Implement request queuing** for high traffic

## Troubleshooting

### Service won't start

**Check the logs for errors:**
- Go to service → "Logs" tab
- Look for Python errors or missing dependencies

**Common issues:**
- Missing environment variables (especially `SECRET_KEY`)
- FFmpeg not installed (add `APT_PACKAGES=ffmpeg`)
- Port binding issues (should use `$PORT` automatically)

### FFmpeg not found

**Solution:**
1. Add environment variable: `APT_PACKAGES` = `ffmpeg`
2. Redeploy the service
3. Check logs to confirm FFmpeg installation

### WebSocket connection fails

**Causes:**
- Service is asleep (free tier) - wait for it to wake up
- CORS issues - check allowed origins in `app.py`
- Network/firewall blocking WebSocket connections

**Solutions:**
- Upgrade to a paid plan to avoid cold starts
- Check browser console for specific WebSocket errors
- Ensure the frontend is connecting to the correct URL

### Downloads failing

**Possible causes:**
- YouTube URL restrictions or geoblocking
- yt-dlp needs updating
- Network timeout issues

**Solutions:**
- Update yt-dlp: Add to requirements.txt: `yt-dlp>=2024.1.1`
- Increase timeout settings in `app.py`
- Check Render logs for specific yt-dlp errors

### Out of memory errors

**Solutions:**
- Upgrade to a larger instance type
- Limit concurrent downloads
- Implement download queuing system

## Updating Your Deployment

To update your deployed application:

1. **Push changes to your Git repository**
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```

2. **Automatic deployment**
   - Render automatically deploys when you push to your main branch
   - Watch the deployment logs in the Render dashboard

3. **Manual deployment** (if auto-deploy is disabled)
   - Go to your service in Render
   - Click "Manual Deploy" → "Deploy latest commit"

## Alternative Platforms

While Render is recommended, you can also deploy to:

### Railway
- Similar to Render with excellent developer experience
- Good WebSocket support
- Simple pricing model

### Heroku
- Requires buildpack for FFmpeg
- Add: `heroku/python` and `https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git`
- Uses same `Procfile` configuration

### DigitalOcean App Platform
- Supports Docker deployments
- Use the included `Dockerfile` and `docker-compose.yml`
- More control but requires more configuration

### Fly.io
- Excellent for global deployment
- Use `Dockerfile` for deployment
- Good performance and pricing

## Getting Help

- **Render Documentation**: [https://render.com/docs](https://render.com/docs)
- **Render Community**: [https://community.render.com](https://community.render.com)
- **Project Issues**: Create an issue in the GitHub repository

## Next Steps

After deployment:
1. Test the application thoroughly
2. Set up monitoring and alerts
3. Configure custom domain (optional)
4. Implement cloud storage for production use
5. Add authentication if needed
6. Set up CI/CD pipelines for automated testing

---

**Need help?** Check the troubleshooting section or create an issue in the repository.
