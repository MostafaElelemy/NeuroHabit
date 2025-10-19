/**
 * Pet component - Gamification element that responds to user progress.
 */
import React from 'react';

interface PetProps {
  level: number;
  happiness: number;
  experience: number;
}

const Pet: React.FC<PetProps> = ({ level, happiness, experience }) => {
  // Determine pet state based on happiness
  const getPetState = () => {
    if (happiness >= 80) return 'happy';
    if (happiness >= 50) return 'neutral';
    return 'sad';
  };

  const state = getPetState();

  // Calculate experience progress to next level
  const xpForNextLevel = level * 100;
  const xpProgress = (experience / xpForNextLevel) * 100;

  // Pet SVG based on state
  const renderPet = () => {
    const baseColor = state === 'happy' ? '#10B981' : state === 'neutral' ? '#F59E0B' : '#EF4444';
    const eyeExpression = state === 'happy' ? '^' : state === 'neutral' ? '•' : '•';
    const mouthPath = state === 'happy' 
      ? 'M 40 55 Q 50 65 60 55' 
      : state === 'neutral' 
      ? 'M 40 60 L 60 60' 
      : 'M 40 65 Q 50 55 60 65';

    return (
      <svg
        viewBox="0 0 100 100"
        className={`w-full h-full ${state === 'happy' ? 'animate-bounce-slow' : ''}`}
      >
        {/* Body */}
        <ellipse cx="50" cy="60" rx="30" ry="35" fill={baseColor} />
        
        {/* Head */}
        <circle cx="50" cy="35" r="25" fill={baseColor} />
        
        {/* Eyes */}
        <text x="40" y="35" fontSize="12" textAnchor="middle">{eyeExpression}</text>
        <text x="60" y="35" fontSize="12" textAnchor="middle">{eyeExpression}</text>
        
        {/* Mouth */}
        <path d={mouthPath} stroke="#000" strokeWidth="2" fill="none" />
        
        {/* Ears */}
        <ellipse cx="30" cy="20" rx="8" ry="12" fill={baseColor} />
        <ellipse cx="70" cy="20" rx="8" ry="12" fill={baseColor} />
        
        {/* Feet */}
        <ellipse cx="40" cy="90" rx="8" ry="6" fill={baseColor} />
        <ellipse cx="60" cy="90" rx="8" ry="6" fill={baseColor} />
        
        {/* Sparkles when happy */}
        {state === 'happy' && (
          <>
            <text x="20" y="30" fontSize="16">✨</text>
            <text x="75" y="30" fontSize="16">✨</text>
          </>
        )}
      </svg>
    );
  };

  return (
    <div className="card">
      <h3 className="text-xl font-bold mb-4 text-gray-800 dark:text-white">
        Your Habit Pet
      </h3>
      
      {/* Pet Display */}
      <div className="w-48 h-48 mx-auto mb-4">
        {renderPet()}
      </div>

      {/* Stats */}
      <div className="space-y-3">
        {/* Level */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="font-semibold text-gray-700 dark:text-gray-300">
              Level {level}
            </span>
            <span className="text-gray-600 dark:text-gray-400">
              {experience} / {xpForNextLevel} XP
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${xpProgress}%` }}
            />
          </div>
        </div>

        {/* Happiness */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="font-semibold text-gray-700 dark:text-gray-300">
              Happiness
            </span>
            <span className="text-gray-600 dark:text-gray-400">
              {happiness}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${
                happiness >= 80
                  ? 'bg-green-500'
                  : happiness >= 50
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${happiness}%` }}
            />
          </div>
        </div>
      </div>

      {/* Status Message */}
      <div className="mt-4 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
        <p className="text-sm text-center text-gray-700 dark:text-gray-300">
          {state === 'happy' && "Your pet is thriving! Keep up the great work! 🎉"}
          {state === 'neutral' && "Your pet is doing okay. Complete more habits to boost happiness! 😊"}
          {state === 'sad' && "Your pet needs attention! Complete some habits to cheer them up. 🥺"}
        </p>
      </div>
    </div>
  );
};

export default Pet;
