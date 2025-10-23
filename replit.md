# Application de Traitement de PDFs

## Overview
This project is a professional Flask web application designed for advanced PDF processing. Its core capabilities include massive PDF downloading and ZIP compression, merging multiple PDFs from a ZIP archive with Excel metadata generation, and rule-based extraction of legal data (jurisprudence) from legal documents. The jurisprudence extraction feature uses robust regex patterns to extract references, jurisdictions, dates, keywords, legal bases, and summaries, with export options to Excel/CSV. The application aims to provide robust, scalable, and efficient PDF handling for various business needs without AI dependencies or timeout issues.

## User Preferences
- Interface en français
- Interface professionnelle avec Tailwind CSS

## System Architecture
The application uses a Flask backend with a modular blueprint structure, and an HTML/CSS frontend leveraging Tailwind CSS via CDN. PDF manipulation is handled by `pypdf`, and `openpyxl` is used for Excel file generation. For downloading, `requests` is combined with `ThreadPoolExecutor` for parallel processing. Jurisprudence extraction uses robust regex-based pattern matching for reliable data extraction without AI dependencies.

Key architectural decisions and features include:
- **Modular Flask Application**: Organized into blueprints for downloader, merger, analyzer, jurisprudence, and library functionalities.
- **Robust File Handling**: Supports massive uploads via streaming, handles temporary file cleanup, and uses secured naming conventions.
- **Parallel Processing**: Utilizes `ThreadPoolExecutor` for efficient parallel downloading (20 workers) and jurisprudence extraction (4 workers).
- **Error Management**: Implements automatic retries with exponential backoff, optimized timeouts, and detailed error logging.
- **Real-time Feedback**: Integrates Server-Sent Events (SSE) for real-time progress updates, including counters, batch status, and visual progress bars.
- **Persistent Logging**: Stores all action logs (startups, successes, errors) in an SQLite database, accessible via a dedicated `/logs/` page.
- **Secure Git Update**: A protected `/git_pull` route, authenticated by `ADMIN_SECRET`, allows for secure code deployment.
- **UI/UX**: Features a responsive layout with a professional aesthetic provided by Tailwind CSS, including distinct interfaces for each core functionality (downloader, merger, analyzer, jurisprudence extractor, PDF library). The Library feature is integrated as a main feature card on the homepage rather than a navigation link, providing better visibility and user flow. The Library interface has been simplified with 4 clear primary actions: Import PDFs, Extract to Excel, Extract to CSV, and Delete.

### Feature Specifications:
- **Massive Download & ZIP**: Supports 10,000+ documents with optimized batching (50 URLs/batch), parallel downloading, automatic retries, and robust error handling.
- **PDF Merging**: Allows unlimited uploads, streams data in chunks, automatically merges PDFs from a ZIP, and generates detailed Excel metadata.
- **Rule-Based Jurisprudence Extraction**: Specifically designed to extract over 20 legal fields from judicial PDFs using robust regex patterns (e.g., reference, jurisdiction, dates, keywords, legal basis, summaries). Features:
  - No AI dependency - purely rule-based extraction
  - Single-pass processing for both Excel and CSV export (optimized performance)
  - Parallel processing of PDFs (4 workers) for efficient batch handling
  - Accent-tolerant regex patterns for French/Arabic bilingual content
  - Intelligent failure detection - reports error when all PDFs fail
  - Progressive upload support for unlimited file volumes without timeouts
  - Comprehensive error handling and logging
- **PDF Library**: Complete PDF management system with unlimited file imports, renaming, deletion, individual or bulk selection, and robust text extraction using PyPDF. Features:
  - **Preview-First Upload**: Users can preview selected PDFs before uploading, remove unwanted files, and see total size
  - **Progressive Upload**: Each PDF is uploaded individually (1-by-1) with real-time progress tracking
  - **Flexible Export**: Extract and export text to Excel or CSV formats from selected PDFs
  - Streaming-based batch processing to handle large volumes without memory issues
  - Intelligent error handling for image-only PDFs and automatic validation of extracted content
  - All imported PDFs are stored persistently in a SQLite database with full metadata tracking

## External Dependencies
- **pypdf**: Python library for PDF manipulation.
- **openpyxl**: Python library for reading and writing Excel 2010 xlsx/xlsm/xltx/xltm files.
- **requests**: Python HTTP library for making web requests (used for downloading PDFs).
- **Tailwind CSS (CDN)**: For frontend styling.
- **SQLite**: Used for persistent logging of application events.

## Deployment Ports
- **Replit**: Port 5000 (required by Replit infrastructure)
- **VPS**: Port 5003 (configured in deploy_vps.sh and DEPLOYMENT_VPS.md)