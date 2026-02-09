# Portfolio Deployment Guide

This guide will help you deploy your portfolio website with the integrated AO3 Year in Review application to your personal domain.

## Quick Overview

Your portfolio is a static HTML/CSS/JS site with one Python Flask application (AO3 Year in Review) that requires a backend server.

## Structure

```
portfolio/
├── index.html              # Main portfolio page
├── style.css               # Portfolio styles
├── Images/                 # Portfolio images
├── MemGame/               # Memory game project (static)
├── AO3YearInReview/       # AO3 app (requires Python backend)
│   ├── app.py
│   ├── ao3_scraper.py
│   ├── image_generator.py
│   ├── requirements.txt
│   ├── public/
│   └── README.md
└── DEPLOYMENT.md          # This file
```

## Prerequisites

- A server with Python 3.11+ installed
- Web server (Nginx or Apache)
- SSH access to your server
- Your domain configured to point to your server

## Deployment Steps

### 1. Upload Files to Server

Upload your entire portfolio directory to your web server:

```bash
# Using SCP
scp -r portfolio/ user@your-domain.com:/var/www/html/

# Or use your hosting provider's file manager or FTP client
```

### 2. Install Python Dependencies

SSH into your server and install the required Python packages:

```bash
ssh user@your-domain.com
cd /var/www/html/AO3YearInReview
pip3 install -r requirements.txt
```

### 3. Configure the Flask App

Create a systemd service to run the Flask app:

```bash
sudo nano /etc/systemd/system/ao3-app.service
```

Add this configuration:

```ini
[Unit]
Description=AO3 Year in Review Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/html/AO3YearInReview
Environment="PORT=3000"
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ao3-app
sudo systemctl start ao3-app
sudo systemctl status ao3-app  # Verify it's running
```

### 4. Configure Web Server

#### For Nginx:

Edit your site configuration:

```bash
sudo nano /etc/nginx/sites-available/your-domain
```

Add this location block inside the `server` block:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/html;
    index index.html;

    # Serve static portfolio files
    location / {
        try_files $uri $uri/ =404;
    }

    # Proxy AO3 app to Flask backend
    location /AO3YearInReview/ {
        proxy_pass http://localhost:3000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

Test and reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

#### For Apache:

Enable required modules:

```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
```

Edit your site configuration:

```bash
sudo nano /etc/apache2/sites-available/your-domain.conf
```

Add:

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    DocumentRoot /var/www/html

    <Directory /var/www/html>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    # Proxy for AO3 app
    ProxyPreserveHost On
    ProxyPass /AO3YearInReview/ http://localhost:3000/
    ProxyPassReverse /AO3YearInReview/ http://localhost:3000/
</VirtualHost>
```

Restart Apache:

```bash
sudo systemctl restart apache2
```

### 5. Set Up HTTPS (Recommended)

Use Let's Encrypt for free SSL certificates:

```bash
# For Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx  # For Nginx
# OR
sudo apt install certbot python3-certbot-apache  # For Apache

# Get certificate
sudo certbot --nginx -d your-domain.com  # For Nginx
# OR
sudo certbot --apache -d your-domain.com  # For Apache
```

## Verify Deployment

1. **Portfolio Homepage**: Visit `https://your-domain.com`
   - Should display your portfolio

2. **AO3 App**: Click the "Live Demo" button on the AO3 Year in Review project card
   - Should open the AO3 app interface
   - Try the health check: `https://your-domain.com/AO3YearInReview/api/health`

## Troubleshooting

### Flask App Won't Start

Check the service logs:
```bash
sudo journalctl -u ao3-app -f
```

### Port 3000 Already in Use

Change the port in the service file:
```bash
sudo nano /etc/systemd/system/ao3-app.service
# Change Environment="PORT=3000" to another port like 5000
sudo systemctl daemon-reload
sudo systemctl restart ao3-app
```

### Permission Issues

Ensure correct ownership:
```bash
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html
```

### Web Server Not Proxying Correctly

Check logs:
```bash
# Nginx
sudo tail -f /var/log/nginx/error.log

# Apache
sudo tail -f /var/log/apache2/error.log
```

## Maintenance

### Updating the AO3 App

```bash
cd /var/www/html/AO3YearInReview
# Update files
sudo systemctl restart ao3-app
```

### Updating the Portfolio

Simply upload new files and refresh your browser. No restart needed for static content.

## Alternative: Simple Local Testing

Before deploying, you can test locally:

```bash
cd AO3YearInReview
pip3 install -r requirements.txt
python3 app.py
```

Visit `http://localhost:3000` to test the AO3 app.

For the full portfolio, use a simple HTTP server:

```bash
cd portfolio
python3 -m http.server 8000
```

Visit `http://localhost:8000` to see the portfolio (but the AO3 app link won't work without the backend running).

## Need Help?

- Check the AO3YearInReview/README.md for app-specific details
- Review your server's error logs
- Ensure Python 3.11+ is installed: `python3 --version`
- Verify the service is running: `sudo systemctl status ao3-app`
