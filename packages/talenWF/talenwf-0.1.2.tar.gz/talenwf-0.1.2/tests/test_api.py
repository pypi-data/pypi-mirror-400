import pytest
import tempfile
import os
import pandas as pd
from pathlib import Path
from talenWF import FindTALTask


class TestFindTALTask:
    """Test the FindTALTask class."""

    @pytest.fixture
    def sample_fasta_file(self):
        """Create a temporary FASTA file for testing with different sequences."""
        seq_name = "test_seq"
        sequence = "C" + "CT" + "C" * 26 + "T" + "C" * 26 + "CA" + "C"
        # sequence = "C" + "TC" + "C"*26 + "T" + "C"*26 + "CA"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".fasta", delete=False) as f:
            f.write(f">{seq_name}\n")
            f.write(sequence + "\n")
            temp_file = f.name
        yield temp_file
        os.unlink(temp_file)

    @pytest.fixture
    def output_file(self):
        """Create a temporary output file path."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_file = f.name
        yield temp_file
        if os.path.exists(temp_file):
            os.unlink(temp_file)

    def test_find_tal_task_basic(self, sample_fasta_file, output_file):
        """Test basic functionality of FindTALTask with different sequences."""
        # Create FindTALTask instance
        for min_val in [14, 18]:
            task = FindTALTask(
                fasta=sample_fasta_file,
                min_spacer=18,
                max_spacer=18,
                array_min=18,
                array_max=18,
                outpath=output_file,
                filter_base=30,
            )

            # Run the task
            task.run()

            # Check that output file was created
            assert os.path.exists(output_file)

            # Check that output file can be read properly (TSV with 2 rows skipped)
            out = pd.read_csv(output_file, delimiter="\t")
            assert (
                out.columns[0] == "Sequence Name"
            ), "First column should be Sequence Name"

            print(out[["TAL1 start", "TAL2 start"]].value_counts())

            for i, row in out.iterrows():
                print(dict(row))

            assert len(out) == 1, "Output should have only one row"
            assert (out["TAL1 start"] == 3).all(), "TAL1 start should be 3"
            assert (out["TAL2 start"] == 56).all(), "TAL2 start should be 55"

        # print(out.columns)

        # assert len(out) == 5, "Expected 5 rows"
        # for spac_len in range(14,19):
        #     assert out["Spacer length"].isin([spac_len]).any(), f"Spacer length {spac_len} not found"
        # for i,row in out.iterrows():
        #     print(row["Plus strand sequence"])
        #     assert row["Spacer length"] == len(row["Plus strand sequence"].split()[2])

    def test_find_tal_task_u_d_too_far(self, output_file):
        """Test that the task skips TAL pairs if the upstream base is out of bounds."""
        sequence = "C" + "CT" + "C" * 26 + "T" + "C" * 26 + "CA" + "C"
        task = FindTALTask(
            sequence=sequence,
            min_spacer=14,
            max_spacer=17,
            array_min=14,
            array_max=18,
            outpath=output_file,
            filter_base=20,
        )
        task.run()
        assert os.path.exists(output_file)
        out = pd.read_csv(output_file, delimiter="\t")
        assert len(out) == 0, "Expected 0 rows"

    def test_find_tal_task_max_dist_odd(self, output_file):
        """Test that the task skips TAL pairs if the upstream base is out of bounds."""
        sequence = "C" + "CT" + "C" * 26 + "T" + "C" * 26 + "AC" + "C"
        task = FindTALTask(
            sequence=sequence,
            min_spacer=14,
            max_spacer=17,
            array_min=14,
            array_max=18,
            outpath=output_file,
            filter_base=30,
        )
        task.run()
        assert os.path.exists(output_file)
        out = pd.read_csv(output_file, delimiter="\t")
        assert len(out) > 0, "Expected non-0 rows"
        for i, row in out.iterrows():
            print(dict(row))

    def test_find_tal_task_upstream_out_of_bounds(self, output_file):
        """Test that the task skips TAL pairs if the upstream base is out of bounds."""
        sequence = "T" * 14 + "C" * 14 + "A" * 15
        task = FindTALTask(
            sequence=sequence,
            min_spacer=14,
            max_spacer=18,
            array_min=14,
            array_max=18,
            outpath=output_file,
            filter_base=22,
        )
        task.run()
        assert os.path.exists(output_file)
        out = pd.read_csv(output_file, delimiter="\t")
        assert len(out) == 0, "Expected 0 rows"

    def test_find_tal_task_upstream_at_bounds(self, output_file):
        """Test that the task skips TAL pairs if the upstream base is out of bounds."""
        sequence = "T" * 15 + "C" * 14 + "A" * 15
        task = FindTALTask(
            sequence=sequence,
            min_spacer=14,
            max_spacer=18,
            array_min=14,
            array_max=18,
            outpath=output_file,
            filter_base=23,
        )
        task.run()
        assert os.path.exists(output_file)
        out = pd.read_csv(output_file, delimiter="\t")
        for i, row in out.iterrows():
            print(dict(row))
        assert len(out) == 1, "Expected exactly 1 row"

    def test_find_tal_task_upstream_out_of_bounds_nofilter(self, output_file):
        """Test that the task skips TAL pairs if the upstream base is out of bounds."""
        sequence = "T" * 15 + "C" * 14 + "A" * 14
        task = FindTALTask(
            sequence=sequence,
            min_spacer=14,
            max_spacer=18,
            array_min=14,
            array_max=18,
            outpath=output_file,
        )
        task.run()
        assert os.path.exists(output_file)
        out = pd.read_csv(output_file, delimiter="\t")
        assert len(out) == 0, "Expected 0 rows"

    def test_find_tal_task_upstream_at_bounds_nofilter(self, output_file):
        """Test that the task skips TAL pairs if the upstream base is out of bounds."""
        sequence = "T" * 15 + "C" * 14 + "A" * 15
        task = FindTALTask(
            sequence=sequence,
            min_spacer=14,
            max_spacer=18,
            array_min=14,
            array_max=18,
            outpath=output_file,
        )
        task.run()
        assert os.path.exists(output_file)
        out = pd.read_csv(output_file, delimiter="\t")
        print(out)
        assert len(out) == 1, "Expected 1 row"

    def test_find_tal_task_upstream_two_in_bounds_nofilter(self, output_file):
        """Test that the task skips TAL pairs if the upstream base is out of bounds."""
        sequence = "T" * 16 + "C" * 14 + "A" * 15
        task = FindTALTask(
            sequence=sequence,
            min_spacer=14,
            max_spacer=18,
            array_min=14,
            array_max=18,
            outpath=output_file,
        )
        task.run()
        assert os.path.exists(output_file)
        out = pd.read_csv(output_file, delimiter="\t")
        for _, row in out.iterrows():
            print(dict(row))
        assert len(out) == 2, "Expected 1 row"

    def test_find_tal_task_upstream_in_bounds_far_nofilter(self, output_file):
        """Test that the task skips TAL pairs if the upstream base is out of bounds."""
        sequence = "TT" + "C" * 54 + "A"
        task = FindTALTask(
            sequence=sequence,
            min_spacer=14,
            max_spacer=18,
            array_min=14,
            array_max=18,
            outpath=output_file,
        )
        task.run()
        assert os.path.exists(output_file)
        out = pd.read_csv(output_file, delimiter="\t")
        for _, row in out.iterrows():
            print(dict(row))
        assert len(out) == 1, "Expected 1 row"

    def test_find_tal_task_upstream_two_in_bounds_far_nofilter(self, output_file):
        """Test that the task skips TAL pairs if the upstream base is out of bounds."""
        sequence = "TT" + "C" * 53 + "A"
        task = FindTALTask(
            sequence=sequence,
            min_spacer=14,
            max_spacer=18,
            array_min=14,
            array_max=18,
            outpath=output_file,
        )
        task.run()
        assert os.path.exists(output_file)
        out = pd.read_csv(output_file, delimiter="\t")
        for _, row in out.iterrows():
            if row["Spacer range"] == "20-37":
                print(dict(row))
                # [['TAL1 start','TAL1 length','Spacer length','TAL2 length','Spacer range']]
        assert sum(out["TAL1 start"] == 1) == 1, "Expected 1 row"
        assert (
            sum((out["TAL1 start"] == 2) & (out["TAL1 length"] == 17)) > 0
        ), "Expected result(s) with TAL1 length 17"
        assert (
            sum((out["TAL1 start"] == 2) & (out["TAL2 length"] == 17)) > 0
        ), "Expected result(s) with TAL2 length 17"
        assert (
            sum((out["TAL1 start"] == 2) & (out["Spacer length"] == 17)) > 0
        ), "Expected result(s) with Spacer length 17"
        assert (
            sum(
                (out["TAL1 length"] > 18)
                | (out["TAL2 length"] > 18)
                | (out["Spacer length"] > 18)
            )
            == 0
        ), "Invalid length(s) found"


# TODO: add tests with filter base outside of the sequence
# TODO: add tests with filter base less than min_dist/2
# TODO: add tests with filter base greater than len(seq) - max_dist/2
