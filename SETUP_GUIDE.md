# Font Precision Recognizer

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Google Generative AI API key (optional but recommended)

### Installation & Setup

#### Option 1: Direct Installation (Recommended for beginners)

```bash
# Clone the repository
git clone https://github.com/xingyingmei/font-precision-recognizer.git
cd font-precision-recognizer

# Run the setup script
chmod +x start.sh
./start.sh
```

The script will:
- ✓ Create a Python virtual environment
- ✓ Install all dependencies
- ✓ Initialize the database
- ✓ Start the server automatically

#### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run the application
python app.py
```

#### Option 3: Docker (Recommended for production)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t font-recognizer .
docker run -p 5000:5000 -e GOOGLE_API_KEY=your_key font-recognizer
```

### Configuration

Edit `.env` file and add your settings:

```env
# Required: Google Generative AI API Key
GOOGLE_API_KEY=your_api_key_here

# Optional: Flask configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key

# Server settings
HOST=localhost
PORT=5000
```

**Get Google API Key:**
1. Visit https://ai.google.dev/tutorials/setup
2. Create a new API key
3. Add it to your `.env` file

## 📖 Usage Guide

### Web Interface

Once the server is running, open your browser:

```
http://localhost:5000
```

#### 1. Recognize Fonts from Image

1. Go to the **"Recognize"** tab
2. **Upload an image** or **paste from clipboard** (Ctrl+V)
3. Alternatively, click **📸 Capture Screenshot** to capture screen area
4. Click **"🔍 Recognize Fonts"** button
5. View results with confidence levels and download links

**Supported formats:**
- PNG, JPG, JPEG, GIF, BMP, WEBP, TIFF, SVG
- Maximum file size: 10MB

#### 2. Search for Fonts

1. Go to the **"Search"** tab
2. Enter a **font name** or description
3. (Optional) Filter by:
   - Font type (Serif, Sans-Serif, Script, etc.)
   - License (Free, Commercial, Subscription)
4. Click **"Search"** button
5. Get direct links to 18+ font repositories

### API Usage

#### Recognize Font from Image

```bash
curl -X POST http://localhost:5000/api/recognize-font \
  -F "image=@screenshot.png"
```

**Response:**
```json
{
  "status": "success",
  "fonts": [
    {
      "name": "Montserrat Bold",
      "type": "Sans-Serif",
      "confidence": 0.95,
      "sources": [
        {
          "name": "Google Fonts",
          "url": "https://fonts.google.com/specimen/Montserrat",
          "availability": "free"
        }
      ]
    }
  ]
}
```

#### Search Font by Name

```bash
curl "http://localhost:5000/api/search-font?query=Helvetica&license=free"
```

#### Get All Font Sources

```bash
curl http://localhost:5000/api/sources
```

#### Health Check

```bash
curl http://localhost:5000/api/health
```

## 🎯 Key Features

### ✨ Image Recognition
- **AI-Powered**: Uses Google Generative AI for accurate font identification
- **Screenshot Support**: Capture screen directly from browser
- **Clipboard Paste**: Paste images directly (Ctrl+V)
- **Batch Processing**: Process multiple images
- **Confidence Scoring**: Know how sure the AI is about each match

### 🌐 Multi-Source Integration
Access 18+ premium font repositories:
- **Free**: Google Fonts, DaFont, Font Squirrel, 1001 Fonts, Font Space
- **Commercial**: MyFonts, Adobe Fonts, YouWorkForThem, Global Fonts
- **Subscription**: Creative Fabrica
- **Mixed**: Font Park, FontHub, Elements Envato

### 🔍 Smart Search
- Instant results from local database
- Direct links to all sources
- Filter by font type and license
- Bulk search for multiple fonts

### 🤖 Auto-Discovery
- Automatic web scraping of new fonts
- Weekly database updates
- New source detection

## 🏗️ Project Structure

```
font-precision-recognizer/
├── app.py                      # Main Flask application
├── start.sh                    # Startup script
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
│
├── src/
│   ├── font_recognizer.py     # AI-powered recognition
│   ├── font_searcher.py       # Multi-source search
│   ├── web_scraper.py         # Auto font discovery
│   └── database.py            # Database management
│
├── templates/                  # HTML templates
│   ├── index.html             # Home page
│   ├── recognize.html         # Recognition page
│   └── search.html            # Search page
│
├── static/
│   ├── css/style.css          # Styling
│   └── js/
│       ├── main.js            # Utilities
│       └── recognition.js     # Recognition logic
│
└── data/
    └── font_database.json     # Local font cache
```

## 🔧 Advanced Configuration

### Enable Automatic Scraping

Edit `app.py` to schedule weekly database updates:

```python
from src.web_scraper import WebScraper

scraper = WebScraper()
scraper.schedule_scraping(interval_seconds=604800)  # Weekly
```

### Custom Font Sources

Add new font sources in `src/font_searcher.py`:

```python
'My Font Site': {
    'url': 'https://myfonts.com',
    'type': 'free',
    'search_pattern': 'https://myfonts.com/search?q={query}',
    'priority': 2
}
```

### Rate Limiting

Set in `.env`:

```env
RATE_LIMIT=100  # requests per hour
```

## 📊 Supported Font Types

- Serif
- Sans-Serif
- Script
- Display
- Monospace
- Handwriting
- Decorative
- Geometric

## 🐛 Troubleshooting

### "No API key found"
**Solution**: Add `GOOGLE_API_KEY` to `.env` file

### "Image too large"
**Solution**: Compress image to under 10MB or use screenshot feature

### "Font not recognized"
**Solution**: Try different image with clearer text, or use search feature

### "Connection refused"
**Solution**: Make sure the server is running (`python app.py`)

### Port 5000 already in use
**Solution**: Change port in `.env`:
```env
PORT=5001
```

## 📈 Performance Tips

1. **Use Screenshot**: More accurate than camera photos
2. **Clear Text**: Ensure text is clearly visible
3. **High Contrast**: Dark text on light background works best
4. **Optimize Images**: Larger images = slower processing
5. **Cache Results**: Save recognized fonts locally

## 🔐 Security Notes

- API keys stored in `.env` (never commit to git)
- File uploads validated before processing
- XSS protection on all user inputs
- CORS enabled for trusted origins only
- Rate limiting prevents API abuse

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 💬 Support & Issues

- **Report Bugs**: Open GitHub issue with details
- **Feature Requests**: Describe use case and expected behavior
- **Questions**: Check documentation first, then open discussion

## 🎓 Learning Resources

- [Google Generative AI Docs](https://ai.google.dev/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Font Terminology](https://www.adobe.com/creativecloud/design/discover/typography-basics.html)

## 🚀 What's Next?

- [ ] Browser extension
- [ ] Mobile app (iOS/Android)
- [ ] Advanced font pairing suggestions
- [ ] Font trend analytics
- [ ] Community font database
- [ ] Real-time collaboration

## 📞 Contact

- **Author**: Font Precision Team
- **Email**: support@fontrecognizer.dev
- **GitHub**: https://github.com/xingyingmei/font-precision-recognizer

---

**Last Updated**: 2026-09-16  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
