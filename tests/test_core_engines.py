"""
Automated Test Suite for Aether Core Engines
Verifies graph theory, pathfinding, spatial indexing, probabilistic structures,
LRU caching, string algorithms, audio DSP, and GIS projections.
"""

import math
import pytest
from backend.core.algorithms import (
    Graph,
    dijkstra_shortest_path,
    a_star_search,
    topological_sort,
    has_cycle,
    KDTree2D,
    BloomFilter,
    LRUCacheWithTTL,
    levenshtein_distance,
    damerau_levenshtein_distance,
    jaro_winkler_similarity,
    kmp_search,
    longest_common_subsequence
)
from backend.core.audio_dsp import (
    AudioMetrics,
    DiscreteFourierTransform,
    BiquadFilter,
    WavetableSynthesizer
)
from backend.core.gis_engine import (
    SlippyMapTileMath,
    UTMProjectionEngine,
    SpatialClusterEngine
)


# =============================================================================
# 1. GRAPH THEORY & PATHFINDING TESTS
# =============================================================================

def test_graph_construction_and_traversal():
    g = Graph(directed=True)
    g.add_edge("A", "B", weight=2.0)
    g.add_edge("B", "C", weight=3.0)
    g.add_edge("A", "C", weight=6.0)

    assert len(g.get_nodes()) == 3
    assert g.get_neighbors("A") == {"B": 2.0, "C": 6.0}
    assert g.has_cycle() is False


def test_dijkstra_shortest_path():
    g = Graph(directed=False)
    g.add_edge("A", "B", 4.0)
    g.add_edge("A", "C", 2.0)
    g.add_edge("C", "B", 1.0)
    g.add_edge("B", "D", 5.0)
    g.add_edge("C", "D", 8.0)

    res = dijkstra_shortest_path(g, "A", "D")
    assert res["found"] is True
    assert res["path"] == ["A", "C", "B", "D"]
    assert res["distance"] == 8.0


def test_a_star_search_heuristic():
    g = Graph(directed=False)
    # Grid coordinates
    coords = {"A": (0, 0), "B": (1, 0), "C": (0, 1), "D": (2, 2)}
    for n, pt in coords.items():
        g.add_node(n, x=pt[0], y=pt[1])

    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "D", 2.5)
    g.add_edge("A", "C", 1.0)
    g.add_edge("C", "D", 3.0)

    def euclidean_heuristic(u, target):
        pt1 = coords[u]
        pt2 = coords[target]
        return math.hypot(pt1[0] - pt2[0], pt1[1] - pt2[1])

    res = a_star_search(g, "A", "D", heuristic_fn=euclidean_heuristic)
    assert res["found"] is True
    assert res["path"] == ["A", "B", "D"]
    assert res["distance"] == 3.5


def test_topological_sort_and_cycle_detection():
    dag = Graph(directed=True)
    dag.add_edge("Step1", "Step2")
    dag.add_edge("Step2", "Step3")
    dag.add_edge("Step1", "Step3")

    order = topological_sort(dag)
    assert order.index("Step1") < order.index("Step2") < order.index("Step3")

    # Cyclic graph
    cyclic = Graph(directed=True)
    cyclic.add_edge("A", "B")
    cyclic.add_edge("B", "C")
    cyclic.add_edge("C", "A")
    assert has_cycle(cyclic) is True
    with pytest.raises(ValueError):
        topological_sort(cyclic)


# =============================================================================
# 2. SPATIAL INDEXING: KD-TREE 2D
# =============================================================================

def test_kdtree_2d_nearest_neighbor():
    points = [
        ((40.7128, -74.0060), "New York"),
        ((51.5074, -0.1278), "London"),
        ((35.6762, 139.6503), "Tokyo"),
        ((48.8566, 2.3522), "Paris")
    ]
    tree = KDTree2D(points)

    # Query point near London
    res = tree.nearest_neighbor((52.0, 0.0))
    assert res is not None
    assert res["data"] == "London"

    # K-nearest query
    knn = tree.k_nearest_neighbors((50.0, 1.0), k=2)
    assert len(knn) == 2
    knn_cities = [n["data"] for n in knn]
    assert "London" in knn_cities
    assert "Paris" in knn_cities


# =============================================================================
# 3. PROBABILISTIC BLOOM FILTER & LRU CACHE
# =============================================================================

def test_bloom_filter_membership():
    bf = BloomFilter(expected_elements=1000, false_positive_rate=0.01)
    test_keys = [f"asset_{i}" for i in range(200)]
    for k in test_keys:
        bf.add(k)

    # No false negatives permitted
    for k in test_keys:
        assert bf.contains(k) is True

    # Unknown key should not be present (probabilistic)
    assert bf.contains("definitely_not_present_key_9999") is False
    stats = bf.get_stats()
    assert stats["elements_added"] == 200
    assert stats["fill_ratio"] > 0.0


def test_lru_cache_with_ttl():
    cache = LRUCacheWithTTL(capacity=3, default_ttl_sec=10.0)
    cache.put("k1", "v1")
    cache.put("k2", "v2")
    cache.put("k3", "v3")

    assert cache.get("k1") == "v1"
    assert cache.get("k2") == "v2"

    # Insert 4th element: k3 was least recently used
    cache.put("k4", "v4")
    assert cache.get("k3") is None
    assert cache.get("k4") == "v4"

    stats = cache.get_stats()
    assert stats["hits"] >= 3
    assert stats["evictions"] == 1


# =============================================================================
# 4. STRING METRICS & ALGORITHMS
# =============================================================================

def test_string_algorithms():
    # Levenshtein
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("same", "same") == 0

    # Damerau-Levenshtein (transposition cost 1)
    assert damerau_levenshtein_distance("ca", "ac") == 1

    # Jaro-Winkler
    sim = jaro_winkler_similarity("DIXON", "DICKSONX")
    assert 0.7 < sim < 1.0
    assert jaro_winkler_similarity("Identical", "Identical") == 1.0

    # KMP Search
    matches = kmp_search("ABC ABCDAB ABCDABCDABDE", "ABCDABD")
    assert matches == [15]

    # Longest Common Subsequence
    lcs = longest_common_subsequence("AGGTAB", "GXTXAYB")
    assert lcs == "GTAB"


# =============================================================================
# 5. AUDIO DSP & SPECTRAL ANALYSIS
# =============================================================================

def test_audio_dsp_and_biquad():
    # Waveform synthesis
    samples = WavetableSynthesizer.generate_waveform("sine", freq=440.0, duration_sec=0.01)
    assert len(samples) > 100
    rms = AudioMetrics.calculate_rms(samples)
    assert 0.5 < rms < 0.8
    dbfs = AudioMetrics.calculate_dbfs(samples)
    assert -10.0 < dbfs < 0.0

    # Biquad Filter
    lp_filter = BiquadFilter(filter_type="lowpass", cutoff_hz=1000.0, sample_rate=44100)
    filtered = lp_filter.process_block(samples)
    assert len(filtered) == len(samples)

    # DFT magnitudes
    dft_sample = samples[:64]
    mags = DiscreteFourierTransform.dft_magnitudes(dft_sample)
    assert len(mags) == 32
    assert max(mags) > 0.0


# =============================================================================
# 6. GIS & SPATIAL ENGINE
# =============================================================================

def test_gis_tile_math_and_utm():
    # Slippy map tile
    x, y = SlippyMapTileMath.deg2tile(40.7128, -74.0060, 10)
    lat_back, lon_back = SlippyMapTileMath.tile2deg(x, y, 10)
    assert abs(lat_back - 40.7128) < 1.0
    assert abs(lon_back - -74.0060) < 1.0

    # UTM projection
    utm = UTMProjectionEngine.latlon_to_utm(40.7128, -74.0060)
    assert utm["zone_number"] == 18
    assert utm["zone_letter"] == "T"
    assert utm["is_northern_hemisphere"] is True
    assert utm["easting"] > 0
    assert utm["northing"] > 0

    # Spatial clustering
    pts = [
        {"latitude": 40.7128, "longitude": -74.0060, "name": "NYC 1"},
        {"latitude": 40.7200, "longitude": -74.0100, "name": "NYC 2"},
        {"latitude": 51.5074, "longitude": -0.1278, "name": "LON 1"}
    ]
    clusters = SpatialClusterEngine.cluster_points(pts, distance_threshold_km=50.0)
    assert len(clusters) == 2  # NYC points clustered together, London separate
