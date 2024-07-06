import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';

const SentimentOverTimeChart = () => {
  const [chartData, setChartData] = useState({ negative: [], neutral: [], positive: [] });

  useEffect(() => {
    const fetchSentimentOverTimeData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/sentiment-over-time');
        const data = response.data;

        const negative = [];
        const neutral = [];
        const positive = [];

        data.forEach(item => {
            const parsedDate = new Date(item.published_date);
            const date = new Date(parsedDate.getUTCFullYear(), 
                                    parsedDate.getUTCMonth(), 
                                    parsedDate.getUTCDate(), 
                                    parsedDate.getUTCHours(), 
                                    parsedDate.getUTCMinutes(), 
                                    parsedDate.getUTCSeconds());
          const hours = date.getHours();
          const minutes = date.getMinutes();
          
          // Using hours for x-axis and minutes for y-axis
          const timeX = hours + minutes / 60; // For detailed x-axis placement
          const timeY = minutes; // For detailed y-axis placement

          const point = [timeX, timeY];

          if (item.emotion === 'Negative') {
            negative.push(point);
          } else if (item.emotion === 'Neutral') {
            neutral.push(point);
          } else if (item.emotion === 'Positive') {
            positive.push(point);
          }
        });

        setChartData({ negative, neutral, positive });
      } catch (error) {
        console.error('Error fetching sentiment over time data:', error);
      }
    };

    fetchSentimentOverTimeData();
  }, []);

  const option = {
    title: {
      text: 'Distribuția emoțiilor pe ore astăzi',
      left: 'center',
      textStyle: {
        color: '#000'  // Set title font color to black
      },
    },
    tooltip: {
      trigger: 'item',
      formatter: params => {
        const { value, seriesName } = params;
        const hours = Math.floor(value[0]);
        const minutes = Math.round((value[0] - hours) * 60);
        return `
          <div style="text-align: left;">
            <strong>Time:</strong> ${hours}:${minutes.toString().padStart(2, '0')}<br>
            <strong>Emotion:</strong> ${seriesName}
          </div>
        `;
      },
      textStyle: {
        color: '#000' // Set tooltip text color to black
      }
    },
    legend: {
      data: ['Negative', 'Neutre', 'Pozitive'],
      top: 25,
      textStyle: {
        color: '#000',
        
      }
    },
    xAxis: {
      type: 'value',
      min: 0,
      max: 24,
      interval: 2, // Show every 2 hours
      axisLabel: {
        formatter: value => `${Math.floor(value)}`,
        color: '#000' // Set x-axis labels color to black
      },
      splitLine: { // Remove vertical lines
        show: false
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 60,
      interval: 10, // Show every 10 minutes
      axisLabel: {
        formatter: value => `${value}`,
        color: '#000' // Set y-axis labels color to black
      },
      splitLine: { // Remove horizontal lines
        show: false
      }
    },
    series: [
      {
        name: 'Negative',
        type: 'scatter',
        symbolSize: 17,
        data: chartData.negative,
        itemStyle: {
          color: '#ff1100' // Set negative sentiment color
        }
      },
      {
        name: 'Neutre',
        type: 'scatter',
        symbolSize: 17,
        data: chartData.neutral,
        itemStyle: {
          color: '#597499' // Set neutral sentiment color
        }
      },
      {
        name: 'Pozitive',
        type: 'scatter',
        symbolSize: 17,
        data: chartData.positive,
        itemStyle: {
          color: '#18b52a' // Set positive sentiment color
        }
      }
    ],
    textStyle: {
      color: '#000' // Set general text color to black
    }
  };

  return (
    <ReactECharts
      option={option}
      style={{ height: '400px', width: '100%' }}
    />
  );
};

export default SentimentOverTimeChart;
