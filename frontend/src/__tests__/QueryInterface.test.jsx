import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import QueryInterface from '../components/QueryInterface';

describe('QueryInterface', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  test('renders with placeholder text', () => {
    render(<QueryInterface onSubmit={mockOnSubmit} isLoading={false} />);
    expect(screen.getByPlaceholderText(/Enter your query/i)).toBeInTheDocument();
  });

  test('displays character counter', () => {
    render(<QueryInterface onSubmit={mockOnSubmit} isLoading={false} />);
    expect(screen.getByText('0/500')).toBeInTheDocument();
  });

  test('updates character counter on input', async () => {
    const user = userEvent.setup();
    render(<QueryInterface onSubmit={mockOnSubmit} isLoading={false} />);

    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    await user.type(textarea, 'Test query');

    expect(screen.getByText('10/500')).toBeInTheDocument();
  });

  test('shows error for empty query submission', async () => {
    const user = userEvent.setup();
    render(<QueryInterface onSubmit={mockOnSubmit} isLoading={false} />);

    const button = screen.getByRole('button', { name: /Submit Query/i });
    await user.click(button);

    expect(screen.getByText('Query cannot be empty')).toBeInTheDocument();
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  test('shows error for query exceeding 500 characters', async () => {
    const user = userEvent.setup();
    render(<QueryInterface onSubmit={mockOnSubmit} isLoading={false} />);

    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    const longQuery = 'a'.repeat(501);

    // Note: maxLength attribute prevents typing beyond 500, so we test validation logic directly
    fireEvent.change(textarea, { target: { value: longQuery } });

    const button = screen.getByRole('button', { name: /Submit Query/i });
    await user.click(button);

    expect(screen.getByText('Query too long (max 500 characters)')).toBeInTheDocument();
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  test('submits valid query', async () => {
    const user = userEvent.setup();
    render(<QueryInterface onSubmit={mockOnSubmit} isLoading={false} />);

    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    await user.type(textarea, 'Valid test query');

    const button = screen.getByRole('button', { name: /Submit Query/i });
    await user.click(button);

    expect(mockOnSubmit).toHaveBeenCalledWith('Valid test query');
  });

  test('clears error message on valid submission', async () => {
    const user = userEvent.setup();
    render(<QueryInterface onSubmit={mockOnSubmit} isLoading={false} />);

    // First, trigger an error
    const button = screen.getByRole('button', { name: /Submit Query/i });
    await user.click(button);
    expect(screen.getByText('Query cannot be empty')).toBeInTheDocument();

    // Then type valid input and submit
    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    await user.type(textarea, 'Valid query');
    await user.click(button);

    expect(screen.queryByText('Query cannot be empty')).not.toBeInTheDocument();
  });

  test('disables input and button when loading', () => {
    render(<QueryInterface onSubmit={mockOnSubmit} isLoading={true} />);

    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    const button = screen.getByRole('button');

    expect(textarea).toBeDisabled();
    expect(button).toBeDisabled();
  });

  test('changes button text when loading', () => {
    const { rerender } = render(<QueryInterface onSubmit={mockOnSubmit} isLoading={false} />);
    expect(screen.getByText('Submit Query')).toBeInTheDocument();

    rerender(<QueryInterface onSubmit={mockOnSubmit} isLoading={true} />);
    expect(screen.getByText('Processing...')).toBeInTheDocument();
  });

  test('shows timeout error after 10 seconds', async () => {
    jest.useFakeTimers();
    render(<QueryInterface onSubmit={mockOnSubmit} isLoading={true} />);

    // Fast-forward time by 10 seconds
    act(() => {
      jest.advanceTimersByTime(10000);
    });

    await waitFor(() => {
      expect(screen.getByText('Request timed out. Please try again.')).toBeInTheDocument();
    });

    jest.useRealTimers();
  });

  test('cleans up timeout on unmount', () => {
    jest.useFakeTimers();
    const { unmount } = render(<QueryInterface onSubmit={mockOnSubmit} isLoading={true} />);

    unmount();

    // If cleanup works properly, this shouldn't cause issues
    jest.advanceTimersByTime(10000);

    jest.useRealTimers();
  });

  test('respects maxLength attribute', () => {
    render(<QueryInterface onSubmit={mockOnSubmit} isLoading={false} />);
    const textarea = screen.getByPlaceholderText(/Enter your query/i);

    expect(textarea).toHaveAttribute('maxLength', '500');
  });
});
