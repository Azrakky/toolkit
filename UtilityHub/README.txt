UtilityHub v0.3 — Video Converter

1. Close the old UtilityHub server window.
2. Double-click Start Toolkit.bat and confirm http://localhost:3000 opens.
3. For video conversion, double-click Install Converter Dependencies.bat.
4. Install FFmpeg if needed: open PowerShell and run:
      winget install --id Gyan.FFmpeg -e
   If winget is unavailable, get FFmpeg from https://ffmpeg.org/download.html
   Add its bin folder to your Windows PATH. Restart VS Code and the server.
5. In Gadgets, click Open Video Converter. Verify both dependencies say Ready.
6. Paste a YouTube URL you are authorized to download; choose MP3 or MP4.
7. Set output folder in Settings; files are saved there.

Notes:
- This app runs only on 127.0.0.1:3000, not on the public internet.
- Downloading may be limited by YouTube policies, copyright, or video restrictions.
- No login, DRM bypass, or cookie import is implemented.
- MP4 can require re-encoding; conversions can take time.
- yt-dlp and FFmpeg are third-party tools.
- The browser does not directly download the result; check your configured folder.
- Python 3.15 compatibility depends on third-party package support.
- If the server fails, read the command window error and confirm port 3000 is free.
