#!/usr/bin/env python3
"""
Column-aware PDF text extractor for NSE reports.
Fixes the 46.2% column-layout artifact issue by:
1. Detecting text blocks with spatial positioning
2. Grouping blocks into horizontal bands (rows)
3. Sorting blocks top-to-bottom, left-to-right within each row
4. Preserving logical reading order for multi-column layouts
"""

import fitz  # PyMuPDF
import os
import re
from pathlib import Path


def extract_text_column_aware(pdf_path, output_path=None):
    """
    Extract text from PDF respecting column layout.
    
    Args:
        pdf_path: Path to PDF file
        output_path: Optional path to save extracted text
    
    Returns:
        Extracted text string
    """
    doc = fitz.open(pdf_path)
    all_text = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = extract_page_column_aware(page)
        all_text.append(page_text)
    
    doc.close()
    
    full_text = "\n\n".join(all_text)
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
    
    return full_text


def extract_page_column_aware(page, row_threshold=15, min_column_gap=150):
    """
    Extract text from a single page with column awareness.
    
    Args:
        page: PyMuPDF page object
        row_threshold: Pixels of vertical tolerance to group blocks into same row
        min_column_gap: Minimum horizontal gap (pixels) to consider blocks as separate columns
    
    Returns:
        Text string with proper reading order
    """
    blocks = page.get_text('dict')['blocks']
    
    # Filter to text blocks only (type=0)
    text_blocks = []
    for block in blocks:
        if block.get('type') != 0:
            continue
        
        # Extract text from block
        block_text_lines = []
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                text = span.get('text', '').strip()
                if text:
                    block_text_lines.append(text)
        
        if not block_text_lines:
            continue
        
        bbox = block.get('bbox', [0, 0, 0, 0])
        x0, y0, x1, y1 = bbox
        
        text_blocks.append({
            'y0': y0,
            'y1': y1,
            'x0': x0,
            'x1': x1,
            'y_mid': (y0 + y1) / 2,
            'width': x1 - x0,
            'text': ' '.join(block_text_lines)
        })
    
    if not text_blocks:
        return ""
    
    # Sort blocks by vertical position first
    text_blocks.sort(key=lambda b: b['y_mid'])
    
    # Group blocks into horizontal bands (rows)
    rows = []
    current_row = [text_blocks[0]]
    current_y_mid = text_blocks[0]['y_mid']
    
    for block in text_blocks[1:]:
        # If this block is vertically close to current row, add to same row
        if abs(block['y_mid'] - current_y_mid) <= row_threshold:
            current_row.append(block)
        else:
            # Save current row and start new one
            rows.append(current_row)
            current_row = [block]
            current_y_mid = block['y_mid']
    
    # Don't forget the last row
    if current_row:
        rows.append(current_row)
    
    # Process each row
    page_text_lines = []
    for row in rows:
        # Sort row by x0 (left-to-right)
        row.sort(key=lambda b: b['x0'])
        
        # Check if this row actually has multiple columns
        # Only join with ' | ' if blocks are truly separated horizontally
        if len(row) == 1:
            # Single block - just use its text
            page_text_lines.append(row[0]['text'])
        else:
            # Multiple blocks - check if they're actually columns or just adjacent
            should_join_columns = False
            
            # Check for significant horizontal gaps between blocks
            for i in range(len(row) - 1):
                gap = row[i+1]['x0'] - row[i]['x1']
                if gap > min_column_gap:
                    should_join_columns = True
                    break
            
            # Also check if blocks span most of page width (likely full-width, not columns)
            page_width_estimate = max(b['x1'] for b in row) - min(b['x0'] for b in row)
            total_text_width = sum(b['width'] for b in row)
            
            # If text fills most of the span, it's probably not multi-column
            if page_width_estimate > 400 and total_text_width > page_width_estimate * 0.8:
                should_join_columns = False
            
            if should_join_columns:
                # Join with separator to indicate column break
                row_text = ' | '.join(b['text'] for b in row)
            else:
                # Just concatenate with space - likely continuous text
                row_text = ' '.join(b['text'] for b in row)
            
            page_text_lines.append(row_text)
    
    return '\n'.join(page_text_lines)


def detect_column_layout(pdf_path, sample_pages=5):
    """
    Analyze PDF to detect column layout patterns.
    
    Returns:
        Dictionary with analysis results
    """
    doc = fitz.open(pdf_path)
    analysis = {
        'total_pages': len(doc),
        'pages_with_columns': 0,
        'column_patterns': [],
        'recommendations': []
    }
    
    for page_num in range(min(sample_pages, len(doc))):
        page = doc[page_num]
        blocks = page.get_text('dict')['blocks']
        text_blocks = [b for b in blocks if b.get('type') == 0]
        
        if len(text_blocks) < 3:
            continue
        
        # Check for horizontal separation (columns)
        has_columns = False
        for i, b1 in enumerate(text_blocks):
            for j, b2 in enumerate(text_blocks):
                if i >= j:
                    continue
                
                y1_mid = (b1['bbox'][1] + b1['bbox'][3]) / 2
                y2_mid = (b2['bbox'][1] + b2['bbox'][3]) / 2
                
                # Same vertical band?
                if abs(y1_mid - y2_mid) < 30:
                    x1_mid = (b1['bbox'][0] + b1['bbox'][2]) / 2
                    x2_mid = (b2['bbox'][0] + b2['bbox'][2]) / 2
                    
                    # Horizontally separated?
                    if abs(x1_mid - x2_mid) > 100:
                        has_columns = True
                        break
            
            if has_columns:
                break
        
        if has_columns:
            analysis['pages_with_columns'] += 1
            analysis['column_patterns'].append(page_num)
    
    doc.close()
    
    # Generate recommendations
    if analysis['pages_with_columns'] > 0:
        analysis['recommendations'].append(
            f"Column layout detected on {analysis['pages_with_columns']}/{sample_pages} sampled pages. "
            "Use column-aware extraction."
        )
    else:
        analysis['recommendations'].append(
            "No significant column layout detected. Standard extraction may suffice."
        )
    
    return analysis


def compare_extraction_methods(pdf_path):
    """
    Compare standard vs column-aware extraction quality.
    
    Returns:
        Dictionary with comparison metrics
    """
    doc = fitz.open(pdf_path)
    
    # Standard extraction (PyMuPDF default)
    standard_text = ""
    for page in doc:
        standard_text += page.get_text() + "\n\n"
    
    # Column-aware extraction
    column_text = extract_text_column_aware(pdf_path)
    
    doc.close()
    
    # Simple metrics
    comparison = {
        'standard_length': len(standard_text),
        'column_aware_length': len(column_text),
        'length_diff_pct': abs(len(column_text) - len(standard_text)) / max(len(standard_text), 1) * 100,
        'sample_comparison': {
            'standard_first_500': standard_text[:500].replace('\n', ' '),
            'column_first_500': column_text[:500].replace('\n', ' ')
        }
    }
    
    return comparison


if __name__ == '__main__':
    import sys
    
    # Test on available PDFs
    raw_pdfs_dir = Path('nse_audit_data/raw_pdfs')
    processed_dir = Path('nse_audit_data/processed_text_column_aware')
    
    if not raw_pdfs_dir.exists():
        print("ERROR: nse_audit_data/raw_pdfs/ directory not found")
        sys.exit(1)
    
    pdf_files = list(raw_pdfs_dir.glob('*.pdf*'))[:5]  # Test first 5
    
    print("=" * 70)
    print("COLUMN-AWARE EXTRACTION TEST")
    print("=" * 70)
    
    for pdf_path in pdf_files:
        print(f"\n{'='*60}")
        print(f"FILE: {pdf_path.name}")
        print('='*60)
        
        # Detect column layout
        analysis = detect_column_layout(str(pdf_path))
        print(f"Pages analyzed: {analysis['total_pages']}")
        print(f"Pages with columns: {analysis['pages_with_columns']}")
        for rec in analysis['recommendations']:
            print(f"  → {rec}")
        
        # Extract with column-aware method
        output_name = pdf_path.name.replace('.pdf', '').replace('.pdf', '') + '_column_fixed.txt'
        output_path = processed_dir / output_name
        
        extracted = extract_text_column_aware(str(pdf_path), str(output_path))
        print(f"Extracted {len(extracted):,} characters → {output_path}")
        
        # Show sample
        print("\nFirst 400 chars of column-aware extraction:")
        print("-" * 60)
        print(extracted[:400])
        print("-" * 60)
    
    print(f"\n✓ Column-aware extraction complete!")
    print(f"Output directory: {processed_dir.absolute()}")
