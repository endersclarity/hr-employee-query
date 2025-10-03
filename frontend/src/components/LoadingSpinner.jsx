export default function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center py-8" role="status" aria-live="polite">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" aria-label="Loading"></div>
      <span className="ml-3 text-gray-600">Processing query...</span>
    </div>
  );
}
