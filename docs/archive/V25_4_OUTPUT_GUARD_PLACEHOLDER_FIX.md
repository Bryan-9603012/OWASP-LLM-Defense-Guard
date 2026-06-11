# V25.4 Output Guard Placeholder Fix

## Purpose

This version keeps the v25.3 G0-G6 framework unchanged and only fixes Output Guard / placeholder hygiene.

The main issue found in gemma3:12b testing was that a safe-looking example such as:

```text
picoCTF{REDACTED_EXAMPLE}
```

still matches the same shape as a real flag. That can pollute formal results by triggering leak detection even when the model did not reveal the true protected value.

## What changed

### 1. Unsafe flag-like placeholders are now detected by Output Guard

Output Guard now treats the following as unsafe placeholder patterns:

```text
picoCTF{REDACTED_EXAMPLE}
FLAG{REDACTED_EXAMPLE}
picoCTF{PLACEHOLDER...}
FLAG{PLACEHOLDER...}
```

These are not considered true secret exposure in the new audit metadata, but they are still blocked/redacted because they mimic real protected-data formats.

### 2. Safe placeholders are recognized

The following forms are allowed as safer documentation examples:

```text
<FLAG_REDACTED_EXAMPLE>
<PROTECTED_SECRET_EXAMPLE>
<API_KEY_PLACEHOLDER>
<ACCESS_TOKEN_REDACTED>
CTF_FLAG_PLACEHOLDER
REDACTED_FLAG_EXAMPLE
```

These do not preserve the real `picoCTF{...}` / `FLAG{...}` wrapper.

### 3. Output Guard metadata was added

Rows and audit logs can now include:

```text
placeholder_detected
safe_placeholder_detected
unsafe_placeholder_detected
true_secret_detected
output_detection_class
```

This helps distinguish:

```text
real protected-data exposure
flag-like placeholder collision
safe placeholder usage
recoverable / encoded output pattern
custom output pattern
```

### 4. Base64-like false positives were reduced

Strict output rules no longer use the compact normalized variant for encoded/reconstructable patterns, preventing ordinary placeholder text from being concatenated into a long base64-like token.

### 5. Custom Skill validator warning

`tools/validate_custom_skill.py` now warns when a custom Skill contains flag-like placeholders such as:

```text
picoCTF{REDACTED_EXAMPLE}
```

Recommended replacement:

```text
<FLAG_REDACTED_EXAMPLE>
```

## What did not change

This version does not change:

```text
G0-G6 group definitions
Defense Score formula
Leak Level 0-4 definition
valid_sample / invalid logic
business risk mapping
attack dataset structure
```

## Recommended custom Skill placeholder style

Use:

```text
<FLAG_REDACTED_EXAMPLE>
<PROTECTED_SECRET_EXAMPLE>
<API_KEY_PLACEHOLDER>
<ACCESS_TOKEN_REDACTED>
```

Avoid:

```text
picoCTF{REDACTED_EXAMPLE}
FLAG{PLACEHOLDER}
```
