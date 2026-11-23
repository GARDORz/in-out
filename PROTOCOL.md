# Experiment protocol

1. Read the goal, rules, tests, benchmark, and prior experiment notes.
2. Measure the current branch with `python -m pytest -q` and `python bench.py`.
3. Write down exactly one performance hypothesis.
4. Make one small change in an allowed file.
5. Rerun the tests and benchmark under the same environment.
6. Keep or revert the change based on correctness, checksum, and measured time.
7. Append the result and lesson to the experiment log.
