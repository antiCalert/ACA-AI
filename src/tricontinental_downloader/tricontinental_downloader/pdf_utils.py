from typing import Optional
import re
import sys
import argparse
import glob
import os
from pdfminer.high_level import extract_text
from tqdm import tqdm

"""
common_utils.py

Simple, efficient converter for text-based PDFs to Markdown (no OCR).
Depends on: pdfminer.six
Install: pip install pdfminer.six

Usage:
    python common_utils.py "docs/*.pdf" -o outdir/
    python common_utils.py input.pdf -o output.md
"""


def _is_list_item(line: str) -> bool:
    return bool(re.match(r'^\s*(?:[-\u2022\*\u2023]|(?:\d+[\.\)]))\s+', line))


def _is_heading(line: str) -> bool:
    # Heuristic: short line, all-caps or many caps => heading
    stripped = line.strip()
    if not stripped or len(stripped) > 80:
        return False
    words = stripped.split()
    if len(words) > 8:
        return False
    letters = [c for c in stripped if c.isalpha()]
    if not letters:
        return False
    cap_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    return stripped.isupper() or cap_ratio > 0.6


def _normalize_paragraphs(text: str) -> str:
    """
    Normalize lines into paragraphs, preserve list items, detect simple headings.
    """
    lines = [ln.rstrip() for ln in text.replace('\r', '').splitlines()]
    out_blocks = []
    curr = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            if curr:
                out_blocks.append(' '.join(curr))
                curr = []
            continue
        if _is_list_item(ln):
            if curr:
                out_blocks.append(' '.join(curr))
                curr = []
            # normalize bullet char to '-'
            ln = re.sub(r'^\s*[\u2022\*\u2023]\s*', '- ', ln)
            out_blocks.append(ln)
            continue
        # Append to current paragraph (join lines)
        curr.append(ln)
    if curr:
        out_blocks.append(' '.join(curr))

    # Post-process blocks: headings and cleanup whitespace
    md_blocks = []
    for blk in out_blocks:
        blk = re.sub(r'\s+', ' ', blk).strip()
        if _is_heading(blk):
            md_blocks.append(f'## {blk.capitalize()}')
        else:
            md_blocks.append(blk)
    return '\n\n'.join(md_blocks)


def pdf_to_markdown(input_path: str, output_path: Optional[str] = None, page_break: str = '\n\n---\n\n') -> str:
    """
    Convert a text-based PDF to markdown.
    Returns markdown string. If output_path is provided, writes to file.
    """
    raw = extract_text(input_path) or ''
    # pdfminer often uses formfeed \f as page delimiter
    pages = [p for p in raw.split('\f') if p.strip()]

    md_pages = []
    for p in pages:
        md_pages.append(_normalize_paragraphs(p))

    md = page_break.join(md_pages).strip() + '\n'
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
    return md


def main():
    parser = argparse.ArgumentParser(description="Convert text PDF(s) to Markdown (no OCR). Accepts glob patterns.")
    parser.add_argument("-i", "--input", help="Input PDF file path or glob pattern (e.g. 'docs/*.pdf').", required=True)
    parser.add_argument("-o", "--output", help="Output markdown file path or directory. If omitted, writes .txt next to each input file or prints to stdout for single file.")
    parser.add_argument("--no-page-break", action="store_true", help="Do not insert page break markers.")
    args = parser.parse_args()

    pattern = args.input
    matches = glob.glob(pattern+'*.pdf', recursive=True)
    if not matches:
        sys.exit(f"No files matched pattern: {pattern}")

    page_break = '' if args.no_page_break else '\n\n---\n\n'

    # Multiple files: convert each and write to corresponding .txt (same basename, .txt extension)
    if len(matches) > 1:
        for inpath in tqdm(matches):
            outpath = os.path.splitext(inpath)[0] + '.txt'
            pdf_to_markdown(inpath, outpath, page_break=page_break)
        sys.stdout.write(f"Converted {len(matches)} files.\n")
        return

    # Single file
    inpath = matches[0]
    out = args.output
    if out:
        # If output is a directory, place file inside with same basename and .txt extension
        if os.path.isdir(out) or out.endswith(os.path.sep):
            base = os.path.splitext(os.path.basename(inpath))[0] + '.txt'
            out = os.path.join(out, base)
    else:
        # default: write next to input with .txt extension, and also print to stdout
        out = os.path.splitext(inpath)[0] + '.txt'

    md = pdf_to_markdown(inpath, out, page_break=page_break)
    # If user didn't explicitly request an output path, also print to stdout
    if not args.output:
        sys.stdout.write(md)


if __name__ == "__main__":
    main()