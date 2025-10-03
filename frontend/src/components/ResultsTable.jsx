import PropTypes from 'prop-types';

export default function ResultsTable({ results }) {
  // Handle empty result sets gracefully (Subtask 2.2)
  if (!results || results.length === 0) {
    return (
      <div className="text-center text-zinc-400 py-8">
        No results to display. Submit a query to see results.
      </div>
    );
  }

  const columns = Object.keys(results[0]);

  return (
    // Responsive styling for mobile (Subtask 2.3)
    <div className="overflow-x-auto bg-zinc-900 border-2 border-zinc-700 rounded-lg">
      <table className="min-w-full" aria-label="Query results">
        <caption className="sr-only">Employee query results table</caption>
        <thead className="bg-black border-b-2 border-zinc-700">
          <tr>
            {columns.map(col => (
              <th key={col} className="px-4 py-2 text-left text-xs sm:text-sm text-zinc-400">
                {col.replace(/_/g, ' ').toUpperCase()}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y-2 divide-zinc-800">
          {results.map((row, idx) => (
            <tr key={idx} className="hover:bg-zinc-800/50">
              {columns.map(col => {
                const isId = col.toLowerCase().includes('id');
                const isName = col.toLowerCase().includes('name');
                const textColor = isName ? 'text-white' : isId ? 'text-zinc-300' : 'text-zinc-400';
                return (
                  <td key={col} className={`px-4 py-2 text-xs sm:text-sm ${textColor}`}>
                    {row[col]}
                  </td>
                );
              })}
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
