# Automata Lab — Task 4
## Formal Language and Automata-Based Real-World Problem Solving and System Design
### Case Study: Infinite Loop Detection in Software

**Course:** 21CSC301T — Formal Language and Automata  
**Programme:** B.Tech. Artificial Intelligence and Machine Learning  
**Department:** Artificial Intelligence and Machine Learning  
**Semester:** V | **Academic Year:** 2026–2027  
**Faculty Handling:** Dr. C. Gunasundari (AP)  
**Assessment:** Task 4 — Team Work | **Maximum Marks:** 10  
**SDG:** 9 — Industry, Innovation and Infrastructure  
**Student:** Harshit Parmar | **Registration No.:** RA2411026050026  
**Suggested GitHub repository:** `Infinite-Loop-Detection-AutomataLab`

> Team member names, registration numbers, individual contributions, and presentation evidence should be completed by the team before submission.

---

## Abstract
An infinite loop is a program execution that continues indefinitely without reaching a designated termination state. Detecting such behaviour is important in software reliability, resource management, embedded systems, and service availability. The central theoretical result is that no algorithm can decide, for every arbitrary program and input, whether execution will eventually halt. This is the Halting Problem, established through Turing-machine computability theory. This report formulates the problem, explains the undecidability result and the distinction between decidability and recognizability, and proposes an engineering workaround based on restricted static analysis, bounded execution, finite-state cycle detection, tests, and timeouts. A Python AST prototype and interactive dashboard demonstrate useful restricted cases without claiming to solve the general undecidable problem.

## 1. Problem understanding
### 1.1 Real-world problem
Consider a software service that processes a request inside a loop. If the loop condition never becomes false and no reachable exit is executed, the request may consume CPU time indefinitely. Consequences include blocked threads, delayed responses, battery drain, missed real-time deadlines, and denial of service.

### 1.2 Computational formulation
Let `P` be a program and `x` an input. The decision problem is:

**HALT = { ⟨P, x⟩ | P eventually halts when executed on input x }**

The question is whether there exists a total algorithm that always returns the correct answer “halts” or “does not halt” for every valid pair `⟨P,x⟩`.

### 1.3 Assumptions
- Programs are represented by finite descriptions.
- Execution follows a well-defined operational semantics.
- “Halts” means reaches a designated final/terminal configuration.
- The general result concerns unrestricted computational programs, not a particular programming language syntax.
- Practical prototype rules operate on a deliberately limited subset of Python loop patterns.

## 2. Formal model: Turing machine
A deterministic Turing machine can be represented as:

**M = (Q, Σ, Γ, δ, q₀, q_accept, q_reject)**

where:
- `Q` is a finite set of states.
- `Σ` is the input alphabet.
- `Γ` is the tape alphabet, with `Σ ⊆ Γ`.
- `δ : Q × Γ → Q × Γ × {L,R}` is the transition function.
- `q₀` is the initial state.
- `q_accept` and `q_reject` are halting states.

A configuration records the current state, tape contents, and head position. A computation is a sequence of configurations:

**C₀ ⊢ C₁ ⊢ C₂ ⊢ …**

The machine halts if it reaches a designated halting state. Otherwise, it may continue forever.

### 2.1 Mapping to software
| Software concept | Computability concept |
|---|---|
| Program source and input | TM description and input string |
| Program execution state | TM configuration |
| One instruction step | One transition |
| Return/exit | Halting configuration |
| Infinite execution | Infinite transition sequence |
| Loop detector | Proposed decision procedure for halting |

## 3. Why general exact detection is undecidable
Assume, for contradiction, that a perfect decider `H(P,x)` exists. It always halts and answers:
- YES if program `P` halts on input `x`;
- NO if program `P` does not halt on input `x`.

Construct a program `D(P)` that does the opposite of the prediction `H(P,P)`:
- if `H(P,P)` says that `P` halts on itself, `D` loops forever;
- if `H(P,P)` says that `P` does not halt on itself, `D` halts immediately.

Now execute `D` on its own description, `D(D)`. If `H(D,D)` predicts halting, the construction makes `D(D)` loop. If it predicts non-halting, the construction makes `D(D)` halt. Both possibilities contradict the assumed correctness of `H`.

Therefore, no total algorithm can decide the Halting Problem for all arbitrary program-input pairs.

**Conclusion:** a project must not claim to perfectly detect every infinite loop in every possible program.

## 4. Decidability and recognizability
A language is **decidable** if a Turing machine halts on every input and correctly accepts members and rejects non-members.

A language is **recognizable** if a Turing machine accepts every member, but on a non-member it may reject or run forever.

The Halting language is recognizable: simulate `P(x)` and accept if it halts. If it never halts, the simulation itself continues forever. However, the complement of the Halting language is not recognizable in the unrestricted setting. Consequently, there is no recognizer that will always confirm non-halting by eventually accepting every non-halting instance.

## 5. Worked examples
### Example A — obvious constant-true loop
```python
while True:
    print("still running")
```
The condition is always true. If no reachable `break`, exception, or external termination mechanism exits the loop, the loop does not terminate under the assumed execution model. A syntax-based tool can flag this pattern.

### Example B — condition variable is unchanged
```python
i = 0
while i < 5:
    print(i)
```
The body does not modify `i`. Since `i` starts at zero and remains zero, `i < 5` remains true. This is a restricted case where simple data-flow reasoning can establish the loop behaviour.

### Example C — counter is updated
```python
i = 0
while i < 5:
    print(i)
    i += 1
```
The variable increases on each iteration. Under ordinary integer semantics, the condition eventually becomes false. The prototype does not need to flag this pattern.

### Example D — syntactic break
```python
while True:
    if ready():
        break
    wait()
```
A `break` is syntactically present, but whether it is reached depends on `ready()` and program state. Merely finding `break` is not a proof of termination.

## 6. Proposed restricted-case engineering solution
The project uses two complementary techniques.

### 6.1 Static AST analysis
The Python prototype parses source code into an Abstract Syntax Tree and applies limited rules:
1. Flag `while True` or `while 1` when no `break` targeting that loop is found syntactically.
2. Flag a simple loop when a variable used in its condition is not assigned in the loop body.
3. Report syntax errors separately.
4. Return “no supported pattern found” when no rule fires, explicitly avoiding a claim that the program halts.

These rules are intentionally conservative and incomplete. They do not solve arbitrary aliasing, function calls, exceptions, concurrency, indirect state changes, or complex control flow.

### 6.2 Bounded deterministic finite-state monitor
For a deterministic finite-state transition system with a finite state space, store every visited state:
- If a terminal state is reached, report termination.
- If a state repeats, deterministic behaviour guarantees that the same future sequence repeats; report a cycle.
- If the step limit is reached before either event, report “step limit reached,” not “infinite loop.”

This method is exact for the stated finite-state model, but does not make general Python program termination decidable.

## 7. Prototype architecture
| Component | Input | Method | Output |
|---|---|---|---|
| Python parser | Source code | `ast.parse` | Syntax tree / syntax error |
| Static rule engine | AST | Pattern and assignment checks | Risk findings |
| Finite-state monitor | Initial state and transition function | Visited-state set | Terminated / cycle / limit |
| Dashboard | User-entered snippet | Demonstration rules | Visual explanation |
| Unit tests | Known examples | Assertions | Validation evidence |

### 7.1 Result interpretation
| Status | Meaning |
|---|---|
| `HIGH_RISK_PATTERN` | Constant-true loop without a visible exit was found |
| `POTENTIAL_RISK` | A condition variable may remain unchanged |
| `REVIEW` | A visible break exists, but reachability is unproved |
| `NO_PATTERN_FOUND` | No supported pattern found; termination is not proved |
| `INVALID_SYNTAX` | The input could not be parsed as Python |

## 8. Validation plan and test cases
The project includes unit tests for:
- constant-true loop without break;
- unchanged condition variable;
- counter update;
- invalid Python syntax;
- repeated state in a finite-state transition system;
- terminal state reached in a finite-state transition system.

Run:
```bash
python -m unittest discover -s tests -v
```
The report should be accompanied by a screenshot of the actual test output after the team runs the tests on its machine.

## 9. Practical implications for software/system design
No single technique guarantees detection of every non-terminating execution. Real systems therefore use layered safeguards:
- static analysis and code review before deployment;
- unit, integration, and property-based testing;
- execution timeouts and watchdog timers;
- CPU, memory, and request quotas;
- cancellation and cooperative interruption;
- telemetry and alerts for unusually long-running tasks;
- finite-state verification for components whose state space can be bounded.

Timeouts do not prove that a program would never halt; they establish an operational limit for a particular run. Similarly, testing can find bugs but cannot exhaustively cover every possible input of an unrestricted program.

## 10. SDG 9 alignment
Reliable software infrastructure supports resilient systems and innovation. Detecting selected infinite-loop patterns, monitoring execution time, and applying resource limits can improve service availability and operational reliability. The project demonstrates Level 2 Design Alignment by translating a theoretical limitation into a practical, bounded engineering workflow.

## 11. Limitations and future enhancements
- The AST rules cover only simple patterns.
- The browser dashboard is an explanatory demonstration; the Python AST analyzer is the project implementation.
- The analyzer does not prove termination or non-termination for arbitrary programs.
- Future work could add control-flow graphs, richer data-flow analysis, configurable timeouts, and a sandboxed runner for carefully controlled toy programs.

## 12. Conclusion
The Halting Problem establishes a fundamental boundary: universal exact infinite-loop detection for arbitrary programs is undecidable. This does not make practical loop analysis useless. By narrowing the scope, a tool can identify selected suspicious patterns, detect cycles in finite deterministic models, and combine static checks with testing and runtime safeguards. The Automata Lab prototype illustrates how computability theory informs responsible software engineering.

## 13. Team contribution statement
Complete this section truthfully before submission.

| Team member | Registration number | Contribution |
|---|---|---|
| Harshit Parmar | RA2411026050026 | Formal model, implementation, validation, documentation |
| Member 2 | Add ID | Add actual contribution |
| Member 3 | Add ID | Add actual contribution |

## 14. Presentation evidence checklist
- [ ] Screenshot of dashboard opened in browser
- [ ] Screenshot showing constant-true loop analysis
- [ ] Screenshot showing counter-update example
- [ ] Screenshot of Python unit tests passing
- [ ] GitHub repository URL added after publishing
- [ ] Team contribution statement completed

## References
1. A. M. Turing, “On Computable Numbers, with an Application to the Entscheidungsproblem,” *Proceedings of the London Mathematical Society*, 1936.
2. M. Sipser, *Introduction to the Theory of Computation*, 3rd ed., Cengage Learning, 2012.
3. J. E. Hopcroft, R. Motwani, and J. D. Ullman, *Introduction to Automata Theory, Languages, and Computation*, 3rd ed., Pearson, 2006.
4. Python Software Foundation, “`ast` — Abstract Syntax Trees,” Python documentation, https://docs.python.org/3/library/ast.html.
