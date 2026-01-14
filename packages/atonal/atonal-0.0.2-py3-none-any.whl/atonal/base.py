"""
base.py

A comprehensive module for pitch-class set theory and chord voicing analysis.

This module provides two main functionalities:

1. **Forte-Style Pitch-Class Set Theory** (Section 0)
   - Complete enumeration and analysis of all 4,096 subsets of the 12 pitch classes
   - Implementation of Allen Forte's analytical framework from "The Structure of
     Atonal Music" (1973)
   - Computation of prime forms, interval vectors, Z-relations, invariance properties,
     and more
   - See `tonal/misc/forte_sets.md` for comprehensive field documentation

2. **Chord Voicing Generation and Graph Construction** (Sections 1-4)
   - Enumeration of chord voicings in bounded pitch ranges
   - Graph construction based on voice-leading, shared pitch classes, and subset
     relations
   - Flexible link types for different analytical purposes

Conventions
-----------
- Pitch classes are 0..11 (0 = C, 1 = C#, ..., 11 = B)
- Pitches (not just pitch classes) are integers too: 60 = C4, etc., but here we
  mostly use small integers as semitone offsets from a root
- A "pc-set" is a frozenset of pitch classes
- A "voicing" is a tuple of *pitches* (ordered), e.g. (0, 4, 7), (0, 7, 12)
- A "chord node" in the graph is usually an int-indexed entry referring to a
  voicing or a pc-set

References
----------
Forte, Allen. "The Structure of Atonal Music." Yale University Press, 1973.
https://www.amazon.com/Structure-Atonal-Music-Allen-Forte/dp/0300021208
"""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations, product
from typing import (
    Iterable,
    Iterator,
    List,
    Tuple,
    Callable,
    Dict,
    Any,
    Sequence,
    Set,
    FrozenSet,
    Optional,
    Hashable,
)


# ---------------------------------------------------------------------------
# 0. PC-SET THEORY (FORTE-STYLE UTILITIES)
# ---------------------------------------------------------------------------


@lru_cache(maxsize=None)
def _int_to_pcset(n: int) -> Tuple[int, ...]:
    """Convert a 12-bit bitmap (0..4095) to a sorted pc tuple.

    >>> _int_to_pcset(0)
    ()
    >>> _int_to_pcset(145)  # 0b10010001 -> {0,4,7}
    (0, 4, 7)
    """
    if not (0 <= n < 4096):
        raise ValueError(f"pc-set bitmap out of range [0, 4095]: {n}")
    return tuple(i for i in range(12) if (n >> i) & 1)


def int_to_pcset(n: int) -> Tuple[int, ...]:
    """Public alias for bitmap -> tuple.

    >>> int_to_pcset(145)
    (0, 4, 7)
    """
    return _int_to_pcset(n)


def pcset_to_int(pcs: Iterable[int]) -> int:
    """Convert a pc iterable to a 12-bit bitmap int.

    >>> pcset_to_int((0, 4, 7))
    145
    """
    n = 0
    for p in set(pcs):
        if not (0 <= p < 12):
            raise ValueError(f"Pitch classes must be in [0, 11], got {p}")
        n |= 1 << p
    return n


def transpose(pc_set: Iterable[int], interval: int) -> FrozenSet[int]:
    """Transpose a pc-set by `interval` modulo 12.

    >>> transpose((0, 4, 7), 1) == frozenset({1, 5, 8})
    True
    """
    return frozenset(((p + interval) % 12) for p in set(pc_set))


def invert(pc_set: Iterable[int]) -> FrozenSet[int]:
    """Invert a pc-set about 0 (map p -> -p mod 12).

    >>> invert((0, 4, 7)) == frozenset({0, 5, 8})
    True
    """
    return frozenset(((-p) % 12) for p in set(pc_set))


def best_normal_order(pc_set: Iterable[int]) -> Tuple[int, ...]:
    """Return the best normal order (Forte's packed rotation).

    This is the *pre-prime* ordering: a circular permutation of the pcs in
    ascending registral order, chosen to be most compact.

    Field utility (dataset): “Best Normal Order” provides the canonical
    *template ordering* before transposition-to-0, useful for identifying sets
    encountered in music.

    >>> best_normal_order((0, 4, 7))
    (0, 4, 7)
    >>> best_normal_order((11, 0, 3, 8))  # one valid compact ordering
    (8, 11, 0, 3)
    """

    pcs = sorted(set(pc_set))
    if not pcs:
        return ()
    if len(pcs) == 1:
        return (pcs[0],)

    candidates: List[Tuple[int, ...]] = []
    n = len(pcs)
    for i in range(n):
        rotated = pcs[i:] + [p + 12 for p in pcs[:i]]
        span = rotated[-1] - rotated[0]
        # requirement 2: tie-break by smallest successive distance-from-first
        dist_from_first = tuple(rotated[j] - rotated[0] for j in range(1, n))
        candidates.append((span, dist_from_first, tuple(p % 12 for p in rotated)))

    candidates.sort(key=lambda t: (t[0], t[1]))
    return candidates[0][2]


def _transpose_to_zero(order: Tuple[int, ...]) -> Tuple[int, ...]:
    if not order:
        return ()
    first = order[0]
    return tuple(((p - first) % 12) for p in order)


def prime_form(pc_set: Iterable[int]) -> Tuple[int, ...]:
    """Compute the prime form under T/I equivalence.

    Uses best normal order for the set and its inversion, transposes each to 0,
    and returns the lexicographically smaller.

    >>> prime_form((0, 4, 7))
    (0, 3, 7)
    >>> prime_form(())
    ()
    """
    pcs = tuple(sorted(set(pc_set)))
    if not pcs:
        return ()

    no = best_normal_order(pcs)
    inv_no = best_normal_order(invert(pcs))
    a = _transpose_to_zero(no)
    b = _transpose_to_zero(inv_no)
    return min(a, b)


def interval_vector(pc_set: Iterable[int]) -> Tuple[int, int, int, int, int, int]:
    """Compute the interval vector (ic1..ic6) for a pc-set.

    >>> interval_vector((0, 4, 7))
    (0, 0, 1, 1, 1, 0)
    """
    pcs = sorted(set(pc_set))
    n = len(pcs)
    v = [0] * 6
    for i in range(n):
        for j in range(i + 1, n):
            diff = (pcs[j] - pcs[i]) % 12
            ic = min(diff, 12 - diff)
            v[ic - 1] += 1
    return tuple(v)  # type: ignore[return-value]


def is_transpositionally_symmetric(pc_set: Iterable[int]) -> bool:
    """True if the set is invariant under some non-zero transposition.

    >>> is_transpositionally_symmetric((0, 3, 6, 9))
    True
    >>> is_transpositionally_symmetric((0, 4, 7))
    False
    """
    s = frozenset(set(pc_set))
    if not s:
        return False
    for n in range(1, 12):
        if transpose(s, n) == s:
            return True
    return False


def distinct_transpositions(pc_set: Iterable[int]) -> int:
    """Number of distinct transpositions n(T) in the T-orbit.

    Theoretical utility (Forte Part 1 §1.11): symmetric sets yield fewer than 12
    distinct transpositions.

    >>> distinct_transpositions((0, 4, 7))
    12
    >>> distinct_transpositions((0, 3, 6, 9))
    3
    """
    s = frozenset(set(pc_set))
    return len({transpose(s, n) for n in range(12)})


def distinct_inversions(pc_set: Iterable[int]) -> int:
    """Number of distinct inversions n(I) in the IT-orbit.

    Theoretical utility (Forte Part 1 §1.12): sets that are replicas of their
    own inversion (up to transposition) reduce the total number of distinct
    forms.

    >>> distinct_inversions((0, 4, 7))
    12
    """
    s = frozenset(set(pc_set))
    return len({frozenset(((n - p) % 12) for p in s) for n in range(12)})


def max_invariance_degrees(pc_set: Iterable[int]) -> Dict[str, int]:
    """Maximum invariants under transposition and inversion.

    Theoretical utility (Forte Part 1 §§1.11–1.12): quantifies how many pitch
    classes remain fixed (invariant) under the *best* non-trivial T_n and I T_n.

    Returns a dict with keys:
      - max_T_invariance, max_T_invariance_n
      - max_I_invariance, max_I_invariance_n
    """
    s = frozenset(set(pc_set))
    if not s:
        return {
            "max_T_invariance": 0,
            "max_T_invariance_n": 0,
            "max_I_invariance": 0,
            "max_I_invariance_n": 0,
        }

    best_t = 0
    best_t_n = 0
    for n in range(1, 12):
        inv = len(s & transpose(s, n))
        if inv > best_t:
            best_t = inv
            best_t_n = n

    best_i = 0
    best_i_n = 0
    for n in range(12):
        it = frozenset(((n - p) % 12) for p in s)
        inv = len(s & it)
        if inv > best_i:
            best_i = inv
            best_i_n = n

    return {
        "max_T_invariance": best_t,
        "max_T_invariance_n": best_t_n,
        "max_I_invariance": best_i,
        "max_I_invariance_n": best_i_n,
    }


def combinatorial_property_hexachord(pc_set: Iterable[int]) -> Optional[str]:
    """Combinatorial property label for hexachords (cardinality 6).

    Theoretical utility (Forte Part 1 §1.14): flags hexachords that can form a
    12-tone aggregate with one of their own T_n or I T_n transforms.

    Returns:
      - 'a' (all-combinatorial): both T and I combinatorial
      - 'p' (prime combinatorial): T combinatorial only
      - 'i' (inversion combinatorial): I combinatorial only
      - None: not combinatorial or not a hexachord
    """
    s = frozenset(set(pc_set))
    if len(s) != 6:
        return None

    t_ok = any(len(s & transpose(s, n)) == 0 for n in range(1, 12))
    i_ok = any(len(s & frozenset(((n - p) % 12) for p in s)) == 0 for n in range(12))

    if t_ok and i_ok:
        return "a"
    if t_ok:
        return "p"
    if i_ok:
        return "i"
    return None


def kh_complex_size(nexus: int, *, universe_mask: int = 4095) -> int:
    """Compute Kh-complex size for a nexus set (bitmap int).

    Uses the operational definition from Forte Part 2 (§2.2–2.3) as summarized
    in the notebook request:

    A set S is in Kh(T) iff:
      (S ⊆ T or T ⊆ S) AND (S ⊆ T' or T' ⊆ S)
    where T' is the complement of T.

    Returns the count of S in the 12-tone universe satisfying the condition.
    """
    if not (0 <= nexus < 4096):
        raise ValueError(f"nexus must be in [0, 4095], got {nexus}")
    comp = universe_mask ^ nexus
    count = 0
    for s in range(universe_mask + 1):
        rel_t = ((s & nexus) == s) or ((s & nexus) == nexus)
        rel_c = ((s & comp) == s) or ((s & comp) == comp)
        if rel_t and rel_c:
            count += 1
    return count


# --- Forte-class naming ------------------------------------------------------

# Note: This is intentionally just a lookup table (prime_form -> Forte label).
# It can be extended later or replaced by a data file.
FORTE_CLASSES: Dict[Tuple[int, ...], str] = {
    (0, 1, 2): "3-1",
    (0, 1, 3): "3-2",
    (0, 1, 4): "3-3",
    (0, 1, 5): "3-4",
    (0, 1, 6): "3-5",
    (0, 2, 4): "3-6",
    (0, 2, 5): "3-7",
    (0, 2, 6): "3-8",
    (0, 2, 7): "3-9",
    (0, 3, 6): "3-10",
    (0, 3, 7): "3-11",
    (0, 4, 8): "3-12",
    (0, 1, 2, 3): "4-1",
    (0, 1, 2, 4): "4-2",
    (0, 1, 3, 4): "4-3",
    (0, 1, 2, 5): "4-4",
    (0, 1, 2, 6): "4-5",
    (0, 1, 2, 7): "4-6",
    (0, 1, 4, 5): "4-7",
    (0, 1, 5, 6): "4-8",
    (0, 1, 6, 7): "4-9",
    (0, 2, 3, 5): "4-10",
    (0, 1, 3, 5): "4-11",
    (0, 2, 3, 6): "4-12",
    (0, 1, 3, 6): "4-13",
    (0, 2, 3, 7): "4-14",
    (0, 1, 4, 6): "4-15",
    (0, 1, 5, 7): "4-16",
    (0, 3, 4, 7): "4-17",
    (0, 1, 4, 7): "4-18",
    (0, 1, 4, 8): "4-19",
    (0, 1, 5, 8): "4-20",
    (0, 2, 4, 6): "4-21",
    (0, 2, 4, 7): "4-22",
    (0, 2, 5, 7): "4-23",
    (0, 2, 4, 8): "4-24",
    (0, 2, 6, 8): "4-25",
    (0, 3, 5, 8): "4-26",
    (0, 2, 5, 8): "4-27",
    (0, 3, 6, 9): "4-28",
    (0, 1, 3, 7): "4-Z29",
    (0, 1, 2, 3, 4): "5-1",
    (0, 1, 2, 3, 5): "5-2",
    (0, 1, 2, 4, 5): "5-3",
    (0, 1, 2, 3, 6): "5-4",
    (0, 1, 2, 3, 7): "5-5",
    (0, 1, 2, 5, 6): "5-6",
    (0, 1, 2, 6, 7): "5-7",
    (0, 2, 3, 4, 6): "5-8",
    (0, 1, 2, 4, 6): "5-9",
    (0, 1, 3, 4, 6): "5-10",
    (0, 2, 3, 4, 7): "5-11",
    (0, 1, 3, 5, 6): "5-Z12",
    (0, 1, 2, 4, 8): "5-13",
    (0, 1, 2, 5, 7): "5-14",
    (0, 1, 2, 6, 8): "5-15",
    (0, 1, 3, 4, 7): "5-16",
    (0, 1, 3, 4, 8): "5-Z17",
    (0, 1, 4, 5, 7): "5-Z18",
    (0, 1, 3, 6, 7): "5-19",
    (0, 1, 3, 7, 8): "5-20",
    (0, 1, 4, 5, 8): "5-21",
    (0, 1, 4, 7, 8): "5-22",
    (0, 2, 3, 5, 7): "5-23",
    (0, 1, 3, 5, 7): "5-24",
    (0, 2, 3, 5, 8): "5-25",
    (0, 2, 4, 5, 8): "5-26",
    (0, 1, 3, 5, 8): "5-27",
    (0, 2, 3, 6, 8): "5-28",
    (0, 1, 3, 6, 8): "5-29",
    (0, 1, 4, 6, 8): "5-30",
    (0, 1, 3, 6, 9): "5-31",
    (0, 1, 4, 6, 9): "5-32",
    (0, 2, 4, 6, 8): "5-33",
    (0, 2, 4, 6, 9): "5-34",
    (0, 2, 4, 7, 9): "5-35",
    (0, 1, 2, 4, 7): "5-Z36",
    (0, 3, 4, 5, 8): "5-Z37",
    (0, 1, 2, 5, 8): "5-Z38",
    (0, 1, 2, 3, 4, 5): "6-1",
    (0, 1, 2, 3, 4, 6): "6-2",
    (0, 1, 2, 3, 5, 6): "6-Z3",
    (0, 1, 2, 4, 5, 6): "6-Z4",
    (0, 1, 2, 3, 6, 7): "6-5",
    (0, 1, 2, 5, 6, 7): "6-Z6",
    (0, 1, 2, 6, 7, 8): "6-7",
    (0, 2, 3, 4, 5, 7): "6-8",
    (0, 1, 2, 3, 5, 7): "6-9",
    (0, 1, 3, 4, 5, 7): "6-Z10",
    (0, 1, 2, 4, 5, 7): "6-Z11",
    (0, 1, 2, 4, 6, 7): "6-Z12",
    (0, 1, 3, 4, 6, 7): "6-Z13",
    (0, 1, 3, 4, 5, 8): "6-14",
    (0, 1, 2, 4, 5, 8): "6-15",
    (0, 1, 4, 5, 6, 8): "6-16",
    (0, 1, 2, 4, 7, 8): "6-Z17",
    (0, 1, 2, 5, 7, 8): "6-18",
    (0, 1, 3, 4, 7, 8): "6-Z19",
    (0, 1, 4, 5, 8, 9): "6-20",
    (0, 2, 3, 4, 6, 8): "6-21",
    (0, 1, 2, 4, 6, 8): "6-22",
    (0, 2, 3, 5, 6, 8): "6-Z23",
    (0, 1, 3, 4, 6, 8): "6-Z24",
    (0, 1, 3, 5, 6, 8): "6-Z25",
    (0, 1, 3, 5, 7, 8): "6-Z26",
    (0, 1, 3, 4, 6, 9): "6-Z27",
    (0, 1, 3, 5, 6, 9): "6-Z28",
    (0, 1, 3, 6, 8, 9): "6-Z29",
    (0, 1, 3, 6, 7, 9): "6-30",
    (0, 1, 3, 5, 8, 9): "6-31",
    (0, 2, 4, 5, 7, 9): "6-32",
    (0, 2, 3, 5, 7, 9): "6-33",
    (0, 1, 3, 5, 7, 9): "6-34",
    (0, 2, 4, 6, 8, 10): "6-35",
}

PRIME_TO_FORTE: Dict[Tuple[int, ...], str] = dict(FORTE_CLASSES)
FORTE_TO_PRIME: Dict[str, Tuple[int, ...]] = {v: k for k, v in FORTE_CLASSES.items()}


def forte_name(pc_set: Iterable[int]) -> Optional[str]:
    """Return the Forte label for a pc-set, when the Forte class is defined.

    Notes
    -----
    This module currently stores canonical Forte labels for cardinalities 3..6.
    For cardinalities 7..9, the Forte label is derived from the complement's
    class label (same suffix), e.g. 7-35 complements 5-35.

    >>> forte_name((0, 4, 7))
    '3-11'
    >>> forte_name((0, 2, 4, 5, 7, 9, 11))
    '7-35'
    """
    pcs = tuple(sorted(set(pc_set)))
    card = len(pcs)
    if not (3 <= card <= 9):
        return None

    pf = prime_form(pcs)
    if 3 <= card <= 6:
        return PRIME_TO_FORTE.get(pf)

    # For 7..9, map via complement label: k-XX <-> (12-k)-XX
    comp = tuple(sorted(set(range(12)) - set(pcs)))
    comp_pf = prime_form(comp)
    comp_name = PRIME_TO_FORTE.get(comp_pf)
    if comp_name is None:
        return None
    _, suffix = comp_name.split("-", 1)
    return f"{card}-{suffix}"


def _forte_to_prime_form(name: str) -> Optional[Tuple[int, ...]]:
    """Map a Forte label to a representative prime form.

    Supports the module's 3..6 table directly and derives 7..9 labels via
    complement lookup.

    >>> _forte_to_prime_form('3-11')
    (0, 3, 7)
    >>> _forte_to_prime_form('7-35') == prime_form((0, 2, 4, 5, 7, 9, 11))
    True
    """
    if not name or "-" not in name:
        return None
    head, suffix = name.split("-", 1)
    try:
        card = int(head)
    except ValueError:
        return None

    if 3 <= card <= 6:
        return FORTE_TO_PRIME.get(name)

    if 7 <= card <= 9:
        comp_card = 12 - card
        comp_name = f"{comp_card}-{suffix}"
        comp_pf = FORTE_TO_PRIME.get(comp_name)
        if comp_pf is None:
            return None
        # Complement the representative and re-prime to land in the correct class.
        rep = tuple(sorted(set(range(12)) - set(comp_pf)))
        return prime_form(rep)

    return None


def z_correspondent_prime_form(pf: Tuple[int, ...]) -> Optional[Tuple[int, ...]]:
    """Return the Z-correspondent prime form (if any).

    Z-related pairs share the same interval vector but are not T/I-equivalent.
    (Forte Part 1 §1.9)
    """
    if not pf:
        return None
    iv = interval_vector(pf)
    candidates = [
        p for p, name in PRIME_TO_FORTE.items() if interval_vector(p) == iv and p != pf
    ]
    return min(candidates) if candidates else None


def pc_set_convert(
    value: Any,
    to: str,
    *,
    from_repr: Optional[str] = None,
    on_error: str = "raise",
) -> Any:
    """Convert between pc-set representations.

    Supported reps: 'int', 'tuple', 'frozenset', 'set', 'forte', 'prime'.

    >>> pc_set_convert(145, 'tuple')
    (0, 4, 7)
    >>> pc_set_convert((0, 4, 7), 'prime')
    (0, 3, 7)
    """

    def _error(msg: str) -> Any:
        if on_error == "raise":
            raise ValueError(msg)
        return None

    if from_repr is None:
        if isinstance(value, int):
            from_repr = "int"
        elif isinstance(value, str):
            from_repr = "forte"
        elif isinstance(value, frozenset):
            from_repr = "frozenset"
        elif isinstance(value, set):
            from_repr = "set"
        elif isinstance(value, (tuple, list)):
            from_repr = "tuple"
        else:
            return _error(f"Cannot auto-detect representation for {type(value)}")

    if from_repr == "int":
        n = int(value)
        if not (0 <= n < 4096):
            return _error(f"Integer {n} out of range [0, 4095]")
    elif from_repr in ("tuple", "frozenset", "set"):
        try:
            n = pcset_to_int(value)
        except Exception as e:  # pragma: no cover
            return _error(f"Invalid pc-set: {e}")
    elif from_repr == "forte":
        pf = _forte_to_prime_form(value)
        if pf is None:
            return _error(f"Unknown Forte name: {value}")
        n = pcset_to_int(pf)
    elif from_repr == "prime":
        n = pcset_to_int(value)
    else:
        return _error(f"Unknown source representation: {from_repr}")

    if to == "int":
        return n
    if to == "tuple":
        return _int_to_pcset(n)
    if to == "frozenset":
        return frozenset(_int_to_pcset(n))
    if to == "set":
        return set(_int_to_pcset(n))
    if to == "prime":
        return prime_form(_int_to_pcset(n))
    if to == "forte":
        return forte_name(_int_to_pcset(n))
    return _error(f"Unknown target representation: {to}")


# --- Dataset builders (nodes + links) ---------------------------------------


def pcset_node_row(pc_set: Any, /) -> Dict[str, Any]:
    """Compute a single nodes_df-style row for a pc-set.

    This is a convenience helper mirroring the per-row logic of
    :func:`build_pcset_nodes_df` without requiring pandas or enumerating all
    4096 sets.

    Parameters
    ----------
    pc_set:
        Either a 12-bit bitmap int (0..4095) or an iterable of pitch classes.

    Returns
    -------
    dict
        A dict compatible with one row of ``build_pcset_nodes_df()``.

    >>> row = pcset_node_row((0, 2, 4, 5, 7, 9, 11))
    >>> row['forte_name']
    '7-35'
    >>> row['id_'] == pcset_to_int((0, 2, 4, 5, 7, 9, 11))
    True
    """
    if isinstance(pc_set, int):
        n = int(pc_set)
    else:
        n = pcset_to_int(pc_set)

    pcs = _int_to_pcset(n)
    card = len(pcs)
    comp = 4095 ^ n
    pf = prime_form(pcs) if pcs else ()
    iv = interval_vector(pcs) if pcs else (0, 0, 0, 0, 0, 0)

    fn = forte_name(pcs)
    z_pf = z_correspondent_prime_form(pf) if pf else None
    inv = max_invariance_degrees(pcs)

    return {
        "id_": n,
        "pcset": pcs,
        "cardinality": card,
        "contains_zero": 0 in pcs,
        "complement_id": comp,
        "prime_form": pf,
        "forte_name": fn,
        "is_forte_set": bool(pcs and pcs == pf and pf in PRIME_TO_FORTE),
        "interval_vector": iv,
        "is_t_symmetric": is_transpositionally_symmetric(pcs) if pcs else False,
        "z_correspondent_prime_form": z_pf,
        "z_correspondent_forte_name": PRIME_TO_FORTE.get(z_pf) if z_pf else None,
        "n_T": distinct_transpositions(pf if pf else pcs),
        "n_I": distinct_inversions(pf if pf else pcs),
        "kh_size": kh_complex_size(n),
        "hexachord_combinatorial": combinatorial_property_hexachord(pf if pf else pcs),
        "max_T_invariance": inv["max_T_invariance"],
        "max_T_invariance_n": inv["max_T_invariance_n"],
        "max_I_invariance": inv["max_I_invariance"],
        "max_I_invariance_n": inv["max_I_invariance_n"],
        "best_normal_order": best_normal_order(pcs),
    }


def build_pcset_nodes_df() -> "Any":
    """Build nodes_df for all 4096 pc-sets with Forte-style fields.

    Returns a pandas DataFrame when pandas is installed.
    """
    import pandas as pd  # local import to keep module lightweight

    rows: List[Dict[str, Any]] = []
    for n in range(4096):
        pcs = _int_to_pcset(n)
        card = len(pcs)
        comp = 4095 ^ n
        pf = prime_form(pcs) if pcs else ()
        iv = interval_vector(pcs) if pcs else (0, 0, 0, 0, 0, 0)

        fn = forte_name(pcs)

        z_pf = z_correspondent_prime_form(pf) if pf else None
        inv = max_invariance_degrees(pcs)

        rows.append(
            {
                "id_": n,
                "pcset": pcs,
                "cardinality": card,
                "contains_zero": 0 in pcs,
                "complement_id": comp,
                "prime_form": pf,
                "forte_name": fn,
                "is_forte_set": bool(pcs and pcs == pf and pf in PRIME_TO_FORTE),
                "interval_vector": iv,
                "is_t_symmetric": is_transpositionally_symmetric(pcs) if pcs else False,
                # New fields requested
                "z_correspondent_prime_form": z_pf,
                "z_correspondent_forte_name": (
                    PRIME_TO_FORTE.get(z_pf) if z_pf else None
                ),
                "n_T": distinct_transpositions(pf if pf else pcs),
                "n_I": distinct_inversions(pf if pf else pcs),
                "kh_size": kh_complex_size(n),
                "hexachord_combinatorial": combinatorial_property_hexachord(
                    pf if pf else pcs
                ),
                "max_T_invariance": inv["max_T_invariance"],
                "max_T_invariance_n": inv["max_T_invariance_n"],
                "max_I_invariance": inv["max_I_invariance"],
                "max_I_invariance_n": inv["max_I_invariance_n"],
                "best_normal_order": best_normal_order(pcs),
            }
        )

    return pd.DataFrame(rows)


def build_immediate_subset_links_df() -> "Any":
    """Hasse-diagram edges: A -> A ∪ {pc} for every missing pc."""
    import pandas as pd

    links: List[Dict[str, int]] = []
    for a in range(4096):
        for bit in range(12):
            if not (a & (1 << bit)):
                b = a | (1 << bit)
                links.append({"source": a, "target": b})
    return pd.DataFrame(links)


def build_complement_links_df() -> "Any":
    """Links between each set and its complement (half the pairs, undirected)."""
    import pandas as pd

    return pd.DataFrame([{"source": n, "target": 4095 ^ n} for n in range(2048)])


def build_ti_equivalence_links_df(nodes_df: "Any") -> "Any":
    """Links between all nodes in the same T/I set class (same prime form)."""
    import pandas as pd

    links: List[Dict[str, int]] = []
    df = nodes_df[nodes_df["cardinality"] > 0]
    groups = df.groupby("prime_form").groups
    for _, idxs in groups.items():
        if len(idxs) < 2:
            continue
        ids = df.loc[idxs, "id_"].tolist()
        for i, a in enumerate(ids):
            for b in ids[i + 1 :]:
                links.append({"source": a, "target": b})
    return pd.DataFrame(links) if links else pd.DataFrame(columns=["source", "target"])


def build_z_relation_links_df(nodes_df: "Any") -> "Any":
    """Links for Z-related pairs (same IV, different prime form).

    Adds columns: interval_vector, prime_form_a, prime_form_b.
    """
    import pandas as pd

    links: List[Dict[str, Any]] = []
    groups = nodes_df.groupby("interval_vector").groups
    for iv, idxs in groups.items():
        if len(idxs) < 2:
            continue
        g = nodes_df.loc[idxs]
        pfs = g["prime_form"].unique()
        if len(pfs) < 2:
            continue
        ids = g["id_"].tolist()
        for i, a in enumerate(ids):
            pf_a = nodes_df.loc[nodes_df["id_"] == a, "prime_form"].iloc[0]
            for b in ids[i + 1 :]:
                pf_b = nodes_df.loc[nodes_df["id_"] == b, "prime_form"].iloc[0]
                if pf_a != pf_b:
                    links.append(
                        {
                            "source": a,
                            "target": b,
                            "interval_vector": iv,
                            "prime_form_a": pf_a,
                            "prime_form_b": pf_b,
                        }
                    )
    return (
        pd.DataFrame(links)
        if links
        else pd.DataFrame(
            columns=[
                "source",
                "target",
                "interval_vector",
                "prime_form_a",
                "prime_form_b",
            ]
        )
    )


def _inclusion_bitmask(set_a: Iterable[int], set_b: Iterable[int]) -> int:
    """Compute 4-bit inclusion mask for K/Kh complex membership.

    Bit 0: A ⊂ B
    Bit 1: A ⊂ B' (complement of B)
    Bit 2: B ⊂ A
    Bit 3: B ⊂ A' (complement of A)

    Returns integer 0-15.

    Reference: Forte Part 2, §2.2 ("The subcomplex Kh")
    """
    a = set(set_a)
    b = set(set_b)
    universe = set(range(12))
    a_comp = universe - a
    b_comp = universe - b

    mask = 0
    if a and b and a < b:  # proper subset
        mask |= 0b0001
    if a and b_comp and a < b_comp:
        mask |= 0b0010
    if b and a and b < a:
        mask |= 0b0100
    if b and a_comp and b < a_comp:
        mask |= 0b1000

    return mask


def _max_common_subset_size(set_a: Iterable[int], set_b: Iterable[int]) -> int:
    """Maximum size of subset shared between two sets under any T_n or I T_n.

    Used for R_p similarity relation (Forte Part 2, §2.4).

    >>> _max_common_subset_size((0, 4, 7), (0, 3, 7))
    3
    >>> _max_common_subset_size((0, 4, 7), (1, 5, 8))
    3
    """
    if len(set(set_a)) != len(set(set_b)):
        return 0

    a = frozenset(set_a)
    max_common = 0

    for n in range(12):
        # T_n
        b_tn = frozenset((p + n) % 12 for p in set_b)
        common = len(a & b_tn)
        max_common = max(max_common, common)

        # I T_n
        b_itn = frozenset((n - p) % 12 for p in set_b)
        common = len(a & b_itn)
        max_common = max(max_common, common)

    return max_common


def build_k_kh_links_df(nodes_df: "Any", *, kh_only: bool = False) -> "Any":
    """Build K or Kh complex links.

    For K: at least one inclusion relation holds among (A⊂B, A⊂B', B⊂A, B⊂A')
    For Kh: all four must hold (very restrictive)

    Reference: Forte Part 2, §2.2–2.3 ("The subcomplex Kh", "Set-Complex sizes")

    Args:
        nodes_df: The nodes dataframe
        kh_only: If True, only return Kh links (all 4 conditions met)

    Returns:
        DataFrame with columns: source, target, inclusion_mask

    >>> # This is expensive, so skipping doctest
    """
    import pandas as pd

    links: List[Dict[str, Any]] = []

    # Pre-extract pcsets for speed
    pcsets = [tuple(row["pcset"]) for _, row in nodes_df.iterrows()]
    ids = nodes_df["id_"].tolist()

    check = (lambda m: m == 0b1111) if kh_only else (lambda m: m > 0)

    # Only check pairs where cardinalities could allow inclusion
    n = len(nodes_df)
    for i in range(n):
        for j in range(i + 1, n):
            mask = _inclusion_bitmask(pcsets[i], pcsets[j])
            if check(mask):
                links.append(
                    {
                        "source": ids[i],
                        "target": ids[j],
                        "inclusion_mask": mask,
                    }
                )

    return (
        pd.DataFrame(links)
        if links
        else pd.DataFrame(columns=["source", "target", "inclusion_mask"])
    )


def build_rp_similarity_links_df(
    nodes_df: "Any", cardinality: Optional[int] = None
) -> "Any":
    """Build R_p similarity links for sets of a given cardinality.

    Two sets are R_p similar if they share n-1 pitch classes under some T_n or I T_n.

    Reference: Forte Part 2, §2.4 ("Similarity relations")

    Args:
        nodes_df: The nodes dataframe
        cardinality: Optional cardinality to filter to (if None, process all)

    Returns:
        DataFrame with columns: source, target, max_common

    >>> # This is expensive, so skipping doctest
    """
    import pandas as pd

    if cardinality is not None:
        subset = nodes_df[nodes_df["cardinality"] == cardinality]
    else:
        subset = nodes_df[nodes_df["cardinality"] > 1]

    pcsets = [tuple(row["pcset"]) for _, row in subset.iterrows()]
    ids = subset["id_"].tolist()
    cardinalities = [len(pcs) for pcs in pcsets]

    links: List[Dict[str, Any]] = []
    for i, (id_a, pcs_a, card_a) in enumerate(zip(ids, pcsets, cardinalities)):
        for j in range(i + 1, len(ids)):
            id_b, pcs_b, card_b = ids[j], pcsets[j], cardinalities[j]
            if card_a != card_b:
                continue
            common = _max_common_subset_size(pcs_a, pcs_b)
            if common == card_a - 1:
                links.append(
                    {
                        "source": id_a,
                        "target": id_b,
                        "max_common": common,
                    }
                )

    return (
        pd.DataFrame(links)
        if links
        else pd.DataFrame(columns=["source", "target", "max_common"])
    )


# ---------------------------------------------------------------------------
# 1. PITCH-CLASS COMBINATIONS (THEORETICAL, ORDERLESS)
# ---------------------------------------------------------------------------


def pc_combinations(
    k: int,
    pcs: Sequence[int] = tuple(range(12)),
) -> List[FrozenSet[int]]:
    """
    Enumerate all k-element pitch-class combinations from given pitch classes.

    This corresponds to the "dumb upper bound" level:
    choose k from 12, ignore order and octave.

    Args:
        k: number of pitch classes to choose (e.g. 3, 4, 5).
        pcs: iterable of pitch classes to choose from (default 0..11).

    Returns:
        List of frozensets, each a k-element pc-set.

    >>> len(pc_combinations(3, range(12)))
    220
    >>> frozenset({0, 4, 7}) in pc_combinations(3)
    True
    """
    return [frozenset(c) for c in combinations(pcs, k)]


def all_pc_combinations(
    sizes: Iterable[int] = (3, 4, 5),
    pcs: Sequence[int] = tuple(range(12)),
) -> List[FrozenSet[int]]:
    """
    Enumerate all pitch-class combinations for the given sizes.

    >>> combos = all_pc_combinations((3, 4))
    >>> len(combos)  # 220 + 495 = 715
    715
    >>> frozenset({0, 3, 7}) in combos
    True
    """
    out: List[FrozenSet[int]] = []
    for k in sizes:
        out.extend(pc_combinations(k, pcs))
    return out


# ---------------------------------------------------------------------------
# 2. VOICING ENUMERATION IN A BOUNDED RANGE
# ---------------------------------------------------------------------------


def interval_stack_voicings(
    root: int = 0,
    max_semitones: int = 24,
    allowed_intervals: Sequence[int] = (1, 2, 3, 4, 5, 7, 8, 9, 12),
    max_notes: int = 5,
    min_notes: int = 2,
) -> List[Tuple[int, ...]]:
    """
    Enumerate voicings by *stacking intervals* above a root, staying within
    `max_semitones`.

    The algorithm:
        - start with [root]
        - at each step add one of allowed_intervals to the *last* pitch
        - stop when adding any allowed interval would go past max_semitones
        - keep sequences whose length is between min_notes and max_notes

    This is *exactly* the "fixed root, bounded range, interval stacking"
    approach you described.

    Args:
        root: base pitch (0 means 'C' abstractly).
        max_semitones: highest allowed pitch = root + max_semitones.
        allowed_intervals: intervals (in semitones) you can stack.
        max_notes: maximum size of the voicing.
        min_notes: minimum size of the voicing.

    Returns:
        List of tuples, each a voicing like (0, 4, 7) or (0, 5, 9, 12).

    >>> v = interval_stack_voicings(
    ...     root=0,
    ...     max_semitones=12,
    ...     allowed_intervals=(3, 4, 5),
    ...     max_notes=4,
    ...     min_notes=3,
    ... )
    >>> (0, 4, 7) in v or (0, 3, 7) in v
    True
    """
    results: List[Tuple[int, ...]] = []

    def _recur(current: List[int]) -> None:
        if min_notes <= len(current) <= max_notes:
            results.append(tuple(current))
        if len(current) >= max_notes:
            return
        last = current[-1]
        for iv in allowed_intervals:
            nxt = last + iv
            if nxt - root > max_semitones:
                continue
            current.append(nxt)
            _recur(current)
            current.pop()

    _recur([root])
    return results


def expand_with_duplicates(
    base_voicing: Tuple[int, ...],
    max_duplicates: int = 1,
    within: Tuple[int, int] = (0, 24),
) -> List[Tuple[int, ...]]:
    """
    Given a voicing like (0, 4, 7), add (at most) `max_duplicates` extra notes
    that duplicate existing pitch classes in nearby octaves.

    This models the real-life situation where pianists double the root or the
    fifth.

    Args:
        base_voicing: base tuple of pitches (sorted, ascending).
        max_duplicates: how many extra notes to add at most.
        within: (lo, hi) absolute pitch bounds.

    Returns:
        List of voicings, including the original one.

    >>> expand_with_duplicates((0, 4, 7), max_duplicates=1, within=(0, 12))
    [(0, 4, 7), (0, 4, 7, 12)]
    """
    base = tuple(sorted(base_voicing))
    out = [base]

    # Find candidate duplicates: transpose existing notes by octaves
    candidates: List[int] = []
    for p in base:
        for octv in range(-2, 5):  # generous
            cand = p + 12 * octv
            if within[0] <= cand <= within[1] and cand not in base:
                candidates.append(cand)

    # pick up to max_duplicates from candidates
    for r in range(1, max_duplicates + 1):
        for extra in combinations(candidates, r):
            new_v = tuple(sorted(base + extra))
            out.append(new_v)

    return out


# ---------------------------------------------------------------------------
# 3. LINKING / GRAPH CONSTRUCTION
# ---------------------------------------------------------------------------


def shared_pcs(a: Tuple[int, ...], b: Tuple[int, ...]) -> int:
    """
    Number of shared pitch classes between two voicings.

    >>> shared_pcs((0, 4, 7), (0, 7, 11))
    2
    """
    return len({x % 12 for x in a}.intersection({y % 12 for y in b}))


def voice_leading_distance(a: Tuple[int, ...], b: Tuple[int, ...]) -> int:
    """
    A dumb voice-leading distance: compare two voicings of (possibly) the same
    length, and sum absolute differences between *best-matched* notes.

    For simplicity, if lengths differ, we match up to the min length.

    This is *not* Tymoczko's metric, but good enough for building edges.

    >>> voice_leading_distance((0, 4, 7), (0, 5, 7))
    1
    """
    la, lb = len(a), len(b)
    m = min(la, lb)
    # naive: sort and zip
    sa = sorted(a)[:m]
    sb = sorted(b)[:m]
    return sum(abs(x - y) for x, y in zip(sa, sb))


def is_subset_pcs(a: Tuple[int, ...], b: Tuple[int, ...]) -> bool:
    """
    True if pc(a) is subset of pc(b).

    >>> is_subset_pcs((0, 4, 7), (0, 2, 4, 7, 9))
    True
    >>> is_subset_pcs((0, 4, 7), (1, 4, 7))
    False
    """
    return {x % 12 for x in a}.issubset({y % 12 for y in b})


def is_codiatonic(
    a: Tuple[int, ...],
    b: Tuple[int, ...],
    scale_quality: Sequence[int] = (0, 2, 4, 5, 7, 9, 11),
    *,
    tonic: Optional[int] = None,
) -> bool:
    """
    Return True if the union of the pitch classes of chords `a` and `b`
    can be embedded in a single scale derived from the given `scale_quality`.

    If `tonic` is provided (0–11), only test that transposition of the scale;
    otherwise, test all 12 possible transpositions.

    Args:
        a: chord as a tuple of pitches (any integers)
        b: chord as a tuple of pitches (any integers)
        scale_quality: sequence of pitch-class intervals for the scale (default: major)
        tonic: if not None, only use this tonic (0-11), else try all 12 transpositions

    Returns:
        True if union of a and b's pitch classes is a subset of any transposition of the scale.

    >>> is_codiatonic((0, 4, 7), (2, 5, 9))  # e.g. C major triad + D minor triad, both in C major
    True
    >>> is_codiatonic((0, 4, 7), (1, 5, 8))  # No two major triads a semitone apart in major scales...
    False
    >>> is_codiatonic((0, 4, 7), (1, 5, 8), scale_quality=(0,2,3,5,7,8,11))  # ... but in a harmonic minor, there are
    True
    >>> is_codiatonic((0, 4, 7), (1, 4, 8), tonic=0)  # Only test C major scale
    False
    >>> is_codiatonic((0, 4, 7), (1, 4, 8), tonic=1)  # Only test C# major scale
    False
    >>> is_codiatonic((0, 4, 7), (2, 5, 9), tonic=0)  # C major scale, C and Dm triads
    True
    """
    pcs_union = {x % 12 for x in a} | {y % 12 for y in b}
    scale_quality_set = set(x % 12 for x in scale_quality)
    # Precompute all 12 transpositions of the scale as sets
    if tonic is not None:
        tonics = [tonic % 12]
    else:
        tonics = list(range(12))
    for t in tonics:
        scale_pcs = {(p + t) % 12 for p in scale_quality_set}
        if pcs_union.issubset(scale_pcs):
            return True
    return False


def build_graph(
    voicings: List[Tuple[int, ...]],
    *,
    min_shared_pcs: int = 2,
    max_vl_distance: Optional[int] = None,
    include_subset_edges: bool = True,
) -> Dict[int, List[int]]:
    """
    Build an adjacency list over voicings using several criteria.

    A directed edge i -> j is created if ANY of the following are true:
      - shared PCs >= min_shared_pcs
      - voice-leading distance <= max_vl_distance (if given)
      - i is pc-subset of j (if include_subset_edges)

    Args:
        voicings: list of voicings (each is a tuple of ints)
        min_shared_pcs: minimum shared pitch classes to create an edge
        max_vl_distance: max voice-leading distance, or None to ignore
        include_subset_edges: whether to link subset -> superset

    Returns:
        Dict[node_index, List[node_index]]

    >>> V = [(0, 4, 7), (0, 5, 7), (0, 4, 7, 11)]
    >>> G = build_graph(V, min_shared_pcs=2)
    >>> sorted(G[0])
    [1, 2]
    """
    n = len(voicings)
    adj: Dict[int, List[int]] = {i: [] for i in range(n)}

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            a = voicings[i]
            b = voicings[j]
            add_edge = False

            if shared_pcs(a, b) >= min_shared_pcs:
                add_edge = True

            if (max_vl_distance is not None) and voice_leading_distance(
                a, b
            ) <= max_vl_distance:
                add_edge = True

            if include_subset_edges and is_subset_pcs(a, b):
                add_edge = True

            if add_edge:
                adj[i].append(j)

    return adj


# ---------------------------------------------------------------------------
# 4. HIGHER-LEVEL GENERATORS
# ---------------------------------------------------------------------------


def generate_default_voicing_space() -> List[Tuple[int, ...]]:
    """
    Generate a reasonably rich but still small voicing space:

    - root = 0 (C)
    - range = 24 semitones (two octaves)
    - allowed intervals = 2, 3, 4, 5, 7
    - 3 to 5 notes
    - plus optional duplications

    >>> V = generate_default_voicing_space()
    >>> isinstance(V, list) and len(V) > 50
    True
    """
    base = interval_stack_voicings(
        root=0,
        max_semitones=24,
        allowed_intervals=(2, 3, 4, 5, 7),
        max_notes=5,
        min_notes=3,
    )
    # optionally expand some of them with duplicates
    expanded: List[Tuple[int, ...]] = []
    for v in base:
        expanded.extend(expand_with_duplicates(v, max_duplicates=1, within=(0, 24)))
    # deduplicate
    uniq = sorted(set(expanded))
    return uniq


def generate_graph_default() -> Dict[int, List[int]]:
    """
    Convenience: generate a default voicing space and link it.

    >>> G = generate_graph_default()  # doctest: +SKIP
    >>> len(G) > 50  # doctest: +SKIP
    True
    """
    V = generate_default_voicing_space()
    G = build_graph(
        V,
        min_shared_pcs=2,
        max_vl_distance=3,
        include_subset_edges=True,
    )
    return G


# ---------------------------------------------------------------------------
# 5. NOTES ON EXTENSIONS (not code, but pointers)
# ---------------------------------------------------------------------------
# - To include *all 12 transpositions*, just add 0..11 to every pitch.
# - To include *different roots*, call interval_stack_voicings with root=0..11
#   and merge the results.
# - To restrict to "actual" tonal chord qualities, prefilter voicings whose
#   pitch classes match {0,4,7}, {0,3,7}, {0,4,7,11}, etc.
# - To get Forte-style pc-set categories, you’d add a normalization function
#   that maps pitch-class sets to prime form and use that as node label.


# ---------------------------------------------------------------------------
# CHORD TABLES AND LINK COMPUTATION
# ---------------------------------------------------------------------------

# Global configuration for computation warnings
DEFAULT_WARNING_THRESHOLD = 10000  # warn if processing more than this many combinations


def transitive_reduction_links(
    adjacency: Sequence[Sequence[int]],
    *,
    require_dag: bool = True,
) -> List[List[int]]:
    r"""Compute a transitive reduction of a directed graph given as adjacency lists.

    This removes an edge $u \to v$ if there exists an alternate path from $u$ to
    $v$ of length $\ge 2$.

    Notes:
        - For DAGs, the transitive reduction is unique.
        - For graphs with cycles, transitive reduction is not unique; by default
          this function refuses cyclic graphs.

    Args:
        adjacency: adjacency lists indexed by node index.
        require_dag: if True, raise ValueError when cycles are detected.

    Returns:
        A new adjacency list with transitive edges removed.

    >>> adj = [[1, 2], [2], []]  # 0->1->2 and 0->2 (transitive)
    >>> transitive_reduction_links(adj)
    [[1], [2], []]
    """

    adj = [list(dict.fromkeys(neigh)) for neigh in adjacency]
    n = len(adj)

    topo = _topological_order(adj)
    if topo is None:
        if require_dag:
            raise ValueError(
                "Graph has cycles; transitive reduction is ambiguous. "
                "Set require_dag=False to proceed anyway (not recommended)."
            )
        # Fallback: conservative removal using per-edge reachability checks.
        return _transitive_reduction_general(adj)

    # Compute reachability sets in reverse topological order
    reachable: List[Set[int]] = [set() for _ in range(n)]
    for u in reversed(topo):
        r: Set[int] = set()
        for v in adj[u]:
            r.add(v)
            r |= reachable[v]
        reachable[u] = r

    reduced: List[List[int]] = []
    for u in range(n):
        out_u = list(adj[u])
        closure_by_child: Dict[int, Set[int]] = {w: ({w} | reachable[w]) for w in out_u}

        kept: List[int] = []
        for v in out_u:
            # Remove u->v if v is reachable via some other outgoing neighbor.
            implied = any((w != v) and (v in closure_by_child[w]) for w in out_u)
            if implied:
                continue
            kept.append(v)
        reduced.append(kept)

    return reduced


def _topological_order(adjacency: Sequence[Sequence[int]]) -> Optional[List[int]]:
    """Return a topological order if graph is a DAG, else None."""
    n = len(adjacency)
    indeg = [0] * n
    for u in range(n):
        for v in adjacency[u]:
            if 0 <= v < n:
                indeg[v] += 1

    queue = [i for i, d in enumerate(indeg) if d == 0]
    order: List[int] = []
    while queue:
        u = queue.pop()
        order.append(u)
        for v in adjacency[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)

    if len(order) != n:
        return None
    return order


def _transitive_reduction_general(
    adjacency: Sequence[Sequence[int]],
) -> List[List[int]]:
    """Conservative transitive reduction for general directed graphs.

    This removes edge u->v if v is reachable from u without using that edge.
    """

    adj = [list(dict.fromkeys(neigh)) for neigh in adjacency]
    n = len(adj)
    reduced: List[List[int]] = []
    for u in range(n):
        kept: List[int] = []
        for v in adj[u]:
            # BFS from u, skipping the direct edge u->v
            seen = {u}
            stack = [w for w in adj[u] if w != v]
            reachable = False
            while stack and not reachable:
                x = stack.pop()
                if x in seen:
                    continue
                seen.add(x)
                if x == v:
                    reachable = True
                    break
                stack.extend(adj[x])

            if reachable:
                continue
            kept.append(v)
        reduced.append(kept)
    return reduced


def _warn_if_large_computation(
    n: int, threshold: int = DEFAULT_WARNING_THRESHOLD
) -> None:
    """Warn user if computation might take a while."""
    if n > threshold:
        print(f"⚠️  Processing {n:,} items. This may take a while...", flush=True)


def chord_table(
    *,
    voicings: Optional[List[Tuple[int, ...]]] = None,
    id_col: str = "id_",
    index_by: str = "int",
    include_links: bool = False,
    link_kinds: Optional[List[str]] = None,
    use_pandas: bool = True,
    warning_threshold: int = DEFAULT_WARNING_THRESHOLD,
    **link_kwargs,
):
    """
    Build a chord table with one row per chord.

    By default, generates the default voicing space from atonal.base.
    Each row describes the chord's internal features: voicing, number of notes,
    span, pitch-class set, and interval vector.

    If `include_links` is True, link columns are added listing linked chord IDs
    according to the specified link kinds.

    Args:
        voicings: list of chord tuples (if None, use generate_default_voicing_space()).
        id_col: name of the unique ID column.
        index_by: how to compute chord IDs ("int", "hash", or "repr").
        include_links: whether to add link columns.
        link_kinds: types of links to compute if include_links is True
            (e.g., ["shared", "subset", "voiceleading"]).
        use_pandas: return DataFrame if True, otherwise yield dicts.
        warning_threshold: threshold for warning about large computations.
        **link_kwargs: passed to compute_links for each link kind.

    Returns:
        pandas.DataFrame if use_pandas else generator of dicts

    >>> table = list(chord_table(
    ...     voicings=[(0, 4, 7), (0, 3, 7), (0, 4, 7, 11)],
    ...     use_pandas=False
    ... ))
    >>> len(table)
    3
    >>> table[0]['n_notes']
    3
    >>> table[0]['span']
    7
    """
    # 1. Get voicings
    if voicings is None:
        voicings = generate_default_voicing_space()

    _warn_if_large_computation(len(voicings), warning_threshold)

    # 2. Assign IDs based on index_by strategy
    ids = _generate_ids(voicings, index_by)

    # 3. Generate chord feature rows
    rows = list(_chord_feature_rows(voicings, ids, id_col))

    # 4. Add links if requested
    if include_links:
        if link_kinds is None:
            link_kinds = ["shared"]  # default to shared PC links

        for kind in link_kinds:
            _warn_if_large_computation(
                len(rows) * len(rows),
                warning_threshold * 100,  # pairwise is more expensive
            )
            links = compute_links(rows, id_col=id_col, kind=kind, **link_kwargs)
            for row, link_list in zip(rows, links):
                row[f"{kind}_links"] = link_list

    # 5. Produce output
    if use_pandas:
        import pandas as pd

        return pd.DataFrame(rows)
    else:
        return (row for row in rows)


def _generate_ids(voicings: List[Tuple[int, ...]], index_by: str) -> List:
    """Generate IDs for voicings based on indexing strategy."""
    if index_by == "int":
        return list(range(len(voicings)))
    elif index_by == "hash":
        import hashlib

        return [
            int(hashlib.sha1(str(v).encode()).hexdigest(), 16) % (10**12)
            for v in voicings
        ]
    elif index_by == "repr":
        return [repr(v) for v in voicings]
    else:
        raise ValueError(
            f"Unknown index_by mode: {index_by}. " "Must be 'int', 'hash', or 'repr'."
        )


def _chord_feature_rows(
    voicings: List[Tuple[int, ...]], ids: List, id_col: str
) -> Iterator[Dict[str, Any]]:
    """Generate chord feature dicts for each voicing."""
    for chord_id, voicing in zip(ids, voicings):
        yield _chord_features(chord_id, voicing, id_col)


def _chord_features(chord_id, voicing: Tuple[int, ...], id_col: str) -> Dict[str, Any]:
    """Extract features from a single chord voicing."""
    pcs = sorted({p % 12 for p in voicing})
    n_notes = len(voicing)

    # Interval vector: count each interval class (1-6) in the pc-set
    interval_vector = _compute_interval_vector(pcs)

    return {
        id_col: chord_id,
        "voicing": voicing,
        "n_notes": n_notes,
        "span": max(voicing) - min(voicing) if n_notes > 1 else 0,
        "pitch_classes": pcs,
        "n_pcs": len(pcs),
        "interval_vector": interval_vector,
    }


def _compute_interval_vector(pcs: List[int]) -> List[int]:
    """
    Compute the interval vector for a pitch-class set.

    The interval vector counts occurrences of each interval class (1-6).
    """
    return [
        sum(1 for x in pcs for y in pcs if 0 < (y - x) % 12 == ic) for ic in range(1, 7)
    ]


def compute_links(
    chord_table,
    *,
    id_col: str = "id_",
    kind: str = "shared",
    min_shared_pcs: int = 2,
    max_vl_distance: int = 3,
    universe_pcs: Sequence[int] = tuple(range(12)),
    reduce_transitive: bool = False,
    warning_threshold: int = DEFAULT_WARNING_THRESHOLD,
) -> List[List]:
    """
    Compute links between chords based on chosen criteria.

    Args:
        chord_table: list of dicts or DataFrame describing chords.
        id_col: name of chord ID column.
        kind: link definition - either a string or callable:
            String options:
            - "shared": share >= min_shared_pcs pitch classes
            - "subset": subset relation in pitch-class space
            - "voiceleading": voice-leading distance <= max_vl_distance
            - "codiatonic": both chords fit in same major scale

            Callable: custom function with signature:
                (i: int, j: int, voicings: List, pc_sets: List, **kwargs) -> bool
                where i, j are chord indices, voicings is list of tuples,
                pc_sets is list of pitch-class sets, and kwargs includes
                min_shared_pcs and max_vl_distance
        min_shared_pcs: threshold for 'shared' links
        max_vl_distance: max distance for 'voiceleading' links
        warning_threshold: threshold for warning about large computations

    Returns:
        List of lists of chord IDs (parallel to input rows)

    >>> rows = [
    ...     {'id_': 0, 'voicing': (0, 4, 7), 'pitch_classes': [0, 4, 7]},
    ...     {'id_': 1, 'voicing': (0, 5, 7), 'pitch_classes': [0, 5, 7]},
    ...     {'id_': 2, 'voicing': (0, 4, 7, 11), 'pitch_classes': [0, 4, 7, 11]},
    ... ]
    >>> links = compute_links(rows, kind="shared", min_shared_pcs=2)
    >>> len(links[0]) >= 1  # first chord should link to others
    True
    """
    # Normalize to list of dicts
    if hasattr(chord_table, "to_dict"):
        rows = chord_table.to_dict("records")
    else:
        rows = list(chord_table)

    n = len(rows)
    _warn_if_large_computation(n * n, warning_threshold * 100)

    # Extract relevant data
    voicings = [tuple(r["voicing"]) for r in rows]
    ids = [r[id_col] for r in rows]

    # Precompute pitch-class sets for efficiency
    pc_sets = [{p % 12 for p in v} for v in voicings]

    # Build link function based on kind
    link_func = _get_link_function(
        kind,
        pc_sets=pc_sets,
        min_shared_pcs=min_shared_pcs,
        max_vl_distance=max_vl_distance,
        universe_pcs=universe_pcs,
    )

    # Compute links
    adjacency_idx: List[List[int]] = [
        [j for j in range(n) if i != j and link_func(i, j, voicings)] for i in range(n)
    ]

    if reduce_transitive:
        adjacency_idx = transitive_reduction_links(adjacency_idx, require_dag=True)

    return [[ids[j] for j in js] for js in adjacency_idx]


def _get_link_function(
    kind,
    *,
    pc_sets: List[Set[int]],
    min_shared_pcs: int,
    max_vl_distance: int,
    universe_pcs: Sequence[int],
) -> Callable[[int, int, List[Tuple[int, ...]]], bool]:
    """
    Create a link function based on the specified kind.

    Args:
        kind: Either a string name ("shared", "subset", "voiceleading", "codiatonic")
              or a callable with signature (i: int, j: int, voicings, pc_sets, **kwargs) -> bool
        pc_sets: Precomputed pitch-class sets for efficiency
        min_shared_pcs: Threshold for 'shared' links
        max_vl_distance: Max distance for 'voiceleading' links

    Returns:
        A link function with signature (i: int, j: int, voicings: List[Tuple]) -> bool
    """
    # If it's already a callable, wrap it to provide pc_sets
    if callable(kind):

        def link_func(i: int, j: int, voicings: List[Tuple[int, ...]]) -> bool:
            return kind(
                i,
                j,
                voicings,
                pc_sets,
                min_shared_pcs=min_shared_pcs,
                max_vl_distance=max_vl_distance,
            )

        return link_func

    # Otherwise, look up by name
    if kind == "shared":

        def link_func(i: int, j: int, voicings: List[Tuple[int, ...]]) -> bool:
            return len(pc_sets[i] & pc_sets[j]) >= min_shared_pcs

    elif kind == "subset":

        def link_func(i: int, j: int, voicings: List[Tuple[int, ...]]) -> bool:
            return pc_sets[i].issubset(pc_sets[j])

    elif kind == "voiceleading":

        def link_func(i: int, j: int, voicings: List[Tuple[int, ...]]) -> bool:
            return voice_leading_distance(voicings[i], voicings[j]) <= max_vl_distance

    elif kind == "codiatonic":

        def link_func(i: int, j: int, voicings: List[Tuple[int, ...]]) -> bool:
            return is_codiatonic(voicings[i], voicings[j])

    elif kind == "subset_kh":
        # Kh restriction: only include subset edges where both endpoints'
        # complements are present in the node set.
        universe = frozenset({p % 12 for p in universe_pcs})
        pc_frozens = [frozenset(s) for s in pc_sets]
        pc_index: Dict[FrozenSet[int], int] = {s: i for i, s in enumerate(pc_frozens)}
        has_complement = [
            (universe.difference(pc_frozens[i]) in pc_index)
            for i in range(len(pc_frozens))
        ]

        def link_func(i: int, j: int, voicings: List[Tuple[int, ...]]) -> bool:
            if not (has_complement[i] and has_complement[j]):
                return False
            return pc_sets[i].issubset(pc_sets[j])

    else:
        raise ValueError(
            f"Unknown link kind: {kind}. "
            "Must be 'shared', 'subset', 'subset_kh', 'voiceleading', 'codiatonic', or a custom callable."
        )

    return link_func


# if __name__ == "__main__":
#     import doctest

#     doctest.testmod()
