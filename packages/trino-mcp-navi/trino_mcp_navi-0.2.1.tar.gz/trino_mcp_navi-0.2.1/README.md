# 🚀 Trino MCP Server

[![PyPI version](https://badge.fury.io/py/trino-mcp-navi.svg)](https://badge.fury.io/py/trino-mcp-navi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A **Model Context Protocol (MCP)** server that gives AI assistants (like Claude in Cursor) direct access to query and explore Trino/Presto databases.

> 💡 **No installation required!** Just configure and run with `uvx`.

## ✨ Features

- 🔍 **Schema Discovery** - Explore schemas, tables, and columns
- 📊 **Smart Exploration** - Get schema + sample data in one call
- ⚡ **Safe Query Testing** - Automatic LIMIT for exploration queries
- 📈 **Data Profiling** - Null %, distinct counts, top values
- 💾 **Export Results** - Save to CSV, Excel, JSON, or Parquet
- 🔐 **Encryption Check** - Detect encrypted columns
- 📋 **Query History** - Find frequently used queries

## 🚀 Quick Start (3 minutes)

### Prerequisites

- **Cursor IDE** or Claude Desktop
- **Trino database** credentials

### Step 1: Install `uv` (One-time, 30 seconds)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

> 💡 `uv` is a fast Python package manager. The `uvx` command lets you run Python tools without installing them permanently.

### Step 2: Find your `uvx` path

```bash
which uvx
# Usually: ~/.local/bin/uvx (macOS/Linux) or %USERPROFILE%\.local\bin\uvx (Windows)
```

### Step 3: Configure Cursor

Open your Cursor MCP settings:

**macOS:** `~/.cursor/mcp.json`  
**Windows:** `%APPDATA%\Cursor\mcp.json`

Add this config (replace the uvx path with YOUR path from Step 2):

```json
{
  "mcpServers": {
    "trino": {
      "command": "/Users/YOUR_USERNAME/.local/bin/uvx",
      "args": ["trino-mcp-navi"],
      "env": {
        "TRINO_HOST": "your-trino-host.company.com",
        "TRINO_PORT": "443",
        "TRINO_USER": "your.email@company.com",
        "TRINO_CATALOG": "awsdatacatalog",
        "TRINO_DEFAULT_SCHEMA": "default"
      }
    }
  }
}
```

> ⚠️ **Important:** Use the **full path** to `uvx` (not just `"uvx"`). Cursor doesn't inherit your shell's PATH.

### Step 4: Restart Cursor

Restart Cursor completely (close and reopen) to load the MCP server.

### Step 5: Test Connection

In Cursor's AI chat, type:

```
Test my Trino connection
```

The AI will use `mcp_trino_test_connection` and confirm the connection.

**That's it! 🎉** No `pip install`, no cloning repos.

---

## 🔧 Configuration Options

| Environment Variable | Required | Default | Description |
|---------------------|----------|---------|-------------|
| `TRINO_HOST` | ✅ | - | Trino server hostname |
| `TRINO_PORT` | ✅ | `8080` | Server port (usually 443 for HTTPS) |
| `TRINO_USER` | ✅ | - | Your username (usually email) |
| `TRINO_PASSWORD` | ❌ | - | Password (if using basic auth) |
| `TRINO_CATALOG` | ✅ | `awsdatacatalog` | Default catalog |
| `TRINO_DEFAULT_SCHEMA` | ❌ | `default` | Default schema |
| `TRINO_HTTP_SCHEME` | ❌ | `https` | `http` or `https` |
| `TRINO_FALLBACK_HOST` | ❌ | - | Backup host if primary fails |

---

## 📋 Available Tools (18 Total)

### 🔍 Discovery Tools

| Tool | Description |
|------|-------------|
| `test_connection` | Verify Trino connectivity |
| `get_all_schemas` | List all schemas in catalog |
| `get_tables_in_schema` | List tables in a schema |
| `describe_table` | Get column definitions |
| `explore_table` | **Recommended:** Schema + sample data in one call |
| `search_catalog` | Search for tables/columns by name |

### 📊 Data Quality & Analytics

| Tool | Description |
|------|-------------|
| `profile_column` | Null %, distinct values, top 5 values |
| `profile_table` | Row count, null analysis per column |
| `get_table_stats` | Partitions, distinct values, distribution |
| `get_frequent_queries` | Find how others query this table |
| `check_encryption` | Check for encrypted columns |

### ⚡ Query Execution

| Tool | Description |
|------|-------------|
| `test_query` | Quick test with auto-LIMIT (safe) |
| `run_trino_query` | Execute query, return results |
| `save_query_results` | Execute + export to CSV/Excel/JSON/Parquet |
| `execute_sql_file` | Run SQL from a file |

### 🚀 Performance & Schema

| Tool | Description |
|------|-------------|
| `explain_query` | Get execution plan |
| `get_query_history` | Recent queries from session |
| `get_table_ddl` | SHOW CREATE TABLE |
| `compare_tables` | Compare schemas of two tables |

---

## 🎯 Example Usage

### Explore a Table

```
Show me the schema and sample data from the users table in analytics schema
```

→ AI uses `explore_table(table_name="users", schema_name="analytics")`

### Run a Query

```
Get the top 10 customers by revenue from last month
```

→ AI uses `run_trino_query` with appropriate SQL

### Profile Data Quality

```
What's the null rate for email column in customers table?
```

→ AI uses `profile_column(table_name="customers", column_name="email", schema_name="...")`

### Search for Tables

```
Find all tables with "order" in the name
```

→ AI uses `search_catalog(search_term="order", object_type="table")`

---

## ☁️ Cloud Hosting (Zero Install for Users)

Deploy the server to the cloud so users don't need to install anything!

### Deploy to Railway (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/trino-mcp-navi)

1. Click the button above or go to [railway.app](https://railway.app)
2. Connect your GitHub repo
3. Set environment variables:
   - `TRINO_HOST`, `TRINO_PORT`, `TRINO_USER`, `TRINO_CATALOG`
4. Deploy! You'll get a URL like `https://trino-mcp-navi.up.railway.app`

### Deploy to Render

1. Go to [render.com](https://render.com)
2. Create new Web Service → Connect GitHub repo
3. Use the `render.yaml` blueprint
4. Set environment variables
5. Deploy!

### After Deployment - User Config

Users add this to their Cursor `mcp.json` - **no installation needed!**

```json
{
  "mcpServers": {
    "trino": {
      "url": "https://your-deployment-url.railway.app/sse"
    }
  }
}
```

That's it! The server handles everything remotely.

---

## 🐍 Alternative: Run with Python

If you prefer not to use `uvx`:

```bash
# Install
pip install trino-mcp-navi

# Configure Cursor with python instead of uvx
{
  "mcpServers": {
    "trino": {
      "command": "python",
      "args": ["-m", "trino_mcp_navi"],
      "env": { ... }
    }
  }
}
```

---

## 🔧 Troubleshooting

### "Connection refused" Error

- Check `TRINO_HOST` is correct
- Verify `TRINO_PORT` (usually 443 for HTTPS, 8080 for HTTP)
- Ensure network/VPN access to Trino server

### "Authentication failed"

- Verify `TRINO_USER` and `TRINO_PASSWORD`
- Some Trino setups use SSO - check with your admin

### MCP Not Loading in Cursor

1. Check you have `uv` installed: `uv --version`
2. Verify the JSON syntax in `mcp.json` is valid
3. Check Cursor logs: `Help → Toggle Developer Tools → Console`
4. Restart Cursor completely

### "uvx: command not found"

Install uv first:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## 🔐 Security Notes

- **Never commit credentials** to version control
- Use environment variables for sensitive data
- The server connects via HTTPS by default
- All queries go directly to your Trino - no external services

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your Trino credentials work outside of Cursor
3. Test with a simple query: `SELECT 1`
4. Open an issue on GitHub

---

Made with ❤️ for data analysts and engineers
