from pathlib import Path
from typing import List, Optional
from collections import deque
import pandas as pd
import sys
import logging
from .utils.rvd import get_RVD_seq
from .utils.sequence import get_sequence

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("talenWF")

COMPLEMENT = {"T": "A", "A": "T", "C": "G", "G": "C"}


def findAll(seq, sub, start=0, end=None):
    if end is None:
        end = len(seq)
    return [i for i in range(start, end) if seq[i : i + len(sub)] == sub]


class FindTALTask:
    """TALEN window finder class."""

    def __init__(
        self,
        fasta: Optional[str] = None,
        sequence: Optional[str] = None,
        min_spacer: int = 14,
        max_spacer: int = 18,
        array_min: int = 14,
        array_max: int = 18,
        outpath: str = "talenWF_out",
        filter_base: Optional[int] = None,
        upstream_bases: List[str] = ["T"],
        gspec: bool = False,
    ):
        """
        Initialize the TAL window finder.

        Args:
            fasta: The FASTA file to process.
            sequence: The sequence to process.
            min_spacer: The minimum spacer length.
            max_spacer: The maximum spacer length.
            array_min: The minimum array length.
            array_max: The maximum array length.
            filter_base: The base position to filter. If None, no filtering is done. (1-indexed)
            upstream_bases: The upstream bases to consider. (Default: ['T'])
            outpath: The path to the output file.
            gspec: Whether to use G-specific RVDs. (Default: False)
        """
        self.fasta = fasta
        self.sequence = sequence
        self.min_spacer = min_spacer
        self.max_spacer = max_spacer
        self.array_min = array_min
        self.array_max = array_max
        self.outpath = outpath
        self.filter_base = (
            filter_base - 1 if filter_base is not None else None
        )  # make it 0-based
        self.upstream_bases = upstream_bases
        self.gspec = gspec
        # Calculate distances
        self.max_dist = (
            2 * array_max + max_spacer
        )  # max dist between TAL1 and TAL2 start/end
        self.min_dist = (
            2 * array_min + min_spacer
        )  # min dist between TAL1 and TAL2 start/end

    def _find_tal_pairs_for_filterpos(self):
        for upstream_base in self.upstream_bases:
            downstream_base = COMPLEMENT[upstream_base]
            up_pos_array = findAll(
                self.sequence,
                upstream_base,
                max(0, self.filter_base - (self.max_dist // 2) - 1),
                self.filter_base - (self.min_dist // 2) + 1,
            )
            down_pos_array = findAll(
                self.sequence,
                downstream_base,
                self.filter_base + ((self.min_dist) // 2),
                min(
                    len(self.sequence),
                    self.filter_base + ((self.max_dist + 1) // 2) + 2,
                ),
            )
            for up_pos in up_pos_array:
                for down_pos in down_pos_array:
                    assert self.sequence[up_pos] == upstream_base
                    assert self.sequence[down_pos] == downstream_base
                    window_len = (down_pos - 1) - (up_pos + 1) + 1
                    if window_len < self.min_dist or window_len > self.max_dist:
                        continue
                    for spacer_length in range(self.min_spacer, self.max_spacer + 1):
                        # if TAL array lengths are within range
                        sum_tal_lengths = window_len - spacer_length
                        if (
                            sum_tal_lengths >= 2 * self.array_min
                            and sum_tal_lengths <= 2 * self.array_max
                        ):
                            yield self._create_tal_pair(
                                self.filter_base, up_pos, down_pos, spacer_length
                            )

    def _find_tal_pairs_for_seq(self):
        """Generator function that yields TAL pairs for a sequence."""

        if self.filter_base is not None:
            yield from self._find_tal_pairs_for_filterpos()

        # No filter base -> find all valid TAL pairs within the sequence
        # Storing upstream base occurences in a queue to visit the upmost first
        else:
            for upstream_base in self.upstream_bases:
                upstream_q = deque()
                for j in range(len(self.sequence)):
                    ch = self.sequence[j]
                    if ch == upstream_base:
                        upstream_q.append(j)
                    elif ch == COMPLEMENT[upstream_base]:
                        # remove any upstream candidates that are too far for j (i < j-max_dist)
                        up_pos_min = j - self.max_dist - 1
                        up_pos_max = j - self.min_dist - 1
                        while upstream_q:
                            up_pos = upstream_q[0]
                            if up_pos > up_pos_max:
                                break
                            upstream_q.popleft()
                            if up_pos < up_pos_min:
                                continue
                            # up_pos is in range up_pos_min to up_pos_max
                            for spacer_length in range(
                                self.min_spacer, self.max_spacer + 1
                            ):
                                sum_tal_lengths = j - up_pos - 1 - spacer_length
                                for tal1_length in range(
                                    self.array_min, self.array_max + 1
                                ):
                                    tal2_length = sum_tal_lengths - tal1_length
                                    if (
                                        tal2_length >= self.array_min
                                        and tal2_length <= self.array_max
                                    ):
                                        spacer_start = up_pos + 1 + tal1_length
                                        cut = spacer_start + spacer_length // 2
                                        yield self._create_tal_pair(
                                            cut, up_pos, j, spacer_length, False
                                        )

    def _create_tal_pair(
        self,
        cut: int,
        up_pos: int,
        down_pos: int,
        spacer_length: int,
        use_middle2: bool = True,
    ):
        """Create a TAL pair attributes dictionary from positions for the output table."""
        rows = []
        tal1_start = up_pos + 1
        if (spacer_length % 2 == 1) or not use_middle2:
            tal1_ends = [cut - spacer_length // 2 - 1]
        else:
            # if even-sized spacer cut site in the middle 2 positions
            tal1_ends = [cut - spacer_length // 2 - 1, cut - spacer_length // 2]
        for tal1_end in tal1_ends:
            tal2_start = tal1_end + spacer_length + 1
            tal2_end = down_pos - 1

            tal1 = self.sequence[tal1_start : tal1_end + 1]
            tal2 = self.sequence[tal2_start : tal2_end + 1]
            spacer = self.sequence[tal1_end + 1 : tal2_start]
            if (
                len(tal1) > self.array_max
                or len(tal2) > self.array_max
                or len(tal1) < self.array_min
                or len(tal2) < self.array_min
            ):
                continue
            # Plus strand sequence format example: T AGAGCT(TAL1) cgcagcgt(spacer) ACGTCGAC(TAL2) A
            plus_seq = f"{self.sequence[up_pos]} {tal1} {spacer.lower()} {tal2} {self.sequence[down_pos]}"
            row = {
                "Sequence Name": self.sequence_id,
                "Cut Site": cut,
                "TAL1 start": tal1_start,
                "TAL2 start": tal2_end,
                "TAL1 length": len(tal1),
                "TAL2 length": len(tal2),
                "Spacer length": spacer_length,
                "Spacer range": f"{tal1_end+1}-{tal2_start-1}",
                "TAL1 RVDs": get_RVD_seq(tal1, self.gspec),
                "TAL2 RVDs": get_RVD_seq(tal2, self.gspec),
                "Plus strand sequence": plus_seq,
                "Unique RE sites in spacer": "",  # TODO: add function for RE sites in spacer
                "% RVDs HD or NN/NH": "",  # TODO: add function for % RVDs HD or NN/NH
            }
            rows.append(row)
        return rows

    def run(self) -> Optional[pd.DataFrame]:
        """
        Runs the TAL window finder.

        Returns:
            A DataFrame containing the TAL windows.
        """
        self.sequence, self.sequence_id = get_sequence(self.fasta, self.sequence)
        tal_window_rows: List[dict] = []
        for tal_pairs in self._find_tal_pairs_for_seq():
            if tal_pairs is not None:
                tal_window_rows.extend(tal_pairs)

        df = pd.DataFrame(tal_window_rows)
        if self.outpath is not None:
            outpath = Path(self.outpath)
            outpath.parent.mkdir(parents=True, exist_ok=True)
            if df.empty:
                # Write only header
                pd.DataFrame(
                    columns=[
                        "Sequence Name",
                        "Cut Site",
                        "TAL1 start",
                        "TAL2 start",
                        "TAL1 length",
                        "TAL2 length",
                        "Spacer length",
                        "Spacer range",
                        "TAL1 RVDs",
                        "TAL2 RVDs",
                        "Plus strand sequence",
                        "Unique RE sites in spacer",
                        "% RVDs HD or NN/NH",
                    ]
                ).to_csv(outpath, sep="\t", index=False)
            else:
                df.to_csv(outpath, sep="\t", index=False)

        return df
