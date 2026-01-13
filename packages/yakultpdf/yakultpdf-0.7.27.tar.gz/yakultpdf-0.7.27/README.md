# yakultpdf

**Markdown to PDF Converter based on Pandoc and Typst**

Convert Markdown files into beautiful PDFs. Supports Frontmatter configuration, automated TOC management, and Python API usage.

## Installation

```bash
pip install yakultpdf
```

> **Note**: Ensure [Pandoc](https://pandoc.org/) and [Typst](https://typst.app/) are installed before use.

## CLI Usage

**1. Initialization & Configuration**
```bash
# Initialize workspace (create configuration and directory structure)
yakultpdf init

# Install common Chinese fonts (e.g., lxgw-wenkai)
yakultpdf fonts install lxgw-wenkai
```

**2. Convert Documents**
```bash
# Convert single file (default output to out/ directory)
yakultpdf convert document.md

# Convert single file with specified output filename
yakultpdf convert document.md --output my-report

# Convert entire directory (automatically merge all md files in directory)
yakultpdf convert --dir docs/
```

**3. More Features**
```bash
# Copy built-in templates to local template/ directory
yakultpdf template
```

## Python API Usage

Note: use `mark2pdf` for importing:

```python
from mark2pdf import convert_file, convert_directory

# 1. Convert single file
# Convert input.md to output.pdf with default configuration
convert_file("input.md", output_file="output.pdf")

# 2. Convert directory
# Merge all Markdown files in docs directory and convert to merged_report.pdf
convert_directory("docs", output_file="merged_report.pdf")
```
