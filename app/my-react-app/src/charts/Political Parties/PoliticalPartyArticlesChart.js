import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';

const monthNamesRo = ['Ian', 'Feb', 'Mar', 'Apr', 'Mai', 'Iun', 'Iul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const PoliticalPartyArticlesChart = ({ politicalPartyId }) => {
  const [chartData, setChartData] = useState(null);
  const [politicalPartyName, setPoliticalPartyName] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/political-party-articles-distribution-since-january/${politicalPartyId}`);

        const { dates, positive_counts, negative_counts, neutral_counts, total_counts, political_party_name } = response.data;

        setPoliticalPartyName(political_party_name);

        // Prepare data for the chart
        const categories = Array.from(new Set(dates.map(date => date.substring(0, 7)))); // Extract months
        const monthlyData = categories.map(month => ({
          month,
          positive: 0,
          negative: 0,
          neutral: 0,
          total: 0,
        }));

        dates.forEach((date, index) => {
          const month = date.substring(0, 7);
          const monthData = monthlyData.find(data => data.month === month);
          monthData.positive += positive_counts[index];
          monthData.negative += negative_counts[index];
          monthData.neutral += neutral_counts[index];
          monthData.total += total_counts[index];
        });

        const rawData = [
          monthlyData.map(data => data.positive),
          monthlyData.map(data => data.negative),
          monthlyData.map(data => data.neutral),
        ];

        const totalData = monthlyData.map(data => data.total);

        const romanianMonths = categories.map(category => {
          const [year, month] = category.split('-');
          return `${monthNamesRo[parseInt(month, 10) - 1]}`;
        });

        setChartData({ categories: romanianMonths, rawData, totalData });

      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [politicalPartyId]);

  if (!chartData) {
    return <div>Loading...</div>;
  }

  const { categories, rawData, totalData } = chartData;

  const series = [
    {
      name: 'Pozitive',
      type: 'bar',
      stack: 'total',
      barWidth: '80%',
      label: {
        show: true,
        position: 'inside',
        formatter: (params) => `${((params.value / totalData[params.dataIndex]) * 100).toFixed(1)}%`,
        color: 'white',
      },
      itemStyle: {
        color: 'green',
      },
      data: rawData[0]
    },
    {
      name: 'Negative',
      type: 'bar',
      stack: 'total',
      barWidth: '80%',
      label: {
        show: true,
        position: 'inside',
        formatter: (params) => `${((params.value / totalData[params.dataIndex]) * 100).toFixed(1)}%`,
        color: 'white',
      },
      itemStyle: {
        color: 'red',
      },
      data: rawData[1]
    },
    {
      name: 'Neutre',
      type: 'bar',
      stack: 'total',
      barWidth: '80%',
      label: {
        show: true,
        position: 'inside',
        formatter: (params) => `${((params.value / totalData[params.dataIndex]) * 100).toFixed(1)}%`,
        color: 'white',
      },
      itemStyle: {
        color: 'gray',
      },
      data: rawData[2]
    }
  ];

  const option = {
    title: {
      text: 'Distribuția emoții/lună',
      subtext: 'pentru ' + politicalPartyName,
      left: 'center',
      textStyle: {
        color: 'black'
      },
      subtextStyle: {
        color: 'black'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        let result = `${params[0].name}<br/>`;
        params.forEach(item => {
          result += `${item.marker} ${item.seriesName}: ${item.value} (${((item.value / totalData[item.dataIndex]) * 100).toFixed(1)}%)<br/>`;
        });
        return result;
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '15%',
      bottom: '10%'
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: 'black'
      }
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        color: 'black'
      }
    },
    series
  };

  return <ReactECharts option={option} style={{ height: '500px', width: '100%' }} />;
};

export default PoliticalPartyArticlesChart;
