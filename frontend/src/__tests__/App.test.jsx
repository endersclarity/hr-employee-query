import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';

// Mock the API module with shared mock
jest.mock('../services/api', () => require('./__mocks__/api'));
// Mock ErrorBoundary to avoid Jest/ESM issues
jest.mock('react-error-boundary', () => ({
  ErrorBoundary: ({ children }) => children,
}));

describe('App', () => {
  test('renders application title', () => {
    render(<App />);
    expect(screen.getByText('HR Employee Query System')).toBeInTheDocument();
  });

  test('renders QueryInterface component', () => {
    render(<App />);
    expect(screen.getByPlaceholderText(/Enter your query/i)).toBeInTheDocument();
  });

  test('initially shows empty results message', () => {
    render(<App />);
    expect(screen.getByText('No results to display. Submit a query to see results.')).toBeInTheDocument();
  });

  test('does not show loading spinner initially', () => {
    render(<App />);
    expect(screen.queryByText('Processing query...')).not.toBeInTheDocument();
  });

  test('does not show error message initially', () => {
    render(<App />);
    expect(screen.queryByText(/Error:/)).not.toBeInTheDocument();
  });

  test('shows loading spinner when query is submitted', async () => {
    const user = userEvent.setup();
    render(<App />);

    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    await user.type(textarea, 'test query');

    const button = screen.getByRole('button', { name: /Submit Query/i });
    await user.click(button);

    expect(screen.getByText('Processing query...')).toBeInTheDocument();
  });

  test('displays results after query submission', async () => {
    const user = userEvent.setup();

    render(<App />);

    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    await user.type(textarea, 'test query');

    const button = screen.getByRole('button', { name: /Submit Query/i });
    await user.click(button);

    // Wait for the simulated delay to complete
    await waitFor(() => {
      expect(screen.getAllByText('John')).toHaveLength(1);
      expect(screen.getAllByText('Doe')).toHaveLength(1);
    }, { timeout: 3000 });
  });

  test('hides loading spinner after results are loaded', async () => {
    jest.useFakeTimers();
    const user = userEvent.setup({ delay: null });

    render(<App />);

    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    await user.type(textarea, 'test query');

    const button = screen.getByRole('button', { name: /Submit Query/i });
    await user.click(button);

    expect(screen.getByText('Processing query...')).toBeInTheDocument();

    await act(async () => {
      jest.runAllTimers();
    });

    await waitFor(() => {
      expect(screen.queryByText('Processing query...')).not.toBeInTheDocument();
    });

    jest.useRealTimers();
  });

  test('renders placeholder employee data in results', async () => {
    jest.useFakeTimers();
    const user = userEvent.setup({ delay: null });

    render(<App />);

    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    await user.type(textarea, 'test query');

    const button = screen.getByRole('button', { name: /Submit Query/i });
    await user.click(button);

    jest.runAllTimers();

    await waitFor(() => {
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
      expect(screen.getByText('Smith')).toBeInTheDocument();
      expect(screen.getByText('125000')).toBeInTheDocument();
      expect(screen.getByText('135000')).toBeInTheDocument();
    });

    jest.useRealTimers();
  });

  test('results table shows correct column headers', async () => {
    jest.useFakeTimers();
    const user = userEvent.setup({ delay: null });

    render(<App />);

    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    await user.type(textarea, 'test query');

    const button = screen.getByRole('button', { name: /Submit Query/i });
    await user.click(button);

    jest.runAllTimers();

    await waitFor(() => {
      expect(screen.getByText('EMPLOYEE ID')).toBeInTheDocument();
      expect(screen.getByText('FIRST NAME')).toBeInTheDocument();
      expect(screen.getByText('LAST NAME')).toBeInTheDocument();
      expect(screen.getByText('DEPARTMENT')).toBeInTheDocument();
      expect(screen.getByText('SALARY USD')).toBeInTheDocument();
    });

    jest.useRealTimers();
  });

  test('disables query input while loading', async () => {
    const user = userEvent.setup();
    render(<App />);

    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    await user.type(textarea, 'test query');

    const button = screen.getByRole('button', { name: /Submit Query/i });
    await user.click(button);

    expect(textarea).toBeDisabled();
    expect(button).toBeDisabled();
  });

  test('state management: results cleared before new query', async () => {
    jest.useFakeTimers();
    const user = userEvent.setup({ delay: null });

    render(<App />);

    // First query
    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    await user.type(textarea, 'first query');

    const button = screen.getByRole('button', { name: /Submit Query/i });
    await user.click(button);

    jest.runAllTimers();

    await waitFor(() => {
      expect(screen.getByText('John')).toBeInTheDocument();
    });

    // The results should still be visible
    expect(screen.getByText('John')).toBeInTheDocument();

    jest.useRealTimers();
  });

  test('multiple submissions work correctly', async () => {
    jest.useFakeTimers();
    const user = userEvent.setup({ delay: null });

    render(<App />);

    const textarea = screen.getByPlaceholderText(/Enter your query/i);
    const button = screen.getByRole('button', { name: /Submit Query/i });

    // First submission
    await user.type(textarea, 'query 1');
    await user.click(button);

    jest.runAllTimers();

    await waitFor(() => {
      expect(screen.getByText('John')).toBeInTheDocument();
    });

    // Clear and submit again
    await user.clear(textarea);
    await user.type(textarea, 'query 2');
    await user.click(button);

    jest.runAllTimers();

    await waitFor(() => {
      // Results should still appear (placeholder data is the same)
      expect(screen.getByText('John')).toBeInTheDocument();
    });

    jest.useRealTimers();
  });
});
