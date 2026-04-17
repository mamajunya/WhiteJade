# WhiteJade - Pixiv Smart Downloader & Content Moderator

[中文文档](README_ZH.md) | English

WhiteJade is a main branch of the cll project, designed to efficiently curate content from Pixiv.

## Features

### Core Functions
- **Smart Search & Download**: Batch download Pixiv artworks by keywords, bookmarks, and more
- **AI Content Moderation**: Automatically filter inappropriate content using DeepDanbooru deep learning model
- **Precise Quantity Control**: Automatically adjusts download volume to ensure final kept images meet target count
- **Task Control**: Support pause, resume, and stop operations
- **Theme Customization**: Customize interface theme and background colors
- **Multi-language Support**: Chinese, Japanese, Korean, English, French, German

### Advanced Filtering
- Skip R-18 content
- Remove AI-generated artworks
- Minimum bookmark count filter
- Adjustable moderation strictness (5 levels)

### Automated Management
- Auto-categorization: Approved images, filtered images, download history
- Deduplication: Avoid duplicate downloads
- Detailed statistics: Download count, moderation count, filter rate, etc.

## Quick Start

### Method 1: Use Release Version (Recommended)
1. Download the latest release package
2. Extract to any directory
3. Double-click `WhiteJade.exe` to launch

### Method 2: One-Click Launch (Development Version)
Double-click `run.bat`, the program will automatically detect and install required dependencies.

### Method 3: Manual Installation (Development Version)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch GUI
python gui_app.py
```

## Build for Distribution

To package as an exe executable:

```bash
build.bat
```

## Usage Guide

### 1. Get Pixiv Token
In the "Token Acquisition" tab:
1. Enter your Pixiv email and password
2. Click "Get Token"
3. Token will be automatically copied to clipboard
4. Click "Save to Config"

### 2. Download & Filter
In the "Download & Filter" tab:

**Download Settings**
- Search Keywords: Enter character name or tags
- Download Count: Final number of images to keep
- Minimum Bookmarks: Filter low-bookmark artworks
- Skip R-18: Filter adult content
- Remove AI Artworks: Filter AI-generated content

**Moderation Settings**
- Enable Image Moderation: Auto-filter inappropriate content
- Detection Threshold: 0.4 (Very Strict) to 0.8 (Very Loose)
- Move to ban directory: Move filtered images instead of deleting

### 3. Task Control
- Start: Begin download task
- Pause: Pause current task
- Resume: Resume paused task
- Stop: Completely stop task

## Directory Structure

```
WhiteJade/
├── downloads/              # Download root directory
│   └── [keyword]/
│       ├── picture/       # Approved images
│       ├── ban/          # Filtered images
│       └── history/      # Download history and metadata
├── model/                 # DeepDanbooru model files
├── pixiv_downloader/      # Downloader module
├── image_moderator/       # Moderator module
├── gui_app.py            # GUI main program
├── environment_checker.py # Environment checker
└── run.bat               # One-click launch script
```

## Tech Stack

- **GUI Framework**: PyQt6
- **Pixiv API**: pixivpy3
- **Token Acquisition**: gppt
- **AI Moderation**: DeepDanbooru + TensorFlow
- **Image Processing**: Pillow

## Moderation Mechanism

### DeepDanbooru Model
- Deep learning model specifically trained on anime images
- 9,176 tag classifications
- Automatically detects and filters inappropriate content

### Filter Tags
- `penis` (genitalia)
- `sex` (sexual acts)
- `vaginal` (vaginal-related)
- `anal` (anal-related)

### Threshold Explanation
- **0.4 - Very Strict** (default): Strictest filtering, suitable for public settings
- **0.5 - Strict**: Relatively strict filtering
- **0.6 - Default**: Balanced mode
- **0.7 - Loose**: Relatively loose filtering
- **0.8 - Very Loose**: Loosest filtering

## Smart Download Mechanism

When moderation is enabled, the program will:
1. Estimate filter rate, initially download 1.5x the target count
2. Moderate downloaded images
3. If kept count is insufficient, continue downloading based on actual filter rate
4. Repeat until target count is reached (max 5 rounds)

**Example**:
- Target: 20 images
- Round 1: Download 30 artworks → Keep 15 after moderation
- Round 2: Continue downloading 10 artworks → Keep 5 after moderation
- Final: 20 images kept ✓

## Important Notes

1. **First Run**: Will automatically download DeepDanbooru model (~600MB), please be patient
2. **Token Validity**: Pixiv tokens expire and need to be refreshed periodically
3. **Network Requirements**: Requires access to Pixiv servers
4. **Storage Space**: Ensure sufficient space for downloaded images and model files

## FAQ

### Q: Login failed, what should I do?
A: Check if the token is correct, or re-acquire the token.

### Q: Download speed is slow?
A: Pixiv servers are in Japan, access from other regions may be slow. Consider using a proxy.

### Q: Moderation too strict/loose?
A: Adjust the detection threshold in "Moderation Settings".

### Q: How to view filtered images?
A: Check the `downloads/[keyword]/ban/` directory.

## License

This software is completely open source and free.

**Important Notice**: If you purchased this software online, please request a refund immediately and report the seller.

## Changelog

### v2.0.0
- Brand new GUI interface
- Integrated DeepDanbooru AI moderation
- Smart quantity control
- Task pause/resume functionality
- Theme color customization
- Multi-language support
- AI artwork filtering
- Detailed log output

## Contact

For issues or suggestions, please submit an Issue.

---

**Disclaimer**: This tool is for educational and research purposes only. Please comply with Pixiv's Terms of Service and local laws and regulations.
