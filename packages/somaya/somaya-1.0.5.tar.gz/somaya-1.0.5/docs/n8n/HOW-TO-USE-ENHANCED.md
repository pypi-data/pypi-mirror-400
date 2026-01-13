# 🚀 How to Use Enhanced SOMA Workflow

## Quick Start

### Method 1: Edit the Code Node (Easiest)

1. **Import the workflow** (if not already done):
   ```powershell
   cd n8n
   .\IMPORT-ENHANCED.bat
   ```

2. **Open n8n**: `http://localhost:5678`

3. **Open "SOMA Enhanced Execution" workflow**

4. **Click on "Get User Input" node** (second node)

5. **Edit the code** - Change this line:
   ```javascript
   const userText = 'Hello World!';
   ```
   To your text:
   ```javascript
   const userText = 'Your text here!';
   ```

6. **Click "Execute workflow"** button (red button at bottom)

7. **View output** in "Format All Outputs" node

---

### Method 2: Add Input via Manual Trigger

1. **Click "Execute workflow"** button

2. **Click on "Manual Trigger" node** in the execution view

3. **Click "Add Input"** button

4. **Enter JSON**:
   ```json
   {
     "text": "Your text here!",
     "tokenizer_type": "word"
   }
   ```

5. **Click "Execute workflow"** again

6. **View output** in "Format All Outputs" node

---

### Method 3: Edit During Execution

1. **Click "Execute workflow"**

2. **Click on "Get User Input" node** in the execution panel

3. **Click "Edit"** button

4. **Change the text** in the code:
   ```javascript
   const userText = 'Your new text!';
   ```

5. **Execute** - The workflow will continue with your new text

---

## What You'll See in Output

Click on **"Format All Outputs"** node to see:

- **`userInput`** - Your original text
- **`finalInput`** - Processed text  
- **`frontendCodes`** - Array of frontend codes
- **`backendCodes`** - Array of backend codes
- **`allTokenizations`** - Complete token data with all codes
- **`tokens`** - Token texts
- **`tokenCount`** - Number of tokens
- **`processingTime`** - Processing time in ms

---

## Tips

- **Quick edit**: Method 1 is fastest - just edit the code node before executing
- **Multiple runs**: After editing, you can execute multiple times without re-editing
- **Save workflow**: After editing, save the workflow to keep your default text

