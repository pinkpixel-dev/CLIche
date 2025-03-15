# Memory System Error Handling 🛡️

This document provides technical details about the error handling mechanisms implemented in the CLIche memory system, particularly focusing on the FTS (Full-Text Search) error suppression and fallback strategies.

## Overview

The CLIche memory system uses SQLite with the FTS5 virtual table for efficient text-based searching. However, FTS5 can sometimes encounter issues, especially when:
- The database becomes corrupted
- The search query contains special characters that break FTS syntax
- The database structure changes after the FTS index is created

To address these issues, we've implemented robust error handling mechanisms that:
1. Suppress error messages from being displayed to users
2. Provide fallback search mechanisms when FTS fails
3. Log errors for debugging purposes
4. Allow for database repair when needed

## Implementation Details

### Error Suppression in Command Handlers

Both the `chat` and `ask` commands implement error suppression using Python's standard library features:

```python
# Capture standard error to prevent FTS errors from showing up
old_stderr = sys.stderr
sys.stderr = io.StringIO()

try:
    # Find related memories using the enhanced memory retrieval system
    memory_context = find_related_memories(assistant, query_str)
finally:
    # Restore stderr and log any captured errors
    captured_errors = sys.stderr.getvalue()
    sys.stderr = old_stderr
    
    if captured_errors:
        logger.debug(f"Suppressed errors during memory search: {captured_errors}")
```

This approach:
- Redirects standard error output to a string buffer
- Captures any error messages that would normally be displayed
- Restores the standard error stream after the operation
- Logs any captured errors at the debug level

### Improved Search Method

The `search` method in `memory.py` has been enhanced to handle errors more gracefully:

```python
fts_success = False
rows = []

if cleaned_query:
    # Use FTS to search for memories with similar content
    try:
        cursor.execute(
            """
            SELECT m.id, m.content, m.user_id, m.timestamp, m.updated_at, m.metadata,
                highlight(memory_fts, 0, '<mark>', '</mark>') as highlighted
            FROM memory_fts
            JOIN memories m ON memory_fts.id = m.id
            WHERE memory_fts MATCH ? AND m.user_id = ?
            ORDER BY rank
            LIMIT ?
            """,
            (cleaned_query, self.user_id, limit)
        )
        
        rows = cursor.fetchall()
        if rows:
            fts_success = True
    except sqlite3.OperationalError as e:
        # Handle specific FTS errors silently
        error_msg = str(e)
        if "no such column" in error_msg or "syntax error" in error_msg:
            logger.debug(f"FTS search failed with benign error: {error_msg}")
        else:
            # Log other operational errors but still fall back to LIKE search
            logger.warning(f"FTS search failed: {e}. Falling back to LIKE search.")
    except Exception as e:
        # Log other errors but still fall back
        logger.warning(f"FTS search failed: {e}. Falling back to LIKE search.")

# If no results from FTS or FTS failed, try a simple LIKE search
if not fts_success:
    # LIKE search fallback implementation
    # ...
```

This approach:
- Specifically catches `sqlite3.OperationalError` for known FTS issues
- Distinguishes between common benign errors and more serious problems
- Falls back to a LIKE-based search when FTS fails
- Continues operation even when errors occur

## LIKE Search Fallback

When FTS search fails, the system automatically falls back to a SQL LIKE search:

```python
# Extract words from query and create LIKE patterns
words = [w for w in query.split() if len(w) > 2]
if not words:
    words = query.split()

like_patterns = []
params = []

for word in words:
    like_patterns.append("content LIKE ?")
    params.append(f"%{word}%")

if not like_patterns:
    like_patterns.append("content LIKE ?")
    params.append(f"%{query}%")

where_clause = " OR ".join(like_patterns)

query_sql = f"""
    SELECT id, content, user_id, timestamp, updated_at, metadata
    FROM memories
    WHERE ({where_clause}) AND user_id = ?
    ORDER BY timestamp DESC
    LIMIT ?
"""

params.append(self.user_id)
params.append(limit)

cursor.execute(query_sql, params)
rows = cursor.fetchall()
```

This fallback:
- Extracts meaningful words from the query
- Creates multiple LIKE patterns for each word
- Builds a SQL query with these patterns
- Maintains the same interface as the FTS search
- Prioritizes recent memories when ranking results

## User Experience Flow

From the user's perspective, the flow works as follows:

1. User issues a query via `chat` or `ask`
2. System attempts FTS search for relevant memories
3. If FTS fails, system silently falls back to LIKE search
4. If LIKE search also fails, system continues without memories
5. User receives a response without seeing any error messages

## Debugging and Repair

For developers and advanced users:

1. Errors are logged at the `debug` level in the application logs
2. The `cliche memory repair` command can rebuild the FTS index
3. The `search` method in `memory.py` includes detailed comments explaining the error handling strategy
4. The `_clean_query_for_fts` method helps prevent some FTS syntax errors

## Future Improvements

Potential future enhancements to the error handling system:

1. Implement more sophisticated FTS query cleaning
2. Add automatic repair triggered by persistent FTS failures
3. Implement a "health check" for the memory system
4. Consider alternative search approaches for more robust operation
5. Add telemetry to track error frequency (with user permission)

## Conclusion

The improved error handling in the CLIche memory system ensures that users have a smooth experience even when underlying technical issues occur. By suppressing disruptive error messages, providing robust fallback mechanisms, and maintaining detailed logs, the system balances user experience with technical robustness. 