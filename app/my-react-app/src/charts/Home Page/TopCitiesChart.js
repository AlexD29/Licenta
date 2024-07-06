import React, { useEffect, useState } from 'react';
import axios from 'axios';
import EChartsReact from 'echarts-for-react';
import { useNavigate } from 'react-router-dom';

const TopCitiesChart = ({ startDate, endDate }) => {
  const [topCities, setTopCities] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTopCities = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/top-cities', {
          params: { start_date: startDate, end_date: endDate },
        });
        setTopCities(response.data.top_cities);
      } catch (error) {
        console.error('Error fetching top cities:', error);
      }
    };

    fetchTopCities();
  }, [startDate, endDate]);


  const handleChartClick = (params) => {
    const city = topCities[params.dataIndex];
    if (city) {
      navigate(`/city/${city.city_id}`);
    }
  };

  const richTextStyles = topCities.reduce((styles, city) => {
    styles[city.city_id] = {
      height: 50, // Adjust the image height to fit within the chart width
      width: 70,  // Set the image width to match the height for proper aspect ratio
      align: 'center',
      backgroundColor: {
        image: city.image_url // Use the city's image_url for background image
      }
    };
    return styles;
  }, {});

  const option = {
    title: {
      text: 'Top Orașe Astăzi',
      left: 'center',
      textStyle: {
        color: '#000'  // Set title font color to black
      },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function (params) {
        let tooltipText = `${params[0].name}<br/>`;
        params.forEach(param => {
          tooltipText += `${param.seriesName}: ${param.value}<br/>`;
        });
        return tooltipText;
      }
    },
    xAxis: {
      type: 'category',
      axisTick: { show: false },
      data: topCities.map(c => c.name),
      axisLabel: {
        formatter: function (value, index) {
          const city = topCities[index];
          return '{' + city.city_id + '| }';
        },
        margin: 10,
        rich: richTextStyles
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#000'  // Set y-axis label color to black
      }
    },
    series: [
      {
        name: 'Total Articles',
        type: 'bar',
        data: topCities.map(c => c.total_articles),
        label: {
          show: true,
          position: 'top',
          formatter: '{c}'
        },
        itemStyle: {
          color: '#1c55e6'  // Default color for total articles
        },
        barWidth: 20,  // Adjust to reduce the space for bars
        emphasis: {
          focus: 'series',
          itemStyle: {
            opacity: 0.7
          }
        }
      },
      {
        name: 'Positive Articles',
        type: 'bar',
        data: topCities.map(c => c.positive_articles),
        itemStyle: {
          color: '#18b52a'  // Color for positive articles
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}'
        },
        barWidth: 15,
        emphasis: {
          focus: 'series',
          itemStyle: {
            opacity: 0.7
          }
        }
      },
      {
        name: 'Negative Articles',
        type: 'bar',
        data: topCities.map(c => c.negative_articles),
        itemStyle: {
          color: '#ff1100'  // Color for negative articles
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}'
        },
        barWidth: 15,
        emphasis: {
          focus: 'series',
          itemStyle: {
            opacity: 0.7
          }
        }
      },
      {
        name: 'Neutral Articles',
        type: 'bar',
        data: topCities.map(c => c.neutral_articles),
        itemStyle: {
          color: '#597499'  // Color for neutral articles
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}'
        },
        barWidth: 15,
        emphasis: {
          focus: 'series',
          itemStyle: {
            opacity: 0.7
          }
        }
      },
    ],
  };

  return (
    <EChartsReact
      option={option}
      style={{ height: 400, width: '100%' }}
      onEvents={{ 'click': handleChartClick }}
    />
  );
};

export default TopCitiesChart;
