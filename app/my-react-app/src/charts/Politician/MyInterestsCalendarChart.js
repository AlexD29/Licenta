import React, { useState, useEffect } from 'react';
import ReactEcharts from 'echarts-for-react';
import * as echarts from 'echarts';
import { format } from 'date-fns';
import { ro } from 'date-fns/locale';

const MyInterestsCalendarChart = () => {
  const [chartData, setChartData] = useState([]);

  const generateRandomData = () => {
    const data = [];
    const currentDate = new Date();
    const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();

    for (let i = 1; i <= daysInMonth; i++) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), i);
      data.push({
        date,
        positive: Math.floor(Math.random() * 10),
        negative: Math.floor(Math.random() * 10),
        neutral: Math.floor(Math.random() * 10)
      });
    }

    setChartData(data);
  };

  useEffect(() => {
    generateRandomData();
  }, []);

  const getOption = () => ({
    title: {
      text: 'Distribuția Emoțiilor în ultima lună\npentru favoritele tale',
      left: 'center',
      textStyle: {
        color: '#000' // Set title color to black
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985',
        },
      },
      textStyle: {
        color: '#000' // Set tooltip text color to black
      }
    },
    legend: {
      top: 'bottom',
      itemGap: 20,
      textStyle: {
        color: '#000' // Set legend text color to black
      },
      data: [
        {
          name: 'Pozitiv',
          icon: 'circle',
          itemStyle: {
            color: '#4caf50',
          },
        },
        {
          name: 'Negativ',
          icon: 'circle',
          itemStyle: {
            color: '#f44336',
          },
        },
        {
          name: 'Neutru',
          icon: 'circle',
          itemStyle: {
            color: '#9e9e9e',
          },
        },
      ],
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true,
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: chartData.map((entry) => format(entry.date, 'dd MMM yyyy', { locale: ro })),
        axisLabel: {
          color: '#000' // Set x-axis label color to black
        }
      },
    ],
    yAxis: [
      {
        type: 'value',
        axisLabel: {
          color: '#000' // Set y-axis label color to black
        }
      },
    ],
    series: [
      {
        name: 'Pozitiv',
        type: 'line',
        stack: 'Total',
        smooth: true,
        lineStyle: {
          width: 0,
        },
        showSymbol: false,
        areaStyle: {
          opacity: 0.8,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgb(0, 255, 0)', // Green
            },
            {
              offset: 1,
              color: 'rgb(34, 139, 34)', // Darker Green
            },
          ]),
        },
        emphasis: {
          focus: 'series',
        },
        data: chartData.map((entry) => entry.positive),
      },
      {
        name: 'Negativ',
        type: 'line',
        stack: 'Total',
        smooth: true,
        lineStyle: {
          width: 0,
        },
        showSymbol: false,
        areaStyle: {
          opacity: 0.8,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgb(255, 0, 0)', // Red
            },
            {
              offset: 1,
              color: 'rgb(139, 0, 0)', // Darker Red
            },
          ]),
        },
        emphasis: {
          focus: 'series',
        },
        data: chartData.map((entry) => entry.negative),
      },
      {
        name: 'Neutru',
        type: 'line',
        stack: 'Total',
        smooth: true,
        lineStyle: {
          width: 0,
        },
        showSymbol: false,
        areaStyle: {
          opacity: 0.8,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgb(128, 128, 128)', // Gray
            },
            {
              offset: 1,
              color: 'rgb(105, 105, 105)', // Darker Gray
            },
          ]),
        },
        emphasis: {
          focus: 'series',
        },
        data: chartData.map((entry) => entry.neutral),
      },
    ],
    textStyle: {
      color: '#000' // Default text color for the entire chart
    }
  });

  return (
    <div className='chart' style={{ textAlign: 'center' }}>
      <ReactEcharts
        option={getOption()}
        style={{ height: 400, width: '100%' }}
      />
    </div>
  );
};

export default MyInterestsCalendarChart;
