import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';

const ElectionChartComponent = () => {
    const [chartData, setChartData] = useState({ xAxisData: [], series: [] });

    useEffect(() => {
        const fetchElectionData = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/election-articles-distribution');
                const data = response.data.election_distribution;

                const dates = new Set();
                const seriesData = {};

                // Process the data to get dates and series for each election type
                for (const [electionType, records] of Object.entries(data)) {
                    seriesData[electionType] = [];
                    for (const [date, total_articles] of Object.entries(records)) {
                        dates.add(date);
                        seriesData[electionType].push({ date, total_articles });
                    }
                }

                const sortedDates = Array.from(dates).sort();
                const series = Object.keys(seriesData).map(electionType => {
                    // Extract the second word from the election type
                    const secondWord = electionType.split(' ')[1] || electionType;

                    return {
                        name: secondWord,
                        type: 'line',
                        stack: 'Total',
                        data: sortedDates.map(date => {
                            const record = seriesData[electionType].find(r => r.date === date);
                            return record ? record.total_articles : 0;
                        })
                    };
                });

                setChartData({
                    xAxisData: sortedDates,
                    series: series
                });
            } catch (error) {
                console.error('Error fetching election data:', error);
            }
        };

        fetchElectionData();
    }, []);

    const getOption = () => {
        return {
            title: {
                text: 'Distribuția articolelor electorale\ndin ultima săptămână',
                left: 'center',
                textStyle: {
                    color: 'black'
                }
            },
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                data: chartData.series.map(serie => serie.name),
                bottom: 0, // Move the legend to the bottom
                textStyle: {
                    color: 'black' // Set legend text color to black
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '10%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: chartData.xAxisData,
                axisLabel: {
                    color: 'black' // Set xAxis label text color to black
                }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    color: 'black' // Set yAxis label text color to black
                }
            },
            series: chartData.series.map(serie => ({
                ...serie,
            }))
        };
    };

    return (
        <div>
            <ReactECharts option={getOption()} style={{ height: '400px', width: '100%' }} />
        </div>
    );
};

export default ElectionChartComponent;
