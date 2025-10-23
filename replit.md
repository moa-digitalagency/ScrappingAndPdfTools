# Application de Traitement de PDFs

## Overview
This project is a professional Flask web application designed for advanced PDF processing, featuring intelligent AI-powered analysis. Its core capabilities include massive PDF downloading and ZIP compression, merging multiple PDFs from a ZIP archive with Excel metadata generation, and intelligent data extraction from PDFs using AI, leading to structured Excel databases. A key recent addition is the automatic extraction of legal data (jurisprudence) from legal documents, including references, jurisdictions, dates, keywords, and legal bases, with export options to Excel/CSV. The application aims to provide robust, scalable, and intelligent PDF handling for various business needs.

## User Preferences
- Interface en français
- Interface professionnelle avec Tailwind CSS

## System Architecture
The application uses a Flask backend with a modular blueprint structure, and an HTML/CSS frontend leveraging Tailwind CSS via CDN. PDF manipulation is handled by `pypdf`, and `openpyxl` is used for Excel file generation. For downloading, `requests` is combined with `ThreadPoolExecutor` for parallel processing. AI capabilities, including intelligent analysis and jurisprudence extraction, are powered by the OpenRouter API (Llama 3.1).

Key architectural decisions and features include:
- **Modular Flask Application**: Organized into blueprints for downloader, merger, analyzer, and jurisprudence functionalities.
- **Robust File Handling**: Supports massive uploads via streaming, handles temporary file cleanup, and uses secured naming conventions.
- **Parallel Processing**: Utilizes `ThreadPoolExecutor` for efficient parallel downloading (20 workers) and AI analysis (5 workers).
- **Error Management**: Implements automatic retries with exponential backoff, optimized timeouts, and detailed error logging.
- **Real-time Feedback**: Integrates Server-Sent Events (SSE) for real-time progress updates, including counters, batch status, and visual progress bars.
- **Persistent Logging**: Stores all action logs (startups, successes, errors) in an SQLite database, accessible via a dedicated `/logs/` page.
- **Secure Git Update**: A protected `/git_pull` route, authenticated by `ADMIN_SECRET`, allows for secure code deployment.
- **UI/UX**: Features a responsive layout with a professional aesthetic provided by Tailwind CSS, including distinct interfaces for each core functionality (downloader, merger, analyzer, jurisprudence extractor).

### Feature Specifications:
- **Massive Download & ZIP**: Supports 10,000+ documents with optimized batching (50 URLs/batch), parallel downloading, automatic retries, and robust error handling.
- **PDF Merging**: Allows unlimited uploads, streams data in chunks, automatically merges PDFs from a ZIP, and generates detailed Excel metadata.
- **Intelligent AI Analysis**: Processes CSVs of links, ZIPs of PDFs, or single PDFs. Extracts document types, entities, dates, keywords, summaries, and custom fields using OpenRouter AI. Exports data into a structured Excel database with multiple sheets.
- **Jurisprudence Extraction**: Specifically designed to extract over 20 legal fields from judicial PDFs (e.g., reference, jurisdiction, dates, keywords, legal basis, summaries) with output options for Excel and CSV.

## External Dependencies
- **OpenRouter API**: Used for intelligent PDF analysis and jurisprudence extraction (requires `OPENROUTER_API_KEY`).
- **pypdf**: Python library for PDF manipulation.
- **openpyxl**: Python library for reading and writing Excel 2010 xlsx/xlsm/xltx/xltm files.
- **requests**: Python HTTP library for making web requests (used for downloading PDFs).
- **Tailwind CSS (CDN)**: For frontend styling.
- **SQLite**: Used for persistent logging of application events.