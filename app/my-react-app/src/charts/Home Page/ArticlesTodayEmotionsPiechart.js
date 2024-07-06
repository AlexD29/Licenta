import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactEcharts from 'echarts-for-react';

function ArticlesTodayEmotionsPiechart() {
  const [emotionsData, setEmotionsData] = useState([]);
  const [totalArticles, setTotalArticles] = useState(0);

  useEffect(() => {
    const fetchEmotionsData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/articles/today');
        const { total_articles, positive_articles, negative_articles, neutral_articles } = response.data;

        setTotalArticles(total_articles);

        const emotionsCount = {
          Pozitive: positive_articles,
          Negative: negative_articles,
          Neutre: neutral_articles
        };

        const colors = ['#18b52a', '#ff1100', '#597499'];
        const emotionsWithPercentages = Object.keys(emotionsCount).map((emotion, index) => ({
          name: emotion,
          value: emotionsCount[emotion],
          itemStyle: { color: colors[index] }
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
      text: `${totalArticles} articole postate astăzi`,
      left: 'center',
      textStyle: {
        fontSize: 32, // Adjust this value to make the title bigger
        color: '#000' // Set the title text color to black
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b} : {c} ({d}%)',
      textStyle: {
        color: '#000' // Set the tooltip text color to black
      }
    },
    series: [
      {
        name: 'Emotions',
        type: 'pie',
        radius: '50%',
        center: ['50%', '50%'],
        data: emotionsData,
        label: {
          formatter: '{b}',
          textStyle: {
            color: '#000' // Set the series label text color to black
          }
        }
      }
    ],
    textStyle: {
      color: '#000' // Set the global text color to black as a fallback
    }
  });


  return (
    <div className='articles-today-chart' style={{ textAlign: 'center' }}>
      <ReactEcharts option={getOption()} style={{ height: 450, width: 450 }} />
    </div>
  );
}

export default ArticlesTodayEmotionsPiechart;
