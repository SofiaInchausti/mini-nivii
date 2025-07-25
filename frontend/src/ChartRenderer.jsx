import { Bar, Line, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Tooltip, Legend } from 'chart.js';
import React from 'react'

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Tooltip, Legend);

export default function ChartRenderer({ chartType, data, options }) {
  if (!chartType || !data) {
    return <div className="text-gray-500">No hay datos para graficar.</div>;
  }
  if (chartType === 'bar') {
    return <Bar data={data} options={options} />;
  }
  if (chartType === 'line') {
    return <Line data={data} options={options} />;
  }
  if (chartType === 'pie') {
    return <Pie data={data} options={options} />;
  }
  return <div className="text-gray-500">Tipo de gráfico no soportado: {chartType}</div>;
} 