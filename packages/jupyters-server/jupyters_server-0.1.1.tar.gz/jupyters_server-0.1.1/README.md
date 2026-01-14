# Jupyters - AI Notebook Assistant

> 🎉 **Let's keep Jupyter fun!**

Give your AI assistant deep, semantic access to Jupyter notebooks through the Model Context Protocol (MCP).

## What is Jupyters?

Jupyters is a commercial-grade MCP server that allows AI assistants (Claude, ChatGPT, Cursor, etc.) to:

- 📓 Read and write notebook cells
- ⚡ Execute code in live Jupyter kernels
- 🔍 Inspect variables with semantic understanding (DataFrames, tensors, etc.)
- 🧠 Auto-analyze errors with variable context
- 📊 Capture plots and image outputs
- 🛡️ Prevent destructive operations with safety checks

## Quick Start

### 1. Install

```bash
pip install jupyters-server
```

### 2. Configure Your AI Tool

**For Claude Desktop:**

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "jupyters": {
      "command": "jupyters-server"
    }
  }
}
```

**For Claude Code or other MCP clients:** See [documentation](https://jupyters.fun/docs).

### 3. Restart Your AI Tool

Quit and reopen Claude Desktop (or your AI client).

### 4. Try It!

Ask your AI:
```
What Jupyter tools do you have access to?
```

Then:
```
Read my notebook at /path/to/notebook.ipynb and execute the first 3 cells
```

## Features

| Feature                      | Free  | Pro ($9/mo) | Team ($29/mo) |
| ---------------------------- | ----- | ----------- | ------------- |
| Read/Write Cells             | ✅    | ✅          | ✅            |
| Execute Cells                | 5/day | Unlimited   | Unlimited     |
| Variable Inspection          | ❌    | ✅          | ✅            |
| Plot/Image Capture           | ❌    | ✅          | ✅            |
| Domain Profiles (ML/Finance) | ❌    | ❌          | ✅            |
| Auto-Error Analysis          | ✅    | ✅          | ✅            |
| Safety Checks                | ✅    | ✅          | ✅            |

## MCP Tools

Jupyters provides 16 MCP tools for notebook operations:

**Notebooks:** `read_notebook`, `create_notebook`, `read_notebook_outline`
**Cells:** `read_cell`, `update_cell`, `add_cell`, `split_cell`, `merge_cells`
**Execution:** `run_cell`, `restart_kernel`, `get_execution_order`
**Inspection:** `inspect_variable`, `read_variable_sample` (Pro+)
**Config:** `set_profile` (Team), `activate_license`, `get_server_info`

## Upgrade

Get unlimited executions and advanced features:

```bash
# Visit https://jupyters.fun/pricing to get your license key

# Then activate via your AI:
Ask your AI: "Activate my Jupyters license: CE-PRO-XXXXXXXXXX"
```

## Documentation

- 📖 Full docs: https://jupyters.fun/docs
- 💰 Pricing: https://jupyters.fun/pricing
- 🐛 Issues: https://github.com/jupytersfun/jupyters/issues
- 💬 Support: support@jupyters.fun

## Requirements

- Python 3.10+
- Jupyter kernel (ipykernel)
- MCP-compatible AI client

## License

Commercial software with free tier. See [pricing](https://jupyters.fun/pricing) for details.

---

**Let's keep Jupyter fun! 🎉**
