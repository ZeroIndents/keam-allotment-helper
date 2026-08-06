# The KEAM Process — a Deep Guide

This document explains the real-world process that this application mirrors and
how the data on the site relates to it. It is written for anyone (candidates,
parents, developers) who wants to understand *why* the numbers look the way
they do.

> ⚠️ **Source note:** Allotment data and official rules come from the
> Commissioner for Entrance Examinations (CEE), Kerala. Always cross-check the
> live rules against the [official CEE portal](https://cee.kerala.gov.in) before
> making admission decisions. This app is a convenience mirror of published
> allotment lists, not an official source.

---

## 1. What is KEAM?

**KEAM** (Kerala Engineering, Agriculture and Medical) is the state-level
entrance examination conducted by the **Commissioner for Entrance Examinations
(CEE), Government of Kerala**. It is the gateway to:

- **B.Tech** engineering seats across government, government-aided, and
  self-financing colleges in Kerala (including the 50% state-government quota
  seats of self-financing colleges),
- Agriculture, veterinary, pharmacy, and related courses.

The exam is a **computer-based test (CBT)** held in multiple sessions across
several days. Because different sessions use question papers of slightly
different difficulty, raw scores are **normalized** before any rank is computed
(see §3).

---

## 2. Rank preparation — the 50:50 model

The final KEAM engineering merit index is a blend of two components:

| Component | Weight | Scaled to |
|-----------|--------|-----------|
| Normalized KEAM entrance (CBT) score | 50% | **300 marks** |
| Normalized Class 12 (qualifying board) score | 50% | **300 marks** |
| **Total KEAM index** | 100% | **600 marks** |

```
Total Index (out of 600) = Normalized Entrance Score (300) + Normalized Board Score (300)
```

Candidates are ranked by this 600-mark index. That rank is what drives
allotment priority.

---

## 3. The 5:3:2 board-mark normalization

To make marks from different boards (Kerala State Board, CBSE, ISC, NIOS, …)
comparable, the qualifying exam marks are normalized with a **5 : 3 : 2**
weighted ratio across the three core subjects:

| Subject | Weight | Scaled to |
|---------|--------|-----------|
| **Mathematics** | 50% (5 parts) | **150 marks** |
| **Physics** | 30% (3 parts) | **90 marks** |
| **Chemistry** | 20% (2 parts) | **60 marks** |
| *Total board component* | 100% | **300 marks** |

**Subject-substitution rules** (if a subject was not studied):

1. If **Chemistry** was not studied → **Computer Science** marks are substituted.
2. If neither Chemistry nor Computer Science → **Biotechnology** marks.
3. Failing those → **Biology** marks.

This is exactly the formula implemented client-side in the **Rank Predictor**
(`/predictor`): you enter your board marks and predicted entrance score, the
page applies the 5:3:2 weights, computes the 600-mark index, and maps it to an
estimated merit-rank bracket using last year's cutoff distribution.

---

## 4. The Centralised Allotment Process (CAP)

Engineering seats are filled through a structured, publicly documented
**Centralised Allotment Process** run by CEE:

1. **Option entry** — candidates rank their preferred college + course
   combinations.
2. **Trial (mock) allotment** — a non-binding preview so candidates can see
   where they stand and rearrange options before the binding rounds.
3. **Phase 1 allotment** — first binding round. Allottees must pay fees and
   report to college within the deadline, or they forfeit the seat *and*
   remaining options in that stream.
4. **Phase 2 allotment** — fills vacated seats and processes **upgrades**:
   candidates who already hold a seat move up to higher-priority options
   automatically when a seat frees up.
5. **Phase 3 and later rounds** — further mop-up rounds (Phase 3, mop-up,
   stray-vacancy) to fill whatever remains. Each round is published first as a
   **provisional list**, opened for objections for a short window, then
   finalized.

This site indexes **Phase 1, Phase 2, and Phase 3** final lists. Provisional /
trial lists are excluded by default so that "the numbers on the site" always
mean *binding* allotments.

### How to read a row

Each row in the Allotment Finder (`/`) is one candidate seat allotment:

| Field | Meaning |
|-------|---------|
| Register No. / Appl. No. | Candidate's KEAM registration/application number |
| Rank | Candidate's KEAM merit rank |
| Category | Reservation category code (see §5) |
| College | The college allotted (`TVE - College of Engineering, Thiruvananthapuram` …) |
| Course | The branch allotted (`CS - Computer Science & Engineering` …) |
| Seat type | Usually `SM` (State Merit quota) |

Because CEE changes the PDF layout every year, the parser (see
`docs/DATA_PIPELINE.md`) normalizes each column against a dictionary of header
synonyms and the master `KEAM_COLLEGES` / `KEAM_COURSES` code tables in
`app.py`.

---

## 5. Reservation categories

Within the government-controlled quota, seats are distributed per Kerala
government reservation norms:

| Code | Category | % of quota |
|------|----------|-----------|
| **SM** | State Merit (open, all communities) | 50% |
| **SEBC** | Socially & Educationally Backward Classes (umbrella) | 30% |
| **SC** | Scheduled Castes | 8% |
| **ST** | Scheduled Tribes | 2% |
| **EWS** | Economically Weaker Sections | as per norms |
| **PD** | Persons with Disabilities (≥40% benchmark) | 5% (horizontal) |

**SEBC sub-categories** (the 30% is split):

| Code | Community | % |
|------|-----------|----|
| EZ | Ezhava (incl. Thiyya, Billava, …) | 9% |
| MU | Muslim | 8% |
| BH | Other Backward Hindu | 3% |
| LA | Latin Catholic & Anglo Indian | 3% |
| DV | Dheevara & related | 2% |
| VK | Viswakarma & related | 2% |
| KN | Kusavan & related | 1% |
| BX | Other Backward Christian | 1% |
| KU | Kudumbi | 1% |

**Dual competitiveness:** reserved-category candidates compete in **both** the
State Merit list and their community list. If they win a seat on State Merit,
their community-quota seat stays open for the next candidate in that category.

The **Statistics** dashboard's *Category Spread* chart plots the best / average
/ worst (closing) rank per category code — this is what the `candidate_category`
column in the database maps to.

---

## 6. Seat types in self-financing colleges

In **self-financing** engineering colleges, seats split into:

- **State Government Quota — 50%** (filled by CEE through KEAM CAP; these are
  the rows you see on this site),
- **Management Quota — 35%** (filled by the college),
- **NRI Quota — 15%** (filled by the college).

Government and aided colleges fill **100%** of their seats through CAP. The
`seat_type` column in the database is the quota type recorded in the official
allotment PDF (`SM` for State Merit; other codes appear where the PDF records
them).

---

## 7. Glossary of codes used on the site

- **College codes** — three-letter codes used by CEE in allotment tables,
  e.g. `TVE` = College of Engineering, Thiruvananthapuram; `FIT` = Federal
  Institute of Science and Technology; `MEC` = Model Engineering College.
  The full mapping (~140 colleges) lives in `KEAM_COLLEGES` in `app.py`.
- **Course codes** — two-letter branch codes, e.g. `CS` = Computer Science &
  Engineering, `EC` = Electronics & Communication, `ME` = Mechanical
  Engineering, `CE` = Civil, `EE` = Electrical & Electronics, `AH` = Artificial
  Intelligence and Machine Learning, etc. Full mapping in `KEAM_COURSES`.
- **Phase codes** — `Phase1`, `Phase2`, `Phase3` (binding rounds).
- **Category codes** — see §5.
