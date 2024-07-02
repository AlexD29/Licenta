import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import axios from 'axios';

const PoliticianArticlesDistribution = ({ politicianId }) => {
  const [chartData, setChartData] = useState({
    dates: [],
    positive_counts: [],
    negative_counts: [],
    neutral_counts: [],
    total_counts: []
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/politician-articles-distribution/${politicianId}`);
        setChartData(response.data);
      } catch (error) {
        console.error('Error fetching articles distribution data:', error);
      }
    };

    fetchData();
  }, [politicianId]);

  const getOption = () => ({
    title: {
      text: 'Distribuția articolelor în ultimele 7 zile\npentru Marcel Ciolacu',
      left: 'center',
      textStyle: {
        fontSize: 16,
        lineHeight: 20,
        width: 200,
        color: '#000'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#999'
        }
      },
      textStyle: {
        color: '#000' // Tooltip text color
      }
    },
    grid: {
      top: '20%'
    },
    xAxis: {
      type: 'category',
      data: chartData.dates,
      axisPointer: {
        type: 'shadow'
      },
      axisLabel: {
        color: '#000' // X-axis label text color
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      axisLabel: {
        formatter: '{value}',
        color: '#000'
      }
    },
    series: [
      {
        name: 'Positive',
        type: 'bar',
        data: chartData.positive_counts,
        itemStyle: {
          color: '#4caf50'
        }
      },
      {
        name: 'Negative',
        type: 'bar',
        data: chartData.negative_counts,
        itemStyle: {
          color: '#f44336'
        }
      },
      {
        name: 'Neutral',
        type: 'bar',
        data: chartData.neutral_counts,
        itemStyle: {
          color: '#9e9e9e'
        }
      },
      {
        name: 'Total Articles',
        type: 'line',
        data: chartData.total_counts,
        itemStyle: {
          color: '#5470c6'
        },
        lineStyle: {
          width: 2
        }
      }
    ],
    textStyle: {
        color: '#000' // Default text color for the entire chart
    }
  });

  return (
    <div>
      <ReactECharts option={getOption()} style={{ height: '400px', width: '100%' }} />
    </div>
  );
};

export default PoliticianArticlesDistribution;
