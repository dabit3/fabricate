# 🎭 Fabricate

> **An experimental research tool for fabricating GitHub personas with AI-generated repositories**

⚠️ **This is an experimental/research project. Use responsibly and ethically.**

## Overview

Fabricate creates synthetic GitHub activity by generating:
- Multiple repositories with realistic code
- Varied commit histories spanning configurable time periods
- Code across different programming languages
- Projects of varying complexity and scope

All code is generated using Anthropic's Claude API, creating unique and realistic-looking projects.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fabricate.git
cd fabricate

# Install with uv
uv venv
source .venv/bin/activate
uv pip install -e .
```

Or run directly without activating:

```bash
uv run fabricate generate
```

## Configuration

### Required Credentials

1. **Anthropic API Key**: Get from [console.anthropic.com](https://console.anthropic.com)
2. **GitHub Personal Access Token**: Create at [github.com/settings/tokens](https://github.com/settings/tokens)
   - Required scopes: `repo`, `delete_repo` (optional, for cleanup)

### Environment Variables

Set these environment variables or pass them as CLI arguments:

```bash
export FABRICATE_ANTHROPIC_API_KEY="sk-ant-..."
export FABRICATE_GITHUB_TOKEN="ghp_..."
export FABRICATE_GITHUB_USERNAME="your-username"  # Optional, auto-detected
```

Or create a `.env` file in the project root:

```
FABRICATE_ANTHROPIC_API_KEY=sk-ant-...
FABRICATE_GITHUB_TOKEN=ghp_...
```

## Usage

### Basic Generation

```bash
# Generate with random settings (1-50 repos, random history depth)
fabricate generate

# Specify exact count and languages
fabricate generate -l python -l javascript -l rust -r 10

# Custom history depth (commits spread over 2 years)
fabricate generate -d 730

# Custom commit range per repository
fabricate generate --min-commits 10 --max-commits 50

# Specify technologies and project types
fabricate generate -l nextjs -t tailwind -t prisma -c saas

# Full-stack apps with specific stack
fabricate generate -l nextjs -t supabase -t stripe -t shadcn -c "e-commerce platform"
```

### Command Options

```
fabricate generate [OPTIONS]

Options:
  -a, --anthropic-key TEXT     Anthropic API key
  -g, --github-token TEXT      GitHub personal access token
  -l, --languages TEXT         Languages to use (can repeat)
  -r, --repos INTEGER          Number of repos (random 1-50 if not set)
  -d, --history-days INTEGER   History depth (random 30-1825 days if not set)
  -t, --tech TEXT              Technologies to use (can repeat, e.g., tailwind, prisma)
  -c, --category TEXT          Project types to build (can repeat, e.g., saas, cli_tool)
  --min-commits INTEGER        Min commits per repo (1-100)
  --max-commits INTEGER        Max commits per repo (1-100)
  -u, --github-username TEXT   GitHub username
  -w, --work-dir TEXT          Local work directory
  --no-push                    Don't push to GitHub (local only)
  --cleanup                    Remove local files after pushing
  --dry-run                    Show what would be created
```

### Other Commands

```bash
# Check GitHub connection status
fabricate status

# List existing repositories
fabricate list-repos
fabricate list-repos --prefix my-project

# Delete repositories (use with caution!)
fabricate delete repo-name-1 repo-name-2
fabricate delete --force repo-name
```

## Examples

### Create a Python-focused persona

```bash
fabricate generate \
  -l python \
  -r 8 \
  -d 365 \
  --min-commits 10 \
  --max-commits 40
```

### Multi-language developer profile

```bash
fabricate generate \
  -l python \
  -l typescript \
  -l go \
  -l rust \
  -r 15 \
  -d 730
```

### Test locally without pushing

```bash
fabricate generate \
  -l python \
  -r 2 \
  --no-push \
  -w ./test-repos
```

## How It Works

1. **Configuration**: Parse input parameters for languages, repo count, and history depth
2. **Concept Generation**: Claude generates unique project concepts with names, descriptions, and features
3. **Code Generation**: For each repository:
   - Generate initial project structure (README, config files, source code)
   - Generate 5-37 subsequent commits with incremental changes
   - Each commit includes realistic commit messages
4. **Git Operations**: Create local repos with properly timestamped commits
5. **GitHub Push**: Create remote repos and push with full history preserved

### Generated Project Types

The system creates varied projects including:
- CLI tools
- Web APIs
- Libraries/packages
- Data processing utilities
- Automation scripts
- Games
- Visualization tools
- DevOps utilities
- Machine learning projects

### Complexity Levels

- **Low**: 2-5 files, simple utilities or scripts
- **Medium**: 5-15 files, small libraries or tools
- **High**: 10-30 files, complex applications or frameworks

## Project Structure

```
fabricate/
├── fabricate/
│   ├── __init__.py
│   ├── cli.py          # Click-based CLI
│   ├── config.py       # Pydantic models and settings
│   ├── generator.py    # Anthropic code generation
│   ├── git_ops.py      # Local git operations
│   ├── github_client.py # GitHub API client
│   └── persona.py      # Main orchestrator
├── main.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Limitations

- **API Costs**: Code generation uses Anthropic API tokens
- **Rate Limits**: GitHub has rate limits for repo creation
- **Quality**: Generated code may not always compile/run correctly
- **Detection**: Patterns may be detectable with analysis

## Ethical Considerations

This tool is intended for:
- Research into AI-generated code detection
- Understanding GitHub activity patterns
- Educational purposes about code generation

**Do NOT use for:**
- Fraudulent job applications
- Deceiving others about your experience
- Any malicious purposes

## License

MIT License - See LICENSE file

## Contributing

This is an experimental research project. Issues and PRs welcome for improvements.

