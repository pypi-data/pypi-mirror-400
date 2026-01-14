# Snow Leopard SDK for Python

This repo contains the Python client library for [Snow Leopard Playground](https://try.snowleopard.ai) APIs. 

See our [API documentation](https://docs.snowleopard.ai/#api-documentation) for more details.

## Installation

```bash
pip install snowleopard
```

## Quick Start

```python
from snowleopard import SnowLeopardClient

# Initialize the client (or AsyncSnowLeopardClient)
client = SnowLeopardClient(api_key="your-api-key")

# Query your data in natural language
response = client.retrieve(user_query="How many users signed up last month?", datafile_id="your-datafile-id")
```

## Getting Started

1. **Get your API key** from [https://auth.snowleopard.ai/account/api_keys](https://auth.snowleopard.ai/account/api_keys)
2. **Upload your datafiles** at [https://try.snowleopard.ai](https://try.snowleopard.ai)
3. **Set your API key** via environment variable:
    ```bash
    export SNOWLEOPARD_API_KEY="your-api-key"
    ```
    
    Or pass it directly to the client:
    
    ```python
    SnowLeopardClient(api_key="your-api-key")
    ```

## Usage

### Synchronous Client

```python
from snowleopard import SnowLeopardClient

with SnowLeopardClient() as client:
   # Get data directly from a natural language query
   response = client.retrieve(user_query="How many superheroes are there?")
   print(response.data)

   # Stream natural language summary of live data
   for chunk in client.response(user_query="How many superheroes are there?"):
      print(chunk)
```

### Async Client

```python
from snowleopard import AsyncSnowLeopardClient

async with AsyncSnowLeopardClient() as client:
   # Get complete results
   response = await client.retrieve(user_query="How many superheroes are there?")
   print(response.data)

   # Get streaming results
   async for chunk in client.response(user_query="How many superheroes are there?"):
      print(chunk)
```

### CLI

The SDK includes a command-line interface:

```bash
pip install snowleopard
snowy retrieve --datafile <datafile-id> "How many records are there?"
snowy response --datafile <datafile-id> "Summarize the data"
```

### On Premise Customers

For our customers who have a separate deployment per dataset, you should declare <url> explicitly when creating a 
client and omit <datafile id> when querying.

Example:
```python
client = SnowLeopardClient(url="https://{your-vm-ip}:{port}", api_key="your-api-key")
response = client.retrieve(user_query="How many users signed up last month?")
```


## Contributing

For SDK developer docs and how to contribute, see [CONTRIBUTING.md](CONTRIBUTING.md)
