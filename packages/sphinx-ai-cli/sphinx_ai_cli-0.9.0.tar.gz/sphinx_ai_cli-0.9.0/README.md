## 🚀 Quick Start

```bash
# Start Sphinx CLI (interactive mode by default)
sphinx-cli
```

## 🎨 Interactive Mode (Default)

Running `sphinx-cli` starts an interactive terminal-based chat interface similar to Claude Code or Cursor agent:

### Features:
- **Notebook Selection**: Automatically scans your directory for `.ipynb` files and lets you choose one
- **Notebook Creation**: Prompts to create a new notebook if none are found in your directory
- **Beautiful UI**: Clean terminal interface with minimal design
- **Thinking Indicators**: Shows cycling verbs in dim cyan while Sphinx processes (Thinking, Analyzing, Processing, Debugging, etc.)
- **Conversational Chat**: Type natural language prompts and get responses
- **Real-time Feedback**: See processing status with animated indicators

### Usage:
```bash
# Start interactive mode (default - will prompt for notebook selection or creation)
sphinx-cli

# Start with a specific notebook (creates it if it doesn't exist)
sphinx-cli --notebook-filepath ./my-notebook.ipynb

# Use with existing Jupyter server
sphinx-cli --jupyter-server-url http://localhost:8888 --jupyter-server-token your_token
```

### In Interactive Mode:
- Type your questions naturally at the `>` prompt
- See real-time thinking indicators while Sphinx works
- Type `exit` to end the session
- Press `Ctrl+C` to interrupt at any time

## 📋 Commands

- `sphinx-cli` - Start interactive chat mode (default)
- `sphinx-cli login` - Authenticate with Sphinx (opens web browser)
- `sphinx-cli logout` - Clear stored authentication tokens
- `sphinx-cli status` - Check authentication status
- `sphinx-cli chat --notebook-filepath <path> --prompt <prompt>` - Run a single non-interactive chat