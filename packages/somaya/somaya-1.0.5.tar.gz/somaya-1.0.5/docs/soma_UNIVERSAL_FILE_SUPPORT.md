# SOMA Universal File Support

## 🎯 **SOMA Works on EVERYTHING - Not Just Text!**

**SOMA is a UNIVERSAL tokenization system that handles ANY file type, not just text.**

## 📁 Supported File Types

### ✅ **Media Files** (Images, Video, Audio, GIFs)
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.svg`
- **Video**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.flv`
- **Audio**: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.m4a`
- **Documents**: `.pdf`, `.doc`, `.docx`
- **GIFs**: `.gif` (animated and static)

### ✅ **Text Files**
- `.txt`, `.md`, `.log`, `.csv`, `.json`, `.xml`, `.html`, `.css`

### ✅ **Code Files**
- `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.go`, `.rs`, `.php`, `.rb`, and more

### ✅ **Binary Files**
- `.exe`, `.dll`, `.so`, `.dylib`, `.bin`

### ✅ **Archive Files**
- `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`

### ✅ **ANY Other File Type**
- **SOMA can tokenize literally ANY file on your system!**

## 🔧 How It Works

SOMA uses a **universal file handling system** that:

1. **Reads ANY file as binary** - No file type is excluded
2. **Converts to tokenizable format** - Binary files are converted to hex representation
3. **Maintains full reversibility** - You can reconstruct the original file
4. **Auto-detects file types** - Automatically recognizes file extensions and content
5. **Handles corrupted files gracefully** - Robust error handling

## 💻 Code Implementation

The universal file handling is implemented in `src/core/core_tokenizer.py`:

```python
def _read_any_file(file_path):
    """
    UNIVERSAL FILE READER - Handles ANY file type.
    No matter what - text, binary, images, videos, executables, etc.
    """
    # Reads file as binary, converts to tokenizable format
    with open(file_path, "rb") as f:
        raw_bytes = f.read()
    
    # Converts bytes to text representation for tokenization
    text_content = _bytes_to_text_representation(raw_bytes)
    return text_content
```

## 📊 File Type Detection

SOMA automatically detects and categorizes files:

```python
# Media file extensions
media_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'mp4', 'avi', 'mp3', 'wav', 'pdf']
```

## 🚀 Usage Examples

### Tokenize an Image
```python
from src.core.core_tokenizer import TextTokenizer

tokenizer = TextTokenizer(seed=42, embedding_bit=False)
tokens = tokenizer.tokenize_file("image.jpg", method="byte")
# Works perfectly! Image is converted to hex and tokenized
```

### Tokenize a Video
```python
tokens = tokenizer.tokenize_file("video.mp4", method="byte")
# Video file is processed as binary and tokenized
```

### Tokenize Audio
```python
tokens = tokenizer.tokenize_file("audio.mp3", method="byte")
# Audio file is tokenized
```

### Tokenize a GIF
```python
tokens = tokenizer.tokenize_file("animation.gif", method="byte")
# GIF (animated or static) is tokenized
```

## 📝 Demo File

See `src/examples/demo_universal_files.py` for a complete demonstration:

```python
print("💡 EXAMPLES:")
print("  Input:  image.jpg     → Output: tokens.json")
print("  Input:  video.mp4     → Output: tokens.csv")
print("  Input:  document.pdf  → Output: tokens.xml")
print("  Input:  executable.exe → Output: tokens.txt")
print("  Input:  ANY file      → Output: ANY format")
```

## 🎯 Key Points

1. **SOMA is NOT limited to text** - It's a universal tokenization system
2. **Media files are fully supported** - Images, videos, audio, GIFs all work
3. **Binary files work perfectly** - Converted to hex representation
4. **Full reversibility maintained** - Original files can be reconstructed
5. **No file type is excluded** - If it's a file, SOMA can tokenize it

## 🔍 Proof in Code

The implementation clearly shows media support:

- **File Detection**: Lines 2336-2340 in `core_tokenizer.py` explicitly list media extensions
- **Universal Reader**: `_read_any_file()` function handles ANY file type
- **Binary Conversion**: `_bytes_to_text_representation()` converts binary to tokenizable format
- **Demo Examples**: `demo_universal_files.py` shows image.jpg, video.mp4 examples

## 📢 **Answer to Common Question**

**Q: "Does SOMA only work on text tokenization?"**

**A: NO! SOMA is a UNIVERSAL tokenization system that works on:**
- ✅ Text files
- ✅ Images (JPG, PNG, GIF, etc.)
- ✅ Videos (MP4, AVI, etc.)
- ✅ Audio (MP3, WAV, etc.)
- ✅ GIFs (animated and static)
- ✅ Binary files
- ✅ Executables
- ✅ Archives
- ✅ **ANY file type you can think of!**

SOMA doesn't discriminate - if it's a file, it can be tokenized!

