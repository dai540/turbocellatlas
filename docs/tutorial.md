# Tutorials

Tutorials are the best place to learn TurboCell Atlas by following a complete story from question to output.

This section is intentionally written as prose rather than as a short index. A new user should be able to understand not only which command to run, but also why a given workflow exists, what kind of biological question it answers, and how to read the resulting tables and figures.

## What tutorials are for

TurboCell Atlas is easiest to understand when you imagine a concrete starting point. You may have one unusual fibroblast state in IPF, one representative cell that looks suspicious in a pilot experiment, or one disease cohort that you want to compare against the whole atlas. Tutorials take those situations one by one and walk through the reasoning behind the search.

Each tutorial should help you answer four questions:

1. what biological question am I asking
2. what data do I need before I can ask it
3. what output should I expect from the search
4. how should I interpret the result without over-claiming

## Before you choose a tutorial

If you are still deciding whether the package is relevant, start with these two short articles first:

- [What TurboCell Atlas Can Do](what-turbocellatlas-can-do.md)
- [What You Need Before Using TurboCell Atlas](what-you-need.md)

Those pages explain the package in simple terms before you commit to a full workflow.

## Entry points

- [Get Started](get-started.md): first installation, first files to inspect, and first search command
- [Wet Lab Guide](wet-lab-guide.md): easiest path for non-computational users who want help understanding inputs, outputs, and interpretation

Use `Get Started` when you mainly want to run the software. Use `Wet Lab Guide` when you mainly want to understand what the outputs mean biologically.

## Worked examples

- [Rare-State Retrieval](tutorial-rare-state.md): the clearest current success case, where a compact disease state is used as the query
- [Single-Cell Query](tutorial-single-cell.md): how to start from one biologically interesting cell instead of a curated centroid
- [Cohort Triage](tutorial-cohort-triage.md): how metadata filters change the answer and why cohort restriction matters
- [Broad-State Tuning](tutorial-broad-state.md): why broad heterogeneous states are harder, and how query planning changes recall

## Review workflow

- [Benchmark Review](tutorial-benchmark-review.md): how to inspect the artifact bundle as a collaborator, reviewer, or method developer

## How to read a tutorial

A good TurboCell Atlas tutorial is not just a command log. It should be read in this order:

1. read the background and objective so you understand why the query was chosen
2. inspect the input description so you know what data frame or embedding bank is actually being used
3. look at the output tables before jumping to the conclusion
4. check the interpretation and limitations, especially when compressed retrieval differs from exact retrieval

If you only read the final figure, you will miss the most important part of the package, which is the connection between a biological question and a retrieval artifact that can be reviewed by someone else.

## Suggested reading paths

Choose one path depending on your goal.

### I want the easiest first run

1. [What You Need](what-you-need.md)
2. [Get Started](get-started.md)
3. [Wet Lab Guide](wet-lab-guide.md)

### I want to see a clear success case

1. [What TurboCell Atlas Can Do](what-turbocellatlas-can-do.md)
2. [Rare-State Retrieval](tutorial-rare-state.md)
3. [Real Data Case Study](real-data-case-study.md)

### I want to understand where the method is still weak

1. [Broad-State Tuning](tutorial-broad-state.md)
2. [Benchmark Review](tutorial-benchmark-review.md)
3. [Benchmarks](benchmarks.md)
