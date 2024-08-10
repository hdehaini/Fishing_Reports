fetch("../database/daily_averages.csv")
  .then((response) => response.text())
  .then((csv) => {
    const data = csv
      .split("\n")
      .filter((line) => line)
      .slice(1)
      .map((row) => row.split(","));
    const dates = data.map((row) => {
      const date = new Date(row[0] + "T00:00:00Z"); // Append time and timezone designator for UTC
      return isNaN(date) ? "Invalid Date" : date.toLocaleDateString();
    });

    const yellowtailAvg = data.map((row) => +row[1]);
    const bluefinAvg = data.map((row) => +row[2]);
    const doradoAvg = data.map((row) => +row[3]);
    const yellowfinAvg = data.map((row) => +row[4]);

    console.log(dates, yellowtailAvg, bluefinAvg, doradoAvg, yellowfinAvg);

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
          },
          {
            label: "Bluefin Tuna",
            data: bluefinAvg,
            borderColor: "rgb(54, 162, 235)",
            backgroundColor: "rgba(54, 162, 235, 0.5)",
            borderWidth: 2,
          },
          {
            label: "Dorado",
            data: doradoAvg,
            borderColor: "rgb(255, 206, 86)",
            backgroundColor: "rgba(255, 206, 86, 0.5)",
            borderWidth: 2,
          },
          {
            label: "Yellowfin Tuna",
            data: yellowfinAvg,
            borderColor: "rgb(75, 192, 192)",
            backgroundColor: "rgba(75, 192, 192, 0.5)",
            borderWidth: 2,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  });
