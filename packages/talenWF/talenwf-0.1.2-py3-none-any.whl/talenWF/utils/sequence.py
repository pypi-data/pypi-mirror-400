from Bio import SeqIO
import warnings
import logging
import sys
import typing

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("talenWF")


def get_sequence(
    fasta: typing.Optional[str] = None, sequence: typing.Optional[str] = None
) -> tuple[str, str]:
    """
    Get the sequence from a FASTA file or a string.

    Args:
        fasta: The path to the FASTA file.
        sequence: The sequence string.
    Returns:
        tuple[str, str]: The sequence and sequence ID.
    """
    sequence_id = None
    if fasta is not None:
        # Validate FASTA file exists and is readable
        try:
            with open(fasta, "r") as f:
                # Try to parse the first record to validate FASTA format
                records_iter = SeqIO.parse(f, "fasta")
                first_record = next(records_iter)
                logger.info(f"Processing FASTA file: {fasta}")
                logger.info(
                    f"First sequence: {first_record.id} (length: {len(first_record.seq)})"
                )
                sequence = str(first_record.seq).upper()
                sequence_id = first_record.id
                if next(records_iter, None) is not None:
                    warnings.warn(
                        "Multiple sequences found in FASTA file, only the first sequence will be used"
                    )
        except FileNotFoundError:
            raise FileNotFoundError(f"FASTA file not found: {fasta}")
        except Exception as e:
            raise Exception(f"Error reading FASTA file: {e}")
    else:
        # use sequence arg if fasta not provided
        if sequence is None:
            raise ValueError("Sequence is required if fasta is not provided")
        sequence = sequence.upper()
        sequence_id = "Sequence"

    if len(sequence) == 0:
        raise ValueError("Sequence is empty")
    return sequence, sequence_id
