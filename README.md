# NSE-Testing: Disclosure Quality Audit (East Africa)

## Project Overview
This repository contains the auditing pipeline and "Ground Truth" verification methodology for the **Nairobi Securities Exchange (NSE)** listed company annual reports. This work extends the **MSQECC "Scientific Audit" Framework** (previously validated on US SEC 10-K filings) to the East African capital markets.

## What has been done so far (The MSQECC Heritage)
Before pivoting to the NSE, this auditing framework successfully identified three systemic "Linguistic Hallucinations" in modern financial NLP on the Bao et al. (2020) US fraud corpus:

1.  **The "Bao Gap" (0.67 vs 0.72 AUC)**: We replicated the State-of-the-Art benchmark and identified a 0.05 AUC inflation caused by undocumented preprocessing (winsorization and sector-year normalization) rather than real signal.
2.  **Temporal Drift Artifacts**: We demonstrated that comparing language from different SEC filing eras (1998 vs. 2024) creates false fraud signals that collapse when filings are matched by year.
3.  **TDA "Fraud Cycle" Kill**: We applied an Adversarial Shuffle-Kill test (Monte Carlo) to a purported topological signal (H1 Persistence), proving it was a statistical artifact of "dimensional inflation" rather than a real fraud pattern.

## Forensic Audit Log (Current Status)
- [x] US SEC Benchmark Replicated (AUC 0.6697).
- [x] Fraud Cycle TDA killed (Statistical Artifact confirmed).
- [x] NSE Connectivity Test: [https://www.nse.co.ke/annual-reports/](https://www.nse.co.ke/annual-reports/) is confirmed accessible for PDF harvest.
- [ ] **Next Step**: Build the PDF Extraction Layer (using `PyMuPDF`) for NSE Annual Reports.
- [ ] **Next Step**: Match NSE disclosures to **CMA Kenya Enforcement Actions** (ground truth).

## Repository Contents
- `test_kenya_pipeline.py`: Foundation for NSE connectivity and PDF text extraction.
- `VERIFICATION_PROTOCOL.md`: The MSQECC "V-Protocol" for 5-Sigma auditing.
- `MANUSCRIPT_DRAFT_V1.md`: Technical documentation of the identified US artifacts.

## To-Do for Next Developer
1.  Verify extraction quality on scanned vs. text-encoded NSE PDFs.
2.  Harvest CMA enforcement list for 2019-2024.
3.  Run the **Temporal Drift Test** on the NSE sample to check if linguistic benchmarks established in the US apply to the Kenyan context.

## 🚀 The NSE "SuperTool" Pipeline
I have included `nse_supertool_v1.py` for automated extraction of the NSE dataset. It performs:
1.  **Direct Harvest**: Scrapes `nse.co.ke` for all available `.pdf` annual reports.
2.  **Autonomous Download**: Maps URLs to unique company/year filenames.
3.  **Linguistic Extraction**: Uses `PyMuPDF` to convert binary PDF layout into clean UTF-8 text for NLP analysis.

---

## ⚠️ 10 Critical Market Artifacts (Avoid these Traps)
The next stage of this audit (the Kenyan Sprint) must account for these structural biases, or the findings will be statistically invalid:

1.  **Small N Statistical Trap**: In a market of only 66 companies, a single outlier (e.g., Safaricom) can hallucinate a market-wide trend. Use **Leave-One-Out (LOO)** cross-validation.
2.  **PDF "Dark Matter"**: Scanned PDFs (common in older filings) produce extraction noise. If OCR error rates exceed 5%, linguist analysis collapses.
3.  **Defining "Fraud"**: CMA enforcement lists include administrative fines for "late filings." Do not treat administrative delays as accounting fraud labels.
4.  **Dictionary Locale Mismatch**: US financial dictionaries (Loughran-McDonald) miss Kenyan-British business idioms.
5.  **Peer Group Ghost Town**: Matching a "fraud" firm against a "clean" contemporary in the same sub-sector (e.g., Agricultural) is nearly impossible given the low count.
6.  **IFRS Cut-offs**: The "Companies Act 2015" in Kenya created a massive linguistic discontinuity. Do not compare pre-2015 to post-2015 without normalization.
7.  **Governance vs Accounting**: The primary NSE issue is "Boardroom Composition" (Director Independence), not "Earnings Management."
8.  **Safaricom Dominance Bias**: Safaricom is the "Gold Standard" by market cap. Using it as a benchmark will just flag "smaller, poorer firms" as high-risk.
9.  **Colum-Flow Hallucinations**: Multicolumn PDF layouts often lead to "jumbled" text extraction; this looks like high entropy to a model but is just a layout error.
10. **Regulatory Sales Logic**: To sell to the CMA, transition from "AUC Scores" to "Case Recall"—demonstrating how many millions in the *Imperial Bank* or *Chase Bank* cases could have been saved by flagging language 12 months earlier.

---

## 🎖️ The NSE Priority-A Audit List (Top 10)
I have identified these 10 items as the "Absolute Bedrock" for the Kenyan market sprint. Skip these, and any signal found will be an artifact:

1.  **PDF "Dark Matter" (Layout vs OCR)**: Detecting scanned-image PDFs vs text-encoded ones. OCR error noise mimics "deception complexity."
2.  **The Safaricom Outlier**: Normalizing for Safaricom's massive market-cap dominance to prevent it from skewing the market mean.
3.  **Governance Independence (Section 41)**: Automated extraction of "Independent Director" counts to cross-check against the "CG Code."
4.  **Tenure Erosion (Section 45)**: Identifying directors with 9+ years tenure who are listed as "Independent" but are structurally compromised.
5.  **Related Party "Tunneling" (Section 48)**: High-resolution analysis of the "Related Party Disclosures" note—the primary fraud mechanism in family-controlled NSE firms.
6.  **British/Kenyan Locale Normalization**: Updating dictionaries for British spelling (`-ise` vs `-ize`) and local idioms (`Sacco`, `KRA Disputes`).
7.  **"Late Filing" Label Correction**: Manually separating administrative delay fines from core accounting fraud in the CMA ground truth.
8.  **Section Identification (MD&A Equivalent)**: Regex logic to consistently find the management narrative across 66 non-standardized reports.
9.  **The "Silence of the Regulator"**: Implementing a "False Negative" filter for companies that are high-risk (linguistically) but un-fined due to regulatory lag.
10. **Signature Authenticity Proxy**: Auditing the scan quality and consistency of CEO/Chairman signatures as a proxy for board engagement.

---

## 💤 Parked Categories (Skip for Phase 1)
To maximize speed, we are skipping these **Moderate/Low Priority** areas for now:
*   **Scientific Rigor (Cat 9)**: No "5-Sigma" or complex TDA shuffles until the basic linear model is stable.
*   **EAC Regional Expansion (Cat 10)**: Uganda/Tanzania exchanges are parked until the Kenya baseline is validated.
*   **Social Media/Sentiment Bridging (Cat 10)**: Focus solely on official filings; third-party "noise" is too high for N=66.
*   **Economic Cycle Modeling (Cat 6)**: Election/Global debt jitter analysis is deferred.

---
**Status**: ACTIVE SPRINT (March 2026)
**Contact**: Antigravity-Audit Agent
