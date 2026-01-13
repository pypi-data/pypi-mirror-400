# Directory-Aware Verification: Council Reviews Entire Directories

*Published: January 2026*

---

When you ask the LLM Council to verify `docs/`, what should it see?

Before v0.23.0, it saw this:

```
040000 tree abc123   adr
100644 blob def456   api.md
040000 tree ghi789   blog
...
```

A git tree listing. Not exactly useful for reviewing documentation quality. The council models correctly identified the problem:

> "This review can only assess the directory structure, not the actual documentation content." - All 3 models

This post explains how directory expansion solves this problem by automatically expanding directory paths to their constituent text files.

## The Problem: Tree Listings vs File Contents

The verification API uses `git show {commit}:{path}` to fetch file contents. For files, this works perfectly. For directories, git returns a tree listing—metadata about what's inside, not the actual content.

```python
# Before v0.23.0
content = await _fetch_file_at_commit_async(snapshot_id, "docs/")
# Returns: "040000 tree abc123  adr\n100644 blob def456  api.md\n..."
```

Council models are smart enough to recognize insufficient context. They'd return UNCLEAR verdicts with helpful messages like "Without actual file contents, it is impossible to verify..."

Helpful, but not what you want when running verification in CI/CD.

## The Solution: Smart Directory Expansion

Now when you specify a directory path, the API automatically:

1. **Detects directories** using `git cat-file -t`
2. **Lists files recursively** using `git ls-tree -rz`
3. **Filters to text files** using an 80+ extension whitelist
4. **Excludes garbage** like `package-lock.json`
5. **Caps at 100 files** to prevent token overflow

```python
# After v0.23.0
files, truncated, warnings = await _expand_target_paths(snapshot_id, ["docs/"])
# Returns: (["docs/api.md", "docs/intro.md", ...], False, [])
```

Each file is then fetched individually, producing actual reviewable content.

## Implementation Details

### Git Object Type Detection

First, we need to know if a path is a file or directory:

```python
async def _get_git_object_type(snapshot_id: str, path: str) -> Optional[str]:
    """Returns 'blob' for files, 'tree' for directories, None for not found."""
    proc = await asyncio.create_subprocess_exec(
        "git", "cat-file", "-t", f"{snapshot_id}:{path}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return stdout.decode().strip() if proc.returncode == 0 else None
```

### Safe Filename Parsing with Mode Filtering

Git filenames can contain spaces, newlines, and other special characters. The `-z` flag gives us NUL-delimited output that's safe to parse. Critically, we parse the file mode to filter out symlinks and submodules:

```python
async def _git_ls_tree_z_name_only(snapshot_id: str, tree_path: str) -> List[str]:
    """
    List files recursively, parsing modes to apply security filters.

    We do NOT use --name-only because we need the mode (100644 vs 120000).
    Output format: <mode> <type> <hash>\t<path>\0
    """
    proc = await asyncio.create_subprocess_exec(
        "git", "ls-tree", "-rz",  # Recursive, NUL-delimited
        f"{snapshot_id}:{tree_path}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()

    files = []
    for entry in stdout.decode().split("\0"):
        if not entry.strip():
            continue

        # Parse: "100644 blob abc123\tfilename"
        parts = entry.split("\t", 1)
        if len(parts) != 2:
            continue

        metadata, file_path = parts
        mode_parts = metadata.split(" ")
        mode = mode_parts[0]
        obj_type = mode_parts[1]

        # Security: Skip symlinks (120000) and submodules (160000)
        if mode in ("120000", "160000"):
            continue

        # Only include blobs (files), not trees (directories)
        if obj_type != "blob":
            continue

        files.append(f"{tree_path}/{file_path}")

    return files
```

**Key security detail**: We parse the full `ls-tree` output (not `--name-only`) because we need the mode field to identify and skip symlinks and submodules.

### Text File Filtering

Not all files should be included. Binary files waste tokens and confuse the review. We use an extension whitelist with special handling for extensionless files:

```python
TEXT_EXTENSIONS = frozenset({
    # Source code
    ".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".cpp", ".rb",
    # Config
    ".json", ".yaml", ".yml", ".toml", ".xml", ".ini",
    # Documentation
    ".md", ".rst", ".txt",
    # Build files (by extension)
    ".dockerfile", ".makefile",
    # And 70+ more...
})

GARBAGE_FILENAMES = frozenset({
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "poetry.lock", "Cargo.lock", "go.sum",
    # Lock files that add noise without value
})

# Special handling for extensionless files
def _is_text_file(file_path: str) -> bool:
    name = Path(file_path).name.lower()
    suffix = Path(file_path).suffix.lower()

    # Handle extensionless files by name
    if not suffix and name in {"makefile", "dockerfile", "jenkinsfile", "cmakelists"}:
        return True

    return suffix in TEXT_EXTENSIONS
```

This ensures important configuration files like `Makefile`, `Dockerfile`, and `Jenkinsfile` are included even though they lack file extensions.

### Truncation and Warnings

Large directories can have thousands of files. We cap at 100 with **deterministic alphabetical sorting** for reproducible CI/CD results:

```python
MAX_FILES_EXPANSION = 100

# Files are processed in alphabetical order for determinism
expanded_files = sorted(expanded_files)

if len(expanded_files) >= MAX_FILES_EXPANSION:
    truncated = True
    warnings.append(
        f"Truncated at {MAX_FILES_EXPANSION} files. "
        "List sorted alphabetically for reproducibility."
    )
    expanded_files = expanded_files[:MAX_FILES_EXPANSION]
```

**Why alphabetical?** This ensures that the same directory always produces the same file list, making verification results deterministic across CI/CD runs.

The response now includes expansion metadata for transparency:

```json
{
  "verdict": "pass",
  "confidence": 0.85,
  "expanded_paths": ["docs/api.md", "docs/intro.md", "docs/guide.md"],
  "paths_truncated": false,
  "expansion_warnings": []
}
```

## Security Considerations

### Symlinks

Symlinks (mode 120000) are skipped to prevent:
- Path traversal attacks
- Infinite cycles
- Repository escape

### Submodules

Submodules (mode 160000) are skipped because:
- They're separate repositories
- The snapshot ID doesn't apply to them
- Their content may not be available

### DoS Protection

The existing protections still apply:
- MAX_FILE_CHARS (15,000) per file
- MAX_TOTAL_CHARS (50,000) total
- Semaphore limiting (10 concurrent git ops)
- Streaming reads with early termination

## Usage Examples

### Verify Documentation

```python
result = await verify(
    snapshot_id="abc1234",
    target_paths=["docs/"],
    rubric_focus="Documentation"
)
# Council now sees actual markdown content, not tree listing
```

### Mixed Files and Directories

```python
result = await verify(
    snapshot_id="abc1234",
    target_paths=["README.md", "src/api/", "docs/"],
)
# All paths expanded to files, deduplicated, sorted alphabetically
```

### Via MCP

```bash
llm-council verify abc1234 --paths docs/ --focus documentation
```

### Via Claude Code Skills

```bash
/council-verify --snapshot HEAD --paths docs/
```

## Performance

Directory expansion adds one git call per directory (to detect type) plus one `ls-tree` call. Both are fast operations:

| Operation | Typical Time |
|-----------|-------------|
| `git cat-file -t` | ~5ms |
| `git ls-tree -rz` | ~10-50ms |
| Total expansion overhead | <100ms |

The actual time is dominated by fetching file contents and LLM API calls, not expansion.

## Upgrade Notes

This is a backward-compatible enhancement. Existing verification calls continue to work:

- File paths work exactly as before
- Directory paths now expand automatically
- No API changes required

The new response fields (`expanded_paths`, `paths_truncated`, `expansion_warnings`) are optional and present only when directory expansion occurs.

## Try It

```bash
# Upgrade to v0.23.0
pip install --upgrade llm-council-core

# Verify a directory
llm-council verify $(git rev-parse HEAD) --paths docs/
```

---

*Directory expansion makes verification practical for real codebases where you want to review entire directories, not just individual files. Combined with the existing DoS protections and configurable limits, it's safe to use even on large repositories.*
