import sys
import pathlib
from collections import defaultdict
from typing import List, Dict, Tuple, Iterator


def calculate_similarity(lines1: List[str], lines2: List[str]) -> float:
    if not lines1 or not lines2:
        return 0.0
    matches = sum(1 for a, b in zip(lines1, lines2) if a == b)
    return matches / max(len(lines1), len(lines2))


def ranges_overlap(start1: int, end1: int, start2: int, end2: int) -> bool:
    """Check if two ranges overlap by more than 50%"""
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)
    
    if overlap_start >= overlap_end:
        return False
    
    overlap_size = overlap_end - overlap_start
    range1_size = end1 - start1
    range2_size = end2 - start2
    
    overlap_pct1 = overlap_size / range1_size if range1_size > 0 else 0
    overlap_pct2 = overlap_size / range2_size if range2_size > 0 else 0
    
    return overlap_pct1 > 0.5 or overlap_pct2 > 0.5


def merge_overlapping_groups(
    groups: List[Tuple[str, int, List[Tuple[str, int, float]]]],
    block_size: int,
    file_lines: Dict[str, List[str]]
) -> List[Tuple[str, int, int, List[Tuple[str, int, float]]]]:
    """Merge groups that have overlapping ranges by more than 50%,
    recompute similarity after merging"""
    if not groups:
        return []
    
    groups_by_file: Dict[str, List[Tuple[int, List[Tuple[str, int, float]]]]]
    groups_by_file = defaultdict(list)
    for fname, lnum, similar_blocks in groups:
        groups_by_file[fname].append((lnum, similar_blocks))
    
    merged_groups = []
    
    for fname, file_groups in groups_by_file.items():
        file_groups.sort(key=lambda x: x[0])
        
        current_start = file_groups[0][0]
        current_end = current_start + block_size - 1
        current_similar_dict: Dict[str, List[Tuple[int, int]]] = {}
        
        for f, l, s in file_groups[0][1]:
            end = l + block_size - 1
            key = f
            if key not in current_similar_dict:
                current_similar_dict[key] = []
            current_similar_dict[key].append((l, end))
        
        for i in range(1, len(file_groups)):
            lnum, similar_blocks = file_groups[i]
            end_line = lnum + block_size - 1
            
            if ranges_overlap(current_start, current_end, lnum, end_line):
                current_end = max(current_end, end_line)
                
                for f, l, s in similar_blocks:
                    end = l + block_size - 1
                    key = f
                    if key not in current_similar_dict:
                        current_similar_dict[key] = []
                    current_similar_dict[key].append((l, end))
            else:
                actual_size = current_end - current_start + 1
                merged_similar = compute_merged_similarities(
                    fname, current_start, current_end,
                    current_similar_dict, file_lines
                )
                merged_groups.append(
                    (fname, current_start, actual_size, merged_similar)
                )
                
                current_start = lnum
                current_end = end_line
                current_similar_dict = {}
                for f, l, s in similar_blocks:
                    end = l + block_size - 1
                    key = f
                    if key not in current_similar_dict:
                        current_similar_dict[key] = []
                    current_similar_dict[key].append((l, end))
        
        actual_size = current_end - current_start + 1
        merged_similar = compute_merged_similarities(
            fname, current_start, current_end,
            current_similar_dict, file_lines
        )
        entry = (fname, current_start, actual_size, merged_similar)
        merged_groups.append(entry)
    
    return merged_groups


def compute_merged_similarities(
    fname: str,
    start: int,
    end: int,
    similar_dict: Dict[str, List[Tuple[int, int]]],
    file_lines: Dict[str, List[str]]
) -> List[Tuple[str, int, float]]:
    """Compute similarity for merged ranges"""
    merged_similar: List[Tuple[str, int, float]] = []
    
    if fname not in file_lines:
        return merged_similar
    
    primary_lines = file_lines[fname][start - 1:end]
    
    for other_file, ranges in similar_dict.items():
        if other_file not in file_lines:
            continue
        
        ranges.sort()
        merged_ranges: List[Tuple[int, int]] = []
        
        for range_start, range_end in ranges:
            if (
                merged_ranges
                and ranges_overlap(
                    merged_ranges[-1][0], merged_ranges[-1][1],
                    range_start, range_end
                )
            ):
                prev_start, prev_end = merged_ranges[-1]
                merged_ranges[-1] = (
                    min(prev_start, range_start),
                    max(prev_end, range_end)
                )
            else:
                merged_ranges.append((range_start, range_end))
        
        for merged_start, merged_end in merged_ranges:
            other_lines = file_lines[other_file][merged_start - 1:merged_end]
            similarity = calculate_similarity(primary_lines, other_lines)
            merged_similar.append((other_file, merged_start, similarity))
    
    return merged_similar


def find_duplicates(
    files: List[str],
    block_size: int = 10,
    min_occur: int = 3
) -> Iterator[Tuple[str, int, int, List[Tuple[str, int, float]]]]:
    """
    Find duplicate blocks of code across files.

    Args:
        files: list of file paths
        block_size: number of consecutive lines in a block
        min_occur: minimum number of occurrences to report

    Yields:
        (primary_filename, primary_line, actual_block_size,
         [(other_file, other_line, similarity), ...])
    """
    file_lines: Dict[str, List[str]] = {}
    for fname in files:
        try:
            with open(fname, encoding="utf-8") as f:
                file_lines[fname] = f.readlines()
        except OSError as e:
            print(f"Could not read {fname}: {e}", file=sys.stderr)
            continue

    all_blocks: List[Tuple[str, int, List[str]]] = []
    for fname in file_lines:
        lines = file_lines[fname]
        for i in range(len(lines) - block_size + 1):
            block_lines = lines[i:i + block_size]
            all_blocks.append((fname, i + 1, block_lines))

    reported: set[Tuple[str, int]] = set()
    groups: List[Tuple[str, int, List[Tuple[str, int, float]]]] = []

    for i, (fname1, lnum1, block1) in enumerate(all_blocks):
        key1 = (fname1, lnum1)
        
        if key1 in reported:
            continue
        
        similar_blocks: List[Tuple[str, int, float]] = []
        
        for j, (fname2, lnum2, block2) in enumerate(all_blocks):
            if i >= j:
                continue
            
            key2 = (fname2, lnum2)
            if key2 in reported:
                continue
            
            similarity = calculate_similarity(block1, block2)
            if similarity > 0.8:
                similar_blocks.append((fname2, lnum2, similarity))
                reported.add(key2)
        
        if len(similar_blocks) + 1 >= min_occur:
            reported.add(key1)
            groups.append((fname1, lnum1, similar_blocks))
    
    merged = merge_overlapping_groups(groups, block_size, file_lines)
    
    for fname, lnum, actual_size, similar_blocks in merged:
        yield fname, lnum, actual_size, similar_blocks


def validate_inputs(files: List[pathlib.Path]) -> bool:
    """Validate that files list is not empty and all files exist."""
    if not files:
        print("Usage: inspectr duplicates [--block-size N] [--min-occur N] "
              "file1.py [file2.py ...]")
        return False

    for f in files:
        if not f.exists():
            print(f"Error: File does not exist: {f}")
            return False
        if not f.is_file():
            print(f"Error: Not a file: {f}")
            return False
    return True


def main(
    files: List[pathlib.Path],
    block_size: int = 10,
    min_occur: int = 3
) -> None:
    if not validate_inputs(files):
        return

    file_paths = [str(f) for f in files]
    duplicates = find_duplicates(
        file_paths, block_size=block_size, min_occur=min_occur
    )
    for fname, lnum, block_sz, similar_blocks in duplicates:
        end_line = lnum + block_sz - 1
        output_parts = [f"{fname}: lines {lnum}-{end_line} occur in"]
        
        for other_file, other_line, similarity in similar_blocks:
            other_end = other_line + block_sz - 1
            similarity_pct = int(similarity * 100)
            output_parts.append(
                f" {other_file} at lines {other_line}-{other_end} "
                f"({similarity_pct}% similarity) and"
            )
        
        output = "".join(output_parts).rstrip(" and")
        print(output)
