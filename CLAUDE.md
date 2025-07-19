# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a web-based QR code processing toolkit designed for Vercel serverless deployment. The application detects, extracts, and converts QR codes from images with multiple processing options including transparent backgrounds, SVG conversion, and color inversion.

## Dependencies and Installation

### Required Dependencies
```bash
pip install -r requirements.txt
```

Dependencies include:
- `opencv-python-headless>=4.5.0` - Image processing
- `pyzbar>=0.1.8` - QR code detection
- `Pillow>=8.0.0` - Image manipulation
- `qrcode[pil]>=7.0.0` - QR code generation
- `Flask>=2.0.0` - Web framework

## Deployment

### Vercel Deployment (Primary)
```bash
# Deploy to Vercel
vercel deploy

# Test locally with Vercel dev environment
vercel dev
```

### Local Development
```bash
# Run API server directly
cd api && python app.py

# Access at http://localhost:5000 (when running locally)
```

## Code Architecture

### Core Components

1. **Serverless API** (`api/app.py`)
   - `VercelQRProcessor` class handles all QR processing operations
   - RESTful API endpoints under `/api/` route
   - Session-based file management with UUID tracking
   - Background processing with real-time status updates

2. **Frontend** (`public/index.html`)
   - Modern single-page application
   - Drag-and-drop file upload interface
   - Real-time processing status and progress
   - Multilingual support (English, Chinese, Japanese)
   - Responsive design with mobile support

3. **Configuration** (`vercel.json`)
   - Serverless function configuration
   - Static file routing
   - Environment variables setup

### API Endpoints

- `POST /api/process` - Upload files and start processing
- `GET /api/status` - Get real-time processing status
- `GET /api/results` - Retrieve processing results list
- `GET /api/preview/{session_id}/{file_path}` - Preview processed files
- `GET /api/download` - Download processed files
- `GET /api/health` - Health check endpoint
- `POST /api/cleanup` - Clean up old sessions

### Processing Pipeline

1. **File Upload**: Supports JPG, PNG, BMP, TIFF, WEBP formats (max 100MB)
2. **QR Detection**: Uses pyzbar for QR code detection in images
3. **Extraction**: Crops QR codes with configurable margins
4. **Processing Options**:
   - **Extract**: Basic QR code detection and cropping
   - **Transparent**: Converts white background to transparent
   - **SVG**: Generates scalable vector graphics version
   - **Invert**: Swaps black/white colors for dark themes

### Session Management

The application uses UUID-based sessions for file management:
- Each upload creates a unique session ID
- Files are organized by session in temporary storage
- Automatic cleanup prevents storage overflow
- Results are session-scoped for security

## Key Classes and Methods

### VercelQRProcessor Class
- `create_session()` - Creates new processing session with UUID
- `save_uploaded_files()` - Handles secure file uploads
- `process_files()` - Background processing with status updates
- `_detect_qr_codes()` - QR code detection using pyzbar
- `_extract_qr_region()` - QR code region extraction with margins
- `_create_transparent_version()` - Transparent background generation
- `_create_svg_version()` - SVG format conversion
- `scan_result_files()` - Results file scanning and metadata
- `cleanup_old_sessions()` - Automatic session cleanup

### Configuration Parameters
- `margin_ratio`: QR extraction margin (default: 0.05)
- `min_size`: Minimum QR size in pixels (default: 50)
- `white_threshold`: White color threshold for transparency (default: 240)
- `tolerance`: Color tolerance for transparency (default: 15)

## File Structure

```
/
├── api/
│   └── app.py              # Serverless API backend
├── public/
│   └── index.html          # Frontend web application
├── image/                  # Sample images for testing
│   ├── 123d24deb8ee85fd728be533a9789207.png
│   └── c7d18a0541d72fcc2c575634821dee1f_qr.png
├── requirements.txt        # Python dependencies
├── vercel.json            # Vercel deployment configuration
├── CLAUDE.md              # This file
└── README.md              # Project documentation
```

## Development Notes

### Testing
```bash
# Test API functionality locally
cd api && python app.py

# Test with sample images
# Upload files from image/ directory through web interface
```

### Deployment Requirements
- Vercel account and CLI installed
- All dependencies specified in requirements.txt
- Proper vercel.json configuration for API routes
- Static files served from public/ directory

### Web Features
- **Drag & Drop**: Intuitive file upload interface
- **Real-time Progress**: Live processing status updates
- **Multi-language**: English, Chinese, Japanese support
- **Responsive**: Mobile-friendly design
- **Session-based**: Secure file management
- **Download Management**: Easy result file downloads

### Common Issues
- Ensure vercel.json properly routes API calls to `/api/`
- Images must contain visible QR codes for processing
- Transparent background works best with white background QR codes
- Session cleanup prevents storage overflow in serverless environment
- File size limit is 100MB per upload

## Usage Patterns

### Web Interface
The primary interface is through the web application:
1. Upload images via drag-and-drop or file picker
2. Configure processing steps (transparent, SVG, invert)
3. Start processing and monitor real-time progress
4. Download results individually or preview online

### API Integration
For programmatic access, use the REST API endpoints with session-based file management and real-time status monitoring.