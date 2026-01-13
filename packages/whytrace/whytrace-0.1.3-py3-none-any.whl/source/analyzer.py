import ast


class DecisionNode:
    def __init__(self, test=None, node_type="if"):
        self.test = test
        self.node_type = node_type
        self.children = []
        self.orelse = None
        self.source = ast.unparse(test) if test else "else"
        self.effects = []


class LoopNode:
    def __init__(self, target, iterable, body):
        self.target = ast.unparse(target)
        self.iterable = ast.unparse(iterable)
        self.body = body

class WhileLoopNode:
    def __init__(self, test, body):
        self.test = test
        self.source = ast.unparse(test)
        self.body = body


class FlowNode:
    def __init__(self, kind):
        self.kind = kind  # break | continue | pass


class DecisionTreeBuilder(ast.NodeVisitor):
    def __init__(self):
        self.nodes = []

    def visit_For(self, node):
        body_nodes = []

        for stmt in node.body:
            if isinstance(stmt, ast.If):
                body_nodes.append(self._build_if(stmt))

        self.nodes.append(LoopNode(node.target, node.iter, body_nodes))

    def visit_If(self, node):
        self.nodes.append(self._build_if(node))

    def _build_if(self, node):
        decision = DecisionNode(node.test, "if")

        for stmt in node.body:
            if isinstance(stmt, ast.If):
                decision.children.append(self._build_if(stmt))
            elif isinstance(stmt, (ast.Break, ast.Continue, ast.Pass)):
                decision.children.append(
                    FlowNode(stmt.__class__.__name__.lower())
                )

        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                decision.orelse = self._build_if(node.orelse[0])
                decision.orelse.node_type = "elif"
            else:
                decision.orelse = DecisionNode(None, "else")

                for stmt in node.orelse:
                    if isinstance(stmt, (ast.Break, ast.Continue, ast.Pass)):
                        decision.orelse.children.append(
                            FlowNode(stmt.__class__.__name__.lower())
                        )

        return decision

    def visit_While(self, node):
        body_nodes = []

        for stmt in node.body:
            if isinstance(stmt, ast.If):
                body_nodes.append(self._build_if(stmt))
            elif isinstance(stmt, (ast.Break, ast.Continue, ast.Pass)):
                body_nodes.append(FlowNode(stmt.__class__.__name__.lower()))

        self.nodes.append(WhileLoopNode(node.test, body_nodes))


