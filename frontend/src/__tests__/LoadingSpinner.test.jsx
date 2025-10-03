import { render, screen } from '@testing-library/react';
import LoadingSpinner from '../components/LoadingSpinner';

describe('LoadingSpinner', () => {
  test('renders loading spinner', () => {
    const { container } = render(<LoadingSpinner />);
    const spinner = container.querySelector('.animate-spin');

    expect(spinner).toBeInTheDocument();
  });

  test('displays loading text', () => {
    render(<LoadingSpinner />);
    expect(screen.getByText('Processing query...')).toBeInTheDocument();
  });

  test('applies correct styling classes to container', () => {
    const { container } = render(<LoadingSpinner />);
    const spinnerContainer = container.firstChild;

    expect(spinnerContainer).toHaveClass('flex');
    expect(spinnerContainer).toHaveClass('justify-center');
    expect(spinnerContainer).toHaveClass('items-center');
    expect(spinnerContainer).toHaveClass('py-8');
  });

  test('applies correct styling to spinner element', () => {
    const { container } = render(<LoadingSpinner />);
    const spinner = container.querySelector('.animate-spin');

    expect(spinner).toHaveClass('rounded-full');
    expect(spinner).toHaveClass('h-12');
    expect(spinner).toHaveClass('w-12');
    expect(spinner).toHaveClass('border-b-2');
    expect(spinner).toHaveClass('border-blue-600');
  });

  test('renders text with correct styling', () => {
    const { container } = render(<LoadingSpinner />);
    const text = screen.getByText('Processing query...');

    expect(text).toHaveClass('ml-3');
    expect(text).toHaveClass('text-gray-600');
  });

  test('renders spinner and text as siblings', () => {
    const { container } = render(<LoadingSpinner />);
    const spinnerContainer = container.firstChild;

    expect(spinnerContainer.children).toHaveLength(2);
  });
});
