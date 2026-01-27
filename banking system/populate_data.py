import mysql.connector
from datetime import date
import random

# --- CONFIGURATION ---
db_config = {
    'user': 'root',
    'password': 'Pratyu@123',  # <--- UPDATE THIS
    'host': 'localhost',
    'database': 'bank_db'
}

def get_connection():
    return mysql.connector.connect(**db_config)

def populate_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Starting data population...")

    try:
        # 1. Clear existing data to avoid duplicates (Optional safety)
        # Note: Order matters due to Foreign Keys
        tables = ['Loan_Payment', 'Customer_Loan', 'Loan', 'Customer_Account', 
                  'SavingsAccount', 'CheckingAccount', 'Account', 
                  'BusinessCustomer', 'IndividualCustomer', 'Customer', 
                  'Dependent', 'Employee', 'Branch']
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print("Existing data cleared.")

        # 2. Create 10 Branches
        branches = [
            ('Downtown', 'Buffalo', 10000000), ('North', 'Amherst', 5000000),
            ('South', 'Orchard Park', 2000000), ('East', 'Cheektowaga', 3000000),
            ('West', 'Kenmore', 1500000), ('University', 'Buffalo', 750000),
            ('Airport', 'Cheektowaga', 4000000), ('Waterfront', 'Buffalo', 6000000),
            ('Suburban', 'Williamsville', 8000000), ('TechPark', 'Amherst', 9000000)
        ]
        cursor.executemany("INSERT INTO Branch VALUES (%s, %s, %s)", branches)
        print("10 Branches created.")

        # 3. Create 40 Employees
        # We need a Manager first to satisfy the self-referencing FK
        manager_ssn = '999-00-0001'
        cursor.execute("INSERT INTO Employee VALUES (%s, 'Big Boss', '1 Admin Ln', '555-0001', '2010-01-01', 120, NULL)", (manager_ssn,))
        
        employees = []
        # Generate 39 more employees
        for i in range(2, 41):
            ssn = f"999-00-{i:04d}"
            name = f"Employee {i}"
            # Make the first 5 employees "Star Bankers" for the report
            if i <= 6: name = f"Star Banker {i}"
            
            emp = (ssn, name, f"{i} Worker Rd", f"555-{i:04d}", '2020-01-01', 36, manager_ssn)
            employees.append(emp)
        
        cursor.executemany("INSERT INTO Employee VALUES (%s, %s, %s, %s, %s, %s, %s)", employees)
        print("40 Employees created.")

        # 4. Create Customers (Individuals & Business)
        # We need customers to assign accounts to.
        
        # Create 20 Individual Customers
        for i in range(1, 21):
            # Create Supertype
            cursor.execute("INSERT INTO Customer (CustomerType, Address) VALUES ('Individual', '123 Home St')")
            c_id = cursor.lastrowid
            
            # Link to a Banker (Assign mostly to the first 5 bankers to skew the "Top 5" report)
            banker_ssn = f"999-00-{random.randint(2, 6):04d}" 
            
            # Create Subtype
            ssn = f"111-00-{i:04d}"
            cursor.execute("INSERT INTO IndividualCustomer VALUES (%s, %s, %s, %s)", 
                           (c_id, ssn, f"Indiv Customer {i}", banker_ssn))

        # Create 5 Business Customers
        for i in range(1, 6):
            cursor.execute("INSERT INTO Customer (CustomerType, Address) VALUES ('Business', '456 Corp Blvd')")
            c_id = cursor.lastrowid
            cursor.execute("INSERT INTO BusinessCustomer VALUES (%s, %s)", (c_id, f"Biz Corp {i}"))

        print("25 Customers created.")

        # 5. Create 20 Accounts (Mix of Savings/Checking)
        # Assign high balances to customers managed by "Star Banker 2" to ensure they win the report
        for i in range(1, 21):
            acct_id = 1000 + i
            balance = random.randint(1000, 50000)
            
            # Rig the data: Make accounts 1-5 have huge balances
            if i <= 5: balance = 500000 
            
            acct_type = 'Savings' if i % 2 == 0 else 'Checking'
            
            cursor.execute("INSERT INTO Account VALUES (%s, %s, %s, %s)", (acct_id, balance, date.today(), acct_type))
            
            # Link to a random Individual Customer (ID 1-20)
            cust_id = random.randint(1, 20)
            cursor.execute("INSERT INTO Customer_Account VALUES (%s, %s)", (cust_id, acct_id))

            # Subtype details
            if acct_type == 'Savings':
                cursor.execute("INSERT INTO SavingsAccount VALUES (%s, 1.5)", (acct_id,))
            else:
                cursor.execute("INSERT INTO CheckingAccount VALUES (%s, 500.00)", (acct_id,))

        print("20 Accounts created.")

        # 6. Create Loans (For "Highest Debt" Report)
        # We need loans with High Amounts and Low Payments
        branches_list = [b[0] for b in branches]
        
        for i in range(1, 11):
            loan_id = 5000 + i
            amount = random.randint(10000, 100000)
            branch = random.choice(branches_list)
            
            cursor.execute("INSERT INTO Loan VALUES (%s, %s, %s)", (loan_id, amount, branch))
            
            # Link to customer
            cust_id = random.randint(1, 20)
            cursor.execute("INSERT INTO Customer_Loan VALUES (%s, %s)", (cust_id, loan_id))
            
            # Add small payments to leave high debt
            cursor.execute("INSERT INTO Loan_Payment VALUES (%s, 1, %s, %s)", (loan_id, date.today(), 100.00))

        print("10 Loans created.")

        conn.commit()
        print("Data population complete! You can now run the reports.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    populate_db()