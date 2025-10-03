import PropTypes from 'prop-types';

export default function ResultsTable({ results }) {
  // Handle empty result sets gracefully (Subtask 2.2)
  if (!results || results.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No results to display. Submit a query to see results.
      </div>
    );
  }

  const columns = Object.keys(results[0]);

  return (
    // Responsive styling for mobile (Subtask 2.3)
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border" aria-label="Query results">
        <caption className="sr-only">Employee query results table</caption>
        <thead className="bg-gray-100">
          <tr>
            {columns.map(col => (
              <th key={col} className="px-4 py-2 border text-left text-xs sm:text-sm">
                {col.replace(/_/g, ' ').toUpperCase()}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {results.map((row, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              {columns.map(col => (
                <td key={col} className="px-4 py-2 border text-xs sm:text-sm">
                  {row[col]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

ResultsTable.propTypes = {
  results: PropTypes.arrayOf(PropTypes.object),
};
