# AI CLI Assistant (LLM Powered)

AI-powered command-line assistant that converts natural language into safe shell commands using Gemini LLM with human-in-the-loop confirmation.

## 🚀 Quick Start

### Install via pip
```bash
pip install ai-cli-llm==2.0.1
```

### Set your API Key

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "your_api_key_here"
```

**Linux/macOS:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

> Get your free Gemini API key at [ai.google.com](https://ai.google.com)

### Run the CLI
```bash
python -m ai_cli.main
```

### Fallback Mode (Offline)
You can switch to offline fallback mode at any time by typing:
```bash
/mode fallback
```
This disables LLM and uses pattern-based command generation locally (no API required).

That's it! Start typing natural language commands like:
- `create folder named projects`
- `show all files`
- `delete test.txt`
- `/mode fallback` (to switch to offline mode)

---

## Features

✨ **Core Capabilities**
- 🤖 **Natural Language Processing**: Describe what you want to do in plain English
- 🧠 **LLM-Powered Command Generation**: Uses Gemini API to generate accurate shell commands
- 🔒 **Safety First**: Built-in risk assessment and execution approval workflow
- 🔄 **Undo/Rollback**: Revert executed commands with automatic backup management
- 📋 **Multi-Step Planning**: Execute complex workflows with automatic plan generation
- 💾 **Context Memory**: Maintains conversation context across sessions

🔧 **Advanced Features**
- 🎯 **Intent Recognition**: NLP-based command categorization (file ops, system, dev, etc.)
- 🚀 **Fallback Generator**: Pattern-based command generation when API unavailable
- 📊 **Execution Tracking**: Full history of executed commands with timestamps
- ⚙️ **Smart Autocomplete**: Context-aware command suggestions
- 🌐 **Multi-LLM Support**: Works with Gemini API or local Ollama instances

## Installation (From Source)

### Prerequisites
- **Python 3.10+**
- **Google Gemini API Key** (free tier available at [ai.google.com](https://ai.google.com))
- **PowerShell** (Windows) or **Bash** (Linux/macOS)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-cli.git
   cd ai-cli
   ```

2. **Install the package**
   ```bash
   pip install -e .
   ```

3. **Configure environment**
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_api_key_here
   # Optional: for Ollama fallback
   OLLAMA_API_URL=http://localhost:11434
   ```

   Get your free Gemini API key:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key
   - Paste it in your `.env` file

4. **Verify installation**
   ```bash
   python -m ai_cli.main
   ```

## Usage

### Interactive Mode

```bash
ai-cli
```

You can switch between LLM and fallback modes at any time:
```
> /mode fallback   # Switch to offline mode
> /mode llm        # Switch back to Gemini LLM
```

Then describe what you want to do:
```
> Clean up all .pyc files in the project
Generated command: find . -name "*.pyc" -type f -delete
Safe to execute? (y/n): y
✓ Command executed successfully
```

### Supported Commands

**File Operations**
```
> Create a backup of my config file
> Delete all temporary files
> Find files larger than 100MB
> Rename all .txt files to .bak
```

**System Management**
```
> Show disk usage
> Kill process on port 8080
> Restart the Docker service
```

**Development**
```
> Install dependencies from requirements.txt
> Build and test the project
> Format all Python files
```

### Command Flow

1. **Input** → Natural language description
2. **Parse** → Intent recognition and command mapping
3. **Generate** → LLM creates the actual command
4. **Review** → Risk assessment with execution approval
5. **Execute** → Command runs with output capture
6. **Track** → Stores for undo/history

## Safety Features

### Risk Assessment
Commands are automatically classified by risk level:

- 🟢 **LOW**: Read operations, non-destructive
- 🟡 **MEDIUM**: File modifications, package installations
- 🔴 **HIGH**: System changes, destructive operations

### Approval Workflow
```
Generated command: rm -rf /important/directory
⚠️  HIGH RISK: Destructive file operation
Estimated impact: Permanent deletion
Safe to execute? (y/n): n
❌ Command blocked by user
```

### Undo Capability
```
> undo
Recent commands:
1. mv file.txt file.bak ✓
2. rm oldfile.py ✓
Undo which? (1): 1
✓ Command reverted: file.bak → file.txt
```

## Command History

AI CLI now tracks all commands executed in its own internal history file (`ai_cli_history.txt`).

- To view your AI CLI command history, type:

  ```
  show ai-cli history
  ```

- This will display a numbered list of all commands run via the AI CLI (not PowerShell session history).

- The history file is stored in the project root and is persistent across sessions.

## Project Structure

```
ai-cli/
├── ai_cli/
│   ├── main.py                 # Entry point and CLI loop
│   ├── llm_generator.py        # Gemini API integration & fallback
│   ├── executor.py             # Command execution engine
│   ├── safety.py               # Risk assessment module
│   ├── planner.py              # Multi-step plan execution
│   ├── undo_manager.py         # Undo/rollback functionality
│   ├── context_manager.py      # Context and history tracking
│   ├── intent_parser.py        # NLP intent recognition
│   ├── command_mapper.py       # Intent → command mapping
│   └── autocomplete.py         # Tab completion support
├── setup.py                    # Package configuration
├── .env                        # API keys (not in git)
├── .gitignore                  # Git ignore patterns
└── README.md                   # This file
```

## Configuration

### Environment Variables

```env
# Required
GEMINI_API_KEY=sk_...

# Optional
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral
SAFETY_LEVEL=medium  # low, medium, high
HISTORY_SIZE=100
DEBUG=false
```

## Architecture

### Command Generation Flow
```
User Input
    ↓
Intent Parser (NLP)
    ↓
Intent → Command Mapper
    ↓
LLM Generator (Gemini API)
    ↓
Fallback Generator (if needed)
    ↓
Safety Assessment
    ↓
User Approval
    ↓
Executor
```

### Undo System
- Maintains command history with metadata
- Tracks file state changes
- Generates reverse commands automatically
- Supports multi-command rollback

## API Keys & Security

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key to your `.env` file
4. **Never commit `.env` to git** (already in `.gitignore`)

### Free Tier Limits
- **100 requests per minute** (sufficient for interactive use)
- **15 requests per day** for batch operations
- Upgrade to paid plan for higher limits

## Troubleshooting

### "API Key not found"
```bash
# Check .env exists and has GEMINI_API_KEY
cat .env
```

### "No module named 'spacy'"
```bash
# Install NLP dependencies
pip install spacy
python -m spacy download en_core_web_sm
```

### Commands taking too long
- Check API rate limits
- Switch to Ollama for instant generation (local)
- Use fallback generator for common commands

### Undo not working
- Check undo history: `ai-cli --history`
- Ensure backup files exist in `.ai-cli-backups/`

## Advanced Usage

### Batch Mode
```bash
echo "Find all .log files" | ai-cli --batch
```

### Dry Run (preview only)
```bash
ai-cli --dry-run
> Clean up temp files
[DRY RUN] rm -rf /tmp/*.log
No commands executed
```

### View History
```bash
ai-cli --history
```

### Clear History
```bash
ai-cli --clear-history
```

## Contributing

Contributions welcome! Areas for improvement:
- [ ] Cross-platform command support (Windows/Linux/macOS)
- [ ] More fallback patterns for common operations
- [ ] Integration with other LLMs (Claude, GPT-4)
- [ ] Web UI dashboard
- [ ] Docker container support

## Limitations & Known Issues

⚠️ **Important Notes**
- Commands are OS-specific (PowerShell on Windows, Bash on Linux/macOS)
- Some complex multi-step operations may require manual execution
- API rate limits apply during batch operations
- Undo only works for tracked file operations

## Dependencies

```
google-generativeai>=0.3.0   # Gemini API
requests>=2.28.0             # Ollama API
python-dotenv>=0.19.0        # .env support
spacy>=3.0.0                 # NLP (optional)
```

## License

MIT License - Feel free to use, modify, and distribute.

## Support

- 📧 **Issues**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions
- 📚 **Documentation**: See ADVANCED_FEATURES.md

## Roadmap

- [x] Basic command generation
- [x] Safety checks
- [x] Undo functionality
- [ ] Web interface
- [ ] Database backend for history
- [ ] Custom command templates
- [ ] Multi-user support
- [ ] Cloud sync

---

**Made with ❤️ for command-line enthusiasts**


