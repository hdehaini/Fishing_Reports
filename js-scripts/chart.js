document.addEventListener("DOMContentLoaded", function () {
  fetch("/database/daily_averages.csv")
    .then((response) => response.text())
    .then((csv) => {
      const data = csv
        .split("\n")
        .map((row) => row.split(","))
        .slice(1); // Split CSV into rows and cells, and skip the header row

      const validData = data.filter(
        (row) => row.length === 5 && row.every((value) => value.trim() !== "") // Ensure every row has exactly 5 values and no empty strings
      );

      const dates = validData.map((row) => {
        const [year, month, day] = row[0].split("-");
        // Create a date that is midday UTC to avoid any timezone causing a date shift
        const date = new Date(Date.UTC(year, month - 1, day, 12));
        return date.toLocaleDateString("en-US", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          timeZone: "UTC", // Ensure we are considering the date in UTC
        });
      });

      const yellowtailAvg = validData.map((row) => parseFloat(row[1]) || 0);
      const bluefinAvg = validData.map((row) => parseFloat(row[2]) || 0);
      const doradoAvg = validData.map((row) => parseFloat(row[3]) || 0);
      const yellowfinAvg = validData.map((row) => parseFloat(row[4]) || 0);

      const ctx = document.getElementById("fishChart").getContext("2d");
      const fishChart = new Chart(ctx, {
        type: "line",
        data: {
          labels: dates,
          datasets: [
            {
              label: "Yellowtail",
              data: yellowtailAvg,
              borderColor: "rgb(255, 99, 132)",
              backgroundColor: "rgba(255, 99, 132, 0.5)",
              borderWidth: 2,
              fill: false,
            },
            {
              label: "Bluefin Tuna",
              data: bluefinAvg,
              borderColor: "rgb(54, 162, 235)",
              backgroundColor: "rgba(54, 162, 235, 0.5)",
              borderWidth: 2,
              fill: false,
            },
            {
              label: "Dorado",
              data: doradoAvg,
              borderColor: "rgb(255, 206, 86)",
              backgroundColor: "rgba(255, 206, 86, 0.5)",
              borderWidth: 2,
              fill: false,
            },
            {
              label: "Yellowfin Tuna",
              data: yellowfinAvg,
              borderColor: "rgb(75, 192, 192)",
              backgroundColor: "rgba(75, 192, 192, 0.5)",
              borderWidth: 2,
              fill: false,
            },
          ],
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
            },
          },
          elements: {
            line: {
              tension: 0, // Disables bezier curves
              fill: false,
            },
          },
          responsive: true,
          maintainAspectRatio: false,
        },
      });

      document.querySelectorAll('input[name="fishType"]').forEach((input) => {
        input.addEventListener("change", function () {
          fishChart.data.datasets.forEach((dataset) => {
            if (dataset.label === this.value) {
              dataset.hidden = !this.checked; // Toggle the visibility of the dataset
            }
          });
          fishChart.update();
        });
      });
    });
});
