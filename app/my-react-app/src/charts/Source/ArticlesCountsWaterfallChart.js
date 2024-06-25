import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import ReactEcharts from 'echarts-for-react';

function SourceArticlesCountsWaterfallChart({ sourceId }) {
  const [counts, setCounts] = useState({ total: 0, positive: 0, negative: 0, neutral: 0 });

  const fetchCounts = useCallback(async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/articles/counts-today/source/${sourceId}`);
      setCounts(response.data);
    } catch (error) {
      console.error('Error fetching article counts:', error);
    }
  }, [sourceId]);

  useEffect(() => {
    fetchCounts();
  }, [fetchCounts]);

  const getOption = () => {
    const { total, positive, negative, neutral } = counts;
    return {
      title: {
        text: 'Articole Publicate Azi',
        left: 'center',
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: function (params) {
          const tar = params[1];
          return `${tar.name}<br/>${tar.seriesName} : ${tar.value}`;
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        splitLine: { show: false },
        data: ['Total', 'Pozitive', 'Negative', 'Neutre']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: 'Placeholder',
          type: 'bar',
          stack: 'Total',
          itemStyle: {
            borderColor: 'transparent',
            color: 'transparent'
          },
          emphasis: {
            itemStyle: {
              borderColor: 'transparent',
              color: 'transparent'
            }
          },
          data: [0, total - positive, total - positive - negative, 0]
        },
        {
          name: 'Număr Articole',
          type: 'bar',
          stack: 'Total',
          label: {
            show: true,
            position: 'inside'
          },
          data: [total, positive, negative, neutral],
          itemStyle: {
            color: function (params) {
              const colors = ['#4682B4','#00FF00', '#FF0000', '#808080'];
              return colors[params.dataIndex];
            }
          }
        }
      ]
    };
  };

  return (
    <div className='chart' style={{ textAlign: 'center' }}>
      <ReactEcharts
        option={getOption()}
        style={{ height: 400, width: '100%' }}
      />
    </div>
  );
}

export default SourceArticlesCountsWaterfallChart;
