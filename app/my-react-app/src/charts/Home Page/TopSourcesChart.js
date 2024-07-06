import React, { useEffect, useState } from 'react';
import axios from 'axios';
import EChartsReact from 'echarts-for-react';
import { useNavigate } from 'react-router-dom';

const TopSourcesChart = ({ startDate, endDate }) => {
  const [topSources, setTopSources] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTopSources = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/top-sources', {
          params: { start_date: startDate, end_date: endDate },
        });
        setTopSources(response.data.top_sources);
      } catch (error) {
        console.error('Error fetching top sources:', error);
      }
    };

    fetchTopSources();
  }, [startDate, endDate]);

  const handleChartClick = (params) => {
    const source = topSources.find(e => e.name === params.name);
    if (source) {
      navigate(`/source/${source.source_id}`);
    }
  };

  const richTextStyles = topSources.reduce((styles, source) => {
    styles[source.source_id] = {
      height: 40,
      width: 40,
      align: 'center',
      backgroundColor: {
        image: source.image_url,
      },
    };
    return styles;
  }, {});

  const option = {
    title: {
      text: 'Top Surse Astăzi',
      left: 'center',
      textStyle: {
        color: '#000',
      },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter: function (params) {
        const source = topSources[params[0].dataIndex];
        return `
          <div style="display: flex; align-items: center;">
            <img src="${source.image_url}" alt="${source.name}" style="width: 20px; height: 20px; margin-right: 5px;" />
            ${source.name}
          </div>
          Total Articles: ${source.total_articles}
        `;
      },
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01],
    },
    yAxis: {
      type: 'category',
      data: topSources.map((source) => source.name),
      axisLabel: {
        interval: 0,
        formatter: function (value, index) {
          return '{' + topSources[index].source_id + '| }';
        },
        margin: 5, // Increase margin for better image display
        rich: richTextStyles,
      },
    },
    series: [
      {
        name: 'Positive Articles',
        type: 'bar',
        stack: 'total',
        data: topSources.map((source) => source.positive_articles),
        itemStyle: {
          color: '#18b52a', // Color for positive articles
        },
        label: {
          show: true,
          position: 'insideRight',
          formatter: function (params) {
            return params.value > 0 ? params.value : '';
          },
        },
        emphasis: {
          focus: 'series',
          itemStyle: {
            opacity: 0.7,
          },
        },
      },
      {
        name: 'Negative Articles',
        type: 'bar',
        stack: 'total',
        data: topSources.map((source) => source.negative_articles),
        itemStyle: {
          color: '#ff1100', // Color for negative articles
        },
        label: {
          show: true,
          position: 'insideRight',
          formatter: function (params) {
            return params.value > 0 ? params.value : '';
          },
        },
        emphasis: {
          focus: 'series',
          itemStyle: {
            opacity: 0.7,
          },
        },
      },
      {
        name: 'Neutral Articles',
        type: 'bar',
        stack: 'total',
        data: topSources.map((source) => source.neutral_articles),
        itemStyle: {
          color: '#597499', // Color for neutral articles
        },
        label: {
          show: true,
          position: 'insideRight',
          formatter: function (params) {
            return params.value > 0 ? params.value : '';
          },
        },
        emphasis: {
          focus: 'series',
          itemStyle: {
            opacity: 0.7,
          },
        },
      },
    ],
  };

  return (
    <EChartsReact option={option} style={{ height: 400, width: '100%' }} onEvents={{ 'click': handleChartClick }}/>
  );
};

export default TopSourcesChart;
