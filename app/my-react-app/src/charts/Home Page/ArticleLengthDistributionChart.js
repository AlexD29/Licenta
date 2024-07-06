import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';

const ArticleLengthDistributionChart = () => {
  const [chartData, setChartData] = useState([]);
  const [drilldownData, setDrilldownData] = useState(null);
  const [isMainChart, setIsMainChart] = useState(true);
  const [mainData, setMainData] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null); // Track selected category

  useEffect(() => {
    const fetchArticleLengthDistribution = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/article-length-distribution');
        const data = response.data.article_length_distribution;

        // Prepare main chart data
        const categories = Object.keys(data);
        const seriesData = categories.map(category => ({
          name: category,
          value: data[category].count,
          negative: data[category].negative,
          neutral: data[category].neutral,
          positive: data[category].positive
        }));

        setChartData(seriesData);
        setMainData(data);
      } catch (error) {
        console.error('Error fetching article length distribution:', error);
      }
    };

    fetchArticleLengthDistribution();
  }, []);

  const handleChartClick = (params) => {
    if (params.data && isMainChart) {
      const { name } = params.data;
      setSelectedCategory(name); // Track selected category
      setIsMainChart(false);

      // Prepare drilldown data
      const drilldownItem = {
        dataGroupId: name.toLowerCase(),
        data: [
          { name: 'Negative', value: mainData[name].negative },
          { name: 'Neutre', value: mainData[name].neutral },
          { name: 'Pozitive', value: mainData[name].positive }
        ]
      };

      setDrilldownData(drilldownItem);
    }
  };

  const getOption = () => ({
    title: {
      text: 'Distribuția articolelor din ultima săptămână\n după lungime',
      left: 'center',
      textStyle: {
        color: '#000' // Set the title color to black
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b} : {c}',
      textStyle: {
        color: '#000' // Set tooltip text color to black
      }
    },
    xAxis: {
      type: 'category',
      data: chartData.map(item => item.name),
      axisLabel: {
        color: '#000' // Set x-axis labels color to black
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#000' // Set y-axis labels color to black
      }
    },
    series: [
      {
        name: 'Articole',
        type: 'bar',
        data: chartData.map(item => ({
          name: item.name,
          value: item.value,
          itemStyle: {
            color: sentimentColor(item.name) // Set color based on sentiment
          }
        })),
      }
    ],
    textStyle: {
      color: '#000' // Set general text color to black
    }
  });

  const getDrilldownOption = () => {
    if (drilldownData) {
      return {
        title: {
          text: `Distribuția emoțiilor pentru articolele ${selectedCategory}`, // Include selected category in title
          top: 22, // Adjust title spacing from top
          left: 'center',
          textStyle: {
            color: '#000' // Set the title color to black
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b} : {c}',
          textStyle: {
            color: '#000' // Set tooltip text color to black
          }
        },
        xAxis: {
          type: 'category',
          data: drilldownData.data.map(item => item.name),
          axisLabel: {
            color: '#000' // Set x-axis labels color to black
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#000' // Set y-axis labels color to black
          }
        },
        series: [
          {
            name: 'Articole',
            type: 'bar',
            data: drilldownData.data.map(item => ({
              name: item.name,
              value: item.value,
              itemStyle: {
                color: sentimentColor(item.name) // Use color function based on sentiment
              }
            })),
          }
        ],
        graphic: [
          {
            type: 'text',
            left: 0,
            top: 0,
            style: {
              text: 'Inapoi',
              fontSize: 18
            },
            onclick: () => {
              setIsMainChart(true);
              setDrilldownData(null);
              setSelectedCategory(null); // Reset selected category
            }
          }
        ],
        textStyle: {
          color: '#000' // Set general text color to black
        }
      };
    } else {
      return {}; // Return empty object if drilldownData is null
    }
  };

  const sentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'Negative':
        return '#ff1100'; // Red
      case 'Neutre':
        return '#597499'; // Blue
      case 'Pozitive':
        return '#18b52a'; // Green
      default:
        return '#1890ff'; // Default blue
    }
  };

  return (
    <ReactECharts
      option={isMainChart ? getOption() : getDrilldownOption()}
      style={{ height: '400px', width: '100%' }}
      onEvents={{ click: handleChartClick }}
    />
  );
};

export default ArticleLengthDistributionChart;
