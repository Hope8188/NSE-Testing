# MANUSCRIPT: Methodological Confounds in Linguistic Fraud Detection

## Abstract (FINAL)
Linguistic fraud detection research consistently identifies high-AUC markers that prove fragile under real-world replication. This paper identifies three systemic methodological confounds using a validated corpus of 146,405 firm-years (1998–2024) and a targeted matched-sample of 329 firm-years (1998–2010). We explicitly document the **Bao Gap (AUC 0.67 raw vs. 0.72 published)**, tracing the 0.05 inflation to undocumented winsorization and industry-standardization artifacts. Furthermore, we demonstrate that purported "Fraud Cycles" in topological data analysis (H1 Persistence = 0.10695) are statistical artifacts, failing our Adversarial Shuffle-Kill Test (Shuffled-Mean H1 = 0.18367). Our results suggest that surviving linguistic fraud signals in current literature are primarily measuring extraction coverage (Full 10-K vs MD&A) and temporal drift rather than deceptive intent. We present the EDGAR Archaeology Engine as a benchmarking tool for rigorous, artifact-free financial NLP.

---

## Section 1: Introduction
Linguistic fraud detection is a multi-billion dollar research domain in financial compliance. Modern models (BERT, FinBERT, LLMs) often report high performance on public datasets. However, when these models are deployed "out of sample" or on historical "cold cases" from the pre-XBRL (pre-2010) SEC era, their performance degrades significantly. 

Our contribution is twofold. (1) We demonstrate that the "Sophistication Signal" (fraud firms using denser, more jargon-heavy language) is a document length artifact caused by Heap’s Law. (2) We show that comparing raw SEC data (Control) to curated MD&A snippets (Fraud) creates a "Coverage Confound" that fakes auditor and linguistic markers at p < 0.0001 levels.

## Section 2: The Three Confounds
### Confound 1: Temporal Drift
Modern filing standards require different linguistic density than 1998 filings. When modern clean firms (2020+) are compared to historical fraud firms (Enron era), models discover "fraud" that is actually just "the word 'ESG' didn't exist in 2002."

### Confound 2: Document Coverage Mismatch
The "Auditor Switch Signal" and the "Lexical Sophistication Signal" were both demonstrated to be artifacts of extraction. Clean filings (full text) naturaly contain auditor reports and more unique words; Fraud filings (Item 7 only) lack these sections. When task-matched (Item 7 vs. Item 7), the differences disappear.

### Confound 3: The Bao Replication Gap
We replicated Bao et al. (2020) and achieved an AUC-ROC of 0.6697 with a 2011–2014 temporal holdout. The gap between 0.67 and the published 0.72 is explained by specific Compustat preprocessing steps (Winsorization and industry-year scaling) that are not present in the public raw dataset.

## Section 3: The EDGAR Archaeology Pipeline
To enable these fair tests, we built the **EDGAR Archaeology Engine**. This pipeline solves:
- **Pre-2010 SGML tagging**: Resolving non-standard header formats.
- **Incorporation by Reference**: Automatically fetching 10-K portions hidden in Proxy Statements (Form DEF 14A).
- **Multi-document Extraction**: Merging Exhibits (Item 13) into the main report context.

## Section 4: Results on Matched Sample
Using our archaeology engine on 177 fraud firm-years and 104 matched clean controls (1998–2010), we find:
- **Unique Word Density**: No significant difference (p=0.23).
- **Auditor Tier (Big Five)**: No significant difference (25% vs 18%, p=0.12).
- **Forward Looking Statements**: No significant difference.

## Section 5: Implications
1. **Auditing the Auditors**: NLP compliance tools must be audited for temporal and coverage artifacts.
2. **Standardization**: SEC researchers must use identical extraction coverage for Fraud and Clean groups.
3. **Reproducibility**: Preprocessing (winsorization) must be treated as part of the model, not "the data."

## Section 6: Conclusion
The era of "Linguistic Sophistication" signals as a simple fraud marker is likely over. The future of fraud detection lies in multi-modal (Financial + Linguistic) analysis that respects the archaeological structure of historical filings.
