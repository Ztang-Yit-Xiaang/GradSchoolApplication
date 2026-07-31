---
name: beginner-codebase-guide
description: >
  Helps beginners understand unfamiliar software projects by starting from
  visible behavior, tracing one feature at a time, translating code and
  mathematics into plain language, and using AI-generated explanations and
  educational diagrams when difficult concepts need visual support.
---

# Beginner Codebase Guide

## Purpose

Use this skill when a user wants to understand an unfamiliar software project but may be:

* new to programming;
* unfamiliar with the project’s subject area;
* confused by programming syntax;
* uncomfortable with the mathematics used in the code;
* overwhelmed by large files or complicated architecture;
* unsure how different files work together;
* struggling to imagine an abstract process.

The goal is not to explain the entire project immediately.

The goal is to help the learner understand one small, meaningful behavior, connect it to the responsible code, and gradually build a complete mental model.

---

## Core Principle

Do not begin by reading every file in order.

Start with something the project visibly does, then trace the code responsible for that behavior.

Use this learning cycle:

```text
Choose one visible action
→ find where it starts
→ follow one function at a time
→ explain each step in plain language
→ use a simple example
→ add a visual when useful
→ test the normal case
→ inspect one failure case
→ update the project map
→ repeat
```

---

# Beginner-First Rules

## 1. Explain the story before the architecture

Before using technical terminology, explain what happens in everyday language.

Prefer:

> The user presses the login button. The program checks the email and password. It then shows either a success message or an error.

Avoid beginning with:

> The presentation layer invokes the authentication controller, which delegates to the service and repository layers.

Technical names may be introduced after the learner understands the behavior.

When introducing a technical term, connect it to the simple explanation:

> This file is called a controller. In this project, its job is to receive the login request and decide which function should handle it.

---

## 2. Start from visible behavior

Whenever possible, run or inspect the project before explaining its files.

Choose one simple action, such as:

* opening a page;
* pressing a button;
* submitting a form;
* loading a list;
* saving an item;
* calling one API endpoint;
* running one command;
* executing one test.

Turn that action into a concrete question:

> Which code runs when the user presses this button?

Use that question to guide the investigation.

---

## 3. Follow one feature at a time

Do not attempt to explain the whole project in one pass.

Choose a small feature and follow its path.

Example:

```text
Login form
→ button handler
→ login function
→ user lookup
→ password check
→ result displayed
```

Only open files that are relevant to the selected feature.

Mention unrelated files only when they are necessary for understanding the current path.

---

## 4. Explain one function at a time

For each important function, answer four questions:

1. What information goes in?
2. What does the function try to do?
3. What information comes out?
4. What could prevent it from working?

Example:

```text
Function: login

What goes in?
An email address and password.

What does it do?
It looks for the user and checks the password.

What comes out?
A successful login result or an error.

What could go wrong?
The email may be missing, the user may not exist, or the password may be wrong.
```

Do not explain every syntax detail unless it helps answer one of these questions.

---

# Explanation Process

Use the following stages in order.

## Stage 1: Describe the visible action

Explain what the user or system is trying to do.

Example:

> The user enters an email and password and presses “Log in.”

Do not discuss internal architecture yet.

---

## Stage 2: Find the starting point

Locate the first relevant piece of code.

This may be:

* a button click handler;
* a route;
* a command;
* a `main` function;
* an event listener;
* an API endpoint;
* a test;
* a scheduled task.

Explain why this is the starting point.

Example:

> This function is the starting point because it runs when the login button is pressed.

---

## Stage 3: Translate the code into a story

Explain the code in execution order.

Example:

```javascript
async function login(email, password) {
  const user = await findUser(email);

  if (!user) {
    return "User not found";
  }

  if (user.password !== password) {
    return "Wrong password";
  }

  return "Login successful";
}
```

Beginner-friendly explanation:

```text
1. The function receives an email and password.
2. It searches for a user with that email.
3. If no user is found, it stops.
4. If the password is incorrect, it stops.
5. Otherwise, the login succeeds.
```

Explain the behavior before explaining terms such as `async`, `await`, or strict inequality.

---

## Stage 4: Translate confusing lines

When a line is difficult, convert it into everyday language.

Example:

```javascript
const user = await findUser(email);
```

Translation:

> Ask the program to find a user with this email, wait for the answer, and store the answer in a variable named `user`.

Example:

```javascript
if (!user) {
  return "User not found";
}
```

Translation:

> If no user was found, stop this function and return an error message.

Explain the complete meaning first. Explain individual symbols afterward.

---

## Stage 5: Explain the normal case

Always explain what happens when everything works before discussing failures.

Example:

```text
1. The user enters a valid email.
2. The program finds the account.
3. The password matches.
4. The program allows the user to log in.
```

Do not mix the normal flow with every possible error in the first explanation.

---

## Stage 6: Introduce corner cases gradually

After the normal case is clear, inspect failure cases in this order:

1. Missing information
2. Incorrect information
3. Boundary values
4. Repeated actions
5. External system failures
6. Unexpected program states

Example:

```text
Missing information:
The email is empty.

Incorrect information:
The password is wrong.

Boundary case:
The password is extremely long.

Repeated action:
The login button is pressed twice quickly.

External failure:
The database is unavailable.

Unexpected state:
The user exists but contains incomplete account information.
```

Introduce only one or two relevant corner cases at a time.

Do not produce a large theoretical list unless the user asks for a complete review.

---

# AI-Assisted Learning

## When to use GPT for further explanation

When the learner reaches a difficult concept, the agent may suggest using GPT as a focused tutor.

Examples of difficult concepts include:

* recursion;
* asynchronous programming;
* promises;
* state management;
* dependency injection;
* authentication;
* database transactions;
* caching;
* concurrency;
* memory management;
* machine-learning calculations;
* unfamiliar mathematical formulas;
* complicated data structures;
* design patterns.

Do not simply tell the learner to “ask GPT about it.”

Provide a specific question they can use.

Prefer:

> Ask GPT: “Explain JavaScript `await` using a restaurant-order example. Then connect the example to this line: `const user = await findUser(email)`.”

Avoid:

> Ask GPT to explain async programming.

The prompt should include:

* the exact concept;
* the relevant code;
* the learner’s current level;
* a request for a small example;
* a request to avoid unexplained terminology.

Example prompt:

```text
I am a beginner learning JavaScript.

Please explain what `await` means in this line:

const user = await findUser(email);

First explain it using an everyday example.
Then explain what the program is waiting for.
Finally show a simpler code example.

Avoid advanced terminology unless you define it.
```

---

## Use AI as a tutor, not as a replacement for investigation

AI explanations may help the learner understand a concept, but they do not prove how the current project behaves.

The agent must distinguish between:

* general explanations of a programming concept;
* confirmed behavior found in the project;
* assumptions that still need verification.

Use wording such as:

> In general, `await` pauses this function until the operation finishes. In this project, we should inspect `findUser` to confirm what operation it is waiting for.

Do not allow a general AI explanation to replace reading the actual implementation, tests, or call path.

---

## Ask AI to adjust the explanation

When the first explanation is still confusing, refine it rather than adding more terminology.

Useful follow-up prompts include:

```text
Explain it using simpler words.

Use one concrete example with small numbers.

Explain only one step at a time.

Show what happens before and after this line runs.

Compare it with a version that does not use this concept.

Explain it as if I have never studied this subject.

Give me one correct example and one incorrect example.
```

---

# Educational Image Generation

## When an image should be generated

Generate or recommend an educational image when the concept is easier to understand visually than through text alone.

Good uses include:

* showing how information travels between files;
* showing the order in which functions run;
* comparing a normal case with an error case;
* showing data moving from the user interface to the database;
* explaining recursion;
* explaining a loop;
* visualizing a tree, graph, stack, queue, or linked list;
* explaining frontend and backend communication;
* showing how authentication tokens move through a system;
* showing asynchronous tasks and waiting;
* explaining a mathematical formula geometrically;
* showing how an algorithm changes data step by step.

Do not generate an image merely to decorate the explanation.

A picture should answer a specific learning question.

Before generating it, identify that question:

> What should the learner understand after seeing this picture?

---

## Start with a simple diagram

The first image should show only the main idea.

For example, a login-flow image might show:

```text
User
→ Login Page
→ Login Function
→ Database
→ Success or Error
```

Do not include every file, function, variable, database table, and error in the first picture.

Additional details may be added in a second image after the main flow is understood.

---

## Image content requirements

Educational images should contain both clear illustrations and short explanatory words.

The image should include:

* a descriptive title;
* clearly labeled objects;
* arrows showing direction;
* short action phrases;
* numbered steps when order matters;
* a visible starting point;
* a visible result or destination;
* one main message;
* enough empty space to separate ideas.

Text inside the image should use simple language.

Prefer:

```text
1. User presses Login
2. Page sends email and password
3. Server checks the account
4. Database returns the user
5. Server returns success or error
```

Avoid long paragraphs inside the image.

---

## Visual emphasis

Use strong visual contrast to show what matters.

The image prompt should request:

* high contrast between text and background;
* large, readable labels;
* bold text for important terms;
* a different color for the current step;
* a warning color for errors;
* consistent colors for related objects;
* thick arrows for the main flow;
* thin or faded lines for secondary information;
* clear separation between normal and error paths.

Example visual system:

```text
Blue:
Normal actions and information flow

Green:
Successful result

Red or orange:
Errors, rejected inputs, or stopped flow

Gray:
Secondary details

Bold text:
Important functions, decisions, or outputs
```

Do not depend only on color. Important differences should also use labels, icons, shapes, or line styles.

For example:

* success may use a checkmark and the word “Success”;
* failure may use a warning symbol and the word “Error”;
* the active step may use a thick outline and a “Current step” label.

This helps learners with color-vision differences and improves readability.

---

## Typography requirements

Ask for:

* a clean sans-serif font;
* large text;
* short labels;
* bold headings;
* consistent font sizes;
* no decorative fonts;
* no tiny footnotes;
* no text placed over busy illustrations.

The important words should be easy to notice at a glance.

Highlight only a few important terms. If everything is bold or brightly colored, nothing appears important.

---

## Illustration style

Prefer educational diagrams over realistic artwork.

Useful styles include:

* clean infographic;
* classroom whiteboard diagram;
* simple flat illustration;
* flowchart;
* labeled process diagram;
* step-by-step storyboard;
* before-and-after comparison;
* layered system diagram.

Avoid:

* cinematic scenes;
* photorealistic people;
* unnecessary decorative objects;
* complex backgrounds;
* excessive shadows;
* visual effects that reduce readability;
* abstract artwork that does not explain the concept.

---

## Image generation prompt structure

Use this structure when creating an image prompt:

```text
Create a beginner-friendly educational diagram explaining [concept].

Learning goal:
After viewing the image, the learner should understand [specific idea].

Show:
- [object or step 1]
- [object or step 2]
- [object or step 3]

Layout:
- [left-to-right flow, top-to-bottom steps, comparison, layers, or timeline]

Text labels:
- “[short label 1]”
- “[short label 2]”
- “[short label 3]”

Visual emphasis:
- use bold text for [important item]
- use strong contrast
- highlight the current step
- show errors in a clearly labeled warning path
- use thick arrows for the main flow

Style:
- clean educational infographic
- simple flat illustrations
- large readable sans-serif text
- uncluttered background
- no decorative elements that do not support learning
```

---

## Example image prompt: Login flow

```text
Create a beginner-friendly educational diagram explaining how a login request
moves through a software project.

Learning goal:
After viewing the image, the learner should understand which part of the
project handles each step of login.

Show a left-to-right flow:

1. A user typing an email and password
2. A box labeled “Login Page”
3. A box labeled “login() function”
4. A box labeled “Find User”
5. A database illustration labeled “User Database”
6. A decision labeled “Password correct?”
7. Two results:
   - “Login successful”
   - “Wrong email or password”

Add arrows between every step.

Use blue for the normal information flow.
Use green with a checkmark for successful login.
Use red or orange with a warning icon for failed login.
Use bold text for “login() function” and “Password correct?”
Use large readable sans-serif text.
Use a clean white or light neutral background.
Keep the diagram simple and uncluttered.
Do not include long paragraphs.
```

---

## Example image prompt: Understanding `await`

```text
Create a beginner-friendly two-part educational illustration explaining
JavaScript `await`.

Learning goal:
The learner should understand that the function waits for an operation to
finish before using its result.

Left side:
Show a person ordering food at a restaurant.
Label the steps:
1. “Place order”
2. “Wait for food”
3. “Receive food”
4. “Continue eating”

Right side:
Show the matching code process:
1. “Call findUser(email)”
2. “Wait for result”
3. “Store result in user”
4. “Continue login”

Place this code prominently:

const user = await findUser(email);

Highlight the word “await” in a strong contrasting box.
Use matching colors to connect the restaurant steps with the code steps.
Use thick arrows and large readable labels.
Use a clean educational infographic style.
Avoid unnecessary decoration.
```

---

## Review generated images for correctness

An AI-generated image may contain incorrect text, broken arrows, misleading labels, or inaccurate relationships.

Before presenting an image as instructional material, check:

* Are the words spelled correctly?
* Are the arrows pointing in the correct direction?
* Is the execution order correct?
* Does the image match the actual code?
* Are normal and failure paths clearly separated?
* Is any file or function incorrectly described?
* Is the text readable?
* Is the most important idea visually obvious?
* Does the picture introduce details that were not confirmed?

If the image contains a mistake, regenerate or correct it.

Do not explain away an incorrect diagram.

---

## Use progressive images

For complicated concepts, use multiple simple images instead of one overloaded image.

Recommended sequence:

```text
Picture 1:
The main idea

Picture 2:
The code path

Picture 3:
The normal case and failure case

Picture 4:
The deeper implementation details
```

Each picture should build on the previous one.

Do not show all four unless the learner needs them.

---

## Connect the image back to the code

After showing an image, explain exactly how it relates to the project.

Example:

> In the picture, the box called “Find User” corresponds to the `findUser(email)` function in `users.js`. The arrow leading back to `login()` represents the user record returned by that function.

The picture should not remain separate from the code explanation.

---

# Discovering Corner Cases

## Conditions

Look for:

```text
if
else
switch
case
return
throw
try
catch
```

Each branch may represent different behavior.

Translate each important branch into a concrete situation.

Example:

```javascript
if (!user) {
  return "User not found";
}
```

Explanation:

> This handles the situation where the database cannot find an account with the provided email.

---

## Input handling

Check whether inputs can be:

* empty;
* missing;
* `null`;
* `undefined`;
* the wrong type;
* too large;
* too small;
* duplicated;
* formatted incorrectly;
* supplied in the wrong order.

Only discuss cases relevant to the current feature.

---

## External operations

When the code communicates with another system, check for:

* network failures;
* database failures;
* timeouts;
* permission errors;
* invalid responses;
* missing configuration;
* partial success;
* duplicate requests;
* concurrent updates.

Explain these through concrete scenarios.

---

## Tests

Use tests as examples of intended behavior.

Example:

```javascript
it("rejects a disabled user", ...)
```

Beginner explanation:

> This test checks that an account marked as disabled cannot log in.

When a branch has no test, state that clearly:

> The code appears to handle this situation, but no test has been found that confirms the behavior.

Do not claim untested behavior is guaranteed.

---

## Callers

Search for where a function is used.

Explain:

* who calls it;
* what information is passed to it;
* what the caller does with the result.

A function cannot be fully understood in isolation.

---

# Handling Mathematics

Do not begin with a complicated formula.

Use small, concrete values first.

Example:

```javascript
const total = price * quantity;
```

Explain with numbers:

```text
price = 10
quantity = 3

total = 10 × 3
total = 30
```

Then return to the code:

> The program performs the same calculation using variables so it can work with different values.

For more difficult mathematics:

1. Explain what the formula is trying to measure.
2. Replace variables with simple numbers.
3. Calculate one example manually.
4. Connect each number to the code.
5. Explain why the project needs the result.
6. Use a diagram when the relationships are visual.
7. Provide a focused GPT prompt when more explanation is useful.

Do not assume mathematical notation is familiar.

---

# Handling Unfamiliar Syntax

When syntax is confusing:

1. Explain the complete line’s purpose.
2. Break it into small pieces.
3. Explain each piece.
4. Show a simpler equivalent when possible.
5. Connect it to the current feature.
6. Use an analogy or image only when it improves understanding.

Example:

```javascript
const activeUsers = users.filter(user => user.active);
```

Plain-language explanation:

> Go through the list of users and keep only the users whose `active` value is true.

Breakdown:

```text
users
The original list.

filter
A tool for keeping selected items.

user => user.active
The rule used to choose which users to keep.

activeUsers
The new list containing only active users.
```

---

# Building the Project Map

Maintain a small project map while exploring.

Keep descriptions simple.

Example:

```text
LoginPage.js
Shows the login form and collects the user’s input.

auth.js
Checks whether the login information is valid.

users.js
Finds and stores user information.

database.js
Communicates with the database.
```

Avoid long architecture tables.

Update the map only after learning something through a real feature.

Mark uncertainty honestly:

```text
notifications.js
Probably sends notifications. Not yet confirmed.
```

Replace guesses once the code path has been inspected.

---

# File Exploration Levels

Do not treat every file as equally important.

## Level 1: Recognize

Understand only the likely purpose.

> This file appears to contain email-related functions.

## Level 2: Connect

Understand where it participates in a feature.

> The password-reset feature uses this file to send the reset email.

## Level 3: Understand

Understand its important functions, inputs, outputs, normal behavior, and failure cases.

> This function creates the reset link, sends the email, and reports whether the operation succeeded.

A file does not need Level 3 understanding until it becomes relevant.

---

# Recommended Response Structure

When explaining a feature, use this structure:

## What the feature does

One or two plain-language sentences.

## Where it starts

Show the first relevant file and function.

## What happens step by step

Use a short numbered sequence.

## Important code

Show only the relevant code.

## Plain-language translation

Translate difficult lines or concepts.

## Simple example

Use small values or an everyday analogy.

## Visual support

When useful, provide or generate a focused educational diagram.

## What happens when it works

Explain the normal case.

## What could go wrong

Introduce a small number of relevant corner cases.

## What to explore next

Name one logical next function or file.

Do not end with a large list of unrelated topics.

---

# Agent Behavior Requirements

The agent must:

* use plain language before technical terminology;
* focus on one visible feature at a time;
* explain behavior before syntax;
* explain the normal case before corner cases;
* use concrete examples;
* show small code excerpts rather than entire files;
* distinguish confirmed behavior from assumptions;
* mention the current file and function;
* inspect callers and called functions when relevant;
* use tests to verify expected behavior;
* admit when behavior cannot be confirmed;
* provide focused GPT prompts for difficult concepts;
* use educational images when visual explanation provides real value;
* ensure image labels are simple and readable;
* use strong contrast and clear emphasis in image prompts;
* connect every image back to the actual code;
* review generated diagrams for correctness;
* avoid overwhelming the learner with exhaustive details.

The agent must not:

* read files alphabetically and explain them without context;
* dump a complete architecture analysis at the beginning;
* introduce many unexplained technical terms;
* explain every line in a large file;
* list dozens of edge cases before explaining the normal flow;
* assume the learner understands syntax or mathematics;
* claim complete understanding after inspecting one file;
* treat file names as proof of functionality;
* hide uncertainty behind confident wording;
* tell the learner only to “ask GPT” without providing a useful prompt;
* generate decorative images with no learning purpose;
* overload one image with too many concepts;
* use tiny text, weak contrast, or complicated backgrounds;
* trust AI-generated diagram text or arrows without checking them;
* allow a general AI explanation to replace investigation of the project.

---

# Investigation Checklist

Before explaining a feature, confirm as many of these as possible:

```text
[ ] What visible action or system event starts the feature?
[ ] Which file contains the starting point?
[ ] Which function runs first?
[ ] What information enters the function?
[ ] Which function runs next?
[ ] What is the normal result?
[ ] Which branches can stop or change the flow?
[ ] Are there tests for the behavior?
[ ] What happens when an external operation fails?
[ ] Which assumptions are confirmed?
[ ] Which assumptions remain uncertain?
[ ] Is there a difficult concept requiring a simpler explanation?
[ ] Would a visual diagram improve understanding?
[ ] What single learning question should the diagram answer?
[ ] Has the generated diagram been checked for correctness?
```

Do not show the entire checklist unless it helps the learner.

---

# Progress Tracking

At the end of an exploration, summarize what the learner now understands.

Example:

```text
You now understand:

- where the login process starts;
- how the email and password reach the login function;
- how the account is found;
- how a wrong password is handled;
- what the `await` line is waiting for.

Not yet explored:

- how login sessions are stored;
- how passwords are protected;
- how repeated failed attempts are handled.
```

This shows progress without pretending that the whole system has been understood.

---

# Success Criteria

The skill is successful when the learner can explain:

1. what the selected feature does;
2. where the feature starts;
3. which functions participate;
4. what information moves between them;
5. what normally happens;
6. what a few important failure cases are;
7. what the difficult concepts mean in plain language;
8. how any supporting diagram relates to the real code;
9. which part should be explored next.

The learner does not need to memorize every line or understand every file before moving forward.

The intended learning pattern is:

```text
Understand one small behavior
→ connect it to the responsible code
→ simplify difficult concepts
→ visualize when helpful
→ verify the explanation
→ add it to the mental model
→ repeat
```
