# WhiteJade - Pixiv Smart Downloader & Content Moderator

[中文文档](README_ZH.md) | English

WhiteJade is a main branch of the cll project, designed to efficiently curate content from Pixiv.

## Features

### Core Functions
- **Smart Search & Download**: Batch download Pixiv artworks by keywords, bookmarks, and more
- **Bookmark Download**: Download artworks from your Pixiv bookmarks/favorites
- **Multi-threaded Download**: Configurable concurrent downloads (1-10 threads, default 3) for faster performance
- **Parallel Moderation**: Download and moderation run simultaneously without blocking
- **Ugoira (Animation) Support**: Download, moderate, and auto-convert animated artworks
  - Auto-convert to GIF or MP4 format (configurable in settings)
  - Default: GIF format
  - Intelligent frame sampling for moderation
- **AI Content Moderation**: Automatically filter inappropriate content using DeepDanbooru deep learning model
- **Custom Filter Tags**: Choose from 16 NSFW tags to customize content filtering
- **Precise Quantity Control**: Automatically adjusts download volume to ensure final kept images meet target count
- **Task Control**: Support pause, resume, and stop operations
- **Theme Customization**: Customize interface theme and background colors
- **Multi-language Support**: Chinese, Japanese, Korean, English, French, German
- **System Tray**: Minimize to system tray, run in background
- **Custom Download Folder**: Set custom download directory with automatic data migration
- **Flexible Close Behavior**: Choose to exit, minimize to tray, or ask every time

### Advanced Filtering
- Skip R-18 content
- Remove AI-generated artworks
- Skip or only download ugoira (animations)
- Minimum bookmark count filter
- Adjustable moderation strictness (5 levels)
- Custom filter tags selection (16 NSFW tags available)
- Debug logging for detailed moderation analysis

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

**Download Mode**
- Keyword Search: Search and download by keywords (original mode)
- My Bookmarks: Download artworks from your Pixiv bookmarks/favorites

**Download Settings**
- Search Keywords: Enter character name or tags (only for Keyword Search mode)
- Download Count: Final number of images to keep
- Minimum Bookmarks: Filter low-bookmark artworks
- Skip R-18: Filter adult content
- Remove AI Artworks: Filter AI-generated content
- Skip Ugoira: Skip animated artworks (ugoira)
- Only Ugoira: Download only animated artworks (mutually exclusive with Skip Ugoira)

**Moderation Settings**
- Enable Image Moderation: Auto-filter inappropriate content
- Detection Threshold: 0.4 (Very Strict) to 0.8 (Very Loose)
  - Dynamic frame sampling for ugoira: 100% frames at 0.4, 90% at 0.5, 80% at 0.6, 60% at 0.7, 40% at 0.8
  - Ugoira threshold offset: -0.1 (stricter moderation for low-quality animations)
- Advanced Filter Options: Customize which NSFW tags to filter
  - 16 selectable tags including: penis, sex, vaginal, anal, fellatio, cunnilingus, pussy, nude, masturbation, cum, orgasm, ejaculation, nipples, pussy_juice, sex_from_behind, female_ejaculation
  - Default: penis + sex (recommended for most users)
  - Compact UI: Shows selected tags, click button to open dialog
  - Settings persist across app restarts
- Move to ban directory: Move filtered images instead of deleting

### 3. Settings

**Theme Color**
- Choose from preset colors or select custom color
- Real-time preview

**Language**
- Select from 6 languages
- Restart required after change

**Close Behavior**
- Ask every time: Show dialog when closing window
- Exit directly: Close window exits application
- Minimize to tray: Close window minimizes to system tray

**Download Threads**
- Configure concurrent download threads (1-10)
- Default: 3 threads
- Higher thread count = faster downloads

**Animation Format**
- Choose output format for ugoira (animated artworks)
- GIF: Universal format, larger file size
- MP4: Smaller file size, requires video player
- Default: GIF
- Approved animations are automatically converted after moderation

**Download Folder**
- View current download directory
- Change folder: Select new directory with automatic data migration
- Open folder: Open download directory in file explorer

**Debug Logging**
- Enable detailed moderation logs (default: off)
- Logs saved to `downloads/logs/debug_[keyword]_[timestamp].log`
- Shows all detected tags, confidence scores, threshold comparisons
- Useful for understanding moderation decisions and fine-tuning settings

**System Tray**
- Double-click tray icon to show/hide window
- Right-click for menu options
- Runs in background when minimized

### 4. Task Control
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
- **Image Processing**: Pillow, OpenCV
- **Multi-threading**: Python threading and queue

## Moderation Mechanism

### DeepDanbooru Model
- Deep learning model specifically trained on anime images
- 9,176 tag classifications
- Automatically detects and filters inappropriate content
- Supports both static images and animated artworks (ugoira)

### Ugoira (Animation) Moderation & Conversion
- **Dynamic Frame Sampling**: Sample rate based on threshold strictness
  - 0.4 (Very Strict): 100% of frames
  - 0.5 (Strict): 90% of frames
  - 0.6 (Default): 80% of frames
  - 0.7 (Loose): 60% of frames
  - 0.8 (Very Loose): 40% of frames
  - Uniform distribution sampling across entire animation
- **Stricter Threshold**: Ugoira moderation uses threshold - 0.1 (due to lower quality)
- All sampled frames must pass moderation for the animation to be kept
- If any frame fails, the entire animation is filtered
- **Auto-conversion**: Approved animations are automatically converted to GIF or MP4
  - GIF: Universal format, works everywhere, larger file size
  - MP4: Modern format, smaller file size, requires video player
  - Format configurable in Settings tab
  - Original ugoira files (zip + frames) are deleted after successful conversion
- Efficient sampling ensures thorough moderation without processing all frames

### Filter Tags
Default tags (recommended):
- `penis` (male genitalia)
- `sex` (sexual acts)

Additional selectable tags (16 total):
- `vaginal`, `anal` (penetration types)
- `fellatio`, `cunnilingus` (oral acts)
- `pussy`, `nude` (nudity)
- `masturbation`, `cum`, `orgasm`, `ejaculation` (sexual activities)
- `nipples`, `pussy_juice`, `sex_from_behind`, `female_ejaculation` (body parts and acts)

Users can customize which tags to filter through the Advanced Filter Options.

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

### v2.3.0 - Performance & Animation Enhancement (2026-04-25)
- **Multi-threaded Download**: Configurable concurrent downloads (1-10 threads, default 3)
  - 3-10x faster download speed depending on thread count
  - Configurable in Settings tab
- **Parallel Processing**: Download and moderation run simultaneously
  - No more waiting for all downloads to complete before moderation starts
  - Each downloaded artwork is immediately queued for moderation
  - Significantly improved overall workflow efficiency
- **Ugoira Auto-conversion**: Automatically convert approved animations
  - GIF format: Universal compatibility, larger file size
  - MP4 format: Smaller file size, modern format
  - Configurable in Settings tab (default: GIF)
  - Original ugoira files deleted after successful conversion
- **Enhanced Performance**: Producer-consumer pattern with thread-safe queues
- **Real-time Progress**: Live updates for download and moderation status
- **Ugoira Filters**: Skip or only download animated artworks
- **Dynamic Frame Sampling**: Adaptive sampling rate based on threshold (40%-100%)
- **Stricter Ugoira Moderation**: -0.1 threshold offset for low-quality animations
- **Advanced Filter UI**: Compact popup dialog with persistent settings
- **Debug Logging**: Detailed moderation logs with tag confidence scores
- Multi-language support for all new features

### v2.2.2 - Ugoira Support (2026-04-18)
- **Ugoira (Animation) Download**: Full support for downloading Pixiv animated artworks
  - Downloads ugoira zip files with frame timing information
  - Preserves animation data for future playback
- **Ugoira Moderation**: Intelligent frame sampling for animation moderation
  - Randomly samples one frame from first 10% and one from last 10%
  - Both frames must pass for animation to be kept
  - Efficient moderation without processing all frames
- **Enhanced Directory Structure**: Separate folders for ugoira files
- All ugoira features support multi-language interface

### v2.2.1 - Better Download (2026-04-19)
- **New Download Mode**: Added "My Bookmarks" mode to download from your Pixiv favorites
- **Custom Filter Tags**: Advanced filter options with 16 selectable NSFW tags
  - Visual checkbox interface for easy tag selection
  - Default: penis + sex (suitable for most users)
  - Customizable based on personal preferences
- **Enhanced Moderation**: More flexible content filtering with tag-based system
- **Improved UX**: Better organization of download modes and filter options
- Multi-language support for all new features

### v2.1.0
- System tray support with background running
- Custom download folder with automatic data migration
- Flexible close behavior settings (ask/exit/minimize to tray)
- Simplified button text for better UI appearance
- Bug fixes and performance improvements

### v2.0.0
- Brand new GUI interface with rounded corners and modern design
- Integrated DeepDanbooru AI moderation system
- Smart quantity control with automatic adjustment
- Task pause/resume/stop functionality
- Theme color customization with preset options
- Multi-language support (6 languages)
- AI artwork filtering option
- System tray support with background running
- Custom download folder with data migration
- Flexible close behavior settings
- Detailed log output with real-time progress
- GitHub integration button

## Contact

For issues or suggestions, please submit an Issue.

---

**Disclaimer**: This tool is for educational and research purposes only. Please comply with Pixiv's Terms of Service and local laws and regulations.
