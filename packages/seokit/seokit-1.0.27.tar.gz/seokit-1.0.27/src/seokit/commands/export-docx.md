Export markdown file to DOCX format.

## Usage

/export-docx [markdown-file]

## Examples

```bash
/export-docx ./keyword-slug/article.md
/export-docx ./docs/guide.md
```

---

## Error Codes Reference

| Code | Description | Suggestion |
|------|-------------|------------|
| `INPUT_MISSING_FILE` | No file path provided | Specify file: `/export-docx ./path/to/file.md` |
| `INPUT_FILE_NOT_FOUND` | Markdown file not found | Check file path |
| `VENV_NOT_FOUND` | Python venv not found | Run: `seokit setup` |
| `DOCX_GENERATOR_NOT_FOUND` | Generator script missing | Run: `seokit setup` |
| `DOCX_EXEC_ERROR` | DOCX export failed | Check python-docx installed |

---

## Step 1: Validate Input

```bash
if [ -z "$1" ]; then
  echo "[INPUT_MISSING_FILE] No markdown file provided"
  echo "Usage: /export-docx [markdown-file]"
  echo "Example: /export-docx ./keyword-slug/article.md"
  exit 1
fi

INPUT_FILE="$1"

if [ ! -f "$INPUT_FILE" ]; then
  echo "[INPUT_FILE_NOT_FOUND] File not found: $INPUT_FILE"
  exit 1
fi

echo "[OK] Found: $INPUT_FILE"
```

---

## Step 2: Export to DOCX

```bash
export SEOKIT_HOME="${SEOKIT_HOME:-$HOME/.claude/seokit}"
VENV_PATH="$SEOKIT_HOME/venv/bin/activate"
DOCX_GENERATOR="$SEOKIT_HOME/scripts/docx-generator.py"

# Check venv
if [ ! -f "$VENV_PATH" ]; then
  echo "[VENV_NOT_FOUND] Python venv not found: $VENV_PATH"
  echo "Suggestion: Run 'seokit setup'"
  exit 1
fi

# Check generator
if [ ! -f "$DOCX_GENERATOR" ]; then
  echo "[DOCX_GENERATOR_NOT_FOUND] Generator not found: $DOCX_GENERATOR"
  echo "Suggestion: Run 'seokit setup'"
  exit 1
fi

# Run generator
source "$VENV_PATH"
python "$DOCX_GENERATOR" "$INPUT_FILE"
DOCX_EXIT=$?

if [ $DOCX_EXIT -ne 0 ]; then
  echo "[DOCX_EXEC_ERROR] Export failed with exit code: $DOCX_EXIT"
  exit 1
fi
```

---

## Step 3: Report Result

```bash
OUTPUT_FILE="${INPUT_FILE%.md}.docx"
echo ""
echo "## Export Complete"
echo "- **Input**: $INPUT_FILE"
echo "- **Output**: $OUTPUT_FILE"
```
