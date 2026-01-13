# langchain-xbaza

LangChain integration for [Xbaza Belarus Job Market API](https://xbaza.by/api/ai) - a comprehensive data source for the Belarusian job market, companies, business opportunities, and commercial real estate.

## Installation

```bash
pip install langchain-xbaza
```

## Quick Start

```python
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain_xbaza import XbazaJobsTool, XbazaUsersTool

# Initialize tools
tools = [
    XbazaJobsTool(),
    XbazaUsersTool(),
]

# Create agent
llm = OpenAI(temperature=0)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use agent
result = agent.run("Find me IT jobs in Minsk with salary above 2000 BYN")
print(result)
```

## Available Tools

### XbazaJobsTool

Search for job listings in Belarus.

```python
from langchain_xbaza import XbazaJobsTool

tool = XbazaJobsTool()
result = tool.run(category="IT", city="Minsk", limit=10)
```

### XbazaUsersTool

Search for professionals and specialists.

```python
from langchain_xbaza import XbazaUsersTool

tool = XbazaUsersTool()
result = tool.run(query="React developer", limit=10)
```

### XbazaBusinessTool

Search for business for sale listings.

```python
from langchain_xbaza import XbazaBusinessTool

tool = XbazaBusinessTool()
result = tool.run(city="Minsk", min_price=10000, max_price=100000)
```

### XbazaPropertyTool

Search for commercial real estate.

```python
from langchain_xbaza import XbazaPropertyTool

tool = XbazaPropertyTool()
result = tool.run(property_type="OFFICE", deal_type="RENT", city="Minsk")
```

### XbazaServicesTool

Search for business services.

```python
from langchain_xbaza import XbazaServicesTool

tool = XbazaServicesTool()
result = tool.run(category="IT", city="Minsk")
```

### XbazaAnalyticsTool

Get market analytics and trends.

```python
from langchain_xbaza import XbazaAnalyticsTool

tool = XbazaAnalyticsTool()
result = tool.run(analytics_type="overview", days=30)
```

## Configuration

All tools support custom configuration:

```python
from langchain_xbaza import XbazaJobsTool

tool = XbazaJobsTool(
    base_url="https://xbaza.by/api/ai",
    user_agent="MyCustomAgent"
)
```

## Features

- ✅ **Easy Integration**: Simple LangChain tools for Xbaza API
- ✅ **Comprehensive Coverage**: Jobs, users, business, property, services, analytics
- ✅ **Type Safe**: Built with Pydantic for validation
- ✅ **Error Handling**: Graceful error handling and user-friendly messages
- ✅ **Rate Limiting**: Respects API rate limits

## API Documentation

For full API documentation, see:
- [Xbaza API Documentation](https://github.com/LabelMinsk/xbaza-ai-api/blob/main/api_documentation.md)
- [Response Examples](https://github.com/LabelMinsk/xbaza-ai-api/blob/main/RESPONSE_EXAMPLES.md)

## Requirements

- Python >= 3.8
- langchain >= 0.1.0
- langchain-core >= 0.1.0
- requests >= 2.31.0

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- **Repository**: https://github.com/LabelMinsk/langchain-xbaza
- **API**: https://xbaza.by/api/ai
- **Documentation**: https://github.com/LabelMinsk/xbaza-ai-api

