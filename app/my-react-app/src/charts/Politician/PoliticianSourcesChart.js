import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import axios from 'axios';

const PoliticianSourcesChart = ({ entityId, entityType }) => {
  const [chartData, setChartData] = useState([]);
  const [entityName, setEntityName] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/entity-sources-count/${entityId}`, {
          params: {
            entity_type: entityType
          }
        });
        const { entity_name, sources } = response.data;
        const data = sources.map(source => ({
          value: source.article_count,
          name: source.name,
          image: source.image_url
        }));

        setEntityName(entity_name);
        setChartData(data);
      } catch (error) {
        console.error('Error fetching sources data:', error);
      }
    };

    fetchData();
  }, [entityId]);

  const getOption = () => ({
    title: {
      text: 'Distribuția articolelor pe surse',
      subtext: 'pentru ' + entityName,
      left: 'center',
      top: 0, // Adjust top value to increase space between title and chart
      textStyle: {
        color: '#000',
      },
      subtextStyle: {
        color: '#666',
        fontSize: 14,
      }
    },
    tooltip: {
      trigger: 'item',
      textStyle: {
        color: '#000'
      }
    },
    series: [
      {
        name: 'Sources',
        type: 'pie',
        top: 25,
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
                  return params.data.image;
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
      color: '#000'
    }
  });

  return (
    <div>
      <ReactECharts option={getOption()} style={{ height: '400px', width: '100%' }} />
    </div>
  );
};

export default PoliticianSourcesChart;
