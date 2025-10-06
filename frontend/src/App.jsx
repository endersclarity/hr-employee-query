import { useState, useEffect } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import QueryInterface from './components/QueryInterface';
import ResultsTable from './components/ResultsTable';
import ErrorDisplay from './components/ErrorDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import RagasScoreDisplay from './components/RagasScoreDisplay';
import RagasAnalysisDashboard from './components/RagasAnalysisDashboard';
import { submitQuery, fetchQueryStatus } from './services/api';

export default function App() {
  const [currentPage, setCurrentPage] = useState('query'); // 'query' or 'analysis'
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generatedSQL, setGeneratedSQL] = useState(null);
  const [showSQL, setShowSQL] = useState(false);
  const [ragasScores, setRagasScores] = useState(null);
  const [queryLogId, setQueryLogId] = useState(null);
  const [evaluationStatus, setEvaluationStatus] = useState(null);

  const handleQuerySubmit = async (query) => {
    setIsLoading(true);
    setError(null);
    setGeneratedSQL(null);
    setRagasScores(null);
    setQueryLogId(null);
    setEvaluationStatus(null);

    try {
      const data = await submitQuery(query);
      setResults(data.results || []);
      setGeneratedSQL(data.sql || null);
      setQueryLogId(data.query_log_id);
      setEvaluationStatus(data.evaluation_status);

      // If scores are already available, set them
      if (data.ragas_scores) {
        setRagasScores(data.ragas_scores);
      }
    } catch (err) {
      setError(err.message);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Poll for RAGAS scores after query submission
  useEffect(() => {
    if (!queryLogId || evaluationStatus === 'completed') return;

    const pollInterval = setInterval(async () => {
      try {
        const status = await fetchQueryStatus(queryLogId);
        setEvaluationStatus(status.evaluation_status);

        if (status.evaluation_status === 'completed' && status.ragas_scores) {
          setRagasScores(status.ragas_scores);
          clearInterval(pollInterval);
        } else if (status.evaluation_status === 'failed') {
          clearInterval(pollInterval);
        }
      } catch (err) {
        console.error('Failed to poll RAGAS scores:', err);
        clearInterval(pollInterval);
      }
    }, 2000); // Poll every 2 seconds

    // Stop polling after 2 minutes (RAGAS can take 60-90 seconds)
    const timeout = setTimeout(() => clearInterval(pollInterval), 120000);

    return () => {
      clearInterval(pollInterval);
      clearTimeout(timeout);
    };
  }, [queryLogId, evaluationStatus]);

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
        <div className="w-full max-w-6xl px-4 py-8">
          {/* Navigation */}
          <div className="flex justify-center mb-8">
            <div className="bg-zinc-900 rounded-lg p-1 inline-flex border border-zinc-800">
              <button
                onClick={() => setCurrentPage('query')}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  currentPage === 'query'
                    ? 'bg-blue-600 text-white'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                Query Interface
              </button>
              <button
                onClick={() => setCurrentPage('analysis')}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  currentPage === 'analysis'
                    ? 'bg-blue-600 text-white'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                RAGAS Analysis
              </button>
            </div>
          </div>

          {/* Query Interface Page */}
          {currentPage === 'query' && (
            <div className="max-w-3xl mx-auto">
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
                    <RagasScoreDisplay scores={ragasScores} evaluationStatus={evaluationStatus} />
                  </>
                )}
              </div>
            </div>
          )}

          {/* RAGAS Analysis Page */}
          {currentPage === 'analysis' && (
            <div className="max-w-6xl mx-auto">
              <RagasAnalysisDashboard />
            </div>
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
}
