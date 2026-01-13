# WIBA Python Client

Official Python client library for the WIBA (What Is Being Argued?) argument mining API.

## 🚀 Quick Start

### Installation

```bash
pip install wiba
```

### Basic Usage

```python
from wiba import WIBA

# Initialize client
client = WIBA(api_token="your_api_token")

# Detect arguments
result = client.detect("Climate change requires immediate action.")
print(result.is_argument)  # True
print(result.confidence)   # 0.89

# Extract topics
topic = client.extract("We must invest in renewable energy now.")
print(topic.topic)  # "renewable energy"

# Analyze stance
stance = client.stance("Solar power is expensive", "renewable energy")
print(stance.stance)  # "Against"

# Discover arguments in longer text
segments = client.discover_arguments(long_text)
for segment in segments:
    print(f"Argument: {segment.text} (confidence: {segment.confidence})")
```

### Batch Processing

```python
# Process multiple texts
texts = [
    "Climate change is a serious threat.",
    "We need renewable energy sources.",
    "Nuclear power is too dangerous."
]

# Batch argument detection
results = client.detect(texts)
for result in results:
    print(f"{result.text}: {result.is_argument}")

# Process DataFrames
import pandas as pd
df = pd.DataFrame({'text': texts})
df_results = client.detect(df)
print(df_results[['text', 'is_argument', 'confidence']])
```

## 🔧 Configuration

### API Token

Get your API token from [wiba.dev](https://wiba.dev):

```python
# Using API token
client = WIBA(api_token="your_token_here")

# Using environment variable
import os
os.environ['WIBA_API_TOKEN'] = 'your_token_here'
client = WIBA()  # Will use WIBA_API_TOKEN automatically
```

### Custom Configuration

```python
from wiba import WIBA, ClientConfig

config = ClientConfig(
    api_url="https://custom.wiba.dev",
    api_token="your_token",
    log_level="DEBUG"
)

client = WIBA(config=config)
```

## 📊 Features

### Core Functions

- **`detect(texts)`** - Argument detection in text
- **`extract(texts)`** - Topic extraction from arguments
- **`stance(texts, topics)`** - Stance analysis (favor/against/neutral)
- **`discover_arguments(text)`** - Find argumentative segments in longer texts

### Input Formats

- **Single text**: `"This is an argument"`
- **List of texts**: `["Text 1", "Text 2", "Text 3"]`
- **pandas DataFrame**: DataFrame with text column
- **CSV string**: Comma-separated values

### Response Objects

All methods return structured response objects with:
- **Results**: List of prediction results
- **Metadata**: Request information and statistics
- **Confidence scores**: Model confidence for each prediction

### Advanced Features

- **Batch processing** with progress bars
- **Automatic retries** with exponential backoff
- **Connection pooling** for better performance
- **DataFrame integration** for data science workflows
- **Statistics tracking** for usage monitoring

## 🧪 Examples

Check out the [examples/](examples/) directory for:
- Basic usage examples
- Batch processing demonstrations
- DataFrame integration
- Advanced configuration
- Error handling patterns

## 🤝 Contributing

This package is part of the WIBA-ORG collaborative development setup:

1. **Report bugs**: [GitHub Issues](https://github.com/WIBA-ORG/wiba-python-client/issues)
2. **Contribute code**: See [CONTRIBUTING.md](CONTRIBUTING.md)
3. **Documentation**: Help improve our docs

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Homepage**: [wiba.dev](https://wiba.dev)
- **API Documentation**: [wiba.dev/docs](https://wiba.dev/docs)
- **Research Paper**: [Link to paper]
- **GitHub Organization**: [WIBA-ORG](https://github.com/WIBA-ORG)