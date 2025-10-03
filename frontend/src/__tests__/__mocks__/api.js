/**
 * Mock API module for testing
 * Provides mock implementation of submitQuery function
 */

export const mockSubmitQuery = jest.fn(() =>
  new Promise((resolve) =>
    setTimeout(() => resolve({
      success: true,
      results: [
        { employee_id: 1, first_name: 'John', last_name: 'Doe', department: 'Engineering', salary_usd: 125000 },
        { employee_id: 2, first_name: 'Jane', last_name: 'Smith', department: 'Marketing', salary_usd: 135000 }
      ],
      sql: 'SELECT * FROM employees',
      ragas_scores: null
    }), 100)
  )
);

export const submitQuery = mockSubmitQuery;
