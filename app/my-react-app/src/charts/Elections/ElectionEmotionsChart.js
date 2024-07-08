import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';

const translateCategoryToElectionType = (category) => {
  const translations = {
    'alegeri-locale': 'Alegeri Locale',
    'alegeri-prezidentiale': 'Alegeri Prezidențiale',
    'alegeri-parlamentare': 'Alegeri Parlamentare',
    'alegeri-europarlamentare': 'Alegeri Europarlamentare'
  };
  return translations[category] || 'Toate Alegerile'; // Default to 'Toate Alegerile' if not found
};

const ElectionEmotionsChart = ({ category }) => {
  const [chartData, setChartData] = useState([]);
  const [totalArticles, setTotalArticles] = useState(0);
  const electionType = translateCategoryToElectionType(category);

  useEffect(() => {
    const fetchElectionData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/election-articles-stats', {
          params: {
            election_type: electionType
          }
        });

        const data = response.data.emotions;
        const chartData = [
          { value: data.positive, name: 'Positive' },
          { value: data.negative, name: 'Negative' },
          { value: data.neutral, name: 'Neutral' }
        ];

        const total = data.positive + data.negative + data.neutral;
        setTotalArticles(total);
        setChartData(chartData);
      } catch (error) {
        console.error('Error fetching election data:', error);
      }
    };

    fetchElectionData();
  }, [category, electionType]);

  const getOption = () => {
    return {
      title: {
        text: `${electionType} Emotion Distribution`,
        left: 'center',
        textStyle: {
          color: 'black'
        }
      },
      tooltip: {
        trigger: 'item'
      },
      series: [
        {
          name: 'Emotions',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            position: 'center',
            formatter: `{b}: {c}\nTotal: ${totalArticles}`,
            color: 'black',
            fontSize: 20
          },
          labelLine: {
            show: false
          },
          data: chartData,
          color: ['green', 'red', 'gray']
        }
      ]
    };
  };

  return (
    <div>
      <ReactECharts option={getOption()} style={{ height: '400px', width: '100%' }} />
    </div>
  );
};

export default ElectionEmotionsChart;
