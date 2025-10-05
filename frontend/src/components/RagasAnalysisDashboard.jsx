import { useState, useEffect } from 'react';
import { fetchAnalysisReport } from '../services/api';

export default function RagasAnalysisDashboard() {
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalysis();
  }, []);

  const loadAnalysis = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await fetchAnalysisReport();
      setAnalysisData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-zinc-400">Loading analysis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-6">
        <h2 className="text-xl font-bold text-red-400 mb-2">Error Loading Analysis</h2>
        <p className="text-zinc-300">{error}</p>
        <button
          onClick={loadAnalysis}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!analysisData) {
    return null;
  }

  const getScoreColor = (score) => {
    if (score >= 0.9) return 'text-emerald-400';
    if (score >= 0.8) return 'text-green-400';
    if (score >= 0.7) return 'text-yellow-400';
    if (score >= 0.6) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreBgColor = (score) => {
    if (score >= 0.9) return 'bg-emerald-500/20 border-emerald-500/50';
    if (score >= 0.8) return 'bg-green-500/20 border-green-500/50';
    if (score >= 0.7) return 'bg-yellow-500/20 border-yellow-500/50';
    if (score >= 0.6) return 'bg-orange-500/20 border-orange-500/50';
    return 'bg-red-500/20 border-red-500/50';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-zinc-900 rounded-lg p-6 border border-zinc-800">
        <h1 className="text-2xl font-bold text-white mb-2">RAGAS Evaluation Analysis</h1>
        <p className="text-zinc-400">
          Comprehensive evaluation metrics across {analysisData.total_queries} queries
        </p>
      </div>

      {/* Average Scores */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className={`border rounded-lg p-6 ${getScoreBgColor(analysisData.average_scores.faithfulness)}`}>
          <div className="text-sm text-zinc-300 mb-1">Faithfulness</div>
          <div className={`text-4xl font-bold ${getScoreColor(analysisData.average_scores.faithfulness)}`}>
            {analysisData.average_scores.faithfulness.toFixed(2)}
          </div>
          <div className="text-xs text-zinc-400 mt-2">
            Factual consistency with database
          </div>
        </div>

        <div className={`border rounded-lg p-6 ${getScoreBgColor(analysisData.average_scores.answer_relevance)}`}>
          <div className="text-sm text-zinc-300 mb-1">Answer Relevance</div>
          <div className={`text-4xl font-bold ${getScoreColor(analysisData.average_scores.answer_relevance)}`}>
            {analysisData.average_scores.answer_relevance.toFixed(2)}
          </div>
          <div className="text-xs text-zinc-400 mt-2">
            Alignment with user intent
          </div>
        </div>

        <div className={`border rounded-lg p-6 ${getScoreBgColor(analysisData.average_scores.context_precision)}`}>
          <div className="text-sm text-zinc-300 mb-1">Context Utilization</div>
          <div className={`text-4xl font-bold ${getScoreColor(analysisData.average_scores.context_precision)}`}>
            {analysisData.average_scores.context_precision.toFixed(2)}
          </div>
          <div className="text-xs text-zinc-400 mt-2">
            Relevant fields included
          </div>
        </div>
      </div>

      {/* Query Type Analysis */}
      {analysisData.query_type_analysis && Object.keys(analysisData.query_type_analysis).length > 0 && (
        <div className="bg-zinc-900 rounded-lg p-6 border border-zinc-800">
          <h2 className="text-xl font-bold text-white mb-4">Query Type Breakdown</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left border-b border-zinc-700">
                <tr>
                  <th className="pb-3 text-zinc-400 font-medium">Query Type</th>
                  <th className="pb-3 text-zinc-400 font-medium text-right">Count</th>
                  <th className="pb-3 text-zinc-400 font-medium text-right">Faithfulness</th>
                  <th className="pb-3 text-zinc-400 font-medium text-right">Answer Relevance</th>
                  <th className="pb-3 text-zinc-400 font-medium text-right">Context Utilization</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {Object.entries(analysisData.query_type_analysis).map(([type, data]) => (
                  <tr key={type} className="text-zinc-300">
                    <td className="py-3 capitalize">
                      {type.replace('_', ' ')}
                    </td>
                    <td className="py-3 text-right text-zinc-400">{data.count}</td>
                    <td className={`py-3 text-right font-medium ${getScoreColor(data.avg_faithfulness)}`}>
                      {data.avg_faithfulness.toFixed(3)}
                    </td>
                    <td className={`py-3 text-right font-medium ${getScoreColor(data.avg_answer_relevance)}`}>
                      {data.avg_answer_relevance.toFixed(3)}
                    </td>
                    <td className={`py-3 text-right font-medium ${getScoreColor(data.avg_context_precision)}`}>
                      {data.avg_context_precision.toFixed(3)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analysisData.recommendations && analysisData.recommendations.length > 0 && (
        <div className="bg-zinc-900 rounded-lg p-6 border border-zinc-800">
          <h2 className="text-xl font-bold text-white mb-4">Recommendations</h2>
          <ul className="space-y-3">
            {analysisData.recommendations.map((rec, index) => (
              <li key={index} className="flex items-start">
                <span className="text-blue-400 mr-3 mt-1">▸</span>
                <span className="text-zinc-300">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Weak Queries */}
      {analysisData.weak_queries && analysisData.weak_queries.length > 0 && (
        <div className="bg-zinc-900 rounded-lg p-6 border border-zinc-800">
          <h2 className="text-xl font-bold text-white mb-4">
            Weak Queries ({analysisData.weak_queries.length})
          </h2>
          <div className="space-y-4">
            {analysisData.weak_queries.map((query, index) => (
              <div key={index} className="bg-zinc-800/50 rounded-lg p-4 border border-zinc-700">
                <div className="text-zinc-200 font-medium mb-2">{query.query}</div>
                <div className="text-xs text-zinc-400 mb-3 font-mono">{query.sql}</div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-zinc-500">Faithfulness: </span>
                    <span className={getScoreColor(query.scores.faithfulness)}>
                      {query.scores.faithfulness?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-zinc-500">Answer Relevance: </span>
                    <span className={getScoreColor(query.scores.answer_relevance)}>
                      {query.scores.answer_relevance?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-zinc-500">Context Utilization: </span>
                    <span className={getScoreColor(query.scores.context_precision)}>
                      {query.scores.context_precision?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                </div>
                {query.reason && (
                  <div className="mt-3 text-sm text-orange-400">
                    {query.reason}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Refresh Button */}
      <div className="text-center">
        <button
          onClick={loadAnalysis}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Refresh Analysis
        </button>
      </div>
    </div>
  );
}
