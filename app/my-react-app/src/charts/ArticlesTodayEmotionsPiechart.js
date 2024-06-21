import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactEcharts from 'echarts-for-react';

function ArticlesTodayEmotionsPiechart() {
  const [emotionsData, setEmotionsData] = useState([]);

  useEffect(() => {
    const fetchEmotionsData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/articles/today');
        const articles = response.data.articles;

        const emotionsCount = articles.reduce((acc, article) => {
          acc[article.emotion] = (acc[article.emotion] || 0) + 1;
          return acc;
        }, {});

        const totalEmotions = Object.values(emotionsCount).reduce((acc, count) => acc + count, 0);

        const colors = ['#18b52a', '#ff1100', '#597499' ];
        const emotionsWithPercentages = Object.keys(emotionsCount).map((emotion, index) => ({
          name: emotion,
          value: emotionsCount[emotion],
          itemStyle: { color: colors[index] },
        }));

        setEmotionsData(emotionsWithPercentages);
      } catch (error) {
        console.error('Error fetching emotions data:', error);
      }
    };

    fetchEmotionsData();
  }, []);

  const getOption = () => ({
    title: {
      text: 'Emoțiile din articolele de astăzi',
      left: 'center',
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b} : {c} ({d}%)',
    },
    series: [
      {
        name: 'Emotions',
        type: 'pie',
        radius: '50%',
        center: ['50%', '50%'],
        data: emotionsData,
        label: {
          formatter: '{b}: {d}%',
        },
      },
    ],
  });

  return (
    <div style={{ textAlign: 'center' }}>
      <ReactEcharts option={getOption()} style={{ height: 450, width: 450 }} />
    </div>
  );
}

export default ArticlesTodayEmotionsPiechart;
