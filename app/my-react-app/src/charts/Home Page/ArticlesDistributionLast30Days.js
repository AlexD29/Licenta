import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import axios from 'axios';

const ArticlesDistributionLast30Days = () => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/articles/last_30_days');
        const data = response.data.map(item => ({
          name: new Date(item.date).toString(),
          value: [item.date, item.total_articles]
        }));
        setChartData(data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  const getOption = () => ({
    title: {
      text: 'Distribuția articolelor în ultimele 30 de zile',
      left: 'center',
      textStyle: {
        color: '#000' // Set the title color to black
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        const date = new Date(params[0].name);
        return `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()} : ${params[0].value[1]}`;
      },
      axisPointer: {
        animation: false
      },
      textStyle: {
        color: '#000' // Set tooltip text color to black
      }
    },
    xAxis: {
      type: 'time',
      splitLine: {
        show: false
      },
      axisLabel: {
        color: '#000' // Set x-axis labels color to black
      }
    },
    yAxis: {
      type: 'value',
      boundaryGap: [0, '100%'],
      splitLine: {
        show: false
      },
      axisLabel: {
        color: '#000' // Set y-axis labels color to black
      }
    },
    series: [
      {
        name: 'Total Articles',
        type: 'line',
        showSymbol: false,
        data: chartData,
        lineStyle: {
          width: 4 // Set the line thickness
        },
      }
    ],
    textStyle: {
      color: '#000' // Set general text color to black
    }
  });

  return <ReactECharts option={getOption()} style={{ height: '500px', width: '100%' }} />;
};

export default ArticlesDistributionLast30Days;
