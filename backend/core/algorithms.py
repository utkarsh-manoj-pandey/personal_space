"""
Aether Core Algorithms Library
Deterministic, high-performance pure Python algorithms and data structures:
- Graph Theory: Directed/Undirected graphs, Dijkstra shortest path, A* heuristic pathfinding, Topological Sorting, Cycle Detection.
- Spatial Indexing: 2D K-D Tree for nearest-neighbor geometric queries.
- Probabilistic Structures: Bloom Filter with optimal bit vector calculation and dual-hash simulation.
- Caching: LRU Cache with TTL expiry and hit/miss telemetry.
- String Algorithms: Levenshtein, Damerau-Levenshtein, Jaro-Winkler similarity, Knuth-Morris-Pratt (KMP) pattern matching, LCS.
"""

import math
import time
import heapq
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Set, Callable, Generic, TypeVar

T = TypeVar('T')


# =============================================================================
# 1. GRAPH THEORY & PATHFINDING
# =============================================================================

class Graph:
    """
    Weighted directed or undirected graph representation using adjacency lists.
    Supports edge weights, node attributes, cycle detection, topological sort,
    Dijkstra shortest path, and A* search.
    """

    def __init__(self, directed: bool = False):
        self.directed = directed
        self.adj: Dict[str, Dict[str, float]] = {}
        self.node_data: Dict[str, Dict[str, Any]] = {}

    def add_node(self, node_id: str, **attributes) -> None:
        """Add a node with optional arbitrary attributes (e.g. coordinates)."""
        if node_id not in self.adj:
            self.adj[node_id] = {}
            self.node_data[node_id] = attributes
        else:
            self.node_data[node_id].update(attributes)

    def add_edge(self, u: str, v: str, weight: float = 1.0) -> None:
        """Add a weighted edge between node u and node v."""
        if u not in self.adj:
            self.add_node(u)
        if v not in self.adj:
            self.add_node(v)
        self.adj[u][v] = float(weight)
        if not self.directed:
            self.adj[v][u] = float(weight)

    def get_neighbors(self, node_id: str) -> Dict[str, float]:
        """Return dict of neighbor nodes with edge weights."""
        return self.adj.get(node_id, {})

    def get_nodes(self) -> List[str]:
        """Return all node IDs in the graph."""
        return list(self.adj.keys())

    def get_edges(self) -> List[Tuple[str, str, float]]:
        """Return list of all (u, v, weight) tuples."""
        edges = []
        seen = set()
        for u in self.adj:
            for v, w in self.adj[u].items():
                if self.directed or (v, u) not in seen:
                    edges.append((u, v, w))
                    seen.add((u, v))
        return edges

    def has_cycle(self) -> bool:
        """Detect whether the graph contains any cycle."""
        if self.directed:
            visited = set()
            rec_stack = set()

            def _dfs_cycle(node: str) -> bool:
                visited.add(node)
                rec_stack.add(node)
                for neighbor in self.adj.get(node, {}):
                    if neighbor not in visited:
                        if _dfs_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                rec_stack.remove(node)
                return False

            for n in self.adj:
                if n not in visited:
                    if _dfs_cycle(n):
                        return True
            return False
        else:
            visited = set()

            def _dfs_undirected(node: str, parent: Optional[str]) -> bool:
                visited.add(node)
                for neighbor in self.adj.get(node, {}):
                    if neighbor not in visited:
                        if _dfs_undirected(neighbor, node):
                            return True
                    elif neighbor != parent:
                        return True
                return False

            for n in self.adj:
                if n not in visited:
                    if _dfs_undirected(n, None):
                        return True
            return False

    def topological_sort(self) -> List[str]:
        """
        Compute topological ordering of DAG nodes using Kahn's in-degree algorithm.
        Raises ValueError if graph contains a cycle or is undirected.
        """
        if not self.directed:
            raise ValueError("Topological sort is only valid for directed acyclic graphs (DAGs).")

        in_degree = {n: 0 for n in self.adj}
        for u in self.adj:
            for v in self.adj[u]:
                in_degree[v] = in_degree.get(v, 0) + 1

        queue = [n for n, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in self.adj.get(node, {}):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.adj):
            raise ValueError("Graph contains a cycle; topological sort is not possible.")

        return order


def dijkstra_shortest_path(graph: Graph, start: str, target: str) -> Dict[str, Any]:
    """
    Compute single-source shortest path using Dijkstra's algorithm with a min-heap.
    Returns path list, total distance, and visited node counts.
    """
    if start not in graph.adj or target not in graph.adj:
        return {"found": False, "path": [], "distance": float('inf'), "visited_count": 0}

    distances: Dict[str, float] = {node: float('inf') for node in graph.adj}
    distances[start] = 0.0
    predecessors: Dict[str, Optional[str]] = {node: None for node in graph.adj}
    visited: Set[str] = set()

    pq: List[Tuple[float, str]] = [(0.0, start)]

    while pq:
        dist_u, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        if u == target:
            break

        for v, weight in graph.adj.get(u, {}).items():
            if v in visited:
                continue
            new_dist = dist_u + weight
            if new_dist < distances[v]:
                distances[v] = new_dist
                predecessors[v] = u
                heapq.heappush(pq, (new_dist, v))

    if distances[target] == float('inf'):
        return {"found": False, "path": [], "distance": float('inf'), "visited_count": len(visited)}

    # Reconstruct path
    path = []
    curr: Optional[str] = target
    while curr is not None:
        path.append(curr)
        curr = predecessors[curr]
    path.reverse()

    return {
        "found": True,
        "path": path,
        "distance": round(distances[target], 4),
        "visited_count": len(visited)
    }


def a_star_search(
    graph: Graph,
    start: str,
    target: str,
    heuristic_fn: Optional[Callable[[str, str], float]] = None
) -> Dict[str, Any]:
    """
    A* search algorithm incorporating an admissible heuristic function h(u, target).
    If no heuristic function is provided, falls back to Dijkstra (h=0).
    """
    if start not in graph.adj or target not in graph.adj:
        return {"found": False, "path": [], "distance": float('inf'), "visited_count": 0}

    if heuristic_fn is None:
        heuristic_fn = lambda u, v: 0.0

    g_score: Dict[str, float] = {node: float('inf') for node in graph.adj}
    g_score[start] = 0.0

    f_score: Dict[str, float] = {node: float('inf') for node in graph.adj}
    f_score[start] = heuristic_fn(start, target)

    predecessors: Dict[str, Optional[str]] = {node: None for node in graph.adj}
    visited: Set[str] = set()

    open_set: List[Tuple[float, float, str]] = [(f_score[start], 0.0, start)]

    while open_set:
        f, g, u = heapq.heappop(open_set)
        if u in visited:
            continue
        visited.add(u)

        if u == target:
            break

        for v, weight in graph.adj.get(u, {}).items():
            if v in visited:
                continue
            tentative_g = g_score[u] + weight
            if tentative_g < g_score[v]:
                predecessors[v] = u
                g_score[v] = tentative_g
                h = heuristic_fn(v, target)
                f_score[v] = tentative_g + h
                heapq.heappush(open_set, (f_score[v], tentative_g, v))

    if g_score[target] == float('inf'):
        return {"found": False, "path": [], "distance": float('inf'), "visited_count": len(visited)}

    path = []
    curr: Optional[str] = target
    while curr is not None:
        path.append(curr)
        curr = predecessors[curr]
    path.reverse()

    return {
        "found": True,
        "path": path,
        "distance": round(g_score[target], 4),
        "visited_count": len(visited)
    }


def topological_sort(graph: Graph) -> List[str]:
    """Helper proxy for graph topological sort."""
    return graph.topological_sort()


def has_cycle(graph: Graph) -> bool:
    """Helper proxy for graph cycle detection."""
    return graph.has_cycle()


# =============================================================================
# 2. SPATIAL INDEXING: 2D K-D TREE
# =============================================================================

class KDNode2D:
    def __init__(self, point: Tuple[float, float], data: Any, left=None, right=None):
        self.point = point
        self.data = data
        self.left = left
        self.right = right


class KDTree2D:
    """
    I have written this part of code because spatial 2D KD-Tree indexing partitions coordinate space
    recursively along alternating axes, enabling logarithmic O(log N) nearest landmark and POI lookups
    on our offline map instead of sluggish linear O(N) full-table scans!
    """

    def __init__(self, points_with_data: Optional[List[Tuple[Tuple[float, float], Any]]] = None):
        if points_with_data:
            self.root = self._build_tree(points_with_data, depth=0)
        else:
            self.root = None

    def _build_tree(self, points: List[Tuple[Tuple[float, float], Any]], depth: int) -> Optional[KDNode2D]:
        if not points:
            return None
        axis = depth % 2
        points.sort(key=lambda p: p[0][axis])
        median_idx = len(points) // 2
        median_pt, median_data = points[median_idx]

        return KDNode2D(
            point=median_pt,
            data=median_data,
            left=self._build_tree(points[:median_idx], depth + 1),
            right=self._build_tree(points[median_idx + 1:], depth + 1)
        )

    def nearest_neighbor(self, target: Tuple[float, float]) -> Optional[Dict[str, Any]]:
        """Find the single closest node to the target point."""
        if not self.root:
            return None

        best: List[Any] = [None, float('inf')]  # [best_node, best_dist_sq]

        def _search(node: Optional[KDNode2D], depth: int):
            if node is None:
                return

            axis = depth % 2
            dx = target[0] - node.point[0]
            dy = target[1] - node.point[1]
            dist_sq = dx * dx + dy * dy

            if dist_sq < best[1]:
                best[0] = node
                best[1] = dist_sq

            axis_dist = target[axis] - node.point[axis]
            first = node.left if axis_dist < 0 else node.right
            second = node.right if axis_dist < 0 else node.left

            _search(first, depth + 1)
            if axis_dist * axis_dist < best[1]:
                _search(second, depth + 1)

        _search(self.root, 0)
        if best[0] is None:
            return None

        return {
            "point": best[0].point,
            "data": best[0].data,
            "distance": round(math.sqrt(best[1]), 6)
        }

    def k_nearest_neighbors(self, target: Tuple[float, float], k: int = 3) -> List[Dict[str, Any]]:
        """Find the k nearest neighbors to the target point."""
        if not self.root or k <= 0:
            return []

        # Max-heap to store k smallest distances: (-dist_sq, id, node)
        heap: List[Tuple[float, int, KDNode2D]] = []
        counter = 0

        def _search(node: Optional[KDNode2D], depth: int):
            nonlocal counter
            if node is None:
                return

            axis = depth % 2
            dx = target[0] - node.point[0]
            dy = target[1] - node.point[1]
            dist_sq = dx * dx + dy * dy

            if len(heap) < k:
                counter += 1
                heapq.heappush(heap, (-dist_sq, counter, node))
            elif dist_sq < -heap[0][0]:
                counter += 1
                heapq.heappushpop(heap, (-dist_sq, counter, node))

            axis_dist = target[axis] - node.point[axis]
            first = node.left if axis_dist < 0 else node.right
            second = node.right if axis_dist < 0 else node.left

            _search(first, depth + 1)
            if len(heap) < k or (axis_dist * axis_dist) < -heap[0][0]:
                _search(second, depth + 1)

        _search(self.root, 0)

        results = []
        for neg_dist_sq, _, node in sorted(heap, key=lambda x: -x[0]):
            results.append({
                "point": node.point,
                "data": node.data,
                "distance": round(math.sqrt(-neg_dist_sq), 6)
            })
        return results


# =============================================================================
# 3. PROBABILISTIC DATA STRUCTURES: BLOOM FILTER
# =============================================================================

class BloomFilter:
    """
    Space-efficient probabilistic set membership filter.
    Eliminates false negatives entirely while bounding false positives.
    Uses double-hashing (Kirsch-Mitzenmacher optimization) based on MD5 and SHA-256.
    """

    def __init__(self, expected_elements: int = 1000, false_positive_rate: float = 0.01):
        if expected_elements <= 0:
            expected_elements = 100
        if not (0 < false_positive_rate < 1.0):
            false_positive_rate = 0.01

        self.expected_elements = expected_elements
        self.fp_rate = false_positive_rate

        # Optimal bit size m = -(n * ln(p)) / (ln(2)^2)
        m = -(expected_elements * math.log(false_positive_rate)) / (math.log(2) ** 2)
        self.bit_size = max(64, int(math.ceil(m)))

        # Optimal hash count k = (m / n) * ln(2)
        k = (self.bit_size / expected_elements) * math.log(2)
        self.hash_count = max(1, int(round(k)))

        self.bit_array = bytearray((self.bit_size + 7) // 8)
        self.elements_count = 0

    def _get_hashes(self, item: str) -> List[int]:
        item_bytes = item.encode('utf-8')
        h1 = int(hashlib.md5(item_bytes).hexdigest(), 16)
        h2 = int(hashlib.sha256(item_bytes).hexdigest(), 16)
        return [(h1 + i * h2) % self.bit_size for i in range(self.hash_count)]

    def add(self, item: str) -> None:
        """Add an item to the Bloom filter."""
        for bit_index in self._get_hashes(item):
            byte_idx = bit_index // 8
            bit_offset = bit_index % 8
            self.bit_array[byte_idx] |= (1 << bit_offset)
        self.elements_count += 1

    def contains(self, item: str) -> bool:
        """
        Check if item is likely in the set.
        False negatives are impossible. False positives adhere to configured rate.
        """
        for bit_index in self._get_hashes(item):
            byte_idx = bit_index // 8
            bit_offset = bit_index % 8
            if not (self.bit_array[byte_idx] & (1 << bit_offset)):
                return False
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Return operational telemetry for the filter."""
        ones_count = sum(bin(b).count('1') for b in self.bit_array)
        fill_ratio = ones_count / self.bit_size
        return {
            "bit_size": self.bit_size,
            "hash_count": self.hash_count,
            "elements_added": self.elements_count,
            "fill_ratio": round(fill_ratio, 4),
            "estimated_current_fp_rate": round((1.0 - math.exp(-self.hash_count * self.elements_count / self.bit_size)) ** self.hash_count, 6)
        }


# =============================================================================
# 4. CACHING: LRU CACHE WITH TTL
# =============================================================================

class LRUNode(Generic[T]):
    def __init__(self, key: str, value: T, expires_at: float):
        self.key = key
        self.value = value
        self.expires_at = expires_at
        self.prev: Optional['LRUNode[T]'] = None
        self.next: Optional['LRUNode[T]'] = None


class LRUCacheWithTTL(Generic[T]):
    """
    High-performance doubly-linked list LRU Cache with absolute Time-To-Live (TTL).
    Maintains O(1) reads, O(1) writes, automatic expiry eviction, and cache telemetry.
    """

    def __init__(self, capacity: int = 128, default_ttl_sec: float = 300.0):
        self.capacity = max(1, capacity)
        self.default_ttl = default_ttl_sec
        self.cache: Dict[str, LRUNode[T]] = {}
        self.head = LRUNode("", None, 0.0)  # Dummy head
        self.tail = LRUNode("", None, 0.0)  # Dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head

        # Telemetry
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def _remove(self, node: LRUNode[T]) -> None:
        prev_node = node.prev
        next_node = node.next
        if prev_node and next_node:
            prev_node.next = next_node
            next_node.prev = prev_node

    def _add_to_front(self, node: LRUNode[T]) -> None:
        node.next = self.head.next
        node.prev = self.head
        if self.head.next:
            self.head.next.prev = node
        self.head.next = node

    def get(self, key: str) -> Optional[T]:
        """Retrieve value by key if present and unexpired."""
        if key not in self.cache:
            self.misses += 1
            return None

        node = self.cache[key]
        now = time.time()
        if node.expires_at < now:
            # Expired
            self._remove(node)
            del self.cache[key]
            self.misses += 1
            return None

        # Move to front (most recently used)
        self._remove(node)
        self._add_to_front(node)
        self.hits += 1
        return node.value

    def put(self, key: str, value: T, ttl_sec: Optional[float] = None) -> None:
        """Insert or update value in cache with expiration."""
        ttl = ttl_sec if ttl_sec is not None else self.default_ttl
        expires_at = time.time() + ttl

        if key in self.cache:
            node = self.cache[key]
            node.value = value
            node.expires_at = expires_at
            self._remove(node)
            self._add_to_front(node)
            return

        if len(self.cache) >= self.capacity:
            # Evict least recently used (tail.prev)
            lru_node = self.tail.prev
            if lru_node and lru_node != self.head:
                self._remove(lru_node)
                del self.cache[lru_node.key]
                self.evictions += 1

        new_node = LRUNode(key, value, expires_at)
        self.cache[key] = new_node
        self._add_to_front(new_node)

    def delete(self, key: str) -> bool:
        """Explicitly remove a key."""
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """Flush cache."""
        self.cache.clear()
        self.head.next = self.tail
        self.tail.prev = self.head

    def get_stats(self) -> Dict[str, Any]:
        """Return cache health metrics."""
        total_requests = self.hits + self.misses
        hit_ratio = (self.hits / total_requests) if total_requests > 0 else 0.0
        return {
            "capacity": self.capacity,
            "current_size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_ratio_percent": round(hit_ratio * 100.0, 2)
        }


# =============================================================================
# 5. STRING ALGORITHMS & METRICS
# =============================================================================

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Standard Levenshtein edit distance (insertions, deletions, substitutions).
    Dynamic programming matrix optimized for O(min(m, n)) space.
    """
    if s1 == s2:
        return 0
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)

    if len(s1) > len(s2):
        s1, s2 = s2, s1

    prev = list(range(len(s1) + 1))
    curr = [0] * (len(s1) + 1)

    for j, c2 in enumerate(s2):
        curr[0] = j + 1
        for i, c1 in enumerate(s1):
            cost = 0 if c1 == c2 else 1
            curr[i + 1] = min(
                curr[i] + 1,       # insertion
                prev[i + 1] + 1,   # deletion
                prev[i] + cost     # substitution
            )
        prev, curr = curr, [0] * (len(s1) + 1)

    return prev[len(s1)]


def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    """
    Damerau-Levenshtein distance accounting for adjacent character transpositions.
    Ideal for spellchecking and fuzzy string reconciliation.
    """
    d: Dict[Tuple[int, int], int] = {}
    len1, len2 = len(s1), len(s2)

    for i in range(-1, len1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len2 + 1):
        d[(-1, j)] = j + 1

    for i in range(len1):
        for j in range(len2):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,      # deletion
                d[(i, j - 1)] + 1,      # insertion
                d[(i - 1, j - 1)] + cost  # substitution
            )
            if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + 1)  # transposition

    return d[(len1 - 1, len2 - 1)]


def jaro_winkler_similarity(s1: str, s2: str, p: float = 0.1) -> float:
    """
    Jaro-Winkler similarity coefficient in range [0.0, 1.0].
    Prioritizes matching prefixes, highly effective for short strings and names.
    """
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0

    match_distance = max(len1, len2) // 2 - 1

    s1_matches = [False] * len1
    s2_matches = [False] * len2

    matches = 0
    transpositions = 0

    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    jaro = (
        (matches / len1) +
        (matches / len2) +
        ((matches - transpositions / 2) / matches)
    ) / 3.0

    # Winkler prefix bonus (up to 4 characters)
    prefix = 0
    for i in range(min(4, len1, len2)):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break

    return round(jaro + prefix * p * (1.0 - jaro), 4)


def kmp_search(text: str, pattern: str) -> List[int]:
    """
    Knuth-Morris-Pratt (KMP) linear-time O(N + M) substring search algorithm.
    Returns list of starting indices where pattern occurs within text.
    """
    if not pattern or not text or len(pattern) > len(text):
        return []

    # Compute Longest Proper Prefix which is also Suffix (LPS) table
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

    # Search phase
    matches = []
    i = 0  # text index
    j = 0  # pattern index
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return matches


def longest_common_subsequence(s1: str, s2: str) -> str:
    """
    Compute Longest Common Subsequence (LCS) string using dynamic programming.
    Used for unified diff algorithms, versioning, and document delta comparison.
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m):
        for j in range(n):
            if s1[i] == s2[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i + 1][j], dp[i][j + 1])

    # Backtrack to reconstruct string
    result = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            result.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    result.reverse()
    return "".join(result)
