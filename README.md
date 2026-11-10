# Automata Lab — Task 4: Infinite Loop Detection

An educational case study connecting software infinite-loop detection to Turing machines, the Halting Problem, decidability, static analysis, and runtime monitoring.

## Project structure
- `web/index.html` — interactive dashboard (open directly in a browser)
- `src/loop_analyzer.py` — restricted Python AST analyzer and finite-state cycle monitor
- `src/demo.py` — runnable demonstrations
- `tests/test_analyzer.py` — unit tests
- `diagrams/` — Mermaid source diagrams
- `report.md` — report source

## Run
Python 3.9+ recommended.

```bash
python src/demo.py
python -m unittest discover -s tests -v
```

Open `web/index.html` in a browser for the interactive dashboard.

## Scope and limitations
This is deliberately a restricted-case educational analyzer, not a general halting decider. It detects selected syntactic patterns. A finding is a warning that requires review; absence of a finding does not prove termination. The bounded monitor is exact only for a deterministic finite-state transition system with stable, hashable states.

## GitHub
Suggested repository: `Infinite-Loop-Detection-AutomataLab`

```bash
git init
git add .
git commit -m "Add Automata Lab Task 4 - Infinite Loop Detection"
git branch -M main
git remote add origin https://github.com/Harshit100306/Infinite-Loop-Detection-AutomataLab.git
git push -u origin main
```
