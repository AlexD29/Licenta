import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import axios from 'axios';

const PoliticalPartyArticlesDistribution = ({ politicalPartyId }) => {
  const [chartData, setChartData] = useState({
    political_party_name: '',
    dates: [],
    positive_counts: [],
    negative_counts: [],
    neutral_counts: [],
    total_counts: []
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/political-party-articles-distribution-last-7-days/${politicalPartyId}`);
        setChartData(response.data);
      } catch (error) {
        console.error('Error fetching articles distribution data:', error);
      }
    };

    fetchData();
  }, [politicalPartyId]);

  const getOption = () => ({
    title: {
      text: 'Distribuția articolelor în ultimele 7 zile',
      subtext: 'pentru ' + chartData.political_party_name,
      left: 'center',
      textStyle: {
        fontSize: 16,
        lineHeight: 20,
        width: 200,
        color: '#000'
      },
      subtextStyle: {
        fontSize: 14,
        lineHeight: 18,
        color: '#666'
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
          color: 'green'
        }
      },
      {
        name: 'Negative',
        type: 'bar',
        data: chartData.negative_counts,
        itemStyle: {
          color: 'red'
        }
      },
      {
        name: 'Neutral',
        type: 'bar',
        data: chartData.neutral_counts,
        itemStyle: {
          color: 'gray'
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

export default PoliticalPartyArticlesDistribution;
