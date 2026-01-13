from rich.tree import Tree
from rich.text import Text
from rich.console import Console
import ast
import io
import contextlib
from .analyzer import FlowNode
from .evaluator import eval_boolop

console = Console()


class RichDecisionRenderer:
    def __init__(self, func_name):
        self.tree = Tree(
            Text(f"{func_name}()", style="bold cyan"),
            guide_style="bright_blue",
        )

    def render_decision(self, node, context, parent):

        # FLOW NODE
        if isinstance(node, FlowNode):
            self.render_flow(node, parent)
            return

        # ELSE branch
        if node.node_type == "else":
            parent.add(Text("else", style="yellow"))
            return

        # BOOL OP (short-circuit)
        if isinstance(node.test, ast.BoolOp):
            branch = parent.add(Text(f"{node.node_type} {node.source}", style="white"))
            result, steps, stopped_at = eval_boolop(node.test, context)

            for expr, value in steps:
                icon = "✅" if value else "❌"
                color = "green" if value else "red"
                branch.add(Text(f"{expr} → {icon}", style=color))

            if stopped_at:
                branch.add(
                    Text(f"⛔ Short-circuited at {stopped_at}", style="bold red")
                )
        else:
            try:
                result = eval(node.source, {}, context)
                icon = "✅" if result else "❌"
                color = "green" if result else "red"
                branch = parent.add(
                    Text(f"{node.node_type} {node.source} → {icon}", style=color)
                )
            except Exception:
                parent.add(
                    Text(
                        f"{node.node_type} {node.source} → ⚠ depends on runtime (not evaluable)",
                        style="yellow",
                    )
                )
                return



        if result:
            for child in node.children:
                if isinstance(child, FlowNode):
                    self.render_flow(child, branch)

                    if child.kind == "break":
                        branch.add(Text("⛔ loop exits here", style="red"))
                        return

                    if child.kind == "continue":
                        branch.add(Text("↩ continue to next iteration", style="yellow"))
                        return
                else:
                    self.render_decision(child, context, branch)
        elif node.orelse:
            self.render_decision(node.orelse, context, parent)


    def render_loop(self, loop, context):
        loop_branch = self.tree.add(
            Text(f"for {loop.target} in {loop.iterable}", style="cyan")
        )

        iterable = eval(loop.iterable, {}, context)

        for idx, value in enumerate(iterable):
            context[loop.target] = value

            iter_branch = loop_branch.add(
                Text(f"iteration {idx} → {loop.target} = {value}", style="dim")
            )

            # 🔥 Render nested logic INSIDE iteration
            for stmt in loop.body:
                self.render_decision(stmt, context, iter_branch)

    def show(self):
        console.print(self.tree)

    def _render_effects(self, node, context, parent):
        for effect in getattr(node, "effects", []):
            if isinstance(effect, ast.Expr):
                expr = ast.unparse(effect.value)

                exec_branch = parent.add(
                    Text("▶ Executed", style="bold yellow")
                )
                exec_branch.add(Text(expr, style="white"))
                if expr.startswith("print"):
                    try:
                        buf = io.StringIO()
                        with contextlib.redirect_stdout(buf):
                            eval(expr, {}, context)
                        output = buf.getvalue().strip()
                        exec_branch.add(Text(f"Output: {output}", style="green"))
                    except NameError:
                        exec_branch.add(
                            Text("Output: <depends on local state>", style="yellow")
                        )

    def render_flow(self, node, parent):
        style = {
            "break": "bold red",
            "continue": "bold yellow",
            "pass": "dim",
        }.get(node.kind, "white")

        parent.add(Text(node.kind, style=style))

    def render_while(self, loop, context, max_iter=10):
        loop_branch = self.tree.add(
            Text(f"while {loop.source}", style="cyan")
        )

        iteration = 0

        while True:
            if iteration >= max_iter:
                loop_branch.add(
                    Text("⛔ stopped (max iterations)", style="bold red")
                )
                break

            result = eval(loop.source, {}, context)

            if not result:
                loop_branch.add(
                    Text("condition → ❌ False (exit)", style="red")
                )
                break

            iter_branch = loop_branch.add(
                Text(f"iteration {iteration}", style="dim")
            )

            for stmt in loop.body:
                if isinstance(stmt, FlowNode):
                    self.render_flow(stmt, iter_branch)
                    if stmt.kind == "break":
                        iter_branch.add(Text("⛔ loop terminated", style="red"))
                        return
                    if stmt.kind == "continue":
                        iter_branch.add(Text("↩ next iteration", style="yellow"))
                        break
                else:
                    self.render_decision(stmt, context, iter_branch)

            iteration += 1

