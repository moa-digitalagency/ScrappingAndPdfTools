# PDF Tools - Professional PDF Management Solution

![PDF Tools](https://img.shields.io/badge/PDF-Tools-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Flask](https://img.shields.io/badge/Flask-3.1+-red)

[Version Française](README.md)

## 📋 Description

PDF Tools is a professional web platform for advanced PDF file management. It offers bulk download, intelligent merging, and automatic AI-powered analysis capabilities.

## ✨ Key Features

### 🔽 Download & Zip
- **Bulk Download**: Support for 10,000+ simultaneous documents
- **Automatic Retry**: Retry logic with exponential backoff
- **Parallel Processing**: 10 concurrent workers for optimal performance
- **Extended Timeout**: 300 seconds per document
- **ZIP Compression**: Direct download of compressed files

### 🔀 Merge PDFs with Intelligent Analysis
- **Unlimited Upload**: No restrictions on size, volume, or number of files
- **Robust Merging**: Combines multiple PDFs into a single document
- **AI Analysis**: Intelligent text and structure extraction with OpenRouter
- **Excel Database**: Automatic generation of structured data
- **Detailed Metadata**: Extraction of titles, dates, entities, keywords

### 🤖 Intelligent Analysis (New)
- **Text Extraction**: Complete PDF content analysis
- **Structure Recognition**: Document type identification
- **Entity Extraction**: Detection of organizations, people, dates
- **Summary Generation**: Automatic 2-3 sentence summaries
- **Custom Fields**: Specific data extraction

## 🚀 Installation

### Prerequisites
- Python 3.11+
- OpenRouter account (for intelligent analysis)

### Local Installation

```bash
# Clone the repository
git clone <your-repo>
cd pdf-tools

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
export SECRET_KEY="your-secret-key"
export OPENROUTER_API_KEY="your-openrouter-key"

# Launch the application
gunicorn --bind 0.0.0.0:5000 --reuse-port main:app
```

### Deployment on Replit

1. Import the project on Replit
2. Configure secrets in the Replit interface:
   - `SECRET_KEY`
   - `OPENROUTER_API_KEY`
3. Click "Run"

See [DEPLOYMENT.md](DEPLOYMENT.md) for more details.

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key | Yes |
| `OPENROUTER_API_KEY` | OpenRouter API key for AI analysis | Optional* |

*If not configured, intelligent analysis will be disabled but other features will continue to work.

### Getting an OpenRouter Key

1. Create an account on [OpenRouter.ai](https://openrouter.ai)
2. Go to Settings > API Keys
3. Create a new API key
4. Copy and add to your secrets

## 📊 Architecture

```
pdf-tools/
├── app/
│   ├── routes/          # Flask routes (downloader, merger, main)
│   ├── services/        # Business logic
│   │   ├── pdf_downloader.py    # Parallel download with retry
│   │   ├── pdf_merger.py        # PDF merging
│   │   └── pdf_analyzer.py      # Intelligent AI analysis (NEW)
│   ├── templates/       # HTML templates
│   └── utils/          # Utilities (storage, etc.)
├── instance/           # Upload folder
├── tmp/               # Temporary files
├── config.py          # Configuration
├── main.py           # Entry point
└── requirements.txt  # Python dependencies
```

## 🎯 Usage

### Download & Zip

1. Go to `/downloader`
2. Enter a list of PDF URLs (one per line)
3. Click "Start"
4. Download the generated ZIP file

### Merge with Intelligent Analysis

1. Go to `/merger`
2. Upload a ZIP file containing PDFs
3. The application will:
   - Extract PDFs from the ZIP
   - Merge them into a single document
   - Analyze content with AI
   - Generate an Excel with detailed analysis
4. Download the ZIP containing merged PDF + analysis Excel

## 📈 Performance

- **Download**: 10,000+ documents supported
- **Upload**: No size limit
- **Parallelization**: 10 concurrent workers
- **Timeout**: 300s per document
- **Retry**: 3 attempts with exponential backoff

## 🔒 Security

- Strict file type validation
- Secure filenames with `secure_filename`
- Secure secret management
- Automatic cleanup of temporary files
- No upload limit (optimized memory management)

## 🛠️ Technologies

- **Backend**: Flask 3.1+
- **PDF Processing**: PyPDF 6.1+
- **Excel**: OpenPyXL 3.1+
- **AI**: OpenRouter API (Llama 3.1)
- **Server**: Gunicorn
- **Frontend**: Tailwind CSS

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for modification history.

## 🤝 Contribution

Contributions are welcome! Please:

1. Fork the project
2. Create a branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is under the MIT License.

## 📞 Support

For any questions or issues:
- Open an issue on GitHub
- Check the [deployment documentation](DEPLOYMENT.md)

---

Developed with ❤️ to simplify your PDF management
