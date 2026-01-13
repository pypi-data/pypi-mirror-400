"""FASTA sequence file importer.

FASTAImporter for DNA/RNA/protein sequences
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class FASTAImporter(BaseImporter[list[dict[str, Any]]]):
    """Import FASTA format sequence files.

        FASTAImporter for sequence analysis

    Features:
    - Standard FASTA format parsing
    - Multi-sequence file support
    - Sequence metadata extraction from headers
    - DNA, RNA, and protein sequences
    - Sequence length calculation
    - GC content calculation for DNA/RNA

    Example:
        >>> importer = FASTAImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("sequences.fasta")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     for seq in result.data:
        ...         print(f"{seq['id']}: {len(seq['sequence'])} bp")
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize importer."""
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata for FASTA importer

            Importer metadata
        """
        return ImporterMetadata(
            name="FASTA Importer",
            description="Import FASTA sequence files (DNA, RNA, protein)",
            supported_formats=("fasta", "fa", "fna", "faa", "txt"),
            category="biology",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate FASTA file.

        Args:
            source: Path to FASTA file

        Returns:
            True if source is valid FASTA file

            Source validation
        """
        path = Path(source) if isinstance(source, str) else source
        if not path.exists() or not path.is_file():
            return False

        # Check if file contains FASTA header (>)
        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                first_line = f.readline()
                return first_line.strip().startswith(">")
        except OSError:
            # File access errors
            return False

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import FASTA sequences.

        Args:
            source: Path to FASTA file

        Returns:
            ImportResult with sequence data

            FASTA data import

        Raises:
            ValueError: If source is invalid
            IOError: If file cannot be read
        """
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data=[],
                errors=["Invalid FASTA file or file does not exist"],
            )

        path = Path(source) if isinstance(source, str) else source

        try:
            sequences: list[dict[str, Any]] = []
            current_id = ""
            current_description = ""
            current_sequence: list[str] = []
            warnings: list[str] = []

            with path.open("r", encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()

                    if not line:
                        continue  # Skip empty lines

                    if line.startswith(">"):
                        # Save previous sequence if exists
                        if current_id:
                            seq_data = self._create_sequence_record(
                                current_id,
                                current_description,
                                "".join(current_sequence),
                            )
                            sequences.append(seq_data)

                        # Parse new header
                        header = line[1:]  # Remove >
                        parts = header.split(None, 1)  # Split on first whitespace
                        current_id = parts[0] if parts else f"seq_{line_num}"
                        current_description = parts[1] if len(parts) > 1 else ""
                        current_sequence = []

                    elif line.startswith(";"):
                        # Comment line, skip
                        continue

                    else:
                        # Sequence data
                        # Remove whitespace and validate characters
                        clean_seq = "".join(line.split()).upper()
                        current_sequence.append(clean_seq)

                # Save last sequence
                if current_id:
                    seq_data = self._create_sequence_record(
                        current_id,
                        current_description,
                        "".join(current_sequence),
                    )
                    sequences.append(seq_data)

            if not sequences:
                return ImportResult(
                    success=False,
                    data=[],
                    errors=["No sequences found in FASTA file"],
                )

            # Report progress
            self.on_progress(len(sequences), len(sequences))

            return ImportResult(
                success=True,
                data=sequences,
                records_imported=len(sequences),
                warnings=warnings,
                metadata={
                    "total_sequences": len(sequences),
                    "total_length": sum(s["length"] for s in sequences),
                },
            )

        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Error reading FASTA file: {e!s}"],
            )

    def _create_sequence_record(
        self,
        seq_id: str,
        description: str,
        sequence: str,
    ) -> dict[str, Any]:
        """Create sequence record with metadata.

        Args:
            seq_id: Sequence identifier
            description: Sequence description
            sequence: Sequence string

        Returns:
            Dictionary with sequence data and metadata
        """
        # Calculate GC content for DNA/RNA
        gc_content = None
        seq_type = "unknown"

        # Detect sequence type
        unique_chars = set(sequence)
        if unique_chars.issubset({"A", "C", "G", "T", "N"}):
            seq_type = "DNA"
        elif unique_chars.issubset({"A", "C", "G", "U", "N"}):
            seq_type = "RNA"
        elif len(unique_chars) > 4:  # Likely protein with 20 amino acids
            seq_type = "protein"

        # Calculate GC content for DNA/RNA
        if seq_type in ("DNA", "RNA"):
            g_count = sequence.count("G")
            c_count = sequence.count("C")
            total_bases = len(sequence)
            if total_bases > 0:
                gc_content = (g_count + c_count) / total_bases * 100

        return {
            "id": seq_id,
            "description": description,
            "sequence": sequence,
            "length": len(sequence),
            "type": seq_type,
            "gc_content": gc_content,
        }


__all__ = ["FASTAImporter"]
