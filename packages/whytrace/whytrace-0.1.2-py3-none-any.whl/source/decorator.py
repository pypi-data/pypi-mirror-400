import inspect
import textwrap
import ast
from functools import wraps

from .analyzer import DecisionTreeBuilder, LoopNode, WhileLoopNode, FlowNode
from .rich_printer import RichDecisionRenderer


def why(func):
    source = textwrap.dedent(inspect.getsource(func))
    tree = ast.parse(source)

    builder = DecisionTreeBuilder()
    builder.visit(tree)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            context = dict(bound.arguments)

            renderer = RichDecisionRenderer(func.__name__)

            for node in builder.nodes:
                if isinstance(node, LoopNode):
                    renderer.render_loop(node, context)
                else:
                    renderer.render_decision(node, context, renderer.tree)

            renderer.show()

        except Exception as e:
            print(
                f"[whytrace] ❌ visualization skipped due to unsupported logic"
            )

        return func(*args, **kwargs)

    return wrapper

