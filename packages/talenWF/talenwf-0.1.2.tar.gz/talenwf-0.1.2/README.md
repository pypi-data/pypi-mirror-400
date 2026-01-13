# talenWF

A minimal TALEN window finder packaged for CLI and API use, intended to be a drop-in for MitoEdit's TAL finding functionality.

## Features

- 🔍 **TALEN Window Finding**: Efficiently finds TALEN binding sites in DNA sequences
- 🐍 **Python API**: Easy-to-use class-based interface
- 💻 **Command Line Interface**: Ready-to-use CLI tool
- 🔄 **MitoEdit Compatible**: Drop-in replacement for MitoEdit's TAL finding functionality
- 📊 **Pandas Integration**: Returns results as DataFrames for easy analysis
- 🧬 **BioPython Support**: Robust FASTA file handling
- ⚡ **Memory Efficient**: Generator-based processing for large sequences

## Installation

### From PyPI (recommended)

```bash
pip install talenWF
```

### From source (development)

```bash
git clone https://github.com/yourusername/talenWF.git
cd talenWF
pip install -e .
```

### With development dependencies

```bash
pip install talenWF[dev]
```

## CLI

```bash
talenWF-findtal --fasta /path/to/seq.fasta --min 14 --max 18 --arraymin 14 --arraymax 18 --outpath /tmp/talenWF.tsv
```

## API

```python
from talenWF import FindTALTask

# Using the modern class-based API
task = FindTALTask(
    fasta="/path/to/seq.fasta",
    min_spacer=14,
    max_spacer=18,
    array_min=14,
    array_max=18,
    outpath="/tmp/talenWF.tsv"
)
df = task.run()
```

## Citation

If you use talenWF in your research, please cite the original TALE-NT 2.0 tool:

```
Doyle, E. L., Booher, N. J., Standage, D. S., Voytas, D. F., Brendel, V. P., VanDyk, J. K., & Bogdanove, A. J. (2012). 
TAL Effector-Nucleotide Targeter (TALE-NT) 2.0: tools for TAL effector design and target prediction. 
Nucleic Acids Research, 40(W1), W117-W122. https://doi.org/10.1093/nar/gks608
```

### About This Project

talenWF is a modernized implementation of the TALE-NT 2.0 algorithm, developed as part of the St. Jude KIDS25 BioHackathon Project. This tool provides a Python-based, memory-efficient alternative to the original TALE-NT 2.0 web interface, with improved performance and easier integration into bioinformatics workflows.

**Key Improvements:**
- Modern Python implementation with class-based API
- Memory-efficient generator-based processing
- Command-line interface for batch processing
- Pandas integration for data analysis
- BioPython support for robust sequence handling

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
