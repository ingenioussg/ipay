# Statutory payroll rules in force on 2026-10-21: Singapore and Malaysia

Status: researched 2026-10-21 for the calculation engine, from official sources only (CPF Board, Singapore Statutes Online, SWDA, MOM, CDAC, MUIS, SINDA and the Eurasian Association; KWSP, PERKESO, LHDN/HASiL and HRD Corp). Each table and formula names its source URL and date next to it: `eff.` is the effective date, `upd.` the page's own "last updated" date, and `ret.` means the page shows no date and was read on 2026-10-21. Section 0 lists every point that official sources leave open or contradict. The engine must not hard-code a guess for any of them.

Rounding helpers used below:

| Helper | Meaning |
| --- | --- |
| `round_half_up_dollar(x)` | to the nearest dollar: under 50 cents down, 50 cents and above up |
| `floor_dollar(x)` | drop the cents |
| `ceil_ringgit(x)` | any sen at all: up to the next whole ringgit |
| `trunc2(x)` | keep 2 decimals and drop the rest (123.4534 → 123.45) |
| `ceil_5sen(x)` | 1-4 sen → 5 sen, 6-9 sen → 10 sen (287.02 → 287.05, 152.06 → 152.10) |

## 0. Open points (confirm before go-live)

| # | Point | What the official sources say | Engine action |
| --- | --- | --- | --- |
| O1 | EPF rounding where the percentage method applies (Part F non-citizens; any wages above RM20,000): is each share rounded up, or only the total? | KWSP non-citizen FAQ Q23: RM1,751 × 2% = 35.02, "rounded up to the next whole ringgit" = RM36 for the employer and RM36 for the employee (total RM72). KWSP mandatory-contribution page, Example 2.4: RM6,710 × 2% = 134.20 + 134.20 = 268.40 → total RM269; Example 2.1: RM21,250 → 2,550.00 + 2,337.50 = 4,887.50 → total RM4,888. Neither page says how a rounded total is split, yet KWSP says contributions are paid "only in ringgit ... without any cent value". Third Schedule text: "The total contribution which includes cents shall be rounded to the next ringgit." Sources: §5. | Make it a setting. Confirm with KWSP (03-8922 6000) or with a test upload in i-Akaun (Employer) |
| O2 | EPF bonus rule (Parts A and C) | Schedule note: when an employee on monthly wages of RM5,000 or less gets a bonus that lifts the month's wages above RM5,000, "the employer's contribution shall be calculated at the rate of 13% [Part C: 6.5%] of the amount of wages for the month", total rounded up to the next ringgit. It does not say whether this is 13% of actual wages or of the band's upper limit, and KWSP forbids exact-percentage calculation below RM20,000. | Confirm with KWSP |
| O3 | Which month switches rates at age 60: EPF (Part A → C or E), SOCSO (first → second category) and EIS (stops) | No KWSP or PERKESO page found states whether the switch is the birthday month or the following month. The Singapore CPF rule (1st day of the month after the birthday) is CPF-only. | Confirm with KWSP and PERKESO |
| O4 | Does the employee's LINDUNG 24 Jam (NEI) share count towards the RM350 SOCSO tax relief (TP1 item C14)? | TP1 2026 notes cover contributions "under ... Act 4 or ... Act 800"; NEI sits in Act 4 (amended by Act A1788), but no LHDN text says so explicitly. | Use the TP1 claim amount; confirm with LHDN |
| O5 | EPF Form A upload layout | KWSP e-Caruman FAQ (19 May 2017): CSV or TXT layouts must be approved by EPF. The only public layout is the June 2020 CSV guide (§10.4), which predates passport-based members (October 2025). | Ask KWSP for the current TXT/CSV specification |
| O6 | SDL payment channel for foreign employees | CPF Board: "For foreign employees only: Pay SDL directly to the Skills and Workforce Development Agency (SWDA)". SWDA's SDL page sends regular SDL payment through CPF EZPay. | Channel only; the amount is computed the same way |
| O7 | Malaysian year-end forms | LHDN form-download PDFs returned HTTP 404 on 2026-10-21. EA fields in §10.1 are from C.P.8A Pin. 2023 (the latest copy that opened); the Form E Part A fields come from LHDN's Form E 2025 sample as shown by the search index, not opened directly. The C.P.8D layout (Pin. 2025) was read directly. | Re-check when building year-end |
| O8 | Malaysian resident tax rates for YA 2026 | LHDN's rate page (upd. 26/06/2026) lists YA 2023-2025 only. The MTD 2026 specification (Table 1, §8.3) uses the same schedule. | Use the MTD 2026 Table 1 for 2026 payroll |
| O9 | CDAC for part months | CDAC: "The employer shall pro-rate the contribution based on the gross wages paid to the employee for that period." Whether this means "look up the band on the wages actually paid" or "prorate the flat amount" is not stated. | Confirm with CDAC |
| O10 | ECF threshold | ECF FAQ (upd. September 2022): contribute "as long as you are contributing to CPF ... if you earn more than $200 monthly". CPF's ECF table has no minimum and CPF now starts above $50. | Use the CPF table; confirm with the Eurasian Association |

## Singapore

### 1. CPF

#### 1.1 Which rate table

| Employee | Table |
| --- | --- |
| Singapore Citizen; SPR from the 3rd year | 1 |
| SPR 1st year, graduated employer and employee (G/G, the default) | 2 |
| SPR 2nd year, G/G | 3 |
| SPR 1st or 2nd year, joint application for full employer and full employee rates | 1 |
| SPR 1st year, joint application for full employer and graduated employee (F/G) | 4 |
| SPR 2nd year, F/G | 5 |

SPR year: the 1st year begins on the day of SPR conversion; the 2nd year on the first day of the month after the first anniversary of conversion; the 3rd year on the first day of the month after the second anniversary.

Age: "New contribution rates apply from the first day of the month after the employee's 55th, 60th, 65th or 70th birthday."

Source: <https://www.cpf.gov.sg/employer/employer-obligations/how-much-cpf-contributions-to-pay> (upd. 19 Oct 2026).

#### 1.2 Rates and wage bands

Tables apply to private-sector and non-pensionable employees. For total wages (TW) above $750, contributions are `t%` (total) and `e%` (employee) of capped OW plus `t%` and `e%` of AW. `Max t` and `Max e` are the caps on the OW part (rate × $8,000). For TW of $750 or less:

| TW for the month | Total | Employee |
| --- | --- | --- |
| $50 or less | nil | nil |
| over $50 to $500 | `r%` × TW | nil |
| over $500 to $750 | `r%` × TW + `f` × (TW − 500) | `f` × (TW − 500) |

| Table | Age | t% | e% | er% (t − e) | Max t ($) | Max e ($) | r% | f |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 55 and below | 37 | 20 | 17 | 2,960 | 1,600 | 17 | 0.6 |
| 1 | above 55 to 60 | 34 | 18 | 16 | 2,720 | 1,440 | 16 | 0.54 |
| 1 | above 60 to 65 | 25 | 12.5 | 12.5 | 2,000 | 1,000 | 12.5 | 0.375 |
| 1 | above 65 to 70 | 16.5 | 7.5 | 9 | 1,320 | 600 | 9 | 0.225 |
| 1 | above 70 | 12.5 | 5 | 7.5 | 1,000 | 400 | 7.5 | 0.15 |
| 2 | 55 and below | 9 | 5 | 4 | 720 | 400 | 4 | 0.15 |
| 2 | above 55 to 60 | 9 | 5 | 4 | 720 | 400 | 4 | 0.15 |
| 2 | above 60 to 65 | 8.5 | 5 | 3.5 | 680 | 400 | 3.5 | 0.15 |
| 2 | above 65 | 8.5 | 5 | 3.5 | 680 | 400 | 3.5 | 0.15 |
| 3 | 55 and below | 24 | 15 | 9 | 1,920 | 1,200 | 9 | 0.45 |
| 3 | above 55 to 60 | 18.5 | 12.5 | 6 | 1,480 | 1,000 | 6 | 0.375 |
| 3 | above 60 to 65 | 11 | 7.5 | 3.5 | 880 | 600 | 3.5 | 0.225 |
| 3 | above 65 | 8.5 | 5 | 3.5 | 680 | 400 | 3.5 | 0.15 |
| 4 | 55 and below | 22 | 5 | 17 | 1,760 | 400 | 17 | 0.15 |
| 4 | above 55 to 60 | 21 | 5 | 16 | 1,680 | 400 | 16 | 0.15 |
| 4 | above 60 to 65 | 17.5 | 5 | 12.5 | 1,400 | 400 | 12.5 | 0.15 |
| 4 | above 65 to 70 | 14 | 5 | 9 | 1,120 | 400 | 9 | 0.15 |
| 4 | above 70 | 12.5 | 5 | 7.5 | 1,000 | 400 | 7.5 | 0.15 |
| 5 | 55 and below | 32 | 15 | 17 | 2,560 | 1,200 | 17 | 0.45 |
| 5 | above 55 to 60 | 28.5 | 12.5 | 16 | 2,280 | 1,000 | 16 | 0.375 |
| 5 | above 60 to 65 | 20 | 7.5 | 12.5 | 1,600 | 600 | 12.5 | 0.225 |
| 5 | above 65 to 70 | 14 | 5 | 9 | 1,120 | 400 | 9 | 0.15 |
| 5 | above 70 | 12.5 | 5 | 7.5 | 1,000 | 400 | 7.5 | 0.15 |

Tables 2 and 3 have one band "above 65"; Tables 1, 4 and 5 split at 70. The graduated (G/G) rates are unchanged since 1 January 2016.

Source: CPF Board, "CPF Contribution Rate Tables from 1 January 2026", Tables 1-5, <https://www.cpf.gov.sg/content/dam/web/employer/employer-obligations/documents/CPFcontributionratesfrom1Jan2026.pdf> (eff. 1 Jan 2026; PDF dated 29 Dec 2025).

#### 1.3 Ceilings, OW and AW

| Item | Rule | Source |
| --- | --- | --- |
| OW ceiling | $8,000 a month from 1 Jan 2026. History: $6,000 (1 Jan 2016 to 31 Aug 2023), $6,300 (1 Sep to 31 Dec 2023), $6,800 (2024), $7,400 (2025) | <https://www.cpf.gov.sg/service/article/what-is-the-ordinary-wage-ow-ceiling> (upd. 14 Aug 2026); rate-table PDF notes |
| Annual salary ceiling | $102,000 (OW + AW) | same |
| OW | wages "given to an employee for their employment in that month" and "payable by the 14th of the following month" | <https://www.cpf.gov.sg/employer/employer-obligations/what-constitutes-wages-for-cpf-contributions> (upd. 06 Oct 2026) |
| AW | wages that are not OW, for example bonuses | same |
| AW ceiling | $102,000 − total OW subject to CPF for the year; per employee, per employer, per calendar year; applies to SCs and SPRs. The AW ceiling of the year in which the AW is due and payable applies (a 2025 bonus payable in 2026 uses 2026) | same; CPF "Examples for computation of AW ceiling" (2026), <https://www.cpf.gov.sg/service/sfc/servlet.shepherd/document/download/069IW00000MoFDuYAN> (ret.) |

AW ceiling procedure (CPF examples PDF above):

1. At every AW payment, estimate the AW ceiling from the current year's estimated monthly OW (a full year at or above the OW ceiling gives $102,000 − $8,000 × 12 = $6,000).
2. In the last month of employment or in December, whichever is earlier, recompute the AW ceiling from the actual OW subject to CPF. Pay any shortfall with that month's contributions; apply online for a refund of any excess.

#### 1.4 Algorithm and rounding

```text
# per employee, per employer, per calendar month
table  = table_for(residency, spr_year(month), spr_option)           # 1.1
band   = age_band(dob, month)        # changes on the 1st of the month AFTER the 55th/60th/65th/70th birthday
t, e, r, f = rates(table, band)      # 1.2; percentages as fractions (37% → 0.37)
OW_s   = min(OW, 8000)
AW_s   = min(AW, max(0, aw_ceiling_estimate - AW_subject_so_far_this_year))   # 1.3
TW     = OW_s + AW_s             # CPF: "apply the wage ceilings to determine Total Wages"
if   TW <= 50:  total = 0;                          ee = 0
elif TW <= 500: total = r * TW;                     ee = 0
elif TW <= 750: total = r * TW + f * (TW - 500);    ee = f * (TW - 500)
else:           total = t * OW_s + t * AW_s;        ee = e * OW_s + e * AW_s
total = round_half_up_dollar(total)  # round the OW + AW sum once, never each part
ee    = floor_dollar(ee)
er    = total - ee
```

Rounding steps as printed under every rate table: "1) Compute the total CPF contribution (rounded to the nearest dollar), i.e., to be rounded down for an amount less than 50 cents and rounded up for an amount of 50 cents and above. 2) Compute the employee's share of CPF contribution (rounded down to the nearest dollar). 3) Employer's share = Total contribution - Employee's share. 4) ... If there are OW and AW payable for the same month, compute and sum up the CPF contributions that are payable for OW and AW and apply the rounding rules accordingly." The CPF page cited in §1.1 also says: "The cents should always be dropped for the employee's share of CPF contributions."

Test case (CPF AW examples PDF, example 1, 2026): age 55 or below, Table 1, OW $9,000 a month, AW $12,000 in January, $10,000 in June and $78,000 in December. OW subject $8,000 → total $2,960, employee $1,600, employer $1,360 each month. Estimated AW ceiling $6,000, so January AW subject is $6,000 → total $2,220, employee $1,200, employer $1,020. January in one computation: total 37% × $14,000 = $5,180, employee $2,800, employer $2,380. The June and December AW attract no CPF.

Announced but not in force on 2026-10-21: from 1 January 2027, above 55 to 60 goes to 35.5% (employer 16.5%, employee 19%) and above 60 to 65 to 26% (13% and 13%); other bands unchanged. The 2027 phase-in factors for $500-750 wages are not given. Source: <https://www.cpf.gov.sg/conrate2023> (upd. 09 Jun 2026).

### 2. Skills Development Levy (SDL)

| Rule | Value | Source |
| --- | --- | --- |
| Rate | 0.25% of the employee's wages for the month; "wages" means remuneration in money, including any bonus | SDL Act 1979, s3(1)(a) and s2, version current at 21 Oct 2026, <https://sso.agc.gov.sg/Act/SDLA1979> (s3 last amended by Act 4 of 2023, eff. 15 Jun 2023) |
| Minimum | the greater of 0.25% and $2, per employee per month | s3(1)(b) |
| Ceiling | not chargeable on wages above $4,500 a month, so the maximum is $11.25 | s3(2) |
| Who | every employee rendering services wholly or partly in Singapore in the month (locals and foreigners), excluding a domestic servant, gardener or chauffeur employed by an individual otherwise than for business | s2 |
| Rounding | compute per employee (keep cents), add up, round the total down to the nearest dollar. CPF example: $609.50 → $2.00; $2,000 → $5.00; $4,500, $4,502.03 and $10,000 → $11.25 each; total $40.75 → $40.00 | <https://www.cpf.gov.sg/service/article/how-do-i-calculate-and-pay-the-skills-development-levy-sdl> (upd. 1 Jul 2026) |
| Administrator | the Skills and Workforce Development Agency (SWDA), formed from SSG and WSG, from 1 Jul 2026 | SDL Act s2 as amended by Act 17 of 2026 (eff. 1 Jul 2026) |
| Payment | local employees: with CPF contributions to CPF Board. Foreign employees: see O6 | CPF article above; <https://www.ourworkforce.gov.sg/e-services/skills-development-levy> (ret.) |

```text
sdl_i   = max(2.00, 0.0025 * min(wages_i, 4500))          # per employee, cents kept
sdl_due = floor_dollar(sum(sdl_i for the employer's submission))
```

### 3. Self-help group (SHG) funds

Monthly amounts by the employee's total wages for the month. "Over A to B" means above A, up to and including B.

| Fund (effective) | Bands: up to and including $X → amount; last band is "over" |
| --- | --- |
| CDAC (1 Jan 2015) | 2,000 → $0.50; 3,500 → $1.00; 5,000 → $1.50; 7,500 → $2.00; over 7,500 → $3.00 |
| ECF (revised 2015) | 1,000 → $2; 1,500 → $4; 2,500 → $6; 4,000 → $9; 7,000 → $12; 10,000 → $16; over 10,000 → $20 |
| MBMF (1 Jun 2016) | 1,000 → $3.00; 2,000 → $4.50; 3,000 → $6.50; 4,000 → $15.00; 6,000 → $19.50; 8,000 → $22.00; 10,000 → $24.00; over 10,000 → $26.00 |
| SINDA (January 2015) | 1,000 → $1; 1,500 → $3; 2,500 → $5; 4,500 → $7; 7,500 → $9; 10,000 → $12; 15,000 → $18; over 15,000 → $30 |

Source: CPF Board, <https://www.cpf.gov.sg/employer/employer-obligations/contributions-to-self-help-groups> (upd. 22 Sep 2026). Cross-checked against: CDAC <https://www.cdac.org.sg/cdac-funding-info> (ret., "effective 1 January 2015"); ECF FAQ <https://www.eurasians.sg/s/ECF-FAQ.pdf> (upd. September 2022, "since 2015"); MUIS <https://www.muis.gov.sg/give-back/mbmf/employer-information/> (page upd. 21 Feb 2025, "wages earned from 1 June 2016"; MBMF splits each amount between Mosque and Religious Education and Mendaki, e.g. $3.00 = $1.75 + $1.25); SINDA <https://www.sinda.org.sg/donate/sindafundcontribution/> (ret.) and <https://www.sinda.org.sg/newsroom/fund-contribution/> (30 Aug 2014, "from January 2015 onwards"). MUIS prints the first MBMF band as "< $1,000" and the next as "> $1,000 to $2,000", leaving exactly $1,000 undefined; CPF prints "$1,000 or less". Use CPF.

| Fund | Who contributes | Basis | Opt-out and changes |
| --- | --- | --- | --- |
| CDAC | Chinese SCs and SPRs; not those working overseas | race on the NRIC; double-barrelled race uses the first component (Chinese-Indian → CDAC; Indian-Chinese → SINDA) | Opt-out form endorsed by the employer; the employer may stop deducting once the form is sent to CDAC. Per employment, so a new job needs a new form. Source: <https://www.cdac.org.sg/cdac-funding-info-information-for-employers> (ret.) |
| ECF | Eurasian SCs and SPRs ("Eurasian" as on the identity card, or of European and Asian ancestry) | race | Deducted "unless they opt out"; the employee may raise the amount but may not go below the minimum; one deduction per employer. Source: ECF FAQ |
| MBMF | all Muslim employees: SCs, SPRs and foreign employees | religion | Change Application Form to MUIS to raise, lower or opt out of any of the three components; MUIS confirms by certificate within two weeks; the employee then tells the employer. Source: MUIS page |
| SINDA | employees of Indian descent (including "all people originating from the Indian sub-continent") who are SCs, SPRs or Employment Pass holders, including part-time, casual and temporary staff and salaried directors | race | Digital notification form, the only accepted channel since 27 October 2025, notifies SINDA and the employer; to resume, the employee tells HR. With several employers, contributions are payable through each unless the employee opts to contribute through one. Source: SINDA page |

A Chinese Muslim contributes to CDAC and MBMF; an Indian Muslim to SINDA and MBMF. Either fund may be opted out of (CDAC annex; MUIS page).

Wage basis: CDAC uses "gross wages of the employee received in the month", including overtime, allowances, commission and bonuses, with no minimum wage threshold. MBMF uses "all monetary remuneration", including bonus and AWS but not termination benefits. SINDA uses "total gross income earned in a calendar month". ECF uses "the same monthly salary as that used to compute CPF liability". No source caps SHG wages at the CPF OW ceiling.

```text
for fund in funds_for(race_on_nric, religion, residency_and_pass):
    if opted_out(employee, fund): continue
    amount = custom_amount(employee, fund) or band_lookup(fund, total_wages_this_month)
```

### 4. Foreign worker levy (FWL)

FWL is billed to the employer by MOM; payroll needs it only for costing and reconciliation.

| Rule | Value | Source |
| --- | --- | --- |
| Liability | from the day the Work Permit (or Temporary Work Permit, whichever is earlier) or S Pass is issued until it is cancelled or expires | <https://www.mom.gov.sg/passes-and-permits/work-permit-for-foreign-worker/foreign-worker-levy/what-is-the-foreign-worker-levy> (upd. 1 Jul 2026); <https://www.mom.gov.sg/passes-and-permits/s-pass/quota-and-levy/levy-and-quota-requirements> (upd. 19 Feb 2026) |
| Part month | "The daily levy rate only applies to Work Permit holders who did not work for a full calendar month"; daily rate = (monthly levy rate × 12) / 365, rounded up to the nearest cent | <https://www.mom.gov.sg/passes-and-permits/work-permit-for-foreign-worker/sector-specific-rules/services-sector-requirements> (upd. 16 Sep 2026); S Pass page |
| Examples | S Pass $650 a month in all sectors and tiers since 1 Sep 2025 → daily $21.37; Services Tier 1 basic-skilled $450 → $14.80; Services Tier 1 higher-skilled $300 → $9.87 | same pages |
| Billing | the bill is viewable on the 3rd working day of each month; the levy for each month is deducted by GIRO on the 17th of the following month (next working day if that is a weekend or public holiday) | <https://www.mom.gov.sg/passes-and-permits/work-permit-for-foreign-worker/foreign-worker-levy/paying-the-levy> (upd. 8 Jul 2026) |
| Rates | by pass type, sector, quota tier and basic or higher skill. Take them from MOM's sector pages: construction, manufacturing, marine shipyard, process and services, all under <https://www.mom.gov.sg/passes-and-permits/work-permit-for-foreign-worker/sector-specific-rules/> | WP levy overview (upd. 1 Jul 2026) |

Announced, not in force: from 2028 Services Tiers 1 and 2 merge (higher-skilled $400, basic-skilled $600), timeline to be announced (services page).

## Malaysia

### 5. EPF (KWSP)

#### 5.1 Parts of the Third Schedule

| Part | Employees | Age | Employer | Employee |
| --- | --- | --- | --- | --- |
| A | Malaysian citizens; permanent residents; non-citizens who elected to contribute before 1 Aug 1998 | below 60 | 13% if wages ≤ RM5,000; 12% if above | 11% |
| C | permanent residents; non-citizens who elected before 1 Aug 1998 | 60 and above | 6.5% if wages ≤ RM5,000; 6% if above | 5.5% |
| E | Malaysian citizens | 60 and above | 4% | 0% |
| F | non-Malaysian citizens (not in A or C) | any, up to 75 | 2% | 2% |

Parts B and D were deleted by Act A1760/2025.

Source: EPF Act 1991 Third Schedule, version "from 1 October 2025", <https://www.kwsp.gov.my/documents/d/guest/third_schedule_from_-1-october-2025> (eff. October 2025 wages); KWSP "Employer Mandatory Contribution", <https://www.kwsp.gov.my/en/employer/responsibilities/mandatory-contribution> (ret.).

Limits (mandatory-contribution page, notes and FAQ 18, 25 and 29): minimum age 14; "maximum age of contribution is 75 years old"; liable once wages for the month exceed RM10.00; no contribution for the month in which the employee dies (s43(7)).

Part F scope, from KWSP <https://www.kwsp.gov.my/en/employer/responsibilities/non-malaysian-citizen-employees> (ret.):

- Starts with October 2025 wages (contribution month November 2025, first payment by 15 Nov 2025).
- Applies when all hold: employer registered or incorporated in Malaysia; employee holds a valid passport and work pass; contract of service or apprenticeship; wages paid in money; employee below 75. Pass types: Visitor's Pass (Temporary Employment) except foreign domestic helpers, Employment Pass, Professional Visitor Pass, Student Pass, Residence Pass, Long-Term Social Visit Pass. Short contracts, part-time and casual work are included.
- Excludes domestic servants (s3 Workmen's Compensation Act 1952: maid, cook, gardener, cleaner, babysitter, driver and others), who may opt in; permanent residents (they use Part A or C); employees of embassies and other Second Schedule bodies.
- The contribution "must be calculated based on at least the minimum wage rate prescribed under the prevailing Minimum Wages Order". i-Akaun (Employer) rejects non-citizen wages below RM1,700, "Malaysia's minimum wage" (KWSP guide, <https://www.kwsp.gov.my/documents/d/guest/managing-non-malaysian-citizen-employees-in-i-akaun-employer-verification-registration-contributions>, ret.).
- The obligation ends in the month of death, at age 75, or two months before the work pass expires if it is not extended.

#### 5.2 EPF wages

Subject to EPF: salary or wages, bonus, allowances, commission, incentives, arrears, payment for unused annual or medical leave, paid maternity and study leave, wages for half-day leave, and other payments under the contract of service. Not subject: service charge, overtime, gratuity, retirement benefits, retrenchment, lay-off or termination benefits, payment in lieu of notice, and travelling allowance (KWSP says the list is not exhaustive). Arrears of an annual increment are contributed in the month they relate to; other salary adjustments in the current month. Source: mandatory-contribution page, FAQ 8, 11, 17, 19 and 20 (ret.).

#### 5.3 Table mechanics (Parts A, C and E)

Bands: RM0.01-10.00 nil; RM10.01-20.00; then RM20 bands up to RM5,000.00; then RM100 bands from RM5,000.01 up to RM20,000.00. Each share in the schedule equals the rate × the band's upper limit, rounded up to the next ringgit. This was checked against all 401 rows of each of Parts A, C and E of the 1 October 2025 schedule on 2026-10-21. Above RM20,000 the percentage applies to actual wages (Part A 12%/11%, Part C 6%/5.5%, Part E 4%/0%), "the total contribution which includes cents shall be rounded to the next ringgit". KWSP: "Employers are not allowed to calculate the employer's and employee's share based on exact percentage EXCEPT for salaries that exceed RM20,000.00."

Source: Third Schedule (eff. 1 Oct 2025) and mandatory-contribution page, both above.

```text
def epf_band_upper(W):                  # W = EPF wages for the month, 10 < W <= 20000
    if W <= 20:   return 20
    if W <= 5000: return ceil(W / 20) * 20
    return ceil(W / 100) * 100

def epf(part, W):
    if age >= 75 or W <= 10: return (0, 0)
    if part == "F":                      # 2% each; rounding per O1
        return pct_with_rounding_rule(0.02 * W, 0.02 * W)
    if W > 20000:                        # A 12/11, C 6/5.5, E 4/0; rounding per O1
        return pct_with_rounding_rule(hi_er[part] * W, ee[part] * W)
    U  = epf_band_upper(W)
    er = lo_er[part] if U <= 5000 else hi_er[part]   # A 13/12, C 6.5/6, E 4/4; bonus rule per O2
    return (ceil_ringgit(er * U), ceil_ringgit(ee[part] * U))
```

Test cases (KWSP mandatory-contribution page, ret.): Part A wages RM3,250.00 → employer RM424, employee RM359 (13% and 11% of 3,260). Part A RM6,710.80 → RM816 and RM748 (12% and 11% of 6,800). Part E RM3,250 → RM131 and RM0. Part C RM3,250 → RM212 and RM180. Part A RM21,250 → 2,550.00 + 2,337.50 = 4,887.50 → total RM4,888.

#### 5.4 Voluntary contributions (i-Topup)

| Who | How | Source |
| --- | --- | --- |
| Employee | i-Topup (formerly Voluntary Excess): an extra percentage above the statutory employee rate, through i-Akaun (Member) or the app, or Form KWSP 17A (AHL); cancel with KWSP 18A (AHL). Effective for the current wage month or up to two months ahead, or the wage month keyed in by the employer if later. Binding until cancelled or until the employee changes employer. The employer may deduct it from salary | form V20251021, <https://www.kwsp.gov.my/documents/d/guest/borang-permohonan-pendaftaran_pembatalan-mencarum-melebihi-kadar-berkanun-kwsp17a-kwsp-18a-pdf>; mandatory-contribution page FAQ 15 |
| Employer | no form; submit i-Topup (Employer's share) through i-Akaun (Employer) | mandatory-contribution page FAQ 14 |

i-Saraan is not open to non-Malaysian members (non-citizen page).

#### 5.5 Timing

Wages for month M are paid as the contribution for month M+1, on or before the 15th of M+1. Late payment charge: dividend-based, minimum RM10, rounded up to the ringgit. Source: mandatory-contribution page (ret.).

### 6. SOCSO (Act 4), including LINDUNG 24 Jam

#### 6.1 Categories and rates

| Category | Schemes | Who | Employer | Employee |
| --- | --- | --- | --- | --- |
| First | Employment Injury, Invalidity, and from 1 Jun 2026 Non-Employment Injury (NEI, "LINDUNG 24 Jam") | employees below 60, except those who reached 55 with no contributions before 55 | 1.75% (1.25% employment injury + 0.5% invalidity) | 0.5% invalidity + 0.75% NEI |
| Second | Employment Injury, and NEI from 1 Jun 2026 | employees aged 60 and above; new employees first covered at 55 or older | 1.25% | 0.75% NEI |

Sources: <https://www.perkeso.gov.my/en/our-services/employer-employee/contributions.html> (ret.); LINDUNG 24 Jam FAQ, Q25 and Q30, <https://www.perkeso.gov.my/images/lindung/lindung-24-jam/25062026-FAQ_LINDUNG_24_JAM_EN.pdf> (25 Jun 2026).

Foreign workers, including expatriates and foreign domestic workers, are covered by Employment Injury (from 1 Jan 2019), Invalidity (from 1 Jul 2024) and NEI (from 1 Jun 2026); the same categories apply: first category if first covered below 55, second category if first covered at 55 or older or once they reach 60. Sources: <https://www.perkeso.gov.my/en/our-services/protection/foreign-worker.html> (ret.); PERKESO FAQ on the Invalidity Scheme for foreign workers, <https://www.perkeso.gov.my/images/pekerja_asing/250724%20-FAQ%20-%20INVALIDITY%20SCHEME%20FOREIGN%20WORKER.pdf> (25 Jul 2024).

LINDUNG 24 Jam (NEI, SKBBK), from the FAQ above:

- In force from 1 Jun 2026 (June 2026 contributions; the first payment was due by 15 Jul 2026, later months by the 15th of the following month).
- Paid by the employee only, deducted by the employer: 0.75% for 1 Jun 2026 to 31 May 2028, 1.00% for 1 Jun 2028 to 31 May 2031, 1.25% from 1 Jun 2031, on wages up to the RM6,000 ceiling. The later phases are "subject to determination and the prescribed effective date". Legal basis: Third Schedule, Employees' Social Security (Amendment) Act 2026 [Act A1788].
- Covers all local and foreign employees under Act 4; no age limit.
- An employee with more than one employer chooses one employer to deduct NEI; failing a choice, PERKESO assigns one. Only that employer deducts it.
- Six-month penalty grace period after enforcement.

#### 6.2 Ceiling and wages

| Rule | Value | Source |
| --- | --- | --- |
| Wage ceiling | RM6,000 a month from 1 Oct 2024 (previously RM5,000); applies to local and foreign workers; wages above RM6,000 use the RM6,000 row | <https://www.perkeso.gov.my/en/rate-of-contribution.html> (ret.); PERKESO ceiling FAQ, 1 Oct 2024, <https://www.perkeso.gov.my/images/dokumen/011024%20-%20FAQ%20PENINGKATAN%20HAD%20SILING%20GAJI%20DARI%20RM5K%20KEPADA%20RM6K%20DI%20BAWAH%20AKSP%20969%20AKTA%204%20%20ASIP%202017%20AKTA%20800.pdf> |
| Wages (Act 4 s2(24); Act 800 s2 is the same except that it also excludes benefits under other laws administered by PERKESO) | all remuneration payable in money, including leave, holiday and overtime pay and extra work on holidays. Excluded: statutory contributions (pension, provident or social security funds), travelling allowance or concession, special expenses due to the nature of the work, gratuity on discharge or retirement, annual bonus, and other items prescribed | LINDUNG 24 Jam FAQ Q26; Act 800 text, <https://www.perkeso.gov.my/images/imej/akta_dan_peraturan/EMPLOYMENT_INSURANCE_SYSTEM_ACT_2017_Act_800.pdf> (as enacted 2017) |
| Monthly wages (Act 800 Second Schedule) | "the wages payable to an employee in respect of any wage period ending in the month" | Act 800 text |

#### 6.3 Contribution table (SOCSO and EIS)

Bands as printed: "wages up to RM30"; then "where wages exceed RMa but do not exceed RMb" for 30-50, 50-70, 70-100, 100-140, 140-200, 200-300, then RM100 steps to RM6,000; "where wages exceed RM6,000" uses the RM6,000 amounts. The amounts are fixed in the Schedules. They approximate rate × band midpoint but follow no single rounding rule (for example 1.75% × 1,450 = 25.375 is printed 25.35, while 1.75% × 1,550 = 27.125 is printed 27.15), so store the table as data and never compute it. Second-category employees pay only the NEI amount; they have no invalidity share.

Sources: SOCSO, "Employees' Social Security Act 1969 (Act 4): new contribution rate including the Non-Employment Injury Security Scheme (SKBBK)", <https://www.perkeso.gov.my/images/lindung/lindung-24-jam/NewContributionRateIncludingSKBBK.pdf> (eff. 1 Jun 2026; row totals checked: employer + invalidity + NEI = total on all 65 rows). EIS, "Rate of Contribution Employment Insurance System (Act 800)", <https://www.perkeso.gov.my/images/dokumen/151124-Rate%20Contribution%20ACT%20800.pdf> (RM6,000 ceiling, eff. 1 Oct 2024; transcribed from the PDF's images).

| # | Wages over (RM) | Up to (RM) | Cat 1 ER | Cat 1 EE invalidity | NEI EE (both cats) | Cat 1 total | Cat 2 ER | Cat 2 total | EIS ER | EIS EE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0 | 30 | 0.40 | 0.10 | 0.20 | 0.70 | 0.30 | 0.50 | 0.05 | 0.05 |
| 2 | 30 | 50 | 0.70 | 0.20 | 0.30 | 1.20 | 0.50 | 0.80 | 0.10 | 0.10 |
| 3 | 50 | 70 | 1.10 | 0.30 | 0.50 | 1.90 | 0.80 | 1.30 | 0.15 | 0.15 |
| 4 | 70 | 100 | 1.50 | 0.40 | 0.65 | 2.55 | 1.10 | 1.75 | 0.20 | 0.20 |
| 5 | 100 | 140 | 2.10 | 0.60 | 0.90 | 3.60 | 1.50 | 2.40 | 0.25 | 0.25 |
| 6 | 140 | 200 | 2.95 | 0.85 | 1.25 | 5.05 | 2.10 | 3.35 | 0.35 | 0.35 |
| 7 | 200 | 300 | 4.35 | 1.25 | 1.85 | 7.45 | 3.10 | 4.95 | 0.50 | 0.50 |
| 8 | 300 | 400 | 6.15 | 1.75 | 2.65 | 10.55 | 4.40 | 7.05 | 0.70 | 0.70 |
| 9 | 400 | 500 | 7.85 | 2.25 | 3.35 | 13.45 | 5.60 | 8.95 | 0.90 | 0.90 |
| 10 | 500 | 600 | 9.65 | 2.75 | 4.15 | 16.55 | 6.90 | 11.05 | 1.10 | 1.10 |
| 11 | 600 | 700 | 11.35 | 3.25 | 4.85 | 19.45 | 8.10 | 12.95 | 1.30 | 1.30 |
| 12 | 700 | 800 | 13.15 | 3.75 | 5.65 | 22.55 | 9.40 | 15.05 | 1.50 | 1.50 |
| 13 | 800 | 900 | 14.85 | 4.25 | 6.35 | 25.45 | 10.60 | 16.95 | 1.70 | 1.70 |
| 14 | 900 | 1,000 | 16.65 | 4.75 | 7.15 | 28.55 | 11.90 | 19.05 | 1.90 | 1.90 |
| 15 | 1,000 | 1,100 | 18.35 | 5.25 | 7.85 | 31.45 | 13.10 | 20.95 | 2.10 | 2.10 |
| 16 | 1,100 | 1,200 | 20.15 | 5.75 | 8.65 | 34.55 | 14.40 | 23.05 | 2.30 | 2.30 |
| 17 | 1,200 | 1,300 | 21.85 | 6.25 | 9.35 | 37.45 | 15.60 | 24.95 | 2.50 | 2.50 |
| 18 | 1,300 | 1,400 | 23.65 | 6.75 | 10.15 | 40.55 | 16.90 | 27.05 | 2.70 | 2.70 |
| 19 | 1,400 | 1,500 | 25.35 | 7.25 | 10.85 | 43.45 | 18.10 | 28.95 | 2.90 | 2.90 |
| 20 | 1,500 | 1,600 | 27.15 | 7.75 | 11.65 | 46.55 | 19.40 | 31.05 | 3.10 | 3.10 |
| 21 | 1,600 | 1,700 | 28.85 | 8.25 | 12.35 | 49.45 | 20.60 | 32.95 | 3.30 | 3.30 |
| 22 | 1,700 | 1,800 | 30.65 | 8.75 | 13.15 | 52.55 | 21.90 | 35.05 | 3.50 | 3.50 |
| 23 | 1,800 | 1,900 | 32.35 | 9.25 | 13.85 | 55.45 | 23.10 | 36.95 | 3.70 | 3.70 |
| 24 | 1,900 | 2,000 | 34.15 | 9.75 | 14.65 | 58.55 | 24.40 | 39.05 | 3.90 | 3.90 |
| 25 | 2,000 | 2,100 | 35.85 | 10.25 | 15.35 | 61.45 | 25.60 | 40.95 | 4.10 | 4.10 |
| 26 | 2,100 | 2,200 | 37.65 | 10.75 | 16.15 | 64.55 | 26.90 | 43.05 | 4.30 | 4.30 |
| 27 | 2,200 | 2,300 | 39.35 | 11.25 | 16.85 | 67.45 | 28.10 | 44.95 | 4.50 | 4.50 |
| 28 | 2,300 | 2,400 | 41.15 | 11.75 | 17.65 | 70.55 | 29.40 | 47.05 | 4.70 | 4.70 |
| 29 | 2,400 | 2,500 | 42.85 | 12.25 | 18.35 | 73.45 | 30.60 | 48.95 | 4.90 | 4.90 |
| 30 | 2,500 | 2,600 | 44.65 | 12.75 | 19.15 | 76.55 | 31.90 | 51.05 | 5.10 | 5.10 |
| 31 | 2,600 | 2,700 | 46.35 | 13.25 | 19.85 | 79.45 | 33.10 | 52.95 | 5.30 | 5.30 |
| 32 | 2,700 | 2,800 | 48.15 | 13.75 | 20.65 | 82.55 | 34.40 | 55.05 | 5.50 | 5.50 |
| 33 | 2,800 | 2,900 | 49.85 | 14.25 | 21.35 | 85.45 | 35.60 | 56.95 | 5.70 | 5.70 |
| 34 | 2,900 | 3,000 | 51.65 | 14.75 | 22.15 | 88.55 | 36.90 | 59.05 | 5.90 | 5.90 |
| 35 | 3,000 | 3,100 | 53.35 | 15.25 | 22.85 | 91.45 | 38.10 | 60.95 | 6.10 | 6.10 |
| 36 | 3,100 | 3,200 | 55.15 | 15.75 | 23.65 | 94.55 | 39.40 | 63.05 | 6.30 | 6.30 |
| 37 | 3,200 | 3,300 | 56.85 | 16.25 | 24.35 | 97.45 | 40.60 | 64.95 | 6.50 | 6.50 |
| 38 | 3,300 | 3,400 | 58.65 | 16.75 | 25.15 | 100.55 | 41.90 | 67.05 | 6.70 | 6.70 |
| 39 | 3,400 | 3,500 | 60.35 | 17.25 | 25.85 | 103.45 | 43.10 | 68.95 | 6.90 | 6.90 |
| 40 | 3,500 | 3,600 | 62.15 | 17.75 | 26.65 | 106.55 | 44.40 | 71.05 | 7.10 | 7.10 |
| 41 | 3,600 | 3,700 | 63.85 | 18.25 | 27.35 | 109.45 | 45.60 | 72.95 | 7.30 | 7.30 |
| 42 | 3,700 | 3,800 | 65.65 | 18.75 | 28.15 | 112.55 | 46.90 | 75.05 | 7.50 | 7.50 |
| 43 | 3,800 | 3,900 | 67.35 | 19.25 | 28.85 | 115.45 | 48.10 | 76.95 | 7.70 | 7.70 |
| 44 | 3,900 | 4,000 | 69.15 | 19.75 | 29.65 | 118.55 | 49.40 | 79.05 | 7.90 | 7.90 |
| 45 | 4,000 | 4,100 | 70.85 | 20.25 | 30.35 | 121.45 | 50.60 | 80.95 | 8.10 | 8.10 |
| 46 | 4,100 | 4,200 | 72.65 | 20.75 | 31.15 | 124.55 | 51.90 | 83.05 | 8.30 | 8.30 |
| 47 | 4,200 | 4,300 | 74.35 | 21.25 | 31.85 | 127.45 | 53.10 | 84.95 | 8.50 | 8.50 |
| 48 | 4,300 | 4,400 | 76.15 | 21.75 | 32.65 | 130.55 | 54.40 | 87.05 | 8.70 | 8.70 |
| 49 | 4,400 | 4,500 | 77.85 | 22.25 | 33.35 | 133.45 | 55.60 | 88.95 | 8.90 | 8.90 |
| 50 | 4,500 | 4,600 | 79.65 | 22.75 | 34.15 | 136.55 | 56.90 | 91.05 | 9.10 | 9.10 |
| 51 | 4,600 | 4,700 | 81.35 | 23.25 | 34.85 | 139.45 | 58.10 | 92.95 | 9.30 | 9.30 |
| 52 | 4,700 | 4,800 | 83.15 | 23.75 | 35.65 | 142.55 | 59.40 | 95.05 | 9.50 | 9.50 |
| 53 | 4,800 | 4,900 | 84.85 | 24.25 | 36.35 | 145.45 | 60.60 | 96.95 | 9.70 | 9.70 |
| 54 | 4,900 | 5,000 | 86.65 | 24.75 | 37.15 | 148.55 | 61.90 | 99.05 | 9.90 | 9.90 |
| 55 | 5,000 | 5,100 | 88.35 | 25.25 | 37.85 | 151.45 | 63.10 | 100.95 | 10.10 | 10.10 |
| 56 | 5,100 | 5,200 | 90.15 | 25.75 | 38.65 | 154.55 | 64.40 | 103.05 | 10.30 | 10.30 |
| 57 | 5,200 | 5,300 | 91.85 | 26.25 | 39.35 | 157.45 | 65.60 | 104.95 | 10.50 | 10.50 |
| 58 | 5,300 | 5,400 | 93.65 | 26.75 | 40.15 | 160.55 | 66.90 | 107.05 | 10.70 | 10.70 |
| 59 | 5,400 | 5,500 | 95.35 | 27.25 | 40.85 | 163.45 | 68.10 | 108.95 | 10.90 | 10.90 |
| 60 | 5,500 | 5,600 | 97.15 | 27.75 | 41.65 | 166.55 | 69.40 | 111.05 | 11.10 | 11.10 |
| 61 | 5,600 | 5,700 | 98.85 | 28.25 | 42.35 | 169.45 | 70.60 | 112.95 | 11.30 | 11.30 |
| 62 | 5,700 | 5,800 | 100.65 | 28.75 | 43.15 | 172.55 | 71.90 | 115.05 | 11.50 | 11.50 |
| 63 | 5,800 | 5,900 | 102.35 | 29.25 | 43.85 | 175.45 | 73.10 | 116.95 | 11.70 | 11.70 |
| 64 | 5,900 | 6,000 | 104.15 | 29.75 | 44.65 | 178.55 | 74.40 | 119.05 | 11.90 | 11.90 |
| 65 | 6,000 | and above | 104.15 | 29.75 | 44.65 | 178.55 | 74.40 | 119.05 | 11.90 | 11.90 |

```text
row = band_row(monthly_wages)        # "exceed lower, not exceed upper"; above 6,000 → row 65
if socso_category == 1:
    er = row.cat1_er;  ee = row.cat1_ee_invalidity
else:
    er = row.cat2_er;  ee = 0
if nei_deducted_by_this_employer(employee):     # one employer only (6.1)
    ee += row.nei_ee
if eis_eligible(employee):                       # 7
    eis_er = row.eis_er;  eis_ee = row.eis_ee
```

### 7. EIS (Act 800)

| Rule | Value | Source |
| --- | --- | --- |
| Rates | employer 0.2%, employee 0.2% of the "assumed monthly salary"; amounts from the §6.3 table | <https://www.perkeso.gov.my/en/our-services/employer-employee/contributions.html> (ret.) |
| Ceiling | RM6,000 (from 1 Oct 2024) | same; ceiling FAQ (1 Oct 2024) |
| Who | Malaysian citizens or permanent residents aged 18 to 60, private sector, under a contract of service; local domestic workers since 1 Jun 2021 | PERKESO FAQ, <https://www.perkeso.gov.my/en/contact-us/pejabat-perkeso-new/frequently-asked-question.html> (ret.); <https://perkeso.gov.my/en/our-services/protection/domestic-workers.html> (ret.) |
| Not covered | foreign workers, including foreign domestic workers; public servants; employees of local authorities and statutory bodies; the self-employed; under 18 or aged 60 and above; aged 57 and above with no contribution payable before 57; casual workers not employed for the employer's industry; the employer's spouse | PERKESO ceiling FAQ (1 Oct 2024): "pekerja asing tidak diliputi di bawah Akta Sistem Insurans Pekerjaan 2017 (Akta 800)"; domestic-workers page; Act 800 First Schedule (as enacted 2017) |

### 8. PCB / MTD (computerised calculation method)

Main source: LHDN, "Specification for Monthly Tax Deduction (MTD) Calculations Using Computerized Calculation for 2026", <https://www.hasil.gov.my/wp-content/uploads/spesifikasi-kaedah-pengiraan-berkomputer-pcb-2026.pdf> (upd. 01 Jan 2026; listed on <https://www.hasil.gov.my/en/majikan/jadual-pcb-dan-spesifikasi-data/>, upd. 29/07/2026). It applies to 2026 payroll (YA 2026). Budget 2026 changed reliefs only: "there is no amendment to the MTD formula". Software verified by LHDN for any year from 2012 to 2025 needs no new verification.

#### 8.1 Residence status

| Status | MTD | Source |
| --- | --- | --- |
| Not resident, or not known to be resident | 30% of remuneration, after excluding exempt allowances and benefits. Example: RM3,000 × 30% = RM900 | spec D(a) |
| Resident | the formulas below | spec D(b) |
| Foreign employees | from August 2017, MTD for residents applies to employees with an employment contract of 182 days or more, including Visit Pass (Temporary Employment) holders and expatriates | spec D(a) note |
| Approved Returning Expert Programme individuals; knowledge workers in a specified region | 15% flat: MTD = [(P × 15% − T) − (Z + X)] / (n + 1), with T = RM400 (categories 1 and 3) or RM800 (category 2) when P ≤ 35,000, else 0 | spec D(b)(3)-(4), Tables 2 and 3 |
| Non-citizen residents in an approved C-suite position | 15% flat, no rebate: MTD = [(P × 15%) − (Z + X)] / (n + 1) | spec D(b)(5), Table 4 |

#### 8.2 Normal remuneration

```text
MTD_month = [ (P - M) * R + B - (Z + X) ] / (n + 1)
Net_MTD   = MTD_month - zakat_this_month
P = [ Σ(Y - K) + (Y1 - K1) + (Y2 - K2) * n + (Yt - Kt) ] - [ D + S + DU + SU + Q*C + (LP + LP1) ]
    # (Yt - Kt) is used only in the additional-remuneration calculation (8.4)
K2 = min( (4000 - (K + K1 + Kt)) / n , K1 )     # K + K1 + K2*n + Kt <= RM4,000 a year
```

| Variable | Meaning |
| --- | --- |
| Y, K | gross normal plus additional remuneration paid this year before the current month, including any previous employer (Form TP3); K = EPF on Y, within the yearly qualifying limit |
| Y1, K1 | gross normal remuneration for the current month; EPF on Y1 |
| Y2, K2 | estimated remuneration for each later month (= Y1); estimated EPF for each later month (formula above) |
| Yt, Kt | gross additional remuneration for the current month; EPF on Yt |
| n | months left in the year after the current month (n + 1 includes it) |
| D, S, DU, SU | reliefs: individual RM9,000; spouse RM4,000 (category 2 only); disabled individual RM7,000; disabled spouse RM6,000 |
| Q, C | RM2,000 per qualifying child; C = number of qualifying children (0 for category 1), with multipliers in 8.5 |
| LP, LP1 | optional deductions claimed on Form TP1: accumulated before this month (including the previous employer); this month |
| M, R, B | from Table 1 (8.3) for the value of P |
| Z | zakat paid this year before the current month |
| X | MTD paid this year before the current month, including the previous employer, excluding extra MTD requested by the employee and tax instalments |

Categories: 1 = single (S = 0, C = 0); 2 = married, spouse not working (S = RM4,000); 3 = married with a working spouse, divorced or widowed, or single with an adopted child (S = 0).

EPF in PCB (spec E13): EPF on a monthly allowance that is EPF-able but tax-exempt stays in K1. EPF caused by a one-off item or bonus is Kt = total EPF − EPF on normal remuneration (RM2,400 salary + RM3,600 bonus, EPF RM660 → K1 = 264, Kt = 396). Voluntary EPF claimed on TP1 goes to LP1. K1 is capped so the yearly total stays within RM4,000. Without mandatory EPF (for example director's fees only), voluntary EPF counts up to RM7,000 (RM4,000 + RM3,000).

Benefits in kind and living accommodation (spec E11-E12): add to Y1 for MTD only, in the current year; never on the payslip or EA as salary. Monthly amount = the year's value / months remaining including the current month (spec example: car RM25,000 from April = 25,000 / 9 = 2,777.77, shown as RM2,777.00).

#### 8.3 Table 1: values of M, R and B

| P (RM) | M (RM) | R (%) | B, categories 1 and 3 (RM) | B, category 2 (RM) |
| --- | --- | --- | --- | --- |
| 5,001 - 20,000 | 5,000 | 1 | -400 | -800 |
| 20,001 - 35,000 | 20,000 | 3 | -250 | -650 |
| 35,001 - 50,000 | 35,000 | 6 | 600 | 600 |
| 50,001 - 70,000 | 50,000 | 11 | 1,500 | 1,500 |
| 70,001 - 100,000 | 70,000 | 19 | 3,700 | 3,700 |
| 100,001 - 400,000 | 100,000 | 25 | 9,400 | 9,400 |
| 400,001 - 600,000 | 400,000 | 26 | 84,400 | 84,400 |
| 600,001 - 2,000,000 | 600,000 | 28 | 136,400 | 136,400 |
| above 2,000,000 | 2,000,000 | 30 | 528,400 | 528,400 |

B is the tax on M less the RM400 self rebate and, for category 2, the RM400 spouse rebate; both rebates apply only up to P = RM35,000. P of RM5,000 or less is in the 0% band. Source: spec Table 1 (2026).

Resident tax schedule, for checking B: 0-5,000 at 0%; next 15,000 at 1% (cumulative tax 150 at 20,000); next 15,000 at 3% (600 at 35,000); next 15,000 at 6% (1,500 at 50,000); next 20,000 at 11% (3,700 at 70,000); next 30,000 at 19% (9,400 at 100,000); next 300,000 at 25% (84,400 at 400,000); next 200,000 at 26% (136,400 at 600,000); next 1,400,000 at 28% (528,400 at 2,000,000); 30% above. Source: <https://www.hasil.gov.my/en/individu/kadar-cukai/> (upd. 26/06/2026, headed YA 2023, 2024 and 2025; see O8). Non-resident individuals: 30% (spec D(a)).

#### 8.4 Additional remuneration (bonus, arrears, commission or allowances not paid monthly, gratuity, compensation, ex-gratia, director's fees not paid monthly, tax borne by employer, ESOS if the employee opts in)

```text
# Step 1: normal remuneration only (P without Yt - Kt)
mtd_c   = [ (P1 - M) * R + B - (Z + X) ] / (n + 1)
net_c   = mtd_c - zakat_this_month
total_c = X + mtd_c * (n + 1)
# Step 2: P2 = same P including (Yt - Kt); recompute K2 with Kt included
# Step 3: tax_year = (P2 - M) * R + B                       # M, R, B for P2
# Step 4: mtd_ar = tax_year - (total_c + zakat_paid)        # bracket as in the spec's worked example
# Step 5: mtd_pay = net_c + mtd_ar
```

Gross employment income is taxed in the year it is received (ITA s25(1), from YA 2016). If no normal remuneration is paid in the month, Y1 = 0; if the additional remuneration is paid before the monthly salary, Y1 is the salary to be paid that month (spec E7-E8).

#### 8.5 Reliefs and TP1 deductions (2026)

| Item | Limit (RM) |
| --- | --- |
| Individual (automatic) | 9,000 |
| Spouse without income, or joint assessment (not allowed if the spouse, not disabled, has foreign income over RM4,000) | 4,000 |
| Disabled individual / disabled spouse | 7,000 / 6,000 |
| Child below 18, or 18 and above in full-time study (C = 1) | 2,000 per child |
| Child 18 and above at diploma level or higher in Malaysia, or degree level or higher abroad (C = 4) | 8,000 |
| Disabled child (C = 4) | 8,000 |
| Disabled child at diploma level or higher in Malaysia, or degree level or higher abroad (C = 8) | 16,000 |
| EPF or other approved scheme (K) | 4,000 |
| Life insurance or takaful for self, spouse and children, plus voluntary EPF (LP) | 3,000 (EPF + this ≤ 7,000) |
| Medical treatment, special needs and carer for parents or grandparents (full medical check-up within it, limit 1,000, now covering all NPRA-registered vaccines) | 8,000 |
| Basic supporting equipment for disabled self, spouse, child or parent | 6,000 |
| Own education fees (up-skilling courses within it limited to 2,000) | 7,000 |
| Admission to tourist attractions and cultural or arts programmes (YA 2026) | 1,000 |
| Serious diseases, fertility treatment, vaccination (1,000), complete medical check-up (1,000), dental (1,000), diagnosis and early intervention for children with learning disabilities (raised to 10,000 for YA 2026) | 10,000 |
| Net SSPN deposits (YA 2012 to 2027) | 8,000 |
| Alimony to a former wife (with wife relief, total ≤ 4,000) | 4,000 |
| Private Retirement Scheme and deferred annuity (to YA 2030) | 3,000 |
| Education and medical insurance | 4,000 |
| SOCSO under Act 4 or EIS under Act 800 (TP1 item C14, ITA para 46(1)(n)); see O4 | 350 |
| Lifestyle (reading material, computer, smartphone or tablet, internet, self-enrichment courses) | 2,500 |
| Breastfeeding equipment (child up to 2; once every 2 years) | 1,000 |
| Child care fees (registered TASKA or TADIKA, child 6 or below; YA 2026 adds day-care and after-school transit centres for children up to 12) | 3,000 |
| Additional lifestyle: sports equipment, facility and competition fees, gym | 1,000 |
| EV charging, household food-waste composter, and for YA 2026-2027 food-waste grinder and home CCTV (grinder or CCTV once per 2 years) | 2,500 |
| First-home housing loan interest, SPA from 1 Jan 2025 to 31 Dec 2027, 3 consecutive YAs | 7,000 (home ≤ RM500,000); 5,000 (RM500,001-750,000) |

Source: spec section C (Budget 2026 changes) and E14 (reliefs); TP1 2026 notes, <https://www.hasil.gov.my/wp-content/uploads/bi-explanatory-notes-for-from-tp1-2026-1.pdf> (ret.). Claims enter LP and LP1 only after the employer approves the employee's Form TP1; the payroll system must show cumulative and current-month amounts.

#### 8.6 Zakat, rounding and the RM10 rule

| Rule | Detail |
| --- | --- |
| Precision | every calculation keeps 2 decimals and drops the rest: `trunc2` (spec E1) |
| Rounding | the final MTD is rounded up with `ceil_5sen` (spec E2) |
| RM10 rule | MTD (before zakat) below RM10: no deduction. Net MTD after zakat below RM10: still deduct it. MTD for additional remuneration below RM10: 0 (spec E3-E4) |
| Zakat | zakat deducted through payroll appears on the payslip and EA; zakat paid directly and claimed on TP1 is treated as zakat for the month it is claimed. Net MTD = max(0, MTD − zakat); the full zakat of the month joins Z next month. Spec examples: MTD 15.00, zakat 8.00 → net 7.00 (deducted); MTD 15.00, zakat 20.00 → net 0 (spec E5, E15) |
| Payment | pay the actual amount, including sen (spec E6) |

Source: spec section E (2026).

```text
mtd = ceil_5sen(trunc2(formula_result))    # truncate first: 110.0003 → 110.00, not 110.05
if mtd < 10: mtd = 0                         # before zakat
net = max(0, mtd - zakat_this_month)         # deduct even if below 10
```

The spec gives no rule for a negative formula result; MTD cannot be negative, so treat it as 0 (inference).

#### 8.7 Test cases (spec Exhibit 5, category 3, 3 children, normal remuneration RM5,500 a month, EPF RM605)

| Month | Key values | MTD |
| --- | --- | --- |
| January | K2 = (4,000 − 605) / 11 = 308.63; P = 4,895.00 + 5,191.37 × 11 − 15,000 = 47,000.07 | [(12,000.07 × 6%) + 600 − 0] / 12 = 110.00 |
| February | K2 = 279.00; P = 47,000.00; X = 110 | 110.00 |
| March | LP1 = 300 (books 100 + parent's medical 200); K2 = 242.77; P = 46,700.07; X = 220 | 108.20 |
| April, bonus RM8,250 with EPF RM908, LP1 = 300 | Step 1: K2 = 197.50, P = 46,400.00, MTD 106.20, total for the year 1,284.00. Step 2: K2 = 84.00, P = 54,650.00. Step 3: tax 2,011.50. Step 4: 727.50 | 106.20 + 727.50 = 833.70 |

### 9. HRD Corp levy

| Rule | Value | Source |
| --- | --- | --- |
| Mandatory | employers with 10 or more Malaysian employees must register; levy 1% of the employees' monthly wages | <https://hrdcorp.gov.my/registered-employers> (ret.); PSMB Act 2001 s14 |
| Optional | employers with 5 to 9 Malaysian employees may register; levy 0.5% | same; PSMB Act s15 |
| Sector scope | "All companies' activities should be covered under PSMB Act 2001" | registered-employers page |
| Employees | Malaysian citizens employed under a contract of service; domestic servants excluded; a director paid only director's fees is not an employee | <https://supportcentre.hrdcorp.gov.my/portal/en/kb/articles/hrd-levy> (ret.) |
| Wages | basic salary and fixed allowances paid in cash (full-time, contract or permanent), less unpaid leave. Excluded: bonus, commission, overtime, variable allowances (night, shift, attendance when the amount varies), production incentives, gratuity, pension and retrenchment payments, travel, transport and petrol allowances, apprentice allowances, special expenses, employer welfare-fund contributions | same |
| Formula | levy = [(basic salary − unpaid leave) + fixed allowance] × 1% (or 0.5%), 2 decimal places | same |
| Timing | levy month = salary month; payment after the 15th of the following month is levy in arrears | same |
| 2026 exception | Employer Circular 1/2026, "The Levy Payment Exemption for Registered Employers in the Education Industries from January 2026 to December 2026" (title only; conditions not read) | <https://hrdcorp.gov.my/circulars> (ret.) |

### 10. Malaysian filings

| Filing | Due | Channel | Source |
| --- | --- | --- | --- |
| EPF Form A (monthly) | 15th of the month after the wage month | i-Akaun (Employer): same as last month, copy from history, upload TXT or CSV, or key in | §10.4 |
| SOCSO + EIS + NEI monthly contribution records (PERKESO's "Employee Contribution Text File"; the Borang 8A data) | 15th of the following month | ASSIST 2.0 portal (from June 2026); the combined format is mandatory from 1 Oct 2026, the old per-Act format was accepted until 30 Sep 2026 | §10.5 |
| CP39 / MTD (monthly) | on or before the 15th of the following month (also CP38) | e-PCB Plus (MyTax, <https://mytax.hasil.gov.my/>), e-Data PCB, e-CP39 or internet banking | §10.3; <https://www.hasil.gov.my/en/majikan/tanggungjawab-majikan/> (ret.) |
| EA (C.P.8A), to each employee (annual) | 28 February of the next year (2025 → 28 Feb 2026) | to the employee | §10.1 |
| Form E with C.P.8D, to LHDN (annual) | 31 March of the next year (2025 → 31 Mar 2026); Form E counts as complete only if C.P.8D is in by then. C.P.8D sent through e-Data Praisi or e-CP8D from 1 January to 25 February is prefilled into employees' returns | e-Filing (e-E); C.P.8D as a txt upload | §10.2 |

#### 10.1 EA form (C.P.8A)

Fields, from C.P.8A Pin. 2023 (<https://www.hasil.gov.my/wp-content/uploads/borang_ea__c.p.8a_-_pin._2023_.pdf>; the latest copy that opened, see O7):

- Header: serial no., employer's E no., year ended 31 December, employee's TIN, LHDNM branch.
- A, employee: A1 full name; A2 job designation; A3 staff or payroll no.; A4 new IC no.; A5 passport no.; A6 EPF no.; A7 SOCSO no.; A8 number of children qualifying for relief; A9 if employed less than a year, commencement and cessation dates.
- B, employment income, benefits and living accommodation, excluding tax-exempt items: B1(a) gross salary, wages or leave pay, including overtime; B1(b) fees (including director's fees), commission or bonus; B1(c) gross tips, perquisites, awards or other allowances; B1(d) income tax borne by the employer; B1(e) ESOS benefit; B1(f) gratuity and its period; B2 arrears and other amounts for earlier years paid this year; B3 benefits in kind; B4 value of living accommodation; B5 refund from an unapproved provident or pension fund; B6 compensation for loss of employment.
- C: C1 pension; C2 annuities or other periodical payments; total.
- D, deductions: D1 MTD remitted; D2 CP38 remitted; D3 zakat paid through salary; D4 approved donations, gifts or contributions through salary; D5 TP1 claims for (a) relief and (b) zakat other than through salary; D6 total qualifying child relief.
- E: E1 provident fund name and the employee's compulsory contribution; E2 the employee's compulsory SOCSO contribution (the 2025 guide notes include EIS under Act 800).
- F: total tax-exempt allowances, perquisites, gifts and benefits.
- Officer's name, designation, employer's name, address and telephone, date.

Due date and content rules: LHDN EA/EC guide notes 2025, <https://www.hasil.gov.my/wp-content/uploads/nota_panduan_ea_2025___ec_2025_1.pdf> (ret.; ITA s83(1A)). Previous-employer (TP3) amounts used for MTD never appear on the payslip or the EA (spec E10); BIK and VOLA must not be shown as gross salary (spec E12).

#### 10.2 Form E and C.P.8D

Form E Part A, from LHDN's Form E 2025 sample as indexed (see O7): A1 number of employees as at 31/12/2025; A2 number subject to MTD; A3 new employees; A4 employees who ceased employment or died; and the number who ceased employment and left Malaysia; plus the employer's TIN and name. Form E must list all employees, including part-time and contract staff, interns and directors.

C.P.8D (Pin. 2025): one line per employee, fields separated by `|`, saved as .txt. Integer fields drop the sen (truncate, not round).

| # | Field | Type, length | Notes |
| --- | --- | --- | --- |
| 1 | Name of employee | text, 60 | compulsory; as on the IC |
| 2 | TIN | integer, 11 | blank if none |
| 3 | IC / passport no. | text, 12 | compulsory; priority new IC, police no., army no., passport (foreigners); none → `000000000000` |
| 4 | Category of employee | integer, 1 | 1, 2 or 3 (MTD categories); latest value |
| 5 | Employee status | integer, 1 | 1 management, 2 permanent, 3 contract, 4 part time, 5 intern, 6 others; latest value |
| 6 | Date of retirement or end of contract | date, 10 | dd-mm-yyyy; compulsory; the termination date if the employee left during the year |
| 7 | Tax borne by employer | integer, 1 | 1 yes, 2 no |
| 8 | Number of children qualifying for relief | integer, 2 | |
| 9 | Total qualifying child relief | integer, 7 | as used for MTD |
| 10 | Total gross remuneration | integer, 11 | |
| 11 | Benefits in kind | integer, 11 | |
| 12 | Value of living accommodation | integer, 11 | |
| 13 | ESOS benefit | integer, 11 | |
| 14 | Tax-exempt allowances, perquisites, gifts, benefits | integer, 11 | |
| 15 | Total TP1 relief claims | integer, 11 | |
| 16 | Zakat claimed on TP1 (not through salary) | decimal, 11 | with sen |
| 17 | EPF contribution | integer, 11 | |
| 18 | Zakat through salary | decimal, 11 | with sen |
| 19 | MTD | decimal, 11 | with sen |
| 20 | CP38 | decimal, 11 | with sen |
| 21 | Medical insurance through salary | integer, 6 | |
| 22 | SOCSO through salary | integer, 6 | |

Example line: `Ali bin Ahmad|03770324020|730510125580|3|2|15-12-2027|2|1|2000|50000|4200|12000|1300|445|2200|1400.30|3600|1700.20|2555.25|1822.63|2210|150`. Empty fields stay empty between delimiters.

Source: LHDN "Return Form (RF) Filing Programme for the Year 2026", incl. "C.P.8D Information Layout - Pin. 2025", <https://www.hasil.gov.my/wp-content/uploads/rf-filing-programme-for-2026.pdf> (ret.).

#### 10.3 CP39 / MTD text file

File name `EEEEEEEEEEmm_yyyy.txt` (employer no., month, year of deduction). Amounts have no decimal point and two implied decimals (RM8,350.00 → `0000835000`). Employer no. is 10 digits without the "E" (E 908915-10 → `0090891510`); TIN is 11 digits without "IG" (IG 531367-080 → `00531367080`) and is mandatory.

| Record | Field | Positions | Length | Notes |
| --- | --- | --- | --- | --- |
| Header (57) | Record type | 1 | 1 | `H` |
| | Employer no. (HQ) | 2-11 | 10 | right-justified, zero-filled |
| | Employer no. | 12-21 | 10 | as above |
| | Year of deduction | 22-25 | 4 | YYYY |
| | Month of deduction | 26-27 | 2 | 01-12 |
| | Total MTD amount | 28-37 | 10 | zero-filled, 2 implied decimals |
| | Total MTD records | 38-42 | 5 | zero-filled |
| | Total CP38 amount | 43-52 | 10 | zero-filled, 2 implied decimals |
| | Total CP38 records | 53-57 | 5 | zero-filled |
| Detail (136) | Record type | 1 | 1 | `D` |
| | Tax identification no. | 2-12 | 11 | zero-filled to 11 digits |
| | Employee's name | 13-72 | 60 | as on IC or passport; space-filled |
| | Old IC no. | 73-84 | 12 | blank if none |
| | New IC no. | 85-96 | 12 | no dashes; blank if none |
| | Passport no. | 97-108 | 12 | foreigners; blank if none |
| | Country code | 109-110 | 2 | issuing country, foreigners only |
| | MTD amount | 111-118 | 8 | zero-filled, 2 implied decimals |
| | CP38 amount | 119-126 | 8 | as above |
| | Employee or salary no. | 127-136 | 10 | left-justified |

Source: MTD 2026 specification, Exhibits 4 and 5 (upd. 01 Jan 2026). The spec also requires the payroll system to produce the PCB 2(II) statement of MTD and CP38 deducted per employee (Exhibit 3) and to support TP1 and TP3 forms.

#### 10.4 EPF Form A upload

Public layout (KWSP, "i-Akaun (Employer) Easy Guide: Preparing CSV File for e-Caruman", June 2020, <https://www.kwsp.gov.my/documents/d/guest/easy-guide_preparing-csv-file-for-e-caruman>): columns A Member No., B IC No. (custom format `######-##-####`), C Name, D Salary (2 decimals), E Employer share (0 decimals), F Employee share (0 decimals). KWSP: "This format is only for e-Caruman usage." The 2017 e-Caruman FAQ (<https://secure.kwsp.gov.my/e-caruman/download/SOALAN_LAZIM_e-Caruman_EN_as_at_19052017.pdf>) also allows TXT files (EPFORMA.TXT, EPFORMA2.TXT) and requires EPF approval of any format. For non-citizens, i-Akaun validates passport numbers (15 characters at most) and rejects wages below RM1,700 (KWSP non-citizen i-Akaun guide). See O5.

#### 10.5 SOCSO + EIS + NEI text file

Fixed width, 278 characters per employee. Amounts in sen with no decimal point, right-justified.

| # | Field | Positions | Length | Type | Required | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Employer code | 1-12 | 12 | alphanumeric | Y | check-digit verified; left-justified |
| 2 | MyCoID / SSM no. | 13-32 | 20 | alphanumeric | N | ROB, ROC; left-justified |
| 3 | IC no. or SOCSO foreign worker no. | 33-44 | 12 | alphanumeric | Y | new IC no., SSFW no. or SSFDW no. |
| 4 | Employee name | 45-194 | 150 | alphanumeric | Y | as on IC or passport; left-justified |
| 5 | Contribution month | 195-200 | 6 | numeric | Y | MMYYYY; not a future month |
| 6 | Employee salary | 201-214 | 14 | numeric | Y | in sen |
| 7 | SOCSO employer share | 215-220 | 6 | numeric | Y | in sen |
| 8 | SOCSO employee share | 221-226 | 6 | numeric | Y | in sen; NEI goes in field 11, not here |
| 9 | EIS employer share | 227-232 | 6 | numeric | Y | in sen |
| 10 | EIS employee share | 233-238 | 6 | numeric | Y | in sen |
| 11 | SKBBK (NEI) employee share | 239-244 | 6 | numeric | Y | in sen; "Populate with 0000 if there is no contribution" |
| 12 | Filler 1 | 245-258 | 14 | alphanumeric | N | spaces |
| 13 | Filler 2 | 259-278 | 20 | alphanumeric | N | spaces |

For an Act with no deduction (for example a government employer, Act 4 only), enter 0 or leave it blank (FAQ Q6). Arrears may be sent in the same file (FAQ Q4).

Source: PERKESO, "Combine SOCSO + EIS Contribution Text File Format", version 2.1 (document dated 13 Feb 2026, published as 28072026-formatteksfail.pdf), <https://perkeso.gov.my/images/borang/lindung24jam/28072026-formatteksfail.pdf>; version 2.0 at <https://www.perkeso.gov.my/images/borang/lindung24jam/formatteksfail.pdf>; text-file FAQ, <https://www.perkeso.gov.my/images/lindung/lindung-24-jam/FAQ_TextFileFormat_EN.pdf> (ret.).

## Sources

All read on 2026-10-21. Dates are each source's own effective or last-updated date.

Singapore

- CPF Board, CPF contribution rate tables from 1 Jan 2026 (Tables 1-5), eff. 1 Jan 2026: <https://www.cpf.gov.sg/content/dam/web/employer/employer-obligations/documents/CPFcontributionratesfrom1Jan2026.pdf>
- CPF Board, How much CPF contributions to pay, upd. 19 Oct 2026: <https://www.cpf.gov.sg/employer/employer-obligations/how-much-cpf-contributions-to-pay>
- CPF Board, What constitutes wages for CPF contributions, upd. 06 Oct 2026: <https://www.cpf.gov.sg/employer/employer-obligations/what-constitutes-wages-for-cpf-contributions>
- CPF Board, What is the OW ceiling, upd. 14 Aug 2026: <https://www.cpf.gov.sg/service/article/what-is-the-ordinary-wage-ow-ceiling>
- CPF Board, Examples for computation of AW ceiling (2026): <https://www.cpf.gov.sg/service/sfc/servlet.shepherd/document/download/069IW00000MoFDuYAN>
- CPF Board, Contribution changes (2027 rates), upd. 09 Jun 2026: <https://www.cpf.gov.sg/conrate2023>
- Skills Development Levy Act 1979, version current at 21 Oct 2026: <https://sso.agc.gov.sg/Act/SDLA1979>
- CPF Board, How do I calculate and pay SDL, upd. 1 Jul 2026: <https://www.cpf.gov.sg/service/article/how-do-i-calculate-and-pay-the-skills-development-levy-sdl>
- SWDA, OurWorkforce SDL page: <https://www.ourworkforce.gov.sg/e-services/skills-development-levy>
- CPF Board, Contributions to self-help groups, upd. 22 Sep 2026: <https://www.cpf.gov.sg/employer/employer-obligations/contributions-to-self-help-groups>
- CDAC, Funding info and information for employers (rates eff. 1 Jan 2015): <https://www.cdac.org.sg/cdac-funding-info> and <https://www.cdac.org.sg/cdac-funding-info-information-for-employers>
- Eurasian Association, ECF FAQ, upd. September 2022: <https://www.eurasians.sg/s/ECF-FAQ.pdf>
- MUIS, MBMF employer information, upd. 21 Feb 2025 (rates eff. 1 Jun 2016): <https://www.muis.gov.sg/give-back/mbmf/employer-information/>
- SINDA, Fund contribution, and rate revision notice of 30 Aug 2014 (eff. January 2015): <https://www.sinda.org.sg/donate/sindafundcontribution/> and <https://www.sinda.org.sg/newsroom/fund-contribution/>
- MOM, S Pass levy and quota requirements, upd. 19 Feb 2026: <https://www.mom.gov.sg/passes-and-permits/s-pass/quota-and-levy/levy-and-quota-requirements>
- MOM, What is the foreign worker levy, upd. 1 Jul 2026: <https://www.mom.gov.sg/passes-and-permits/work-permit-for-foreign-worker/foreign-worker-levy/what-is-the-foreign-worker-levy>
- MOM, Paying the levy, upd. 8 Jul 2026: <https://www.mom.gov.sg/passes-and-permits/work-permit-for-foreign-worker/foreign-worker-levy/paying-the-levy>
- MOM, Services sector requirements, upd. 16 Sep 2026: <https://www.mom.gov.sg/passes-and-permits/work-permit-for-foreign-worker/sector-specific-rules/services-sector-requirements>

Malaysia

- KWSP, EPF Act 1991 Third Schedule from 1 Oct 2025: <https://www.kwsp.gov.my/documents/d/guest/third_schedule_from_-1-october-2025>
- KWSP, Employer mandatory contribution (rates, examples, FAQ): <https://www.kwsp.gov.my/en/employer/responsibilities/mandatory-contribution>
- KWSP, Contribution for non-Malaysian citizen employees (eff. October 2025 wages): <https://www.kwsp.gov.my/en/employer/responsibilities/non-malaysian-citizen-employees>
- KWSP, Managing non-Malaysian citizen employees in i-Akaun (Employer): <https://www.kwsp.gov.my/documents/d/guest/managing-non-malaysian-citizen-employees-in-i-akaun-employer-verification-registration-contributions>
- KWSP, Form KWSP 17A/18A (AHL) i-Topup, version V20251021: <https://www.kwsp.gov.my/documents/d/guest/borang-permohonan-pendaftaran_pembatalan-mencarum-melebihi-kadar-berkanun-kwsp17a-kwsp-18a-pdf>
- KWSP, Preparing CSV file for e-Caruman, June 2020: <https://www.kwsp.gov.my/documents/d/guest/easy-guide_preparing-csv-file-for-e-caruman>
- KWSP, e-Caruman FAQ, 19 May 2017: <https://secure.kwsp.gov.my/e-caruman/download/SOALAN_LAZIM_e-Caruman_EN_as_at_19052017.pdf>
- PERKESO, Contributions: <https://www.perkeso.gov.my/en/our-services/employer-employee/contributions.html>
- PERKESO, Rate of contribution (ceiling RM6,000 from 1 Oct 2024): <https://www.perkeso.gov.my/en/rate-of-contribution.html>
- PERKESO, Ceiling increase FAQ, 1 Oct 2024: <https://www.perkeso.gov.my/images/dokumen/011024%20-%20FAQ%20PENINGKATAN%20HAD%20SILING%20GAJI%20DARI%20RM5K%20KEPADA%20RM6K%20DI%20BAWAH%20AKSP%20969%20AKTA%204%20%20ASIP%202017%20AKTA%20800.pdf>
- PERKESO, Act 4 contribution table including SKBBK, eff. 1 Jun 2026: <https://www.perkeso.gov.my/images/lindung/lindung-24-jam/NewContributionRateIncludingSKBBK.pdf>
- PERKESO, Act 800 contribution table (RM6,000 ceiling): <https://www.perkeso.gov.my/images/dokumen/151124-Rate%20Contribution%20ACT%20800.pdf>
- PERKESO, LINDUNG 24 Jam FAQ, 25 Jun 2026: <https://www.perkeso.gov.my/images/lindung/lindung-24-jam/25062026-FAQ_LINDUNG_24_JAM_EN.pdf>
- PERKESO, Foreign workers: <https://www.perkeso.gov.my/en/our-services/protection/foreign-worker.html>
- PERKESO, Invalidity Scheme for foreign workers FAQ, 25 Jul 2024: <https://www.perkeso.gov.my/images/pekerja_asing/250724%20-FAQ%20-%20INVALIDITY%20SCHEME%20FOREIGN%20WORKER.pdf>
- PERKESO, Domestic workers: <https://perkeso.gov.my/en/our-services/protection/domestic-workers.html>
- PERKESO, FAQ: <https://www.perkeso.gov.my/en/contact-us/pejabat-perkeso-new/frequently-asked-question.html>
- Employment Insurance System Act 2017 (Act 800), as enacted: <https://www.perkeso.gov.my/images/imej/akta_dan_peraturan/EMPLOYMENT_INSURANCE_SYSTEM_ACT_2017_Act_800.pdf>
- PERKESO, Combined SOCSO + EIS text file format v2.1 (dated 13 Feb 2026): <https://perkeso.gov.my/images/borang/lindung24jam/28072026-formatteksfail.pdf>; v2.0: <https://www.perkeso.gov.my/images/borang/lindung24jam/formatteksfail.pdf>
- PERKESO, Text file format FAQ: <https://www.perkeso.gov.my/images/lindung/lindung-24-jam/FAQ_TextFileFormat_EN.pdf>
- LHDN, MTD computerised calculation specification 2026, upd. 01 Jan 2026: <https://www.hasil.gov.my/wp-content/uploads/spesifikasi-kaedah-pengiraan-berkomputer-pcb-2026.pdf>
- LHDN, MTD schedule and data specifications page, upd. 29/07/2026: <https://www.hasil.gov.my/en/majikan/jadual-pcb-dan-spesifikasi-data/>
- LHDN, MTD testing questions 2026 (answers due before 1 Oct 2026): <https://www.hasil.gov.my/wp-content/uploads/mtd-testing-question-2026.pdf>
- LHDN, TP1 2026 explanatory notes: <https://www.hasil.gov.my/wp-content/uploads/bi-explanatory-notes-for-from-tp1-2026-1.pdf>
- LHDN, Tax rate (YA 2023-2025), upd. 26/06/2026: <https://www.hasil.gov.my/en/individu/kadar-cukai/>
- LHDN, Employer responsibilities: <https://www.hasil.gov.my/en/majikan/tanggungjawab-majikan/>
- LHDN, RF filing programme for 2026, incl. C.P.8D layout Pin. 2025: <https://www.hasil.gov.my/wp-content/uploads/rf-filing-programme-for-2026.pdf>
- LHDN, EA/EC guide notes 2025: <https://www.hasil.gov.my/wp-content/uploads/nota_panduan_ea_2025___ec_2025_1.pdf>
- LHDN, Borang EA C.P.8A Pin. 2023: <https://www.hasil.gov.my/wp-content/uploads/borang_ea__c.p.8a_-_pin._2023_.pdf>
- LHDN, Form E 2025 sample (HTTP 404 on 2026-10-21; content seen through the search index only): <https://www.hasil.gov.my/media/forms/upload/form_f090f7b4-d0d5-41e3-9615-79a00b973bde/d7c8c297-bc05-4c42-a8d9-b0e054a66f6a/sample_of_form_e_2025_2.pdf>
- HRD Corp, Levy calculation guideline: <https://supportcentre.hrdcorp.gov.my/portal/en/kb/articles/hrd-levy>
- HRD Corp, Registered employers: <https://hrdcorp.gov.my/registered-employers>
- HRD Corp, Circulars (Employer Circular 1/2026): <https://hrdcorp.gov.my/circulars>
