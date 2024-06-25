import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import * as echarts from 'echarts';
import RomaniaGeoJSON from './romania.geojson'; // Adjust the path based on your project structure

const RomaniaMap = () => {
  const [mapDataLoaded, setMapDataLoaded] = useState(false);

  useEffect(() => {
    // Register the map with ECharts when component mounts
    echarts.registerMap('Romania', RomaniaGeoJSON);
    setMapDataLoaded(true);
  }, []);

  const getOption = () => ({
    geo: {
      map: 'Romania',
      roam: true,
      itemStyle: {
        areaColor: '#f3f3f3',
        borderColor: '#999',
      },
      emphasis: {
        itemStyle: {
          areaColor: '#ddd',
        },
      },
    },
    series: [
      {
        type: 'effectScatter',
        coordinateSystem: 'geo',
        symbolSize: 10,
        rippleEffect: {
          brushType: 'stroke',
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
        },
        itemStyle: {
          color: '#FF0000',
        },
        data: RomaniaGeoJSON.features.map(feature => ({
          name: feature.properties.name,
          value: feature.geometry.coordinates,
        })),
      },
    ],
  });

  if (!mapDataLoaded) {
    return <div>Loading...</div>;
  }

  return (
    <ReactECharts
      option={getOption()}
      style={{ height: '100vh', width: '100%' }}
    />
  );
};

export default RomaniaMap;
