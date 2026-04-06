# PixelShift

A privacy-first bulk image converter that runs entirely on your machine. No email, no account, no upload limits, no server.

---

## Why I Built This

Every time I needed to convert a batch of images (usually iPhone HEIC files that nothing could open), I'd search for a tool online.

Almost every single one wanted something from me. Create an account. Confirm your email. Upgrade to convert more than 5 files. Wait in a queue. Accept that your photos are now on someone else's server.

I didn't want any of that. I just wanted to convert my files.

So I built PixelShift. It runs on your machine, converts as many files as you want, and sends nothing anywhere.

---

## Solution Overview

PixelShift is a desktop app that converts images between formats in bulk. Select your files, pick an output format, and convert. Everything happens locally. No internet connection required after installation.

---

## How It Works

```
Select files (JPEG, PNG, HEIC, WEBP, BMP, GIF, TIFF)
    │
    ▼
Pick output format
    - PNG, JPEG, WEBP, BMP, GIF, HEIC
    - JPEG quality control (1-100 slider)
    │
    ▼
Optional: Resize
    - Set width and/or height in pixels
    - Maintain aspect ratio toggle
    │
    ▼
Convert (background thread - UI stays responsive)
    - EXIF orientation reads the rotation tag and applies it on save
    - GPS and metadata stripped when Privacy Mode is on
    - Transparency fixed for JPEG and HEIC (RGBA to RGB)
    - Existing files: choose Overwrite, Overwrite All, Skip, or Skip All
    │
    ▼
Output saved to chosen folder
    - Progress bar updates in real time
    - Success dialog with Open Folder button
    - Failed files listed separately
```

---

## Features

- **All common formats** : converts between PNG, JPEG, WEBP, BMP, GIF, HEIC, TIFF
- **Bulk conversion** : select and convert as many files as you want at once
- **Add and remove files** : add images from multiple folders one batch at a time, remove individual files with the X button
- **HEIC support** : reads and writes Apple's HEIC format
- **Privacy Mode** : strips GPS coordinates and all metadata before saving. On by default.
- **JPEG quality slider** : control the quality and file size tradeoff. Appears only when JPEG is selected.
- **Resize** : scale images to a target width and/or height, with aspect ratio lock
- **EXIF orientation fix** : reads the rotation tag from the original file and applies it on save
- **Duplicate handling** : if a file already exists, asks you to Overwrite, Overwrite All, Skip, or Skip All
- **Cancel mid-run** : stop conversion at any point
- **Open Folder on completion** : one click to see your converted files
- **Format Guide** : built-in popup explaining when to use each format
- **Fully offline** : nothing leaves your machine

---

## Who Uses It

| User | Problem | How PixelShift Helps |
|---|---|---|
| **The iPhone User** | You took 100 photos on your iPhone but can't upload, print, or share them because they are in HEIC format | Drop them all in, hit JPEG, and they are instantly ready to share with anyone, anywhere |
| **The Privacy-Conscious Parent** | You want to post a photo of your kids online but don't want the hidden GPS coordinates to reveal where your house or their school is | Turn on Privacy Mode. It wipes the location data clean while keeping the photo beautiful |
| **The Professional Office Worker** | Your company asked you to convert employee ID photos or sensitive documents. Using an online converter means uploading private files to a random server in another country | Works fully offline. No data ever leaves your computer, so you stay GDPR compliant without thinking about it |
| **The Website or Canva User** | You have 50 high-quality photos that are 10MB each, too big to upload to Canva or your blog and slow to load | Use the Resize tool. Shrink all 50 photos at once so they upload in seconds |

---

## Installation

**Requirements:** Python 3.10+

```bash
git clone https://github.com/AdrianaGRO/pixelshift.git
cd pixelshift
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

---

## How to Run

```bash
python3 main.py
```

---

## Requirements

```
customtkinter
Pillow
pillow-heif
```

Install all at once:

```bash
pip install -r requirements.txt
```

---

## Format Guide

| Format | Best For |
|--------|----------|
| **JPEG** | Photos and social media. Small file size, slight quality loss. |
| **PNG** | Logos and screenshots. Supports transparency, no quality loss. |
| **WEBP** | Web images. Smaller than JPEG/PNG with great quality. |
| **HEIC** | iPhone photos. Great quality, small size. Limited compatibility outside Apple. |
| **GIF** | Simple animations. Limited to 256 colors. |
| **BMP** | Legacy format. No compression, very large files. |
| **TIFF** | Print and professional work. Huge files, no quality loss. |

---

## License

MIT License.