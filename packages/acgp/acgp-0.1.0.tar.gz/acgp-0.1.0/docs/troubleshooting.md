# Troubleshooting Guide

Solutions to common issues when using CGP SDK.

## Connection Issues

### "SSE Connected: False"

**Symptom:** `client.sse_connected` returns `False` immediately after initialization.

**Causes & Solutions:**

1. **Normal startup delay** - SSE connects in a background thread. Wait 1-2 seconds:
   ```python
   import time
   client = CGPClient(on_feedback=callback)
   time.sleep(2)
   print(f"SSE Connected: {client.sse_connected}")
   ```

2. **Missing callback** - SSE only starts if `on_feedback` is provided:
   ```python
   # SSE not started (no callback)
   client = CGPClient()

   # SSE started
   client = CGPClient(on_feedback=handle_feedback)
   ```

3. **Invalid API key** - Check your credentials:
   ```python
   # Verify configuration
   print(f"Configured: {client.config.is_configured()}")
   print(f"Endpoint: {client.config.endpoint}")
   ```

4. **Network issues** - Check connectivity to the backend endpoint.

---

### "404 Not Found" for SSE endpoint

**Symptom:** Logs show `404 Not Found for url '.../stream/traces'`

**Solutions:**

1. Verify the endpoint URL is correct:
   ```bash
   CGP_ENDPOINT=https://api.steward-agent.com
   ```

2. Ensure the backend has the streaming endpoint deployed.

3. Check for URL construction issues (double `/v1/v1/`).

---

### "Server disconnected without sending a response"

**Symptom:** Traces timeout with `ReadTimeout` or disconnection errors.

**Causes & Solutions:**

1. **Traces not flushed** - Ensure `wait_for_feedback()` is called (it auto-flushes):
   ```python
   with client.trace(...) as trace:
       trace.set_output(result)

   # This flushes automatically before waiting
   client.wait_for_feedback(timeout=30)
   ```

2. **Client closed too early** - Don't close before traces are sent:
   ```python
   # Bad: Close immediately
   client.close()

   # Good: Wait for feedback first
   client.wait_for_feedback(timeout=30)
   client.close()
   ```

3. **Backend processing delay** - Increase timeout:
   ```python
   client.wait_for_feedback(timeout=60)  # Longer timeout
   ```

---

## Authentication Issues

### "401 Unauthorized"

**Symptom:** API calls return 401 status.

**Solutions:**

1. Verify API key is set:
   ```python
   import os
   print(f"API Key set: {bool(os.getenv('CGP_API_KEY'))}")
   ```

2. Check key format (should start with `sk_`):
   ```bash
   CGP_API_KEY=sk_live_xxxxxxxx
   ```

3. Ensure key hasn't been revoked or expired.

---

### "403 Forbidden"

**Symptom:** API calls return 403 status.

**Solutions:**

1. Verify tenant permissions for the API key.
2. Check if the endpoint requires specific permissions.
3. Contact administrator to verify key permissions.

---

## Trace Issues

### Traces not appearing in dashboard

**Symptom:** Traces are sent but don't show in the Steward Agent dashboard.

**Solutions:**

1. **Ensure flush is called** - Traces are batched:
   ```python
   client.flush()  # Force send pending traces
   ```

2. **Check for errors** - Enable debug mode:
   ```python
   client = CGPClient(debug=True, fail_silently=False)
   ```

3. **Verify tenant** - Ensure API key matches the dashboard tenant.

4. **Check batch results**:
   ```python
   def on_flush(results):
       for r in results:
           print(f"Batch: success={r.success}, errors={r.errors}")

   client = CGPClient(on_flush_complete=on_flush)
   ```

---

### "Timeout waiting for feedback"

**Symptom:** `wait_for_feedback()` returns `False`.

**Solutions:**

1. **Increase timeout** - Backend may need more time:
   ```python
   client.wait_for_feedback(timeout=60)  # 60 seconds
   ```

2. **Check pending count**:
   ```python
   print(f"Pending: {client.pending_feedback_count}")
   ```

3. **Verify SSE is connected**:
   ```python
   print(f"SSE Connected: {client.sse_connected}")
   ```

4. **Check backend logs** - Processing may have failed.

---

### Missing output in traces

**Symptom:** Traces appear but have no output.

**Solution:** Always call `set_output()`:

```python
with client.trace(...) as trace:
    try:
        result = agent.run()
        trace.set_output(result)  # Don't forget this!
    except Exception as e:
        trace.set_output(f"Error: {str(e)}")
        raise
```

---

## Performance Issues

### High memory usage

**Symptom:** Application memory grows over time.

**Solutions:**

1. **Reduce queue size**:
   ```python
   client = CGPClient(max_queue_size=1000)
   ```

2. **Flush more frequently**:
   ```python
   client = CGPClient(flush_interval=2.0)
   ```

3. **Truncate large outputs**:
   ```python
   MAX_SIZE = 50000
   output = result[:MAX_SIZE] if len(result) > MAX_SIZE else result
   trace.set_output(output)
   ```

---

### Slow trace submission

**Symptom:** Traces take too long to send.

**Solutions:**

1. **Use larger batches** for high throughput:
   ```python
   client = CGPClient(batch_size=500, flush_interval=10.0)
   ```

2. **Use smaller batches** for low latency:
   ```python
   client = CGPClient(batch_size=10, flush_interval=1.0)
   ```

3. **Check network latency** to the backend endpoint.

---

## SDK Behavior Issues

### SDK not doing anything

**Symptom:** Traces aren't sent, no errors shown.

**Solutions:**

1. **Check if enabled**:
   ```python
   # May be disabled via environment
   print(f"Enabled: {os.getenv('CGP_ENABLED', 'true')}")
   ```

2. **Check if configured**:
   ```python
   print(f"Configured: {client.config.is_configured()}")
   ```

3. **Disable silent failures**:
   ```python
   client = CGPClient(fail_silently=False)
   ```

---

### Exceptions being swallowed

**Symptom:** Errors occur but aren't visible.

**Solution:** Disable `fail_silently` for debugging:

```python
# Development: See all errors
client = CGPClient(fail_silently=False, debug=True)

# Production: Fail silently (default)
client = CGPClient(fail_silently=True)
```

---

## Callback Issues

### Callback not being called

**Symptom:** `on_feedback` callback never fires.

**Solutions:**

1. **Verify SSE is connected**:
   ```python
   print(f"SSE Connected: {client.sse_connected}")
   ```

2. **Wait for feedback**:
   ```python
   client.wait_for_feedback(timeout=30)
   ```

3. **Check callback signature**:
   ```python
   # Correct signature
   def handle_feedback(trace_id: str, data: dict):
       print(f"Feedback: {data}")

   # Wrong - missing parameters
   def handle_feedback(data):  # Missing trace_id!
       print(data)
   ```

---

### Callback errors crashing application

**Symptom:** Exception in callback crashes the app.

**Solution:** Handle exceptions in your callback:

```python
def handle_feedback(trace_id: str, data: dict):
    try:
        # Your logic here
        process_feedback(data)
    except Exception as e:
        logging.error(f"Callback error: {e}")
        # Don't re-raise - let SDK continue
```

---

## Environment Issues

### .env file not loading

**Symptom:** Environment variables aren't being read from `.env`.

**Solutions:**

1. **Ensure python-dotenv is installed**:
   ```bash
   pip install python-dotenv
   ```

2. **Check file location** - `.env` should be in working directory.

3. **Load manually if needed**:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Load before importing cgp_sdk

   from cgp_sdk import CGPClient
   ```

---

### CI/CD failures

**Symptom:** Tests fail in CI due to SDK issues.

**Solution:** Disable SDK in CI:

```bash
# In CI environment
CGP_ENABLED=false pytest
```

```python
# Or programmatically
import os
if os.getenv("CI"):
    client = CGPClient(enabled=False)
```

---

## Debug Mode

Enable comprehensive debugging:

```python
import logging

# Enable SDK debug logging
logging.basicConfig(level=logging.DEBUG)

client = CGPClient(
    debug=True,
    fail_silently=False,
)

# Check metrics
print(client.get_metrics())
```

---

## Getting Help

If issues persist:

1. **Check SDK metrics**: `client.get_metrics()`
2. **Enable debug logging**: `debug=True`
3. **Review backend logs** in the Steward Agent dashboard
4. **Contact support** with trace IDs and error messages
