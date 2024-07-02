import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import axios from 'axios';

const PoliticianSourcesChart = ({ politicianId }) => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/politician-sources-count/${politicianId}`);
        const sources = response.data;
        const data = sources.map(source => ({
          value: source.article_count,
          name: source.name,
          image: source.image_url // include the image URL in the data
        }));
        setChartData(data);
      } catch (error) {
        console.error('Error fetching sources data:', error);
      }
    };

    fetchData();
  }, [politicianId]);

  const getOption = () => ({
    title: {
      text: ['Distribuția articolelor pe surse pentru Marcel Ciolacu'],
      left: 'center',
      textStyle: {
        color: '#000', // Default text color for the entire chart
        fontSize: 16,
        lineHeight: 20
      }
    },
    tooltip: {
      trigger: 'item',
      textStyle: {
        color: '#000' // Tooltip text color
      }
    },
    series: [
      {
        name: 'Sources',
        type: 'pie',
        top: 0,
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          position: 'outside',
          formatter: function (params) {
            const { name, value, percent, data } = params;
            return `{icon|} {name|${name}}\n{value|${value} (${percent}%)}`;
          },
          rich: {
            icon: {
              height: 20,
              align: 'center',
              backgroundColor: {
                image: function (params) {
                  return params.data.image; // Use image URL for the icon
                }
              }
            },
            name: {
              fontSize: 12,
              color: '#333'
            },
            value: {
              fontSize: 10,
              color: '#999'
            }
          }
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: true
        },
        data: chartData
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

export default PoliticianSourcesChart;
