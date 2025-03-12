# Agentic Support Bot

An intelligent customer support bot that trains on documents, answers queries, and improves through feedback.

## Overview

This project implements an agentic workflow in Python that:

1. Trains on a provided document (PDF or text file)
2. Answers customer support queries based on that document
3. Refines its responses using simulated feedback
4. Demonstrates autonomy, decision-making, and iterative improvement

The bot uses natural language processing and machine learning to understand documents, find relevant information, and generate helpful responses. It then uses feedback to improve its answers over time.

## Features

- **Document Processing**: Handles both PDF and text files
- **Semantic Search**: Finds the most relevant sections of a document for a given query
- **Question Answering**: Uses transformer models to extract precise answers
- **Feedback Simulation**: Generates realistic feedback to improve responses
- **Adaptive Learning**: Adjusts internal parameters based on feedback history
- **Decision Making**: Uses different strategies to improve different types of responses
- **Detailed Logging**: Tracks all decisions and actions for analysis

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the support bot with the default FAQ document:

```bash
python support_bot.py
```

### Using Your Own Documents

1. Place your document (PDF or TXT) in the project directory
2. Modify the `document_path` variable in `support_bot.py` to point to your document
3. Run the support bot

### Customizing Queries

Modify the `sample_queries` list in `support_bot.py` to test your own queries.

## Project Structure

- `support_bot.py`: Main implementation of the support bot agent
- `feedback_simulator.py`: Simulates realistic user feedback
- `pdf_processor.py`: Advanced PDF document processing
- `faq.txt`: Sample FAQ document for testing
- `support_bot_log.txt`: Log file generated during execution

## How It Works

1. **Document Loading**: The bot loads and processes the document, splitting it into sections
2. **Query Processing**: For each query, the bot finds relevant sections using semantic search
3. **Answer Generation**: The bot uses a question-answering model to extract an answer
4. **Feedback Loop**: The bot receives feedback and adjusts its response accordingly
5. **Learning**: The bot updates its internal parameters based on feedback history

## Feedback Types

The bot can handle several types of feedback:

- **Good**: The response was helpful and accurate
- **Too Vague**: The response lacks specific details
- **Not Helpful**: The response doesn't address the user's question
- **Incorrect**: The response contains factual errors
- **Partially Correct**: The response is partly right but needs improvement

## Extending the Bot

You can extend the bot's capabilities by:

1. Adding new document types in `DocumentProcessor`
2. Implementing new feedback types in `FeedbackSimulator`
3. Creating new improvement strategies in `SupportBotAgent`
4. Enhancing the learning mechanisms

## License

This project is licensed under the MIT License - see the LICENSE file for details. 