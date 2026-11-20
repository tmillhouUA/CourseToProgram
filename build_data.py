"""Build the course -> program requirement dataset for UA College of Information Science
graduate programs, from infosci.arizona.edu (gathered 2026-11-20)."""
import json, csv, re, os

# ---------------------------------------------------------------- course titles
# From https://infosci.arizona.edu/programs/courses (graduate section) plus program pages.
CATALOG = {}
def add(prefix, items):
    for num, title in items:
        CATALOG[f"{prefix} {num}"] = title

add("CYBR", [("500","Security Programming"),("501","Principles of Cybersecurity"),("505","AI Foundations in Cyber Operations"),
    ("523","Covert Python"),("525","Cyber Physical Systems"),("528","Operational Tradecraft in the Information Environment"),
    ("529","Cyber Law, Ethics and Policy"),("535","Secure Critical Infrastructures with Artificial Intelligence"),("579","Cloud Security"),
    ("599","Independent Study"),("605","AI Agents in Cyber Operations"),("626","Traffic Analysis"),("660","Zero Trust Defensive Techniques"),
    ("680","Advanced Computational Propaganda"),("685","Information Warfare"),("692","Directed Research"),
    ("696","Advanced Topics in Cyber and Information Operations"),("908","Case Study in Cyber Operations"),
    ("909","Masters Report in Cyber Operations"),("910","Masters Thesis in Cyber Operations")])
add("GAME", [("526","Game Artificial Intelligence"),("562","3D Modeling for Games")])
add("INFO", [("501","Designing an Installation"),("502","Data Ethics"),("504","Digital Media: Impact and Innovations"),
    ("505","Foundations of Information"),("507","Information Research Methods"),("508","Qualitative Research in Information Science"),
    ("510","Bayesian Modeling and Inference"),("511","Foundations of Data Science"),("514","Computational Social Science"),
    ("515","Organization of Information"),("516","Introduction to Human Computer Interaction"),
    ("518","Information Trust, Manipulation, and Deception"),("520","Ethical Issues in Information"),("521","Machine Learning"),
    ("523","Data Mining and Discovery"),("524","Virtual Reality"),("525","Algorithms for Games"),("526","Data Analysis and Visualization"),
    ("527","Augmented Reality"),("529","Applied Cyberinfrastructure Concepts"),("531","Data Warehousing and Analytics in the Cloud"),
    ("533","Medical On-Line Searching"),("536","Data Science and Public Interests"),("539","Statistical Natural Language Processing"),
    ("540","Introduction to Archives"),("550","Artificial Intelligence"),("551","Game Development"),("552","Advanced Game Development"),
    ("554","Informatics in Biology"),("555","Applied Natural Language Processing"),("556","Text Retrieval and Web Search"),
    ("557","Neural Networks"),("558","Social Justice in Information Services"),("560","Serious STEM Games"),("561","Game Physics"),
    ("567","Leadership and the Information Organization"),("570","Data Base Development and Management"),
    ("571","Introduction to Information Technology"),("575","User Interface and Website Design"),
    ("576","Inventioneering: Design, Health, Emerging Technologies, and Societal Grand Challenges"),("577","Information Security"),
    ("578","Science Information and its Presentation"),("579","SQL/NoSQL Databases for Data and Information Science"),
    ("580","Data Standards for the Semantic Web"),("584","Intellectual Property and Copyright"),("587","Information Seeking Behaviors"),
    ("589","Scholarly Communication"),("592","Directed Research"),("595","Special Topics in Information Science, Technology, and Arts"),
    ("601","Intro to Geographic Information Systems & Tech I"),("608","Managing the Information Organization"),
    ("621","Advanced Machine Learning Applications"),("640","Advanced Archives: Archival Appraisal and Description"),
    ("671","Introduction to Digital Curation and Preservation"),("672","Introduction to Applied Technology"),
    ("673","Management for Information Professionals"),("675","Advanced Digital Collections"),("692","Directed Research"),
    ("693","Internship"),("696E","Graduate Seminar"),("698","Capstone Project"),("699","Independent Study"),("920","Dissertation")])
add("ISTA", [("599","Independent Study")])
add("LIS", [("504","Foundations of Library and Information Services"),("506","Research Methods for Library and Information Professionals"),
    ("508","Qualitative Research in Information Science"),("515","Organization of Information"),
    ("518","Information Trust, Manipulation, and Deception"),("520","Ethical Issues in Information"),
    ("521","Children's and Young Adult Literature in a Multicultural Society"),("523","Early Childhood and Public Libraries"),
    ("528","Applied AI Literacies in Information Practice"),("529","AI and the Art & Design of Learning"),
    ("530","Cataloging and Metadata Management"),("532","Information Intermediation"),("533","Medical Online Searching"),
    ("535","Business Information"),("540","Introduction to Archives"),("541","Preservation"),
    ("542","Curating & Preserving Media Art Collections"),("546","History of Books after Gutenberg"),("547","Data Literacy"),
    ("549","Cultural Heritage Informatics"),("550","Information Environments from Non-Dominant Perspectives"),
    ("551","Global Librarianship"),("552","Cultural Heritage Collections: Object Itineraries, Curation, and Management"),
    ("557","Documenting Diverse Cultures and Communities"),("558","Social Justice in Information Services"),
    ("559","Marketing of Library and Information Services to Communities"),("560","Collection Management"),
    ("563","Readers' Advisory Services in Public Libraries"),("565","Information Architecture and Controlled Vocabularies"),
    ("567","Leadership and the Information Organization"),("570","Database Development and Management"),
    ("571","Introduction to Information Technology"),("572","Government Information: Policy & Resources"),
    ("578","Science Information and its Presentation"),("580","Data Standards for the Semantic Web"),
    ("582","Young Adults and Public Libraries"),("584","Intellectual Property/Copyright"),("587","Information Seeking"),
    ("589","Scholarly Communication"),("608","Managing the Information Organization"),("624","Community Health and Medical Informatics"),
    ("640","Advanced Issues in Archival Enterprise"),("641","Community-focused Archives and Museums"),
    ("646","Healthcare Informatics: Theory and Practice"),("671","Digital Curation and Digital Preservation"),
    ("672","Introduction to Applied Technology"),("673","Management for Information Professionals"),("675","Advanced Digital Collections"),
    ("681E","Law Library Practice and Administration"),("692","Directed Research"),("693","Internship"),("698","Capstone Exit Requirement"),
    ("699","Independent Study"),("909","ePortfolio (Electronic Portfolio)"),("920","Dissertation Research")])
# Outside-college courses named on program pages
CATALOG.update({
    "CSC 522":"Parallel and Distributed Computing","MIS 584":"Big Data Technologies","MATH 574M":"Statistical Machine Learning",
    "STAT 571A":"Advanced Statistical Regression Analysis","ECE 523":"Engineering Applications of Machine Learning and Data Analytics",
    "SIE 549":"Optimization for Machine Learning","SFWE 503":"Software Project Management","SIE 532":"Sports Analytics",
    "LING 581":"Advanced Computational Linguistics","LING 582":"Advanced Statistical Natural Language Processing",
    "ECE 524":"Fundamentals of Cloud Security","MIS 547":"Fundamentals of Cloud Computing and its Design Strategies",
    "HSD 520":"Makerspace","LAW 689":"Advanced Legal Research","NURS 646":"Healthcare Informatics: Theory and Practice",
})

# ---------------------------------------------------------------- programs
P = "https://infosci.arizona.edu"
PROGRAMS = [
 dict(id="MSCO", name="MS in Cyber Operations", kind="Degree", units="30", url=f"{P}/ms-cyber-operations/curriculum-courses",
      pdf=f"{P}/sites/default/files/2026-08/MS-in-Cyber-Operations-Overview-and-Curriculum.pdf",
      notes="Requirements for students admitted Fall 2026 and later. Earlier cohorts follow a separate requirement set (not captured)."),
 dict(id="MSDS", name="MS in Data Science", kind="Degree", units="30", url=f"{P}/ms-data-science/curriculum-courses",
      pdf=f"{P}/sites/default/files/2026-08/MS-in-Data-Science-Overview-and-Curriculum.pdf",
      notes="Curriculum page is labeled 'Fall 2024 requirements'. Students admitted Fall 2023–Summer 2024 follow a separate document (not captured)."),
 dict(id="MSIS", name="MS in Information Science", kind="Degree", units="30", url=f"{P}/ms-information-science/curriculum-subplans-courses",
      pdf=f"{P}/sites/default/files/2026-08/MS-in-Information-Science-Overview-and-Curriculum.pdf",
      notes="Two subplans: Human-Centered Computing (HCC) and Machine Learning (ML). Legacy curriculum for students admitted before Spring 2023 not included."),
 dict(id="MLIS", name="MA in Library & Information Science", kind="Degree", units="37", url=f"{P}/ma-library-information-science/curriculum-specialties-courses",
      pdf=f"{P}/sites/default/files/2026-08/MA-in-Library-and-Information-Science-Overview-and-Curriculum.pdf",
      notes="Also 6 units of Free Electives: any related coursework, including courses outside the college (not matchable by course number). Specialties are recommendations, not official concentrations."),
 dict(id="PHD", name="PhD in Information", kind="Degree", units="63", url=f"{P}/phd-information/curriculum-courses",
      pdf=f"{P}/sites/default/files/2024-04/PhD%20in%20Information%20Overview%20and%20Curriculum.pdf",
      notes="6 units of research-methods coursework 'matching the student's research' are required but no courses are named. Also a 9–15 unit outside minor."),
 dict(id="PHDMIN", name="PhD Minor in Information", kind="Minor", units="9", url=f"{P}/phd-information/minor", pdf="",
      notes="9 units of approved College of Information Science courses (grade B or better). No approved list is published; the page directs students to the minor coordinator."),
 dict(id="C-ARCH", name="Graduate Certificate in Archival Studies", kind="Certificate", units="12", url=f"{P}/graduate-certificates/archival-studies", pdf="", notes=""),
 dict(id="C-CYBR", name="Graduate Certificate in Cyber Operations", kind="Certificate", units="18", url=f"{P}/graduate-certificates/cyber-operations", pdf="",
      notes="Stackable into the MS in Cyber Operations."),
 dict(id="C-DCUR", name="Graduate Certificate in Digital Curation", kind="Certificate", units="12", url=f"{P}/graduate-certificates/digital-information", pdf="",
      notes="Page also mentions a capstone 'normally taken last' but names no course for it."),
 dict(id="C-FDS", name="Graduate Certificate in Foundations of Data Science", kind="Certificate", units="9", url=f"{P}/graduate-certificates/foundations-data-science", pdf="", notes=""),
 dict(id="C-LEGAL", name="Graduate Certificate in Legal Information", kind="Certificate", units="15", url=f"{P}/graduate-certificates/legal-information", pdf="", notes=""),
]

# ---------------------------------------------------------------- roles
ROLES = {
 "required":     ("Required", "Every student in the program must take this course."),
 "required_opt": ("Required in a subplan / option", "Required for students in a particular subplan, track or option."),
 "either_or":    ("Required: one of alternatives", "Satisfies a required slot that can also be met by another named course."),
 "distribution": ("Distribution requirement option", "One of several courses that can fill a required category (e.g., one course per category)."),
 "restricted":   ("Listed elective (choose from list)", "Counts toward an elective group limited to a named list of courses."),
 "culminating":  ("Culminating / experiential option", "One of the options for an internship, capstone, report or thesis requirement."),
 "recommended":  ("Recommended (specialty)", "Recommended for a specialty or emphasis; not itself a requirement."),
 "rule":         ("Counts as a general elective", "Not named, but eligible under a general rule (e.g., any 500-level INFO course)."),
 "approval":     ("Eligible with approval", "May count, subject to advisor or committee approval."),
}

rows = []
def r(prog, course, group, role, rule="", note="", source="Program webpage", title=None):
    """title: the title as the program's own source lists it (undergraduate checklists vary)."""
    if title and course not in CATALOG:
        CATALOG[course] = title
    assert course in CATALOG, course
    assert role in ROLES
    rows.append(dict(program=prog, course=course, title=title or CATALOG[course], group=group, role=role,
                     group_rule=rule, note=note, source=source))

# ---- MS Cyber Operations
g, rule = "Core (21 units)", "All seven core slots required"
r("MSCO","CYBR 500",g,"either_or",rule,"Required if no programming experience in the past 3 years; otherwise INFO 521 may be taken instead.")
r("MSCO","INFO 521",g,"either_or",rule,"Alternative to CYBR 500 for students with recent programming experience.")
for c in ["CYBR 501","CYBR 505","CYBR 523","CYBR 579","CYBR 626","CYBR 660"]:
    r("MSCO",c,g,"required",rule)
g, rule = "Electives (6 units)", "Report option: two of CYBR 525, CYBR 605, INFO 536, INFO 621. Thesis option: CYBR 692 + one elective."
for c in ["CYBR 525","CYBR 605","INFO 536","INFO 621"]:
    r("MSCO",c,g,"restricted",rule)
r("MSCO","CYBR 696",g,"restricted",rule,"On the elective list, but not among the four named for the report option.")
r("MSCO","CYBR 692",g,"required_opt",rule,"Required for the thesis option.")
g, rule = "Culminating course (3 units)", "Choose one"
r("MSCO","CYBR 908",g,"culminating",rule)
r("MSCO","CYBR 909",g,"culminating",rule,"Report option (no committee).")
r("MSCO","CYBR 910",g,"culminating",rule,"Thesis option (committee + oral defense).")

# ---- MS Data Science
g, rule = "Core (12 units)", "All four required"
for c in ["INFO 502","INFO 511","INFO 523","INFO 526"]:
    r("MSDS",c,g,"required",rule)
g, rule = "Experiential (3 units)", "Internship or capstone"
r("MSDS","INFO 693",g,"culminating",rule)
r("MSDS","INFO 698",g,"culminating",rule,"Requires a software development component.")
for c in ["INFO 514","INFO 521","INFO 529","INFO 531","INFO 536","INFO 555","INFO 556","INFO 557","INFO 570","INFO 578","INFO 579","INFO 580"]:
    r("MSDS",c,"Electives (15 units)","restricted","15 units of electives","Named in the Aug 2026 overview PDF's elective list; also eligible under the general INFO elective rule.","Overview PDF")
SPEC = {
 "Database Management & Architecture": ["CSC 522","INFO 529","INFO 531","INFO 570","INFO 579","INFO 580","MIS 584"],
 "Data Mining & Statistical Analysis": ["INFO 521","INFO 531","INFO 556","INFO 557","INFO 621","MATH 574M","STAT 571A"],
 "Machine Learning & AI": ["ECE 523","INFO 521","INFO 539","INFO 550","INFO 557","INFO 621","SIE 549"],
 "Managerial & Applied Data Science": ["INFO 514","INFO 515","INFO 578","INFO 587","INFO 608","SFWE 503","SIE 532"],
 "Natural Language Processing": ["INFO 539","INFO 555","INFO 556","LING 581","LING 582"],
 "Web Technologies & Cloud Computing": ["ECE 524","INFO 529","INFO 531","INFO 570","INFO 571","INFO 577","MIS 547"],
}
for spec, cs in SPEC.items():
    for c in cs:
        note = "Counts toward the 15 elective units." if c.startswith("INFO") else "Outside-department course listed as a specialty recommendation; counts toward electives."
        r("MSDS",c,f"Specialty: {spec}","recommended","Recommended courses; specialties have no selection rules",note)

# ---- MS Information Science
g = "Core (9 units)"
for c in ["INFO 505","INFO 526"]:
    r("MSIS",c,g,"required","Core in both subplans")
r("MSIS","INFO 516",g,"required_opt","Subplan core","Required in the Human-Centered Computing subplan.")
r("MSIS","INFO 521",g,"required_opt","Subplan core","Required in the Machine Learning subplan.")
g, rule = "Experiential (3 units)", "Internship or capstone"
r("MSIS","INFO 693",g,"culminating",rule)
r("MSIS","INFO 698",g,"culminating",rule)
g, rule = "HCC subplan electives (9 units)", "Choose three"
for c in ["INFO 501","INFO 502","INFO 525","INFO 551","INFO 552","INFO 575"]:
    note = "Listed on the curriculum page but not in the Aug 2026 overview PDF." if c=="INFO 502" else ""
    r("MSIS",c,g,"restricted",rule,note)
for c in ["HSD 520","INFO 524"]:
    r("MSIS",c,g,"restricted",rule,"Listed in the Aug 2026 overview PDF but not on the curriculum page.","Overview PDF")
g = "ML subplan electives (9 units)"
for c in ["INFO 502","INFO 510","INFO 523","INFO 539","INFO 550","INFO 555","INFO 556","INFO 557"]:
    note = "Listed on the curriculum page but not in the Aug 2026 overview PDF." if c=="INFO 502" else ""
    r("MSIS",c,g,"restricted",rule,note)

# ---- MA Library & Information Science
g = "Core (9 units)"
for c in ["LIS 504","LIS 506","LIS 515"]:
    r("MLIS",c,g,"required","All three required")
r("MLIS","LIS 909","ePortfolio (1 unit)","required","Required")
r("MLIS","LIS 698","Capstone internship (3 units)","required","Required","Prerequisites: 18 units completed plus LIS 504, 506 and 515.")
DIST = {
 "Cultural Perspective on Libraries & Information": ["LIS 550","LIS 551","LIS 557","LIS 558"],
 "Information Services & Evaluation": ["LIS 530","LIS 532","LIS 533","LIS 535","LIS 540","LIS 560","LIS 572","LIS 671"],
 "Management of Information Services": ["LIS 567","LIS 608","LIS 673","LIS 681E"],
 "Information Technology & Networked Digital Information": ["LIS 528","LIS 570","LIS 571","LIS 580","LIS 672","LIS 675"],
}
for cat, cs in DIST.items():
    for c in cs:
        r("MLIS",c,f"Distributed electives: {cat}","distribution","12 units: one course from each of four categories")
r("MLIS","LIS 552","Distributed electives: Cultural Perspective on Libraries & Information","distribution",
  "12 units: one course from each of four categories","Listed in the Aug 2026 overview PDF but not on the curriculum page.","Overview PDF")
MSPEC = {
 "Academic Librarianship": "518 530 532 541 550 559 608 671 672 675 693 699",
 "AI Across the Discipline": "518 520 528 529 530 547 549 578 580 584 587 646 671",
 "Archives & Special Collections": "530 540 541 549 550 552 557 558 560 567 570 571 572 584 608 640 641 671 672 673 693 699",
 "Cultural Heritage": "508 530 540 541 542 546 549 550 551 552 557 560 578 580 584 640 641 671 675 699",
 "Digital Curation": "518 532 567 570 572 584 587 589 624 646 671 672 673 675 693 699",
 "Law Librarianship & Legal Information": "518 532 558 559 567 570 572 584 587 608 671 672 681E 693 699",
 "Public Librarianship": "518 521 523 530 532 550 557 558 559 560 563 567 570 571 572 582 584 587 608 671 672 673 693 699",
}
for spec, nums in MSPEC.items():
    for n in nums.split():
        r("MLIS",f"LIS {n}",f"Specialty: {spec}","recommended","Recommended courses (specialties are not official concentrations)","Counts toward LIS electives.")
r("MLIS","NURS 646","Specialty: AI Across the Discipline","recommended","Recommended courses","Cross-listed with LIS 646.")
r("MLIS","NURS 646","Specialty: Digital Curation","recommended","Recommended courses","Cross-listed with LIS 646.")

# ---- PhD in Information
r("PHD","INFO 507","First-year required course (3 units)","required","Required in year 1")
for c in ["INFO 696E"]:
    r("PHD",c,"Graduate seminars (6 units)","required","Two research seminars","Typically one or two offered per year; seminars in other departments need advisor approval.")
for c in ["INFO 692","LIS 692"]:
    r("PHD",c,"Directed research (9 units)","required","9 units (usually three projects with three faculty)","Listed as 'LIS/INFO 692'.")
for c in ["INFO 920","LIS 920"]:
    r("PHD",c,"Dissertation (18 units)","required","18 units after comprehensive exams","Listed as 'LIS/INFO 920'.")

# ---- Certificates
g = "Required (9 units)"
for c in ["LIS 540","LIS 640","LIS 671"]:
    r("C-ARCH",c,g,"required","All three required")
for c in ["LIS 530","LIS 541","LIS 557","LIS 570","LIS 584","LIS 641","LIS 672","LIS 673","LIS 675","LIS 693","LIS 699"]:
    r("C-ARCH",c,"Elective (3 units)","restricted","Choose one")

for c in ["CYBR 500","CYBR 501","CYBR 505","CYBR 660"]:
    r("C-CYBR",c,"Core (12 units)","required","All four required")
for c in ["CYBR 523","CYBR 525","CYBR 579","CYBR 626","CYBR 696","INFO 502","INFO 621"]:
    r("C-CYBR",c,"Electives (6 units)","restricted","Choose two of seven")

for c in ["LIS 671","LIS 672"]:
    r("C-DCUR",c,"Required (6 units)","required","Both required")
for c in ["INFO 531","INFO 556","INFO 570","INFO 579","INFO 580","INFO 675","LIS 541","LIS 560","LIS 565","LIS 584"]:
    r("C-DCUR",c,"Electives (6 units)","restricted","Choose two of ten")

for c in ["INFO 523","INFO 526"]:
    r("C-FDS",c,"Required (6 units)","required","Both required")
for c in ["INFO 502","INFO 520"]:
    r("C-FDS",c,"Ethics requirement (3 units)","either_or","Take one of INFO 502 or INFO 520")

r("C-LEGAL","LAW 689","Required (9 units)","required","Three required slots")
r("C-LEGAL","LIS 693","Required (9 units)","required","Three required slots","Tucson students encouraged to intern at the Cracchiolo Law Library.")
for c, alt in [("LIS 572","LIS 681E"),("LIS 681E","LIS 572")]:
    r("C-LEGAL",c,"Required (9 units)","either_or","Three required slots",f"Alternative to {alt}.")

# ================================================================ UNDERGRADUATE
# Source: the programs' fillable checklist PDFs (Box), downloaded and supplied by the user 2026-11-20.
# Degrees and minors: "Catalog: Fall 2026+". Certificates: "AY 25-26" (last updated Fall 2025).
for p in PROGRAMS:
    p.setdefault("level", "Graduate")

CK = "Checklist PDF"
UG = [
 ("BAS-CD","BAS in Cyber Defense","Degree","120","/bas-cyber-defense/curriculum-emphasis-courses","77nmpz7k6t1icbr3l9uwvib4kfg1ihg6",
  "Major GPA 2.0; 42 upper-division units. Math foundation options are listed in the checklist's advisor notes (not mapped)."),
 ("BS-CYBR","BS in Cyber Operations","Degree","120","/bs-cyber-operations/curriculum-courses","5mmczne04jpsegn2vis3n4yf773kdotf",
  "Choose one emphasis (AI or Security), 27 units; all nine courses in the chosen emphasis are required."),
 ("BA-ETS","BA in Emerging Technologies in Society","Degree","120","/ba-emerging-technologies-society/curriculum-courses","b0v5ps6yatzst3t2gk2xdrfwbandqkcf",
  "Minor or second major required. The checklist's Research Methods list is identical to its Advanced Core list, which looks like a copying error (other programs list ESOC 301/302)."),
 ("BA-GD","BA in Game Design","Degree","120","/ba-game-design/curriculum-courses","t6pzdvfg7my9hi6txe9rs0y38q94zhn5",
  "Minor or second major required. Fourth-semester language proficiency."),
 ("BS-GD","BS in Game Development","Degree","120","/bs-game-development/curriculum-courses","207syux4k2txvmrilpf24cauepg1g8oo",
  "Minor or second major required."),
 ("BS-IS","BS in Information Science","Degree","120","/bs-information-science/curriculum-courses","ytfyfk7qzdrysbrfywzsx68tr4bzj1bz",
  "Minor or second major required. Choose one emphasis (AI, Data Science, or Interactive & Immersive Technologies) and five courses from it."),
 ("BA-ISA","BA in Information Science & Arts","Degree","120","/ba-information-science-arts/curriculum-courses","2h2nfvloet9n30ybt9h0am4w43uztbe1",
  "Minor or second major required."),
 ("MIN-AIS","Minor in AI & Society","Minor","18","/undergraduate-programs/minors/ai-society","v3gp8vmtia2p1ojcfw84qdea4zflfmx3",
  "At least 9 upper-division units. Up to 2 courses may be shared with a major."),
 ("MIN-CYBR","Minor in Cyber Operations","Minor","18","/undergraduate-programs/minors/cyber-operations","77uw0fmcsb4jqs89lb5a5dkp8dz496z8",
  "All six courses required. At least 9 upper-division units."),
 ("MIN-ETS","Minor in Emerging Technologies in Society","Minor","18","/undergraduate-programs/minors/emerging-technologies-society","rarctn36rv9lwqi613dyz6zppc9rkrg1",
  "Four upper-division (300+) courses plus two electives at any level. COMM courses on the list are open only to COMM majors and minors."),
 ("MIN-ESPT","Minor in eSports","Minor","18","/undergraduate-programs/minors/esports","hoii896n97066mlvmnzk8ow06rgimldn",
  "Elective group may also be filled with GAME option courses not already taken."),
 ("MIN-GDES","Minor in Game Design","Minor","18","/undergraduate-programs/minors/game-design","64k0yxs2y9xgibp4uowp7nn0hw92aoxg",
  "At least 3 GAME courses; electives may also be additional GAME courses. At least 9 upper-division units."),
 ("MIN-GDEV","Minor in Game Development","Minor","18","/undergraduate-programs/minors/game-development","bpn906y89nfhhzq18wypif263f1zvf5m",
  "GAME 451 replaces GAME 351 for students who have completed CSC 210 or ISTA 350. At least 9 upper-division units."),
 ("MIN-ISTA","Minor in Information Science, Technology & the Arts","Minor","19","/undergraduate-programs/minors/information-science-technology-arts","a6uj67w6lj2a8mjyt5t8khjpsam5dpo0",
  "At least 6 upper-division units. Electives need not come from the same concentration area."),
 ("MIN-LIS","Minor in Library & Information Science","Minor","18","/undergraduate-programs/minors/library-information-science","i3vftrtsohfub7bdeka4stwdv46se4mv",
  "Up to 2 courses may be shared with a major."),
 ("UCERT-CYBR","Undergraduate Certificate in Cyber Operations","Certificate","18","/undergraduate-certificates/cyber-operations","x6u41kb1izq7ji2oxmbd85nvrdg00ao7",
  "AY 2025–26 checklist; uses CYBV/NETV prefixes, not the CYBR prefix used in the Fall 2026 degree checklists."),
 ("UCERT-CYSEC","Undergraduate Certificate in Cybersecurity","Certificate","18","/undergraduate-certificates/cybersecurity","7ucqiungbwh50ltb4d4yi5fskgdo7hcv",
  "AY 2025–26 checklist; uses CYBV/NETV/APCV prefixes, not the CYBR prefix used in the Fall 2026 degree checklists."),
 ("UCERT-DSV","Undergraduate Certificate in Data Science & Visualization","Certificate","12","/academics/undergraduate/certificates/data-science-visualization","wdxpkxzva6ye74knawk41y7tb3duhs3e",
  "AY 2025–26 checklist."),
]
for pid, name, kind, units, path, box, notes in UG:
    PROGRAMS.append(dict(id=pid, name=name, kind=kind, units=units, level="Undergraduate", url=P+path,
                         pdf=f"https://arizona.app.box.com/s/{box}", notes=notes))

def U(prog, group, role, rule, items, note=""):
    """items: 'CODE|Title' or 'CODE|Title|note'"""
    for it in items:
        parts = it.split("|")
        code, title = parts[0], parts[1]
        n = parts[2] if len(parts) > 2 else note
        r(prog, code, group, role, rule, n, CK, title)

TYPO = "Checklist prints '{}'; recorded as {}."

# ---- BAS Cyber Defense
U("BAS-CD","Supporting coursework (12 units)","required","All required",[
  "CYBR 102|Principles of Cyber Ops II","CYBR 103|Scripting for Cyber Ops I",
  "CYBR 226|Networking for Cyber Ops I","CYBR 228|Networking for Cyber Ops II"])
U("BAS-CD","Major coursework (42 units)","required","All required",[
  "CYBR 302|Linux Security Essentials","CYBR 303|Windows Security Essentials","CYBR 329|Cyber Ethics",
  "CYBR 330|Industrial Controls System Security","CYBR 371|A.I. in Cyber Operations I","CYBR 379|Cloud Computing",
  "CYBR 388|Investigations & Forensics","CYBR 400|Active Cyber Defense","CYBR 435|Cyber Threat Intelligence",
  "CYBR 442|Regulations in Cyber Operations","CYBR 443|Legal & Privacy in Cyber Operations",
  "CYBR 480|Offensive Cyber Operations","CYBR 484|A.I. in Cyber Operations II","CYBR 498|Capstone in Cyber Ops"])

# ---- BS Cyber Operations
U("BS-CYBR","Supporting coursework (18 units)","required","All required",[
  "CYBR 101|Principles of Cyber Ops I","CYBR 102|Principles of Cyber Ops II","CYBR 103|Scripting for Cyber Ops I",
  "CYBR 104|Scripting for Cyber Ops II","MATH 112|College Algebra"])
U("BS-CYBR","Supporting coursework (18 units)","either_or","Statistics: MATH 163 or MATH 263",[
  "MATH 163|Statistics|Listed as 'MATH 163/263'.","MATH 263|Statistics|Listed as 'MATH 163/263'."])
U("BS-CYBR","Major coursework (21 units)","required","All required",[
  "CYBR 226|Networking for Cyber Ops I","CYBR 228|Networking for Cyber Ops II","CYBR 329|Cyber Ethics",
  "CYBR 333|Cryptography","CYBR 379|Cloud Computing","CYBR 400|Active Cyber Defense","CYBR 498|Cyber Operations Capstone"])
U("BS-CYBR","Emphasis: Artificial Intelligence (27 units)","required_opt","All nine required for the AI emphasis",[
  "CYBR 342|Statistics in Information Age","CYBR 361|Data Analysis & Visualization","CYBR 371|AI in Cyber Operations I",
  "CYBR 473|Violent Python","CYBR 474|Adv. Analytics for Security Ops","CYBR 483|Machine Learning in Cyber",
  "CYBR 484|AI in Cyber Operations II","CYBR 485|Deep Learning in Cyber","ISTA 322|Data Engineering"])
U("BS-CYBR","Emphasis: Security (27 units)","required_opt","All nine required for the Security emphasis",[
  "CYBR 310|Intro to Security Programming I","CYBR 311|Intro to Security Programming II","CYBR 388|Investigations & Forensics",
  "CYBR 454|Malware Threat & Analysis","CYBR 470|C Programming","CYBR 471|Assembly","CYBR 479|Wireless Networking",
  "CYBR 480|Offensive Cyber Operations","CYBR 489|OS for Security Professionals"])

# ---- BS Information Science
U("BS-IS","Intro core (15 units)","required","All five required",[
  "ISTA 100|Great Ideas of the Information Age","ISTA 116|Stat Foundations for the Info Age","ISTA 130|Computational Thinking & Doing",
  "ISTA 131|Dealing with Data","ISTA 161|Ethics in a Digital World"])
U("BS-IS","Research methods (3 units)","required","Required",["ESOC 302|Quant. Methods for the Digital Marketplace"])
U("BS-IS","Senior capstone (3 units)","required","Required",["ISTA 498|Senior Capstone"])
U("BS-IS","Computational Arts & Media (3 units)","distribution","Choose 1",[
  "ESOC 200|Visual Content Creation","ESOC 300|Digital Storytelling & Culture","ESOC 340|Info MM Design & Moving Image",
  "ISTA 301|Computing and the Arts","ISTA 302|Technology of Sound","ISTA 329|Intro Web-Design Development",
  "ISTA 352|Images: Past, Present, Future","ISTA 401|Installation Design"])
U("BS-IS","Society (3 units)","distribution","Choose 1",[
  "ESOC 313|Digital Discourse & Identity","ESOC 314|Theories of New Media","ESOC 315|Publishing: From Papyrus to E-Book Readers",
  "ESOC 316|Digital Commerce","ESOC 317|Digital Crime & Social Media","ESOC 318|Disruptive Technologies",
  "ESOC 319|Instructional Technologies","ESOC 330|Digital Dilemmas - Privacy, Property & Access","ESOC 345|Decoding Deceptive Info",
  "ESOC 477|Information Security","ESOC 478|Science Information & its Presentation","ESOC 495|Special Topics in a Digital & Big Data World",
  "INFO 402|Data Ethics","ISTA 495|Special Topics"])
ENGAGE = ["ESOC 480|Digital Engagement","INFO 392|Directed Research|Listed as 'INFO 392/492'.","INFO 492|Directed Research|Listed as 'INFO 392/492'.",
  "INFO 493|Internship","ISTA 391|Preceptorship","ISTA 491|Preceptorship",
  "ISTA 499|Independent Study|Listed as 'ISTA/INFO 499'.","INFO 499|Independent Study|Listed as 'ISTA/INFO 499'."]
U("BS-IS","Engagement / internship / independent study (3 units)","culminating","Choose 1",ENGAGE)
U("BS-IS","Emphasis: Artificial Intelligence (15 units)","restricted","Choose 5 from one emphasis",[
  "ISTA 321|Data Mining","ISTA 355|Intro to Natural Lang Processing","INFO 402|Data Ethics","ISTA 410|Bayesian Modeling",
  "ISTA 421|Intro to Machine Learning","GAME 426|Game Artificial Intelligence","ISTA 455|Applied Natural Lang Processing",
  "ISTA 450|Artificial Intelligence","ISTA 457|Neural Networks","ISTA 439|Statistical Natural Lang Processing"])
U("BS-IS","Emphasis: Data Science (15 units)","restricted","Choose 5 from one emphasis",[
  "ISTA 311|Foundations in Information & Inference","ISTA 320|Data Visualization","ISTA 321|Data Mining","ISTA 322|Data Engineering",
  "ISTA 331|Principles & Practices of Data Science","ISTA 350|Programming for Informatics Apps","ISTA 355|Intro to Natural Lang Processing",
  "ISTA 450|Artificial Intelligence","ISTA 439|Statistical Natural Lang Processing","ISTA 421|Intro to Machine Learning",
  "ISTA 429|Applied Cyber-infrastructure Concepts","ISTA 431|Data Warehousing & Analytics in Cloud","ISTA 414|Computational Social Science",
  "ISTA 410|Bayesian Modeling","ISTA 453|Biodiversity Informatics","ISTA 455|Applied Natural Lang Processing",
  "ISTA 456|Text Retrieval & Web Search","ISTA 457|Neural Networks",
  "LIS 470|Database Development & Management|"+TYPO.format("LIST 470","LIS 470")])
U("BS-IS","Emphasis: Interactive & Immersive Technologies (15 units)","restricted","Choose 5 from one emphasis",[
  "GAME 425|Algorithms for Games","GAME 426|Game AI","GAME 451|Game Development","GAME 452|Adv Game Development",
  "GAME 462|3D Modeling for Games","ISTA 303|Intro to Creative Coding","ISTA 330|Advanced Web Design",
  "ISTA 416|Intro to Human Comp Interactions","ISTA 350|Programming for Informatics App","ISTA 424|Virtual Reality",
  "ISTA 427|Augmented Reality","ISTA 320|Data Visualization"])

# ---- BA Information Science & Arts
U("BA-ISA","Introductory core","required","All five required",[
  "ISTA 100|Great Ideas of the Information Age","ISTA 116|Stat Foundations for the Info Age","ISTA 130|Computational Thinking & Doing",
  "ISTA 131|Dealing with Data","ISTA 161|Ethics in a Digital World"])
U("BA-ISA","Senior capstone","required","Required",["ISTA 498|Senior Capstone"])
U("BA-ISA","Computational Arts & Media (4 courses)","restricted","Choose 4",[
  "ART 231|3D Animation","ART 237|3D Modeling","ESOC 200|Visual Content Creation","ESOC 300|Digital Storytelling & Culture",
  "ESOC 340|Info MM Design & Moving Image","ISTA 301|Computing & the Arts","ISTA 302|Technology of Sound",
  "ISTA 303|Intro to Creative Coding","ISTA 329|Intro Web-Design Development","ISTA 330|Advanced Web Development",
  "ISTA 352|Images: Past, Present & Future","ISTA 401|Designing Installations","ISTA 416|Intro to Human Comp Interactions",
  "ISTA 424|Virtual Reality","GAME 425|Algorithms for Games","GAME 426|Game AI","GAME 451|Game Development",
  "GAME 452|Adv Game Development","GAME 462|3D Modeling for Games","LIS 442|Curating & Preserving Media Art Collections"])
U("BA-ISA","Society (1 course)","distribution","Choose 1",[
  "ESOC 313|Digital Discourse & Identity","ESOC 314|Theories of New Media","ESOC 315|Publishing: From Papyrus to E-Book Readers",
  "ESOC 316|Digital Commerce","ESOC 317|Digital Crime & Social Media","ESOC 318|Disruptive Technologies",
  "ESOC 319|Instructional Technologies","ESOC 325|Contemporary Literature & Digital Media",
  "ESOC 330|Digital Dilemmas - Privacy, Property & Access","ESOC 477|Information Security","ESOC 478|Science Information & its Presentation",
  "ESOC 495|Special Topics","INFO 402|Data Ethics"])
U("BA-ISA","Intensive computing (1 course)","distribution","Choose 1",[
  "ISTA 320|Data Visualization","ISTA 321|Data Mining","ISTA 322|Data Engineering","ISTA 350|Programming for Informatics Apps",
  "ISTA 414|Computational Social Science","ISTA 431|Data Warehousing & Analytics in Cloud","ISTA 495|Special Topics|Ask advisor.",
  "LIS 470|Database Development & Management"])
U("BA-ISA","Research methods (1 course)","distribution","Choose 1",[
  "ESOC 301|Qualitative Internet Research","ESOC 302|Quantitative Methods for the Digital Marketplace"])
U("BA-ISA","Engagement / internship / independent study (1 course)","culminating","Choose 1",ENGAGE)

# ---- BS Game Development
U("BS-GD","Intro core (9 units)","required","All three required",[
  "ISTA 161|Ethics in a Digital World","GAME 251|Introduction to Game Design","ESOC 320|AI Literacies for the Information Age"])
U("BS-GD","Foundational technical core (6 units)","required","Both required",[
  "ISTA 130|Computational Thinking & Doing","ISTA 116|Stat. Foundations for Info Age"])
U("BS-GD","Technical core (9 units)","required","All three required",[
  "GAME 351|Intro to Game Development with Unity","GAME 425|Algorithms for Games","GAME 451|Game Development"])
U("BS-GD","Research methods (3 units)","distribution","Choose 1",[
  "ESOC 301|Qualitative Internet Research","ESOC 302|Quantitative Methods for the Digital Marketplace","ISTA 131|Dealing with Data"])
U("BS-GD","Senior capstone (3 units)","required","Required",["ISTA 498|Senior Capstone"])
U("BS-GD","Major electives (9 units)","restricted","Choose 3",[
  "ART 231|3D Animation","ART 237|3D Modeling","ESOC 200|Visual Content Creation for the Information Age",
  "ESOC 300|Digital Storytelling and Culture","ESOC 316|Digital Commerce","ESOC 318|Disruptive Technologies",
  "ESOC 340|Information, Multimedia Design & the Moving Image","ESOC 345|Decoding Deceptive Info",
  "GAME 303|Digital Games and Society","GAME 304|Video Game & VR Ethics","GAME 305|Legal Aspects of the Game Industry",
  "GAME 307|Narrative Practice in Digital Games","GAME 308|Diversity and Bias in Games","GAME 309|Simulation Design",
  "GAME 310|Gamification in Society","GAME 311|eSports Industries","GAME 312|Monetizing Independent Gaming",
  "GAME 340|Design for Video Game Genres","GAME 426|Game AI","GAME 427|Augmented Reality","GAME 452|Advanced Game Development",
  "GAME 460|STEM Games","GAME 461|Game Physics","GAME 462|3D Modeling for Games","ISTA 301|Computing and the Arts",
  "ISTA 302|Technology of Sound","ISTA 303|Introduction to Creative Coding","ISTA 350|Programming for Informatics Applications",
  "ISTA 416|Introduction to Human Computer Interactions","ISTA 421|Introduction to Machine Learning|Discuss with advisor.",
  "ISTA 424|Virtual Reality","ISTA 450|Artificial Intelligence","ISTA 457|Neural Networks","LIS 484|Introduction to Copyright"])

# ---- BA Game Design
U("BA-GD","Intro core (9 units)","restricted","Choose 3 of 4",[
  "ESOC 320|AI Literacies for the Information Age","GAME 251|Introduction to Game Design",
  "ISTA 130|Computational Thinking & Doing","ISTA 161|Ethics in a Digital World"])
U("BA-GD","Core courses (12 units)","required","All four required",[
  "GAME 307|Narrative Practices in Digital Games","GAME 310|Gamification in Society","GAME 340|Design for Video Game Genres",
  "GAME 351|Intro to Game Dev with Unity"])
U("BA-GD","Advanced core (6 units)","required","Both required",[
  "ISTA 416|Intro to Human Computer Interaction","ISTA 498|Senior Capstone"])
U("BA-GD","Major electives (12 units)","restricted","Choose 4",[
  "ESOC 200|Visual Content Creation for the Information Age","ESOC 210|Digital Pioneers: Innovation & the Open Info Movement",
  "ESOC 211|Collaborating in Online Communities","ESOC 300|Digital Storytelling and Culture","ESOC 318|Disruptive Technologies",
  "ESOC 340|Information, Multimedia Design & the Moving Image","ESOC 480|Digital Engagement",
  "GAME 303|Digital Games and Society","GAME 305|Legal Aspects of the Game Industry","GAME 308|Diversity and Bias in Games",
  "GAME 309|Simulation Design","GAME 311|eSports Industries","GAME 312|Monetizing Independent Gaming",
  "GAME 425|Algorithms for Games","GAME 451|Game Development","GAME 452|Advanced Game Development",
  "ISTA 263|Learning in the Information Age","ISTA 301|Computing and the Arts","ISTA 302|Technology of Sound",
  "ISTA 303|Introduction to Creative Coding","ISTA 424|Virtual Reality","LIS 471|Introduction to Information Technology",
  "LIS 484|Introduction to Copyright","PAH 150A1|Video Game Sights, Sounds, and Stories","PAH 160D1|Play: An Interactive Introduction",
  "PAH 230|Video Games as Artifacts: Apprec. Interactive Multimedia","PAH 231|Global Game Cultures and Histories",
  "PAH 330|Video Game Industry: Business of Making Money W/ Play","PAH 331|Video Game Studies: Critical/Cultural Approaches",
  "PAH 332|Tabletop Games: Play, Culture, & Design of Board & RPGs"])

# ---- BA Emerging Technologies in Society
U("BA-ETS","Core (3 units)","required","Required",["ISTA 100|Great Ideas of the Information Age"])
U("BA-ETS","Engaged learning (3 units)","required","Required",["ESOC 480|Digital Engagement"])
U("BA-ETS","Intro core (9 units)","restricted","Choose 3",[
  "COMM 209|Intro to Communication Technology","ESOC 200|Visual Content Creation for the Info Age",
  "ESOC 210|Hacking & Open Source Culture","ESOC 211|Collaborating in Online Communities",
  "ESOC 212|Social Media Strat Across Professions","ESOC 213|The Past and New Media","ESOC 214|Intro to Data Science",
  "GAME 251|Intro to Game Design","ISTA 130|Computational Thinking & Doing","ISTA 263|Learning in the Information Age"])
ETS_ADV = ["ESOC 313|Digital Discourse & Identity","ESOC 314|Theories of New Media","ESOC 315|Publishing: From Papyrus to E-Book Readers",
  "ESOC 316|Digital Commerce","ESOC 317|Digital Crime & Social Media","ESOC 318|Disruptive Technologies","ESOC 319|Instructional Technologies",
  "ESOC 330|Digital Dilemmas - Privacy, Property & Access","ESOC 340|Info, Multimedia Design & the Moving Image",
  "ESOC 345|Decoding Deceptive Info","ESOC 418|Info Trust, Manipulation, & Deception","ESOC 477|Information Security",
  "ISTA 329|Introduction to Web Design & Development",
  "ESOC 300|Digital Storytelling and Culture|"+TYPO.format("ECOS 300","ESOC 300")]
U("BA-ETS","Advanced core (18 units)","restricted","Choose 6",ETS_ADV)
U("BA-ETS","Research methods (3 units)","distribution","Choose 1",
  [(x + " " if x.count("|") == 2 else x + "|") + "The checklist's Research Methods list is identical to its Advanced Core list; likely a copying error."
   for x in ETS_ADV])
U("BA-ETS","Additional electives (6 units)","restricted","Choose 2",[
  "ESOC 150B1|Social Media & Ourselves","ESOC 325|Contemporary Literature & Digital Media","ESOC 478|Science Information & Its Presentation",
  "ESOC 495|Special Topics","INFO 420|Ethical Issues in Information","INFO 493|Internship","LIS 417|Intro to Digital Cultures",
  "LIS 432|Online Searching","LIS 435|Business Information","LIS 442|Curating & Preserving Media Art Collections",
  "LIS 470|Database Management & Development","LIS 471|Intro to Information Technology","LIS 472|Government Information",
  "LIS 475|User Interface and Website Design","SOC 430|Social Networks"])

# ---- Minors
U("MIN-AIS","Core (take all)","required","All four required",[
  "ESOC 120|Creative Information with AI","ESOC 318|Disruptive Technologies","ESOC 320|AI Literacies for the Information Age",
  "PHIL 206|Ethics of Artificial Intelligence"])
U("MIN-AIS","AI in Context elective","distribution","Take 1",[
  "ESOC 200|Visual Content Creation for the Information Age","ESOC 428|Applied AI Literacies in Information Practice",
  "GWS 260|Sex, Gender & Technology"])
U("MIN-AIS","Applied Knowledge elective","distribution","Take 1",[
  "ESOC 429|AI and the Art & Design of Learning","PHIL 455|Philosophy and Artificial Intelligence"])

U("MIN-CYBR","Minor requirements (18 units)","required","All six required",[
  "CYBR 101|Principles of Cyber Ops I","CYBR 310|Intro to Security Programming I","CYBR 311|Intro to Security Programming II",
  "CYBR 454|Malware Threats & Analysis","CYBR 470|C Programming for Security Professionals",
  "CYBR 471|Assembly Programming for Security Professionals"])

ETSM_NOTE = "Also eligible for the any-level elective group."
U("MIN-ETS","Electives, any level (take 2)","restricted","Take 2 (any level)",[
  "COMM 209|Introduction to Communication|Only available to COMM majors and minors.","ESOC 150B1|Social Media & Ourselves",
  "ESOC 200|Visual Content Creation for the Information Age","ESOC 210|Hacking & Open-Source Culture",
  "ESOC 211|Collaborating in Online Communities","ESOC 212|Social Media Strategies Across Professions","ESOC 213|The Past & New Media",
  "ESOC 214|Introduction to Data Science","GAME 251|Introduction to Game Design","ISTA 263|Learning in the Information Age"])
U("MIN-ETS","Upper-division electives (take 4)","restricted","Take 4 (300-level or above)",[
  "COMM 311|Communication Technology Theory|Only available to COMM majors and minors. "+ETSM_NOTE,
  "ESOC 300|Digital Storytelling & Culture","ESOC 313|Digital Discourse & Identity","ESOC 314|Theories of New Media",
  "ESOC 315|Publishing: From Papyrus to E-Book Readers","ESOC 316|Digital Commerce","ESOC 317|Digital Crime & Social Media",
  "ESOC 318|Disruptive Technologies","ESOC 319|Instructional Technologies","ESOC 325|Contemporary Literature & Digital Media",
  "ESOC 340|Information, Multimedia Design & the Moving Image","ESOC 345|Decoding Disinformation",
  "ESOC 418|Information Trust, Manipulation & Deception","ESOC 477|Information Security","ESOC 478|Science Information & its Presentation",
  "ESOC 495|Special Topics","LIS 417|Introduction to Digital Cultures","LIS 432|Online Searching",
  "LIS 385|Business Information|Listed as LIS 385; the ETS BA and LIS minor list Business Information as LIS 435. "+ETSM_NOTE,
  "LIS 470|Database Management & Development","LIS 471|Introduction to Information Technology","LIS 472|Government Information",
  "LIS 475|User Interface & Website Design","LIS 478|Science Information & its Presentation","LIS 484|Introduction to Copyright"],
  ETSM_NOTE)

ESP_GAME = ["GAME 303|Digital Games & Society","GAME 305|Legal Aspects of the Game Industry","GAME 307|Narrative Practices in Digital Games",
  "GAME 308|Diversity and Bias in Games","GAME 309|Simulation Design & Development for Complex Problem Solving",
  "GAME 310|Gamification in Society","GAME 312|Monetizing Independent Gaming"]
U("MIN-ESPT","Core","required","Both required",["GAME 251|Introduction to Game Design","GAME 311|eSports Industry"])
U("MIN-ESPT","GAME electives (take 2)","restricted","Take 2",ESP_GAME,"Untaken GAME options may also fill the general elective group.")
U("MIN-ESPT","Electives (take 2)","restricted","Take 2 (or GAME options not already taken)",[
  "ESOC 211|Collaborating in Online Communities","ISTA 416|Introduction to Human-Computer Interactions",
  "PAH 150A1|Video Game Sights, Sounds & Stories","PAH 160D1|Play: An Interactive Introduction","PAH 230|Video Games as Artifacts",
  "PAH 231|Global Game Cultures & Histories","PAH 330|The Video Game Industry","PAH 331|Video Game Studies: Critical/Cultural Approaches",
  "PAH 332|Tabletop Games: Play, Culture & Design of Board & Role-Playing Games",
  "TLS 353|Recreation & Leisure in Contemporary Society","TLS 355|Planning Community Events & Recreation Programs"])

U("MIN-GDES","GAME courses (take at least 3)","restricted","Take at least 3; additional GAME courses may count as electives",[
  "GAME 251|Introduction to Game Design","GAME 303|Digital Games & Society","GAME 305|Legal Aspects of the Game Industry",
  "GAME 307|Narrative Practices in Digital Games","GAME 308|Diversity and Bias in Games",
  "GAME 309|Simulation Design & Development for Complex Problem Solving","GAME 310|Gamification in Society","GAME 311|eSports Industry",
  "GAME 312|Monetizing Independent Gaming",
  "GAME 351|Introduction to Game Development in Unity|Cannot be taken concurrently with or after GAME 451.",
  "GAME 451|Game Development","GAME 452|Advanced Game Development"])
U("MIN-GDES","Electives (take 3)","restricted","Take 3 (additional GAME courses also count)",[
  "ESOC 200|Visual Content Creation for the Information Age","ESOC 210|Hacking & Open-Source Culture",
  "ESOC 211|Collaborating in Online Communities","ESOC 300|Digital Storytelling & Culture","ESOC 316|Digital Commerce",
  "ESOC 318|Disruptive Technologies","ESOC 340|Information, Multimedia Design & the Moving Image","ESOC 345|Decoding Disinformation",
  "ISTA 161|Ethics in a Digital Age","ISTA 263|Learning in the Information Age","ISTA 301|Computing & the Arts",
  "ISTA 302|Technology of Sound","ISTA 303|Creative Coding","ISTA 416|Introduction to Human-Computer Interactions",
  "ISTA 424|Virtual Reality",
  "ISTA 425|Algorithms for Games|Listed as ISTA 425; every other checklist lists Algorithms for Games as GAME 425.",
  "LIS 471|Introduction to Information Technology","LIS 484|Introduction to Copyright",
  "PAH 150A1|Video Game Sights, Sounds, & Stories","PAH 160D1|Play: An Interactive Introduction",
  "PAH 230|Video Games as Artifacts: Appreciating Interactive Multimedia Entertainment","PAH 231|Global Game Cultures and Histories",
  "PAH 330|The Video Game Industry: An Introduction to the Business of Making Money with Play",
  "PAH 331|Video Game Studies: Critical/Cultural Approaches",
  "PAH 332|Tabletop Games: Play, Culture, and Design of Board & Role-Playing Games"])

U("MIN-GDEV","Introductory programming (take 1)","distribution","Take 1",[
  "ISTA 130|Computational Thinking and Doing","CSC 110|Introduction to Computer Programming I",
  "ECE 175|Computer Programming for Engineering Applications"])
U("MIN-GDEV","Introductory GAME courses (take 2)","required","Both required",[
  "GAME 251|Introduction to Game Design",
  "GAME 351|Introduction to Game Development with Unity|GAME 451 replaces GAME 351 for students who have completed CSC 210 or ISTA 350."])
U("MIN-GDEV","Electives (take 3)","restricted","Take 3",[
  "ESOC 300|Digital Storytelling and Culture","GAME 303|Digital Games and Society","GAME 305|Legal Aspects of the Game Industry",
  "GAME 307|Narrative Practices in Digital Games","GAME 308|Diversity and Bias in Games","GAME 309|Simulation Design",
  "GAME 310|Gamification in Society","GAME 311|eSports Industries","GAME 312|Monetizing Independent Gaming",
  "GAME 340|Design for Video Game Genres","GAME 425|Algorithms for Games","GAME 426|Game Artificial Intelligence",
  "GAME 427|Augmented Reality","GAME 452|Advanced Game Development","GAME 460|STEM Games","GAME 461|Game Physics",
  "GAME 462|3D Modeling for Games","ISTA 350|Programming for Informatics Applications","ISTA 416|Human-Computer Interaction",
  "ISTA 424|Virtual Reality","ISTA 450|Artificial Intelligence"])
r("MIN-GDEV","GAME 451","Introductory GAME courses (take 2)","either_or","Both required",
  "Replaces GAME 351 for students who have completed CSC 210 or ISTA 350.",CK,"Game Development")

U("MIN-ISTA","Core (take 4)","required","All four required",[
  "ISTA 100|Great Ideas of the Information Age","ISTA 116|Statistical Foundations for the Info. Age",
  "ISTA 130|Computational Thinking & Doing|CSC 110 can fulfill this requirement.","ISTA 161|Ethics in a Digital World"])
U("MIN-ISTA","Upper-division electives (take 2)","restricted","Take any 2",[
  "ISTA 301|Computing & the Arts","ISTA 302|Technology of Sound","ISTA 303|Creative Coding","ISTA 401|Designing Installations",
  "ISTA 403|Advanced Creative Coding","ISTA 329|Introduction to Web Design & Development","ISTA 330|Advanced Web Design",
  "ISTA 352|Images: Past, Present, and Future","ISTA 416|Introduction to Human-Computer Interactions","ISTA 320|Data Visualization",
  "ISTA 321|Data Mining","ISTA 322|Data Engineering","ISTA 331|Principles & Practices of Data Science",
  "ISTA 429|Applied Cyberinfrastructure Concepts","ISTA 431|Data Warehousing & Analytics in the Cloud",
  "ISTA 350|Programming for Informatics Applications","ISTA 311|Foundations of Information & Inference",
  "ISTA 335|Introduction to Natural Language Processing|Listed as ISTA 335; the BS in Information Science checklist lists this title as ISTA 355.",
  "ISTA 410|Bayesian Modeling","ISTA 421|Introduction to Machine Learning","ISTA 450|Artificial Intelligence",
  "ISTA 455|Applied Natural Language Processing","GAME 451|Game Development","ISTA 424|Virtual Reality",
  "ISTA 425|Algorithms for Games|Listed as ISTA 425; degree checklists list Algorithms for Games as GAME 425.",
  "ISTA 495|Special Topics"])

U("MIN-LIS","Core (take 4)","required","All four required",[
  "ESOC 210|Hacking & Open-Source Culture","ESOC 213|The Past & New Media","ESOC 315|Publishing: From Papyrus to E-Book Readers",
  "LIS 432|Online Searching"])
U("MIN-LIS","Electives (take 2)","restricted","Take 2",[
  "ANTH 372|Critical Issues for Museums in the 21st Century","ESOC 319|Instructional Technologies","ESOC 345|Decoding Disinformation",
  "INFO 420|Ethical Issues in Information","LIS 417|Introduction to Digital Cultures","LIS 418|Information Trust, Manipulation, & Deception",
  "LIS 435|Business Information","LIS 442|Curating & Preserving Media Art Collections","LIS 470|Database Management & Development",
  "LIS 471|Introduction to Information Technology","LIS 472|Government Information","LIS 475|User Interface & Website Design",
  "LIS 484|Introduction to Copyright","LIS 487|Information-Seeking Behaviors"])

# ---- Undergraduate certificates (AY 2025-26 checklists)
U("UCERT-CYBR","Core (take all)","required","All five required",[
  "CYBV 470|C Programming for Security Professionals","CYBV 471|Assembly Language Programming for Security Pro.",
  "CYBV 479|Wireless Networking & Security","CYBV 489|Operating Systems Theory for Security Pro.","NETV 379|Cloud Computing"])
U("UCERT-CYBR","Option course (take 1)","either_or","Take 1",[
  "CYBV 388|Cyber Investigation & Forensics","CYBV 472|Secure Software Design & Analysis"])

U("UCERT-CYSEC","Core (take all)","required","All three required",[
  "CYBV 326|Introduction to Network Analysis","CYBV 385|Introduction to Cyber Operations","CYBV 400|Active Cyber Defense"])
NT = "Recommended for students without a technical background or enrolled as certificate-seeking."
EM = "Recommended for B.A.S. Cyber Operations Defense & Forensics or Cyber Law & Policy emphasis students."
U("UCERT-CYSEC","Electives (take 3)","restricted","Take 3",[
  "APCV 320|Computational Thinking & Doing","APCV 470|C Programming for Security Professionals","CYBV 301|Fundamentals of Cybersecurity",
  f"CYBV 302|Linux Security Essentials|{NT} {EM}",f"CYBV 303|Windows Security Essentials|{NT} {EM}",
  "CYBV 310|Introduction to Security Programming I","CYBV 311|Introduction to Security Programming II",
  f"CYBV 312|Introduction to Security Scripting|{NT}","CYBV 329|Cyber Ethics","CYBV 330|Introduction to Industrial Control System Security",
  "CYBV 351|Signals Intelligence & Electronic Warfare","CYBV 354|Principles of Open Source Intelligence",
  "CYBV 381|From Incident Responses to Digital Forensics","CYBV 382|Network Forensics","CYBV 383|Mobile Device Forensics",
  "CYBV 384|Host & File System Forensics (Windows)","CYBV 386|Enterprise & File System Forensics (Linux)",
  "CYBV 388|Forensics & Investigation","CYBV 435|Cyber Threat Intelligence",f"CYBV 436|Counter Cyber Threat Intelligence|{EM}",
  "CYBV 437|Deception, Counter-Deception & Counter Intelligence",f"CYBV 440|Digital Espionage|{EM}",
  f"CYBV 441|Cyber War, Terror and Crime|{EM}","CYBV 442|Regulatory Limitations and Controls for Cyber Operations",
  "CYBV 443|Legal and Privacy Constraints in Cyber Operations","CYBV 450|Information Warfare","CYBV 454|Malware Threats and Analysis",
  "CYBV 460|Principles of Zero Trust Networks","CYBV 471|Assembly Language Programming for Security Professions",
  "CYBV 472|Secure Software Development and Assessment",f"CYBV 473|Violent Python|{EM}",
  "CYBV 474|Advanced Analytics for Security Operations","CYBV 475|Cyber Deception Detection",
  f"CYBV 477|Advanced Computer Forensics|{EM}",f"CYBV 479|Wireless Networking and Security|{EM}",
  "CYBV 480|Cyber Warfare",f"CYBV 481|Social Engineering Attacks & Defenses|{EM}","CYBV 482|Computational Propaganda",
  "CYBV 489|Operating Systems Theory for Security Professionals",f"CYBV 496|Special Topics in Cybersecurity|Department consent. {EM}",
  "NETV 301|Virtualization: Applications and Best Practices",f"NETV 379|Cloud Computing|{EM}"])

U("UCERT-DSV","Introductory statistics (take 1)","either_or","Take 1",[
  "ESOC 214|Introduction to Data Science","ISTA 116|Statistical Foundations for the Info. Age"])
U("UCERT-DSV","Core (take 2)","required","Both required",[
  "ISTA 320|Applied Data & Visualization","ISTA 321|Data Mining & Discovery"])
U("UCERT-DSV","Elective (take 1)","restricted","Take 1",[
  "BIOS 376|Introduction to Biostatistics","ESOC 302|Quantitative Methods for the Digital Marketplace",
  "ESOC 414|Computational Social Science","ISTA 130|Computational Thinking & Doing","ISTA 322|Data Engineering",
  "ISTA 331|Principles & Practices of Data Science","ISTA 421|Introduction to Machine Learning",
  "ISTA 429|Applied Cyberinfrastructure Concepts","LIS 470|Database Management & Development","WFSC 223|Dealing with Data in the Wild"])

# ---------------------------------------------------------------- general rules
# matcher: prefixes, numeric ranges [lo,hi] inclusive, exclusions (exact course codes)
RULES = [
 dict(program="MSDS", group="Electives (15 units)", role="rule", prefixes=["INFO"], ranges=[[500,590],[600,690]],
      exclude=["INFO 502","INFO 511","INFO 523","INFO 526"],
      text="Any INFO 500–590 or 600–690 course except the core. Approved courses from other departments also count (advisor contact required if not pre-approved)."),
 dict(program="MSIS", group="General electives (9 units)", role="rule", prefixes=["INFO"], ranges=[[500,590],[600,690]],
      exclude=["INFO 505","INFO 526","INFO 516","INFO 521"],
      text="Any INFO 500–590 or 600–690 course except core courses. Approved courses in other departments also count (consult advisor). Subplan core courses cannot double as electives."),
 dict(program="MLIS", group="LIS electives (6 units)", role="rule", prefixes=["LIS"], ranges=[[500,699]],
      exclude=["LIS 504","LIS 506","LIS 515","LIS 698"],
      text="Any graduate-level LIS course, including specialty courses. (6 further units of Free Electives may be any related coursework.)"),
 dict(program="PHD", group="Electives (12 units)", role="rule", prefixes=["CYBR","GAME","INFO","LIS"], ranges=[[500,699]],
      exclude=["INFO 507","INFO 692","LIS 692","INFO 696E"],
      text="Four graduate courses within the College (CYBR, GAME, INFO, LIS). Courses outside the College need major advisor and DGS approval."),
 dict(program="PHDMIN", group="Minor coursework (9 units)", role="approval", prefixes=["CYBR","GAME","INFO","LIS"], ranges=[[500,699]],
      exclude=[],
      text="9 units of approved College of Information Science courses, grade B or better. The approved list is not published; confirm with the minor coordinator."),
 dict(program="C-LEGAL", group="Electives (6 units)", role="rule", prefixes=["LIS"], ranges=[[500,699]],
      exclude=["LIS 693"],
      text="Two electives; any LIS course counts. Meet with the certificate advisor."),
]

# ---------------------------------------------------------------- cross-listings
# Only cross-listings a source states explicitly. Shared numbers across prefixes (INFO 570 / LIS 570,
# ISTA 425 / GAME 425, CYBV 470 / CYBR 470, ...) are NOT treated as cross-listings.
CROSS = {"LIS 646": "NURS 646", "NURS 646": "LIS 646"}

data = dict(
    gathered="2026-11-20",
    sources=["https://infosci.arizona.edu/graduate-programs/graduate",
             "https://infosci.arizona.edu/undergraduate-programs/undergraduate",
             "Undergraduate checklist PDFs (Box), supplied by the user"],
    roles={k: dict(label=v[0], desc=v[1]) for k, v in ROLES.items()},
    programs=PROGRAMS, rows=rows, rules=RULES, catalog=dict(sorted(CATALOG.items())), cross=CROSS,
)
# Output files are written next to this script, wherever it is run from.
HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "course_program_data.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1)

# data.js: the same data as a JavaScript global, loaded by index.html with a <script> tag.
# (Browsers block fetch() on file:// pages, so this lets the tool run straight from disk.)
with open(os.path.join(HERE, "data.js"), "w", encoding="utf-8") as f:
    f.write("// Generated by build_data.py. Do not edit by hand.\n")
    f.write("const DATA = ")
    json.dump(data, f, ensure_ascii=False)
    f.write(";\n")

prog = {p["id"]: p for p in PROGRAMS}
def key(x):
    pre, num = x["course"].split()
    return (pre, int(re.match(r"\d+", num).group()), num, prog[x["program"]]["level"], x["program"])
with open(os.path.join(HERE, "course_program_map.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Course","Title (as listed)","Program","Level","Program type","Requirement group","How it counts","Group rule","Note","Source","Source URL"])
    for x in sorted(rows, key=key):
        p = prog[x["program"]]
        src_url = p["url"] if x["source"] == "Program webpage" else (p["pdf"] or p["url"])
        w.writerow([x["course"],x["title"],p["name"],p["level"],p["kind"],x["group"],ROLES[x["role"]][0],x["group_rule"],x["note"],x["source"],src_url])
print(len(rows), "rows;", len({x['course'] for x in rows}), "distinct courses;", len(PROGRAMS), "programs;", len(RULES), "rules")
