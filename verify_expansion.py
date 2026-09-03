#!/usr/bin/env python3
"""Expansion-based audit of the 18-vertex o6c4c counterexample.

The program reconstructs the graph from the Petersen-neighbourhood triangle
expansion, exhausts its perfect matchings and six-matching double covers, and
derives the sparse integer contradiction to directional balance. It uses only
the Python standard library.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path


P_VERTICES = tuple(range(10))
P_EDGES = tuple(
    sorted(
        {
            (0, 1), (1, 2), (2, 3), (3, 4), (0, 4),
            (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
            (5, 7), (7, 9), (6, 9), (6, 8), (5, 8),
        }
    )
)
EXPANDED = frozenset({0, 1, 4, 5})  # the closed Petersen neighbourhood N[0]
ROOT = Path(__file__).resolve().parent


def canon(edge):
    a, b = edge
    return (a, b) if vertex_key(a) < vertex_key(b) else (b, a)


def vertex_key(v):
    base, port = v
    return (base, -1 if port is None else port)


def vertex_name(v):
    base, port = v
    return f"u{base}" if port is None else f"p{base}_{port}"


def edge_name(e):
    return [vertex_name(e[0]), vertex_name(e[1])]


P_NEIGHBOURS = {v: set() for v in P_VERTICES}
for a, b in P_EDGES:
    P_NEIGHBOURS[a].add(b)
    P_NEIGHBOURS[b].add(a)


def image_endpoint(v, other):
    return (v, other) if v in EXPANDED else (v, None)


H_VERTICES = set()
for v in P_VERTICES:
    if v in EXPANDED:
        H_VERTICES.update((v, w) for w in P_NEIGHBOURS[v])
    else:
        H_VERTICES.add((v, None))

H_EDGES = set()
for a, b in P_EDGES:
    H_EDGES.add(canon((image_endpoint(a, b), image_endpoint(b, a))))
for v in EXPANDED:
    ports = sorted(((v, w) for w in P_NEIGHBOURS[v]), key=vertex_key)
    H_EDGES.update(canon(e) for e in combinations(ports, 2))
H_VERTICES = tuple(sorted(H_VERTICES, key=vertex_key))
H_EDGES = tuple(sorted(H_EDGES, key=lambda e: (vertex_key(e[0]), vertex_key(e[1]))))


def adjacency(vertices, edges):
    ans = {v: [] for v in vertices}
    for i, (a, b) in enumerate(edges):
        ans[a].append((b, i))
        ans[b].append((a, i))
    return ans


H_ADJ = adjacency(H_VERTICES, H_EDGES)


def release_edge_list():
    result = set()
    for raw in (ROOT / "graph.edgelist").read_text(encoding="ascii").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        a, b = map(int, line.split())
        result.add(tuple(sorted((a, b))))
    return result


def connected_after_deleting(deleted):
    start = H_VERTICES[0]
    seen = {start}
    todo = [start]
    while todo:
        v = todo.pop()
        for w, ei in H_ADJ[v]:
            if ei not in deleted and w not in seen:
                seen.add(w)
                todo.append(w)
    return len(seen) == len(H_VERTICES)


def enumerate_perfect_matchings(vertices, edges):
    adj = adjacency(vertices, edges)
    answer = []

    def visit(uncovered, chosen):
        if not uncovered:
            answer.append(frozenset(chosen))
            return
        v = min(uncovered, key=vertex_key)
        for w, ei in adj[v]:
            if w in uncovered:
                visit(uncovered - {v, w}, chosen + [ei])

    visit(set(vertices), [])
    return tuple(sorted(set(answer), key=lambda m: tuple(sorted(m))))


def enumerate_petersen_matchings():
    edges = tuple(((a, None), (b, None)) for a, b in P_EDGES)
    vertices = tuple((v, None) for v in P_VERTICES)
    raw = enumerate_perfect_matchings(vertices, edges)
    return tuple(
        frozenset(P_EDGES[i] for i in matching)
        for matching in raw
    )


P_MATCHINGS = enumerate_petersen_matchings()


def lift_petersen_matching(matching):
    lifted = set()
    for e in matching:
        a, b = e
        lifted.add(H_EDGES.index(canon((image_endpoint(a, b), image_endpoint(b, a)))))
    for v in EXPANDED:
        used = next(e for e in matching if v in e)
        other = used[0] if used[1] == v else used[1]
        unused_ports = [(v, w) for w in P_NEIGHBOURS[v] if w != other]
        lifted.add(H_EDGES.index(canon(tuple(unused_ports))))
    return frozenset(lifted)


LIFTED_MATCHINGS = tuple(lift_petersen_matching(m) for m in P_MATCHINGS)
H_MATCHINGS = enumerate_perfect_matchings(H_VERTICES, H_EDGES)


def components_of_edge_set(edge_indices):
    local = defaultdict(list)
    for ei in edge_indices:
        a, b = H_EDGES[ei]
        local[a].append((b, ei))
        local[b].append((a, ei))
    unseen = set(local)
    components = []
    while unseen:
        root = min(unseen, key=vertex_key)
        vertices = {root}
        todo = [root]
        component_edges = set()
        while todo:
            v = todo.pop()
            for w, ei in local[v]:
                component_edges.add(ei)
                if w not in vertices:
                    vertices.add(w)
                    todo.append(w)
        unseen -= vertices
        components.append((frozenset(vertices), frozenset(component_edges)))
    return tuple(sorted(components, key=lambda c: tuple(vertex_key(v) for v in sorted(c[0], key=vertex_key))))


def canonical_directed_cycle(component):
    vertices, edge_indices = component
    local = defaultdict(list)
    for ei in edge_indices:
        a, b = H_EDGES[ei]
        local[a].append(b)
        local[b].append(a)
    assert all(len(local[v]) == 2 for v in vertices)
    start = min(vertices, key=vertex_key)
    second = min(local[start], key=vertex_key)
    cycle = [start, second]
    previous, current = start, second
    while current != start:
        following = local[current][0] if local[current][1] == previous else local[current][1]
        previous, current = current, following
        if current != start:
            cycle.append(current)
    assert len(cycle) == len(vertices)
    return tuple(cycle)


def orientation_coefficients(cycle):
    result = {}
    for a, b in zip(cycle, cycle[1:] + cycle[:1]):
        ei = H_EDGES.index(canon((a, b)))
        result[ei] = 1 if H_EDGES[ei] == (a, b) else -1
    return result


FACTOR_COMPONENTS = []
VARIABLES = []
EDGE_ROWS = [[0] * 12 for _ in H_EDGES]
variable_index = 0
for matching_index, matching in enumerate(LIFTED_MATCHINGS):
    factor_edges = frozenset(set(range(len(H_EDGES))) - set(matching))
    components = components_of_edge_set(factor_edges)
    FACTOR_COMPONENTS.append(components)
    for component_index, component in enumerate(components):
        cycle = canonical_directed_cycle(component)
        VARIABLES.append((matching_index, component_index, cycle))
        coeffs = orientation_coefficients(cycle)
        for ei, coefficient in coeffs.items():
            EDGE_ROWS[ei][variable_index] = coefficient
        variable_index += 1


def find_sparse_contradiction(max_rows=5):
    """Find sum of distinct edge rows with signs +/-1 equal to +/-4 unit."""
    rows = tuple(tuple(row) for row in EDGE_ROWS)
    for size in range(1, max_rows + 1):
        for indices in combinations(range(len(rows)), size):
            first = rows[indices[0]]
            # Fix the first coefficient to +1; global negation is redundant.
            for tail_signs in product((-1, 1), repeat=size - 1):
                signs = (1,) + tail_signs
                total = tuple(
                    sum(signs[k] * rows[indices[k]][j] for k in range(size))
                    for j in range(len(VARIABLES))
                )
                nonzero = [(j, x) for j, x in enumerate(total) if x]
                if len(nonzero) == 1 and abs(nonzero[0][1]) >= 2:
                    return indices, signs, total
    return None


def fixed_five_row_certificate():
    named_edges = [
        ((0, 1), (0, 4)),   # p0_1 -- p0_4
        ((0, 5), (5, 0)),   # p0_5 -- p5_0
        ((1, 2), (1, 6)),   # p1_2 -- p1_6
        ((4, 3), (4, 9)),   # p4_3 -- p4_9
        ((5, 7), (5, 8)),   # p5_7 -- p5_8
    ]
    indices = tuple(H_EDGES.index(canon(e)) for e in named_edges)
    signs = (1, -1, -1, -1, -1)
    total = tuple(
        sum(signs[k] * EDGE_ROWS[indices[k]][j] for k in range(5))
        for j in range(len(VARIABLES))
    )
    return indices, signs, total


def main():
    assert len(H_VERTICES) == 18
    assert len(H_EDGES) == 27
    assert all(a != b for a, b in H_EDGES)
    assert all(len(H_ADJ[v]) == 3 for v in H_VERTICES)
    indexed_edges = {
        tuple(sorted((H_VERTICES.index(a), H_VERTICES.index(b))))
        for a, b in H_EDGES
    }
    assert release_edge_list() == indexed_edges

    deletion_tests = 0
    for size in range(3):
        for deleted_tuple in combinations(range(len(H_EDGES)), size):
            deletion_tests += 1
            assert connected_after_deleting(frozenset(deleted_tuple))
    assert deletion_tests == 379

    assert len(P_MATCHINGS) == 6
    assert all(len(a & b) == 1 for a, b in combinations(P_MATCHINGS, 2))
    p_edge_counts = Counter(e for matching in P_MATCHINGS for e in matching)
    assert set(p_edge_counts.values()) == {2}

    assert len(H_MATCHINGS) == 18
    assert all(not (a.isdisjoint(b)) for a, b in combinations(H_MATCHINGS, 2))
    assert len(set(LIFTED_MATCHINGS)) == 6
    assert all(m in H_MATCHINGS for m in LIFTED_MATCHINGS)

    double_covers = []
    for indices in combinations_with_replacement(range(len(H_MATCHINGS)), 6):
        counts = [0] * len(H_EDGES)
        for mi in indices:
            for ei in H_MATCHINGS[mi]:
                counts[ei] += 1
        if counts == [2] * len(H_EDGES):
            double_covers.append(indices)
    assert len(double_covers) == 1
    unique_cover = tuple(H_MATCHINGS[i] for i in double_covers[0])
    assert set(unique_cover) == set(LIFTED_MATCHINGS)

    assert len(VARIABLES) == 12
    assert all(len(components) == 2 for components in FACTOR_COMPONENTS)
    contradiction = fixed_five_row_certificate()
    indices, signs, total = contradiction
    nonzero = [(i, x) for i, x in enumerate(total) if x]
    assert total == (4,) + (0,) * 11
    # A blind bounded search independently rediscovers this same shortest
    # certificate (up to multiplying the whole row combination by -1).
    assert find_sparse_contradiction() == contradiction

    # Exhaustion is a secondary check; the displayed row combination is the
    # concise nonexistence certificate used in the proof note.
    feasible_sign_assignments = 0
    for assignment in product((-1, 1), repeat=len(VARIABLES)):
        if all(sum(row[j] * assignment[j] for j in range(len(VARIABLES))) == 0 for row in EDGE_ROWS):
            feasible_sign_assignments += 1
    assert feasible_sign_assignments == 0

    report = {
        "petersen_edges": [list(e) for e in P_EDGES],
        "expanded_vertices": sorted(EXPANDED),
        "graph_vertices": [vertex_name(v) for v in H_VERTICES],
        "graph_edges": [edge_name(e) for e in H_EDGES],
        "order": len(H_VERTICES),
        "size": len(H_EDGES),
        "edge_deletion_connectivity_tests": deletion_tests,
        "petersen_perfect_matchings": [[list(e) for e in sorted(m)] for m in P_MATCHINGS],
        "expanded_graph_perfect_matching_count": len(H_MATCHINGS),
        "six_matching_multisets_tested": sum(1 for _ in combinations_with_replacement(range(len(H_MATCHINGS)), 6)),
        "double_cover_count": len(double_covers),
        "lifted_matchings": [[edge_name(H_EDGES[i]) for i in sorted(m)] for m in LIFTED_MATCHINGS],
        "factor_components": [
            [[vertex_name(v) for v in canonical_directed_cycle(component)] for component in components]
            for components in FACTOR_COMPONENTS
        ],
        "variables": [f"x{i}" for i in range(len(VARIABLES))],
        "selected_edge_equations": [
            {
                "sign": signs[k],
                "edge": edge_name(H_EDGES[ei]),
                "row": EDGE_ROWS[ei],
            }
            for k, ei in enumerate(indices)
        ],
        "combined_row": list(total),
        "isolated_variable": f"x{nonzero[0][0]}",
        "isolated_coefficient": nonzero[0][1],
        "component_sign_assignments_tested": 2 ** len(VARIABLES),
        "feasible_component_sign_assignments": feasible_sign_assignments,
    }
    print(json.dumps({
        "component_orientation_assignments": report["component_sign_assignments_tested"],
        "double_covers": report["double_cover_count"],
        "edges": report["size"],
        "implementation": "expansion",
        "matching_multisets": report["six_matching_multisets_tested"],
        "perfect_matchings": report["expanded_graph_perfect_matching_count"],
        "status": "passed",
        "vertices": report["order"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
