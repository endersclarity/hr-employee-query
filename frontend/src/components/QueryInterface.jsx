import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

export default function QueryInterface({ onSubmit, isLoading, onTimeout, error: serverError, results }) {
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

  const handleKeyDown = (e) => {
    // Submit on Enter (but allow Shift+Enter for line breaks)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
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
    <div className="w-full space-y-3">
      <form onSubmit={handleSubmit} className="w-full bg-zinc-900 border-2 border-zinc-700 rounded-lg p-4">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g., Show me employees in Engineering with salary > 120K"
          className="w-full p-3 bg-zinc-950 border-2 border-zinc-700 text-white placeholder-zinc-500 rounded-lg resize-none focus:border-blue-500 focus:outline-none transition-colors"
          rows={3}
          maxLength={500}
          disabled={isLoading}
          aria-label="Natural language query input"
          aria-describedby="char-counter"
        />
        <div className="flex justify-between items-center mt-3">
          <span id="char-counter" className="text-xs text-zinc-500">{query.length}/500</span>
          <button
            type="submit"
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 border-2 border-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:bg-zinc-700 disabled:border-zinc-600 disabled:cursor-not-allowed transition-all"
          >
            {isLoading ? 'Processing...' : 'Submit Query'}
          </button>
        </div>
        {(error || serverError) && (
          <div className="mt-3 flex items-start gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg p-3 animate-shake" role="alert" aria-live="assertive">
            <span className="text-base">⚠️</span>
            <span><strong>Error:</strong> {error || serverError}</span>
          </div>
        )}
      </form>

      {!isLoading && !error && !serverError && results.length === 0 && (
        <div className="text-center text-zinc-500 text-xs space-y-1">
          <p>Try asking:</p>
          <div className="flex flex-wrap justify-center gap-2">
            <button
              onClick={() => setQuery("Show me all employees in Engineering")}
              className="px-3 py-1 bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700 rounded-md text-zinc-400 hover:text-zinc-300 transition-colors"
            >
              Employees in Engineering
            </button>
            <button
              onClick={() => setQuery("Who earns more than 100K?")}
              className="px-3 py-1 bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700 rounded-md text-zinc-400 hover:text-zinc-300 transition-colors"
            >
              High earners
            </button>
            <button
              onClick={() => setQuery("List all departments")}
              className="px-3 py-1 bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700 rounded-md text-zinc-400 hover:text-zinc-300 transition-colors"
            >
              All departments
            </button>
          </div>
          <p className="text-zinc-600 mt-2">Press Enter to submit • Shift+Enter for new line</p>
        </div>
      )}
    </div>
  );
}

QueryInterface.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  onTimeout: PropTypes.func,
  error: PropTypes.string,
  results: PropTypes.array.isRequired,
};
