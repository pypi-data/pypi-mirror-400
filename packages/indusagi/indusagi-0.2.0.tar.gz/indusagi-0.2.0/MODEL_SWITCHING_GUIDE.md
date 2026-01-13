# Model Switching Guide

## ✅ Quick Fix for Rate Limits

Both `example_agency.py` and `example_agency_improved.py` now use **gpt-4o-mini** by default to avoid rate limit errors.

## 🚀 Running with Mini Model

```bash
# Option 1: Run improved agency (recommended)
python example_agency_improved.py

# Option 2: Run original agency
python example_agency.py

# Option 3: Run with custom config
python config_agency.py
```

All use **gpt-4o-mini** now - **no more rate limit errors!**

## 🎛️ **Switching Models**

### Option 1: Edit `config_agency.py` (Easiest)

```python
# Change this line:
MODEL = "gpt-4o-mini"  # Current

# To one of these:
MODEL = "gpt-4o"           # More capable, slower, expensive
MODEL = "gpt-3.5-turbo"    # Fastest, cheapest
```

Then run:
```bash
python config_agency.py
```

### Option 2: Edit Agency Files Directly

**In `example_agency_improved.py` (line 352):**
```python
agency = create_development_agency(
    model="gpt-4o-mini",  # ← Change this
    reasoning_effort="medium",
    max_handoffs=15
)
```

**In `example_agency.py` (line 383):**
```python
agency = create_development_agency(
    model="gpt-4o-mini",  # ← Change this
    reasoning_effort="medium",
    max_handoffs=10
)
```

## 📊 **Model Comparison**

| Model | Speed | Cost/1M tokens | Rate Limit | Quality | Best For |
|-------|-------|----------------|------------|---------|----------|
| **gpt-4o-mini** ⭐ | ⚡⚡⚡ Fast | $0.15 | High | Good | **Development, Testing** |
| gpt-4o | ⚡⚡ Medium | $2.50 | Medium | Excellent | Production, Complex |
| gpt-3.5-turbo | ⚡⚡⚡⚡ Fastest | $0.50 | High | Basic | High Volume |

**⭐ Recommended: gpt-4o-mini** - Best balance of speed, cost, and quality

## 🔥 **Why gpt-4o-mini?**

### ✅ **Advantages:**
1. **Higher Rate Limits** - 200K tokens/min vs 30K for gpt-4o
2. **Much Cheaper** - ~17x cheaper than gpt-4o
3. **Fast Response** - Quick iteration during development
4. **Good Quality** - Handles most coding tasks well
5. **Perfect for Multi-Agent** - Multiple agent calls won't hit limits

### ⚠️ **When to Use gpt-4o Instead:**
- Complex architectural decisions
- Large-scale refactoring
- Production deployments
- When quality > cost

## 🎯 **Rate Limit Breakdown**

### gpt-4o Rate Limits (OLD - causes errors):
- **30,000 tokens/min**
- Multi-agent system easily exceeds this
- **Error:** "Rate limit reached... Please try again in 16ms"

### gpt-4o-mini Rate Limits (NEW - no errors):
- **200,000 tokens/min** (6.6x higher!)
- Can run multiple agents continuously
- **No errors** during development

## 🧪 **Testing Different Models**

Create a test script:

```python
from config_agency import create_development_agency

# Test mini
agency_mini = create_development_agency(model="gpt-4o-mini")
response_mini = agency_mini.process("Create hello.html")

# Test regular (if you have quota)
agency_regular = create_development_agency(model="gpt-4o")
response_regular = agency_regular.process("Create hello.html")

# Compare results
print(f"Mini: {response_mini.total_time:.2f}s")
print(f"Regular: {response_regular.total_time:.2f}s")
```

## 💡 **Best Practices**

1. **Development:** Always use `gpt-4o-mini`
2. **Testing:** Use `gpt-4o-mini` for rapid iteration
3. **Production:** Consider `gpt-4o` if quality critical
4. **Cost-Sensitive:** Stick with `gpt-4o-mini`

## 🚨 **Troubleshooting Rate Limits**

If you still hit rate limits with mini:

1. **Check your OpenAI usage:**
   - Visit: https://platform.openai.com/usage
   - Check tokens/min usage

2. **Reduce max_handoffs:**
```python
agency = create_development_agency(
    model="gpt-4o-mini",
    max_handoffs=5  # Lower = fewer API calls
)
```

3. **Use shorter system prompts:**
   - Edit agent instructions to be more concise

4. **Add delays between requests:**
```python
import time
time.sleep(1)  # 1 second delay
```

## 📝 **Summary**

**Current Setup:**
- ✅ All agency files use **gpt-4o-mini**
- ✅ No more rate limit errors
- ✅ Fast, cheap, reliable

**To Change Models:**
- Edit `MODEL = "gpt-4o-mini"` in `config_agency.py`
- Or edit the `model=` parameter in agency files

**Recommended:**
- **Development:** gpt-4o-mini
- **Production:** Your choice (mini is usually fine!)

Enjoy building with no rate limit issues! 🎉
