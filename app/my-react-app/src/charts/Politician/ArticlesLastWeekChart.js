import React from 'react';
import ReactEcharts from 'echarts-for-react';
import * as echarts from 'echarts';
import { format } from 'date-fns';

const ArticlesLastMonthChart = () => {
  const generateRandomData = () => {
    let base = +new Date();
    let oneDay = 24 * 3600 * 1000;
    let date = [];
    let data = [];

    for (let i = 0; i < 30; i++) {
      const now = new Date(base - i * oneDay);
      date.unshift(format(now, 'dd/MM/yyyy'));
      data.unshift(Math.round(Math.random() * 20));
    }

    return { date, data };
  };

  const { date, data } = generateRandomData();

  const getOption = () => ({
    tooltip: {
      trigger: 'axis',
      position: function (pt) {
        return [pt[0], '10%'];
      }
    },
    title: {
      left: 'center',
      text: 'Articole despre acest subiect în ultima lună',
      textStyle: {
        color: '#000' // Title text color black
      }
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: date,
      axisLabel: {
        textStyle: {
          color: '#000' // X-axis labels text color black
        }
      }
    },
    yAxis: {
      type: 'value',
      boundaryGap: [0, '100%'],
      axisLabel: {
        textStyle: {
          color: '#000' // Y-axis labels text color black
        }
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: 'Articles',
        type: 'line',
        symbol: 'none',
        sampling: 'lttb',
        itemStyle: {
          color: 'rgb(255, 70, 131)'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgb(255, 158, 68)'
            },
            {
              offset: 1,
              color: 'rgb(255, 70, 131)'
            }
          ])
        },
        data: data
      }
    ],
    textStyle: {
      color: '#000' // Default text color for the entire chart
    }
  });

  return (
    <div className="chart" style={{ textAlign: 'center' }}>
      <ReactEcharts
        option={getOption()}
        style={{ height: 400, width: '100%' }}
      />
    </div>
  );
};

export default ArticlesLastMonthChart;
