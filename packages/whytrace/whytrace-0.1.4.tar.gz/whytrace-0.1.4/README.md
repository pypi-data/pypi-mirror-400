## whytrace

Explain and visualize why your Python function took a particular control-flow path for a given set of inputs.

`whytrace` helps evaluate your `if` / `elif` / `else` conditions (including short-circuiting `and`/`or`), and renders a rich, human-friendly decision tree. It also steps through loops, showing per-iteration state and flow-control (`break`, `continue`, `pass`) so you can quickly see what executed and why.

---

## Features

- **Decorator-based**: Add `@why` and call your function as usual.
- **Rich console tree**: Clear, colorized decision diagrams using `rich`.
- **Condition insight**: Shows boolean short-circuiting (`and`/`or`) step-by-step.
- **Flow control**: Displays `break`, `continue`, and `pass` exactly where they occur.
- **Zero app logic changes**: Your function still runs and returns its normal result.

---

## Installation

This project currently targets Python 3.9+

```bash
pip install whytrace
```

---

## Quickstart

```python
from whytrace import why

@why
def check_user(user):
    if user["is_active"] and user["age"] > 18:
        if user["age"] > 21:
            return "ALLOW"
    else:
        return "DENY"

result = check_user({"is_active": False, "age": 16})
print("Result:", result)
```

Example console output (trimmed):

```
check_user()
└── if user["is_active"] and user["age"] > 18
    ├── user["is_active"] → ❌
    └── ⛔ Short-circuited at user["is_active"]
└── else
```

## Conditional Looping

```python

@why
def process(items, user):
    for i in items:
        if user["active"] and i > 3:
            print("Active user")
        elif user["banned"]:
            print("blocked")
            continue
        else:
            print("skip")


process(
    items=[1, 4, 7],
    user={"active": True, "banned": True},
)

```

Example console output (trimmed):

```
process()
└── for i in items
    ├── iteration 0 → i = 1
    │   ├── if user['active'] and i > 3
    │   │   ├── user['active'] → ✅
    │   │   ├── i > 3 → ❌
    │   │   └── ⛔ Short-circuited at i > 3
    │   └── elif user['banned'] → ✅
    │       ├── continue
    │       └── ↩ continue to next iteration
    ├── iteration 1 → i = 4
    │   └── if user['active'] and i > 3
    │       ├── user['active'] → ✅
    │       └── i > 3 → ✅
    └── iteration 2 → i = 7
        └── if user['active'] and i > 3
            ├── user['active'] → ✅
            └── i > 3 → ✅
blocked
Active user
Active user

```

---

## More Examples

### Nested conditionals

See `examples/nested.py`:

```python
from whytrace import why

@why
def access_control(user, resource):
    if user["active"]:
        if resource["public"]:
            print("Access granted")
        elif user["role"] == "admin":
            print("Admin access")
        else:
            print("Access denied")
    else:
        print("Inactive user")

access_control(
    user={"active": True, "role": "user"},
    resource={"public": False}
)
```

### Loops, break/continue/pass

See `examples/loop.py`:

```python
from whytrace import why

@why
def process(items, user):
    for i in items:
        if user["active"] and i > 3:
            print("Active user")
        elif user["banned"]:
            print("blocked")
        else:
            print("skip")

process(
    items=[1, 4, 7],
    user={"active": True, "banned": True},
)
```

#### Note : Checkout examples folder for further examples



---

## Supported Constructs

- `if` / `elif` / `else`
- Boolean operations: `and`, `or` (with explicit short-circuit visibility)
- Flow nodes: `break`, `continue`, `pass`

---

## CLI-Free: Just Run Your Script

The easiest way to use `whytrace` is to decorate functions in your code and run your script normally:

```bash
python examples/credit_score.py
python examples/feature_flag.py
python examples/loop.py
python examples/multi_layer.py
python examples/nested.py
```

You’ll see a rich tree printed before the function’s return value.

---

## Contributing

Ideas and PRs welcome! Useful areas to explore:

- Support for `try`/`except` and additional control structures.
- Support for `switch` , `goto` etc
- Configurable `while` iteration caps.
- Safer evaluation strategies and richer context controls.
- Output adapters (e.g., HTML export) in addition to the console tree.


