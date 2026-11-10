"""
Automata Lab Task 4 — Restricted Infinite-Loop Analyzer
This educational analyzer uses conservative AST heuristics. It is NOT a
general halting decider and must not be presented as one.
"""
import ast
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class Finding:
    severity: str
    category: str
    line: int
    message: str
    evidence: str

class LoopAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.findings: List[Finding] = []

    def visit_While(self, node: ast.While):
        # Rule 1: literal-true condition with no break that exits this loop.
        literal_true = isinstance(node.test, ast.Constant) and node.test.value is True
        literal_one = isinstance(node.test, ast.Constant) and node.test.value == 1
        if literal_true or literal_one:
            if not self._has_break_for_this_loop(node.body):
                self.findings.append(Finding(
                    "HIGH", "constant-true-loop", node.lineno,
                    "The loop condition is always true and no break targeting this loop was found.",
                    ast.unparse(node.test)
                ))
            else:
                self.findings.append(Finding(
                    "INFO", "constant-true-loop-with-break", node.lineno,
                    "A constant-true loop contains a possible exit; termination depends on reachability.",
                    ast.unparse(node.test)
                ))
        else:
            # Rule 2: simple-name condition whose variable is never assigned
            # anywhere in the current loop body (excluding nested scopes).
            names = {n.id for n in ast.walk(node.test) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
            assigned = self._assigned_names(node.body)
            unchanged = sorted(names - assigned)
            if names and unchanged:
                self.findings.append(Finding(
                    "MEDIUM", "condition-variable-not-updated", node.lineno,
                    "Condition variable(s) are not assigned in this loop body; the condition may remain unchanged.",
                    ", ".join(unchanged)
                ))
        self.generic_visit(node)

    def _has_break_for_this_loop(self, statements):
        for stmt in statements:
            if isinstance(stmt, ast.Break):
                return True
            # A break inside a nested loop belongs to that nested loop.
            if isinstance(stmt, (ast.For, ast.While, ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                continue
            for child in ast.iter_child_nodes(stmt):
                if isinstance(child, ast.Break):
                    return True
                if isinstance(child, (ast.For, ast.While, ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                    continue
                if self._has_break_for_this_loop([child]):
                    return True
        return False

    def _assigned_names(self, statements):
        assigned = set()
        class AssignmentVisitor(ast.NodeVisitor):
            def visit_Name(self, n):
                if isinstance(n.ctx, (ast.Store, ast.Del)):
                    assigned.add(n.id)
            def visit_FunctionDef(self, n): pass
            def visit_AsyncFunctionDef(self, n): pass
            def visit_Lambda(self, n): pass
            def visit_ClassDef(self, n): pass
        v = AssignmentVisitor()
        for stmt in statements:
            # Do not count assignments inside nested loops as proof that the
            # outer loop's condition variable is updated on every iteration.
            if isinstance(stmt, (ast.For, ast.While, ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                continue
            v.visit(stmt)
        return assigned

def analyze_source(source: str) -> Dict[str, Any]:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {
            "status": "INVALID_SYNTAX",
            "summary": f"Python syntax error at line {exc.lineno}: {exc.msg}",
            "findings": []
        }
    visitor = LoopAnalyzer()
    visitor.visit(tree)
    findings = [asdict(x) for x in visitor.findings]
    if any(f["severity"] == "HIGH" for f in findings):
        status = "HIGH_RISK_PATTERN"
        summary = "A strong non-termination pattern was found. Review control flow before execution."
    elif any(f["severity"] == "MEDIUM" for f in findings):
        status = "POTENTIAL_RISK"
        summary = "A loop condition may remain unchanged. This heuristic is not a proof."
    elif findings:
        status = "REVIEW"
        summary = "A loop exit exists syntactically, but reachability has not been proved."
    else:
        status = "NO_PATTERN_FOUND"
        summary = "No supported risk pattern was found. This does NOT prove that the program halts."
    return {"status": status, "summary": summary, "findings": findings}

def bounded_deterministic_monitor(initial_state, transition, max_steps=100):
    """
    Exact cycle detection for a deterministic finite-state transition system,
    provided states have stable equality/hash behaviour.
    transition(state) returns next_state or None to indicate termination.
    """
    seen = {}
    state = initial_state
    trace = []
    for step in range(max_steps + 1):
        if state is None:
            return {"status": "TERMINATED", "steps": step, "trace": trace}
        if state in seen:
            return {
                "status": "CYCLE_DETECTED",
                "steps": step,
                "cycle_start": seen[state],
                "cycle_length": step - seen[state],
                "trace": trace
            }
        if step == max_steps:
            return {"status": "STEP_LIMIT_REACHED", "steps": step, "trace": trace}
        seen[state] = step
        trace.append(state)
        state = transition(state)
    return {"status": "STEP_LIMIT_REACHED", "steps": max_steps, "trace": trace}

if __name__ == "__main__":
    demo = """i = 0
while i < 5:
    print(i)
"""
    print(json.dumps(analyze_source(demo), indent=2))
