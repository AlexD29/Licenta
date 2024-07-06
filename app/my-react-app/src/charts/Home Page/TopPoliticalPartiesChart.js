import React, { useState, useEffect } from 'react';
import axios from 'axios';
import EChartsReact from 'echarts-for-react';
import { useNavigate } from 'react-router-dom';

const TopPoliticalPartiesChart = ({ startDate, endDate }) => {
  const [topPoliticalParties, setTopPoliticalParties] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTopPoliticalParties = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/top-political-parties', {
          params: { start_date: startDate, end_date: endDate },
        });
        setTopPoliticalParties(response.data.top_political_parties);
      } catch (error) {
        console.error('Error fetching top political parties:', error);
      }
    };

    fetchTopPoliticalParties();
  }, [startDate, endDate]);

  const handleChartClick = (params) => {
    const party = topPoliticalParties[params.dataIndex];
    if (party) {
      navigate(`/political-party/${party.party_id}`);
    }
  };

  const richTextStyles = topPoliticalParties.reduce((styles, party) => {
    styles[party.party_id] = {
      height: 50, // Adjust the image height to fit within the chart width
      width: 50,  // Set the image width to match the height for proper aspect ratio
      align: 'center',
      backgroundColor: {
        image: party.image_url
      }
    };
    return styles;
  }, {});

  const option = {
    title: {
      text: 'Top Partide Politice Astăzi',
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
      data: topPoliticalParties.map(p => p.abbreviation),
      axisLabel: {
        formatter: function (value, index) {
          const party = topPoliticalParties[index];
          return '{' + party.party_id + '| }';
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
        data: topPoliticalParties.map(p => p.total_articles),
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
        data: topPoliticalParties.map(p => p.positive_articles),
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
        data: topPoliticalParties.map(p => p.negative_articles),
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
        data: topPoliticalParties.map(p => p.neutral_articles),
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

export default TopPoliticalPartiesChart;
