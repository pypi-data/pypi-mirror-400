# Which Design Patterns to Use in 2025

**Section:** Generic Python | **See Also:** [4-rules-design.md](4-rules-design.md), [nouns-and-verbs.md](nouns-and-verbs.md)

Out of the 22 original design patterns in the famous "Gang of Four" (GoF) book, only a few are still relevant for Python in 2025.

The core themes driving the evaluation are:
1.  **Python's Language Features:** Python's dynamic nature and first-class functions render many classic patterns overly complex or obsolete.
2.  **Love Your Data:** Patterns that obscure data, hide its format, or create complex, untraceable state changes are now considered anti-patterns. Modern development favors explicit, inspectable data.
3.  **Managing Complexity:** The surviving patterns are those that solve fundamental problems of complexity, either by composing behavior, structuring frameworks, or adapting interfaces.

---

## The "Good" and Surviving Patterns

These patterns remain relevant because they address fundamental aspects of software design and complexity that persist regardless of language features.

### 1. The "Framework" Patterns

These are foundational patterns that you are more likely to *use* as part of a larger library than to implement from scratch.

*   **Composite:** The bedrock of any tree-like structure. It allows you to treat both individual objects (leaves) and groups of objects (branches) uniformly. The browser DOM is the quintessential example.
*   **Chain of Responsibility:** Works hand-in-hand with the Composite pattern. It defines a clean way for an event to be passed up a hierarchy until it's handled. This is exactly how event "bubbling" works in web browsers.
*   **Command:** Essential for any system that requires undo/redo functionality. By encapsulating an action and its inverse in an object, you can create a history of operations. It is also powerful for managing transactional workflows.
*   **Interpreter:** The ideal solution for implementing a small, domain-specific language (DSL). It uses a composite structure to represent an expression or program as an executable syntax tree.

### 2. The "Decomposition" Patterns

These patterns are valuable tools for breaking apart large, monolithic classes and separating concerns, fully embracing the principle of "favor composition over inheritance."

*   **Bridge:** Decouples an abstraction from its implementation, allowing both to vary independently. It's the solution for avoiding a combinatorial explosion of subclasses.
*   **Decorator:** Dynamically adds behavior to an object without altering its class. While Python has language-level decorators (`@`), the original object-wrapping pattern is still very useful for applying layers of functionality at runtime.
*   **Mediator:** Centralizes complex interactions between a set of objects. Instead of creating a tangled web where everyone talks to everyone, objects only talk to the mediator, simplifying the logic.
*   **State:** A clean way to manage an object whose behavior changes dramatically based on its state. It avoids complex conditional logic by encapsulating state-specific behaviors in distinct state objects.

### 3. Small but Useful Patterns

These are practical, widely applicable patterns for everyday coding challenges.

*   **Builder:** Excellent for constructing complex objects step-by-step. It provides a fluent API that hides the messy details of the object's internal construction. The `matplotlib` library's API for building plots is a great example.
*   **Adapter:** Makes an existing class's interface conform to the one a client expects. It's a fundamental pattern for integrating incompatible libraries or legacy code.
*   **Flyweight:** A memory optimization technique for sharing the immutable parts of an object's state among many instances. Python's pre-allocation of small integer objects is a language-level application of this principle.

---

## The "Bad" or Less Relevant Patterns

These patterns are considered "bad" not because their original goal was wrong, but because modern languages and architectural principles offer far better solutions.

### 1. Patterns Made Obsolete by Python's Features

These patterns were primarily workarounds for the limitations of older, statically-typed languages. Python's core features provide a more direct and simpler solution.

*   **Factory Method & Template Method:** These rely on subclassing to change a small piece of behavior. In Python, it's far simpler to just pass a function or a class directly as an argument.
*   **Abstract Factory:** While better than Factory Method because it uses composition, it's still unnecessarily verbose. Instead of creating a whole factory object, you can just pass the necessary functions or constructors.
*   **Strategy:** The classic use case is swapping algorithms. In Python, you don't need to wrap each algorithm in a separate class; you just pass the desired function.
*   **Singleton:** The complex implementation described by the GoF is unnecessary. In Python, you can achieve the same result by simply instantiating a class once at the module level and importing that instance.

### 2. Anti-Patterns that Obscure Data

These patterns violate the modern principle that data should be transparent, inspectable, and easy to reason about.

*   **Proxy (specifically, the Remote Proxy):** This pattern makes a remote network call look like a local method call, hiding the inherent latency, failure modes, and different design considerations. Modern approaches like explicit REST APIs or gRPC are preferred because they make the network boundary clear.
*   **Memento:** This pattern saves an object's state as an opaque binary blob. This is a nightmare for debugging, data migration, and interoperability. The modern approach is to use standard, transparent serialization formats like JSON, YAML, or Protocol Buffers.
*   **Observer:** This pattern leads to a complex web of objects directly updating each other, making the flow of data hard to trace ("Domino Programming"). The modern alternative is to have a single, centralized data structure as the "source of truth." Components react to changes in this central state, creating a unidirectional and much more debuggable data flow.

---

## Summary Table

| Category | Pattern | Status | Why |
|----------|---------|--------|-----|
| Framework | Composite | **Good** | Fundamental for tree structures |
| Framework | Chain of Responsibility | **Good** | Event handling in hierarchies |
| Framework | Command | **Good** | Undo/redo, transactional workflows |
| Framework | Interpreter | **Good** | DSLs, expression parsing |
| Decomposition | Bridge | **Good** | Decouples abstraction from implementation |
| Decomposition | Decorator | **Good** | Dynamic behavior composition |
| Decomposition | Mediator | **Good** | Centralizes complex interactions |
| Decomposition | State | **Good** | Clean state machine implementation |
| Small/Useful | Builder | **Good** | Complex object construction |
| Small/Useful | Adapter | **Good** | Interface compatibility |
| Small/Useful | Flyweight | **Good** | Memory optimization |
| Obsolete | Factory Method | **Obsolete** | Use functions instead |
| Obsolete | Template Method | **Obsolete** | Use functions instead |
| Obsolete | Abstract Factory | **Obsolete** | Pass functions/constructors directly |
| Obsolete | Strategy | **Obsolete** | Pass functions directly |
| Obsolete | Singleton | **Obsolete** | Module-level instance |
| Anti-pattern | Remote Proxy | **Bad** | Hides network complexity |
| Anti-pattern | Memento | **Bad** | Opaque state storage |
| Anti-pattern | Observer | **Bad** | Tangled data flow |

---

## Related Documents

- [4-rules-design.md](4-rules-design.md) — Kent Beck's Four Rules of Simple Design
- [nouns-and-verbs.md](nouns-and-verbs.md) — Functional architecture patterns
- [coding-guidelines.md](coding-guidelines.md) — Core development practices

**Last Updated:** 2025-12-24
