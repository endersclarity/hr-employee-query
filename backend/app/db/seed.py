"""
Seed script for populating the employees table with realistic test data.
Designed to align with test queries from Story 1.5.
"""
import os
import sys
from datetime import date, timedelta
from decimal import Decimal

# Add backend to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import text
from app.db.session import get_engine
from app.db.models import Base, Employee


def check_if_seeded(session):
    """Check if database already has data"""
    result = session.execute(text("SELECT COUNT(*) FROM employees"))
    count = result.scalar()
    return count > 0


def seed_employees(engine):
    """Seed the employees table with realistic test data"""
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Check if already seeded
        if check_if_seeded(session):
            print("Database already contains employee data. Skipping seed.")
            return

        print("Seeding employee data...")

        # Calculate dynamic dates
        today = date.today()
        six_months_ago = today - timedelta(days=180)
        four_months_ago = today - timedelta(days=120)
        three_months_ago = today - timedelta(days=90)
        two_months_ago = today - timedelta(days=60)
        one_month_ago = today - timedelta(days=30)

        employees = [
            # Recent hires (5+ employees hired in last 6 months) - CRITICAL for test query 1
            Employee(
                first_name="Emma", last_name="Johnson", department="Engineering",
                role="Software Engineer", employment_status="Active",
                hire_date=four_months_ago, leave_type=None,
                salary_local=Decimal("95000.00"), salary_usd=Decimal("95000.00"),
                manager_name="Sarah Williams"
            ),
            Employee(
                first_name="Liam", last_name="Martinez", department="Marketing",
                role="Marketing Coordinator", employment_status="Active",
                hire_date=three_months_ago, leave_type=None,
                salary_local=Decimal("62000.00"), salary_usd=Decimal("62000.00"),
                manager_name="Michael Thompson"
            ),
            Employee(
                first_name="Sophia", last_name="Davis", department="Sales",
                role="Sales Representative", employment_status="Active",
                hire_date=two_months_ago, leave_type=None,
                salary_local=Decimal("68000.00"), salary_usd=Decimal("68000.00"),
                manager_name="John Doe"
            ),
            Employee(
                first_name="Noah", last_name="Garcia", department="Engineering",
                role="DevOps Engineer", employment_status="Active",
                hire_date=one_month_ago, leave_type=None,
                salary_local=Decimal("105000.00"), salary_usd=Decimal("105000.00"),
                manager_name="Sarah Williams"
            ),
            Employee(
                first_name="Olivia", last_name="Rodriguez", department="HR",
                role="HR Specialist", employment_status="Active",
                hire_date=two_months_ago, leave_type=None,
                salary_local=Decimal("58000.00"), salary_usd=Decimal("58000.00"),
                manager_name="Jennifer Lee"
            ),
            Employee(
                first_name="Ava", last_name="Wilson", department="Finance",
                role="Financial Analyst", employment_status="Active",
                hire_date=three_months_ago, leave_type=None,
                salary_local=Decimal("72000.00"), salary_usd=Decimal("72000.00"),
                manager_name="Robert Chen"
            ),

            # Engineering employees with salary > 120K (3+ required) - CRITICAL for test query 2
            Employee(
                first_name="James", last_name="Anderson", department="Engineering",
                role="Senior Software Engineer", employment_status="Active",
                hire_date=date(2022, 3, 15), leave_type=None,
                salary_local=Decimal("135000.00"), salary_usd=Decimal("135000.00"),
                manager_name="Sarah Williams"
            ),
            Employee(
                first_name="Michael", last_name="Brown", department="Engineering",
                role="Engineering Manager", employment_status="Active",
                hire_date=date(2021, 6, 1), leave_type=None,
                salary_local=Decimal("155000.00"), salary_usd=Decimal("155000.00"),
                manager_name="David Park"
            ),
            Employee(
                first_name="William", last_name="Taylor", department="Engineering",
                role="Principal Engineer", employment_status="Active",
                hire_date=date(2020, 9, 10), leave_type=None,
                salary_local=Decimal("175000.00"), salary_usd=Decimal("175000.00"),
                manager_name="David Park"
            ),
            Employee(
                first_name="Alexander", last_name="Harris", department="Engineering",
                role="Staff Software Engineer", employment_status="Active",
                hire_date=date(2021, 11, 20), leave_type=None,
                salary_local=Decimal("145000.00"), salary_usd=Decimal("145000.00"),
                manager_name="Sarah Williams"
            ),

            # Employees on Parental Leave (2+ required) - CRITICAL for test query 3
            Employee(
                first_name="Isabella", last_name="Thomas", department="Marketing",
                role="Senior Marketing Manager", employment_status="On Leave",
                hire_date=date(2022, 1, 15), leave_type="Parental Leave",
                salary_local=Decimal("98000.00"), salary_usd=Decimal("98000.00"),
                manager_name="Michael Thompson"
            ),
            Employee(
                first_name="Daniel", last_name="Jackson", department="Engineering",
                role="Software Engineer", employment_status="On Leave",
                hire_date=date(2023, 4, 1), leave_type="Parental Leave",
                salary_local=Decimal("110000.00"), salary_usd=Decimal("110000.00"),
                manager_name="Sarah Williams"
            ),

            # Employees managed by John Doe (4+ required) - CRITICAL for test query 4
            Employee(
                first_name="Matthew", last_name="White", department="Sales",
                role="Sales Manager", employment_status="Active",
                hire_date=date(2021, 2, 10), leave_type=None,
                salary_local=Decimal("92000.00"), salary_usd=Decimal("92000.00"),
                manager_name="John Doe"
            ),
            Employee(
                first_name="Emily", last_name="Lopez", department="Sales",
                role="Account Executive", employment_status="Active",
                hire_date=date(2022, 7, 20), leave_type=None,
                salary_local=Decimal("78000.00"), salary_usd=Decimal("78000.00"),
                manager_name="John Doe"
            ),
            Employee(
                first_name="David", last_name="Hill", department="Sales",
                role="Sales Development Rep", employment_status="Active",
                hire_date=date(2023, 5, 15), leave_type=None,
                salary_local=Decimal("55000.00"), salary_usd=Decimal("55000.00"),
                manager_name="John Doe"
            ),
            Employee(
                first_name="Sarah", last_name="Scott", department="Sales",
                role="Senior Account Executive", employment_status="Active",
                hire_date=date(2020, 11, 5), leave_type=None,
                salary_local=Decimal("88000.00"), salary_usd=Decimal("88000.00"),
                manager_name="John Doe"
            ),

            # Additional diverse employees to reach 50+
            Employee(
                first_name="Sarah", last_name="Williams", department="Engineering",
                role="Director of Engineering", employment_status="Active",
                hire_date=date(2019, 3, 1), leave_type=None,
                salary_local=Decimal("185000.00"), salary_usd=Decimal("185000.00"),
                manager_name="David Park"
            ),
            Employee(
                first_name="Jennifer", last_name="Lee", department="HR",
                role="HR Director", employment_status="Active",
                hire_date=date(2020, 1, 15), leave_type=None,
                salary_local=Decimal("125000.00"), salary_usd=Decimal("125000.00"),
                manager_name="David Park"
            ),
            Employee(
                first_name="Robert", last_name="Chen", department="Finance",
                role="Finance Director", employment_status="Active",
                hire_date=date(2019, 8, 20), leave_type=None,
                salary_local=Decimal("140000.00"), salary_usd=Decimal("140000.00"),
                manager_name="David Park"
            ),
            Employee(
                first_name="Michael", last_name="Thompson", department="Marketing",
                role="Marketing Director", employment_status="Active",
                hire_date=date(2020, 5, 10), leave_type=None,
                salary_local=Decimal("130000.00"), salary_usd=Decimal("130000.00"),
                manager_name="David Park"
            ),
            Employee(
                first_name="David", last_name="Park", department="Executive",
                role="Chief Technology Officer", employment_status="Active",
                hire_date=date(2018, 1, 1), leave_type=None,
                salary_local=Decimal("250000.00"), salary_usd=Decimal("250000.00"),
                manager_name=None
            ),

            # Marketing team
            Employee(
                first_name="Jessica", last_name="Moore", department="Marketing",
                role="Content Marketing Manager", employment_status="Active",
                hire_date=date(2022, 3, 10), leave_type=None,
                salary_local=Decimal("82000.00"), salary_usd=Decimal("82000.00"),
                manager_name="Michael Thompson"
            ),
            Employee(
                first_name="Kevin", last_name="Martin", department="Marketing",
                role="SEO Specialist", employment_status="Active",
                hire_date=date(2023, 1, 5), leave_type=None,
                salary_local=Decimal("68000.00"), salary_usd=Decimal("68000.00"),
                manager_name="Jessica Moore"
            ),
            Employee(
                first_name="Amanda", last_name="Clark", department="Marketing",
                role="Social Media Manager", employment_status="Active",
                hire_date=date(2022, 9, 20), leave_type=None,
                salary_local=Decimal("65000.00"), salary_usd=Decimal("65000.00"),
                manager_name="Jessica Moore"
            ),
            Employee(
                first_name="Ryan", last_name="Lewis", department="Marketing",
                role="Marketing Analyst", employment_status="Active",
                hire_date=date(2023, 6, 1), leave_type=None,
                salary_local=Decimal("70000.00"), salary_usd=Decimal("70000.00"),
                manager_name="Michael Thompson"
            ),
            Employee(
                first_name="Lauren", last_name="Walker", department="Marketing",
                role="Brand Manager", employment_status="Active",
                hire_date=date(2021, 4, 15), leave_type=None,
                salary_local=Decimal("89000.00"), salary_usd=Decimal("89000.00"),
                manager_name="Michael Thompson"
            ),

            # Engineering team
            Employee(
                first_name="Christopher", last_name="Hall", department="Engineering",
                role="Software Engineer", employment_status="Active",
                hire_date=date(2022, 2, 1), leave_type=None,
                salary_local=Decimal("98000.00"), salary_usd=Decimal("98000.00"),
                manager_name="Sarah Williams"
            ),
            Employee(
                first_name="Michelle", last_name="Allen", department="Engineering",
                role="QA Engineer", employment_status="Active",
                hire_date=date(2023, 3, 10), leave_type=None,
                salary_local=Decimal("85000.00"), salary_usd=Decimal("85000.00"),
                manager_name="Sarah Williams"
            ),
            Employee(
                first_name="Brandon", last_name="Young", department="Engineering",
                role="Frontend Developer", employment_status="Active",
                hire_date=date(2022, 8, 5), leave_type=None,
                salary_local=Decimal("92000.00"), salary_usd=Decimal("92000.00"),
                manager_name="Michael Brown"
            ),
            Employee(
                first_name="Rachel", last_name="King", department="Engineering",
                role="Backend Developer", employment_status="Active",
                hire_date=date(2021, 10, 20), leave_type=None,
                salary_local=Decimal("105000.00"), salary_usd=Decimal("105000.00"),
                manager_name="Michael Brown"
            ),
            Employee(
                first_name="Justin", last_name="Wright", department="Engineering",
                role="Data Engineer", employment_status="Active",
                hire_date=date(2022, 5, 15), leave_type=None,
                salary_local=Decimal("115000.00"), salary_usd=Decimal("115000.00"),
                manager_name="Sarah Williams"
            ),

            # HR team
            Employee(
                first_name="Nicole", last_name="Green", department="HR",
                role="Recruiter", employment_status="Active",
                hire_date=date(2022, 4, 1), leave_type=None,
                salary_local=Decimal("65000.00"), salary_usd=Decimal("65000.00"),
                manager_name="Jennifer Lee"
            ),
            Employee(
                first_name="Andrew", last_name="Baker", department="HR",
                role="HR Coordinator", employment_status="Active",
                hire_date=date(2023, 2, 10), leave_type=None,
                salary_local=Decimal("52000.00"), salary_usd=Decimal("52000.00"),
                manager_name="Jennifer Lee"
            ),
            Employee(
                first_name="Stephanie", last_name="Adams", department="HR",
                role="Compensation Analyst", employment_status="Active",
                hire_date=date(2021, 9, 5), leave_type=None,
                salary_local=Decimal("72000.00"), salary_usd=Decimal("72000.00"),
                manager_name="Jennifer Lee"
            ),
            Employee(
                first_name="Tyler", last_name="Nelson", department="HR",
                role="Learning & Development Manager", employment_status="Active",
                hire_date=date(2022, 1, 20), leave_type=None,
                salary_local=Decimal("78000.00"), salary_usd=Decimal("78000.00"),
                manager_name="Jennifer Lee"
            ),

            # Finance team
            Employee(
                first_name="Rebecca", last_name="Carter", department="Finance",
                role="Senior Accountant", employment_status="Active",
                hire_date=date(2021, 3, 10), leave_type=None,
                salary_local=Decimal("85000.00"), salary_usd=Decimal("85000.00"),
                manager_name="Robert Chen"
            ),
            Employee(
                first_name="Joshua", last_name="Mitchell", department="Finance",
                role="Accountant", employment_status="Active",
                hire_date=date(2022, 6, 1), leave_type=None,
                salary_local=Decimal("68000.00"), salary_usd=Decimal("68000.00"),
                manager_name="Rebecca Carter"
            ),
            Employee(
                first_name="Megan", last_name="Perez", department="Finance",
                role="Financial Planning Analyst", employment_status="Active",
                hire_date=date(2023, 4, 15), leave_type=None,
                salary_local=Decimal("75000.00"), salary_usd=Decimal("75000.00"),
                manager_name="Robert Chen"
            ),
            Employee(
                first_name="Jason", last_name="Roberts", department="Finance",
                role="Controller", employment_status="Active",
                hire_date=date(2020, 2, 1), leave_type=None,
                salary_local=Decimal("118000.00"), salary_usd=Decimal("118000.00"),
                manager_name="Robert Chen"
            ),

            # Sales team
            Employee(
                first_name="Amber", last_name="Turner", department="Sales",
                role="Account Manager", employment_status="Active",
                hire_date=date(2022, 10, 5), leave_type=None,
                salary_local=Decimal("75000.00"), salary_usd=Decimal("75000.00"),
                manager_name="Matthew White"
            ),
            Employee(
                first_name="Eric", last_name="Phillips", department="Sales",
                role="Sales Engineer", employment_status="Active",
                hire_date=date(2021, 7, 20), leave_type=None,
                salary_local=Decimal("95000.00"), salary_usd=Decimal("95000.00"),
                manager_name="Matthew White"
            ),
            Employee(
                first_name="Heather", last_name="Campbell", department="Sales",
                role="Customer Success Manager", employment_status="Active",
                hire_date=date(2022, 11, 10), leave_type=None,
                salary_local=Decimal("72000.00"), salary_usd=Decimal("72000.00"),
                manager_name="Matthew White"
            ),
            Employee(
                first_name="Jonathan", last_name="Parker", department="Sales",
                role="Business Development Rep", employment_status="Active",
                hire_date=date(2023, 8, 1), leave_type=None,
                salary_local=Decimal("58000.00"), salary_usd=Decimal("58000.00"),
                manager_name="John Doe"
            ),

            # Additional employees to reach 50+
            Employee(
                first_name="Ashley", last_name="Evans", department="Engineering",
                role="UI/UX Designer", employment_status="Active",
                hire_date=date(2022, 12, 1), leave_type=None,
                salary_local=Decimal("88000.00"), salary_usd=Decimal("88000.00"),
                manager_name="Sarah Williams"
            ),
            Employee(
                first_name="Brian", last_name="Edwards", department="Engineering",
                role="Security Engineer", employment_status="Active",
                hire_date=date(2021, 5, 10), leave_type=None,
                salary_local=Decimal("125000.00"), salary_usd=Decimal("125000.00"),
                manager_name="Sarah Williams"
            ),
            Employee(
                first_name="Christina", last_name="Collins", department="Marketing",
                role="Product Marketing Manager", employment_status="Active",
                hire_date=date(2021, 8, 15), leave_type=None,
                salary_local=Decimal("95000.00"), salary_usd=Decimal("95000.00"),
                manager_name="Michael Thompson"
            ),
            Employee(
                first_name="Patrick", last_name="Stewart", department="Finance",
                role="Tax Analyst", employment_status="Active",
                hire_date=date(2023, 3, 20), leave_type=None,
                salary_local=Decimal("70000.00"), salary_usd=Decimal("70000.00"),
                manager_name="Jason Roberts"
            ),
            Employee(
                first_name="Melissa", last_name="Sanchez", department="HR",
                role="Benefits Administrator", employment_status="Active",
                hire_date=date(2022, 7, 5), leave_type=None,
                salary_local=Decimal("58000.00"), salary_usd=Decimal("58000.00"),
                manager_name="Jennifer Lee"
            ),
            Employee(
                first_name="Gregory", last_name="Morris", department="Sales",
                role="Regional Sales Director", employment_status="Active",
                hire_date=date(2020, 4, 1), leave_type=None,
                salary_local=Decimal("135000.00"), salary_usd=Decimal("135000.00"),
                manager_name="John Doe"
            ),

            # Employee on medical leave
            Employee(
                first_name="Angela", last_name="Rogers", department="Engineering",
                role="Product Manager", employment_status="On Leave",
                hire_date=date(2021, 12, 10), leave_type="Medical Leave",
                salary_local=Decimal("112000.00"), salary_usd=Decimal("112000.00"),
                manager_name="Sarah Williams"
            ),

            # Terminated employees
            Employee(
                first_name="Mark", last_name="Reed", department="Sales",
                role="Account Executive", employment_status="Terminated",
                hire_date=date(2022, 2, 15), leave_type=None,
                salary_local=Decimal("75000.00"), salary_usd=Decimal("75000.00"),
                manager_name="Matthew White"
            ),
            Employee(
                first_name="Laura", last_name="Cook", department="Marketing",
                role="Marketing Specialist", employment_status="Terminated",
                hire_date=date(2023, 1, 10), leave_type=None,
                salary_local=Decimal("60000.00"), salary_usd=Decimal("60000.00"),
                manager_name="Jessica Moore"
            ),
        ]

        # Add all employees to session
        session.add_all(employees)
        session.commit()

        print(f"✅ Successfully seeded {len(employees)} employee records")

        # Verify test scenarios
        print("\nValidating test scenarios...")
        validate_test_scenarios(session)

    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        session.close()


def validate_test_scenarios(session):
    """Validate that all test scenarios have sufficient data"""
    from datetime import date, timedelta

    tests = [
        ("Recent hires (last 6 months)",
         "SELECT COUNT(*) FROM employees WHERE hire_date >= CURRENT_DATE - INTERVAL '6 months'",
         5),
        ("Engineering high earners (>120K)",
         "SELECT COUNT(*) FROM employees WHERE department = 'Engineering' AND salary_usd > 120000",
         3),
        ("Parental leave",
         "SELECT COUNT(*) FROM employees WHERE leave_type = 'Parental Leave'",
         2),
        ("John Doe reports",
         "SELECT COUNT(*) FROM employees WHERE manager_name = 'John Doe'",
         4),
    ]

    all_passed = True
    for name, query, min_count in tests:
        result = session.execute(text(query))
        count = result.scalar()
        status = "✓" if count >= min_count else "✗"
        print(f"  {status} {name}: {count} records (required: >= {min_count})")
        if count < min_count:
            all_passed = False

    if all_passed:
        print("\n✅ All test scenarios validated - seed data ready for Story 1.5")
    else:
        print("\n❌ Some test scenarios failed validation")
        raise ValueError("Test scenario validation failed")


if __name__ == "__main__":
    print("Starting database seed process...")
    engine = get_engine()
    seed_employees(engine)
    print("\n✅ Database seed completed successfully")
