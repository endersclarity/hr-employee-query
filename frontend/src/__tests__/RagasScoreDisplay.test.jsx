import { render, screen } from '@testing-library/react';
import RagasScoreDisplay from '../components/RagasScoreDisplay';

describe('RagasScoreDisplay', () => {
  test('returns null when scores is null', () => {
    const { container } = render(<RagasScoreDisplay scores={null} />);
    expect(container.firstChild).toBeNull();
  });

  test('returns null when scores is undefined', () => {
    const { container } = render(<RagasScoreDisplay scores={undefined} />);
    expect(container.firstChild).toBeNull();
  });

  test('renders all three scores correctly', () => {
    const mockScores = {
      faithfulness: 0.85,
      answer_relevance: 0.92,
      context_utilization: 0.78
    };

    render(<RagasScoreDisplay scores={mockScores} />);

    expect(screen.getByText(/0\.85/)).toBeInTheDocument();
    expect(screen.getByText(/0\.92/)).toBeInTheDocument();
    expect(screen.getByText(/0\.78/)).toBeInTheDocument();
  });

  test('applies green color for scores > 0.8', () => {
    const mockScores = {
      faithfulness: 0.85,
      answer_relevance: 0.92,
      context_utilization: 0.81
    };

    const { container } = render(<RagasScoreDisplay scores={mockScores} />);

    const badges = container.querySelectorAll('.text-green-400');
    expect(badges).toHaveLength(3); // All scores > 0.8
  });

  test('applies yellow color for scores between 0.7 and 0.8 (inclusive)', () => {
    const mockScores = {
      faithfulness: 0.75,
      answer_relevance: 0.7,
      context_utilization: 0.8
    };

    const { container } = render(<RagasScoreDisplay scores={mockScores} />);

    const yellowBadges = container.querySelectorAll('.text-yellow-400');
    expect(yellowBadges).toHaveLength(3); // All scores 0.7-0.8
  });

  test('applies red color for scores < 0.7', () => {
    const mockScores = {
      faithfulness: 0.65,
      answer_relevance: 0.55,
      context_utilization: 0.69
    };

    const { container } = render(<RagasScoreDisplay scores={mockScores} />);

    const redBadges = container.querySelectorAll('.text-red-400');
    expect(redBadges).toHaveLength(3); // All scores < 0.7
  });

  test('applies mixed colors for mixed score ranges', () => {
    const mockScores = {
      faithfulness: 0.85,  // green
      answer_relevance: 0.75,  // yellow
      context_utilization: 0.65  // red
    };

    const { container } = render(<RagasScoreDisplay scores={mockScores} />);

    expect(container.querySelectorAll('.text-green-400')).toHaveLength(1);
    expect(container.querySelectorAll('.text-yellow-400')).toHaveLength(1);
    expect(container.querySelectorAll('.text-red-400')).toHaveLength(1);
  });

  test('formats scores to 2 decimal places', () => {
    const mockScores = {
      faithfulness: 0.8567,
      answer_relevance: 0.9234,
      context_utilization: 0.7891
    };

    render(<RagasScoreDisplay scores={mockScores} />);

    expect(screen.getByText(/0\.86/)).toBeInTheDocument();
    expect(screen.getByText(/0\.92/)).toBeInTheDocument();
    expect(screen.getByText(/0\.79/)).toBeInTheDocument();
  });

  test('boundary test: score exactly 0.8 is yellow', () => {
    const mockScores = {
      faithfulness: 0.8,
      answer_relevance: 0.8,
      context_utilization: 0.8
    };

    const { container } = render(<RagasScoreDisplay scores={mockScores} />);

    const yellowBadges = container.querySelectorAll('.text-yellow-400');
    expect(yellowBadges).toHaveLength(3);
  });

  test('boundary test: score exactly 0.7 is yellow', () => {
    const mockScores = {
      faithfulness: 0.7,
      answer_relevance: 0.7,
      context_utilization: 0.7
    };

    const { container } = render(<RagasScoreDisplay scores={mockScores} />);

    const yellowBadges = container.querySelectorAll('.text-yellow-400');
    expect(yellowBadges).toHaveLength(3);
  });

  test('renders with correct CSS classes structure', () => {
    const mockScores = {
      faithfulness: 0.85,
      answer_relevance: 0.75,
      context_utilization: 0.65
    };

    const { container } = render(<RagasScoreDisplay scores={mockScores} />);

    const wrapper = container.querySelector('.mt-4.bg-zinc-900');
    expect(wrapper).toBeInTheDocument();

    const cards = container.querySelectorAll('.bg-zinc-950.border-2.border-zinc-800');
    expect(cards).toHaveLength(3);
  });
});
