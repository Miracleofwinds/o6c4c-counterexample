# Semidirect result record: o6c4c

## Result

Semidirect independently generated a finite simple cubic 3-edge-connected
graph `H` on 18 vertices and 27 edges for which no oriented 6-cycle 4-cover
exists. The graph is obtained from the Petersen graph by replacing the four
vertices of one closed neighbourhood with triangles. Its exact numbered edge
set is stored in `graph.edgelist`.

This record documents the generated result and its reproducibility evidence.
It makes no claim of priority or novelty and is not a peer-reviewed
publication.

## What it does and does not refute

The construction refutes the conjecture as literally stated for finite
loopless bridgeless graphs. Its four replacement triangles give cyclic
3-edge-cuts, so the graph is not cyclically 4-edge-connected; its girth is 3.
It does not address the intended version restricted to cyclically
4-edge-connected graphs, nor the conventional snark setting with girth at
least 5.

Counterexamples to the literal statement were already known before this
repository was created. This artifact is retained solely as an independently
generated Semidirect result and reproducibility case study.

## Finite reduction

For a cubic graph, the complement of every spanning 2-factor is a perfect
matching. Local degree parity forces every member of a putative 6-cycle
4-cover of `H` to be a spanning 2-factor. Consequently, the six complements
must form a perfect-matching double cover.

The graph has 18 perfect matchings. Exhaustive exact enumeration checks all
100,947 multisets of six perfect matchings and finds one double cover, up to
permutation. Its complementary 2-factors split into twelve circuit
components.

## Directional obstruction

Once the unique unoriented cover is fixed, orienting the twelve circuit
components gives `2^12 = 4,096` assignments. Exact enumeration finds none that
balances every covered edge twice in each direction.

The same obstruction has a compact certificate. Five selected edge-balance
equations yield rows `r1,...,r5` satisfying

    r1 - r2 - r3 - r4 - r5 = (4, 0, 0, 0, 0, 0).

If the component-orientation signs are `z0,...,z5` in `{ -1, 1 }`, this row
combination forces `4*z0 = 0`, which is impossible.

## Independent checks

Two separately written standard-library Python programs verify the result:

    python verify_expansion.py
    python verify_numbered.py

The first derives the graph from the Petersen expansion. The second begins
from the numbered edge list. Both check the graph invariants, all perfect
matchings, the unique double cover, the circuit decompositions, the displayed
linear certificate, and all component-orientation assignments.

Expected final output:

    {"component_orientation_assignments": 4096, "double_covers": 1, "edges": 27, "implementation": "expansion", "matching_multisets": 100947, "perfect_matchings": 18, "status": "passed", "vertices": 18}
    {"component_orientation_assignments": 4096, "double_covers": 1, "edges": 27, "implementation": "numbered", "matching_multisets": 100947, "perfect_matchings": 18, "status": "passed", "vertices": 18}

## Provenance

- Generated during a Semidirect automated mathematics research run.
- Reduced to explicit finite data and a hand-checkable linear obstruction.
- Checked by two independent implementations.
- Retained as a Semidirect case study rather than as a novelty claim.

For the conjecture and its historical context, consult Nikolay Ulyanov's
[arXiv paper](https://arxiv.org/abs/2501.05348) and
[research repository](https://github.com/gexahedron/cycle-double-covers).
