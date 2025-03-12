# Running the Agentic Support Bot

This document provides detailed instructions for running the Agentic Support Bot on your system.

## Prerequisites

Before running the bot, ensure you have the following installed:

1. **Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Required Python packages**
   - Install using pip:
   ```
   python -m pip install -r requirements.txt
   ```

## Running the Bot

### Basic Usage

To run the bot with the default settings:

```bash
python support_bot.py
```

This will:
- Load the sample FAQ document (`faq.txt`)
- Process a set of predefined queries
- Show the bot's responses and how it improves them based on feedback

### Interactive Mode

To interact with the bot directly:

```bash
python demo.py --interactive
```

This allows you to:
- Ask your own questions
- See the bot's responses
- Observe how it handles simulated feedback
- Exit by typing 'exit', 'quit', or 'q'

### Using a Different Document

To use your own document:

```bash
python demo.py --document your_document.pdf
```

The bot supports both PDF and TXT files.

### Verbose Mode

For more detailed output:

```bash
python demo.py --verbose
```

This will show additional debugging information.

## Troubleshooting

### Python Not Found

If you see "Python was not found" error:

1. Make sure Python is installed
2. Add Python to your PATH environment variable
3. Try using the full path to Python:
   ```
   C:\Path\To\Python\python.exe support_bot.py
   ```

### Package Installation Issues

If you encounter errors installing packages:

1. Make sure pip is up to date:
   ```
   python -m pip install --upgrade pip
   ```

2. Install packages one by one:
   ```
   python -m pip install transformers
   python -m pip install sentence-transformers
   python -m pip install torch
   python -m pip install PyPDF2
   python -m pip install colorama
   ```

### Memory Issues

The transformer models can be memory-intensive. If you encounter memory errors:

1. Close other applications
2. Use a smaller model by modifying the code:
   - In `support_bot.py`, change the model to a smaller variant:
   ```python
   self.qa_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
   self.embedder = SentenceTransformer('paraphrase-MiniLM-L3-v2')  # Smaller model
   ```

## Example Output

When running successfully, you should see output similar to:

```
Initializing support bot...
Support bot initialized successfully with 12 document sections

Starting support bot session with 6 queries

Query 1/6: How do I reset my password?
Initial Response: click on the "Forgot Password" link on the login page
Reasoning: Found answer with confidence 0.92. High confidence in this answer.
Feedback: good

Query 2/6: What's the refund policy?
...
```

## Log File

The bot generates a log file (`support_bot_log.txt`) that contains detailed information about its operation. This can be useful for debugging or understanding how the bot makes decisions. 