# Using n8n Workflows with Existing n8n Installation

This guide helps you use the SOMA workflows with your existing n8n installation (not Docker).

## 🚀 Quick Setup

### Step 1: Update Configuration

Edit `config.json` with your n8n connection details:

```json
{
  "n8n_url": "http://localhost:5678",
  "n8n_credentials": {
    "username": "your_username",
    "password": "your_password"
  },
  "soma_api": {
    "url": "http://localhost:8000",
    "timeout": 1800000
  }
}
```

### Step 2: Ensure SOMA API is Running

Make sure your SOMA backend is running:
```bash
python src/servers/main_server.py
```

### Step 3: Import Workflows

**Windows:**
```bash
cd n8n/scripts
import-workflows-existing-n8n.bat
```

**Linux/Mac:**
```bash
cd n8n/scripts
chmod +x import-workflows-existing-n8n.sh
./import-workflows-existing-n8n.sh
```

**Manual Import:**
1. Open n8n at `http://localhost:5678`
2. Go to "Workflows" → "Import from File"
3. Select workflow files from `workflows/` directory
4. Click "Import"

## 📋 Available Workflows

All workflows are in the `workflows/` directory:

1. **soma-tokenization-workflow.json** - Basic text tokenization
2. **soma-analysis-workflow.json** - Text analysis with metrics
3. **soma-batch-processing-workflow.json** - Batch processing for large files
4. **soma-scheduled-analysis-workflow.json** - Scheduled analysis
5. **soma-webhook-integration-workflow.json** - Flexible webhook integration
6. **soma-slack-integration-workflow.json** - Slack integration example

## 🔧 Updating Workflows

After importing, you may need to update the SOMA API URL in workflows:

1. Open workflow in n8n UI
2. Find the "SOMA API" HTTP Request node
3. Update the URL if your API is not on `localhost:8000`
4. Save and activate the workflow

## 🧪 Testing Workflows

After importing, test the workflows:

**Windows:**
```bash
cd n8n/scripts
test-workflows.bat
```

**Linux/Mac:**
```bash
cd n8n/scripts
chmod +x test-workflows.sh
./test-workflows.sh
```

## 📝 Workflow Webhook URLs

After importing workflows, n8n will provide webhook URLs. You can find them:

1. Open the workflow in n8n
2. Click on the webhook node
3. Copy the "Production URL" or "Test URL"

Example webhook URLs:
- `http://localhost:5678/webhook/tokenize`
- `http://localhost:5678/webhook/analyze`
- `http://localhost:5678/webhook/batch-process`

## 🔐 Authentication

If your n8n requires authentication:

1. Update credentials in `config.json`
2. Or pass them as command line arguments:
   ```bash
   ./import-workflows-existing-n8n.sh http://localhost:5678 your_username your_password
   ```

## 🛠️ Customization

### Changing SOMA API URL

If your SOMA API is hosted elsewhere:

1. Update `config.json` with the new API URL
2. Or manually update each workflow in n8n UI:
   - Find "SOMA API" node
   - Update URL field
   - Save workflow

### Creating Custom Workflows

1. Import a workflow as a template
2. Modify it in n8n UI
3. Export it to save your custom version

## 🆘 Troubleshooting

### Workflows Not Importing

- Check n8n is running and accessible
- Verify credentials in `config.json`
- Check n8n logs for errors
- Ensure workflow JSON files are valid

### Workflows Not Executing

- Activate workflows (toggle switch in n8n UI)
- Check webhook URLs are correct
- Verify SOMA API is running
- Check execution logs in n8n

### API Connection Errors

- Verify SOMA API is running: `curl http://localhost:8000/health`
- Check CORS settings in SOMA API
- Verify API URL in workflow nodes

## 📚 Next Steps

- Read the main [README.md](README.md) for detailed documentation
- Explore workflow examples in `workflows/` directory
- Customize workflows for your specific needs
- Create new workflows using n8n's visual editor

---

**Note:** These workflows are designed to work with your existing n8n installation. The Docker setup is optional and only needed if you want to run n8n in a container.

