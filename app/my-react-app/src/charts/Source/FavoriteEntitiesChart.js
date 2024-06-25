import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactEcharts from 'echarts-for-react';
import { useNavigate } from 'react-router-dom';

function SourceFavoriteEntitiesChart({ sourceId }) {
  const [chartData, setChartData] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/sources/favorite-entities/${sourceId}`);
        setChartData(response.data.top_entities);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [sourceId]);

  const handleChartClick = (params) => {
    const entity = chartData.find(e => e.entity_name === params.name);
    if (entity) {
      navigate(`/${entity.entity_type}/${entity.entity_id}`);
    }
  };

  const getOption = () => {
    const sortedData = chartData.sort((a, b) => b.total_count - a.total_count);

    const richTextStyles = sortedData.reduce((styles, entity) => {
      styles[entity.entity_id] = {
        height: 40, // Adjust the image height as needed
        align: 'left',
        backgroundColor: {
          image: entity.image_url
        }
      };
      return styles;
    }, {});

    return {
      title: {
        text: 'Top 5 Favorite Entities',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {
        show: false
      },
      grid: {
        left: 150 // Adjust to give more space for images
      },
      toolbox: {
        show: false
      },
      xAxis: {
        type: 'value',
        show: false // Remove the values from the bottom of the graph
      },
      yAxis: {
        type: 'category',
        inverse: true,
        data: sortedData.map(entity => entity.entity_name),
        axisLabel: {
          formatter: function (value, index) {
            const entity = sortedData[index];
            return '{' + entity.entity_id + '| }\n{value|' + value + '}';
          },
          margin: 20,
          rich: {
            value: {
              lineHeight: 30,
              align: 'left'
            },
            ...richTextStyles
          }
        }
      },
      series: [
        {
          name: 'Articles',
          type: 'bar',
          data: sortedData.map(entity => entity.total_count),
          label: {
            show: true,
            position: 'right',
            formatter: '{c}'
          },
          itemStyle: {
            color: '#3398DB'
          },
          barWidth: 30 // Adjust to reduce the space for bars
        }
      ]
    };
  };

  return (
    <div className='chart' style={{ textAlign: 'center' }}>
      <ReactEcharts
        option={getOption()}
        style={{ height: '500px', width: '100%' }}
        onEvents={{ 'click': handleChartClick }}
      />
    </div>
  );
}

export default SourceFavoriteEntitiesChart;
