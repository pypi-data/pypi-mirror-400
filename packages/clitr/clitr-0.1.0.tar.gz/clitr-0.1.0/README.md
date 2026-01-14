# clitr

CLI Translate - A tool to translate natural language to shell commands using LLMs.

## Installation

```bash
pip install clitr
```

## Usage

```bash
clitr "Remove everything under the directory foo/"
```

The command will be printed to the console and copied to your clipboard.

## Configuration

Set your OpenAI API key:
```bash
export OPENAI_API_KEY=sk-...
```

Or configure a local endpoint (e.g., vLLM, LMStudio). You can set this via the command line:

```bash
clitr --set-config -local_endpoint=http://127.0.0.1:1234/v1 -model=openai/qwen3-30b-a3b
```

Alternatively, you can manually edit `~/.clitr_config.json`:
```json
{
  "local_endpoint": "http://localhost:8000/v1",
  "model": "hosted_vllm/..."
}
```
