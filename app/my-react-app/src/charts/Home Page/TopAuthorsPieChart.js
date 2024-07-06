import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';

const TopAuthorsPieChart = () => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    const fetchTopAuthorsData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/top-authors');
        const data = response.data;
        const formattedData = data.map(item => ({
          value: item.articles_count,
          name: item.author,
          sourceName: item.source.name,
          sourceImage: item.source.image_url,
          positiveCount: item.positive_count,
          negativeCount: item.negative_count,
          neutralCount: item.neutral_count
        }));

        setChartData(formattedData);
      } catch (error) {
        console.error('Error fetching top authors data:', error);
      }
    };

    fetchTopAuthorsData();
  }, []);

  const option = {
    title: {
      text: 'Top Autori Astăzi',
      left: 'center',
      textStyle: {
        color: '#000' // Set title font color to black
      },
    },
    tooltip: {
      trigger: 'item',
      formatter: params => {
        const { name, value, data } = params;
        return `
          <div style="text-align: left;">
            <div style="display: flex; align-items: center;">
              <img src="${data.sourceImage}" alt="${data.sourceName}" style="width: 50px; height: auto; margin-right: 10px;">
              ${data.sourceName}
            </div>
            <strong>Total:</strong> ${value}<br>
            <strong>Pozitive:</strong> ${data.positiveCount}<br>
            <strong>Negative:</strong> ${data.negativeCount}<br>
            <strong>Neutre:</strong> ${data.neutralCount}
          </div>
        `;
      },
      textStyle: {
        color: '#000' // Set tooltip text color to black
      }
    },
    series: [
      {
        name: 'Top Autori Astăzi',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: true,
          position: 'inside',
          color: '#000', // Set label text color to black
          formatter: '{b|{b}}',
          fontWeight: 'bold',
          fontSize: 16,
          rich: {
            b: {
              backgroundColor: '#ffe6e6', // Set the background color for the label
              padding: [4, 6],
              borderRadius: 4,
              color: '#000', // Ensure text color is readable
              fontWeight: 'bold',
              fontSize: 16,
            }
          }
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 17,
            fontWeight: 'bold',
            color: '#000' // Set emphasis label text color to black
          }
        },
        labelLine: {
          show: true
        },
        data: chartData
      }
    ],
    textStyle: {
      color: '#000' // Set general text color to black
    }
  };
  

  return (
    <ReactECharts
      option={option}
      style={{ height: '400px', width: '100%' }}
    />
  );
};

export default TopAuthorsPieChart;
