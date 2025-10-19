/**
 * HabitGraph component - Visualizes habit completion data using Recharts.
 */
import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface HabitGraphProps {
  data: Array<{
    date: string;
    completions: number;
    target?: number;
  }>;
  type?: 'line' | 'bar';
  title?: string;
}

const HabitGraph: React.FC<HabitGraphProps> = ({ 
  data, 
  type = 'line',
  title = 'Habit Completion Trend'
}) => {
  // Generate sample data if none provided
  const chartData = data.length > 0 ? data : generateSampleData();

  return (
    <div className="card">
      <h3 className="text-xl font-bold mb-4 text-gray-800 dark:text-white">
        {title}
      </h3>
      
      <ResponsiveContainer width="100%" height={300}>
        {type === 'line' ? (
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9CA3AF"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#9CA3AF"
              style={{ fontSize: '12px' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: 'none',
                borderRadius: '8px',
                color: '#F3F4F6',
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="completions"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={{ fill: '#3B82F6', r: 4 }}
              activeDot={{ r: 6 }}
              name="Completions"
            />
            {chartData[0]?.target !== undefined && (
              <Line
                type="monotone"
                dataKey="target"
                stroke="#10B981"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Target"
              />
            )}
          </LineChart>
        ) : (
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9CA3AF"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#9CA3AF"
              style={{ fontSize: '12px' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: 'none',
                borderRadius: '8px',
                color: '#F3F4F6',
              }}
            />
            <Legend />
            <Bar 
              dataKey="completions" 
              fill="#3B82F6" 
              radius={[8, 8, 0, 0]}
              name="Completions"
            />
          </BarChart>
        )}
      </ResponsiveContainer>

      {/* Stats Summary */}
      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="text-center">
          <p className="text-2xl font-bold text-primary-600">
            {calculateTotal(chartData)}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Total Completions
          </p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-green-600">
            {calculateAverage(chartData).toFixed(1)}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Daily Average
          </p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-purple-600">
            {calculateStreak(chartData)}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Current Streak
          </p>
        </div>
      </div>
    </div>
  );
};

// Helper functions
function generateSampleData() {
  const data = [];
  const today = new Date();
  
  for (let i = 13; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    data.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      completions: Math.floor(Math.random() * 8) + 2,
      target: 7,
    });
  }
  
  return data;
}

function calculateTotal(data: Array<{ completions: number }>) {
  return data.reduce((sum, item) => sum + item.completions, 0);
}

function calculateAverage(data: Array<{ completions: number }>) {
  if (data.length === 0) return 0;
  return calculateTotal(data) / data.length;
}

function calculateStreak(data: Array<{ completions: number }>) {
  let streak = 0;
  
  // Count from the end (most recent) backwards
  for (let i = data.length - 1; i >= 0; i--) {
    if (data[i].completions > 0) {
      streak++;
    } else {
      break;
    }
  }
  
  return streak;
}

export default HabitGraph;
