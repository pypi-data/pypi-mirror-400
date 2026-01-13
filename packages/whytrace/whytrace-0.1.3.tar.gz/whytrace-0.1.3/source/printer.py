def print_header(func_name):
    print("\nDecision Path")
    print("─────────────")
    print(f"{func_name}()")


def print_condition(condition, result, context):
    icon = "✅ True" if result else "❌ False"
    print(f" └─ if {condition.source} → {icon}")

    for var in condition.variables:
        value = context.get(var, "<undefined>")
        print(f"     ├─ {var} = {value}")
