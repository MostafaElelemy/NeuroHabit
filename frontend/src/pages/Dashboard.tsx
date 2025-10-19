/**
 * Dashboard page - Main view showing habits, stats, and pet.
 */
import React, { useEffect, useState } from 'react';
import { dashboardAPI, habitAPI, Habit, DashboardData } from '../services/api';
import HabitCard from '../components/HabitCard';
import HabitGraph from '../components/HabitGraph';
import Pet from '../components/Pet';

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getDashboard();
      setDashboardData(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteHabit = async (habitId: number) => {
    try {
      await habitAPI.createHabitEvent(habitId, {
        mood: 4,
        energy_level: 4,
      });
      
      // Reload dashboard to update stats
      await loadDashboard();
      
      // Show success message
      alert('Habit completed! 🎉');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to complete habit');
    }
  };

  const handleDeleteHabit = async (habitId: number) => {
    if (!confirm('Are you sure you want to delete this habit?')) {
      return;
    }

    try {
      await habitAPI.deleteHabit(habitId);
      await loadDashboard();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete habit');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="card max-w-md">
          <h2 className="text-xl font-bold text-red-600 mb-2">Error</h2>
          <p className="text-gray-700 dark:text-gray-300">{error}</p>
          <button onClick={loadDashboard} className="btn-primary mt-4">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return null;
  }

  const { user, habits, stats } = dashboardData;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                NeuroHabit
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Welcome back, {user.full_name || user.email}!
              </p>
            </div>
            <button
              onClick={() => {
                localStorage.removeItem('token');
                window.location.href = '/login';
              }}
              className="btn-secondary"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
              Total Habits
            </p>
            <p className="text-3xl font-bold text-primary-600">
              {stats.total_habits}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
              Active Habits
            </p>
            <p className="text-3xl font-bold text-green-600">
              {stats.active_habits}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
              Completion Rate
            </p>
            <p className="text-3xl font-bold text-purple-600">
              {stats.completion_rate.toFixed(0)}%
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
              Avg Streak
            </p>
            <p className="text-3xl font-bold text-orange-600">
              {stats.average_streak.toFixed(1)}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Graph */}
            <HabitGraph data={[]} />

            {/* Habits List */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Your Habits
                </h2>
                <button className="btn-primary">
                  + New Habit
                </button>
              </div>

              {habits.length === 0 ? (
                <div className="card text-center py-12">
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    No habits yet. Create your first habit to get started!
                  </p>
                  <button className="btn-primary">
                    Create Habit
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {habits.map((habit) => (
                    <HabitCard
                      key={habit.id}
                      habit={habit}
                      onComplete={handleCompleteHabit}
                      onDelete={handleDeleteHabit}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Pet */}
            <Pet
              level={user.pet_level}
              happiness={user.pet_happiness}
              experience={user.pet_experience}
            />

            {/* Quick Stats */}
            <div className="card">
              <h3 className="text-xl font-bold mb-4 text-gray-800 dark:text-white">
                Quick Stats
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Total Completions
                  </span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {stats.total_completions}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Member Since
                  </span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {new Date(user.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Account Type
                  </span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {user.is_premium ? '⭐ Premium' : 'Free'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
