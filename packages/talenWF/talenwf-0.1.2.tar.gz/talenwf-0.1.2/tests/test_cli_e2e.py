import os
import sys
import tempfile

from talenWF.cli import main

import pandas as pd


def test_end_to_end_happy_path(monkeypatch):
    """Invoke CLI main() with all options and verify output file is created and non-empty."""
    # Create a temporary FASTA file with a simple valid sequence
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".fasta", delete=False
    ) as fasta_file:
        # Empty any preexisting contents
        fasta_file.truncate(0)
        fasta_file.write(
            ">test_seq\n" + "ATCG" * 30 + "T" + "C" * 20 + "A" + "ATCG" * 30 + "\n"
        )
        fasta_path = fasta_file.name

    # Create a temporary output file path (will be created by the CLI)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as out_file:
        outpath = out_file.name

    try:
        # Build argv to pass all options
        argv = [
            "talenWF-findtal",
            "--fasta",
            fasta_path,
            "--min_spacer",
            "14",
            "--max_spacer",
            "18",
            "--array_min",
            "14",
            "--array_max",
            "18",
            "--outpath",
            outpath,
            "--filter_base",
            "31",
            "--upstream_bases",
            "T",
        ]

        # Patch sys.argv and invoke main
        monkeypatch.setattr(sys, "argv", argv)
        main()

        # Assert the output file is created and non-empty
        assert os.path.exists(outpath), "Output file was not created by CLI"
        assert os.path.getsize(outpath) > 0, "Output file is empty"

        out = pd.read_csv(outpath, delimiter="\t")
        assert "Sequence Name" in out.columns[0], "Column should be Sequence Name"
        assert "TAL1 start" in out.columns, "Column should be TAL1 start"
        assert "TAL2 start" in out.columns, "Column should be TAL2 start"
        assert len(out) > 0, "Output file should have at least one row"
        for i, row in out.iterrows():
            print(dict(row))

    finally:
        # Cleanup temp files
        try:
            os.unlink(fasta_path)
        except Exception:
            pass
        try:
            os.unlink(outpath)
        except Exception:
            pass


def test_end_to_end_happy_path_nofilter(monkeypatch):
    """Invoke CLI main() with all options and verify output file is created and non-empty."""
    # Create a temporary FASTA file with a simple valid sequence
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".fasta", delete=False
    ) as fasta_file:
        # Empty any preexisting contents
        fasta_file.truncate(0)
        fasta_file.write(
            ">test_seq\n" + "ATCG" * 30 + "T" + "C" * 20 + "A" + "ATCG" * 30 + "\n"
        )
        fasta_path = fasta_file.name

    # Create a temporary output file path (will be created by the CLI)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as out_file:
        outpath = out_file.name

    try:
        # Build argv to pass all options
        argv = [
            "talenWF-findtal",
            "--fasta",
            fasta_path,
            "--min_spacer",
            "14",
            "--max_spacer",
            "18",
            "--array_min",
            "14",
            "--array_max",
            "18",
            "--outpath",
            outpath,
            "--upstream_bases",
            "T",
        ]

        # Patch sys.argv and invoke main
        monkeypatch.setattr(sys, "argv", argv)
        main()

        # Assert the output file is created and non-empty
        assert os.path.exists(outpath), "Output file was not created by CLI"
        assert os.path.getsize(outpath) > 0, "Output file is empty"

        out = pd.read_csv(outpath, delimiter="\t")
        assert "Sequence Name" in out.columns[0], "Column should be Sequence Name"
        assert "TAL1 start" in out.columns, "Column should be TAL1 start"
        assert "TAL2 start" in out.columns, "Column should be TAL2 start"
        assert len(out) > 0, "Output file should have at least one row"
        for i, row in out.iterrows():
            print(dict(row))

    finally:
        # Cleanup temp files
        try:
            os.unlink(fasta_path)
        except Exception:
            pass
        try:
            os.unlink(outpath)
        except Exception:
            pass
