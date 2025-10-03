import { render, screen } from '@testing-library/react';
import ResultsTable from '../components/ResultsTable';

describe('ResultsTable', () => {
  const mockResults = [
    {
      employee_id: 1,
      first_name: 'John',
      last_name: 'Doe',
      department: 'Engineering',
      salary_usd: 125000
    },
    {
      employee_id: 2,
      first_name: 'Jane',
      last_name: 'Smith',
      department: 'Marketing',
      salary_usd: 95000
    }
  ];

  test('renders empty state message when results is null', () => {
    render(<ResultsTable results={null} />);
    expect(screen.getByText('No results to display. Submit a query to see results.')).toBeInTheDocument();
  });

  test('renders empty state message when results is empty array', () => {
    render(<ResultsTable results={[]} />);
    expect(screen.getByText('No results to display. Submit a query to see results.')).toBeInTheDocument();
  });

  test('renders table with correct column headers', () => {
    render(<ResultsTable results={mockResults} />);

    expect(screen.getByText('EMPLOYEE ID')).toBeInTheDocument();
    expect(screen.getByText('FIRST NAME')).toBeInTheDocument();
    expect(screen.getByText('LAST NAME')).toBeInTheDocument();
    expect(screen.getByText('DEPARTMENT')).toBeInTheDocument();
    expect(screen.getByText('SALARY USD')).toBeInTheDocument();
  });

  test('formats column headers correctly (uppercase and underscores replaced)', () => {
    render(<ResultsTable results={mockResults} />);

    // Check that underscores are replaced with spaces and text is uppercase
    expect(screen.getByText('EMPLOYEE ID')).toBeInTheDocument();
    expect(screen.getByText('SALARY USD')).toBeInTheDocument();
  });

  test('renders correct number of data rows', () => {
    render(<ResultsTable results={mockResults} />);

    // Should have 2 data rows plus 1 header row
    const rows = screen.getAllByRole('row');
    expect(rows).toHaveLength(3); // 1 header + 2 data rows
  });

  test('renders cell data correctly', () => {
    render(<ResultsTable results={mockResults} />);

    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('Doe')).toBeInTheDocument();
    expect(screen.getByText('Engineering')).toBeInTheDocument();
    expect(screen.getByText('125000')).toBeInTheDocument();

    expect(screen.getByText('Jane')).toBeInTheDocument();
    expect(screen.getByText('Smith')).toBeInTheDocument();
    expect(screen.getByText('Marketing')).toBeInTheDocument();
    expect(screen.getByText('95000')).toBeInTheDocument();
  });

  test('handles single result correctly', () => {
    const singleResult = [mockResults[0]];
    render(<ResultsTable results={singleResult} />);

    const rows = screen.getAllByRole('row');
    expect(rows).toHaveLength(2); // 1 header + 1 data row

    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('Engineering')).toBeInTheDocument();
  });

  test('renders table with responsive classes', () => {
    const { container } = render(<ResultsTable results={mockResults} />);

    const tableWrapper = container.querySelector('.overflow-x-auto');
    expect(tableWrapper).toBeInTheDocument();
  });

  test('handles different data shapes dynamically', () => {
    const differentData = [
      { id: 1, name: 'Test', status: 'active' },
      { id: 2, name: 'Test2', status: 'inactive' }
    ];

    render(<ResultsTable results={differentData} />);

    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('NAME')).toBeInTheDocument();
    expect(screen.getByText('STATUS')).toBeInTheDocument();

    expect(screen.getByText('Test')).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
    expect(screen.getByText('inactive')).toBeInTheDocument();
  });

  test('applies hover styles class to table rows', () => {
    const { container } = render(<ResultsTable results={mockResults} />);

    const dataRows = container.querySelectorAll('tbody tr');
    dataRows.forEach(row => {
      expect(row).toHaveClass('hover:bg-gray-50');
    });
  });

  test('renders table structure correctly', () => {
    const { container } = render(<ResultsTable results={mockResults} />);

    expect(container.querySelector('table')).toBeInTheDocument();
    expect(container.querySelector('thead')).toBeInTheDocument();
    expect(container.querySelector('tbody')).toBeInTheDocument();
  });
});
