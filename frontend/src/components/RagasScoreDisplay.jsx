import PropTypes from 'prop-types';

/**
 * Displays Ragas evaluation scores with color-coded badges
 * @param {Object} props
 * @param {Object|null} props.scores - Ragas scores object
 * @param {number} props.scores.faithfulness - Score 0.0-1.0
 * @param {number} props.scores.answer_relevance - Score 0.0-1.0
 * @param {number} props.scores.context_utilization - Score 0.0-1.0
 * @param {string|null} props.evaluationStatus - 'pending', 'evaluating', 'completed', 'failed'
 * @returns {JSX.Element|null} Score badges or null if no evaluation started
 */
export default function RagasScoreDisplay({ scores, evaluationStatus }) {
  if (!evaluationStatus) return null;

  const isLoading = evaluationStatus === 'pending' || evaluationStatus === 'evaluating';

  const getColor = (score) => {
    if (score > 0.8) return 'text-green-400';
    if (score >= 0.7) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="mt-4 bg-zinc-900 border-2 border-zinc-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4 border-b-2 border-zinc-700 pb-2">
        RAGAS Evaluation Scores
        {isLoading && <span className="ml-2 text-sm text-zinc-400 font-normal">Evaluating...</span>}
      </h3>

      {isLoading ? (
        <div className="flex gap-4 flex-wrap">
          {['Faithfulness', 'Answer Relevance', 'Context Utilization'].map((metric) => (
            <div key={metric} className="bg-zinc-950 border-2 border-zinc-800 p-6 rounded-lg flex-1 min-w-[200px]">
              <div className="text-zinc-400 text-sm mb-1">{metric}</div>
              <div className="text-2xl font-bold text-zinc-600 animate-pulse">--</div>
            </div>
          ))}
        </div>
      ) : scores ? (
        <div className="flex gap-4 flex-wrap">
          <div className="bg-zinc-950 border-2 border-zinc-800 p-6 rounded-lg flex-1 min-w-[200px]">
            <div className="text-zinc-400 text-sm mb-1">Faithfulness</div>
            <div
              className={`text-2xl font-bold ${getColor(scores.faithfulness)}`}
              aria-label={`Faithfulness score: ${scores.faithfulness.toFixed(2)} out of 1.0`}
            >
              {scores.faithfulness.toFixed(2)}
            </div>
          </div>
          <div className="bg-zinc-950 border-2 border-zinc-800 p-6 rounded-lg flex-1 min-w-[200px]">
            <div className="text-zinc-400 text-sm mb-1">Answer Relevance</div>
            <div
              className={`text-2xl font-bold ${getColor(scores.answer_relevance)}`}
              aria-label={`Answer Relevance score: ${scores.answer_relevance.toFixed(2)} out of 1.0`}
            >
              {scores.answer_relevance.toFixed(2)}
            </div>
          </div>
          <div className="bg-zinc-950 border-2 border-zinc-800 p-6 rounded-lg flex-1 min-w-[200px]">
            <div className="text-zinc-400 text-sm mb-1">Context Utilization</div>
            <div
              className={`text-2xl font-bold ${getColor(scores.context_utilization)}`}
              aria-label={`Context Utilization score: ${scores.context_utilization.toFixed(2)} out of 1.0`}
            >
              {scores.context_utilization.toFixed(2)}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-zinc-500 text-center py-4">Evaluation failed</div>
      )}
    </div>
  );
}

RagasScoreDisplay.propTypes = {
  scores: PropTypes.shape({
    faithfulness: PropTypes.number.isRequired,
    answer_relevance: PropTypes.number.isRequired,
    context_utilization: PropTypes.number.isRequired
  }),
  evaluationStatus: PropTypes.string
};
