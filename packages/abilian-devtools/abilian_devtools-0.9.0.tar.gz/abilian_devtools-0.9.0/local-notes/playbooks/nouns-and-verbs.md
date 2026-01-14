# Actionable Recommendations for Modern Python Architecture

**Section:** Generic Python | **See Also:** [4-rules-design.md](4-rules-design.md), [design-patterns.md](design-patterns.md)

This guide translates the "Nouns and Verbs" philosophy into five core principles for writing clean, testable, and maintainable Python code.

---

## Core Principles

### 1. Start with the Data, Not the Action

Before writing any functions or classes, define the shape of your data. Prefer simple, transparent data structures over opaque objects.

*   **Action:** Use standard types (`dict`, `list`, `str`, dataclasses) as the primary way to represent information in your system. Your data should be easily printable and serializable (e.g., to JSON).
*   **Litmus Test:** If you can't easily `print()` the state of an object and understand it, your object is hiding its data. Refactor it to be more legible.
*   **Advanced Mindset:** Treat *events* or *transactions* as immutable data (nouns). Treat an object's current *state* (like a bank balance) as a temporary calculation derived from that log of events (a verb). This "event sourcing" approach leads to more robust and auditable systems.

### 2. Separate Logic (Verbs) from State (Nouns)

This is the central rule. Resist the old Object-Oriented urge to attach every piece of logic to a class.

*   **Verbs (Your Functions):**
    *   **Should be stateless.** They receive data, process it, and return new data.
    *   **Should orchestrate complexity.** The main "story" of your application—calling a series of operations—should live here.
    *   **Action:** Keep your call graphs shallow. A verb should do its work and return; avoid deep chains where `A()` calls `B()` which calls `C()` which calls `D()`.

*   **Nouns (Your Classes/Data Objects):**
    *   **Should be the home of state.** Their primary job is to hold and guard the integrity of data.
    *   **Methods should be shallow.** A method on a noun should perform a single, simple operation on the object's *own* internal state (`self.value = x`). It should not orchestrate other objects or contain complex business logic.
    *   **Action:** If a method on a class needs to call methods on three other objects to get its job done, that logic belongs in a standalone function (a verb).

### 3. Write a Class ("Invent a Noun") Only When You Must

Creating a new class is the most significant architectural decision you can make. Treat it as an act of last resort, not a default starting point.

*   **DO write a class for these reasons:**
    1.  **To Model a Stateful Entity:** When you need to manage a real-world, stateful resource like a database connection, a network socket, or a temporary file.
    2.  **To Name a Specific Behavior:** To create a principled wrapper that clarifies intent. For example, using `Sum(5)` and `Product(5)` to distinguish between two different ways of combining integers. The noun names the *conformance*, not just the data.
    3.  **To Define a Simple, Reusable Component:** To create a small, well-defined API boundary, like a `FocusRequester` in a UI toolkit.

*   **DON'T write a class for this reason:**
    1.  **Just to hold a single function.** This is the "Kingdom of Nouns" anti-pattern (`ActionExecutor().execute()`). In Python, functions can and should exist on their own.

### 4. Structure Your Logic ("Verbs") in Layers

Organize your functions to create a clean, testable, and decoupled architecture.

*   **Action: Keep I/O at the Edges.** Create a clear boundary between your pure business logic and the "messy" outside world.
    *   **Core Logic (Verbs):** A set of pure functions that take simple data and return simple data. This core is easy to test.
    *   **Outer Layer:** A thin set of functions at the top of your call stack responsible for all I/O—reading files, making network requests, querying the database. This layer calls your core logic.

*   **Action: Do One Thing at a Time.** Separate high-level orchestration from low-level implementation.
    *   **Orchestrator Function:** A verb whose job is to call other verbs in the correct order (e.g., `1. read_data`, `2. process_records`, `3. write_report`). It contains no complex loops or conditionals.
    *   **Worker Functions:** The verbs that do the actual work (parsing a line, transforming a record).

### 5. Solve Problems from the Bottom-Up: Use, Then Invent

Follow a clear progression when tackling a new problem to avoid over-engineering. This is the practical application of the developer progression model.

1.  **First, Use (Procedural):** Try to solve the entire problem in a single script using existing libraries (`requests`, `pandas`) and basic data structures (`dict`, `list`). Get it working. This is your baseline.
2.  **Next, Invent Verbs (Abstraction):** Identify repeated logic or distinct steps in your script. Refactor them into standalone functions. At this stage, you should have a clean, procedural script composed of well-named function calls.
3.  **Last, Invent Nouns (Encapsulation):** Only after you have a working procedural solution, ask if any part of it would be clearer or more reusable if encapsulated in a class (refer to Guideline #3). If not, you're done. A well-structured script of functions is often the best and most "Pythonic" solution.

---

## Additional Principles

Here are four other valuable concepts that guide experienced developers in creating clean, maintainable, and adaptable code.

### 1. The Mindset: YAGNI (You Ain't Gonna Need It)

**Core Idea:** Only build what is necessary to meet the current, concrete requirements.

This principle directly combats over-engineering by treating all code as a long-term liability, not an asset. Every line of code must be maintained, understood, and tested for the life of the project.

*   **What it Solves:** It prevents wasted effort on speculative features that may never be used. It also keeps the codebase smaller and simpler, making it easier to change when new, real requirements emerge.
*   **How to Apply It:** When you find yourself thinking, "We should add this because we'll probably need it later," stop. Ask: "Do we have a requirement for this *right now*?" If the answer is no, do not build it.


### 2. The Structure: Composition Over Inheritance

**Core Idea:** When modeling an object's capabilities, favor assembling it from independent components (`has-a`) over inheriting its behavior from a parent class (`is-a`).

While inheritance is a core part of object-oriented programming, this principle guides you to use it for what an object fundamentally *is*, not for what it *does*. Capabilities and behaviors are better modeled as components.

*   **What it Solves:** It prevents rigid and brittle class hierarchies. Using inheritance for capabilities often leads to a "class explosion," where you need a new class for every combination of features. Composition creates a flexible, "plug-and-play" architecture.
*   **How to Apply It:**
    *   **Inheritance (is-a):** Use for fundamental types. A `Car` *is a* `Vehicle`. This relationship is stable.
    *   **Composition (has-a):** Use for behaviors, strategies, or parts that can vary. A `Car` *has an* `Engine` and *has a* `TrimPackage`. This allows you to create any type of car by simply combining different engine and trim components.


### 3. The Boundaries: High Cohesion & Low Coupling

**Core Idea:** Modules should be highly focused on a single purpose (High Cohesion) and should know as little as possible about each other (Low Coupling).

These two concepts are the foundation of modular, understandable software. They guide how you draw the lines between different parts of your system.

*   **What it Solves:** They prevent the creation of "God Objects" that do everything and know everything. A system with high cohesion and low coupling is easier to debug and maintain because problems are isolated.
*   **How to Apply It:**
    *   **To increase cohesion:** Look at a class or function. Can you describe its purpose in one sentence without using the word "and"? If a module validates user input *and* sends emails *and* logs errors, it has low cohesion and should be broken apart.
    *   **To decrease coupling:** Minimize the dependencies a class has. Instead of reaching deep into another object (`order.getCustomer().getAddress().getZipCode()`), ask for what you need directly (`order.getShippingZipCode()`).


### 4. The Workflow: Tidy First?

**Core Idea:** Separate the act of cleaning code (refactoring) from the act of adding new functionality.

This is a pragmatic workflow heuristic popularized by Kent Beck. It makes changing code safer and more methodical.

*   **What it Solves:** It eliminates the risky practice of trying to restructure code and add new logic at the same time. This "two-handed" approach often introduces subtle bugs and makes code reviews difficult.
*   **How to Apply It:** Before adding a feature or fixing a bug, look at the code you need to change.
    1.  **Assess:** Is the existing structure making the change hard?
    2.  **If yes, Tidy First:** Perform a pure refactoring to make the code cleaner. Do not change any behavior. Commit this work with a clear "Refactor" message.
    3.  **Then, Make the Change:** With the code now clean, implement the new feature or fix. Commit this behavioral change separately.

---

## Related Documents

- [4-rules-design.md](4-rules-design.md) — Kent Beck's Four Rules of Simple Design
- [design-patterns.md](design-patterns.md) — GoF patterns for Python
- [coding-guidelines.md](coding-guidelines.md) — Core development practices

**Last Updated:** 2025-12-24
