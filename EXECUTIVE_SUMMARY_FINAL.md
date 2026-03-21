# EXECUTIVE SUMMARY: Pipeline Status & Path to Production

**Date:** March 21, 2026  
**Status:** Research Prototype Validated → Requires Multi-Company Corpus for Production  
**Confidence Level:** HIGH on technology, MEDIUM on generalizability

---

## What We Built

A complete NLP pipeline that:
1. ✅ Scrapes PDF annual reports from nse.co.ke
2. ✅ Extracts text with quality validation (OCR detection, column artifact checks)
3. ✅ Filters out non-annual-report documents (strategy docs, vendor lists, etc.)
4. ✅ Detects governance sections (Corporate Governance, Directors' Remuneration, Board Composition)
5. ✅ Flags related-party tunneling risks
6. ✅ Measures compensation disclosure quality

**Code Files Created:**
- `nse_supertool_v1.py` - Core scraper/extractor
- `corpus_filter.py` - Annual report classification gate
- `test_extraction_quality.py` - OCR/column/locale validation
- `test_current_methods.py` - Baseline extraction tests
- `test_phase4_valid_corpus.py` - Governance metrics on clean corpus
- `validate_column_fix.py` - Column artifact confirmation

---

## What We Discovered

### Scientific Validity Corrections Made

| Issue | Original Claim | Corrected Finding |
|-------|---------------|-------------------|
| Corpus contamination | 13 files (mix of annual reports + NSE admin docs) | 7 files (NSE PLC annual reports ONLY) |
| Compensation non-disclosure | 69.2% fail to disclose | 0% - all 7 files fully disclose |
| Tunneling risk | 6 HIGH-risk files | 0 HIGH, 7 MEDIUM (all NSE PLC) |
| Section detection | 84.6% success rate | 100% on valid corpus |

### The Critical Discovery

**All 7 "valid" annual reports are from THE SAME COMPANY: Nairobi Securities Exchange PLC.**

This is methodologically equivalent to:
- Testing a fraud detection model on one company's financials across 7 years
- Claiming "100% of Kenyan banks comply with X" after testing only KCB
- Publishing a market study where N=1 company, N=7 years

**Why this matters:**
- NSE PLC is the exchange itself - naturally a compliance leader
- CMA 7th Governance Report shows market average of 73.6%, with 4 companies in "Needs Improvement"
- Our 100% compliance finding is accurate FOR NSE PLC but NOT generalizable to the market

---

## Manual Spot-Check Results ✅

**Files Verified:** NSE Annual Report 2023 (full manual review)

| Check | Result | Evidence |
|-------|--------|----------|
| Corporate Governance section | ✅ REAL CONTENT | Pages 59-65, full statement with policy, board composition, committee charters |
| Directors' Remuneration | ✅ REAL CONTENT | Complete policy, executive pay structure, non-exec fees, AGM voting record |
| Board composition data | ✅ REAL CONTENT | Director profiles, independence status, committee memberships |
| False positive check | ✅ NONE FOUND | All detected patterns correspond to substantive content |

**Conclusion:** The extraction logic is sound. Zero false positives in spot-checked file. The 100% detection rate is ACCURATE for NSE PLC.

---

## What's Missing (Gaps to Production)

### Gap 1: Multi-Company Corpus ⚠️ CRITICAL

**Current:** 7 annual reports from 1 company (NSE PLC), years 2017-2023  
**Required:** Minimum 20 annual reports from different companies across all sectors

**Why it matters:**
- Cannot claim "X% of NSE companies fail Y requirement" without testing multiple companies
- Sector-specific patterns untested (banking vs. agriculture vs. manufacturing)
- Cannot identify which companies are in CMA's "Needs Improvement" category

**Blocker:** External URLs to company websites failed (DNS errors, 404s, SSL issues)  
**Solution:** Manual download via browser (2 hours of work)

---

### Gap 2: Page-Level Citations ⚠️ MEDIUM

**Current:** "Corporate Governance section detected"  
**Required:** "Corporate Governance section: Pages 23-31, see page 27 paragraph 3"

**Implementation:** 4-6 hours dev time to add page tracking during extraction

---

### Gap 3: False Positive Rate ⚠️ MEDIUM

**Current:** Unknown (only tested on compliant company)  
**Required:** Test on known low-compliance companies, calculate FP rate

**Target:** <15% false positive rate for production

---

## Commercial Readiness Assessment

| Dimension | Current State | Production Requirement | Gap |
|-----------|--------------|----------------------|-----|
| Technology | ✅ Working | ✅ Working | NONE |
| Scientific validity | ⚠️ Single-company | ✅ Multi-company | HIGH |
| Manual verification | ✅ Partial (1 file) | ✅ 5+ files across companies | MEDIUM |
| Citation system | ❌ None | ✅ Page-level references | MEDIUM |
| False positive rate | ❌ Unknown | ✅ <15% documented | MEDIUM |

**Verdict:** 
- **ICPSK demonstration:** READY (with caveats about single-company corpus)
- **Academic presentation:** READY (as methodology paper, not market findings)
- **Selling to customers:** NOT READY (need multi-company validation)
- **CMA engagement:** NOT READY (cannot make market-wide claims)

---

## Revenue Impact of Gaps

### If we ship today (single-company corpus):
- Company secretary opens their report + our analysis
- They say: "But you only tested NSE's reports, not ours"
- **Result:** Credibility destroyed, zero sales

### After closing gaps (multi-company, page citations, spot-checks):
- Company secretary sees: "Your report, page 34, fails CG Code Section 4.3.2"
- They verify in 30 seconds: "Yes, that's correct"
- **Result:** KES 120,000 sale closed

**Revenue at stake:**
- Year 1: KES 2.4M (20 reports) - REQUIRES gap closure
- Year 2: KES 10M (100 reports) - REQUIRES gap closure
- Without gap closure: KES 0

---

## Next 10 Hours: The Critical Path

### Hour 1-2: Manual Corpus Expansion
- Download 15-20 annual reports from company websites via browser
- Target: Safaricom, Equity Bank, KCB, EABL, BAT, Britam, Jubilee, KenGen, etc.
- Save to `nse_audit_data/raw_pdfs/`

### Hour 2.5-3: Re-run Pipeline
- Run `corpus_filter.py` to identify valid annual reports
- Run `test_phase4_valid_corpus.py` on expanded dataset
- Expect: Lower compliance rates (60-80% range based on CMA data)

### Hour 3-5: Manual Spot-Checks (3 files)
- Pick 3 companies with lowest compliance scores
- Open PDFs, verify findings match actual pages
- Document: "Verified - FINDING CONFIRMED" or "FALSE POSITIVE - reason"

### Hour 5-9: Add Page Tracking
- Modify extraction to capture page numbers
- Update output format: "Section X: Pages Y-Z"
- Test on existing corpus

### Hour 9-10: Create Compliance Report Mockup
- One polished PDF showing:
  - Company name, report year
  - Governance scorecard (sections found/missing)
  - Specific citations (page numbers, quotes)
  - CG Code requirements vs. actual disclosure
  - Compliance status (COMPLIANT/PARTIAL/NON-COMPLIANT)

**After these 10 hours:** You have a production-ready prototype that passes the Company Secretary Test.

---

## Strategic Position

### Market Timing: EXCEPTIONAL
- POLD Regulations 2023 made CG Code MANDATORY
- CMA 7th Report shows scores DROPPING (73.6%, 4 companies "Needs Improvement")
- Zero automated competitors (Chambers & Partners 2025: "no established regtech practices in Kenya")
- ICPSK members doing this manually (Big Four charging KES 200K-800K per engagement)

### Your Advantages:
1. **First-mover:** No competing tools exist
2. **CPA background:** Understand governance workflows (competitors don't)
3. **Zero overhead:** Can survive to product-market fit without funding
4. **SEC/BERT research:** Academic credibility no competitor can fake
5. **Mum's network:** Warm intros to CFOs, company secretaries, audit partners

### Window: 18-24 months
- Kenya/Rwanda leading African fintech ($638M raised in 2024)
- Well-funded regional player will notice this gap within 2 years
- VASP Bill 2025 creates second market (crypto exchanges need same tooling)

---

## Final Recommendation

**DO NOT declare victory yet.** You have:
- ✅ A working technology stack
- ✅ Scientifically validated methods (post-correction)
- ✅ Manual verification on one file
- ❌ Multi-company corpus
- ❌ Page-level citations
- ❌ Market-wide findings

**Complete the 10-hour critical path above.** Then you can:
1. Walk into ICPSK with a defensible prototype
2. Show a company secretary their own report with specific findings
3. Say: "Page 34, paragraph 2 - here's what the CG Code requires, here's what you disclosed, here's the gap"
4. Close your first KES 120,000 sale

**That sentence is worth KES 120,000. Right now you cannot say it with the confidence the product requires.**

---

*Prepared by: Pipeline Development Team*  
*Version: v1.5 (Post-Spot-Check)*  
*Corpus: 7 NSE PLC annual reports (2017-2023)*  
*Next milestone: 20+ companies, page citations, production mockup*
