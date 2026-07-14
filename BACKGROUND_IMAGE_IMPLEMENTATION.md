# Background Image Implementation

## Overview
Added the Delicate Arch image as a background to the main app and to the sidebar's "About Author" section.

## Changes Made

### 1. Added Imports
```python
import base64
from pathlib import Path
```

### 2. Background Image Function
Created a helper function to convert images to base64 for CSS embedding:
```python
def get_base64_image(image_path):
    """Convert image to base64 for CSS embedding"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
```

### 3. Main Page Background
- **Image path**: `Asstes/Delicate Arch landscape with moonlight.JPG` (460KB)
- Applied as a CSS background with a white overlay (85% opacity) for readability
- **Hover effect**: Reduces overlay to 20% opacity when hovering
- Background properties:
  - `background-size: contain` - Shows full image without cropping
  - `background-position: center` - Centers the image
  - `background-repeat: no-repeat` - Prevents tiling
  - `background-attachment: fixed` - Creates parallax effect on scroll
  - `transition: 0.3s` - Smooth hover animation

### 4. Sidebar Author Image
- Same moonlight image added to the "About Author" expander
- **Rotated 90 degrees clockwise** for portrait orientation
- **Scaled to 60% size** using `scale(0.6)` transform
- **Max-width: 60%** for smaller display
- Uses `st.image()` with `use_container_width=True` for responsive sizing
- Caption: "Delicate Arch"

## Visual Effects

### Main Page (Updated)
```
Normal State:
┌─────────────────────────────────────┐
│  [Full Delicate Arch - Fitted]      │
│  + 85% white overlay                │
│                                      │
│  🌌 Governed RAG Architecture...    │
│  [Content over background]          │
│  (background-size: contain)         │
└─────────────────────────────────────┘

Hover State:
┌─────────────────────────────────────┐
│  [Full Delicate Arch - Visible]     │
│  + 20% white overlay (transparent!) │
│                                      │
│  🌌 Governed RAG Architecture...    │
│  [Image clearly visible]            │
│  (smooth 0.3s transition)           │
└─────────────────────────────────────┘
```

### Sidebar (Updated)
```
┌─────────────────┐
│ 🌌 Source of    │
│    Truth        │
│                 │
│ 📖 About Author │
│ ▼               │
│                 │
│   ┌───────┐     │  ← Rotated 90° clockwise
│   │  /\   │     │     AND scaled to 60%
│   │ /  \  │     │     (smaller size)
│   │[Arch] │     │
│   └───────┘     │
│                 │
│ Publisher:      │
│ Harshit Gola    │
└─────────────────┘
```

## Technical Details

### Why Base64 Encoding?
- Streamlit doesn't support direct file paths in CSS
- Base64 encoding embeds the image directly in the CSS
- No need for external hosting or file serving

### Background Image Settings

**background-size: contain** (Changed from cover)
- Shows the FULL image without cropping
- Adapts to screen size dynamically
- Maintains aspect ratio
- No parts of the image are cut off
- Perfect for seeing the entire Delicate Arch

**Hover Effect**
- Normal: 85% white overlay (0.85 opacity)
- Hover: 20% white overlay (0.2 opacity) - much more transparent!
- Transition: Smooth 0.3s fade effect
- User can hover over any part of the page to see the image more clearly

### Sidebar Image Rotation
- `transform: rotate(90deg) scale(0.6)` - rotates clockwise AND scales to 60% size
- `max-width: 60%` - limits maximum width for smaller display
- `margin: auto` - centers the smaller image
- `transition: transform 0.3s ease` - smooth animation
- Applied to all `.stImage img` elements
- Maintains responsive sizing while being more compact

### Error Handling
- Uses `Path.exists()` to check if image file is present
- Gracefully degrades if image is missing (app still works)
- No error thrown if Assets folder is renamed or missing

## Testing

Run the app to see the changes:
```bash
streamlit run App.py
```

### What to Check
1. ✅ Background image appears on main page
2. ✅ Background shows FULL image (not cropped) - uses `contain`
3. ✅ Background adapts to different browser window sizes
4. ✅ Text is readable over background (85% white overlay)
5. ✅ **HOVER TEST**: Move mouse over page - background becomes more transparent (20% overlay)
6. ✅ Smooth transition effect when hovering (0.3s fade)
7. ✅ Sidebar "About Author" section shows the image
8. ✅ **Sidebar image is rotated 90 degrees clockwise**
9. ✅ Image is responsive in sidebar
10. ✅ App works even if image path changes

### Interactive Features to Test

**Background Hover Effect:**
- Normal state: Image is subtle (85% white overlay)
- Hover state: Image becomes prominent (20% white overlay)
- Transition: Smooth 0.3s animation
- Works anywhere on the main page

**Sidebar Image:**
- Opens in "About Author" expander
- Image rotated 90° clockwise
- Maintains aspect ratio
- Responsive to sidebar width

## File Locations

```
/Users/harshitgola/Projects/RAG Architecture (SOT)/
├── Asstes/
│   ├── Delicate Arch horizontal.JPG           (310KB - original)
│   └── Delicate Arch landscape with moonlight.JPG  (460KB - ACTIVE background)
├── App.py                                     (modified)
├── BACKGROUND_IMAGE_IMPLEMENTATION.md         (this file)
└── IMAGE_FEATURES_UPDATE.md                   (quick reference)
```

## Future Enhancements

Consider adding:
- Option to toggle background on/off via sidebar
- Multiple background images with selection
- Adjustable opacity slider
- Different images for light/dark mode
- Animated transitions between backgrounds

## Notes

- Image file size: 310KB (reasonable for web)
- Format: JPG (good compression for photos)
- Filename has spaces (handled by Path object)
- Located in "Asstes" folder (note: possibly "Assets" typo in original folder name)
