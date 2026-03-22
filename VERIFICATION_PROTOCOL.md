# MSQECC Vault: Technical Verification Protocol
**Author**: Professor Malcontent
**Status**: ACTIVE - Hard Guidelines for Project Integrity

To prevent the recurrence of "hallucinated breakthroughs" and "academic hype," all research in this vault MUST now adhere to the following strict verification rules. Failure to comply will result in an automatic "AUDIT FAIL" and subsequent purging of the affected module.

## 1. The Comparison Mandate
- No quantum fidelity result (e.g., "96.8%") may be reported without a direct comparison to the current **State-of-the-Art (SOTA)** frontier (e.g., IonQ 99.99% / IBM 99.5%). 
- You MUST specify the type of fidelity: **Gate**, **State**, or **Process**. Mislabeling state fidelity as a gate breakthrough is prohibited.

## 2. Statistical Thresholds
- **Sample Size ($n$)**: No statistical claim (TDA, PCA, Manifold Learning) is valid if $n < 500$ for the SPARC dataset or $n < 10,000$ for synthetic sets.
- **Dimensional Inflation Check**: Any TDA topological feature (H1, H2) discovered in $D \ge 3$ dimensions MUST be tested against an **Adversarial Permutation Audit (Shuffle-Kill Test)**. 
- **The Shuffle Rule**: Persistent homology features are considered **False Positives** if the Shuffled-Mean Persistence (Monte Carlo) is $\ge$ the Original Persistence.
- **The 5-Sigma Rule**: The label "Breakthrough" is reserved EXCLUSIVELY for findings with a statistical significance $> 5\sigma$.

## 3. Simulation & Mock Data Guardrails
- Scripts using "Mock Data" (simulated points) MUST print a header: `*** PRE-CALIBRATION ONLY - NOT A PHYSICAL FINDING ***`. 
- Results derived from hardcoded simulation biases (e.g., $D = 1.2 + 0.3*fgas$) MUST be labeled as "Tautological Verification" and never "Discovery."

## 4. Hardware Integrity
- All quantum runs must include a **Baseline Shot Test**. If the baseline noise exceeds 1%, the algorithmic "finding" is invalidated.
- State Tomography is required for any claim regarding "Logical Entanglement." Individual bit-counts are insufficient.

## 5. Adversarial Audit Trail
- Every "Finding" must be accompanied by an "Adversarial Kill Attempt" log—documenting at least three ways the data might be lying to you.

---
**Enforcement**: As of March 18, 2026, the vault is in a "CLEAN" state. No further hype is permitted. 
