$(document).ready(function () {
  // Ensure date-select styling class exists even if template was older
  (function ensureDateSelectClasses() {
    var sel = document.getElementById("reportDateSelect");
    if (sel && !sel.classList.contains("date-select")) {
      sel.classList.add("date-select");
    }
    var grp = sel ? sel.closest(".filter-group") : null;
    if (grp && !grp.classList.contains("date-filter")) {
      grp.classList.add("date-filter");
    }
  })();
  // Initialize DataTable with simple alphabetical sort on Trip Type (col 2)
  // Custom sort for Trip Type based on trip length heuristic
  function tripTypeRank(t) {
    t = String(t || "").toLowerCase();
    if (t.includes("1/2 day")) {
      if (t.includes("am")) return 0.5;
      if (t.includes("pm")) return 0.51;
      if (t.includes("twilight")) return 0.52;
      return 0.5;
    }
    if (t.includes("3/4 day")) return 0.75;
    if (t.includes("full day")) return 1.0;
    if (t.includes("overnight")) return 1.2;
    const extended = t.includes("extended") ? 0.05 : 0;
    const m = t.match(/(\d+(?:\.\d+)?)\s*day/);
    if (m) return parseFloat(m[1]) + extended;
    const m2 = t.match(/(\d+)\s*\/\s*(\d+)\s*day/);
    if (m2) {
      const num = parseFloat(m2[1]);
      const den = parseFloat(m2[2]);
      if (den) return num / den + extended;
    }
    return 99;
  }

  $.fn.dataTable.ext.type.order["trip-rank-pre"] = function (d) {
    return tripTypeRank(d);
  };

  var table = $("#reports").DataTable({
    paging: false,
    info: false,
    order: [[2, "asc"]],
    columnDefs: [{ targets: 2, type: "trip-rank" }],
  });

  // Build Trip Type filter checkboxes dynamically from table data
  function buildTripTypeFilters() {
    var tripTypes = new Set(
      table
        .column(2, { search: "applied" })
        .data()
        .toArray()
        .map(function (v) {
          return String(v).trim();
        })
    );
    var container = document.getElementById("tripTypeFilter");
    container.innerHTML = "";
    Array.from(tripTypes)
      .sort()
      .forEach(function (tt) {
        if (!tt) return;
        var id = "tt-" + tt.replace(/[^a-z0-9]+/gi, "-").toLowerCase();
        var label = document.createElement("label");
        label.innerHTML =
          '<input type="checkbox" id="' +
          id +
          '" value="' +
          tt.replace(/"/g, "&quot;") +
          '" checked> ' +
          tt;
        container.appendChild(label);
      });
  }

  // History: populate date selector and enable loading previous days
  // Use absolute URL to avoid base-path/CORS issues on mobile
  const historyUrl =
    "https://hdehaini.github.io/Fishing_Reports/database/reports_history.csv";
  const dateSelect = document.getElementById("reportDateSelect");

  function parseCsv(text) {
    // Simple CSV parser for lines without embedded commas in fields other than Fish Count which we don't split
    // We'll split by commas but keep the Fish Count field intact by only splitting the first 5 commas
    const lines = text.trim().split(/\r?\n/);
    if (lines.length <= 1) return { header: [], rows: [] };
    const header = lines[0].split(",");
    const rows = lines
      .slice(1)
      .map((line) => {
        // Split into max 6 parts: Date, Source, Boat Name, Trip Type, Anglers, Fish Count (rest)
        const parts = line.split(/,(.+)/); // first comma
        if (parts.length < 3) return null;
        const date = parts[0];
        const rest1 = parts[1];
        const p2 = rest1.split(/,(.+)/); // Source
        if (p2.length < 2) return null;
        const source = p2[0];
        const rest2 = p2[1];
        const p3 = rest2.split(/,(.+)/); // Boat Name
        if (p3.length < 2) return null;
        const boat = p3[0];
        const rest3 = p3[1];
        const p4 = rest3.split(/,(.+)/); // Trip Type
        if (p4.length < 2) return null;
        const trip = p4[0];
        const rest4 = p4[1];
        const p5 = rest4.split(/,(.+)/); // Anglers
        if (p5.length < 2) return null;
        const anglers = p5[0];
        const fish = p5[1]; // remainder is Fish Count
        return [date, source, boat, trip, anglers, fish];
      })
      .filter(Boolean);
    return { header, rows };
  }

  function stripOuterQuotes(s) {
    s = String(s == null ? "" : s).trim();
    if (s.length >= 2 && s.startsWith('"') && s.endsWith('"')) {
      return s.slice(1, -1);
    }
    return s;
  }

  function populateDateSelector(rows) {
    const dates = Array.from(new Set(rows.map((r) => r[0])))
      .sort()
      .reverse();
    dateSelect.innerHTML = "";
    dates.forEach((d) => {
      const opt = document.createElement("option");
      opt.value = d;
      opt.textContent = d;
      dateSelect.appendChild(opt);
    });
  }

  function loadDateIntoTable(rows, isoDate) {
    const dayRows = rows.filter((r) => r[0] === isoDate);
    // Replace table body
    table.clear();
    dayRows.forEach((r) => {
      const fish = stripOuterQuotes(r[5]);
      table.row.add([r[1], r[2], r[3], r[4], fish]);
    });
    // Ensure trip-type sort is applied after data replacement
    table.order([[2, "asc"]]).draw();
    // Rebuild filters from new data
    buildTripTypeFilters();
    buildFishFilters();
  }

  fetch(historyUrl, { cache: "no-store" })
    .then((res) => (res.ok ? res.text() : Promise.reject(res.status)))
    .then((text) => {
      const { rows } = parseCsv(text);
      if (!rows.length) return;
      populateDateSelector(rows);
      // Default to latest
      const latest = dateSelect.options[0]?.value;
      if (latest) {
        loadDateIntoTable(rows, latest);
      }
      dateSelect.addEventListener("change", () => {
        loadDateIntoTable(rows, dateSelect.value);
      });
    })
    .catch((err) => {
      // If history CSV unavailable, keep current page data
      if (dateSelect) {
        dateSelect.innerHTML = "";
        const opt = document.createElement("option");
        opt.value = "";
        opt.textContent = "No history available";
        opt.disabled = true;
        opt.selected = true;
        dateSelect.appendChild(opt);
      }
      console.warn("History CSV fetch failed:", err);
    });

  // Build Fish Species filter checkboxes dynamically from Fish Count text
  function buildFishFilters() {
    var speciesSet = new Set();
    var fishCol = table.column(4, { search: "applied" }).data().toArray();
    fishCol.forEach(function (text) {
      var s = String(text || "");
      // Match patterns like "12 Yellowtail", "3 Bluefin Tuna", separated by commas
      var regex = /(\d+)\s+([A-Za-z][A-Za-z\s&\-]+?)(?=,|$)/g;
      var m;
      while ((m = regex.exec(s)) !== null) {
        var name = m[2].trim();
        speciesSet.add(name);
      }
    });
    var container = document.getElementById("fishCountFilter");
    container.innerHTML = "";
    Array.from(speciesSet)
      .sort()
      .forEach(function (sp) {
        if (!sp) return;
        var id = "sp-" + sp.replace(/[^a-z0-9]+/gi, "-").toLowerCase();
        var label = document.createElement("label");
        label.innerHTML =
          '<input type="checkbox" id="' +
          id +
          '" value="' +
          sp.replace(/"/g, "&quot;") +
          '" checked> ' +
          sp;
        container.appendChild(label);
      });
  }

  // Apply filters on change
  function attachFilterHandlers() {
    $(document).on(
      "change",
      '#tripTypeFilter input[type="checkbox"]',
      function () {
        var selectedTripTypes = $(
          '#tripTypeFilter input[type="checkbox"]:checked'
        )
          .map(function () {
            var escapedValue = this.value.replace(
              /[-\/\\^$*+?.()|[\]{}]/g,
              "\\$&"
            );
            return "^" + escapedValue + "$"; // Match entire cell
          })
          .get()
          .join("|");
        table.column(2).search(selectedTripTypes, true, false).draw();
      }
    );

    $(document).on(
      "change",
      '#fishCountFilter input[type="checkbox"]',
      function () {
        var selectedFish = $('#fishCountFilter input[type="checkbox"]:checked')
          .map(function () {
            return this.value.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&");
          })
          .get();
        var pattern = selectedFish.length
          ? "\\b(" + selectedFish.join("|") + ")\\b"
          : ""; // show all if none selected
        table.column(4).search(pattern, true, false).draw();
      }
    );
  }

  // Initial build
  buildTripTypeFilters();
  buildFishFilters();
  attachFilterHandlers();
});
