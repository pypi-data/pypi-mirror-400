# Forte Set Theory: Complete Pitch-Class Set Dataset

## Context

This dataset represents a comprehensive computational approach to **pitch-class (pc) set theory**, based on the analytical framework developed by Allen Forte in his seminal work [*The Structure of Atonal Music* (1973)](https://www.amazon.com/Structure-Atonal-Music-Allen-Forte/dp/0300021208).

Our goal is to:
1. **Enumerate all 4,096 possible subsets** of the 12 pitch classes {0, 1, ..., 11}
2. **Compute structural properties** for each set based on Forte's theoretical framework
3. **Establish relationships** between sets through various graph structures (subset lattices, equivalence classes, Z-relations, etc.)
4. **Provide a flexible data format** (pandas DataFrames, parquet files) for music-theoretical analysis and computational composition

This work builds a bridge between traditional music theory and modern data science, enabling researchers and composers to explore the mathematical structures underlying atonal and twelve-tone music.

---

## Dataset Structure

### Nodes DataFrame (`nodes_df`)

Each of the **4,096 rows** represents one subset of the 12 pitch classes. The dataset uses a **bitmap integer representation** where each subset is encoded as an integer from 0 to 4095, with bit `i` set if pitch class `i` is in the set.

#### Core Fields

##### `id_` (int)
**Bitmap integer representation** (0 to 4095) where bit `i` indicates the presence of pitch class `i` in the set.

- **Example:** `145 = 0b10010001` represents the set {0, 4, 7} (C major triad in pitch-class space)
- **Utility:** Enables efficient bitwise operations for subset testing, complement computation, and set manipulation

##### `pcset` (tuple)
**Sorted tuple of pitch classes** in ascending order.

- **Example:** `(0, 4, 7)` for C major triad
- **Convention:** Pitch class 0 = C, 1 = C♯/D♭, ..., 11 = B
- **Utility:** Human-readable representation for inspection and debugging

##### `cardinality` (int)
**Number of pitch classes** in the set (0 to 12).

- **Reference:** Part 1, Section 1.1 of Forte (1973)
- **Utility:** Primary filter for analysis; different cardinalities have different theoretical properties
- **Distribution:** Symmetric around 6 (220 triads, 495 tetrads, 924 hexachords, etc.)

##### `contains_zero` (bool)
**Whether pitch class 0 is in the set.**

- **Utility:** Quick filter for sets in "normal form" starting position
- **Context:** Many analytical workflows begin by transposing sets to contain 0

##### `complement_id` (int)
**Bitmap ID of the complement set** (all pitch classes NOT in this set).

- **Computation:** `complement_id = 4095 ^ id_` (bitwise XOR with all-ones)
- **Theoretical significance:** Forte's theory establishes deep relationships between a set and its complement
- **Example:** The complement of {0, 4, 7} is {1, 2, 3, 5, 6, 8, 9, 10, 11}

---

#### Equivalence and Classification Fields

##### `prime_form` (tuple)
**Canonical representative** of the equivalence class under transposition and inversion (T/I equivalence).

- **Reference:** Part 1, Section 1.2 ("Normal order; the prime forms")
- **Algorithm:**
  1. Compute best normal order for the set and its inversion
  2. Transpose each to start on 0
  3. Return the lexicographically smaller result
- **Example:** Both {0, 4, 7} and {0, 3, 7} have prime form `(0, 3, 7)` because one is the inversion of the other
- **Utility:** Groups all transpositions and inversions of a "chord type" into a single representative

##### `best_normal_order` (tuple)
**Pre-prime ordering** that represents the most compact circular permutation of the pitch classes.

- **Reference:** Part 1, Section 1.2 ("Normal order; the prime forms")
- **Algorithm:**
  1. Arrange pitch classes in ascending order
  2. Test all circular permutations
  3. Select the permutation with the smallest interval between first and last pitch class (**Requirement 1**)
  4. If there's a tie, select the permutation with the smallest successive differences from the first pitch class (**Requirement 2**)
- **Example:** For {0, 3, 8, 11}, one valid normal order is `(11, 0, 3, 8)` (span of 9 semitones)
- **Theoretical utility:** Provides the canonical *template ordering* before transposition-to-0; useful for identifying sets encountered in music before they are converted to prime form
- **Analogy:** If prime form is the "dictionary entry," normal order is the "original spelling" in the music

##### `forte_name` (str or None)
**Forte's label** for the set class (e.g., "3-11", "4-Z29", "6-35").

- **Reference:** Appendix 1 (Complete list of set classes)
- **Format:** `{cardinality}-{index}` or `{cardinality}-Z{index}` for Z-related sets
- **Coverage:** Assigned to sets with cardinality 3–6; larger sets use their complement's name
- **Example:** `"3-11"` for the major/minor triad prime form `(0, 3, 7)`
- **Utility:** Standard nomenclature for communication with music theorists and score analysis

##### `is_forte_set` (bool)
**True if this exact set IS a prime form** (i.e., it appears in Forte's canonical list).

- **Utility:** Filters to the 114 distinct prime forms that represent all equivalence classes
- **Example:** `(0, 3, 7)` is a Forte set; `(0, 4, 7)` is not (it reduces to the same prime form)

---

#### Intervallic Properties

##### `interval_vector` (tuple of 6 ints)
**Counts of each interval class (ic1 through ic6)** present in the set.

- **Reference:** Part 1, Section 1.6 ("The interval vector")
- **Format:** `(ic1, ic2, ic3, ic4, ic5, ic6)` where each entry counts the number of times that interval class appears between pairs of pitch classes
- **Interval class mapping:**
  - ic1 = semitone or major seventh (interval 1 or 11)
  - ic2 = major second or minor seventh (interval 2 or 10)
  - ic3 = minor third or major sixth (interval 3 or 9)
  - ic4 = major third or minor sixth (interval 4 or 8)
  - ic5 = perfect fourth or fifth (interval 5 or 7)
  - ic6 = tritone (interval 6)
- **Example:** `(0, 0, 1, 1, 1, 0)` for the major triad {0, 4, 7} (one each of ic3, ic4, ic5)
- **Theoretical significance:** The interval vector is invariant under transposition and inversion; it captures the "sound quality" of a set class
- **Utility:** Used to identify Z-relations and measure similarity between sets

##### `is_t_symmetric` (bool)
**True if the set is invariant under some non-zero transposition.**

- **Reference:** Part 1, Section 1.11 ("Invariant subsets under transposition")
- **Example:** The diminished seventh chord {0, 3, 6, 9} (4-28) is invariant under T₃, T₆, and T₉
- **Theoretical significance:** Symmetric sets yield fewer than 12 distinct transpositions, reducing the available "versions" for compositional use
- **Utility:** Identifies sets with special structural properties; relevant for voice-leading analysis

---

#### New Fields: Advanced Theoretical Measures

##### `z_correspondent_prime_form` (tuple or None)
**Prime form of the Z-related partner**, if one exists.

- **Reference:** Part 1, Section 1.9 ("Non-equivalent pc sets with identical vectors")
- **Definition:** Two sets are **Z-related** if they share the same interval vector but have different prime forms (i.e., they are not T/I-equivalent)
- **Theoretical significance:** Z-pairs are structurally distinct yet share identical interval content—a paradoxical phenomenon central to Forte's theory
- **Example:** Sets 6-Z3 `(0, 1, 2, 3, 5, 6)` and 6-Z36 `(0, 1, 2, 3, 4, 7)` are Z-related
- **Utility:** Enables composers to substitute sets with identical "harmonic quality" but different pitch-class structure

##### `z_correspondent_forte_name` (str or None)
**Forte label** of the Z-related partner.

- **Utility:** Human-readable reference for the Z-correspondent

---

##### `n_T` (int)
**Number of distinct transpositions** in the T-orbit (range: 1 to 12).

- **Reference:** Part 1, Section 1.11 ("Invariant subsets under transposition")
- **Computation:** Count the number of unique sets produced by $T_0, T_1, ..., T_{11}$
- **Formula:** For a set with $m$ non-zero transpositions that produce duplicates, $n(T) = 12 / (m+1)$
- **Theoretical utility:** Symmetric sets (like the diminished seventh chord 4-28) produce duplicate forms at certain transposition levels, reducing the number of unique "versions" available to a composer
- **Example:**
  - Major triad {0, 4, 7}: $n(T) = 12$ (all transpositions are distinct)
  - Diminished seventh {0, 3, 6, 9}: $n(T) = 3$ (only T₀, T₁, T₂ produce unique sets)
- **Analogy:** If each set is a "building block," $n(T)$ tells you how many different positions you can place it in before patterns repeat

##### `n_I` (int)
**Number of distinct inversions** in the IT-orbit (range: 1 to 12).

- **Reference:** Part 1, Section 1.12 ("Invariant subsets under inversion")
- **Computation:** Count the number of unique sets produced by $IT_0, IT_1, ..., IT_{11}$
- **Theoretical utility:** Sets that are replicas of their own inversion (up to transposition) reduce the total number of distinct forms by a factor of 12
- **Example:**
  - Augmented triad {0, 4, 8}: $n(I) = 4$ (inversionally symmetric)
  - Major triad {0, 4, 7}: $n(I) = 12$ (inversion produces a different set class—minor triad)
- **Combined significance:** The total number of distinct forms in the TI-orbit is $n(T) \times n(I) / 12$ (since T₀ is counted in both)

---

##### `kh_size` (int)
**Size of the Kh subcomplex** for this set as nexus.

- **Reference:** Part 2, Section 2.2 ("The subcomplex Kh") and Section 2.3 ("Set-Complex sizes")
- **Definition:** The Kh subcomplex is a restricted version of Forte's K complex where a set $S$ and its complement must both satisfy the inclusion relation with nexus set $T$ and its complement $T'$:

  $$S \in K_h(T) \iff (S \subseteq T \text{ or } T \subseteq S) \text{ AND } (S \subseteq T' \text{ or } T' \subseteq S)$$

- **Computation:** For a nexus set $T$, count all sets $S$ in the 12-tone universe that satisfy the reciprocal complement relation
- **Theoretical utility:** Acts as a measure of **relational density**—a set with a large Kh size is a powerful "hub" in a musical structure, connecting to many other sets through subset/superset relations
- **Analogy:** If pitch-class sets are "cities," Kh size measures how many "roads" connect this city to others through subset relationships
- **Example:** The chromatic scale {0, 1, 2, ..., 11} has a large Kh size because many sets are subsets of it

---

##### `hexachord_combinatorial` (str or None)
**Combinatorial property label for hexachords** (cardinality 6 only).

- **Reference:** Part 1, Section 1.14 (Notes on Example 73)
- **Definition:** A hexachord is **combinatorial** if it can form a **12-tone aggregate** when combined with one of its own transformations ($T_n$ or $IT_n$)
- **Labels:**
  - `'a'` (all-combinatorial): Both T-combinatorial and I-combinatorial
  - `'p'` (prime combinatorial): T-combinatorial only
  - `'i'` (inversion combinatorial): I-combinatorial only
  - `None`: Not combinatorial or not a hexachord
- **Theoretical utility:** Foundational for certain structural designs in 20th-century music (Schoenberg, Webern, Babbitt)
- **Computation:** For hexachord $H$, check if there exists $T_n$ (n ≠ 0) such that $H \cap T_n(H) = \emptyset$, and similarly for $IT_n$
- **Example:** The whole-tone scale {0, 2, 4, 6, 8, 10} (6-35) is all-combinatorial
- **Analogy:** If a hexachord is a "puzzle piece," combinatoriality tells you whether it can interlock with a transformed copy of itself to fill the 12-tone space

---

##### `max_T_invariance` (int)
**Maximum number of pitch classes** that remain invariant (fixed) under the *best* non-trivial transposition.

- **Reference:** Part 1, Section 1.11 ("Invariant subsets under transposition")
- **Computation:** Inspect the interval vector; for interval class 1–5, the vector entry gives the number of invariants for that transposition level; for ic6, multiply the entry by 2
- **Theoretical utility:** Quantifies the potential for **structural continuity** when a set is transposed—how much of the "sound" stays the same
- **Example:** For {0, 1, 5, 6} (tetrad), transposing by T₅ keeps two pitch classes fixed
- **Analogy:** If a set is a "constellation of stars," max_T_invariance measures how many stars stay in the same position after the constellation rotates

##### `max_T_invariance_n` (int)
**Transposition level** (0–11) that yields `max_T_invariance`.

##### `max_I_invariance` (int)
**Maximum number of pitch classes** that remain invariant under the *best* inversion.

- **Reference:** Part 1, Section 1.12 ("Invariant subsets under inversion")
- **Computation:** Create a "sums table" (all possible sums of pairs within the set); the sum that appears most frequently is the transposition index for $IT_n$ that yields the maximum invariants
- **Theoretical utility:** Measures the degree to which a set "reflects onto itself"

##### `max_I_invariance_n` (int)
**Inversion index** (0–11) that yields `max_I_invariance`.

---

## Link DataFrames: Relationships Between Sets

In addition to the nodes DataFrame, we provide several **link DataFrames** that encode various relationships between pitch-class sets as graph edges.

### Immediate Subset Links (Hasse Diagram)
**Source → Target** edges where Source ⊂ Target and |Target| = |Source| + 1.

- **Graph type:** Directed acyclic graph (DAG)
- **Theoretical interpretation:** The subset lattice ordered by inclusion
- **Utility:** Visualizes the hierarchical structure of pc-sets; useful for finding "voice-leading paths" through subset expansion

### Complement Links
**Source ↔ Target** pairs where Target = complement of Source.

- **Theoretical significance:** Forte's theory establishes that a set and its complement share deep structural relationships
- **Utility:** Enables analysis of "negative space" in pc-set compositions

### TI-Equivalence Links
**Source ↔ Target** pairs where Source and Target share the same `prime_form`.

- **Interpretation:** All transpositions and inversions of a given "chord type"
- **Utility:** Groups sets into equivalence classes for set-class analysis

### Z-Relation Links
**Source ↔ Target** pairs where:
- Source and Target have the same `interval_vector`
- Source and Target have different `prime_form`

- **Theoretical significance:** Z-relations are one of the most mysterious phenomena in pc-set theory
- **Utility:** Enables compositional techniques based on preserving "harmonic color" while varying pitch-class structure

### R_p Similarity Links
**Source ↔ Target** pairs (same cardinality) that share $n-1$ pitch classes under some $T_n$ or $IT_n$.

- **Reference:** Part 2, Section 2.4 ("Similarity relations")
- **Utility:** Voice-leading analysis; sets that differ by a single pitch-class motion

---

## References

This dataset and the accompanying `atonal.base` module implement the analytical framework from:

**Forte, Allen.** *The Structure of Atonal Music.* New Haven: Yale University Press, 1973.
[Amazon Link](https://www.amazon.com/Structure-Atonal-Music-Allen-Forte/dp/0300021208)

Key sections referenced:
- **Part 1, §1.1–1.6:** Basic definitions, prime form, interval vector
- **Part 1, §1.9:** Z-relations
- **Part 1, §1.11–1.12:** Invariance under T and I
- **Part 1, §1.14:** Combinatoriality for hexachords
- **Part 2, §2.2–2.3:** K and Kh complexes
- **Part 2, §2.4:** Similarity relations

---

## Usage Examples

### Loading the Data

```python
import pandas as pd
from atonal.base import build_pcset_nodes_df

# Generate the full dataset
nodes_df = build_pcset_nodes_df()

# Filter to triads (cardinality 3)
triads = nodes_df[nodes_df['cardinality'] == 3]

# Find all sets with a specific interval vector
augmented_triads = nodes_df[nodes_df['interval_vector'] == (0, 0, 0, 3, 0, 0)]
```

### Finding Z-Related Pairs

```python
# Find all Z-related pairs
z_pairs = nodes_df[nodes_df['z_correspondent_prime_form'].notna()]

# Example: 6-Z3 and 6-Z36
set_6z3 = nodes_df[nodes_df['forte_name'] == '6-Z3'].iloc[0]
print(f"6-Z3: {set_6z3['prime_form']}")
print(f"Z-correspondent: {set_6z3['z_correspondent_prime_form']}")
print(f"Both have IV: {set_6z3['interval_vector']}")
```

### Analyzing Symmetry

```python
# Find all transpositionally symmetric sets
symmetric = nodes_df[nodes_df['is_t_symmetric'] == True]

# Find sets with maximum T-invariance
highly_invariant = nodes_df[nodes_df['max_T_invariance'] >= 3]
```

### Hexachord Combinatoriality

```python
# Find all-combinatorial hexachords
all_comb = nodes_df[nodes_df['hexachord_combinatorial'] == 'a']
print(f"All-combinatorial hexachords: {len(all_comb)}")
```

---

## Computational Architecture

All core functions are implemented in the `atonal.base` module:

- **Bitmap representation:** Efficient set operations using bitwise arithmetic
- **Memoization:** LRU caching for expensive computations (e.g., prime form)
- **Pandas integration:** DataFrames returned by default for easy filtering and analysis
- **Graph construction:** Multiple link types available for network analysis

---

## Future Extensions

Potential additions to this framework:
- **Voice-leading distance metrics** (Tymoczko, Callender)
- **Fourier transforms on pc-sets** (Quinn, Amiot)
- **Inclusion lattice visualizations** with interactive graphics
- **Machine learning features** derived from pc-set properties
- **MIDI/audio synthesis** for "playing" pc-sets and their transformations

---

**Maintained by:** The `tonal` project contributors
**License:** (Specify your project's license here)
**Last updated:** 2026-01-07
