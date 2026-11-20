/* ============================================================
   Course to Program Search: app logic
   Reads the global DATA (from data.js) and renders search results.

   Lookup logic follows README.md:
     1. Normalize the input to "PREFIX NUMBER".
     2. Collect every named row for the course (plus any stated cross-listing).
     3. Apply general elective rules (prefix, number range, not excluded), alongside any named rows.
     4. Never merge courses that only share a number across prefixes.
   ============================================================ */

const verbose = false;   // set true to log lookups to the console

// ---------------------------------------------------------------- reference tables

// Roles from strongest to weakest (README order). Used for sorting and badge color.
const ROLE_ORDER = [
  "required", "required_opt", "either_or",           // strong
  "culminating", "distribution", "restricted",        // mid
  "recommended", "rule", "approval",                  // weak
];

function roleRank(role) {
  const i = ROLE_ORDER.indexOf(role);
  return i === -1 ? ROLE_ORDER.length : i;   // unknown roles sort last
}

function roleStrength(role) {
  const i = roleRank(role);
  return i < 3 ? "strong" : i < 6 ? "mid" : "weak";
}

function roleLabel(role) {
  return DATA.roles[role] ? DATA.roles[role].label : role;
}

const LEVEL_ORDER = ["Graduate", "Undergraduate"];
const KIND_ORDER = ["Degree", "Minor", "Certificate"];

// Program id -> program object, for quick lookup.
const PROGRAMS = {};
for (const p of DATA.programs) PROGRAMS[p.id] = p;

// ---------------------------------------------------------------- input cleanup

/**
 * Turn free-form input into a course code like "INFO 550", or null if it can't be read.
 * Accepts "info550", " Info-550 ", "INFO  550", "ista 150b1" -> "ISTA 150B1".
 * The number must start with three digits; letter/digit suffixes are kept (e.g., 696E).
 */
function normalizeCourse(raw) {
  const squashed = raw.toUpperCase().replace(/[^A-Z0-9]/g, "");   // drop spaces, dashes, etc.
  const m = squashed.match(/^([A-Z]{2,5})(\d{3}[A-Z0-9]*)$/);
  return m ? `${m[1]} ${m[2]}` : null;
}

// ---------------------------------------------------------------- lookup

/** Leading digits of the course number as an integer: "ISTA 150B1" -> 150. */
function courseNumber(code) {
  return parseInt(code.split(" ")[1], 10);
}

/**
 * Find every program that uses the course.
 * Returns an array of { program, uses: [...] }, one entry per program, where each use is
 *   { kind: "row",  row,  via }   a named row (via = cross-listed code it was found under, or null)
 *   { kind: "rule", rule }        a general elective rule the course falls under
 */
function lookup(code) {
  const byProgram = new Map();   // Map keeps insertion order, unlike some object-key cases
  function addUse(programId, use) {
    if (!byProgram.has(programId)) byProgram.set(programId, []);
    byProgram.get(programId).push(use);
  }

  // Step 2a: named rows for the code itself.
  for (const row of DATA.rows) {
    if (row.course === code) addUse(row.program, { kind: "row", row, via: null });
  }
  // Step 2b: rows under an explicitly stated cross-listing, only for programs that don't
  // already name the code itself (some programs list both, e.g., MLIS lists LIS 646 and NURS 646).
  const cross = DATA.cross[code];
  if (cross) {
    const named = new Set(byProgram.keys());
    for (const row of DATA.rows) {
      if (row.course === cross && !named.has(row.program)) addUse(row.program, { kind: "row", row, via: cross });
    }
  }

  // Step 3: general rules. These apply even when the program also names the course
  // (e.g., INFO 550 is "recommended" in MSDS but also counts under its INFO 500–590 elective rule).
  // Each rule's exclude list keeps core courses from also showing as general electives.
  const [prefix] = code.split(" ");
  const num = courseNumber(code);
  for (const rule of DATA.rules) {
    if (!rule.prefixes.includes(prefix)) continue;
    if (rule.exclude.includes(code)) continue;
    if (!rule.ranges.some(([lo, hi]) => num >= lo && num <= hi)) continue;
    // Skip if the course is already named in this same group (e.g., MSDS lists INFO 531 under
    // "Electives (15 units)", which is also the group the rule describes).
    const sameGroup = (byProgram.get(rule.program) || [])
      .some(u => u.kind === "row" && u.row.group === rule.group);
    if (sameGroup) continue;
    addUse(rule.program, { kind: "rule", rule });
  }

  const results = [...byProgram].map(([id, uses]) => ({ program: PROGRAMS[id], uses }));

  // Within a program, show the strongest use first.
  for (const r of results) r.uses.sort((a, b) => roleRank(useRole(a)) - roleRank(useRole(b)));

  // Across programs: strongest use, then Graduate before Undergraduate, then Degree/Minor/Certificate, then name.
  results.sort((a, b) =>
    roleRank(useRole(a.uses[0])) - roleRank(useRole(b.uses[0])) ||
    LEVEL_ORDER.indexOf(a.program.level) - LEVEL_ORDER.indexOf(b.program.level) ||
    KIND_ORDER.indexOf(a.program.kind) - KIND_ORDER.indexOf(b.program.kind) ||
    a.program.name.localeCompare(b.program.name)
  );

  if (verbose) console.log("lookup", code, "cross-listing:", cross, "results:", results);
  return results;
}

function useRole(use) {
  return use.kind === "row" ? use.row.role : use.rule.role;
}

// ---------------------------------------------------------------- rendering helpers

/** Escape text before inserting it into HTML. */
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, ch =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}

function badge(role) {
  return `<span class="badge ${roleStrength(role)}">${esc(roleLabel(role))}</span>`;
}

/** Course title: catalog first, then the title any program lists for it. */
function courseTitle(code) {
  if (DATA.catalog[code]) return DATA.catalog[code];
  const row = DATA.rows.find(r => r.course === code);
  return row ? row.title : "";
}

// ---------------------------------------------------------------- result cards

/** One collapsible card per program. The summary shows how the course counts. */
function renderCard(result, matchCodes) {
  const p = result.program;

  const useItems = result.uses.map(use => {
    if (use.kind === "row") {
      const via = use.via ? ` <span class="via">(listed as ${esc(use.via)})</span>` : "";
      return `<li>${badge(use.row.role)}<span class="group">${esc(use.row.group)}</span>${via}</li>`;
    }
    return `<li>${badge(use.rule.role)}<span class="group">${esc(use.rule.group)}</span></li>`;
  }).join("");

  return `
    <details class="result">
      <summary>
        <div class="result-head">
          <span class="program-name">${esc(p.name)}</span>
          <span class="tags">${esc(p.level)} · ${esc(p.kind)}</span>
        </div>
        <ul class="uses">${useItems}</ul>
      </summary>
      <div class="details-body">${renderRequirements(p, matchCodes, result.uses)}</div>
    </details>`;
}

/**
 * The full requirements of a program, rebuilt from its rows and rules.
 * Groups appear in source order. The searched course (and a matched rule) is highlighted.
 */
function renderRequirements(p, matchCodes, uses) {
  // Gather rows by group, preserving the order groups first appear in the data.
  const groups = new Map();
  for (const row of DATA.rows) {
    if (row.program !== p.id) continue;
    if (!groups.has(row.group)) groups.set(row.group, { rows: [], rules: [] });
    groups.get(row.group).rows.push(row);
  }
  // Attach general rules to the group of the same name, or add them as their own group.
  for (const rule of DATA.rules) {
    if (rule.program !== p.id) continue;
    if (!groups.has(rule.group)) groups.set(rule.group, { rows: [], rules: [] });
    groups.get(rule.group).rules.push(rule);
  }
  const matchedRules = uses.filter(u => u.kind === "rule").map(u => u.rule);

  let html = "";
  for (const [name, g] of groups) {
    // A group's rule text can vary row to row (e.g., "Core in both subplans" / "Subplan core").
    const groupRules = [...new Set(g.rows.map(r => r.group_rule).filter(Boolean))];
    // Show each course's role only when the group mixes roles (e.g., required + either_or).
    const mixedRoles = new Set(g.rows.map(r => r.role)).size > 1;

    const items = g.rows.map(r => {
      const isMatch = matchCodes.includes(r.course);
      const role = mixedRoles ? ` <span class="row-role">(${esc(roleLabel(r.role))})</span>` : "";
      const note = r.note ? `<span class="row-note">${esc(r.note)}</span>` : "";
      return `<li${isMatch ? ' class="match"' : ""}><span class="code">${esc(r.course)}</span> ${esc(r.title)}${role}${note}</li>`;
    }).join("");

    const ruleTexts = g.rules.map(rule => {
      const isMatch = matchedRules.includes(rule);
      return `<p class="rule-text${isMatch ? " match" : ""}">${badge(rule.role)}${esc(rule.text)}</p>`;
    }).join("");

    html += `
      <section class="req-group">
        <h3>${esc(name)}</h3>
        ${groupRules.length ? `<div class="group-rule">${esc(groupRules.join(" · "))}</div>` : ""}
        ${items ? `<ul>${items}</ul>` : ""}
        ${ruleTexts}
      </section>`;
  }

  // Program-level information and source links.
  const links = [];
  if (p.url) links.push(`<a href="${esc(p.url)}" target="_blank" rel="noopener">Program webpage</a>`);
  if (p.pdf) {
    const label = p.level === "Undergraduate" ? "Checklist PDF" : "Overview PDF";
    links.push(`<a href="${esc(p.pdf)}" target="_blank" rel="noopener">${label}</a>`);
  }
  html += `
    <div class="program-meta">
      ${p.units ? `<p>Total units: ${esc(p.units)}</p>` : ""}
      ${p.notes ? `<p>${esc(p.notes)}</p>` : ""}
      ${links.length ? `<p>${links.join(" · ")}</p>` : ""}
    </div>`;
  return html;
}

// ---------------------------------------------------------------- search

const form = document.getElementById("search-form");
const input = document.getElementById("course-input");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

function runSearch(raw) {
  resultsEl.innerHTML = "";
  resultsEl.scrollTop = 0;

  if (!raw.trim()) { statusEl.innerHTML = ""; return; }

  const code = normalizeCourse(raw);
  if (!code) {
    statusEl.innerHTML = `<p class="message error">Enter a course prefix and number, such as INFO 550.</p>`;
    return;
  }
  input.value = code;   // show the cleaned-up form

  const results = lookup(code);
  const title = courseTitle(code);
  const n = results.length;
  const cross = DATA.cross[code];

  let countLine;
  if (n === 0) countLine = "Not used by any program in this dataset. Check the prefix and number.";
  else countLine = `Used in ${n} program${n === 1 ? "" : "s"}. Click a program to see its full requirements.`;
  if (cross) countLine += ` Cross-listed as ${cross}.`;

  statusEl.innerHTML = `
    <div><span class="course-code">${esc(code)}</span>${title ? ` <span class="course-title">${esc(title)}</span>` : ""}</div>
    <div class="count">${esc(countLine)}</div>`;

  // Codes to highlight inside expanded cards: the course and its stated cross-listing.
  const matchCodes = cross ? [code, cross] : [code];
  resultsEl.innerHTML = results.map(r => renderCard(r, matchCodes)).join("");
}

form.addEventListener("submit", event => {
  event.preventDefault();   // stop the browser from reloading the page
  runSearch(input.value);
});

// Footer: data date and the authoritative source.
document.getElementById("footer").textContent =
  `Data gathered ${DATA.gathered} from College of Information Science program pages and checklists. ` +
  `The UA Academic Catalog is authoritative.`;

input.focus();
