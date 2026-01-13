# SOMA FAQ: Universal File Support

## ❓ **Common Question: "Does SOMA only work on text tokenization?"**

## ✅ **Answer: NO! SOMA is a UNIVERSAL tokenization system!**

SOMA works on **EVERYTHING**, not just text:

### 🖼️ **Images**
- ✅ JPG/JPEG
- ✅ PNG
- ✅ GIF (animated and static)
- ✅ BMP
- ✅ WebP
- ✅ SVG

### 🎬 **Videos**
- ✅ MP4
- ✅ AVI
- ✅ MOV
- ✅ MKV
- ✅ WebM
- ✅ FLV

### 🎵 **Audio**
- ✅ MP3
- ✅ WAV
- ✅ FLAC
- ✅ AAC
- ✅ OGG
- ✅ M4A

### 📄 **Documents**
- ✅ PDF
- ✅ DOC/DOCX
- ✅ And more!

### 💻 **Code Files**
- ✅ Python (.py)
- ✅ JavaScript (.js)
- ✅ Java (.java)
- ✅ C/C++ (.c, .cpp)
- ✅ And 50+ more languages!

### 🔧 **Binary Files**
- ✅ Executables (.exe)
- ✅ Libraries (.dll, .so, .dylib)
- ✅ Binary data (.bin)

### 📦 **Archives**
- ✅ ZIP
- ✅ RAR
- ✅ 7Z
- ✅ TAR, GZ, BZ2

### 🌐 **ANY File Type!**
**If it's a file, SOMA can tokenize it!**

---

## 🔍 **How Does It Work?**

SOMA uses a **universal file handling system**:

1. **Reads ANY file as binary** - No file type is excluded
2. **Converts to tokenizable format** - Binary files become hex representation
3. **Tokenizes the content** - Uses byte-level or character-level tokenization
4. **Maintains full reversibility** - Original files can be reconstructed

---

## 💻 **Quick Example**

```python
from src.core.core_tokenizer import TextTokenizer

tokenizer = TextTokenizer(seed=42, embedding_bit=False)

# Tokenize an image
tokens = tokenizer.tokenize_file("photo.jpg", method="byte")

# Tokenize a video
tokens = tokenizer.tokenize_file("video.mp4", method="byte")

# Tokenize audio
tokens = tokenizer.tokenize_file("song.mp3", method="byte")

# Tokenize a GIF
tokens = tokenizer.tokenize_file("animation.gif", method="byte")

# Tokenize ANY file!
tokens = tokenizer.tokenize_file("any_file.xyz", method="byte")
```

---

## 📚 **Where's the Proof?**

1. **Code Implementation**: `src/core/core_tokenizer.py`
   - `_read_any_file()` function handles ANY file type
   - `_detect_file_type()` recognizes media extensions
   - Lines 2336-2340 explicitly list media file support

2. **Demo File**: `src/examples/demo_universal_files.py`
   - Shows examples with image.jpg, video.mp4, etc.
   - Demonstrates universal file handling

3. **Documentation**: `docs/SANTOK_UNIVERSAL_FILE_SUPPORT.md`
   - Complete guide to universal file support

---

## 🎯 **Bottom Line**

**SOMA is NOT a text-only tokenizer.**

**SOMA is a UNIVERSAL tokenization system that works on:**
- ✅ Text
- ✅ Images
- ✅ Videos
- ✅ Audio
- ✅ GIFs
- ✅ Binary files
- ✅ Executables
- ✅ Archives
- ✅ **ANY file type!**

**If someone asks you if SOMA only works on text, the answer is:**
> **"No! SOMA is universal - it works on images, videos, audio, GIFs, and ANY file type. It's not limited to text at all!"**

---

## 📖 **More Information**

- **Full Documentation**: See `docs/SANTOK_UNIVERSAL_FILE_SUPPORT.md`
- **Demo**: Run `python src/examples/demo_universal_files.py`
- **Code**: Check `src/core/core_tokenizer.py` lines 2251-2353

