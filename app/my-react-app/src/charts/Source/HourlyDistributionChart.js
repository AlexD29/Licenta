import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import ReactEcharts from 'echarts-for-react';
import * as echarts from 'echarts';

function SourceHourlyDistributionChart({ sourceId }) {
  const [chartData, setChartData] = useState([]);

  const fetchData = useCallback(async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/articles/hourly-distribution/source/${sourceId}`);
      setChartData(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }, [sourceId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getOption = () => ({
    title: {
      text: 'Distribuția Articolelor pe Ore',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 24 }, (_, i) => `${i}:00`),
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: 'Număr de Articole',
        type: 'line',
        data: chartData,
        itemStyle: {
          color: '#5470C6', // Line color
        },
        lineStyle: {
          color: '#5470C6', // Line color
        },
      },
    ],
  });

  return (
    <div className='chart' style={{ textAlign: 'center' }}>
      <ReactEcharts
        option={getOption()}
        style={{ height: 400, width: '100%' }}
      />
    </div>
  );
}

export default SourceHourlyDistributionChart;
