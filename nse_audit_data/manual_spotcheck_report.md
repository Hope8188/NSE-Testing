# Manual Spot-Check Report: Governance Extraction Validation

**Generated:** 2026-03-21 11:21:47

**Corpus Size:** 11 valid annual reports

**Purpose:** Verify that automated governance extraction is citing real text from actual documents.

---

## Top 3 Files for Manual Review (Highest Tunneling Risk)

### 1. NSE-2021-ANNUAL-REPORT-AND-FINANCIAL-STATEMENTS-1.txt.txt

**Corresponding PDF:** `NSE-2021-ANNUAL-REPORT-AND-FINANCIAL-STATEMENTS-1.pdf.pdf`

**Text Length:** 332,181 characters

**Governance Sections Found:** 139

**Tunneling Indicators:** 8

**Governance Section Citations:**

- **Corporate Governance** (line ~25)
  ```
  Nairobi Securities Exchange PLC Integrated Report and Financial Statements 2021
Director's Statement
Corporate Governance Statement
Directors Remuneration
Material Issues
Financial Statements
05 - 06
...
  ```

- **Executive Compensation** (line ~26)
  ```
  Director's Statement
Corporate Governance Statement
Directors Remuneration
Material Issues
Financial Statements
05 - 06
26 - 67
68 - 74
75 - 81
82 - 158...
  ```

- **Corporate Governance** (line ~882)
  ```
  with this, we will continue to engage both public and private institutions to consider blending their capital 
structures, by taking up equity capital which has proven to be critical to their long ter...
  ```

**Tunneling Risk Indicators:**

- **Pattern:** `Due from related party` (line ~4462)
  ```
  67,672
Due from related party
31
12,913...
  ```

- **Pattern:** `related party balances` (line ~9003)
  ```
  1,404
Movement in related party balances
-
-...
  ```

- **Pattern:** `Related Party Transaction` (line ~9076)
  ```
  Notes To The Financial Statements (Continued)
31 Related Party Transactions
The Group and Company are related to various parties by virtue of common shareholding. The shareholders exercise 
significan...
  ```

---

### 2. NSE-Annual-Report-2022-Integrated-Report.txt.txt

**Corresponding PDF:** `NSE-Annual-Report-2022-Integrated-Report.pdf.pdf`

**Text Length:** 346,853 characters

**Governance Sections Found:** 85

**Tunneling Indicators:** 8

**Governance Section Citations:**

- **Risk Management** (line ~81)
  ```
   
 
Enterprise Risk Management Framework  
31 - 32
Value Creation Process  
 
 
33 - 34
Strategy 
 ...
  ```

- **Corporate Governance** (line ~103)
  ```
   
39- 43
Corporate Governance Statement 
 
49 - 57
Corporate Governance Statement
28 - 30
 
Directors’ Remuneration Report  
 ...
  ```

- **Corporate Governance** (line ~106)
  ```
   
49 - 57
Corporate Governance Statement
28 - 30
 
Directors’ Remuneration Report  
 
62 - 67
Statement of Directors’ Responsibilities 
  ...
  ```

**Tunneling Risk Indicators:**

- **Pattern:** `Due from related party` (line ~4824)
  ```
  89,409
Due from related party
12,913
12,913...
  ```

- **Pattern:** `related party balances` (line ~10148)
  ```
  (1,017)
Movement in related party balances
-
-...
  ```

- **Pattern:** `RELATED PARTY TRANSACTION` (line ~10223)
  ```
  ======
32  RELATED PARTY TRANSACTIONS
The following transactions were carried out by the Group and Company with related parties at market rates. 
Group...
  ```

---

### 3. NSE-Annual-Report-2023Interactive.txt.txt

**Corresponding PDF:** `NSE-Annual-Report-2023Interactive.pdf.pdf`

**Text Length:** 331,528 characters

**Governance Sections Found:** 71

**Tunneling Indicators:** 8

**Governance Section Citations:**

- **Corporate Governance** (line ~50)
  ```
  53-56
FINANCIAL PERFORMANCE
CORPORATE GOVERNANCE STATEMENT 	
59-65
DIRECTORS’ REMUNERATION REPORT	
66-69
STATEMENT OF DIRECTORS’ RESPONSIBILITY	
70
INDEPENDENT AUDITOR’S REPORT	
71-73...
  ```

- **Executive Compensation** (line ~52)
  ```
  CORPORATE GOVERNANCE STATEMENT 	
59-65
DIRECTORS’ REMUNERATION REPORT	
66-69
STATEMENT OF DIRECTORS’ RESPONSIBILITY	
70
INDEPENDENT AUDITOR’S REPORT	
71-73
STATEMENT OF PROFIT OR LOSS AND OTHER COMPRE...
  ```

- **Corporate Governance** (line ~1341)
  ```
  & GHG Emissions 
•	
Corporate Governance 
•	
Financial Results 
•	
Business Ethics & Integrity 
•	
Information Security & Data Privacy 
•	...
  ```

**Tunneling Risk Indicators:**

- **Pattern:** `Due from related party` (line ~4691)
  ```
  89,931
Due from related party
33 (f)(i)
30,267...
  ```

- **Pattern:** `related party balances` (line ~9674)
  ```
  (1)
Movement in related party balances
-
-...
  ```

- **Pattern:** `RELATED PARTY TRANSACTION` (line ~9727)
  ```
  0.15
33	 RELATED PARTY TRANSACTIONS
The following transactions were carried out by the Group and Company with related parties at market rates.
 Group...
  ```

---

## Manual Validation Checklist

For each file above:

- [ ] Open the corresponding PDF in a PDF reader
- [ ] Navigate to the approximate page (estimate: line_number / 50 lines per page)
- [ ] Verify the governance section header exists at that location
- [ ] Verify the tunneling indicator text appears in the actual document
- [ ] Confirm the context matches what the extractor found
- [ ] Note any discrepancies (column artifacts, OCR errors, mis-citations)

## Expected Outcomes

✓ **PASS**: Extracted text matches PDF content exactly (allowing for minor formatting differences)

⚠️ **PARTIAL**: Text exists but column artifacts or formatting issues present

✗ **FAIL**: Extracted text does not match PDF (extraction bug, wrong file, or corruption)

## Notes

*Line numbers are approximate. PDF page estimation: divide line number by 40-60 depending on layout density.*

*If more than 2 out of 3 files fail validation, stop and fix extraction pipeline before proceeding.*
