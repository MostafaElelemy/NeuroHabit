/**
 * HabitCard component - Displays individual habit information.
 */
import React from 'react';
import { Habit } from '../services/api';

interface HabitCardProps {
  habit: Habit;
  onComplete: (habitId: number) => void;
  onEdit?: (habit: Habit) => void;
  onDelete?: (habitId: number) => void;
}

const HabitCard: React.FC<HabitCardProps> = ({
  habit,
  onComplete,
  onEdit,
  onDelete,
}) => {
  return (
    <div
      className="card hover:shadow-lg transition-shadow duration-200"
      style={{ borderLeft: `4px solid ${habit.color}` }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{habit.icon}</span>
          <div>
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
              {habit.title}
            </h3>
            {habit.description && (
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {habit.description}
              </p>
            )}
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex gap-2">
          {onEdit && (
            <button
              onClick={() => onEdit(habit)}
              className="text-gray-500 hover:text-primary-600 transition-colors"
              title="Edit habit"
            >
              ✏️
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(habit.id)}
              className="text-gray-500 hover:text-red-600 transition-colors"
              title="Delete habit"
            >
              🗑️
            </button>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Current Streak
          </p>
          <p className="text-2xl font-bold text-primary-600">
            {habit.current_streak} 🔥
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Best Streak
          </p>
          <p className="text-2xl font-bold text-purple-600">
            {habit.longest_streak} 🏆
          </p>
        </div>
      </div>

      {/* Difficulty & Importance */}
      <div className="flex gap-4 mb-4">
        <div className="flex-1">
          <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
            Difficulty
          </p>
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((level) => (
              <div
                key={level}
                className={`h-2 flex-1 rounded ${
                  level <= habit.difficulty_rating
                    ? 'bg-orange-500'
                    : 'bg-gray-300 dark:bg-gray-600'
                }`}
              />
            ))}
          </div>
        </div>
        <div className="flex-1">
          <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
            Importance
          </p>
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((level) => (
              <div
                key={level}
                className={`h-2 flex-1 rounded ${
                  level <= habit.importance_rating
                    ? 'bg-green-500'
                    : 'bg-gray-300 dark:bg-gray-600'
                }`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Complete Button */}
      <button
        onClick={() => onComplete(habit.id)}
        className="w-full btn-primary"
        disabled={!habit.is_active}
      >
        ✓ Complete Today
      </button>

      {/* Category Badge */}
      {habit.category && (
        <div className="mt-3">
          <span className="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
            {habit.category}
          </span>
        </div>
      )}
    </div>
  );
};

export default HabitCard;
