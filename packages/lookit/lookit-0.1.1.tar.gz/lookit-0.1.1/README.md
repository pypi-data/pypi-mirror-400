# Lookit

LLM-first vision toolkit for GUI grounding, OCR, and more. Built with [LangChain](https://github.com/langchain-ai/langchain) and [Qwen3-VL](https://ollama.com/library/qwen3-vl). Outputs minimal plain text optimized for token efficiency.

## Quick Start

Choose your setup method:

| Method | Use Case |
|--------|----------|
| [Skills Setup](#skills-setup) | Claude Code, DeepAgents, or other agent frameworks (recommended) |
| [CLI Installation](#cli-installation) | Standalone command-line usage |

## Skills Setup

Skills are self-contained and auto-download the binary on first run. No Python or dependencies required.

| Skill | Description |
|-------|-------------|
| `computer-use` | GUI grounding for desktop screenshots |
| `mobile-use` | GUI grounding for mobile screenshots |
| `ocr` | Text extraction from screenshots |

### Prerequisites

Choose ONE backend option:

<details>
<summary>Option A: Ollama Cloud (recommended, no local setup)</summary>

1. Create an Ollama account at [ollama.com](https://ollama.com)
2. Go to [ollama.com/settings/keys](https://ollama.com/settings/keys)
3. Click "Create new key" and copy the API key

You'll use these settings:
```
LOOKIT_API_KEY=your-api-key-here
LOOKIT_MODEL=qwen3-vl:235b-cloud
LOOKIT_BASE_URL=https://ollama.com/v1
```

</details>

<details>
<summary>Option B: Ollama Local (requires local setup)</summary>

1. Install Ollama: [ollama.com/download](https://ollama.com/download)
2. Pull the model:
   ```bash
   ollama pull qwen3-vl
   ```
3. Start Ollama (runs automatically after install, or run `ollama serve`)

You'll use these settings:
```
LOOKIT_API_KEY=ollama
LOOKIT_MODEL=qwen3-vl
LOOKIT_BASE_URL=http://localhost:11434/v1
```

</details>

<details>
<summary>Option C: LM Studio (local GUI app)</summary>

1. Download LM Studio: [lmstudio.ai](https://lmstudio.ai)
2. Search and download a Qwen3-VL model (e.g., `qwen/qwen3-vl-8b`)
3. Start the local server (Server tab → Start Server)

You'll use these settings (model name uses `owner/model` format):
```
LOOKIT_API_KEY=lmstudio
LOOKIT_MODEL=qwen/qwen3-vl-8b
LOOKIT_BASE_URL=http://127.0.0.1:1234/v1
```

</details>

### Install Skills

<details>
<summary>Claude Code</summary>

**Step 1: Download skills**

```bash
# Set version to download
VERSION="0.1.1"

# Create skill directories
mkdir -p ~/.claude/skills/{computer-use,mobile-use,ocr}/{bin,config}

# Download computer-use skill
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/computer-use/SKILL.md" -o ~/.claude/skills/computer-use/SKILL.md
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/computer-use/bin/lookit" -o ~/.claude/skills/computer-use/bin/lookit
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/computer-use/config/lookit.env.example" -o ~/.claude/skills/computer-use/config/lookit.env.example
chmod +x ~/.claude/skills/computer-use/bin/lookit

# Download mobile-use skill
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/mobile-use/SKILL.md" -o ~/.claude/skills/mobile-use/SKILL.md
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/mobile-use/bin/lookit" -o ~/.claude/skills/mobile-use/bin/lookit
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/mobile-use/config/lookit.env.example" -o ~/.claude/skills/mobile-use/config/lookit.env.example
chmod +x ~/.claude/skills/mobile-use/bin/lookit

# Download ocr skill
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/ocr/SKILL.md" -o ~/.claude/skills/ocr/SKILL.md
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/ocr/bin/lookit" -o ~/.claude/skills/ocr/bin/lookit
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/ocr/config/lookit.env.example" -o ~/.claude/skills/ocr/config/lookit.env.example
chmod +x ~/.claude/skills/ocr/bin/lookit

# Create config files from examples
cp ~/.claude/skills/computer-use/config/lookit.env.example ~/.claude/skills/computer-use/config/lookit.env
cp ~/.claude/skills/mobile-use/config/lookit.env.example ~/.claude/skills/mobile-use/config/lookit.env
cp ~/.claude/skills/ocr/config/lookit.env.example ~/.claude/skills/ocr/config/lookit.env
```

**Step 2: Configure API settings**

Edit each config file with your API settings from the Prerequisites section:

```bash
# Edit each config (use any text editor: nano, vim, code, etc.)
nano ~/.claude/skills/computer-use/config/lookit.env
nano ~/.claude/skills/mobile-use/config/lookit.env
nano ~/.claude/skills/ocr/config/lookit.env
```

Example config for Ollama Cloud:
```bash
LOOKIT_API_KEY=your-api-key-here
LOOKIT_MODEL=qwen3-vl:235b-cloud
LOOKIT_BASE_URL=https://ollama.com/v1
```

**Step 3: Verify setup**

```bash
# Test the skill (downloads binary on first run)
~/.claude/skills/computer-use/bin/lookit --help
```

</details>

<details>
<summary>DeepAgents CLI</summary>

[DeepAgents](https://github.com/langchain-ai/deepagents) is an agent framework built on LangChain and LangGraph.

**Step 1: Download skills**

```bash
# Install deepagents CLI
pip install deepagents-cli

# Set version to download
VERSION="0.1.1"

# Create skill directories
mkdir -p ~/.deepagents/default/skills/{computer-use,mobile-use,ocr}/{bin,config}

# Download computer-use skill
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/computer-use/SKILL.md" -o ~/.deepagents/default/skills/computer-use/SKILL.md
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/computer-use/bin/lookit" -o ~/.deepagents/default/skills/computer-use/bin/lookit
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/computer-use/config/lookit.env.example" -o ~/.deepagents/default/skills/computer-use/config/lookit.env.example
chmod +x ~/.deepagents/default/skills/computer-use/bin/lookit

# Download mobile-use skill
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/mobile-use/SKILL.md" -o ~/.deepagents/default/skills/mobile-use/SKILL.md
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/mobile-use/bin/lookit" -o ~/.deepagents/default/skills/mobile-use/bin/lookit
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/mobile-use/config/lookit.env.example" -o ~/.deepagents/default/skills/mobile-use/config/lookit.env.example
chmod +x ~/.deepagents/default/skills/mobile-use/bin/lookit

# Download ocr skill
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/ocr/SKILL.md" -o ~/.deepagents/default/skills/ocr/SKILL.md
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/ocr/bin/lookit" -o ~/.deepagents/default/skills/ocr/bin/lookit
curl -sL "https://raw.githubusercontent.com/atom2ueki/lookit/$VERSION/skills/ocr/config/lookit.env.example" -o ~/.deepagents/default/skills/ocr/config/lookit.env.example
chmod +x ~/.deepagents/default/skills/ocr/bin/lookit

# Create config files from examples
cp ~/.deepagents/default/skills/computer-use/config/lookit.env.example ~/.deepagents/default/skills/computer-use/config/lookit.env
cp ~/.deepagents/default/skills/mobile-use/config/lookit.env.example ~/.deepagents/default/skills/mobile-use/config/lookit.env
cp ~/.deepagents/default/skills/ocr/config/lookit.env.example ~/.deepagents/default/skills/ocr/config/lookit.env
```

**Step 2: Configure API settings**

Edit each config file with your API settings from the Prerequisites section:

```bash
# Edit each config (use any text editor: nano, vim, code, etc.)
nano ~/.deepagents/default/skills/computer-use/config/lookit.env
nano ~/.deepagents/default/skills/mobile-use/config/lookit.env
nano ~/.deepagents/default/skills/ocr/config/lookit.env
```

Example config for Ollama Cloud:
```bash
LOOKIT_API_KEY=your-api-key-here
LOOKIT_MODEL=qwen3-vl:235b-cloud
LOOKIT_BASE_URL=https://ollama.com/v1
```

**Step 3: Verify setup**

```bash
# Test the skill (downloads binary on first run)
~/.deepagents/default/skills/computer-use/bin/lookit --help

# Verify skills are detected
deepagents skills list
```

</details>

<details>
<summary>Programmatic Integration</summary>

For integrating skills into your own LangChain agents, see [deepagents PR #611](https://github.com/langchain-ai/deepagents/pull/611) (WIP).

```bash
# Install in your project
pip install lookit

# Create .env file with your API settings from Prerequisites section
cat << 'EOF' > .env
LOOKIT_API_KEY=your-api-key-here
LOOKIT_MODEL=qwen3-vl:235b-cloud
LOOKIT_BASE_URL=https://ollama.com/v1
EOF
```

```python
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.middleware import SkillsMiddleware

# Create backend and skills middleware
backend = FilesystemBackend()
skills_middleware = SkillsMiddleware(
    backend=backend,
    registries=[
        {"path": "/skills/user/", "name": "user"},
        {"path": "/skills/project/", "name": "project"},
    ],
)

# Create agent with skills middleware
agent = create_deep_agent(
    model="openai:gpt-4o",
    middleware=[skills_middleware],
)

# Agent will automatically discover and use lookit skills
result = agent.invoke({
    "messages": [{"role": "user", "content": "Click the submit button in screenshot.png"}]
})
```

</details>

## CLI Installation

For standalone command-line usage (requires Python). First complete the [Prerequisites](#prerequisites) to get your API settings.

**Step 1: Install**

```bash
pip install lookit
```

**Step 2: Configure**

Add to your shell profile (`~/.zshrc` on macOS, `~/.bashrc` on Linux):

For Ollama Cloud (recommended, see [Prerequisites](#prerequisites) for API key):
```bash
export LOOKIT_API_KEY="your-api-key-here"
export LOOKIT_MODEL="qwen3-vl:235b-cloud"
export LOOKIT_BASE_URL="https://ollama.com/v1"
```

For Ollama Local (see [Prerequisites](#prerequisites) for setup):
```bash
export LOOKIT_API_KEY="ollama"
export LOOKIT_MODEL="qwen3-vl"
export LOOKIT_BASE_URL="http://localhost:11434/v1"
```

Then reload: `source ~/.zshrc`

**Step 3: Verify**

```bash
lookit --help
```

## Usage

Same screenshot, different modes and prompts = different results:

| OCR Mode | Computer Mode |
|----------|---------------|
| `lookit "extract the transaction history" -s screenshot.png --mode ocr` | `lookit "click search" -s screenshot.png --mode computer` |
| ![Screenshot](assets/example_screenshot.png) | ![Result](assets/example_result.png) |
| `Max Now Pte. Ltd.`<br>`Singapore SG`<br>`24 Dec 2025 10:07:13`<br>`SGD 70.85`<br>`140 points`<br>`Pending`<br>`...` | `left_click 2910,365` |

## Output Format

### Action Modes (computer/mobile)

```
left_click 960,324
type "hello world"
swipe 500,800 to 500,200
key Control+c
scroll -100
```

### OCR Mode

Returns extracted text directly.

## Arguments

| Argument | Description |
|----------|-------------|
| `query` | Natural language instruction |
| `-s, --screenshot` | Path to screenshot (required) |
| `-m, --mode` | `computer`, `mobile`, or `ocr` (required) |
| `--debug` | Debug mode (for humans): print info to stderr, save annotated image |

## Actions

### Computer

`left_click`, `right_click`, `double_click`, `type`, `key`, `scroll`, `mouse_move`

### Mobile

`click`, `long_press`, `swipe`, `type`, `system_button`

## License

MIT
