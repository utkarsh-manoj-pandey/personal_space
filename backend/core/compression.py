"""
Aether Compression and Archival Utility Engine
Pure Python implementations of fundamental lossless compression algorithms:
- Run-Length Encoding (RLE)
- Huffman Variable-Length Prefix Coding with Canonical Tree Reconstruction
- Lempel-Ziv-Welch (LZW) Dictionary-Based Compression
- Shannon Entropy and Compression Efficiency Evaluators
Designed for deterministic data serialization and offline enclave backups.
"""

from __future__ import annotations
import heapq
import math
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter


class ShannonEntropy:
    """
    I have written this part of code because calculating Shannon information entropy
    allows our local database backup engine to instantly detect whether an enclave payload
    is already compressed or encrypted before wasting CPU cycles on unnecessary compression!
    """

    @staticmethod
    def calculate(data: bytes) -> float:
        """Calculates Shannon entropy in bits per byte (0.0 to 8.0)."""
        if not data:
            return 0.0
        counts = Counter(data)
        total = len(data)
        entropy = 0.0
        for count in counts.values():
            prob = count / total
            entropy -= prob * math.log2(prob)
        return round(entropy, 4)

    @classmethod
    def theoretical_compression_limit(cls, data: bytes) -> float:
        """Returns theoretical maximum compression ratio based on entropy (0.0 to 1.0)."""
        if not data:
            return 0.0
        entropy = cls.calculate(data)
        return round(entropy / 8.0, 4)


class RunLengthEncoding:
    """
    Lossless Run-Length Encoding (RLE).
    Ideal for binary masks, sparse bit vectors, and raw monochromatic raster buffers.
    """

    @staticmethod
    def encode_bytes(data: bytes) -> bytes:
        if not data:
            return b""
        result = bytearray()
        i = 0
        n = len(data)
        while i < n:
            current_byte = data[i]
            run_length = 1
            while i + 1 < n and data[i + 1] == current_byte and run_length < 255:
                run_length += 1
                i += 1
            result.append(run_length)
            result.append(current_byte)
            i += 1
        return bytes(result)

    @staticmethod
    def decode_bytes(encoded: bytes) -> bytes:
        if not encoded:
            return b""
        if len(encoded) % 2 != 0:
            raise ValueError("Corrupted RLE payload: uneven byte length")
        result = bytearray()
        for i in range(0, len(encoded), 2):
            run_length = encoded[i]
            byte_val = encoded[i + 1]
            result.extend([byte_val] * run_length)
        return bytes(result)

    @classmethod
    def encode_text(cls, text: str) -> str:
        if not text:
            return ""
        encoded = []
        i = 0
        n = len(text)
        while i < n:
            char = text[i]
            count = 1
            while i + 1 < n and text[i + 1] == char:
                count += 1
                i += 1
            encoded.append(f"{count}{char}")
            i += 1
        return "".join(encoded)


class HuffmanNode:
    """Node in a Huffman coding tree."""

    def __init__(self, char: Optional[int], freq: int, left: Optional[HuffmanNode] = None, right: Optional[HuffmanNode] = None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other: HuffmanNode) -> bool:
        return self.freq < other.freq

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


class HuffmanCoder:
    """
    Canonical Huffman prefix coding engine.
    Encodes byte streams into variable-length bit codes.
    """

    @classmethod
    def build_tree(cls, data: bytes) -> Optional[HuffmanNode]:
        if not data:
            return None
        frequencies = Counter(data)
        heap: List[HuffmanNode] = [HuffmanNode(char=b, freq=f) for b, f in frequencies.items()]
        heapq.heapify(heap)

        if len(heap) == 1:
            single = heapq.heappop(heap)
            return HuffmanNode(char=None, freq=single.freq, left=single, right=None)

        while len(heap) > 1:
            node1 = heapq.heappop(heap)
            node2 = heapq.heappop(heap)
            merged = HuffmanNode(char=None, freq=node1.freq + node2.freq, left=node1, right=node2)
            heapq.heappush(heap, merged)

        return heap[0]

    @classmethod
    def _generate_codes(cls, node: Optional[HuffmanNode], current_code: str, codes: Dict[int, str]) -> None:
        if node is None:
            return
        if node.is_leaf and node.char is not None:
            codes[node.char] = current_code or "0"
            return
        if node.left:
            cls._generate_codes(node.left, current_code + "0", codes)
        if node.right:
            cls._generate_codes(node.right, current_code + "1", codes)

    @classmethod
    def encode(cls, data: bytes) -> Tuple[bytes, Dict[int, int]]:
        """
        Encodes data bytes. Returns (packed_bytes, frequency_table)
        where frequency_table is required for decompression.
        """
        if not data:
            return b"", {}

        freq_table = dict(Counter(data))
        root = cls.build_tree(data)
        codes: Dict[int, str] = {}
        cls._generate_codes(root, "", codes)

        bit_string = "".join(codes[b] for b in data)
        # Pad bit string to multiple of 8
        padding = (8 - len(bit_string) % 8) % 8
        bit_string += "0" * padding

        packed = bytearray([padding])
        for i in range(0, len(bit_string), 8):
            byte_chunk = bit_string[i : i + 8]
            packed.append(int(byte_chunk, 2))

        return bytes(packed), freq_table

    @classmethod
    def decode(cls, packed: bytes, freq_table: Dict[int, int]) -> bytes:
        """
        Reconstructs original payload from packed bytes and frequency table.
        """
        if not packed or not freq_table:
            return b""

        # Rebuild tree from frequency table
        heap: List[HuffmanNode] = [HuffmanNode(char=b, freq=f) for b, f in freq_table.items()]
        heapq.heapify(heap)

        if len(heap) == 1:
            single = heapq.heappop(heap)
            root = HuffmanNode(char=None, freq=single.freq, left=single, right=None)
        else:
            while len(heap) > 1:
                n1 = heapq.heappop(heap)
                n2 = heapq.heappop(heap)
                merged = HuffmanNode(char=None, freq=n1.freq + n2.freq, left=n1, right=n2)
                heapq.heappush(heap, merged)
            root = heap[0]

        padding = packed[0]
        bit_chars = []
        for b in packed[1:]:
            bit_chars.append(f"{b:08b}")
        full_bits = "".join(bit_chars)
        if padding > 0:
            full_bits = full_bits[:-padding]

        result = bytearray()
        current = root
        for bit in full_bits:
            current = current.left if bit == "0" else current.right
            if current and current.is_leaf and current.char is not None:
                result.append(current.char)
                current = root

        return bytes(result)


class LZWCompressor:
    """
    Lempel-Ziv-Welch (LZW) Dictionary-Based Compression Engine.
    High performance text and structured log compressor.
    """

    @classmethod
    def compress(cls, uncompressed: str) -> List[int]:
        """Compresses string text into a list of 16-bit dictionary integer codes."""
        if not uncompressed:
            return []

        # Build initial dictionary with all 256 single-byte ASCII characters
        dict_size = 256
        dictionary: Dict[str, int] = {chr(i): i for i in range(dict_size)}

        w = ""
        result = []
        for c in uncompressed:
            wc = w + c
            if wc in dictionary:
                w = wc
            else:
                result.append(dictionary[w])
                dictionary[wc] = dict_size
                dict_size += 1
                w = c

        if w:
            result.append(dictionary[w])
        return result

    @classmethod
    def decompress(cls, compressed: List[int]) -> str:
        """Decompresses a list of integer codes back into the original string."""
        if not compressed:
            return ""

        dict_size = 256
        dictionary: Dict[int, str] = {i: chr(i) for i in range(dict_size)}

        w = chr(compressed[0])
        result = [w]

        for k in compressed[1:]:
            if k in dictionary:
                entry = dictionary[k]
            elif k == dict_size:
                entry = w + w[0]
            else:
                raise ValueError(f"Bad compressed LZW code: {k}")

            result.append(entry)
            dictionary[dict_size] = w + entry[0]
            dict_size += 1
            w = entry

        return "".join(result)


class CompressionBenchmark:
    """Benchmarks and evaluates compression performance across algorithms."""

    @classmethod
    def evaluate(cls, raw_data: bytes) -> Dict[str, Any]:
        raw_len = len(raw_data)
        if raw_len == 0:
            return {"raw_bytes": 0}

        entropy = ShannonEntropy.calculate(raw_data)

        # RLE
        rle_bytes = RunLengthEncoding.encode_bytes(raw_data)
        rle_ratio = round(len(rle_bytes) / raw_len, 3)

        # Huffman
        huff_bytes, freq_table = HuffmanCoder.encode(raw_data)
        huff_ratio = round(len(huff_bytes) / raw_len, 3)

        # LZW (on text if valid utf-8)
        lzw_codes_count = 0
        lzw_ratio = 1.0
        try:
            text = raw_data.decode("utf-8")
            codes = LZWCompressor.compress(text)
            lzw_codes_count = len(codes)
            # 2 bytes per code
            lzw_size = lzw_codes_count * 2
            lzw_ratio = round(lzw_size / raw_len, 3)
        except UnicodeDecodeError:
            pass

        return {
            "raw_bytes": raw_len,
            "shannon_entropy_bits": entropy,
            "theoretical_limit": ShannonEntropy.theoretical_compression_limit(raw_data),
            "rle": {
                "compressed_bytes": len(rle_bytes),
                "ratio": rle_ratio,
                "savings_pct": round(max(0.0, (1.0 - rle_ratio) * 100), 1)
            },
            "huffman": {
                "compressed_bytes": len(huff_bytes),
                "ratio": huff_ratio,
                "savings_pct": round(max(0.0, (1.0 - huff_ratio) * 100), 1)
            },
            "lzw": {
                "codes": lzw_codes_count,
                "ratio": lzw_ratio,
                "savings_pct": round(max(0.0, (1.0 - lzw_ratio) * 100), 1)
            }
        }
