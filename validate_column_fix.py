#!/usr/bin/env python3
"""
Validation script to measure column layout artifact reduction.
Compares standard vs column-aware extraction quality.
"""

import os
from pathlib import Path
from column_aware_extractor import extract_text_column_aware, detect_column_layout


def check_column_artifact(text_sample):
    """
    Check for common column-reading artifacts.
    Returns True if artifact detected, False if clean.
    """
    artifacts = []
    
    # Artifact 1: Disjointed sentences (reading across columns)
    lines = text_sample.split('\n')
    for i, line in enumerate(lines[:20]):
        # Look for pipe separators indicating column joins
        if ' | ' in line:
            parts = line.split(' | ')
            if len(parts) >= 2:
                # Check if parts are semantically disconnected
                part1_end = parts[0].strip()[-20:] if len(parts[0]) > 20 else parts[0].strip()
                part2_start = parts[1].strip()[:20]
                
                # Heuristic: if both parts look like complete phrases, it's intentional column separation
                # If they're fragments that don't connect, it might be an artifact
                if not part1_end.endswith(('.', ',', ';', ':')) and not part2_start[0].isupper():
                    artifacts.append(f"Potential column break at line {i+1}")
    
    # Artifact 2: Table of contents jumbling
    toc_patterns = [
        '... 05', '... 06', '... 08', '... 10', '... 12'
    ]
    toc_count = sum(1 for pattern in toc_patterns if pattern in text_sample)
    if toc_count >= 3:
        # Multiple TOC entries on same line = column artifact
        for line in lines[:30]:
            if line.count('...') >= 2:
                artifacts.append(f"TOC column merge detected: {line[:80]}")
    
    return artifacts


def compare_extractions(pdf_path, standard_text_path, column_text_path):
    """
    Compare standard vs column-aware extraction for a single PDF.
    """
    results = {
        'pdf': pdf_path.name,
        'standard_artifacts': [],
        'column_artifacts': [],
        'improvement': None
    }
    
    # Read standard extraction
    if os.path.exists(standard_text_path):
        with open(standard_text_path, 'r', encoding='utf-8') as f:
            standard_text = f.read()
        results['standard_artifacts'] = check_column_artifact(standard_text[:2000])
        results['standard_length'] = len(standard_text)
    else:
        results['standard_artifacts'] = ['File not found']
        results['standard_length'] = 0
    
    # Read column-aware extraction
    if os.path.exists(column_text_path):
        with open(column_text_path, 'r', encoding='utf-8') as f:
            column_text = f.read()
        results['column_artifacts'] = check_column_artifact(column_text[:2000])
        results['column_length'] = len(column_text)
    else:
        results['column_artifacts'] = ['File not found']
        results['column_length'] = 0
    
    # Calculate improvement
    std_count = len(results['standard_artifacts'])
    col_count = len(results['column_artifacts'])
    
    if std_count > 0:
        reduction = (std_count - col_count) / std_count * 100
        results['improvement'] = f"{reduction:+.1f}% artifact change"
    else:
        results['improvement'] = "No artifacts in either method"
    
    return results


def main():
    print("=" * 80)
    print("COLUMN LAYOUT ARTIFACT VALIDATION REPORT")
    print("=" * 80)
    
    raw_dir = Path('nse_audit_data/raw_pdfs')
    standard_dir = Path('nse_audit_data/processed_text')
    column_dir = Path('nse_audit_data/processed_text_column_aware')
    
    all_results = []
    total_std_artifacts = 0
    total_col_artifacts = 0
    
    # Process all PDFs
    pdf_files = list(raw_dir.glob('*.pdf*'))
    
    for pdf_path in pdf_files:
        pdf_name = pdf_path.name.replace('.pdf.pdf', '.pdf').replace('.pdf', '')
        standard_path = standard_dir / f"{pdf_name}.txt.txt"
        column_path = column_dir / f"{pdf_name}_column_fixed.txt"
        
        result = compare_extractions(pdf_path, standard_path, column_path)
        all_results.append(result)
        
        total_std_artifacts += len(result['standard_artifacts'])
        total_col_artifacts += len(result['column_artifacts'])
        
        # Print summary for this file
        print(f"\n{result['pdf']}")
        print("-" * 60)
        print(f"  Standard extraction: {len(result['standard_artifacts'])} artifacts")
        for artifact in result['standard_artifacts'][:2]:
            print(f"    ⚠️  {artifact}")
        
        print(f"  Column-aware:      {len(result['column_artifacts'])} artifacts")
        for artifact in result['column_artifacts'][:2]:
            print(f"    ⚠️  {artifact}")
        
        print(f"  Improvement:       {result['improvement']}")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Total PDFs analyzed:     {len(all_results)}")
    print(f"Total standard artifacts: {total_std_artifacts}")
    print(f"Total column artifacts:   {total_col_artifacts}")
    
    if total_std_artifacts > 0:
        overall_reduction = (total_std_artifacts - total_col_artifacts) / total_std_artifacts * 100
        print(f"Overall artifact reduction: {overall_reduction:.1f}%")
    else:
        print("Overall artifact reduction: N/A (no baseline artifacts)")
    
    # Files with most improvement
    improved_files = [r for r in all_results if len(r['standard_artifacts']) > len(r['column_artifacts'])]
    if improved_files:
        print(f"\n✓ Files with improvement: {len(improved_files)}/{len(all_results)}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    
    if total_col_artifacts < total_std_artifacts:
        print("✅ Column-aware extraction REDUCES artifacts. RECOMMENDED for production.")
    elif total_col_artifacts == total_std_artifacts:
        print("⚖️  Both methods show similar artifact rates. Consider hybrid approach.")
    else:
        print("❌ Column-aware extraction shows MORE artifacts. Needs refinement.")
    
    return all_results


if __name__ == '__main__':
    main()
