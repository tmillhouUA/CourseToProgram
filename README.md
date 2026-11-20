# InfoSci course → program dataset (graduate + undergraduate)

Gathered 2026-11-20 for the University of Arizona College of Information Science.

- **Graduate (11 programs):** from https://infosci.arizona.edu/graduate-programs/graduate and the curriculum pages and Overview PDFs it links to.
- **Undergraduate (18 programs):** from the programs' fillable checklist PDFs on Box, which the user downloaded and supplied. The undergraduate webpages list almost no courses themselves. Degree and minor checklists are "Catalog: Fall 2026+". Certificate checklists are AY 2025–26.

## Files
- `course_program_data.json`: the dataset to build from (schema below).
- `course_program_map.csv`: the explicitly named rows, flattened. One row per course × program × requirement group.
- `data.js`: the same data as a JavaScript global (`const DATA = {...}`), loaded by the search page.
- `build_data.py`: the script that generates all three data files, writing them next to itself. Edit it and run it again to update.
- `index.html`, `style.css`, `app.js`: the search page. Open `index.html` directly or host the folder on GitHub Pages. No server or build step needed.

## JSON schema
- `programs[]`: `id, name, level (Graduate|Undergraduate), kind (Degree|Minor|Certificate), units, url, pdf, notes`. For undergraduate programs, `pdf` is the Box checklist link.
- `rows[]`: `program, course ("ISTA 498"), title, group, role, group_rule, note, source`.
  - `title` is the course title as that program's source lists it. Titles vary between checklists (e.g., ISTA 320 is "Data Visualization" in one and "Applied Data & Visualization" in another).
  - `source` is one of "Program webpage", "Overview PDF" or "Checklist PDF".
- `rules[]`: general elective rules for courses that count without being named (graduate only). Fields: `program, group, role, prefixes[], ranges[[lo,hi]], exclude[], text`. Ranges apply to the numeric part of the course number, so `150B1` is read as 150.
- `roles{}`: role key → display label and description. Ordered from strongest to weakest:
  - `required`: everyone in the program takes it.
  - `required_opt`: required within one subplan, emphasis or option.
  - `either_or`: one of a small set of named alternatives for a required slot.
  - `culminating`: one option for an internship, capstone, engagement, report or thesis requirement.
  - `distribution`: one of several courses that can fill a required single-course category, such as Society or Research Methods.
  - `restricted`: an elective from a named list ("choose N").
  - `recommended`: suggested for a specialty; not a requirement.
  - `rule`: counts under a general elective rule.
  - `approval`: may count, subject to approval.
- `cross{}`: only cross-listings a source states explicitly. Currently that is just LIS 646 = NURS 646.
- `catalog{}`: course code → title.

## Lookup logic
1. Normalize the input: uppercase it and put one space between prefix and number (`ista498` → `ISTA 498`).
2. Return every `rows[]` entry for the course.
3. Apply each `rules[]` entry: the prefix matches, the number is in a range, and the course is not in `exclude`. Apply it even if that program also has a named row for the course, and show both uses (e.g., INFO 550 is recommended in an MSDS specialty and also counts as an MSDS elective). The `exclude` lists keep core courses from also appearing as general electives. Skip a rule only when the program already names the course in that rule's own group.
4. Do not merge courses that merely share a number across prefixes.

## Caveats
### Prefixes and numbering (kept as listed, not merged)
- **INFO/LIS 5xx.** Both prefixes use the same numbers (570, 608, 671 and others) with near-identical titles. They are treated as separate courses.
- **CYBV / NETV / APCV vs. CYBR.** The two cyber certificate checklists (AY 25–26) use CYBV, NETV and APCV. The Fall 2026 degree and minor checklists use CYBR, with many matching numbers and titles (e.g., CYBV 470 and CYBR 470 are both C Programming). A search for CYBR 470 will **not** surface the Cyber Operations certificate. Confirm whether CYBV courses were renumbered as CYBR, and whether the certificate checklists have Fall 2026 versions.
- **Algorithms for Games.** It is listed as ISTA 425 in the Game Design minor and ISTA minor checklists, and as GAME 425 everywhere else.
- **Intro to NLP.** It is ISTA 335 in the ISTA minor and ISTA 355 in the BS in Information Science.
- **Business Information.** It is LIS 385 in the ETS minor and LIS 435 in the ETS BA and LIS minor.
- **Augmented Reality.** It is ISTA 427 in the BS in Information Science and GAME 427 in Game Development.

### Checklist errors flagged in `note`
- "LIST 470" was recorded as LIS 470, and "ECOS 300" as ESOC 300.
- The BA ETS Research Methods list is identical to its Advanced Core list, which is probably a copying error. Every Advanced Core course therefore also shows as a Research Methods option for the BA ETS.
- Several minor checklists state the upper-division minimum as "3 units (9 classes)". That is presumably 9 units (3 classes); it isn't used in the data.

### Graduate (unchanged from the first pass)
- **Webpage vs. PDF discrepancies:**
  - MSIS: the PDF adds HSD 520 and INFO 524 to the HCC electives and leaves out INFO 502 in both subplans.
  - MLIS: the PDF adds LIS 552 to the Cultural Perspective distribution category.
  - MSDS: the PDF names specific electives, while the webpage says any INFO 500–590/600–690 course counts.
- **Not captured:**
  - earlier-cohort requirement sets
  - the PhD research-methods courses, which aren't named
  - the PhD minor's approved course list, which isn't published
  - MLIS Free Electives (any related coursework)
  - the Digital Curation certificate's unnamed capstone

### Not included anywhere
- General education and university requirements (WRIT, UNIV, gen-ed categories, language), except where a major names specific courses, such as MATH 112 in the BS Cyber Operations.
- Prerequisites. The checklists list them, but they aren't stored here.

### Official source
The UA Academic Catalog is authoritative. Its course lists load with JavaScript and could not be read in this pass.
