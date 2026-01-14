# Specific.ai SDK

## Installation

```bash
pip install specific-ai
```

## Quick Start

### OpenAI

```python
from specific_ai import OpenAI

# Initialize the client
client = OpenAI(
    specific_ai_url="<your-specific-ai-service-URL>",
    api_key="<your-openai-api-key>",
    use_specific_ai_inference=False,
)

# Use like regular OpenAI client with the SpecificAI additional field
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello!"}
    ],
    specific_ai={
        "task_name": "greeting",
    }
)

print(response.choices[0].message.content)
```

### Anthropic

```python
from specific_ai import Anthropic

# Initialize the client
client = Anthropic(
    specific_ai_url="<your-specific-ai-service-URL>",
    api_key="<your-anthropic-api-key>",
    use_specific_ai_inference=False,
)

# Use like regular Anthropic client with the SpecificAI additional field
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[
        {"role": "user", "content": "Hello!"}
    ],
    max_tokens=1000,
    specific_ai={
        "task_name": "greeting",
    }
)

print(response.content[0].text)
```

## Features

- 🎯 Custom-tailored models optimized for your specific use cases
- 🚀 Works with OpenAI and Anthropic APIs
- 📊 Automatic request and response logging
- 🎯 Response optimization capabilities
- 📈 Advanced analytics integration

## Core Features Explained

### Model Inference Options

The SDK offers two approaches to model inference, controlled by `use_specific_ai_inference`:

```python
client = OpenAI(
    api_key="your-key",
    use_specific_ai_inference=True  # Enable SpecificAI's optimized models
)
```

- **Standard Inference** (`use_specific_ai_inference=False`):
  - Uses the provider's models directly (OpenAI/Anthropic)
  - Standard pricing and performance
  - Data is collected for future optimization

- **Specific.ai Inference** (`use_specific_ai_inference=True`):
  - Uses task-specific models optimized for your use cases
  - Potential improvements in performance and cost
  - Automatic fallback to standard models if needed
  - Requires prior data collection for model training


### Best Practices

1. **Start with Data Collection**: 
   - Keep `use_specific_ai_inference=False` initially
   - This builds up training data for your use cases
   - Use collected data to train a specific model with Specific.ai

2. **Transition to Optimized Models**:
   - Deploy your model with Specific.ai
   - Enable `use_specific_ai_inference=True`
   - Monitor performance improvements

3. **Testing New Features**:
   - Use A/B testing between standard and optimized models
   - Compare performance metrics
   - Gradually roll out optimization to production


## Logging

This SDK uses Python's standard logging module. To capture logs from the SDK, 
configure logging in your application:

```python
import logging

# Basic console logging
logging.basicConfig(level=logging.INFO)

# Or for more detailed logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Support

Need help? Contact our support team at support@specific.ai
