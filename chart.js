fetch("daily_averages.csv")
  .then((response) => response.text())
  .then((csv) => {
    const data = csv
      .split("\n")
      .slice(1)
      .map((row) => row.split(","));
    const dates = data.map((row) => row[0]);
    const yellowtailAvg = data.map((row) => +row[1]);
    const bluefinAvg = data.map((row) => +row[2]);
    // Other fish types similarly...

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
          },
          {
            label: "Bluefin Tuna",
            data: bluefinAvg,
            borderColor: "rgb(54, 162, 235)",
            backgroundColor: "rgba(54, 162, 235, 0.5)",
          },
          // Add other datasets for different fish types...
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
