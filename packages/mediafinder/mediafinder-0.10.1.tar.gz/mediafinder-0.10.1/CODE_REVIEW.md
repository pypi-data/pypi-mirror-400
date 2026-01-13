# Code Review: mf (mediafinder)

**Review Date**: 2025-12-23
**Reviewer**: Claude Code
**Scope**: Complete codebase analysis (fresh review)

---

## Priority Rankings

Issues are ranked by:
- **CRITICAL**: Bugs causing crashes, security vulnerabilities, data loss risks
- **HIGH**: Significant architectural issues, major maintainability problems, robustness concerns
- **MEDIUM**: Code quality issues, performance problems, error handling gaps
- **LOW**: Minor improvements, documentation gaps, style issues

---

## CRITICAL Priority

### 1. Missing f-string Prefix in play() Error Message
**File**: `src/mf/cli_main.py:103`
**Severity**: CRITICAL (Broken Functionality)

```python
print_and_raise(
    "Invalid target: {target}. Use an index number, 'next', or 'list'.",
    raise_from=e,
)
```

**Issue**: Missing `f` prefix on f-string. Error message displays literal `{target}` instead of the actual invalid input value.

**Impact**: Users see confusing error message: "Invalid target: {target}. Use an index number, 'next', or 'list'." instead of seeing their actual invalid input.

**Fix**:
```python
print_and_raise(
    f"Invalid target: {target}. Use an index number, 'next', or 'list'.",
    raise_from=e,
)
```

---

### 2. Unhandled ValueError in save_last_played() - Application Crash
**File**: `src/mf/utils/playlist.py:19`
**Severity**: CRITICAL (Runtime Error)

```python
def save_last_played(result: FileResult):
    with open_utf8(get_search_cache_file()) as f:
        cached = json.load(f)

    last_search_results: list[str] = cached["results"]
    last_played_index = last_search_results.index(str(result))  # NO ERROR HANDLING!
    cached["last_played_index"] = last_played_index
```

**Issue**: `list.index()` raises `ValueError` if the result is not found in cached results. This happens when:
- Files were deleted from disk since last search
- Cache was cleared/corrupted
- Result file path format changed

**Impact**: Application crashes with unhandled `ValueError` when trying to save last played file.

**Reproduction**:
1. Run `mf find pattern` (caches results)
2. Delete one of the found files from disk
3. Run `mf play 1` (attempts to save that deleted file)
4. Crash: `ValueError: <path> is not in list`

**Fix**:
```python
try:
    last_played_index = last_search_results.index(str(result))
except ValueError:
    print_warn("File not found in cached results, skipping last played tracking.")
    return

cached["last_played_index"] = last_played_index
```

---

### 3. Unhandled ValueError in get_next() - Application Crash
**File**: `src/mf/utils/playlist.py:52-60`
**Severity**: CRITICAL (Runtime Error)

```python
def get_next() -> FileResult:
    with open_utf8(get_search_cache_file()) as f:
        cached = json.load(f)

    results: list[str] = cached["results"]

    try:
        index_last_played = int(cached["last_played_index"])
    except KeyError:
        index_last_played = -1

    try:
        return FileResult.from_string(results[index_last_played + 1])
    except IndexError as e:
        print_and_raise("Last available file already played.", raise_from=e)
```

**Issue**: `int()` conversion can raise `ValueError` if `"last_played_index"` contains invalid data. Current code only catches `KeyError` and `IndexError`.

**Impact**: Unhandled `ValueError` crashes the app when cache contains corrupted data.

**Reproduction**:
1. Manually edit `~/.cache/mf/last_search.json`
2. Change `"last_played_index": 5` to `"last_played_index": "invalid"`
3. Run `mf play next`
4. Crash: `ValueError: invalid literal for int() with base 10: 'invalid'`

**Fix**:
```python
try:
    index_last_played = int(cached["last_played_index"])
except (KeyError, ValueError):
    index_last_played = -1
```

---

## HIGH Priority

### 4. Inconsistent Configuration Access Pattern - Type Safety
**Files**: `src/mf/utils/cache.py:148`, `src/mf/utils/scan.py:191,193`
**Severity**: HIGH (Type Safety)

**Issue**: Codebase mixes two different config access patterns:

```python
# Pattern 1 (cache.py) - Uses build_config() with type conversion
cache_interval: timedelta = build_config()["library_cache_interval"]

# Pattern 2 (scan.py) - Uses raw get_config() requiring type: ignore
prefer_fd = get_config()["prefer_fd"]  # type: ignore [assignment]
max_workers = get_max_workers(..., get_config()["parallel_search"])  # type: ignore [arg-type]
```

**Impact**:
- Many `# type: ignore` comments indicate type checker failures
- `get_config()` returns raw `TOMLDocument` without type hints
- `build_config()` returns typed `Configuration` object
- Renaming config keys won't be caught by static analysis in some places
- IDE autocomplete doesn't work for config values accessed via `get_config()`

**Recommendation**: Use `build_config()` consistently throughout codebase for type safety.

---

### 5. Missing JSON Schema Validation in load_search_results()
**File**: `src/mf/utils/search.py:79-103`
**Severity**: HIGH (Robustness)

**Issue**: Search cache loaded without validation:

```python
def load_search_results() -> tuple[FileResults, str, datetime]:
    cache_file = get_search_cache_file()
    try:
        with open_utf8(cache_file) as f:
            cache_data = json.load(f)  # NO VALIDATION!

        pattern = cache_data["pattern"]
        results = FileResults.from_paths(cache_data["results"])
        timestamp = datetime.fromisoformat(cache_data["timestamp"])

        return results, pattern, timestamp
```

**Impact**:
- `cache_data["results"]` assumed to be `list[str]` but not validated
- Could contain non-string items: `"results": [123, 456]` causes downstream crash
- Malformed timestamp causes `ValueError` in `fromisoformat()`
- Manually edited cache files can crash the application

**Recommendation**: Add validation:
```python
def _validate_search_cache(data: dict) -> None:
    """Validate search cache structure and types."""
    if not isinstance(data, dict):
        raise ValueError("Search cache must be a dictionary")

    required_keys = {"pattern", "results", "timestamp"}
    if not required_keys.issubset(data.keys()):
        raise ValueError(f"Search cache missing keys: {required_keys - data.keys()}")

    if not isinstance(data["results"], list):
        raise ValueError("Search cache 'results' must be a list")

    if not all(isinstance(r, str) for r in data["results"]):
        raise ValueError("Search cache 'results' must contain only strings")
```

---

### 6. Pickle Protocol Compatibility Risk
**File**: `src/mf/utils/cache.py:14, 109`
**Severity**: HIGH (Robustness)

```python
PICKLE_PROTOCOL = 5  # Binary protocol version 5 (Python 3.8+)

with open(get_library_cache_file(), "rb") as f:
    cache_data: CacheData = pickle.load(f)
```

**Issue**:
- Protocol 5 hardcoded, incompatible with Python < 3.8
- No version marker in cache file to detect incompatible formats
- Upgrading pickle protocol version breaks old cache files
- Silent failure mode (exception caught, cache rebuilt)

**Impact**: Users upgrading package versions may experience cache rebuilds due to pickle incompatibility.

**Recommendation**: Add version marker to cache or document protocol version changes in changelog.

---

### 7. Symlink Cycle Detection Missing - Infinite Recursion Risk
**File**: `src/mf/utils/scan.py:382-402`
**Severity**: HIGH (Robustness)

```python
def scan_dir(path: str):
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file(follow_symlinks=False):
                    # ...
                elif entry.is_dir(follow_symlinks=False):
                    scan_dir(entry.path)  # Potential infinite recursion
    except PermissionError:
        print_warn(f"Missing access permissions for directory {path}, skipping.")
```

**Issue**:
- Uses `follow_symlinks=False` but no visited set or depth limit
- Directory structures with symlink loops cause infinite recursion
- Python recursion limit (default 1000) will be hit, crashing the application

**Example**:
```bash
mkdir -p a/b
ln -s .. a/b/parent_link
# Running scan on 'a' causes infinite recursion
```

**Recommendation**: Track visited inodes:
```python
def scan_path_with_python(
    search_path: Path,
    with_mtime: bool = False,
    progress_callback: Callable[[FileResult], None] | None = None,
) -> FileResults:
    results = FileResults()
    visited_inodes: set[tuple[int, int]] = set()  # (device, inode) pairs

    def scan_dir(path: str):
        try:
            stat = os.stat(path)
            inode_key = (stat.st_dev, stat.st_ino)

            if inode_key in visited_inodes:
                return  # Already visited, skip to prevent cycle

            visited_inodes.add(inode_key)

            with os.scandir(path) as entries:
                # ... rest of logic
```

---

## MEDIUM Priority

### 8. Missing Edge Case Handling in fd Output
**File**: `src/mf/utils/scan.py:255-259`
**Severity**: MEDIUM (Robustness)

**Issue**: fd output is split and used without validation:

```python
for line in result.stdout.strip().split("\n"):
    if line:
        files.append(FileResult(Path(line)))
```

**Impact**:
- Empty lines silently ignored (acceptable)
- Invalid paths could crash
- Encoding issues not handled

**Recommendation**:
```python
for line in result.stdout.strip().split("\n"):
    if not line:
        continue

    try:
        path = Path(line)
        if not path.is_absolute():
            print_warn(f"fd returned non-absolute path: {line}")
            continue
        files.append(FileResult(path))
    except Exception as e:
        print_warn(f"Invalid path from fd: {line} ({e})")
```

---

### 9. Configuration Type Coercion Inconsistency
**Files**: `src/mf/utils/cache.py:148`, `src/mf/utils/config.py:148-154`
**Severity**: MEDIUM (Type Safety)

```python
# In cache.py - uses build_config() which applies from_toml conversion
cache_interval: timedelta = build_config()["library_cache_interval"]

# In scan.py - uses raw get_config() without type conversion
prefer_fd = get_config()["prefer_fd"]  # Still a raw value, not converted!
```

**Issue**:
- `build_config()` applies `from_toml()` function to convert values
- `get_config()` returns raw TOML document without conversion
- Some settings might have `from_toml` transformations that aren't applied

**Impact**: Type mismatches between different code paths accessing configuration.

**Recommendation**: Consistently use `build_config()` for all configuration access.

---

### 10. Silent Permission Error Suppression Without Context
**File**: `src/mf/utils/scan.py:399-400`
**Severity**: MEDIUM (Observability)

```python
except PermissionError:
    print_warn(f"Missing access permissions for directory {path}, skipping.")
```

**Issue**:
- Permission errors are silently skipped
- User has no way to know how much data was skipped
- No summary at end of scan

**Impact**: If entire directory tree is inaccessible, user gets many warnings but no context about data loss.

**Recommendation**: Track skipped directories and report summary:
```python
def scan_path_with_python(...) -> FileResults:
    results = FileResults()
    skipped_count = 0

    def scan_dir(path: str):
        nonlocal skipped_count
        try:
            # ... scanning logic
        except PermissionError:
            skipped_count += 1
            print_warn(f"Missing access permissions for directory {path}, skipping.")

    scan_dir(str(search_path))

    if skipped_count > 0:
        console.print(f"[yellow]Skipped {skipped_count} inaccessible directories[/yellow]")

    return results
```

---

### 11. play() Command Error Handling Logic Gap
**File**: `src/mf/cli_main.py:95-105`
**Severity**: MEDIUM (Error Handling)

```python
else:
    # Play requested file
    try:
        index = int(target)
        file_to_play = get_result_by_index(index)  # Can raise multiple error types
        save_last_played(file_to_play)
    except ValueError as e:
        print_and_raise(
            "Invalid target: {target}. Use an index number, 'next', or 'list'.",  # Also has f-string bug
            raise_from=e,
        )
```

**Issue**:
- `get_result_by_index()` calls `print_and_raise()` internally on both IndexError and file-not-found errors
- But outer try-except only catches `ValueError` from `int(target)` conversion
- Other exceptions propagate up without being caught

**Impact**: Error handling is unclear and incomplete.

**Recommendation**: Review exception handling flow and document expected exception types.

---

## LOW Priority

### 12. Hardcoded VLC Paths - Limited Windows Support
**File**: `src/mf/utils/misc.py:132-135`
**Severity**: LOW (Portability)

**Issue**: Only checks 2 Windows paths:

```python
vlc_paths = [
    r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
]
```

**Missing**:
- Windows Store installation
- Portable VLC
- Custom install locations

**Recommendation**: Check Windows registry or add more paths:

```python
def _get_windows_vlc_path() -> str | None:
    """Try to find VLC on Windows."""
    # Common installation paths
    paths = [
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "VideoLAN" / "VLC" / "vlc.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "VideoLAN" / "VLC" / "vlc.exe",
        Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps" / "vlc.exe",  # Store
    ]

    for path in paths:
        if path.exists():
            return str(path)

    return None
```

---

### 13. Missing Docstring in version() CLI Command
**File**: `src/mf/cli_main.py:181`
**Severity**: LOW (Documentation)

```python
def version(target: str | None = typer.Argument(...)) -> None:
    "Print version or perform version check."  # Short docstring only
```

**Recommendation**:
```python
def version(target: str | None = typer.Argument(...)) -> None:
    """Print version or perform version check.

    Displays the installed mediafinder version. If 'check' is provided as
    argument, queries PyPI for the latest available version.
    """
```

---

### 14. Overly Broad Exception Catch in VLC Launch
**File**: `src/mf/cli_main.py:149-150`
**Severity**: LOW (Error Handling)

```python
except Exception as e:
    print_and_raise(f"Error launching VLC: {e}", raise_from=e)
```

**Recommendation**: Should specify exact exception types:
```python
except (FileNotFoundError, subprocess.SubprocessError, OSError) as e:
    print_and_raise(f"Error launching VLC: {e}", raise_from=e)
```

---

### 15. Inconsistent Help Text Formatting
**Files**: Multiple CLI files
**Severity**: LOW (Documentation)

**Issue**:
- `cli_main.py:181`: Uses simple string docstring
- `cli_main.py:42`: Uses triple-quoted docstring with detailed description
- Inconsistent style across commands

**Recommendation**: Standardize on triple-quoted docstrings with detailed descriptions for all commands.

---

## Testing Gaps

### 16. Missing Edge Case Tests
**Severity**: MEDIUM

**Not tested**:
- Empty search paths configuration
- Very large collections (1000s of files)
- Symlinks in search paths (especially cycles)
- Special characters in filenames (Unicode, spaces, etc.)
- Cache corruption recovery
- Concurrent cache access
- VLC not installed scenarios
- Network timeouts in version check
- fd binary permissions issues

**Recommendation**: Add systematic edge case testing.

---

### 17. Playlist Integration Tests Missing
**Severity**: MEDIUM

**Not tested**:
- `save_last_played()` with file that doesn't exist in cache
- `get_next()` with invalid `last_played_index` value (non-integer)
- Behavior when cache file is corrupted during playlist operations

**Recommendation**: Add test matrix:
- Cache states: valid | empty | corrupted | missing
- Last played index: valid | invalid | missing | out-of-bounds

---

### 18. Configuration Type Consistency Tests Missing
**Severity**: MEDIUM

**Not tested**:
- `get_config()` and `build_config()` return compatible values
- Type conversions are correct across all settings
- `from_toml` functions work correctly

**Recommendation**: Add tests verifying config access patterns produce identical results.

---

### 19. Symlink Edge Cases Not Tested
**Severity**: LOW

**Not tested**:
- Symlink cycles
- Deep symlink chains
- Broken symlinks
- Symlinks to files outside search paths

**Recommendation**: Add symlink-specific test suite.

---

## Summary Statistics

| Priority | Count | Categories |
|----------|-------|------------|
| CRITICAL | 3 | Runtime crashes, broken error messages |
| HIGH | 4 | Type safety, robustness, infinite recursion risk |
| MEDIUM | 4 | Error handling, observability, validation |
| LOW | 3 | Documentation, portability, minor improvements |
| Testing Gaps | 4 | Edge cases, integration, symlinks |
| **TOTAL** | **18** | |

---

## Quick Wins (High Impact, Low Effort)

1. **Fix f-string bug in cli_main.py:103** - 1 character (`f` prefix) - CRITICAL
2. **Add ValueError handling in playlist.py** - 2 lines each (issues #2 and #3) - CRITICAL
3. **Add inode tracking for symlink cycle detection** - 10-15 lines - HIGH
4. **Validate search cache data structure** - 10 lines - HIGH
5. **Standardize on build_config()** - Refactor 3-4 files - HIGH

---

## Recommended Next Steps

1. **IMMEDIATE** (This Week):
   - Fix CRITICAL issues #1, #2, #3 (f-string bugs and ValueError handling)
   - Add symlink cycle detection (HIGH #7)

2. **SHORT TERM** (This Month):
   - Add JSON schema validation (HIGH #5)
   - Standardize configuration access pattern (HIGH #4)
   - Add playlist integration tests (Testing Gap #17)

3. **MEDIUM TERM** (Next 2-3 Months):
   - Address MEDIUM priority issues (#8-#11)
   - Expand edge case test coverage (Testing Gap #16)

4. **LONG TERM** (Ongoing):
   - Address LOW priority improvements as part of regular maintenance
   - Continue expanding test coverage

---

## Notes

- All CRITICAL issues cause application crashes under realistic usage scenarios
- HIGH priority issues represent robustness and type safety concerns that should be addressed soon
- Testing gaps indicate areas where bugs are more likely to slip through
- This review supersedes the 2025-12-10 review; previous issues have been resolved or marked WONTFIX

---

## DONE - Previously Completed or Marked WONTFIX

The following issues from the 2025-12-10 review have been resolved or marked as WONTFIX:

### Completed (✔)
1. **String Formatting Bug in IMDB Error Message** - `src/mf/utils/misc.py:68` (CRITICAL)
2. **Complex Progress Bar Function with Duplicated Code** - `src/mf/utils/scan.py:107-223` (HIGH)
3. **Global Config Cache Without Invalidation** - `src/mf/utils/config.py:25, 69-74` (HIGH)
4. **JSON Schema Validation Missing** - `src/mf/utils/cache.py:99-108`, `src/mf/utils/search.py:77-82` (HIGH)
5. **Overly Complex Scanner Selection Logic** - `src/mf/utils/scan.py:24-104` (HIGH)
6. **Type Hint Inaccuracies** - `src/mf/utils/scan.py:107`, `src/mf/utils/stats.py:19` (MEDIUM)
7. **Overly Broad Exception Handling** - `src/mf/version.py:24`, `src/mf/utils/scan.py:58-65` (MEDIUM)
8. **Inefficient List Operations in Loops** - `src/mf/utils/scan.py:144-145, 181-182, 218-219` (MEDIUM)
9. **Magic Numbers Not Documented** - Multiple files (LOW)
10. **Typo in Setting Help Text** - `src/mf/utils/settings.py:138` (LOW)
11. **Missing main() Docstring** - `src/mf/__init__.py:15-16` (LOW)
12. **Missing Integration Tests** - play() command test coverage (MEDIUM)

### Marked WONTFIX
1. **Circular Import Workaround** - `src/mf/utils/settings.py:25-31` - Not actually a problem
2. **Silent Error Suppression in Directory Scanning** - `src/mf/utils/scan.py:297-298` - Assessment was incorrect
3. **Duplicated Config Action Handlers** - `src/mf/cli_config.py:56-85` - Required by Typer framework
4. **Inefficient Progress Bar Polling** - `src/mf/utils/scan.py:152, 202, 221` - Alternative doesn't work with current implementation
5. **Cache Rebuild Triggers Multiple Times** - `src/mf/utils/settings.py:77, 127` - Expected behavior
6. **Missing Docstring Examples** - `src/mf/utils/normalizers.py` - Functions are self-explanatory
7. **Inconsistent Path Format** - `src/mf/utils/file.py:135-138` - Consistent and intentional design choice
8. **No Duplicate File Detection** - Feature gap, not a bug
9. **Editor Selection Inconsistency** - `src/mf/utils/misc.py:34-45` - Platform-specific behavior is acceptable

---

*End of Code Review*

