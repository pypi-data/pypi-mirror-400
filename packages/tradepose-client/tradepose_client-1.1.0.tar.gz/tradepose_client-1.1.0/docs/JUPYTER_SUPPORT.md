# Jupyter Notebook Support

## Overview

The TradePose Client SDK provides **automatic Jupyter notebook support** without requiring manual configuration. When you initialize a `BatchTester`, it automatically detects if you're running in a Jupyter environment and applies the necessary patches.

## What Happens Automatically

When you create a `BatchTester` instance:

```python
from tradepose_client import BatchTester

tester = BatchTester(api_key="sk_xxx", server_url="https://api.tradepose.com")
```

The SDK automatically:

1. **Detects Jupyter Environment** - Checks if running inside Jupyter/IPython
2. **Applies nest_asyncio** - If a running event loop is detected, applies `nest_asyncio` to enable nested async operations
3. **Logs Notification** - Shows an INFO message confirming Jupyter support is active

## User Experience

### Before (Manual Setup Required)

```python
# ❌ Old way - user had to remember this
import nest_asyncio
nest_asyncio.apply()

from tradepose_client import BatchTester
tester = BatchTester(api_key="sk_xxx")
```

### After (Automatic Setup)

```python
# ✅ New way - just import and use
from tradepose_client import BatchTester

tester = BatchTester(api_key="sk_xxx")
# INFO: 📓 Jupyter environment detected - nest_asyncio automatically applied for seamless async support
```

## Requirements

The SDK requires `nest-asyncio` to be installed when running in Jupyter:

```bash
pip install nest-asyncio
# or
uv pip install nest-asyncio
```

If `nest-asyncio` is not installed and you're running in Jupyter, you'll see a warning:

```
⚠️  Jupyter environment detected but nest-asyncio not installed.
   Some async operations may fail. Install with: pip install nest-asyncio
```

## Technical Details

### How It Works

The auto-detection system uses three key functions in `tradepose_client.utils`:

1. **`is_jupyter()`** - Checks if `get_ipython()` is available (present in Jupyter/IPython)
2. **`setup_jupyter_support()`** - Called during `BatchTester.__init__()`, applies nest_asyncio if needed
3. **`run_async_safe()`** - Used internally for safe async execution in both Jupyter and standard Python

### Why nest_asyncio?

Jupyter notebooks run their own asyncio event loop. When you call async functions (like downloading results), Python tries to create a nested event loop, which normally raises an error:

```
RuntimeError: This event loop is already running
```

`nest_asyncio` patches asyncio to allow nested event loops, making async code work seamlessly in Jupyter.

### Performance Impact

**Minimal to None:**
- Applied only once during `BatchTester` initialization
- No runtime overhead for async operations
- Only affects Jupyter environments (standard Python is unchanged)

### Risks

**Very Low:**
- `nest_asyncio` is widely used in the data science community
- Has been stable for years (used by projects like IPython, papermill, jupyter-client)
- Only modifies event loop behavior in controlled ways
- Does not affect code outside of async contexts

## Supported Environments

- ✅ Jupyter Notebook
- ✅ JupyterLab
- ✅ Google Colab
- ✅ IPython
- ✅ VS Code Jupyter Extension
- ✅ PyCharm Jupyter Support
- ✅ Standard Python (no action needed, runs normally)

## Troubleshooting

### Not Seeing the INFO Message?

Check your logging level. The message is logged at INFO level:

```python
import logging
logging.basicConfig(level=logging.INFO)

from tradepose_client import BatchTester
tester = BatchTester(api_key="sk_xxx")
# Should now see: 📓 Jupyter environment detected - nest_asyncio automatically applied...
```

### Still Getting "Event Loop Already Running" Errors?

This shouldn't happen after initialization. If you do see this error:

1. Make sure `nest-asyncio` is installed
2. Check that `setup_jupyter_support()` was called (it should be automatic)
3. Try restarting your Jupyter kernel

### Using Outside of BatchTester

If you're using lower-level client APIs directly, you can manually call:

```python
from tradepose_client.utils import setup_jupyter_support

setup_jupyter_support()  # Apply once at the start of your notebook
```

## Examples

### Single Strategy, Multiple Periods

```python
from tradepose_client import BatchTester

# No manual setup needed!
tester = BatchTester(api_key="sk_xxx")

batch = tester.submit(
    strategies=[strategy],
    periods=[
        ("2024-01-01", "2024-03-31"),
        ("2024-04-01", "2024-06-30"),
    ]
)

# Wait for completion (works seamlessly in Jupyter)
batch.wait()
print(batch.summary())
```

### Multiple Strategies, Single Period

```python
# Create strategy variants
strategies = [
    create_strategy("fast", multiplier=2.0),
    create_strategy("medium", multiplier=3.0),
    create_strategy("slow", multiplier=4.0),
]

# Submit for parameter testing
batch = tester.submit(
    strategies=strategies,
    periods=[("2024-01-01", "2024-06-30")]
)

# All async operations work automatically
batch.wait()
results = batch.summary()
```

## References

- [nest_asyncio GitHub](https://github.com/erdewit/nest_asyncio)
- [Jupyter Event Loop Documentation](https://ipython.readthedocs.io/en/stable/interactive/autoawait.html)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
