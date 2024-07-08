import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';

const TopCityAuthorsPieChart = ({ cityId }) => {
  const [chartData, setChartData] = useState([]);
  const [name, setName] = useState([]);

  useEffect(() => {
    const fetchTopCityAuthorsData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/top-city-authors', {
          params: { city_id: cityId }
        });
        const data = response.data.top_authors_data;
        const name = response.data.city_name;
        setName(name);
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
        console.error('Error fetching top city authors data:', error);
      }
    };

    fetchTopCityAuthorsData();
  }, [cityId]);

  const option = {
    title: {
      text: 'Top Autori pentru ' + name,
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
            <strong>Positive:</strong> ${data.positiveCount}<br>
            <strong>Negative:</strong> ${data.negativeCount}<br>
            <strong>Neutral:</strong> ${data.neutralCount}
          </div>
        `;
      },
      textStyle: {
        color: '#000' // Set tooltip text color to black
      }
    },
    series: [
      {
        name: 'Top Autori pentru ' + name,
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

export default TopCityAuthorsPieChart;
