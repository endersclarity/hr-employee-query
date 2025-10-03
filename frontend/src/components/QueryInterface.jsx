import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

export default function QueryInterface({ onSubmit, isLoading, onTimeout }) {
  const [query, setQuery] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    // Client-side validation (AC5)
    if (query.length < 1) {
      setError('Query cannot be empty');
      return;
    }
    if (query.length > 500) {
      setError('Query too long (max 500 characters)');
      return;
    }

    onSubmit(query);
  };

  // Loading state timeout (AC6) - 10 seconds
  useEffect(() => {
    if (isLoading) {
      const timeout = setTimeout(() => {
        setError('Request timed out. Please try again.');
        if (onTimeout) {
          onTimeout();
        }
      }, 10000);
      return () => clearTimeout(timeout);
    }
  }, [isLoading, onTimeout]);

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl">
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter your query (e.g., 'Show me employees in Engineering with salary > 120K')"
        className="w-full p-4 border rounded-lg"
        rows={3}
        maxLength={500}
        disabled={isLoading}
        aria-label="Natural language query input"
        aria-describedby="char-counter"
      />
      <div className="flex justify-between items-center mt-2">
        {/* Character counter (Subtask 1.2) */}
        <span id="char-counter" className="text-sm text-gray-600">{query.length}/500</span>
        {error && <span className="text-sm text-red-600" role="alert" aria-live="assertive">{error}</span>}
      </div>
      <button
        type="submit"
        disabled={isLoading}
        className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
      >
        {isLoading ? 'Processing...' : 'Submit Query'}
      </button>
    </form>
  );
}

QueryInterface.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  onTimeout: PropTypes.func,
};
