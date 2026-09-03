# Semidirect result: an 18-vertex o6c4c counterexample

This repository preserves one independently generated result of Semidirect:
an explicit 18-vertex graph with no oriented 6-cycle 4-cover, together with
two independent finite verification implementations.

## Correct scope

The graph refutes the o6c4c statement **as literally written** for finite
loopless bridgeless graphs. It is only cyclically 3-edge-connected and it
contains triangles. It therefore does **not** refute the intended snark-level
version restricted to cyclically 4-edge-connected graphs (normally also
studied with girth at least 5).

## Status and priority

This is a research-system result record, not a submission manuscript. It makes
no claim of priority or novelty: counterexamples to the literal formulation
were already known before this repository was created. The files are retained
to document what Semidirect generated independently and to make its finite
checks reproducible.

For the conjecture's origin and context, see Ulyanov,
[_Computational Graph Decompositions I: Oriented Berge--Fulkerson
Conjecture_](https://arxiv.org/abs/2501.05348), and the associated
[cycle-double-covers repository](https://github.com/gexahedron/cycle-double-covers).

The generated result and certificate are summarized in
[`RESULT.md`](RESULT.md).

## Requirements

- Python 3.10 or later
- no third-party Python packages

## Reproduce

Run from the repository root:

    python verify_expansion.py
    python verify_numbered.py

Each command must print one JSON object with `"status": "passed"`. The exact
expected lines are recorded in `expected_output.txt`.

## Included data

- `graph.edgelist`: the 27 edges on vertices 0 through 17;
- `verify_expansion.py`: constructs the graph from the Petersen
  closed-neighbourhood triangle expansion;
- `verify_numbered.py`: starts from the numbered edge list and independently
  checks the matching cover, circuit decomposition, and obstruction;
- `expected_output.txt`: fixed expected summaries;
- `SHA256SUMS`: hashes of the reproducibility payload files.

The two programs share no imported project module or generated intermediate
file. Both use only exact integer and finite combinatorial operations.

## Verified finite claims

The programs check:

1. 18 vertices, 27 edges, simplicity, cubicity, and 379 connectivity tests
   after deleting at most two edges;
2. six Petersen perfect matchings and all 18 perfect matchings of the expanded
   graph;
3. one perfect-matching double cover among 100,947 six-matching multisets;
4. the twelve complementary circuit components;
5. the displayed five-row directional obstruction; and
6. infeasibility of all 4,096 component-orientation assignments.

## Frozen verification package

The original code-only package remains available as GitHub release `v1.0.0`.
Its ZIP SHA-256 digest is:

    2243f4e96bc58f28c386a5b57f8af5a63ad43ebbf9efa323627f15be757b9d71

## License

The verification software is released under the MIT License.
