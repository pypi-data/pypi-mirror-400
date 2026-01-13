import argparse
import sys
import logging
from Bio import SeqIO
from .api import FindTALTask


def main():
    """CLI entry point for talenWF."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
    logger = logging.getLogger("talenWF")
    parser = argparse.ArgumentParser(description="talenWF: TALEN window finder")
    parser.add_argument("--fasta", required=True, help="FASTA file path")
    parser.add_argument(
        "--min_spacer", type=int, default=14, help="Minimum spacer length for TALE-NT"
    )
    parser.add_argument(
        "--max_spacer", type=int, default=18, help="Maximum spacer length for TALE-NT"
    )
    parser.add_argument(
        "--array_min", type=int, default=14, help="Minimum array length for TALE-NT"
    )
    parser.add_argument(
        "--array_max", type=int, default=18, help="Maximum array length for TALE-NT"
    )
    parser.add_argument("--outpath", default="NA", help="Output path for TALE-NT")
    parser.add_argument(
        "--filter_base",
        type=int,
        help="(1-based) Filter base position for TALE-NT (comma separated)",
    )
    parser.add_argument(
        "--upstream_bases",
        type=str,
        help="Upstream bases for TALE-NT (comma separated)",
    )
    parser.add_argument("--gspec", action="store_true", help="Use G-specific RVD")
    args = parser.parse_args()

    # Run the TAL finding task
    logger.info("Starting TAL finding task...")
    FindTALTask(
        fasta=args.fasta,
        min_spacer=args.min_spacer,
        max_spacer=args.max_spacer,
        array_min=args.array_min,
        array_max=args.array_max,
        outpath=args.outpath,
        filter_base=args.filter_base,
        upstream_bases=args.upstream_bases.split(",") if args.upstream_bases else ["T"],
        gspec=args.gspec,
    ).run()
    logger.info("TAL finding task completed successfully!")


if __name__ == "__main__":
    main()
