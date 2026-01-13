# 🚀 SOMA Advanced Execution Workflow - Guide

## 🌟 Features

This advanced workflow provides:

1. **Multiple Tokenizer Types**: Test and compare different tokenizers (word, character, whitespace, etc.)
2. **Comprehensive Analysis**: Calls `/analyze` endpoint for detailed metrics
3. **Compression Analysis**: Calls `/compress` endpoint for compression statistics
4. **Validation**: Validates tokenization reversibility
5. **Comparison**: Automatically compares results across different tokenizer types
6. **Batch Processing**: Process single text or multiple texts at once
7. **Detailed Statistics**: Comprehensive statistics and metrics
8. **Error Handling**: Graceful handling of optional features

---

## 📥 Import the Workflow

```powershell
cd n8n
.\IMPORT-ADVANCED.bat
```

---

## 🎯 How to Use

### Step 1: Open the Workflow

1. Open n8n: `http://localhost:5678`
2. Find **"SOMA Advanced Execution"** workflow

### Step 2: Configure Input

1. Click on **"Configure Input & Options"** node
2. Edit the code section

#### Basic Configuration:

```javascript
// INPUT: Single string OR array of strings
let userText = 'Your text here';

// PROCESSING OPTIONS
const config = {
  // Tokenizer types to test (will process with ALL and compare)
  tokenizerTypes: ['word', 'character', 'whitespace'],
  
  // Common options
  lower: false,
  drop_specials: false,
  collapse_repeats: 1,
  embedding: false,
  
  // Advanced features
  enableAnalysis: true,      // Call /analyze endpoint
  enableCompression: true,   // Call /compress endpoint
  enableValidation: true,    // Validate tokenization reversibility
  enableComparison: true      // Compare different tokenizer types
};
```

#### Multiple Texts:

```javascript
let userText = [
  "First text to process",
  "Second text to process",
  "Third text to process"
];
```

#### Single Tokenizer:

```javascript
const config = {
  tokenizerTypes: ['word'],  // Only test one tokenizer
  enableAnalysis: true,
  enableCompression: false,
  enableValidation: false,
  enableComparison: false
};
```

### Step 3: Execute

1. Click the **"Execute workflow"** button (red button at bottom)
2. Wait for processing to complete

### Step 4: View Results

Check these nodes for results:

1. **"Format Comprehensive Output"** - Detailed results for each processing
2. **"Compare Tokenizer Types"** - Comparison between different tokenizers
3. **"Final Summary"** - Complete summary with all data

---

## 📊 Output Structure

### Format Comprehensive Output

Each item contains:

```json
{
  "userInput": "Your text",
  "tokenizerType": "word",
  
  "tokenization": {
    "tokens": [...],
    "tokenCount": 10,
    "characterCount": 30,
    "processingTime": 0.5,
    "memoryUsage": 1.2,
    "compressionRatio": 0.75,
    "reversibility": true
  },
  
  "frontendCodes": [9, 3, 4, ...],
  "backendCodes": [13600, 91573, ...],
  "contentIds": [1, 2, 3, ...],
  
  "analysis": {
    "entropy": 2.5,
    "balanceIndex": 0.8,
    "mean": 5.2,
    "variance": 2.1,
    "fingerprint": {...}
  },
  
  "compression": [...],
  "validation": {...},
  
  "statistics": {
    "tokensPerChar": "0.3333",
    "charsPerToken": "3.0000",
    "compressionEfficiency": "75.00%",
    "processingSpeed": "20.00 tokens/ms",
    "memoryEfficiency": "8.33 tokens/KB"
  },
  
  "allTokenizations": [...]
}
```

### Compare Tokenizer Types

Shows comparison across different tokenizers:

```json
{
  "userInput": "Your text",
  "tokenizerCount": 3,
  "comparison": {
    "bestTokenCount": {
      "tokenizer": "word",
      "count": 10
    },
    "bestCompression": {
      "tokenizer": "character",
      "ratio": 0.85
    },
    "bestSpeed": {
      "tokenizer": "whitespace",
      "time": 0.3
    }
  },
  "allResults": [...]
}
```

### Final Summary

Complete overview:

```json
{
  "timestamp": "2024-01-01T00:00:00.000Z",
  "totalTexts": 1,
  "totalProcessings": 3,
  "comparisons": [...],
  "detailedResults": [...],
  "overallStats": {
    "totalTokens": 30,
    "totalCharacters": 90,
    "avgProcessingTime": 0.5,
    "avgCompressionRatio": 0.75
  }
}
```

---

## ⚙️ Configuration Options

### Tokenizer Types

Available options:
- `'word'` - Word-based tokenization
- `'char'` - Character-based tokenization
- `'space'` - Space-based tokenization
- `'grammar'` - Grammar-based tokenization
- `'subword'` - Subword tokenization
- `'bpe'` - Byte Pair Encoding
- `'syllable'` - Syllable-based tokenization
- `'frequency'` - Frequency-based tokenization
- `'byte'` - Byte-level tokenization

### Feature Flags

- `enableAnalysis: true/false` - Enable detailed analysis
- `enableCompression: true/false` - Enable compression analysis
- `enableValidation: true/false` - Enable reversibility validation
- `enableComparison: true/false` - Enable tokenizer comparison

### Processing Options

- `lower: true/false` - Convert to lowercase
- `drop_specials: true/false` - Drop special characters
- `collapse_repeats: 1` - Collapse repeated characters
- `embedding: true/false` - Enable embeddings

---

## 🔧 Troubleshooting

### Workflow not processing all items

- Make sure `tokenizerTypes` array has multiple items
- Check that all API endpoints are accessible

### Analysis/Compression not showing

- Check `enableAnalysis` and `enableCompression` flags
- Verify SOMA API is running on port 8000
- Check if endpoints `/analyze` and `/compress` are available

### Validation failing

- Ensure `enableValidation` is `true`
- Check that tokens can be decoded back to text

---

## 💡 Tips

1. **Start Simple**: Test with one tokenizer type first
2. **Enable Features Gradually**: Enable analysis, compression, validation one at a time
3. **Compare Results**: Use comparison feature to find best tokenizer for your use case
4. **Batch Processing**: Process multiple texts to see patterns
5. **Check Statistics**: Use statistics section to understand performance

---

## 🎯 Use Cases

1. **Tokenizer Selection**: Compare different tokenizers to choose the best one
2. **Performance Analysis**: Analyze processing time and memory usage
3. **Compression Testing**: Test compression efficiency
4. **Quality Assurance**: Validate tokenization reversibility
5. **Batch Processing**: Process multiple texts efficiently

---

Enjoy your advanced SOMA processing! 🚀

