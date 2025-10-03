import PropTypes from 'prop-types';

export default function ErrorDisplay({ error }) {
  if (!error) return null;

  return (
    // Style error messages with appropriate colors (Subtask 3.2)
    <div className="bg-zinc-900 border-2 border-red-500/30 text-red-400 px-4 py-3 rounded-lg" role="alert" aria-live="assertive">
      <strong>Error:</strong> {error}
    </div>
  );
}

ErrorDisplay.propTypes = {
  error: PropTypes.string,
};
