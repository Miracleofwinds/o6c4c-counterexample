# o6c4c 18-vertex counterexample: reproducibility release v1.0.0

This fixed release contains the finite data and two separately written
verification implementations accompanying the manuscript
_An 18-Vertex Counterexample to the Oriented Berge--Fulkerson Conjecture_.
The mathematical proof in the manuscript is self-contained and does not use
these programs as a premise.

## Manuscript

The public paper and its complete LaTeX source are available in
[`paper/`](paper/). The compiled manuscript is [`paper/main.pdf`](paper/main.pdf).
The archived version is identified by
[DOI: 10.5281/zenodo.22282127](https://doi.org/10.5281/zenodo.22282127).

## Requirements

- Python 3.10 or later
- no third-party Python packages

## Reproduce

Run the following commands from this directory:

    python verify_expansion.py
    python verify_numbered.py

Each command must print one JSON object whose status is passed. The exact
expected lines are recorded in expected_output.txt.

## Included data

- graph.edgelist: the 27 edges on vertices 0 through 17;
- verify_expansion.py: constructs the graph from the Petersen
  closed-neighbourhood triangle expansion;
- verify_numbered.py: starts from the numbered edge list and separately
  checks the matching cover, circuit decomposition, and obstruction;
- expected_output.txt: fixed expected summaries;
- SHA256SUMS: hashes of all release payload files.

The two programs share no imported project module or generated intermediate
file. Both use only exact integer and finite combinatorial operations.

## Verified claims

The programs check:

1. 18 vertices, 27 edges, simplicity, cubicity, and 379 connectivity tests
   after deleting at most two edges;
2. six Petersen perfect matchings and 18 perfect matchings of the expanded
   graph;
3. one perfect-matching double cover among 100,947 six-matching multisets;
4. the twelve complementary circuit components;
5. the displayed five-row certificate yielding 4 z0 = 0; and
6. infeasibility of all 4,096 component-orientation assignments.

## Version

- release: v1.0.0
- frozen: 2026-09-03

This package may be uploaded unchanged as an arXiv ancillary file or deposited
in a DOI-bearing archive.
