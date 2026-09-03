"""Independent numbered audit of the 18-vertex o6c4c counterexample.

The graph is obtained from the Petersen graph by expanding the closed
neighbourhood of u0 into four triangles.  Only the Python standard library is
used.  The program enumerates perfect matchings, all six-matching multisets,
and a five-row integral obstruction to orienting the unique double cover.
"""

from __future__ import annotations

from itertools import combinations, combinations_with_replacement, product
import json


# Vertex-name table.  A name x[y] denotes the port toward y in the triangle
# replacing x.  Vertices u2,u3,v1,v2,v3,v4 were not expanded.
NAMES = (
    "u2", "u3", "v1", "v2", "v3", "v4",
    "u0[u1]", "u0[u4]", "u0[v0]",
    "u1[u0]", "u1[u2]", "u1[v1]",
    "u4[u3]", "u4[u0]", "u4[v4]",
    "v0[u0]", "v0[v2]", "v0[v3]",
)

# Each edge is stored in the fixed reference orientation min -> max.
EDGES = tuple(sorted(tuple(sorted(e)) for e in (
    # The four replacement triangles.
    (6, 7), (7, 8), (8, 6),
    (9, 10), (10, 11), (11, 9),
    (12, 13), (13, 14), (14, 12),
    (15, 16), (16, 17), (17, 15),
    # Lifts of the fifteen Petersen edges.
    (6, 9), (10, 0), (0, 1), (1, 12), (13, 7),
    (8, 15), (11, 2), (0, 3), (1, 4), (14, 5),
    (16, 3), (3, 5), (5, 2), (2, 4), (4, 17),
)))


def adjacency(edges=EDGES):
    adj = {v: set() for v in range(len(NAMES))}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def connected_after_deleting(deleted):
    deleted = set(deleted)
    adj = adjacency(e for e in EDGES if e not in deleted)
    seen = {0}
    todo = [0]
    while todo:
        v = todo.pop()
        for w in adj[v] - seen:
            seen.add(w)
            todo.append(w)
    return len(seen) == len(NAMES)


def enumerate_perfect_matchings():
    adj = adjacency()

    def rec(unmatched, chosen):
        if not unmatched:
            yield frozenset(chosen)
            return
        v = min(unmatched)
        for w in sorted(adj[v] & unmatched):
            yield from rec(unmatched - {v, w}, chosen + [(min(v, w), max(v, w))])

    return tuple(rec(set(range(len(NAMES))), []))


def matching_double_covers(matchings):
    edge_index = {e: j for j, e in enumerate(EDGES)}
    vectors = []
    for matching in matchings:
        vector = [0] * len(EDGES)
        for edge in matching:
            vector[edge_index[edge]] = 1
        vectors.append(vector)

    covers = []
    for indices in combinations_with_replacement(range(len(matchings)), 6):
        totals = [sum(vectors[i][j] for i in indices) for j in range(len(EDGES))]
        if totals == [2] * len(EDGES):
            covers.append(indices)
    return tuple(covers)


def cycle_components(edge_set):
    adj = {v: set() for v in range(len(NAMES))}
    for a, b in edge_set:
        adj[a].add(b)
        adj[b].add(a)
    active = {v for v in adj if adj[v]}
    components = []
    while active:
        start = min(active)
        component = {start}
        todo = [start]
        while todo:
            v = todo.pop()
            for w in adj[v] - component:
                component.add(w)
                todo.append(w)
        active -= component

        # Canonical directed traversal: start at the least vertex and choose
        # the lesser of its two neighbours as the next vertex.
        first = min(adj[start])
        cycle = [start, first]
        previous, current = start, first
        while True:
            nxt = next(w for w in adj[current] if w != previous)
            if nxt == start:
                break
            cycle.append(nxt)
            previous, current = current, nxt
        assert set(cycle) == component
        components.append(tuple(cycle))
    return tuple(components)


def oriented_component_rows(matchings, cover):
    components = []
    edge_to_component = {}
    edge_to_sign = {}
    for slot, matching_index in enumerate(cover):
        support = set(EDGES) - set(matchings[matching_index])
        slot_components = cycle_components(support)
        for cycle in slot_components:
            component_index = len(components)
            components.append((slot, cycle))
            directed = tuple(zip(cycle, cycle[1:] + cycle[:1]))
            for a, b in directed:
                edge = (min(a, b), max(a, b))
                assert (slot, edge) not in edge_to_component
                edge_to_component[(slot, edge)] = component_index
                edge_to_sign[(slot, edge)] = 1 if a < b else -1

    rows = []
    for edge in EDGES:
        row = [0] * len(components)
        for slot in range(6):
            key = (slot, edge)
            if key in edge_to_component:
                row[edge_to_component[key]] = edge_to_sign[key]
        assert sum(value != 0 for value in row) == 4
        rows.append(tuple(row))
    return tuple(components), tuple(rows)


def find_five_row_obstruction(rows):
    """Find signed distinct rows whose sum is +/-4 times one variable."""
    dimension = len(rows[0])
    for row_indices in combinations(range(len(rows)), 5):
        for coefficients in product((-1, 1), repeat=5):
            total = tuple(
                sum(coefficients[k] * rows[row_indices[k]][j] for k in range(5))
                for j in range(dimension)
            )
            nonzero = [(j, value) for j, value in enumerate(total) if value]
            if len(nonzero) == 1 and abs(nonzero[0][1]) == 4:
                return row_indices, coefficients, nonzero[0]
    raise AssertionError("no five-row obstruction found")


def audit():
    assert len(NAMES) == 18
    assert len(EDGES) == 27 and len(set(EDGES)) == 27
    adj = adjacency()
    assert all(len(adj[v]) == 3 for v in adj)

    deletion_sets = [()] + [(e,) for e in EDGES] + list(combinations(EDGES, 2))
    assert len(deletion_sets) == 379
    assert all(connected_after_deleting(deleted) for deleted in deletion_sets)

    matchings = enumerate_perfect_matchings()
    assert len(matchings) == 18
    assert not any(a.isdisjoint(b) for a, b in combinations(matchings, 2))

    covers = matching_double_covers(matchings)
    assert len(covers) == 1
    cover = covers[0]
    assert len(set(cover)) == 6

    components, rows = oriented_component_rows(matchings, cover)
    assert len(components) == 12
    obstruction = find_five_row_obstruction(rows)
    row_indices, coefficients, (variable, scalar) = obstruction

    # The five necessary edge-balance equations would imply scalar*x=0,
    # impossible because every component-orientation variable is +/-1.
    assert scalar in (-4, 4)

    return {
        "deletion_tests": len(deletion_sets),
        "perfect_matchings": matchings,
        "matching_multisets_tested": 100947,
        "double_cover": cover,
        "components": components,
        "rows": rows,
        "obstruction": obstruction,
    }


def named_edge(edge):
    return [NAMES[edge[0]], NAMES[edge[1]]]


if __name__ == "__main__":
    result = audit()
    print(json.dumps({
        "component_orientation_assignments": 2 ** len(result["components"]),
        "double_covers": 1,
        "edges": len(EDGES),
        "implementation": "numbered",
        "matching_multisets": result["matching_multisets_tested"],
        "perfect_matchings": len(result["perfect_matchings"]),
        "status": "passed",
        "vertices": len(NAMES),
    }, sort_keys=True))
