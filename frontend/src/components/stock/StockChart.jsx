import { useMemo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { CHART_COLORS } from "../../constants";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip
);

function StockChart({ ticker, historyData }) {
  const chartData = useMemo(() => {
    if (!historyData || !historyData.data || historyData.data.length === 0) {
      return {
        labels: [],
        datasets: [],
      };
    }

    const prices = historyData.data || historyData.prices || historyData;
    
    const labels = prices.map((item) => {
      const date = item.date || item.timestamp || item.time;
      return new Date(date).toLocaleDateString();
    });

    const data = prices.map((item) => {
      return item.price || item.close || item.current_price || 0;
    });

    return {
      labels,
      datasets: [
        {
          label: `${ticker} Price`,
          data,
          borderColor: CHART_COLORS.PRIMARY,
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          tension: 0.1,
        },
      ],
    };
  }, [historyData, ticker]);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: "index",
        intersect: false,
        backgroundColor: "rgba(20, 27, 59, 0.9)",
        titleColor: CHART_COLORS.PRIMARY,
        bodyColor: "#F9FAFB",
        borderColor: "rgba(139, 92, 246, 0.3)",
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        ticks: {
          color: CHART_COLORS.TEXT,
        },
        grid: {
          color: CHART_COLORS.GRID,
        },
      },
      y: {
        beginAtZero: false,
        ticks: {
          callback: (value) => `$${value.toLocaleString()}`,
          color: CHART_COLORS.TEXT,
        },
        grid: {
          color: CHART_COLORS.GRID,
        },
      },
    },
  };

  if (!historyData || (Array.isArray(historyData) && historyData.length === 0)) {
    return (
      <div className="stock-chart-empty">
        No historical data available
      </div>
    );
  }

  return (
    <div className="stock-chart-container">
      <Line data={chartData} options={options} />
    </div>
  );
}

export default StockChart;
