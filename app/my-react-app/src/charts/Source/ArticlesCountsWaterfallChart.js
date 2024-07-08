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
        text: 'Articole Publicate Astăzi',
        left: 'center',
        textStyle: {
          color: '#000', // Title text color black
          fontSize: 20,
          lineHeight: 24
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: function (params) {
          const tar = params[1];
          return `${tar.name}<br/>${tar.seriesName} : ${tar.value}`;
        },
        textStyle: {
          color: '#000' // Tooltip text color black
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
        data: ['Total', 'Pozitive', 'Negative', 'Neutre'],
        axisLabel: {
          textStyle: {
            color: '#000' // X-axis labels text color black
          }
        }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          textStyle: {
            color: '#000' // Y-axis labels text color black
          }
        }
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
            position: 'inside',
            textStyle: {
              color: 'white' // Labels text color black
            }
          },
          data: [total, positive, negative, neutral],
          itemStyle: {
            color: function (params) {
              const colors = ['#4682B4', '#00FF00', '#FF0000', '#808080'];
              return colors[params.dataIndex];
            }
          }
        }
      ],
      textStyle: {
        color: '#000' // Default text color for the entire chart
      }
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
