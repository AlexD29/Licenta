import React from 'react';
import ReactEcharts from 'echarts-for-react';

const EntityChart = ({ positive, negative, neutral, entityName }) => {
  const option = {
    title: {
      text: `Distribuția emoțiilor`,
      subtext: 'Ultimele 7 zile',
      left: 'center',
      bottom: '7%', // Move the title to the bottom
      textStyle: {
        color: 'black' // Set title font color to black
      },
      subtextStyle: {
        color: 'black' // Set subtext font color to black
      }
    },
    tooltip: {
      trigger: 'item',
      textStyle: {
        color: 'black' // Set tooltip text color to black
      }
    },
    series: [
      {
        name: 'Sentiment',
        type: 'pie',
        radius: ['40%', '70%'], // Increase the radius to make the pie chart larger
        center: ['50%', '35%'], // Center the pie chart vertically
        label: {
          show: false 
        },
        data: [
          { value: positive, name: 'Pozitive', itemStyle: { color: 'green' } },
          { value: negative, name: 'Negative', itemStyle: { color: 'red' } },
          { value: neutral, name: 'Neutre', itemStyle: { color: 'gray' } },
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          },
          label: {
            show: false 
          },
        }
      }
    ],
    textStyle: {
      color: 'black' // Set global text color to black
    }
  };

  return <ReactEcharts option={option} style={{ height: '250px', width: '100%' }} />; // Increase the height to accommodate the larger pie chart
};

export default EntityChart;
