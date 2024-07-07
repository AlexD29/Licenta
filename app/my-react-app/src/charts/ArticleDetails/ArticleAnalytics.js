import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';

const ArticleAnalytics = ({ articleId, emotion }) => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [emotionCounts, setEmotionCounts] = useState({
    Positive: 0,
    Negative: 0,
    Neutral: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Set default dates to the last 7 days
    const end = new Date();
    const start = new Date();
    start.setDate(end.getDate() - 7);

    setEndDate(end.toISOString().split('T')[0]);
    setStartDate(start.toISOString().split('T')[0]);
  }, []);

  useEffect(() => {
    if (startDate && endDate) {
      fetchAnalytics();
    }
  }, [startDate, endDate]);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`http://localhost:8000/api/article-analytics/${articleId}`, {
        params: { start: startDate, end: endDate },
      });
      
      // Add the current article's emotion to the fetched emotion counts
      const updatedEmotionCounts = { ...response.data.emotion_counts };
      if (emotion in updatedEmotionCounts) {
        updatedEmotionCounts[emotion] += 1;
      } else {
        updatedEmotionCounts[emotion] = 1;
      }

      setEmotionCounts(updatedEmotionCounts);
    } catch (err) {
      setError('Failed to fetch article analytics');
    } finally {
      setLoading(false);
    }
  };

  const getChartOptions = () => ({
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        name: 'Article Emotions',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '70%'], // Center the pie chart
        startAngle: 180,
        endAngle: 360,
        label: {
          color: 'black', // Font color of labels
        },
        data: [
          { value: emotionCounts.Positive, name: 'Positive', itemStyle: { color: 'green' } },
          { value: emotionCounts.Negative, name: 'Negative', itemStyle: { color: 'red' } },
          { value: emotionCounts.Neutral, name: 'Neutral', itemStyle: { color: 'gray' } }
        ]
      }
    ],
    title: {
      text: 'Emoțiile despre acest subiect\nîn ultima săptămână', // Title of the chart
      left: 'center', // Center-align the title
      textStyle: {
        color: 'black', // Font color of the title
        fontSize: 20, // Font size of the title
        fontWeight: 'bold', // Bold style for the title,
        lineHeight: 25
      }
    }
  });

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-animation"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="article-analytics">
      {error && <p>{error}</p>}
      {!loading && !error && (
        <ReactECharts option={getChartOptions()} />
      )}
    </div>
  );
};

export default ArticleAnalytics;
