import React from 'react';
import ReactEcharts from 'echarts-for-react';
import * as echarts from 'echarts';

const NightingaleChart = () => {
  const entities = ['USR', 'Entity 2', 'Entity 3', 'Entity 4', 'Entity 5', 'Entity 6', 'Marcel Ciolacu', 'PSD'];

  const generateRandomData = (names) => {
    return names.map(name => ({
      value: Math.floor(Math.random() * 100) + 1,
      name: name
    }));
  };

  const option = {
    title: {
      text: 'Favoritele tale cu cele\nmai multe articole săptămâna asta',
      left: 'center',
      textStyle: {
        color: '#000' // Title color black
      },
      subtextStyle: {
        color: '#000' // Subtitle color black
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b} : {c} ({d}%)'
    },
    series: [
      {
        name: 'Area Mode',
        type: 'pie',
        radius: [20, 140],
        center: ['75%', '50%'],
        roseType: 'area',
        itemStyle: {
          borderRadius: 5
        },
        data: generateRandomData(entities)
      }
    ],
    textStyle: {
      color: '#000' // Default text color for the entire chart
    }
  };

  return (
    <div className='chart' style={{ textAlign: 'center' }}>
      <ReactEcharts
        option={option}
        style={{ height: 400, width: '100%' }}
      />
    </div>
  );
};

export default NightingaleChart;
