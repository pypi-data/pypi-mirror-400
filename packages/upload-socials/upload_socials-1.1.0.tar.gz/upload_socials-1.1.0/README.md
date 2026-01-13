# 🚀 upload-socials

Streamline your content workflow by automating video uploads to YouTube with this Python library. Now supports automated monetization settings!

---

## ⚠️ Prerequisites

This is a GUI automation library and **requires a specific setup to function**:

1.  **Screen Resolution:** Your screen resolution should ideally be **1920x1080**. The browser window should be maximized during the process.
2.  **Reference Images:** GUI automation works by finding images on the screen. You **must** provide your own folders of reference images (e.g., screenshots of the 'Upload', 'Next', and 'Publish' buttons).
3.  **Platform Language:** The YouTube Studio website must be set to **English**.

This library is best suited for developers comfortable with tuning GUI automation scripts.

## Installation

```bash
pip install upload-socials
```

## Setup: Reference Images

You must create a directory (e.g., `assets/youtube`) containing screenshots of the YouTube Studio interface. The script looks for `.png` files with specific names.

**Basic Upload Images:**
*   `create.png`, `uploadvids.png`, `select.png`
*   `filename.png` (The file input field in Windows Explorer)
*   `title.png`, `tell.png` (Description box)
*   `thumbnail.png`
*   `showmore.png`, `tags.png`
*   `next.png`, `publish.png`
*   `processing.png` (The "SD/HD processing" checkmark at the end)

**Monetization Images (Required if `monetization=True`):**
*   `monetizeselect.png` (The monetization tab/dropdown)
*   `monetizeon.png` (Radio button to turn On)
*   `monetizedone.png` (Done button inside dropdown)
*   `monetizeactive.png`
*   `monetizenone.png` (The "None of the above" checkbox for ad suitability)
*   `monetizesubmit.png` (Submit rating button)
*   `monetizepublic.png` (Public visibility radio button)
*   `publish2.png` (Secondary publish button if layout differs)

## Quick Start

```python
from upload_socials import upload_youtube

# 1. Define the path to your screenshots folder
YT_IMAGE_PATH = r"C:\\my_automation_images\\youtube"

# 2. Define Video details
video_file = r"C:\\path\\to\\my_awesome_video.mp4"
video_title = "My First Automated Upload!"
video_desc = "This was uploaded using the upload-socials Python library."
thumb_file = r"C:\\path\\to\\my_thumbnail.png"
video_tags = "python,automation,coding"

# 3. Call the function
upload_youtube(
    filepath=video_file,
    title=video_title,
    image_path=YT_IMAGE_PATH,
    description=video_desc,
    thumbnail=thumb_file,
    tags=video_tags,
    monetization=True  # Set to True to enable ads and submit rating
)
```

## API Reference

### `upload_youtube(...)`

Automates the upload process to YouTube Studio.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `filepath` | `str` | **Required** | Absolute path to the video file. |
| `title` | `str` | **Required** | The title of the YouTube video. |
| `image_path` | `str` | `.../uploadyt` | Path to the folder containing your `.png` reference screenshots. |
| `description` | `str` | `None` | The text for the video description. |
| `channelurl` | `str` | `studio.youtube.com` | The starting URL. |
| `thumbnail` | `str` | `None` | Absolute path to a thumbnail image. |
| `tags` | `str` | `None` | Comma-separated string of tags. |
| `monetization`| `bool` | `False` | If `True`, performs steps to enable monetization, select "None of the above" for suitability, and submit rating. |

## Tips for Success

*   **Wait Times:** The script uses `optimiseWait` to look for images. If your internet is slow, ensure your screenshots are accurate so the script doesn't time out.
*   **Mouse Control:** Do not touch the mouse or keyboard while the script is running.
*   **Smart Paste:** This library uses a smart pasting method to handle emojis and special characters in titles and descriptions automatically.

## License

This project is licensed under the MIT License.