# Engineering Standards

These rules define how I want coding tasks to be approached and implemented.

The goal is not merely to produce working code.
The goal is to produce code that a strong engineer would be comfortable
maintaining, reviewing, and extending.

---

## 1. Understand Before Coding

Do not immediately modify code when given a task.

First inspect the relevant parts of the repository:

- the target files
- related callers and dependencies
- existing implementations of similar behavior
- relevant tests
- configuration or documentation when necessary

Never speculate about code that has not been inspected.

Before implementing a non-trivial change, understand:

- what the system currently does
- what the requested behavior is
- why the current behavior is insufficient
- which components are actually affected

Do not invent architecture or behavior without evidence.

---

## 2. Search Before Building

Before creating a new helper, abstraction, utility, class, or module:

1. Search the repository for existing equivalents.
2. Inspect how similar problems are already solved.
3. Prefer reusing or extending an existing appropriate abstraction.

Do not create duplicate concepts under different names.

Consistency with the existing codebase is preferred over introducing
a new personal style.

---

## 3. Choose the Simplest Correct Solution

Prefer the smallest solution that fully satisfies the requirements.

Use KISS, YAGNI, and DRY as practical guidelines.

Do not introduce:

- unnecessary abstractions
- unnecessary classes
- unnecessary helper functions
- speculative configuration
- unnecessary dependencies
- unnecessary flexibility
- new architectural layers without a real need

Do not design for hypothetical future requirements.

Optimize for clarity and maintainability, not cleverness.

---

## 4. Anti-Overengineering

Before introducing an abstraction, ask:

1. Does it remove real duplication?
2. Does it represent a meaningful domain concept?
3. Is it required by the current requirements?
4. Does it make the code easier to understand?

If not, do not introduce it.

A small amount of duplication can be preferable to a premature abstraction.

Do not turn a simple change into a framework.

Do not perform unrelated refactoring while completing a task.

---

## 5. Scope Control

Stay within the scope of the request.

A bug fix should not become a general cleanup.
A small feature should not become an architectural redesign.

Do not modify unrelated files unless there is a clear dependency.

If you discover a separate issue:

- do not silently fix it
- mention it separately
- continue with the requested task

The goal is a focused, reviewable diff.

---

## 6. Write Readable Code

Optimize for the next engineer reading the code.

Prefer:

- clear names
- straightforward control flow
- cohesive functions and modules
- explicit behavior
- consistent patterns already used by the repository

Avoid clever tricks when a simple implementation is clearer.

Do not compress code merely to reduce line count.

Do not split code into many tiny functions merely because each function
should be "small."

A unit should be extracted when the extraction improves cohesion,
reuse, testability, or readability.

---

## 7. Functions and Responsibilities

Each function, class, and module should have a clear responsibility.

Avoid mixing unrelated concerns such as:

- business logic
- data access
- formatting
- user interaction
- infrastructure concerns

However, do not create artificial layers just to satisfy a pattern.

Prefer cohesive code over excessive decomposition.

---

## 8. Comments and Documentation

Write comments to explain WHY, not WHAT.

Useful comments explain:

- non-obvious constraints
- important tradeoffs
- surprising behavior
- decisions that future maintainers might otherwise question

Do not add comments that simply restate the code.

Do not add documentation for code that was not meaningfully changed
unless the documentation is required for correctness.

---

## 9. Error Handling

Handle errors at the appropriate boundary.

Do not catch exceptions merely to suppress them.

Do not silently convert unexpected failures into successful-looking results.

At external boundaries:

- validate inputs
- handle expected failures
- provide useful error information

Inside trusted internal code:

- rely on established contracts
- avoid defensive checks for impossible states unless they protect
  against a real failure mode

Do not add error handling without understanding the ownership of the error.

---

## 10. Tests Are Part of the Work

For behavior changes:

1. inspect existing tests
2. identify what behavior should be verified
3. add or update focused tests when appropriate
4. run the relevant tests
5. investigate failures rather than assuming the test is wrong

Tests should primarily verify behavior, not implementation details.

Do not hard-code behavior merely to make tests pass.

Do not weaken or delete a test simply because the implementation fails it.

When a test exposes a real defect, fix the underlying behavior.

---

## 11. Verification

Do not declare a task complete merely because the code was written.

Before finishing, verify as much as practical:

- the requested behavior works
- relevant tests pass
- relevant lint/type checks pass when available
- no debug code remains
- no temporary files remain
- no accidental files were modified
- the final diff is focused

Use the repository's existing commands and conventions.

Do not invent new tooling when existing tooling is sufficient.

---

## 12. Review Your Own Diff

Before reporting completion, review the final changes as if reviewing
another engineer's pull request.

Ask:

- Is this actually the root-cause fix?
- Did I change more than necessary?
- Did I introduce an abstraction that is not justified?
- Did I duplicate existing functionality?
- Is the naming clear?
- Are there obvious edge cases?
- Did I accidentally change unrelated behavior?
- Can anything be removed without losing correctness?

If the answer is yes, simplify the implementation before finishing.

---

## 13. Investigate Uncertainty

When important information is missing, do not guess.

Distinguish between:

- facts established by inspecting the repository
- reasonable inferences
- unknowns

For important unknowns, investigate further or ask for clarification.

Never present an assumption as a repository fact.

---

## 14. Task Sizing

Choose the smallest workflow appropriate for the task.

For a trivial change:

- inspect
- change
- verify

For a non-trivial change:

- investigate
- identify the root cause or design constraint
- propose the smallest sound approach
- implement
- test
- review

Do not use a heavyweight process for a one-line change.

Do not skip investigation for a change that affects multiple components.

---

## 15. Completion Standard

"Done" means the requested work is actually finished.

Do not stop at:

- "I found the issue"
- "Here is what you should change"
- "I created a partial implementation"
- "The remaining work is straightforward"

When the task is within scope and can reasonably be completed,
complete it.

Do not leave avoidable dangling work.

---

## 16. Engineering Judgment

The objective is not maximum abstraction,
maximum defensiveness,
maximum test coverage,
or minimum lines of code.

The objective is:

    correct
    clear
    maintainable
    appropriately tested
    appropriately scoped
    no more complex than necessary

When two implementations are both correct, prefer the one that is easier
for another competent engineer to understand and maintain.
