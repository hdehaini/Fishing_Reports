$(document).ready(function () {
  // Custom sorting for trip types
  // Custom sort mapping
  var customOrder = {
    "1/2 Day AM": 1,
    "1/2 Day PM": 2,
    "1/2 Day Twilight": 3,
    "3/4 Day": 4,
    "Full Day": 5,
    Overnight: 6,
    "1.5 Day": 7,
    "2 Day": 8,
    "2.5 Day": 9,
    "3 Day": 10,
    "3.5 Day": 11,
    "4 Day": 12,
  };

  // Initialize DataTable
  var table = $("#reports").DataTable({
    paging: false,
    info: false,
    order: [[2, "asc"]], // Set default sorting on the third column, ascending order
    columnDefs: [
      {
        targets: 2,
        render: function (data, type, row) {
          return type === "sort" ? customOrder[data] : data;
        },
        type: "num", // Ensure the sorting is handled as numeric
      },
    ],
  });

  $('#tripTypeFilter input[type="checkbox"]').on("change", function () {
    var selectedTripTypes = $('#tripTypeFilter input[type="checkbox"]:checked')
      .map(function () {
        return "\\b" + this.value + "\\b"; // Ensure exact match
      })
      .get()
      .join("|");
    table.column(2).search(selectedTripTypes, true, false).draw();
  });

  $('#fishCountFilter input[type="checkbox"]').on("change", function () {
    var selectedFishCounts = $(
      '#fishCountFilter input[type="checkbox"]:checked'
    )
      .map(function () {
        return this.value;
      })
      .get()
      .join("|");
    table.column(4).search(selectedFishCounts, true, false).draw();
  });
});
