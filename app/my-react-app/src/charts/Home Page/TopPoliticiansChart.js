import React, { useEffect, useState } from 'react';
import axios from 'axios';
import EChartsReact from 'echarts-for-react';
import { useNavigate } from 'react-router-dom';

const TopPoliticiansChart = ({ startDate, endDate }) => {
  const [topPoliticians, setTopPoliticians] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTopPoliticians = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/top-politicians', {
          params: { start_date: startDate, end_date: endDate },
        });
        setTopPoliticians(response.data.top_politicians);
      } catch (error) {
        console.error('Error fetching top politicians:', error);
      }
    };

    fetchTopPoliticians();
  }, [startDate, endDate]);

  const handleChartClick = (params) => {
    const politician = topPoliticians[params.dataIndex];
    if (politician) {
      navigate(`/politician/${politician.politician_id}`);
    }
  };

  const richTextStyles = topPoliticians.reduce((styles, politician) => {
    styles[politician.politician_id] = {
      height: 50, // Adjust the image height to fit within the chart width
      width: 70,  // Set the image width to match the height for proper aspect ratio
      align: 'center',
      backgroundColor: {
        image: politician.image_url
      }
    };
    return styles;
  }, {});

  const option = {
    title: {
      text: 'Top Politicieni Astăzi',
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
      data: topPoliticians.map(p => p.politician_name),
      axisLabel: {
        formatter: function (value, index) {
          const politician = topPoliticians[index];
          return '{' + politician.politician_id + '| }';
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
        name: 'Total Articole',
        type: 'bar',
        data: topPoliticians.map(p => p.total_articles),
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
        name: 'Articole Pozitive',
        type: 'bar',
        data: topPoliticians.map(p => p.positive_articles),
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
        name: 'Articole Negative',
        type: 'bar',
        data: topPoliticians.map(p => p.negative_articles),
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
        name: 'Articole Neutre',
        type: 'bar',
        data: topPoliticians.map(p => p.neutral_articles),
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

export default TopPoliticiansChart;
