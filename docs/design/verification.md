# Verification log for payroll calculations

The repository has no test suite (the owner's choice). Money logic is still proved: every change to a payroll or statutory calculation is checked against the official reference cases below **before it is committed**, and the check is recorded in the log at the end of this page.

## Rule

1. Identify the calculations the change can affect (its blast radius).
2. Run those cases against the code, ad hoc, from a Python shell or a throwaway script that is not committed.
3. Compare to the cent with the expected values here. A difference is a defect: fix it, or prove the reference wrong from its official source.
4. Add one log row per case run, with the commit the result belongs to. Never mark a case passed without running it.
5. When official rules change, add the new case with its source and effective date. Keep the old case; it still governs payroll for past periods.

Sources and full rules are in [statutory-rules-2026.md](statutory-rules-2026.md). Items it marks as unconfirmed (its §0) have no expected value until they are confirmed.

## Reference cases

### Singapore

| ID | Case | Expected | Source |
| --- | --- | --- | --- |
| SG-CPF-1 | Age 55 or below, Table 1 (SC / SPR 3rd year+). OW $9,000 every month; AW $12,000 (Jan), $10,000 (Jun), $78,000 (Dec). OW ceiling $8,000 | Each month on OW: total $2,960, employee $1,600, employer $1,360. Estimated AW ceiling leaves $6,000 of January AW subject: total $2,220, employee $1,200, employer $1,020. January as one computation: 37% × $14,000 = total $5,180, employee $2,800, employer $2,380. June and December AW: no CPF | CPF Board, *Examples for computation of AW ceiling* (2026), example 1 |
| SG-CPF-2 | Rounding: total to the nearest dollar (50 cents up); employee share has cents dropped; employer = total − employee | Applied in SG-CPF-1 | CPF Board contribution rates; statutory-rules-2026.md §1 |
| SG-SDL-1 | SDL at 0.25% of total wages, minimum $2, maximum $11.25 | $609.50 → $2.00; $2,000 → $5.00; $4,500, $4,502.03 and $10,000 → $11.25 each; employer total $40.75 → $40.00 (rounded down to the dollar) | CPF Board, *How do I calculate and pay SDL* (updated 1 Jul 2026) |
| SG-SHG-1 | MBMF splits each contribution between Mosque & Religious Education and Mendaki | $3.00 = $1.75 + $1.25. Wages of exactly $1,000 fall in the "$1,000 or less" band (CPF Board wording) | CPF Board SHG page (updated 22 Sep 2026); MUIS |
| SG-FWL-1 | Daily levy for partial months | S Pass $650 a month → $21.37 a day; Services Tier 1 basic-skilled $450 → $14.80 a day | MOM; statutory-rules-2026.md §4 |

### Malaysia

| ID | Case | Expected | Source |
| --- | --- | --- | --- |
| MY-EPF-1 | Wages up to RM20,000: contribution from the Third Schedule band, not from actual wages. Each share = rate × band upper limit, rounded up to the ringgit (RM20 bands to RM5,000, then RM100 bands) | Matches every row of Parts A, C and E of the 1 Oct 2025 schedule (401 rows each) | KWSP Third Schedule (1 Oct 2025); checked 2026-10-21 |
| MY-EPF-2 | Wages above RM20,000: percentage of actual wages, total rounded up to the ringgit. RM21,250 (Part A: 12% / 11%) | 2,550.00 + 2,337.50 = 4,887.50 → total RM4,888 | KWSP mandatory contribution page, example 2.1 |
| MY-EPF-3 | Part F non-citizen, 2% + 2% | Open item O1: KWSP FAQ Q23 gives RM1,751 → RM36 + RM36 (each share rounded up); example 2.4 gives RM6,710 → 268.40 → total RM269. No expected value until KWSP confirms | KWSP non-citizen FAQ; statutory-rules-2026.md §0 |
| MY-PCB-1 | EPF split for PCB: RM2,400 salary + RM3,600 bonus, EPF RM660 | K1 = 264 (EPF on normal remuneration), Kt = 396 | LHDN MTD 2026 specification, E13 |
| MY-PCB-2 | LHDN worked example, January to April including a bonus month | Use the specification's figures, as reproduced in statutory-rules-2026.md §8 | LHDN MTD 2026 specification |
| MY-PCB-3 | Non-resident: 30% of remuneration after exempt items | RM3,000 → RM900 | LHDN MTD 2026 specification, D |
| MY-PCB-4 | Final rounding: truncate to 2 decimals, round up to 5 sen, then apply the RM10 rule | Applied in MY-PCB-2 | LHDN MTD 2026 specification |

SOCSO, EIS and HRD Corp cases are added when their engine is built. They come from the PERKESO tables (65 rows, including the employee-only 0.75% LINDUNG 24 Jam contribution from 1 Jun 2026) and HRD Corp's rates.

## Log

| Date | Commit | Case | Result | Notes |
| --- | --- | --- | --- | --- |
| 2026-10-21 | research | SG-CPF-1, SG-SDL-1, MY-EPF-1, MY-PCB-2 | pass (formulas) | The statutory research reproduced each official example from its documented formulas. No engine code exists yet. |
