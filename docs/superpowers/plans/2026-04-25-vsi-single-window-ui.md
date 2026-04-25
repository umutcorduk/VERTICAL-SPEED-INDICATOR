# VSI Single Window UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the separate terminal input flow with a single Tkinter window that includes an integrated, user-friendly control panel.

**Architecture:** Keep the gauge drawing logic in `vsi.py`, but remove the terminal thread and drive all value changes through a single UI update path. Add small pure helper functions for parsing, clamping, and formatting so the input behavior is testable without launching Tkinter.

**Tech Stack:** Python 3, Tkinter, unittest

---

### Task 1: Add testable input helpers

**Files:**
- Modify: `C:\Users\Administrator\Desktop\abla proje\VERTICAL-SPEED-INDICATOR\vsi.py`
- Create: `C:\Users\Administrator\Desktop\abla proje\VERTICAL-SPEED-INDICATOR\test_vsi.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest

from vsi import clamp_value, parse_fpm_input


class InputHelperTests(unittest.TestCase):
    def test_parse_accepts_numeric_text(self):
        self.assertEqual(parse_fpm_input("1500"), 1500.0)

    def test_parse_rejects_invalid_text(self):
        with self.assertRaises(ValueError):
            parse_fpm_input("abc")

    def test_clamp_limits_large_values(self):
        self.assertEqual(clamp_value(7100), 6000)
        self.assertEqual(clamp_value(-7100), -6000)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test_vsi.py -v`
Expected: FAIL with import or missing function errors for `clamp_value` and `parse_fpm_input`

- [ ] **Step 3: Write minimal implementation**

```python
MIN_FPM = -6000
MAX_FPM = 6000


def clamp_value(value):
    return max(MIN_FPM, min(MAX_FPM, value))


def parse_fpm_input(text):
    return float(text.strip())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test_vsi.py -v`
Expected: PASS

### Task 2: Replace terminal input with a control panel

**Files:**
- Modify: `C:\Users\Administrator\Desktop\abla proje\VERTICAL-SPEED-INDICATOR\vsi.py`
- Test: `C:\Users\Administrator\Desktop\abla proje\VERTICAL-SPEED-INDICATOR\test_vsi.py`

- [ ] **Step 1: Write the failing test**

```python
def test_status_message_formats_clamped_value(self):
    self.assertEqual(
        build_status_message(6500),
        "Hedef dikey hiz 6000 FPM olarak ayarlandi.",
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test_vsi.py -v`
Expected: FAIL with missing `build_status_message`

- [ ] **Step 3: Write minimal implementation**

```python
def build_status_message(value):
    return f"Hedef dikey hiz {int(clamp_value(value))} FPM olarak ayarlandi."
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test_vsi.py -v`
Expected: PASS

- [ ] **Step 5: Refactor the Tkinter window**

```python
root.protocol("WM_DELETE_WINDOW", root.destroy)

main_frame = tk.Frame(root, bg="#10141c")
gauge_frame = tk.Frame(main_frame, bg="#151515")
control_frame = tk.Frame(main_frame, bg="#1b2230")

self.input_var = tk.StringVar(value="0")
self.scale_var = tk.DoubleVar(value=0.0)
self.status_var = tk.StringVar(value="Hazir")
```

Add:
- entry + `Uygula`
- `Sifirla`
- slider bound to the same target setter
- quick preset buttons
- current value label and status message

- [ ] **Step 6: Run verification**

Run: `python -m unittest test_vsi.py -v`
Expected: PASS

Run: `python vsi.py`
Expected: One GUI window opens with integrated controls and no separate terminal input prompt
