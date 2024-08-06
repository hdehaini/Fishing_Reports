document.addEventListener("DOMContentLoaded", function () {
  var currentDate = new Date();
  var options = { year: "numeric", month: "long", day: "numeric" };
  var title = `Fishing Reports ${currentDate.toLocaleDateString(
    "en-US",
    options
  )}`;
  document.title = title;
  document.querySelector("h1").textContent = title;

  var table = $("#reports").DataTable();

  var corsProxy = "https://bright-hill-peach.glitch.me/"; // Replace with your Glitch project URL
  var urls = [
    corsProxy +
      "https://www.sportfishingreport.com/landings/seaforth-sportfishing.php",
    corsProxy + "https://www.sportfishingreport.com/landings/h&m-landing.php",
    corsProxy +
      "https://www.sportfishingreport.com/landings/point-loma-sportfishing.php",
    corsProxy +
      "https://www.sportfishingreport.com/landings/fishermans-landing.php",
    corsProxy +
      "https://www.sportfishingreport.com/landings/oceanside-sea-center.php",
    corsProxy +
      "https://www.sportfishingreport.com/landings/ironclad-sportfishing.php",
  ];

  var reports = [];

  Promise.all(
    urls.map((url) =>
      fetch(url, {
        headers: {
          Origin: window.location.origin,
          "x-requested-with": "XMLHttpRequest",
        },
      }).then((response) => response.text())
    )
  )
    .then((responses) => {
      responses.forEach((html, index) => {
        var parser = new DOMParser();
        var doc = parser.parseFromString(html, "text/html");
        var tableElement = doc.querySelector("table.scale-table");

        if (tableElement) {
          var rows = tableElement.querySelectorAll("tr");
          for (var i = 2; i < rows.length; i++) {
            var cols = rows[i].querySelectorAll("td");
            if (cols.length === 4) {
              var boatName = cols[0].textContent.trim();
              var tripType = cols[1].textContent.trim();
              var anglers = cols[2].textContent.trim();
              var fishCount = cols[3].textContent.trim();
              reports.push({
                Source: urls[index],
                "Boat Name": boatName,
                "Trip Type": tripType,
                Anglers: anglers,
                "Fish Count": fishCount,
              });
            }
          }
        }
      });

      console.log("Reports:", reports);

      table.clear();
      reports.forEach((report) => {
        table.row
          .add([
            report["Source"],
            report["Boat Name"],
            report["Trip Type"],
            report["Anglers"],
            report["Fish Count"],
          ])
          .draw();
      });

      calculateAverages(reports);
    })
    .catch((error) => console.error("Error fetching data:", error));

  function calculateAverages(reports) {
    var fullDayReports = reports.filter((report) =>
      report["Trip Type"].includes("Full Day")
    );
    var fishTypes = ["Yellowtail", "Bluefin Tuna", "Yellowfin Tuna", "Dorado"];
    var averages = {};

    fishTypes.forEach((fish) => {
      var totalFish = 0;
      var totalAnglers = 0;
      fullDayReports.forEach((report) => {
        var match = report["Fish Count"].match(new RegExp(`(\\d+)\\s+${fish}`));
        if (match) {
          totalFish += parseInt(match[1], 10);
          totalAnglers += parseInt(report["Anglers"], 10);
        }
      });

      averages[fish] = totalAnglers > 0 ? totalFish / totalAnglers : 0;
    });

    var averagesHtml = "<ul>";
    for (var fish in averages) {
      averagesHtml += `<li>Average ${fish} per angler: ${averages[fish].toFixed(
        2
      )}</li>`;
    }
    averagesHtml += "</ul>";
    document.getElementById("averages").innerHTML = averagesHtml;
  }

  function filterTable() {
    var selectedTripTypes = [];
    $("#tripTypeFilter input:checked").each(function () {
      selectedTripTypes.push($(this).val());
    });

    var selectedFishCounts = [];
    $("#fishCountFilter input:checked").each(function () {
      selectedFishCounts.push($(this).val());
    });

    var tripTypeRegex =
      selectedTripTypes.length > 0 ? selectedTripTypes.join("|") : "";
    var fishCountRegex =
      selectedFishCounts.length > 0 ? selectedFishCounts.join("|") : "";

    table.column(2).search(tripTypeRegex, true, false).draw();
    table.column(4).search(fishCountRegex, true, false).draw();
  }

  $("#tripTypeFilter input").on("change", filterTable);
  $("#fishCountFilter input").on("change", filterTable);
});
