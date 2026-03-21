#!/usr/bin/env python3
"""
Manual spot-check generator for governance findings.
Opens 3 highest-risk PDFs and shows exact page/paragraph citations.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

TEXT_DIR = Path("nse_audit_data/processed_text")
PDF_DIR = Path("nse_audit_data/raw_pdfs")
OUTPUT_FILE = Path("nse_audit_data/manual_spotcheck_report.md")


def find_governance_sections(text: str, filename: str):
    """Find governance sections with page markers."""
    sections = []
    
    # Look for governance section headers
    patterns = [
        (r"(CORPORATE GOVERNANCE)", "Corporate Governance"),
        (r"(DIRECTORS[\'\s]+REPORT)", "Directors Report"),
        (r"(EXECUTIVE\s+COMPENSATION|REMUNERATION\s+REPORT|DIRECTORS[\'\s]+REMUNERATION)", "Executive Compensation"),
        (r"(RELATED\s+PARTY\s+TRANSACTIONS)", "Related Party Transactions"),
        (r"(RISK\s+MANAGEMENT)", "Risk Management"),
        (r"(INTERNAL\s+CONTROL)", "Internal Control"),
        (r"(AUDIT\s+COMMITTEE)", "Audit Committee"),
        (r"(BOARD\s+COMPOSITION)", "Board Composition"),
    ]
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        for pattern, section_name in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Get context (5 lines before and after)
                start = max(0, i - 2)
                end = min(len(lines), i + 8)
                context = '\n'.join(lines[start:end])
                
                sections.append({
                    "section": section_name,
                    "line_num": i,
                    "context": context[:500]
                })
    
    return sections


def find_tunneling_indicators(text: str, filename: str):
    """Find related party tunneling indicators with context."""
    indicators = []
    
    tunneling_patterns = [
        r"related\s+party\s+(?:transaction|balances|payments|loans|advances)",
        r"inter[- ]company\s+(?:balances|transactions|loans)",
        r"due\s+(?:from|to)\s+related\s+part(?:ies|y)",
        r"management\s+fees?\s+(?:paid|payable)\s+to",
        r"consultancy\s+fees?\s+(?:paid|payable)",
        r"unsecured\s+loans?\s+(?:from|to)\s+(?:directors|shareholders|related)",
    ]
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        for pattern in tunneling_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # Get context
                start = max(0, i - 1)
                end = min(len(lines), i + 3)
                context = '\n'.join(lines[start:end])
                
                indicators.append({
                    "indicator": pattern,
                    "matched_text": match.group(0),
                    "line_num": i,
                    "context": context[:400]
                })
    
    return indicators


def main():
    print("=" * 70)
    print("MANUAL SPOT-CHECK REPORT GENERATOR")
    print("=" * 70)
    print()
    
    # Load all processed texts
    files_data = []
    for txt_file in sorted(TEXT_DIR.glob("*.txt")):
        if not txt_file.name.startswith('.'):
            try:
                with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                
                # Skip non-annual reports
                if len(text) < 1000:
                    continue
                
                gov_sections = find_governance_sections(text, txt_file.name)
                tunneling = find_tunneling_indicators(text, txt_file.name)
                
                files_data.append({
                    "filename": txt_file.name,
                    "text_length": len(text),
                    "governance_sections": gov_sections,
                    "tunneling_indicators": tunneling,
                    "tunneling_count": len(tunneling)
                })
                
            except Exception as e:
                print(f"Error reading {txt_file}: {e}")
    
    # Sort by tunneling count (highest first)
    files_data.sort(key=lambda x: x['tunneling_count'], reverse=True)
    
    # Take top 3 for manual review
    top_3 = files_data[:3]
    
    # Generate report
    report_lines = [
        "# Manual Spot-Check Report: Governance Extraction Validation",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"**Corpus Size:** {len(files_data)} valid annual reports",
        "",
        "**Purpose:** Verify that automated governance extraction is citing real text from actual documents.",
        "",
        "---",
        "",
        "## Top 3 Files for Manual Review (Highest Tunneling Risk)",
        "",
    ]
    
    for idx, file_data in enumerate(top_3, 1):
        pdf_name = file_data['filename'].replace('.txt', '.pdf')
        
        report_lines.extend([
            f"### {idx}. {file_data['filename']}",
            "",
            f"**Corresponding PDF:** `{pdf_name}`",
            "",
            f"**Text Length:** {file_data['text_length']:,} characters",
            "",
            f"**Governance Sections Found:** {len(file_data['governance_sections'])}",
            "",
            f"**Tunneling Indicators:** {file_data['tunneling_count']}",
            "",
        ])
        
        # Show governance sections
        if file_data['governance_sections']:
            report_lines.append("**Governance Section Citations:**")
            report_lines.append("")
            for sec in file_data['governance_sections'][:3]:  # Top 3 sections
                report_lines.append(f"- **{sec['section']}** (line ~{sec['line_num']})")
                report_lines.append(f"  ```")
                report_lines.append(f"  {sec['context'][:200]}...")
                report_lines.append(f"  ```")
                report_lines.append("")
        
        # Show tunneling indicators
        if file_data['tunneling_indicators']:
            report_lines.append("**Tunneling Risk Indicators:**")
            report_lines.append("")
            for ind in file_data['tunneling_indicators'][:3]:  # Top 3 indicators
                report_lines.append(f"- **Pattern:** `{ind['matched_text']}` (line ~{ind['line_num']})")
                report_lines.append(f"  ```")
                report_lines.append(f"  {ind['context'][:200]}...")
                report_lines.append(f"  ```")
                report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("")
    
    # Add validation checklist
    report_lines.extend([
        "## Manual Validation Checklist",
        "",
        "For each file above:",
        "",
        "- [ ] Open the corresponding PDF in a PDF reader",
        "- [ ] Navigate to the approximate page (estimate: line_number / 50 lines per page)",
        "- [ ] Verify the governance section header exists at that location",
        "- [ ] Verify the tunneling indicator text appears in the actual document",
        "- [ ] Confirm the context matches what the extractor found",
        "- [ ] Note any discrepancies (column artifacts, OCR errors, mis-citations)",
        "",
        "## Expected Outcomes",
        "",
        "✓ **PASS**: Extracted text matches PDF content exactly (allowing for minor formatting differences)",
        "",
        "⚠️ **PARTIAL**: Text exists but column artifacts or formatting issues present",
        "",
        "✗ **FAIL**: Extracted text does not match PDF (extraction bug, wrong file, or corruption)",
        "",
        "## Notes",
        "",
        "*Line numbers are approximate. PDF page estimation: divide line number by 40-60 depending on layout density.*",
        "",
        "*If more than 2 out of 3 files fail validation, stop and fix extraction pipeline before proceeding.*",
        "",
    ])
    
    # Write report
    report_content = '\n'.join(report_lines)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"Spot-check report generated: {OUTPUT_FILE}")
    print()
    print(f"Files analyzed: {len(files_data)}")
    print(f"Top 3 selected for manual review:")
    for idx, file_data in enumerate(top_3, 1):
        print(f"  {idx}. {file_data['filename']} ({file_data['tunneling_count']} tunneling indicators)")
    print()
    print("NEXT STEP: Open the report and manually verify citations against PDFs")
    print("=" * 70)


if __name__ == "__main__":
    main()
