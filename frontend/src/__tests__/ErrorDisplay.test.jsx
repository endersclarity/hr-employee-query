import { render, screen } from '@testing-library/react';
import ErrorDisplay from '../components/ErrorDisplay';

describe('ErrorDisplay', () => {
  test('renders nothing when error is null', () => {
    const { container } = render(<ErrorDisplay error={null} />);
    expect(container.firstChild).toBeNull();
  });

  test('renders nothing when error is undefined', () => {
    const { container } = render(<ErrorDisplay error={undefined} />);
    expect(container.firstChild).toBeNull();
  });

  test('renders nothing when error is empty string', () => {
    const { container } = render(<ErrorDisplay error="" />);
    expect(container.firstChild).toBeNull();
  });

  test('renders error message when provided', () => {
    render(<ErrorDisplay error="An error occurred" />);
    expect(screen.getByText(/An error occurred/i)).toBeInTheDocument();
  });

  test('displays "Error:" label', () => {
    render(<ErrorDisplay error="Test error" />);
    expect(screen.getByText('Error:')).toBeInTheDocument();
  });

  test('applies correct styling classes', () => {
    const { container } = render(<ErrorDisplay error="Test error" />);
    const errorDiv = container.firstChild;

    expect(errorDiv).toHaveClass('bg-zinc-900');
    expect(errorDiv).toHaveClass('border-2');
    expect(errorDiv).toHaveClass('border-red-500/30');
    expect(errorDiv).toHaveClass('text-red-400');
    expect(errorDiv).toHaveClass('px-4');
    expect(errorDiv).toHaveClass('py-3');
    expect(errorDiv).toHaveClass('rounded-lg');
  });

  test('renders long error messages correctly', () => {
    const longError = 'This is a very long error message that contains multiple sentences and detailed information about what went wrong during the query execution process.';
    render(<ErrorDisplay error={longError} />);

    expect(screen.getByText(new RegExp(longError))).toBeInTheDocument();
  });

  test('handles special characters in error message', () => {
    const errorWithSpecialChars = 'Error: Query failed with status code 500 & message: "Internal Server Error"';
    render(<ErrorDisplay error={errorWithSpecialChars} />);

    expect(screen.getByText(new RegExp(errorWithSpecialChars))).toBeInTheDocument();
  });

  test('renders multiple errors if called multiple times', () => {
    const { rerender } = render(<ErrorDisplay error="First error" />);
    expect(screen.getByText(/First error/i)).toBeInTheDocument();

    rerender(<ErrorDisplay error="Second error" />);
    expect(screen.getByText(/Second error/i)).toBeInTheDocument();
    expect(screen.queryByText(/First error/i)).not.toBeInTheDocument();
  });
});
