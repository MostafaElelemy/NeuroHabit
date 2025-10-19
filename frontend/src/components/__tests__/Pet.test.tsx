/**
 * Unit tests for Pet component.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Pet from '../Pet';

describe('Pet Component', () => {
  it('renders pet with correct level', () => {
    render(<Pet level={5} happiness={80} experience={250} />);
    
    expect(screen.getByText(/Level 5/i)).toBeDefined();
  });

  it('displays happiness percentage', () => {
    render(<Pet level={3} happiness={75} experience={150} />);
    
    expect(screen.getByText(/75%/i)).toBeDefined();
  });

  it('shows happy message when happiness is high', () => {
    render(<Pet level={5} happiness={85} experience={250} />);
    
    expect(screen.getByText(/thriving/i)).toBeDefined();
  });

  it('shows neutral message when happiness is medium', () => {
    render(<Pet level={3} happiness={60} experience={150} />);
    
    expect(screen.getByText(/doing okay/i)).toBeDefined();
  });

  it('shows sad message when happiness is low', () => {
    render(<Pet level={2} happiness={30} experience={50} />);
    
    expect(screen.getByText(/needs attention/i)).toBeDefined();
  });

  it('calculates experience progress correctly', () => {
    const level = 5;
    const experience = 250;
    const xpForNextLevel = level * 100; // 500
    const expectedProgress = (experience / xpForNextLevel) * 100; // 50%
    
    render(<Pet level={level} happiness={70} experience={experience} />);
    
    expect(screen.getByText(`${experience} / ${xpForNextLevel} XP`)).toBeDefined();
  });

  it('renders title correctly', () => {
    render(<Pet level={1} happiness={50} experience={0} />);
    
    expect(screen.getByText('Your Habit Pet')).toBeDefined();
  });
});
