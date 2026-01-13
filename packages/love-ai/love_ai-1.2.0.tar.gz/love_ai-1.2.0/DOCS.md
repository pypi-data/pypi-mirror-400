# 📚 LOVE AI - Official Documentation

## 🚀 Installation

### From Source (Current)
Since the package is in development, install it locally:

```bash
git clone https://github.com/love-ai-engine/love-ai.git
cd love-ai
pip install -e .
```

### With API Support
If you want to use the Google Gemini integration for accurate emotional stress analysis:

```bash
pip install -e .[api]
```
*Note: You will need to set the `GOOGLE_API_KEY` environment variable.*

---

## ⚡ Core API

### 1. `is_allowed()`
The simplest way to use the engine. Returns `True` or `False`.

```python
from love_ai import is_allowed

# Syntax
# is_allowed(filepath, action_description, user="unknown")

if is_allowed("thesis.pdf", "delete this file", user="jorge"):
    print("Action permitted")
    # perform action...
else:
    print("Action blocked by LOVE AI")
```

### 2. `decide()`
Returns the full decision object with metrics (Entropy, Stress, Risk). Useful for debugging or logging.

```python
from love_ai import decide

result = decide(
    filepath="config/production.yaml",
    prompt="overwrite configuration",
    user="admin"
)

# Accessing the response
if result["allowed"]:
    print("✅ Approved")
else:
    print(f"🛑 Blocked: {result['reason']}")

# Inspecting metrics
print(f"Entropy: {result['metrics']['entropy']} bits")
print(f"Stress:  {result['metrics']['stress']}")
print(f"Risk:    {result['metrics']['total_risk']}")
```

---

## ⚙️ Configuration (`heart.txt`)

You can customize the engine's sensitivity by creating a file named `heart.txt` in your project's root directory.

**Default Values:**

```ini
# Informational Complexity
# Files with entropy > 3.5 bits are considered "meaningful"
H_THRESHOLD: 3.5

# Maximum Risks
# 0.0 = Block everything, 1.0 = Allow everything
RISK_MAX: 0.75
OMEGA_MAX: 0.8  # Max allowed user stress (0.0 to 1.0)

# Weights
# How much the file's fragility matters vs. context
FRAGILITY_WEIGHT: 0.7
CONTEXT_WEIGHT: 0.3

# Safety Features
ALLOW_DESTRUCTIVE_CURIOSITY: FALSE
AXIOM_02: TRUE  # Enable history tracking
```

To use a custom config file:

```python
decide("file.txt", "delete", config_path="my_custom_heart.txt")
```

---

## 🧠 Understanding the Metrics

When you run `decide()`, you get the following metrics:

| Metric | Description | Range |
| :--- | :--- | :--- |
| **Entropy (H)** | How complex/unique the file is. High entropy = fragile. | 0.0 - 8.0+ |
| **Stress (Ω)** | How upset/rushed the user seems. | 0.0 - 1.0 |
| **Cluster** | Does this file look like it belongs to other files nearby? | 0.0 - 1.0 |
| **Bias** | Adjustment based on past errors. Positive = more cautious. | -∞ to +∞ |
| **Total Risk** | The final calculated risk score. | 0.0 - 1.0 |

---

## 💾 Persistence & Learning

The engine creates two files in your working directory to "remember" context:

1.  `psi_history.json`: Stores past errors (False Positives/Negatives) to adjust the **Bias**.
2.  `rate_limit.json`: Prevents brute-force attempts.

### Reporting Errors (Feedback Loop)

You can teach the system if it makes a mistake:

```python
from love_ai.persistence import report_false_positive, report_false_negative

# CASE 1: System blocked something safe (False Positive)
# The system will lower its anxiety (bias decreases)
report_false_positive("harmless_log.txt")

# CASE 2: System allowed something bad (False Negative)
# The system will increase its anxiety (bias increases)
report_false_negative("critical_db.sql", "Database was lost")
```

---

## 🛡️ Error Handling

The system is designed to fail safely (fail-closed). If an error occurs during analysis (e.g., API failure), it defaults to **high stress** to prevent damage.

```python
try:
    result = decide(...)
except Exception as e:
    # This rarely happens, decide() usually handles exceptions internally
    print("Engine failure, defaulting to block.")
```
