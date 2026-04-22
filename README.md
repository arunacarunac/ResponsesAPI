# ResponsesAPI

A simple Python client for the [Azure OpenAI Responses API](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/responses) using the official OpenAI Python SDK.

## Code Structure

```
.
├── SimpleClient.py       # Main CLI client
├── requirements.txt      # Python dependencies
└── .env-example.txt      # Environment variable template
```

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**  
   Copy `.env-example.txt` to `.env` and fill in your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   ```

## Usage

```bash
# Basic prompt
python SimpleClient.py --prompt "Say hello."

# Stream the response
python SimpleClient.py --prompt "Tell me a story." --stream

# Chain responses (follow-up explanation at freshman level)
python SimpleClient.py --prompt "Explain neural networks." --chain
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--prompt` | Yes | User prompt to send to the model |
| `--stream` | No | Stream the response as it arrives |
| `--chain` | No | Follow up with a freshman-level explanation |
