# Proof Beyond Reasonable Doubt: Validation Protocol

## Current Status

### What We Have Validated ✓
1. **NSE Annual Reports**: The pipeline works on NSE-listed company reports (190 documents from CMA portal)
2. **CMA Portal Structure**: URL pattern confirmed: `annualreport.cma.or.ke/company/{sector_id}/company/{company_id}/`
3. **PDF Extraction Pattern**: `/media/{SECTOR}/{Company Name}/documents/{year}.pdf`

### What Has NOT Been Validated ✗
1. **SACCO Documents**: Zero SACCO annual reports have been processed
2. **SASRA Guidance Notes**: No regulatory documents analyzed
3. **Cross-Reference Validation**: No comparison between self-reported governance and regulator assessments

---

## The Honest Boundary

**You can prove the pipeline works on NSE annual reports. That is it.**

The 190 documents scraped from CMA are mostly NSE-listed companies — same document type, same regulatory framework (NSE Corporate Governance Code), same disclosure language. This is variety in company name and sector, NOT variety in document structure or regulatory regime.

---

## What "Beyond Reasonable Doubt" Requires

For a SACCO compliance officer to trust this tool, they need to see FOUR specific proofs:

### Proof 1: Correct Extraction on Verifiable Document
**What:** Run the tool on their own annual report (or a comparable SACCO like Stima).

**Why it matters:** They know their own report. If the tool correctly identifies board composition, committee structure, and related party disclosures — and they can open the PDF and confirm every citation is accurate — that is direct verification. No statistical argument required.

**Status:** BLOCKED - Waiting for manual download of Stima SACCO 2023 Annual Report

---

### Proof 2: Correct Failure Detection
**What:** Show a SACCO that SASRA fined for governance failures, and demonstrate the tool flags the same gap.

**Why it matters:** This is predictive validity. The tool found the problem before (or at the same time as) the regulator did.

**How to achieve:**
1. Find a SACCO with known SASRA sanctions in the 2023 Supervision Report
2. Get that SACCO's annual report for the same year
3. Run the extractor
4. Compare findings against SASRA's published infractions

**Status:** BLOCKED - Need to cross-reference SASRA supervision reports with individual SACCO reports

---

### Proof 3: Honest Disclosure of Limitations
**What:** The tool explicitly states what it cannot check due to ambiguous formatting or missing sections.

**Why it matters:** A compliance officer trusts a tool MORE when it admits limitations. Overconfidence kills trust faster than admitted uncertainty.

**Implementation:**
```python
class GovernanceResult(BaseModel):
    confidence_level: Literal["high", "medium", "low"]
    requires_manual_review: List[str]  # Sections needing human verification
    missing_disclosures: List[str]  # Required items not found in document
```

**Status:** PARTIAL - Schema supports this, but extractor needs to populate these fields

---

### Proof 4: Works on THEIR Document Type Specifically
**What:** Not NSE reports — actual SACCO annual report format.

**Why it matters:** SACCO governance structure is fundamentally different from NSE companies:
- Elected boards (not appointed independent directors)
- Mandatory Credit & Education Committees (not just Audit)
- CEO non-voting at board meetings
- Related party LENDING (not just transactions)
- Independent governance audit requirement

**Status:** BLOCKED - SACCO schema built (`sacco_schema.py`) but never tested on real SACCO document

---

## The Four-Step Proof Protocol (Action Plan)

### Step 1: Download Stima FY2023 Today
**File:** `nse_data/saccos_direct/Stima_SACCO_Annual_Report_2023.pdf`

**Source:** https://www.stima-sacco.com/download/annual-report-for-the-year-ended-31-december-2023/

**Expected size:** ~7.73 MB

**Why Stima?** Kenya's second-largest SACCO by assets (KES 59.1 billion, 200,000+ members). If the tool works on this, it works on the most demanding SACCO governance report in East Africa. Everything smaller will be easier.

**STATUS:** ⏳ MANUAL DOWNLOAD REQUIRED

---

### Step 2: Create Ground Truth Manually (45 minutes)
**Before running the extractor**, read the Stima report yourself:

1. Open the PDF
2. Find the governance section
3. Write down by hand:
   - Number of board members and their roles
   - Which committees exist (Audit, Credit, Education, etc.)
   - Whether CEO attends board as non-voting
   - Whether independent governance audit was conducted
   - Related party loans to officials disclosed?

4. Save as `nse_data/saccos_direct/stima_ground_truth.json`

**This is the only scientific method.** Everything else is the extractor grading itself.

**STATUS:** ⏳ WAITING FOR DOCUMENT DOWNLOAD

---

### Step 3: Run Extractor and Compare
Once SACCO schema and extractor are ready:

```bash
python3 run_sacco_extractor.py nse_data/saccos_direct/Stima_SACCO_Annual_Report_2023.pdf
```

Compare output against ground truth. Every discrepancy tells you:
- Which regex pattern failed
- Which prompt needs adjustment
- Which section of the document structure broke the current logic

Document each failure with:
- Exact quote that confused the extractor
- Exact quote containing correct answer
- Specific fix needed

**STATUS:** ⏳ WAITING FOR SCHEMA + DOCUMENT

---

### Step 4: Build Cross-Reference Proof
This is the most powerful proof and requires NO customer document.

1. Open `nse_data/sasra_reports/SASRA_Supervision_Report_2023.pdf` (already downloaded ✓)
2. Find Stima SACCO's entry
3. Note their compliance status
4. Compare with your extractor's findings

**Possible outcomes:**
- **Positive concordance:** SASRA gave clean bill of health, tool also finds clean results = Your tool agrees with regulator
- **Predictive concordance:** Tool finds gap that SASRA also noted = Your tool predicts regulator findings
- **Divergence:** Tool finds issue SASRA missed (or vice versa) = Investigation needed

Either way, write it up as a one-page finding showing regulator alignment.

**STATUS:** ✅ SUPERVISION REPORT AVAILABLE, ⏳ WAITING FOR STIMA REPORT

---

## What to Show the Contact Right Now

You do NOT need their document to prove the tool works in their situation. You need:

### The Demonstration Package

1. **Stima Analysis Results** (once extracted):
   ```
   Board Composition: 9 members (6 male, 3 female) - Gender compliant ✓
   Committees: Audit ✓, Credit ✓, Education ✓
   CEO Non-Voting: Yes ✓
   Independent Governance Audit: Conducted ✓
   Compliance Score: 0.85/1.0
   Gaps Identified: [specific items]
   ```

2. **SASRA Cross-Reference**:
   ```
   SASRA 2023 Supervision Report Assessment: "Compliant"
   Our Tool Assessment: "Passes minimum requirements"
   Concordance: YES
   ```

3. **Framing Script**:
   > "I ran the tool on Stima SACCO's publicly available 2023 annual report — Kenya's second-largest SACCO. Here is what it found on governance structure, committee composition, and related party disclosures. Here is where it agrees with SASRA's public assessment of the same institution.
   >
   > Your SACCO uses the same regulatory framework (SASRA GG/2/2023) and similar document structure. I expect similar accuracy on your reports, and I would like to demonstrate that live with you watching."

**This removes every objection.** You are not asking them to trust an untested system. You are showing them a live result on a comparable institution they know and respect, and inviting them to verify it themselves in real time.

---

## Timeline to Proof

| Task | Duration | Status |
|------|----------|--------|
| Download Stima 2023 report | 15 min | ⏳ MANUAL |
| Download SASRA GG/2/2023 guidance | 15 min | ⏳ MANUAL |
| Read Stima report, create ground truth | 45 min | ⏳ WAITING |
| Build SACCO extractor | 2 hours | ✅ Schema ready |
| Run extractor on Stima | 10 min | ⏳ WAITING |
| Compare results, document gaps | 1 hour | ⏳ WAITING |
| Cross-reference with SASRA report | 30 min | ✅ Report available |
| Prepare demonstration package | 1 hour | ⏳ WAITING |
| **TOTAL TO PROOF** | **~5 hours** | **BLOCKED ON MANUAL DOWNLOAD** |

---

## Why This Is Scientifically Valid

This protocol follows the same validation methodology used in:
- **Medical diagnostics:** Compare new test against gold standard on same patient samples
- **Legal discovery:** Verify e-discovery tool accuracy on known document set
- **Financial auditing:** Test audit software on previously-audited financial statements

The key principle: **Ground truth first, extraction second, comparison third.**

Anything else is the tool grading itself — which you already proved does not work.

---

## Next Action Required

**YOU must manually download these two files today:**

1. **Stima SACCO Annual Report 2023**
   - URL: https://www.stima-sacco.com/download/annual-report-for-the-year-ended-31-december-2023/
   - Save to: `/workspace/nse_data/saccos_direct/Stima_SACCO_Annual_Report_2023.pdf`

2. **SASRA Guidance Note GG/2/2023**
   - URL: https://www.sasra.go.ke → Publications → search "GG/2/2023"
   - Save to: `/workspace/nse_data/saccos_direct/SASRA_Guidance_Note_GG_2_2023.pdf`

Everything else in this protocol can proceed once these files exist.

See detailed download instructions in: `MANUAL_DOWNLOAD_INSTRUCTIONS.md`
