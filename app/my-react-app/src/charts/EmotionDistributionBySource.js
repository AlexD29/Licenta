import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import ReactEcharts from 'echarts-for-react';
import { useNavigate } from 'react-router-dom';

function SimpleEmotionChart() {
  const [chartData, setChartData] = useState({
    sources: [],
    series: [],
    images: {},
    ids: {}
  });
  const [imagesLoaded, setImagesLoaded] = useState(false);
  const navigate = useNavigate();

  const colors = ['#18b52a', '#ff1100', '#597499' ];

  const fetchData = useCallback(async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/articles/emotion-distribution');
      console.log('Fetched data:', response.data);
      const processedData = processData(response.data);
      setChartData(processedData);
      preloadImages(processedData.images);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const processData = (data) => {
    const sources = Object.keys(data);
    const images = {};
    const ids = {};
    const emotions = ['positive', 'negative', 'neutral'];
    const series = emotions.map((emotion, index) => ({
      name: emotion,
      type: 'bar',
      stack: 'emotions',
      data: sources.map((source) => data[source][emotion] || 0),
      itemStyle: { color: colors[index] }
    }));

    sources.forEach((source) => {
      images[source] = data[source].image_url;
      ids[source] = data[source].id;
    });

    console.log('Processed data:', { sources, series, images, ids });
    return {
      sources,
      series,
      images,
      ids
    };
  };

  const preloadImages = (images) => {
    const promises = Object.values(images).map((url) => {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.src = url;
        img.onload = () => resolve(url);
        img.onerror = () => reject(url); // Log error on image load failure
      });
    });

    Promise.all(promises)
      .then(() => {
        console.log('All images preloaded successfully');
        setImagesLoaded(true);
      })
      .catch((failedUrl) => {
        console.error(`Failed to load image: ${failedUrl}`);
        setImagesLoaded(true); // Continue even if some images fail to load
      });
  };

  const handleChartClick = (params) => {
    const sourceId = chartData.ids[params.name];
    if (sourceId) {
      navigate(`/source/${sourceId}`);
    }
  };

  const getOption = () => ({
    title: {
      text: 'Emotion Distribution per Source',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    legend: {
      top: 'bottom',
    },
    xAxis: {
      type: 'value',
    },
    yAxis: {
      type: 'category',
      data: chartData.sources,
      axisLabel: {
        formatter: (value) => {
          console.log(`Formatting label for source: ${value}`);
          if (chartData.images[value]) {
            console.log(`Image URL for ${value}: ${chartData.images[value]}`);
          } else {
            console.log(`No image found for ${value}`);
          }
          return chartData.images[value] ? `{${value}|}` : value;
        },
        rich: chartData.sources.reduce((acc, source) => {
          acc[source] = {
            height: 20,
            width: 20,
            align: 'center',
            backgroundColor: {
              image: chartData.images[source],
            },
          };
          return acc;
        }, {}),
      },
    },
    series: chartData.series,
  });

  const onEvents = {
    click: handleChartClick,
  };

  return (
    <div style={{ textAlign: 'center' }}>
      {imagesLoaded ? (
        <ReactEcharts
          option={getOption()}
          onEvents={onEvents}
          style={{ height: 400, width: '100%' }}
        />
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default SimpleEmotionChart;
