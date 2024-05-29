import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Legend, Tooltip } from 'recharts';

function TodayPiechart() {
  const [emotionsData, setEmotionsData] = useState([]);

  useEffect(() => {
    const fetchEmotionsData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/articles/today');
        const articles = response.data.articles;

        const emotionsCount = articles.reduce((acc, article) => {
          acc[article.emotion] = (acc[article.emotion] || 0) + 1;
          return acc;
        }, {});

        const totalEmotions = Object.values(emotionsCount).reduce((acc, count) => acc + count, 0);

        const colors = ['#ff1100', '#18b52a', '#597499'];
        const emotionsWithPercentages = Object.keys(emotionsCount).map((emotion, index) => ({
          name: emotion,
          value: emotionsCount[emotion],
          color: colors[index],
          percentage: ((emotionsCount[emotion] / totalEmotions) * 100).toFixed(2),
        }));

        setEmotionsData(emotionsWithPercentages);
      } catch (error) {
        console.error('Error fetching emotions data:', error);
      }
    };

    fetchEmotionsData();
  }, []);

  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percentage }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * (Math.PI / 180));
    const y = cy + radius * Math.sin(-midAngle * (Math.PI / 180));

    return (
      <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central">
        {`${percentage}%`}
      </text>
    );
  };

  return (
    <div style={{ textAlign: 'center' }}>
      <h2>Today's Articles Emotions</h2>
      <div style={{ display: 'inline-block' }}>
        <PieChart width={400} height={400}>
            <Pie
            data={emotionsData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={150}
            fill="#8884d8"
            label={renderCustomizedLabel}
            >
            {emotionsData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
            </Pie>
        </PieChart>
      </div>
    </div>
  );
}

export default TodayPiechart;
