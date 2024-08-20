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
    "Extended 1.5 Day": 7.5,
    "2 Day": 8,
    "2.5 Day": 9,
    "3 Day": 10,
    "3.5 Day": 11,
    "4 Day": 12,
  };

  var lastOrderIndex = 12; // Last known index
  var dynamicOrderMap = {}; // Map to store the order of the trip types

  // Initialize DataTable
  var table = $("#reports").DataTable({
    paging: false,
    info: false,
    order: [[2, "asc"]], // Set default sorting on the third column, ascending order
    columnDefs: [
      {
        targets: 2,
        render: function (data, type, row) {
          if (type === "sort") {
            if (customOrder.hasOwnProperty(data)) {
              return customOrder[data];
            } else if (!dynamicOrderMap.hasOwnProperty(data)) {
              dynamicOrderMap[data] = ++lastOrderIndex; // Assign a new order index
            }
            return dynamicOrderMap[data];
          }
          return data;
        },
        type: "num",
      },
    ],
  });

  $('#tripTypeFilter input[type="checkbox"]').on("change", function () {
    var selectedTripTypes = $('#tripTypeFilter input[type="checkbox"]:checked')
      .map(function () {
        var escapedValue = this.value.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&"); // Escape regex special chars
        return "\\b" + escapedValue + "\\b"; // Use word boundaries to ensure exact matches
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
