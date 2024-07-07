import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const EmotionPieChart = ({ positive, negative, neutral }) => {
    const data = [
        { name: 'Positive', value: positive },
        { name: 'Negative', value: negative },
        { name: 'Neutral', value: neutral },
    ];

    const COLORS = ['#28a745', '#dc3545', '#6c757d']; // Green, Red, Gray

    return (
        <div className="emotion-pie-chart">
            <ResponsiveContainer width="100%" height={100}>
                <PieChart>
                    <Pie data={data} dataKey="value" outerRadius={40} fill="#8884d8">
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

export default EmotionPieChart;
