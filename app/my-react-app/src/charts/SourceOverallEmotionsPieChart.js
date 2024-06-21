import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import ReactEcharts from 'echarts-for-react';

function SourceOverallEmotionsPieChart({ sourceId, startDate, endDate }) {
  const [chartData, setChartData] = useState({
    positive: 0,
    negative: 0,
    neutral: 0,
  });

  const fetchData = useCallback(async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/articles/emotion-distribution/source/${sourceId}`, {
        params: {
          start_date: startDate,
          end_date: endDate,
        },
      });
      console.log('Fetched data:', response.data);
      setChartData(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }, [sourceId, startDate, endDate]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getOption = () => ({
    title: {
      text: 'Emotion Distribution for Source',
      left: 'center',
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b} : {c} ({d}%)',
    },
    legend: {
      top: 'bottom',
    },
    series: [
      {
        name: 'Emotions',
        type: 'pie',
        radius: '50%',
        data: [
          { value: chartData.positive, name: 'Positive', itemStyle: { color: '#18b52a' } },
          { value: chartData.negative, name: 'Negative', itemStyle: { color: '#ff1100' } },
          { value: chartData.neutral, name: 'Neutral', itemStyle: { color: '#597499' } },
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  });

  return (
    <div style={{ textAlign: 'center' }}>
      <ReactEcharts
        option={getOption()}
        style={{ height: 400, width: '100%' }}
      />
    </div>
  );
}

export default SourceOverallEmotionsPieChart;
