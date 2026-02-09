# AO3 Year in Review

A web application that retrieves and analyzes your AO3 (Archive of Our Own) reading history, generating beautiful statistics and visualizations.

## Features

- 📚 Retrieve complete reading history from your AO3 account
- 📊 Generate visual statistics including:
  - Top ships/relationships
  - Most read tags
  - Favorite fandoms
  - Overall reading stats (total fics, word count, longest work)
- 🎯 Filter results by year
- 🔒 Privacy-focused: credentials are only sent to AO3, never stored
- ⚡ Real-time progress updates during scraping

## Project Structure

```
AO3YearInReview/
├── app.py                 # Flask backend server
├── ao3_scraper.py         # Web scraping logic
├── image_generator.py     # Statistics visualization generator
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version specification
├── public/
│   └── index.html        # Frontend interface
└── README.md             # This file
```

## Deployment Options

### Option 1: Deploy with Portfolio (Recommended for your use case)

Since this is integrated into your portfolio, you can deploy the entire portfolio directory to your server.

#### Requirements:
- Python 3.11 or higher
- pip (Python package manager)
- A web server (Apache, Nginx, etc.)

#### Steps:

1. **Upload your entire portfolio to your server**
   ```bash
   # Via SCP, SFTP, or your hosting provider's file manager
   scp -r /path/to/portfolio user@your-domain.com:/var/www/html/
   ```

2. **Install Python dependencies for the AO3 app**
   ```bash
   cd /var/www/html/AO3YearInReview
   pip install -r requirements.txt
   ```

3. **Set up the Flask app to run as a service**

   Create a systemd service file at `/etc/systemd/system/ao3-app.service`:
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

4. **Start the service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable ao3-app
   sudo systemctl start ao3-app
   ```

5. **Configure your web server as a reverse proxy**

   **For Nginx**, add this to your site configuration:
   ```nginx
   location /AO3YearInReview/ {
       proxy_pass http://localhost:3000/;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection 'upgrade';
       proxy_set_header Host $host;
       proxy_cache_bypass $http_upgrade;
   }
   ```

   **For Apache**, enable required modules and add:
   ```apache
   ProxyPreserveHost On
   ProxyPass /AO3YearInReview/ http://localhost:3000/
   ProxyPassReverse /AO3YearInReview/ http://localhost:3000/
   ```

6. **Restart your web server**
   ```bash
   # For Nginx
   sudo systemctl restart nginx

   # For Apache
   sudo systemctl restart apache2
   ```

### Option 2: Standalone Deployment

You can also run this as a standalone application:

```bash
cd AO3YearInReview
pip install -r requirements.txt
python app.py
```

The app will be available at `http://localhost:3000`

## Usage

1. Navigate to the AO3 Year in Review app on your website
2. Enter your AO3 username and password
3. Optionally select a specific year to filter results
4. Click "Start Scraping" and watch the progress
5. Once complete, view your statistics and download the visualizations

## Technical Details

### Backend (Python/Flask)
- **Flask** - Web framework
- **BeautifulSoup4** - HTML parsing
- **Requests** - HTTP requests with retry logic
- **Pillow** - Image generation for statistics

### Features
- Rate limiting to respect AO3's servers
- Exponential backoff for failed requests
- CAPTCHA and bot detection handling
- Server-sent events for real-time progress updates

### Security
- Credentials are only sent directly to AO3
- No data is stored on the server
- Session cookies are used only for the duration of scraping

## Troubleshooting

### Port Already in Use
If port 3000 is already in use, you can change it by setting the `PORT` environment variable:
```bash
export PORT=5000
python app.py
```

### Rate Limiting
If you encounter rate limiting from AO3:
- The scraper automatically implements delays between requests
- Wait a few minutes before trying again
- Consider using the year filter to reduce the number of pages scraped

### Missing Fonts for Image Generation
The app tries to find system fonts automatically. If images don't render text properly:
- Linux: Install `fonts-dejavu` or `fonts-liberation`
- macOS: Should work out of the box
- Windows: Ensure Arial or another TrueType font is installed

## License

This project is for personal use. Please respect AO3's Terms of Service and use responsibly.

## Credits

Built by Alice Henry
GitHub: https://github.com/AliceHenrySCT/AO3HistoryRetriever
