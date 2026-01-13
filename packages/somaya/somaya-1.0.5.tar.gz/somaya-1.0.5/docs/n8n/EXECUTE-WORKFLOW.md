# 🚀 How to Execute SOMA Advanced Workflow - Complete Guide

## Quick Start

### Step 1: Make Sure Everything is Running

1. **SOMA API must be running:**
   ```powershell
   # Check if it's running
   curl.exe http://127.0.0.1:8000/
   
   # If not running, start it:
   cd n8n
   .\start.bat
   ```

2. **n8n must be running:**
   - Open browser: `http://localhost:5678`
   - Make sure you're logged in

---

## Step 2: Import/Open the Workflow

1. **If not already imported:**
   ```powershell
   cd n8n
   .\IMPORT-ADVANCED.bat
   ```

2. **In n8n:**
   - Click "Workflows" in left sidebar
   - Find "SOMA Advanced Execution" workflow
   - Click to open it

---

## Step 3: Configure Input

1. **Click on "Configure Input & Options" node** (second node)

2. **Click the "Edit" button** (or double-click the node)

3. **Edit the code section** - Find this part:

   ```javascript
   // INPUT: Single string OR array of strings
   let userText = 'Hello World! This is advanced SOMA processing.';
   
   // PROCESSING OPTIONS
   const config = {
     // Tokenizer types to test (will process with ALL and compare)
     // Available: 'word', 'char', 'space', 'grammar', 'subword', 'bpe', 'syllable', 'frequency', 'byte'
     tokenizerTypes: ['word', 'char', 'space'],
     
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

4. **Change your text:**
   ```javascript
   let userText = 'Your text here!';
   ```

   **Or use multiple texts:**
   ```javascript
   let userText = [
     "First text to process",
     "Second text to process",
     "Third text to process"
   ];
   ```

5. **Adjust tokenizer types** (optional):
   ```javascript
   tokenizerTypes: ['word', 'char'],  // Test only these two
   ```

6. **Enable/disable features** (optional):
   ```javascript
   enableAnalysis: true,      // Set to false to skip analysis
   enableCompression: true,   // Set to false to skip compression
   enableValidation: true,    // Set to false to skip validation
   enableComparison: true      // Set to false to skip comparison
   ```

7. **Click "Save" or close the editor**

---

## Step 4: Execute the Workflow

### Method 1: Execute Button (Recommended)

1. **Click the red "Execute workflow" button** at the bottom of the screen
   - Or press `Ctrl + Enter` (Windows) / `Cmd + Enter` (Mac)

2. **Wait for execution to complete**
   - You'll see nodes turning green as they execute
   - Green checkmark = success
   - Red X = error

3. **Check execution progress:**
   - Watch the nodes execute from left to right
   - Each node will show "Success" or "Error" when done

---

### Method 2: Execute from Node

1. **Right-click on any node**
2. **Select "Execute Node"**
3. **This will execute from that node onwards**

---

## Step 5: View Results

### Check Each Node Output:

1. **Click on any node** to see its output:
   - **"SOMA Tokenize"** - Shows tokenization results
   - **"SOMA Analyze"** - Shows analysis results (if enabled)
   - **"SOMA Compress"** - Shows compression results (if enabled)
   - **"SOMA Validate"** - Shows validation results (if enabled)
   - **"Format Comprehensive Output"** - Shows formatted results
   - **"Compare Tokenizer Types"** - Shows comparison between tokenizers
   - **"Final Summary"** - Shows complete summary

2. **Click "Output" tab** in the node panel to see data

---

### Final Summary Output

**Click on "Final Summary" node** to see:

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

## Step 6: Understanding the Workflow Flow

The workflow executes in this order:

1. **Manual Trigger** → Starts the workflow
2. **Configure Input & Options** → Prepares your input
3. **Prepare Tokenize Body** → Creates JSON for tokenize API
4. **SOMA Tokenize** → Calls `/tokenize` endpoint
5. **Check Analysis Enabled** → Decides if analysis should run
   - If `true` → Runs analysis
   - If `false` → Skips to merge
6. **SOMA Analyze** → Calls `/analyze` endpoint (if enabled)
7. **Check Compression Enabled** → Decides if compression should run
   - If `true` → Runs compression
   - If `false` → Skips to merge
8. **SOMA Compress** → Calls `/compress` endpoint (if enabled)
9. **Merge All Results** → Combines all results
10. **Check Validation Enabled** → Decides if validation should run
11. **SOMA Validate** → Calls `/validate` endpoint (if enabled)
12. **Format Comprehensive Output** → Formats all data nicely
13. **Compare Tokenizer Types** → Compares different tokenizers
14. **Final Summary** → Creates complete summary

---

## Troubleshooting

### ❌ Error: "The service was not able to process your request"

**Solution:**
- Make sure SOMA API is running: `curl.exe http://127.0.0.1:8000/`
- If not running, start it: `cd n8n && .\start.bat`

### ❌ Error: "JSON parameter needs to be valid JSON"

**Solution:**
- This is already fixed in the latest workflow
- Re-import the workflow: `.\IMPORT-ADVANCED.bat`

### ❌ Error: "Unknown tokenizer type"

**Solution:**
- Check available tokenizers: `['word', 'char', 'space', 'grammar', 'subword', 'bpe', 'syllable', 'frequency', 'byte']`
- Make sure you're using correct names (not 'character' or 'whitespace')

### ❌ Workflow not executing

**Solution:**
- Make sure workflow is saved
- Check that all nodes are connected properly
- Try clicking "Execute workflow" button again

### ❌ Some nodes showing errors

**Solution:**
- Check if the feature is enabled in config
- If `enableAnalysis: false`, analysis nodes will be skipped (this is normal)
- If `enableCompression: false`, compression nodes will be skipped (this is normal)
- If `enableValidation: false`, validation nodes will be skipped (this is normal)

---

## Example Configurations

### Simple: Single Text, One Tokenizer

```javascript
let userText = 'Hello World!';
const config = {
  tokenizerTypes: ['word'],
  enableAnalysis: false,
  enableCompression: false,
  enableValidation: false,
  enableComparison: false
};
```

### Advanced: Multiple Texts, Multiple Tokenizers

```javascript
let userText = [
  "First text",
  "Second text",
  "Third text"
];
const config = {
  tokenizerTypes: ['word', 'char', 'space'],
  enableAnalysis: true,
  enableCompression: true,
  enableValidation: true,
  enableComparison: true
};
```

### Full Analysis: Everything Enabled

```javascript
let userText = 'Your text here!';
const config = {
  tokenizerTypes: ['word', 'char', 'space', 'grammar', 'subword'],
  lower: false,
  drop_specials: false,
  collapse_repeats: 1,
  embedding: false,
  enableAnalysis: true,
  enableCompression: true,
  enableValidation: true,
  enableComparison: true
};
```

---

## Tips

1. **Start Simple:** Begin with one tokenizer and one text
2. **Enable Features Gradually:** Enable one feature at a time to see what each does
3. **Check Node Outputs:** Click on nodes to see intermediate results
4. **Use Final Summary:** The "Final Summary" node has all the data you need
5. **Save Your Config:** Keep your configuration code for reuse

---

## Quick Reference

| Step | Action | Location |
|------|--------|----------|
| 1 | Start SOMA API | Run `.\start.bat` |
| 2 | Open n8n | `http://localhost:5678` |
| 3 | Open workflow | Workflows → SOMA Advanced Execution |
| 4 | Configure input | Click "Configure Input & Options" node |
| 5 | Edit code | Change `userText` and `config` |
| 6 | Execute | Click red "Execute workflow" button |
| 7 | View results | Click "Final Summary" node |

---

**That's it! Your workflow should now execute from start to finish! 🎉**

