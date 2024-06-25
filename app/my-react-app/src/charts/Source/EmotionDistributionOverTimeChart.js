import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import ReactEcharts from 'echarts-for-react';
import * as echarts from 'echarts';
import { format } from 'date-fns';
import { ro } from 'date-fns/locale';

function SourceEmotionDistributionOverTimeChart({ sourceId }) {
  const [chartData, setChartData] = useState([]);

  // Calculate start date as January 1, 2024
  const startDate = '2024-01-01';

  // Calculate end date as today's date
  const endDate = new Date().toISOString().split('T')[0];

  const fetchData = useCallback(async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/articles/emotion-distribution-over-time/source/${sourceId}`, {
        params: {
          start_date: startDate,
          end_date: endDate,
        },
      });
      setChartData(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }, [sourceId, startDate, endDate]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getOption = () => ({
    title: {
      text: 'Distribuția Emoțiilor în Timp',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985',
        },
      },
    },
    legend: {
        top: 'bottom',
        itemGap: 20,
        data: [
          {
            name: 'Pozitiv',
            icon: 'circle',
            itemStyle: {
              color: 'green',
            },
          },
          {
            name: 'Negativ',
            icon: 'circle',
            itemStyle: {
              color: 'red',
            },
          },
          {
            name: 'Neutru',
            icon: 'circle',
            itemStyle: {
              color: 'gray',
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
        data: chartData.map((entry) => format(new Date(entry.date), 'dd MMM yyyy', { locale: ro })),
      },
    ],
    yAxis: [
      {
        type: 'value',
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
  });

  return (
    <div className='chart' style={{ textAlign: 'center' }}>
      <ReactEcharts
        option={getOption()}
        style={{ height: 400, width: '100%' }}
      />
    </div>
  );
}

export default SourceEmotionDistributionOverTimeChart;
