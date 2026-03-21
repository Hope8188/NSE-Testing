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

---
**Status**: ACTIVE SPRINT (March 2026)
**Contact**: Antigravity-Audit Agent
