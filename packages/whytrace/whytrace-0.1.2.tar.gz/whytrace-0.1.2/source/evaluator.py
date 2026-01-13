import ast


def eval_boolop(node, context):
    steps = []

    if isinstance(node.op, ast.And):
        for expr in node.values:
            value = eval(ast.unparse(expr), {}, context)
            steps.append((ast.unparse(expr), value))
            if not value:
                return False, steps, ast.unparse(expr)
        return True, steps, None

    if isinstance(node.op, ast.Or):
        for expr in node.values:
            value = eval(ast.unparse(expr), {}, context)
            steps.append((ast.unparse(expr), value))
            if value:
                return True, steps, ast.unparse(expr)
        return False, steps, None
