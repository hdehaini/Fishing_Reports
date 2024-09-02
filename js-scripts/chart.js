document.addEventListener("DOMContentLoaded", function () {
  fetch(
    "https://hdehaini.github.io/Fishing_Reports/database/daily_averages.csv"
  )
    .then((response) => response.text())
    .then((csv) => {
      const data = csv
        .split("\n")
        .map((row) => row.split(","))
        .slice(1);
      console.log("Raw CSV Data:", data);
      const validData = data.filter(
        (row) => row.length === 5 && row.every((value) => value.trim() !== "")
      );

      // Parsing dates for proper handling and keeping the full data array
      const originalData = validData.map((row) => {
        const [year, month, day] = row[0].split("-");
        const date = new Date(Date.UTC(year, month - 1, day));
        date.setMinutes(date.getMinutes() + date.getTimezoneOffset());
        console.log("Parsed Date:", date.toISOString()); // Log each date as it's parsed
        return {
          date: date,
          yellowtail: parseFloat(row[1]) || 0,
          bluefin: parseFloat(row[2]) || 0,
          dorado: parseFloat(row[3]) || 0,
          yellowfin: parseFloat(row[4]) || 0,
        };
      });

      const ctx = document.getElementById("fishChart").getContext("2d");
      const fishChart = new Chart(ctx, {
        type: "line",
        data: {
          labels: originalData.map((d) => d.date.toLocaleDateString("en-US")),
          datasets: [
            {
              label: "Yellowtail",
              data: originalData.map((d) => d.yellowtail),
              borderColor: "rgb(255, 206, 86)",
              backgroundColor: "rgba(255, 206, 86, 0.5)",
              borderWidth: 2,
              fill: false,
            },
            {
              label: "Bluefin Tuna",
              data: originalData.map((d) => d.bluefin),
              borderColor: "rgb(54, 162, 235)",
              backgroundColor: "rgba(54, 162, 235, 0.5)",
              borderWidth: 2,
              fill: false,
            },
            {
              label: "Dorado",
              data: originalData.map((d) => d.dorado),
              borderColor: "rgb(75, 192, 192)",
              backgroundColor: "rgba(75, 192, 192, 0.5)",
              borderWidth: 2,
              fill: false,
            },
            {
              label: "Yellowfin Tuna",
              data: originalData.map((d) => d.yellowfin),
              borderColor: "rgb(255, 99, 132)",
              backgroundColor: "rgba(255, 99, 132, 0.5)",
              borderWidth: 2,
              fill: false,
            },
          ],
        },
        options: {
          scales: { y: { beginAtZero: true } },
          elements: { line: { tension: 0, fill: false } },
          responsive: true,
          maintainAspectRatio: false,
        },
      });

      document
        .getElementById("pastWeek")
        .addEventListener("click", () => filterData(7));
      document
        .getElementById("pastMonth")
        .addEventListener("click", () => filterData(30));
      document
        .getElementById("pastYear")
        .addEventListener("click", () => filterData(365));

      function filterData(days) {
        const now = new Date(); // Gets the current date and time
        now.setHours(0, 0, 0, 0); // Normalize to start of the day, local time
        const nowUtc = new Date(
          Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())
        ); // Convert to UTC

        const filteredData = originalData.filter((d) => {
          const dayDifference = Math.floor(
            (nowUtc - d.date) / (1000 * 3600 * 24)
          );
          console.log(d.date.toISOString(), dayDifference);
          return dayDifference < days && dayDifference >= 0; // Adjusted to include from today to 'days' days ago
        });

        updateChart(filteredData);
        console.log(
          `Filtered for last ${days} days:`,
          filteredData.map((d) => d.date.toISOString().substring(0, 10)) // Display the filtered dates in ISO format
        );
      }

      function updateChart(filteredData) {
        fishChart.data.labels = filteredData.map((d) =>
          d.date.toLocaleDateString("en-US")
        );
        fishChart.data.datasets.forEach((dataset, index) => {
          dataset.data = filteredData.map((d) => {
            if (index === 0) return d.yellowtail;
            if (index === 1) return d.bluefin;
            if (index === 2) return d.dorado;
            if (index === 3) return d.yellowfin;
          });
        });
        fishChart.update();
      }
    })
    .catch((error) =>
      console.error("Error fetching or parsing the data:", error)
    );
});
