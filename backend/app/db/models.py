from sqlalchemy import Column, Integer, String, Date, DECIMAL, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Employee(Base):
    """Employee ORM model for HR database"""
    __tablename__ = 'employees'

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    employment_status = Column(String(50), nullable=False)
    hire_date = Column(Date, nullable=False)
    leave_type = Column(String(50), nullable=True)
    salary_local = Column(DECIMAL(12, 2), nullable=False)
    salary_usd = Column(DECIMAL(12, 2), nullable=False)
    manager_name = Column(String(200), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"<Employee(id={self.employee_id}, name={self.first_name} {self.last_name}, department={self.department})>"


class QueryLog(Base):
    """QueryLog ORM model for query history with Ragas scores"""
    __tablename__ = 'query_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    natural_language_query = Column(String, nullable=False)
    generated_sql = Column(String, nullable=False)
    evaluation_status = Column(String(20), server_default=text("'pending'"), nullable=False)  # 'pending', 'evaluating', 'completed', 'failed'
    faithfulness_score = Column(DECIMAL(3, 2), nullable=True)
    answer_relevance_score = Column(DECIMAL(3, 2), nullable=True)
    context_precision_score = Column(DECIMAL(3, 2), nullable=True)
    result_count = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)

    def __repr__(self):
        return f"<QueryLog(id={self.id}, query='{self.natural_language_query[:50]}...', created_at={self.created_at})>"
