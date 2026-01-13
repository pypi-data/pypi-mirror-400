# Proposal: Verification Context Enhancement - Directory Expansion

**Status:** Draft (Pending Council Review)
**Date:** 2026-01-01
**Related:** ADR-034 Agent Skills Integration for Work Verification

---

## Problem Statement

When running `mcp__llm-council__verify` with directory-based `target_paths` (e.g., `["docs/"]`), the verification prompt receives a git tree listing instead of actual file contents. This causes council models to correctly identify that they cannot perform a meaningful review, resulting in UNCLEAR verdicts.

### Evidence

Verification transcript `fb172c21` shows council response:
> "This review can only assess the directory structure, not the actual documentation content."

All three models noted:
- "Without viewing the file contents, it is impossible to verify..." (Gemini)
- "Only directory structure visible: The actual content of files is not shown" (Claude)
- "Without actual file contents, it is impossible to verify..." (Grok)

### Root Cause

In `verification/api.py`, the `_fetch_files_for_verification_async` function:

```python
files_to_fetch = list(target_paths) if target_paths else []
# ...
content = await _fetch_file_at_commit_async(snapshot_id, file_path)
```

When `target_paths = ["docs/"]`, the function passes `"docs/"` directly to `git show commit:docs/` which returns a tree listing, not file contents.

---

## Proposed Solution

### Option A: Directory Expansion with `git ls-tree` (Recommended)

Detect directories and expand them to constituent files before fetching:

```python
async def _expand_target_paths(
    snapshot_id: str,
    target_paths: List[str],
) -> List[str]:
    """
    Expand directories in target_paths to their constituent files.

    Uses git ls-tree to list files in directories at the given commit.

    Args:
        snapshot_id: Git commit SHA
        target_paths: List of paths (may include directories)

    Returns:
        Expanded list of file paths (directories replaced with their files)
    """
    expanded_files: List[str] = []

    for path in target_paths:
        # Check if path is a directory using git cat-file
        obj_type = await _get_git_object_type(snapshot_id, path)

        if obj_type == "tree":
            # Directory: expand using ls-tree
            files = await _list_tree_files(snapshot_id, path)
            expanded_files.extend(files)
        elif obj_type == "blob":
            # File: keep as-is
            expanded_files.append(path)
        else:
            # Unknown/error: skip with warning
            pass

    return expanded_files
```

#### Implementation Details

1. **Object Type Detection**
```python
async def _get_git_object_type(snapshot_id: str, path: str) -> Optional[str]:
    """Get git object type (blob, tree, or None for error)."""
    proc = await asyncio.create_subprocess_exec(
        "git", "cat-file", "-t", f"{snapshot_id}:{path}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    if proc.returncode == 0:
        return stdout.decode().strip()
    return None
```

2. **Directory File Listing**
```python
async def _list_tree_files(snapshot_id: str, tree_path: str) -> List[str]:
    """List all files in a git tree (recursively)."""
    proc = await asyncio.create_subprocess_exec(
        "git", "ls-tree", "-r", "--name-only", f"{snapshot_id}:{tree_path}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    if proc.returncode == 0:
        files = stdout.decode().strip().split("\n")
        # Prepend tree_path to get full paths
        return [f"{tree_path}/{f}" for f in files if f]
    return []
```

3. **Integration into Fetch Function**
```python
async def _fetch_files_for_verification_async(
    snapshot_id: str,
    target_paths: Optional[List[str]] = None,
) -> str:
    """Fetch file contents for verification prompt."""
    # Expand directories to files
    if target_paths:
        files_to_fetch = await _expand_target_paths(snapshot_id, target_paths)
    else:
        # Use git diff-tree for changed files (existing behavior)
        files_to_fetch = await _get_changed_files(snapshot_id)

    # ... rest of existing implementation
```

### Option B: Smart Path Inference

Instead of expanding, detect when a tree is returned and warn:

```python
async def _fetch_file_at_commit_async(snapshot_id: str, file_path: str) -> Tuple[str, bool]:
    # ... existing code ...

    # Detect tree output (starts with "tree" object listing)
    if content.startswith("tree ") or re.match(r"^\d{6} (blob|tree) [0-9a-f]+", content):
        return f"[Warning: '{file_path}' is a directory. Specify individual files.]", False

    return content, truncated
```

### Option C: Hybrid (Recommended Extension)

Combine directory expansion with file type filtering:

```python
# Only include text-like files, skip binaries
TEXT_EXTENSIONS = {'.py', '.md', '.js', '.ts', '.json', '.yaml', '.yml', '.toml', ...}

async def _expand_target_paths(snapshot_id: str, target_paths: List[str]) -> List[str]:
    expanded = await _raw_expand_target_paths(snapshot_id, target_paths)
    return [f for f in expanded if Path(f).suffix.lower() in TEXT_EXTENSIONS]
```

---

## Design Considerations

### 1. Size Limits

The existing limits should be respected:
- `MAX_FILE_CHARS = 15000` per file
- `MAX_TOTAL_CHARS = 50000` total

Directory expansion may generate many files. The batched fetching with early termination (existing in api.py lines 402-426) handles this.

### 2. Concurrency

Existing `MAX_CONCURRENT_GIT_OPS = 10` semaphore prevents DoS. Directory expansion adds one extra git call per directory before file fetching.

### 3. Binary File Handling

Binary files should be excluded or marked. The existing `decode("utf-8", errors="replace")` handles encoding, but binary files waste context.

### 4. Symbolic Links

Git ls-tree shows symlinks. They should be skipped or followed depending on security posture.

### 5. Empty Directories

Empty directories return empty file lists - handled gracefully by existing code.

---

## Trade-offs

| Aspect | Option A (ls-tree) | Option B (Detection) | Option C (Hybrid) |
|--------|-------------------|---------------------|-------------------|
| Implementation | Medium | Low | Higher |
| User Experience | Best | Poor (requires retry) | Best |
| Performance | +1-2 git calls | No change | +1-2 git calls |
| Binary handling | Needs filtering | N/A | Built-in |
| Maintenance | Low | Low | Medium |

**Recommendation**: Option C (Hybrid) for best UX with binary filtering.

---

## Exit Criteria

1. `mcp__llm-council__verify` with `target_paths=["docs/"]` returns file contents, not tree listing
2. Binary files are excluded from context
3. Size limits are respected (existing tests pass)
4. Concurrency limits prevent DoS (existing tests pass)
5. Unit tests for directory expansion

---

## Questions for Council

1. Should we support glob patterns in target_paths (e.g., `"src/**/*.py"`)?
2. Should binary detection use magic bytes or file extension?
3. For very large directories, should we sample files or require explicit paths?
4. Should we add a `max_files` parameter to limit expansion?

---

## Implementation Tasks (if approved)

1. [ ] Add `_get_git_object_type()` helper
2. [ ] Add `_list_tree_files()` helper
3. [ ] Add `_expand_target_paths()` with text filtering
4. [ ] Update `_fetch_files_for_verification_async()` to use expansion
5. [ ] Add unit tests for directory expansion
6. [ ] Add integration test with docs/ verification
7. [ ] Update ADR-034 with implementation notes
