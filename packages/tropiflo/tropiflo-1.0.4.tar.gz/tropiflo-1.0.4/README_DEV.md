# TropiFlow Developer Guide

User-facing CLI for Co-DataScientist - evolves ML code using LLMs.

**Dependencies:** Requires `co-datascientist-backend` running (for evolution phase)

---

## Quick Start: Testing TropiFlow

### 1. Set Up a Test Environment

Create a clean conda environment that mimics a real user's setup:

```bash
# Create environment with Python 3.12
conda create -n my_test_env python=3.12 -y
conda activate my_test_env

# Install your project's dependencies only
pip install numpy scikit-learn pandas  # example

# Install tropiflo in editable/dev mode
cd /home/ozkilim/Co-DataScientist_/co-datascientist
pip install -e .
```

**Why this matters:** This creates a clean environment without the 235+ dev packages. When tropiflo auto-generates the Dockerfile, it will only capture these minimal dependencies.

### 2. Test with a Demo

```bash
# Activate your test environment
conda activate my_test_env

# Go to any demo directory
cd /home/ozkilim/Co-DataScientist_/demos/XOR

# Run tropiflo (it will auto-detect everything!)
tropiflo run --config config.yaml
```

**What happens automatically:**
- Detects Python version from active environment
- Finds `requirements.txt` in project OR runs `pip freeze`
- Generates Dockerfile automatically
- Builds Docker container
- Runs your baseline code
- Extracts KPI from output

### 3. Expected Output

```
No Dockerfile found - auto-generating from your environment...
Docker setup generated automatically
Docker image built successfully: co-datascientist-xxxxx
Baseline result: runtime_ms=1554.0 return_code=0 stdout='KPI: 0.5\n' kpi=0.5
ERROR: Token expired  # ← Expected if backend not running
```

The "Token expired" error is **expected** when testing without the backend. The important part is that your baseline runs successfully in Docker!

---

## Project Structure for Users

Your demo/project should have:

**`your_script.py`** - Your ML code with KPI output:
```python
# Your ML code here
accuracy = model.score(X_test, y_test)
print("KPI:", accuracy)  # ← TropiFlow extracts this
```

**`requirements.txt`** - Your dependencies (RECOMMENDED for fast builds):
```txt
numpy
scikit-learn
pandas
torch
pillow
```

**Why requirements.txt is recommended:**
- 🚀 Much faster Docker builds (only installs what you need)
- 📦 Explicit control over dependencies
- 🔒 Safety: TropiFlow is automatically filtered out (even if you accidentally include it)
- 💡 Fallback: If missing, pip freeze is used (slower, includes everything)

**`config.yaml`** - How to run your code:
```yaml
mode: "local"
entry_command: "python your_script.py"
parallel: 2

# Optional: API key for backend evolution (if you want AI improvements)
# api_key: "sk_your_token_here"
# Without api_key, baseline still runs locally!
```

**That's it!** No Dockerfile needed, no Docker knowledge required, no login/logout commands.

### Engine selection (EVOLVE vs MAP-ELITES)

- Default engine: `engine: "EVOLVE_HYPOTHESIS"`.
- MAP-Elites: set `engine: "MAP_ELITES"` to explore a MAP-Elites archive instead of pure fitness selection.
- Descriptor output (MAP-Elites only): add a line to stdout with your prediction vector:
  ```python
  import json
  print("PREDICTIONS_JSON:", json.dumps(list(preds)))
  ```
  If missing, MAP-Elites falls back to a default bin; other engines ignore it.
- Internal note: the core evolutionary engine is now `EvolutionaryHypothesisEngine` (alias `EvolveHypothesisEngine`) and other engines inherit the same generation pipeline for consistency.

---

## Running with Backend

### 1. Start the Backend

Follow `co-datascientist-backend` instructions to start the backend server (usually port 8000 or 8001).

Make sure `CO_DATASCIENTIST_BACKEND_URL` in your `.env` is correct:
```bash
CO_DATASCIENTIST_BACKEND_URL=http://localhost:8000
```

### 2. Run TropiFlow

```bash
conda activate my_test_env
cd /home/ozkilim/Co-DataScientist_/demos/XOR
tropiflo run --config config.yaml
```

Now it will:
1. Run baseline (as before)
2. Connect to backend
3. Generate evolution ideas
4. Run evolved variants
5. Save best results to `co_datascientist_checkpoints/`

---

## Testing Different Demos

```bash
# XOR Demo (simple)
cd /home/ozkilim/Co-DataScientist_/demos/XOR
tropiflo run --config config.yaml

# MPPE1 Demo (with data)
cd /home/ozkilim/Co-DataScientist_/demos/MPPE1
tropiflo run --config config.yaml

# Your Custom Demo
cd /home/ozkilim/Co-DataScientist_/demos/my_demo
tropiflo run --config config.yaml
```

---

## Developer CLI Flags

### `--dev`
Enables development mode (local backend, verbose logging). Hidden from user help.

```bash
tropiflo run --config config.yaml --dev
```

### `--debug`
Shows detailed logs and verbose output. Hidden from user help.

```bash
tropiflo run --config config.yaml --debug
```

### `--no-preflight`
Skips preflight validation checks.

```bash
tropiflo run --config config.yaml --no-preflight
```

---

## KPI Extraction

TropiFlow automatically extracts KPIs from your code's output:

**Supported formats:**
```python
print("KPI:", 0.85)
print("kpi: 0.95")
print("KPI: 1.0")
```

**Folder naming:**
- `print("KPI: 0.85")` → folder named `0_85_baseline`
- `print("KPI: 1.0")` → folder named `1_baseline`
- No KPI found → folder named `baseline` (original behavior)

**Control:**
```bash
export ENABLE_KPI_FOLDER_NAMING=true   # enable (default)
export ENABLE_KPI_FOLDER_NAMING=false  # disable
```

---

## Authentication (Super Simple!)

### Option 1: Config File (Recommended)

Just add your API key to `config.yaml`:
```yaml
mode: "local"
entry_command: "python train.py"
parallel: 2
api_key: "sk_your_backend_token_here"  # For backend evolution features
```

**Benefits:**
- No login/logout commands
- No keyring complexity
- Easy to share/version control (with .gitignore)
- Clear and visible
- Works across machines

### Option 2: Environment Variable

```bash
export API_KEY="sk_your_token_here"
tropiflo run --config config.yaml
```

### Option 3: Legacy Keyring (still supported)

The old login commands still work:
```bash
tropiflo set-token  # Saves to keyring
```

**Priority order:**
1. config.yaml `api_key` (highest)
2. Environment variable `API_KEY`
3. Keyring (legacy)
4. Prompt user

### No API Key? No Problem!

Without an API key:
- ✅ Baseline runs locally
- ✅ Docker auto-generation works
- ✅ KPI extraction works
- ❌ Backend evolution disabled (you just get baseline results)

---

## MCP Server (AI Assistant Integration)

Run TropiFlow as an MCP server for Cursor or other AI clients:

```bash
tropiflo mcp-server
```

### Configure Cursor

1. Go to: `File → Preferences → Cursor Settings → MCP → Add new global MCP server`
2. Add configuration:
```json
{
  "mcpServers": {
    "CoDatascientist": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```
3. (Optional) Enable auto-run mode: `Settings → Features → Enable auto-run`
4. Reload MCP when restarting the server

---

## Publishing to PyPI

### Automated (Recommended)

The `.github/workflows/pypi-publish.yml` workflow auto-publishes when:
- A new release is created on GitHub
- Manually triggered via workflow_dispatch

**Requirements:**
- Add `PYPI_API_TOKEN` to GitHub secrets
- Version in `pyproject.toml` matches release tag

### Manual Publishing

```bash
# 1. Update version in pyproject.toml
# 2. Build package
uv build

# 3. Check package
uv run twine check dist/*

# 4. Upload to PyPI
uv run twine upload dist/*
```

Package name: `tropiflo` (install with `pip install tropiflo`)

---

## Architecture Overview

**Auto-Docker Flow:**
```
User's Project
├── your_script.py        # ML code with KPI output
├── requirements.txt      # Dependencies (optional)
└── config.yaml          # Entry command

↓ tropiflo run --config config.yaml

1. Environment Detection
   - Detect Python version from active env
   - Read requirements.txt OR run pip freeze
   - Filter out conda artifacts, editable installs

2. Docker Generation
   - Generate Dockerfile automatically
   - Generate requirements.txt if missing
   - Use python:{version}-slim base image

3. Execution
   - Build Docker image
   - Run baseline code
   - Extract KPI from output

4. Evolution (if backend running)
   - Send code to backend
   - Generate evolution ideas
   - Run variants in Docker
   - Save best results
```

**Key Files:**
- `environment_detector.py` - Detects Python version and dependencies
- `docker_generator.py` - Generates Dockerfile and requirements.txt
- `workflow_runner.py` - Orchestrates the entire flow
- `kpi_extractor.py` - Extracts KPI scores from output

---

## Troubleshooting

### "Docker image failed to build"
- Check that requirements.txt has valid package names
- Ensure no conda-specific packages (they're auto-filtered)
- Verify Python version matches your active environment

### "Baseline execution failed"
- Run your script locally first: `python your_script.py`
- Check entry_command in config.yaml matches your run command
- Verify all data files are in your project directory

### "Token expired" error
- This is expected when backend isn't running
- Your baseline still runs successfully
- Start the backend to test full evolution flow

### Docker cleanup
```bash
# Remove old co-datascientist images
docker images | grep co-datascientist | awk '{print $3}' | xargs docker rmi -f

# Remove stopped containers
docker ps -a | grep co-datascientist | awk '{print $1}' | xargs docker rm -f
```

---

## Pro Tips

1. **Always use a clean test environment** - Don't test from the dev environment with 235+ packages
2. **Test baseline locally first** - Make sure `python your_script.py` works before using tropiflo
3. **Use editable install** - `pip install -e .` means changes take effect immediately
4. **Check generated Dockerfile** - Look in `/tmp/co-datascientist-*/Dockerfile` to debug issues
5. **Start simple** - Test with XOR demo first, then move to your custom code

---

## Support

- Issues: [GitHub Issues](https://github.com/yourusername/co-datascientist/issues)
- Backend: See `co-datascientist-backend` repository
- Package: `pip install tropiflo` or `pip install -e .` for dev
