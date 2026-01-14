# Sage MCP Server

This folder contains the standalone FastAPI MCP server.

## Setup

1. Create the conda environment:

   ```bash
   conda env create -f environment.yml
   ```

2. Create your `.env` file:

   ```bash
   cp .env.example .env
   ```

3. Add your Anthropic API key to `.env`.

## Run

From `jupyter-sage-agent`:

```bash
uvicorn mcp_server.main:app --reload
```

## Terminal Tool Behavior

- Executes the command and returns `stdout`, `stderr`, and `exit_code`.
- If total output exceeds 20 lines, responses include the first 10 and last
  10 lines (per stream), set `output_truncated=true`, and include a `summary`
  of the full output.
- If total output is 20 lines or fewer, stdout/stderr are returned in full and
  no summary is added.

## LLM Summaries

- Set `ANTHROPIC_API_KEY` in `.env` to enable real summaries.
- Optional: set `ANTHROPIC_MODEL` (defaults to `claude-haiku-4-5`).
