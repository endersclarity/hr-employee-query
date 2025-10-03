import { useState } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import QueryInterface from './components/QueryInterface';
import ResultsTable from './components/ResultsTable';
import ErrorDisplay from './components/ErrorDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import RagasScoreDisplay from './components/RagasScoreDisplay';
import { submitQuery } from './services/api';

export default function App() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generatedSQL, setGeneratedSQL] = useState(null);
  const [showSQL, setShowSQL] = useState(false);
  const [ragasScores, setRagasScores] = useState(null);

  const handleQuerySubmit = async (query) => {
    setIsLoading(true);
    setError(null);
    setGeneratedSQL(null);
    setRagasScores(null);

    try {
      const data = await submitQuery(query);
      setResults(data.results || []);
      setGeneratedSQL(data.sql || null);
      setRagasScores(data.ragas_scores || null);
    } catch (err) {
      setError(err.message);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTimeout = () => {
    setIsLoading(false);
    setError('Request timed out. Please try again.');
  };

  return (
    <ErrorBoundary
      fallback={<div className="min-h-screen flex items-center justify-center bg-zinc-950">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-400 mb-4">Something went wrong</h1>
          <p className="text-zinc-400 mb-4">Please refresh the page to try again.</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Refresh Page
          </button>
        </div>
      </div>}
    >
      <div className="min-h-screen bg-zinc-950 flex flex-col items-center">
        <div className="w-full max-w-3xl px-4 py-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">
              HR Employee Query System
            </h1>
            <p className="text-zinc-400 text-sm">
              Ask questions about employees in natural language
            </p>
          </div>

          <QueryInterface
            onSubmit={handleQuerySubmit}
            isLoading={isLoading}
            onTimeout={handleTimeout}
            error={error}
            results={results}
          />

          <div className="mt-8">
            {isLoading && <LoadingSpinner />}
            {!isLoading && !error && results.length > 0 && (
              <>
                {generatedSQL && (
                  <div className="mb-4 bg-zinc-900 rounded-lg p-4">
                    <button
                      onClick={() => setShowSQL(!showSQL)}
                      className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                    >
                      {showSQL ? '▼' : '▶'} Generated SQL
                    </button>
                    {showSQL && (
                      <pre className="mt-2 text-sm text-emerald-400 font-mono overflow-x-auto">
                        {generatedSQL}
                      </pre>
                    )}
                  </div>
                )}
                <ResultsTable results={results} />
                <RagasScoreDisplay scores={ragasScores} />
              </>
            )}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
