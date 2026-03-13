# Thread-Safe Cost Logging

## Problem
When agents run in parallel, multiple processes write to `cost_log.json` simultaneously, causing race conditions and malformed JSON.

## Solution
Implemented file-based locking using the `filelock` library to ensure only one agent writes to the cost log at a time.

## Implementation

### Centralized Logging Function
All agents now use the centralized `log_cost()` function in `agents/utils/__init__.py`:

```python
from filelock import FileLock

def log_cost(agent_name, tokens_used, estimated_cost, model, operation, **extra_fields):
    lock_file = COST_LOG_FILE + '.lock'
    
    with FileLock(lock_file, timeout=10):
        # Load existing logs
        if os.path.exists(COST_LOG_FILE):
            with open(COST_LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Append new entry
        logs.append(log_entry)
        
        # Save updated logs
        with open(COST_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)
```

### How It Works
1. When an agent needs to log cost, it calls `log_cost()`
2. The function acquires a file lock (`cost_log.json.lock`)
3. Only one process can hold the lock at a time
4. Other processes wait (up to 10 seconds timeout)
5. Once lock is acquired, the process reads, modifies, and writes the JSON
6. Lock is released automatically when the `with` block exits
7. Next waiting process acquires the lock and repeats

### Benefits
- **No race conditions**: Only one writer at a time
- **Valid JSON**: Always properly formatted
- **Automatic cleanup**: Lock files are managed automatically
- **Timeout protection**: Prevents deadlocks (10-second timeout)
- **Zero code changes**: Agents just call the centralized function

### Updated Agents
All agents now use the thread-safe centralized logging:
- `news-synthesis/local_news_agent_nova.py`
- `voice_briefing_nova.py`
- `image_analysis_nova.py`
- `bridge_to_permits_nova.py`
- `web_scraper_nova_act.py`
- `features/smart_alerts_nova.py`
- `features/safety_intelligence_nova.py`
- `features/investment_insights_nova.py`
- `features/community_pulse_nova.py`

### Testing
Verified with multiple parallel runs:
- ✅ All 10 agents complete successfully
- ✅ cost_log.json remains valid JSON
- ✅ No race conditions or corruption
- ✅ Cost summary displays correctly

### Dependencies
```bash
pip install filelock
```

Already included in project requirements.
