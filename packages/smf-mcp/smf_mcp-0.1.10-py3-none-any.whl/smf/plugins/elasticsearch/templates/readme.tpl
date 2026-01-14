# {server_name}

SMF server with Elasticsearch integration for the `{default_index}` index.

## Setup

1. **Install dependencies:**
   ```bash
   uv add smf-mcp[elasticsearch]
   # or
   pip install smf-mcp[elasticsearch]
   ```

2. **Configure Elasticsearch connection:**
   
   Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your Elasticsearch settings:
   ```bash
   ELASTICSEARCH_HOSTS=http://localhost:9200
   ELASTICSEARCH_API_KEY=your-api-key  # Optional
   ```

3. **Start Elasticsearch** (if running locally):
   ```bash
   docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.0.0
   ```

## Usage

### Run the server:
```bash
smf run server.py
```

### Run with HTTP transport:
```bash
smf run server.py --transport http --port 8000
```

### Test with inspector:
```bash
smf inspector server.py
```

## Available Tools

The server provides these Elasticsearch tools:

- **search_tool** - Search documents in the `{default_index}` index
- **get_document_tool** - Get a document by ID
- **index_document_tool** - Index a new document
- **update_document_tool** - Update a document
- **delete_document_tool** - Delete a document
- **list_indices_tool** - List all Elasticsearch indices
- **cluster_health_tool** - Get cluster health information

## Customization

Edit `server.py` to add additional Elasticsearch tools or modify existing ones.

## Environment Variables

- `ELASTICSEARCH_HOSTS` - Elasticsearch host(s) (default: {es_hosts})
- `ELASTICSEARCH_API_KEY` - API key for authentication (optional)
- `ELASTICSEARCH_USERNAME` - Username for basic auth (optional)
- `ELASTICSEARCH_PASSWORD` - Password for basic auth (optional)
- `ELASTICSEARCH_VERIFY_CERTS` - Verify SSL certificates (default: true)
- `ELASTICSEARCH_TIMEOUT` - Request timeout in seconds
- `ELASTICSEARCH_MAX_RETRIES` - Maximum retries (default: 3)

## Documentation

- [SMF Documentation](https://github.com/guinat/smf-mcp)
- [FastMCP Documentation](https://fastmcp.wiki/)
- [Elasticsearch Python Client](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html)
