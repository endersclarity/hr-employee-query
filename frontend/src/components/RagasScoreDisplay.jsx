import PropTypes from 'prop-types';

/**
 * Displays Ragas evaluation scores with color-coded badges
 * @param {Object} props
 * @param {Object|null} props.scores - Ragas scores object
 * @param {number} props.scores.faithfulness - Score 0.0-1.0
 * @param {number} props.scores.answer_relevance - Score 0.0-1.0
 * @param {number} props.scores.context_utilization - Score 0.0-1.0
 * @returns {JSX.Element|null} Score badges or null if no scores
 */
export default function RagasScoreDisplay({ scores }) {
  if (!scores) return null;

  const getColor = (score) => {
    if (score > 0.8) return 'bg-green-100 text-green-800';
    if (score >= 0.7) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="mt-4 flex gap-4">
      <div
        className={`px-3 py-1 rounded ${getColor(scores.faithfulness)}`}
        aria-label={`Faithfulness score: ${scores.faithfulness.toFixed(2)} out of 1.0`}
      >
        Faithfulness: {scores.faithfulness.toFixed(2)}
      </div>
      <div
        className={`px-3 py-1 rounded ${getColor(scores.answer_relevance)}`}
        aria-label={`Answer Relevance score: ${scores.answer_relevance.toFixed(2)} out of 1.0`}
      >
        Answer Relevance: {scores.answer_relevance.toFixed(2)}
      </div>
      <div
        className={`px-3 py-1 rounded ${getColor(scores.context_utilization)}`}
        aria-label={`Context Utilization score: ${scores.context_utilization.toFixed(2)} out of 1.0`}
      >
        Context Utilization: {scores.context_utilization.toFixed(2)}
      </div>
    </div>
  );
}

RagasScoreDisplay.propTypes = {
  scores: PropTypes.shape({
    faithfulness: PropTypes.number.isRequired,
    answer_relevance: PropTypes.number.isRequired,
    context_utilization: PropTypes.number.isRequired
  })
};
