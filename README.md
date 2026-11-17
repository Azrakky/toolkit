
Website
https://toolkit-production-2707fb56.up.railway.app/

# Toolkit — UtilityHub

**A modular, web-based utility platform built with Python, HTML, CSS, and JavaScript.**

Toolkit is a growing collection of tools designed to simplify everyday tasks through a centralized dashboard. Its primary application, **UtilityHub**, provides a browser-based interface connected to a Python backend.

The project is designed to support additional gadgets and utilities over time, while allowing local development and cloud deployment.

## Project Overview

**Application:** UtilityHub  
**Current Version:** 0.3  
**Repository:** [Azrakky/toolkit](https://github.com/Azrakky/toolkit)  
**Hosting:** Railway  
**Development Environment:** Visual Studio Code  
**Backend:** Python 3  
**Frontend:** HTML5, CSS3, JavaScript

### Live Application

[Launch UtilityHub](https://toolkit-production-2707fb56.up.railway.app)

*The hosted application is under active development. Some features require additional cloud configuration.*

## Features

### 1. UtilityHub Dashboard

The main interface provides centralized access to the application's available and planned gadgets.

- Browser-based dashboard
- Navigation between Dashboard, Gadgets, and Settings
- Connection to the Python backend
- Modular design for future expansion

### 2. Backend Connection Test

A diagnostic gadget used to verify communication between the frontend and Python backend.

- Sends a test request to the server
- Confirms successful API communication
- Helps troubleshoot deployment and connectivity problems

### 3. Video Converter — MP3 / MP4

A media conversion gadget powered by `yt-dlp` and FFmpeg.

**Capabilities:**
- Accepts supported YouTube video URLs
- Extracts audio into MP3 format
- Downloads and processes video into MP4 format
- Supports video quality selections up to 1080p
- Displays conversion progress and job status
- Checks whether required dependencies are installed
- Limits simultaneous conversions

**Dependencies:**
- Python 3
- yt-dlp
- FFmpeg

**Important:** The converter is intended only for content the user owns or is authorized to download. On Railway, generated files are stored in the server environment rather than automatically transferred to the user's computer. Cloud file retrieval remains a planned enhancement.

### 4. Settings Management

UtilityHub includes a settings interface connected to the Python backend.

Current settings include:
- Customizable application display name
- Configurable download directory
- Server-side settings storage using JSON

Cloud environments may require persistent storage for settings and downloaded files.

### 5. PDF Toolkit — Planned

A future gadget intended to provide PDF-related utilities.

Potential functionality includes:
- PDF merging
- PDF splitting
- PDF conversion
- Page extraction
- Document organization

These features are planned and are not yet implemented.

## Project Structure

```text
Toolkit/
├── UtilityHub/
│   ├── frontend/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   ├── gadgets/
│   ├── main.py
│   ├── Install Converter Dependencies.bat
│   ├── Start Toolkit.bat
│   └── README.txt
├── converter/
│   └── main.cpp
├── main.html
├── README.md
└── .gitignore
```

**Directory descriptions:**

| File / Directory | Purpose |
|---|---|
| `UtilityHub/` | Main modular utility application |
| `frontend/index.html` | Dashboard HTML structure |
| `frontend/style.css` | Interface styling |
| `frontend/app.js` | Frontend behavior and API communication |
| `gadgets/` | Directory reserved for modular utilities |
| `main.py` | Python HTTP server and API |
| `Start Toolkit.bat` | Local application launcher |
| `Install Converter Dependencies.bat` | Local dependency installation |
| `converter/main.cpp` | Separate C++ converter project |
| `main.html` | Additional root-level HTML project file |
| `.gitignore` | Excludes selected generated and temporary files |

## Local Installation

### Requirements

Install Python 3 from [python.org](https://www.python.org/downloads/).

Install the converter dependencies:

```bash
python -m pip install -U yt-dlp
```

FFmpeg must also be installed and available through the system PATH.

Alternatively, run the provided Windows dependency installation script.

### Start UtilityHub

Navigate to the UtilityHub directory:

```bash
cd UtilityHub
python main.py
```

Open the local application:

http://localhost:3000

By default, UtilityHub uses port 3000 locally unless the `PORT` environment variable specifies another port.

## Cloud Deployment — Railway

UtilityHub is configured to run on Railway.

**Deployment configuration:**

| Setting | Value |
|---|---|
| Source repository | `Azrakky/toolkit` |
| Branch | `main` |
| Root directory | `UtilityHub` |
| Start command | `python main.py` |
| Server host | `0.0.0.0` |
| Port | Railway `PORT` environment variable |
| Healthcheck endpoint | `/api/health` |

The Python backend reads the port assigned by Railway:

```python
port = int(os.environ.get("PORT", 3000))
server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
```

The Railway public domain's target port must match the port the application is listening on.

### Deployment Updates

Changes are committed and pushed to GitHub:

```bash
git add .
git commit -m "Update UtilityHub"
git push
```

Railway can automatically deploy new commits when GitHub auto-deployment is enabled and correctly configured.

## Backend API

UtilityHub currently includes the following endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Check backend health |
| `/api/gadgets` | GET | Retrieve available gadgets |
| `/api/settings` | GET | Retrieve application settings |
| `/api/settings` | POST | Update application settings |
| `/api/gadgets/connection-test` | POST | Test frontend/backend communication |
| `/api/converter/dependencies` | GET | Check converter dependencies |
| `/api/converter/start` | POST | Start a conversion job |
| `/api/converter/jobs/{id}` | GET | Retrieve conversion status |

## Security

UtilityHub currently includes basic request validation, URL restrictions for the converter, and limits on concurrent conversion jobs.

However, these protections do not replace authentication.

**Private access protection must be configured before exposing the converter for general use.** A service such as Cloudflare Access may be used to restrict access to authorized users.

## Development Roadmap

### Completed
- [x] Initial UtilityHub dashboard
- [x] Python backend integration
- [x] Backend connection test
- [x] YouTube MP3 conversion
- [x] YouTube MP4 conversion
- [x] Conversion progress tracking
- [x] Settings API
- [x] GitHub repository integration
- [x] Railway deployment configuration

### Planned
- [ ] Secure cloud access and authentication gateway
- [ ] Cloud-based MP3/MP4 dependency verification
- [ ] Download converted files directly through the browser
- [ ] Persistent cloud storage
- [ ] Faster conversion and download performance
- [ ] Fast / Balanced / Best Quality modes
- [ ] Improved download progress and speed reporting
- [ ] PDF Toolkit
- [ ] Additional modular gadgets
- [ ] Improved deployment automation

## Technologies

- **Python:** Backend application logic and HTTP server
- **HTML5:** Web interface
- **CSS3:** Dashboard styling
- **JavaScript:** Frontend functionality and API requests
- **yt-dlp:** Supported media retrieval
- **FFmpeg:** Audio/video processing
- **Git and GitHub:** Source control
- **Railway:** Cloud application hosting
- **Visual Studio Code:** Development environment

## Project Status

**UtilityHub v0.3 — Active Development**

The application has a functioning local dashboard and converter, with cloud deployment being configured and tested. Features and documentation will continue to evolve as new gadgets are developed.

---

**Developed by Azrakky**

Toolkit is an evolving personal software project focused on building practical, reusable utilities through a single platform.