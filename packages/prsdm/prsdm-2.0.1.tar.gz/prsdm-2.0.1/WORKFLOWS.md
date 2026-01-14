# GitHub Actions Workflows

## Setup

### Option 1: Trusted Publishing (Recommended - like OpenAI)
1. Go to PyPI: https://pypi.org/manage/account/publishing/
2. Add a new pending publisher for your GitHub repository
3. Configure the GitHub environment in your repo:
   - Settings → Environments → New environment → Name: `pypi`
   - The workflow will use OIDC for authentication (no token needed)

### Option 2: API Token (Simpler)
1. Add `PYPI_API_TOKEN` to GitHub Secrets:
   - Settings → Secrets and variables → Actions → Repository secrets
   - New secret: `PYPI_API_TOKEN` = your PyPI token
2. Update `publish.yml` to use the token (remove trusted publishing parts)

## Workflow Files

- `.github/workflows/tests.yml` - Tests workflow
- `.github/workflows/publish.yml` - Publish workflow

## Publication Workflow

1. **Normal Commit:**
```bash
git status
git add .
git commit -m "Prepare for release"
git push
```

2. **Bump version and create tag:**

   **Recommended (using script):**
```bash
   ./release.sh patch   # Bumps patch version (0.0.4 → 0.0.5)
   # or
   ./release.sh minor   # Bumps minor version (0.0.4 → 0.1.0)
   # or
   ./release.sh major   # Bumps major version (0.0.4 → 1.0.0)
   ```

   **Manual approach:**
```bash
   uv version --bump patch
   git add pyproject.toml
   git commit -m "v0.0.4"  # Use tag name as commit message (like OpenAI)
   git tag -a v0.0.4 -m "v0.0.4"  # Create annotated tag (required for --follow-tags)
   git push --follow-tags  # Pushes commit + annotated tag in one command
   ```

   **Note on tags:**
   - `git tag v0.0.4` creates a lightweight tag (just a pointer) - won't work with `--follow-tags`
   - `git tag -a v0.0.4 -m "v0.0.4"` creates an annotated tag (includes metadata) - required for `--follow-tags`
   - `--follow-tags` only pushes annotated tags that point to commits being pushed (prevents pushing unwanted tags)
   - Reference: [Git documentation](https://git-scm.com/docs/git-push.html) and [release-it issue #43](https://github.com/release-it/release-it/issues/43)

3. **Create GitHub Release (triggers publish workflow):**
   - Go to repository → **Releases** → You should see a draft release for `v0.0.4`
   - Click **Publish release** (or edit and then publish)
   - This triggers the publish workflow automatically

4. **Check GitHub Actions:**
   - Go to your repository → **Actions** tab
   - You should see the "Publish to PyPI" workflow running
   - Wait for it to complete and verify it published successfully

## Summary

- **Regular commits/PRs** → Tests workflow (builds, no publish)
- **GitHub Releases** → Publish workflow (publishes to PyPI)

----------------------------------------------------------------

<div align="center" style="margin: 0 auto; max-width: 80%;">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="./static/logowhite.png">
      <source media="(prefers-color-scheme: light)" srcset="./static/logoblack.png">
      <img 
        src="./static/logoblack.png" 
        style="width: 300px; height: auto; margin: 20px auto;"
      >
    </picture>
</div>


<div align="center">

[![PyPI](https://img.shields.io/pypi/v/hypertic?label=pypi%20package)](https://pypi.org/project/hypertic/)

</div>

Hypertic is the fastest and easiest way to build AI agent applications. It provides a clean, simple interface for connecting models, tools, vector databases, memory, and more.

### Key Features:

1. **[Tools](https://docs.hypertic.ai/tools)**: Create custom tools with Python functions or connect to MCP servers
2. **[Memory](https://docs.hypertic.ai/memory)**: Store conversation history with in-memory, PostgreSQL, MongoDB, or Redis backends
3. **[Retriever](https://docs.hypertic.ai/retriever)**: Connect agent to your documents and data for RAG capabilities
4. **[Structured Output](https://docs.hypertic.ai/structured-output)**: Get validated, structured responses using Pydantic models or schemas
5. **[Guardrails](https://docs.hypertic.ai/guardrails)**: Add safety and validation rules to control agent behavior

Check out the [examples](https://github.com/hypertic/hypertic/tree/main/examples) to see how Hypertic works, and visit our [documentation](https://docs.hypertic.ai) to learn more.

## Get Started

To get started, set up your Python environment (Python 3.10 or newer required), and then install the Hypertic package.

### venv

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install hypertic
```

For specific model providers, install the corresponding packages:

```bash
pip install openai          # For OpenAI
pip install anthropic       # For Anthropic
pip install google-genai    # For Google Gemini
```

### uv

If you're familiar with [uv](https://docs.astral.sh/uv/), installing the package would be even easier:

```bash
uv init
uv add hypertic
```

For specific model providers:

```bash
uv add openai          # For OpenAI
uv add anthropic       # For Anthropic
uv add google-genai    # For Google Gemini
```

### Quick Start

**Sync (non-streaming):**

Use `run()` for synchronous, non-streaming responses. This returns the complete response after the agent finishes processing:

```python
from hypertic import Agent, tool
from openai import OpenAI

# Define a tool
@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"Sunny, 72°F in {city}"

# Create agent
model = OpenAI(model="gpt-4")
agent = Agent(
    model=model,
    tools=[get_weather],
    instructions="You are a helpful assistant."
)

# Use it
response = agent.run("What's the weather in San Francisco?")
print(response.content)
```

**Sync (streaming):**

Use `stream()` for synchronous streaming. This yields events in real-time as the agent generates responses, improving user experience for longer outputs:

```python
from hypertic import Agent, tool
from openai import OpenAI

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"Sunny, 72°F in {city}"

model = OpenAI(model="gpt-4")
agent = Agent(
    model=model,
    tools=[get_weather],
    instructions="You are a helpful assistant."
)

# Stream responses in real-time
for event in agent.stream("What's the weather in San Francisco?"):
    if event.type == "content":
        print(event.content, end="", flush=True)
```

**Async (non-streaming):**

Use `arun()` for asynchronous, non-streaming responses. This is ideal for concurrent operations and non-blocking I/O:

```python
import asyncio
from hypertic import Agent, tool
from openai import OpenAI

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"Sunny, 72°F in {city}"

model = OpenAI(model="gpt-4")
agent = Agent(
    model=model,
    tools=[get_weather],
    instructions="You are a helpful assistant."
)

async def main():
    response = await agent.arun("What's the weather in San Francisco?")
    print(response.content)

asyncio.run(main())
```

**Async (streaming):**

Use `astream()` for asynchronous streaming. This combines the benefits of async operations with real-time response streaming:

```python
import asyncio
from hypertic import Agent, tool
from openai import OpenAI

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"Sunny, 72°F in {city}"

model = OpenAI(model="gpt-4")
agent = Agent(
    model=model,
    tools=[get_weather],
    instructions="You are a helpful assistant."
)

async def main():
    async for event in agent.astream("What's the weather in San Francisco?"):
        if event.type == "content":
            print(event.content, end="", flush=True)

asyncio.run(main())
```

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.


## License

This project is licensed under the [Apache License 2.0](LICENSE).
