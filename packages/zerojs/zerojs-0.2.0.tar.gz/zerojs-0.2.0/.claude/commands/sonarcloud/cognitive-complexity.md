---
argument-hint: "[filename] [line-number] [function-name]"
description: Refactor a function to reduce its cognitive complexity
---

# Refactor this function to reduce its Cognitive Complexity to the 15 allowed.

## Where is the issue?

- **Filename**: $1
- **Line**: $2
- **Function Name**: $3

## Why is this an issue?

Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high
cognitive complexity is hard to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller,
easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

- **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**\
  This concerns, for example, loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing
  multiple operators.
- **Each nesting level increases complexity.**\
  During code reading, the deeper you go through nested layers, the harder it becomes to keep the context in mind.
- **Method calls are free**
  A well-picked method name is a summary of multiple lines of code. A reader can first explore a high-level view of what
  the code is performing then go deeper and deeper by looking at called functions content.\
  _Note:_ This does not apply to recursive calls, those will increment cognitive score.

The method of computation is fully detailed in the pdf linked in the resources.

### What is the potential impact?

Developers spend more time reading and understanding code than writing it. High cognitive complexity slows down changes
and increases the cost of maintenance.

## How can I fix it?

Reducing cognitive complexity can be challenging.

Here are a few suggestions:

- **Extract complex conditions in a new function.**\
  Mixed operators in condition will increase complexity. Extracting the condition in a new function with an appropriate
  name will reduce cognitive load.
- **Break down large functions.**\
  Large functions can be hard to understand and maintain. If a function is doing too many things, consider breaking it
  down into smaller, more manageable functions. Each function should have a single responsibility.
- **Avoid deep nesting by returning early.**\
  To avoid the nesting of conditions, process exceptional cases first and return early.

### Extraction of a complex condition in a new function.

#### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```python
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple conditions)
            user.has_profile) or   # +1 (mixed operator)
            user.age > 18 ):
            user.process()
```

#### Compliant solution

Even if the cognitive complexity of the whole program did not change, it is easier for a reader to understand the code
of the process_eligible_users function, which now only has a cognitive cost of 3.

```python
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if is_eligible_user(user): # +1 (if) +1 (nested)
            user.process()

def is_eligible_user(user):
    return ((user.is_active and user.has_profile) or user.age > 18) # +1 (multiple conditions) +1 (mixed operators)
```

### Break down large functions.

#### Noncompliant code example

_Note:_ The code is simplified here, to illustrate the purpose. Please imagine there is more happening in the process.

The bellow code has a cognitive complexity score of 8.

```python
def process_user(user):
    if user.is_active():             # +1 (if)
        if user.has_profile():       # +1 (if) +1 (nested)
            ... # process active user with profile
        else:                        # +1 (else)
            ... # process active user without profile
    else:                            # +1 (else)
        if user.has_profile():       # +1 (if) +1 (nested)
            ... # process inactive user with profile
        else:                        # +1 (else)
            ... # process inactive user without profile
```

This function could be refactored into smaller functions: The complexity is spread over multiple functions and the breaks in flow are no more nested.
The `process_user` has now a complexity score of two.

#### Compilant Solution

```python
def process_user(user):
    if user.is_active():             # +1 (if)
        process_active_user(user)
    else:                            # +1 (else)
        process_inactive_user(user)

def process_active_user(user):
    if user.has_profile():           # +1 (if) +1 (nested)
        ... # process active user with profile
    else:                            # +1 (else)
        ... # process active user without profile

def process_inactive_user(user):
    if user.has_profile():           # +1 (if) +1 (nested)
        ... # process inactive user with profile
    else:                            # +1 (else)
        ... # process inactive user without profile
```

### Avoid deep nesting by returning early.

#### Noncompliant code example

The below code has a cognitive complexity of 6.

```python
def calculate(data):
    if data is not None:  # +1 (if)
        total = 0
        for item in data: # +1 (for) +1 (nested)
            if item > 0:  # +1 (if)  +2 (nested)
                total += item * 2
        return total
```

#### Compliant solution

Checking for the edge case first flattens the `if` statements and reduces the cognitive complexity to 4.

```python
def calculate(data):
    if data is None:      # +1 (if)
        return None
    total = 0
    for item in data:     # +1 (for)
        if item > 0:      # +1 (if) +1 (nested)
            total += item * 2
    return total
```

## Pitfalls

**IMPORTANT**: As this code is complex, ensure that you have unit tests that cover the code BEFORE refactoring.
