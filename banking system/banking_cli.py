import mysql.connector
import sys
from datetime import date

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    'user': 'root',
    'password': 'YOUR PWD',  # <--- Verify this matches your setup
    'host': 'localhost',
    'database': 'bank_db'
}

def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return None

# --- TRANSACTIONS ---
def create_business_account():
    print("\n--- Create Business Account ---")
    name = input("Business Name: ")
    address = input("Business Address: ")
    try:
        balance = float(input("Initial Balance: "))
    except ValueError:
        print("Invalid balance.")
        return

    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        # 1. Create Customer
        cursor.execute("INSERT INTO Customer (CustomerType, Address) VALUES ('Business', %s)", (address,))
        cust_id = cursor.lastrowid
        cursor.execute("INSERT INTO BusinessCustomer VALUES (%s, %s)", (cust_id, name))
        
        # 2. Create Account
        cursor.execute("SELECT IFNULL(MAX(AccountNumber), 2000) + 1 FROM Account")
        acct_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO Account VALUES (%s, %s, %s, 'Business')", (acct_id, balance, date.today()))
        cursor.execute("INSERT INTO Customer_Account VALUES (%s, %s)", (cust_id, acct_id))
        
        conn.commit()
        print(f"\n[SUCCESS] Business Account #{acct_id} created for '{name}'.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()

def create_individual_account():
    print("\n--- Create Individual Account ---")
    name = input("Full Name: ")
    ssn = input("SSN (e.g. 000-00-0000): ")
    address = input("Address: ")
    
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        # 1. Create Customer
        cursor.execute("INSERT INTO Customer (CustomerType, Address) VALUES ('Individual', %s)", (address,))
        cust_id = cursor.lastrowid
        cursor.execute("INSERT INTO IndividualCustomer (CustomerID, SSN, Name) VALUES (%s, %s, %s)", (cust_id, ssn, name))
        
        # 2. Create Account ($1000 fixed)
        cursor.execute("SELECT IFNULL(MAX(AccountNumber), 1000) + 1 FROM Account")
        acct_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO Account VALUES (%s, 1000.00, %s, 'Savings')", (acct_id, date.today()))
        cursor.execute("INSERT INTO SavingsAccount VALUES (%s, 1.5)", (acct_id,))
        cursor.execute("INSERT INTO Customer_Account VALUES (%s, %s)", (cust_id, acct_id))
        
        conn.commit()
        print(f"\n[SUCCESS] Savings Account #{acct_id} created for '{name}' with $1000.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()

def issue_loan():
    print("\n--- Issue Loan ---")
    try:
        cust_id = int(input("Customer ID: "))
        branch = input("Branch Name: ")
    except ValueError:
        print("Invalid input.")
        return

    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT IFNULL(MAX(LoanNumber), 5000) + 1 FROM Loan")
        loan_id = cursor.fetchone()[0]
        
        # Fixed $20,000 Amount
        cursor.execute("INSERT INTO Loan VALUES (%s, 20000.00, %s)", (loan_id, branch))
        cursor.execute("INSERT INTO Customer_Loan VALUES (%s, %s)", (cust_id, loan_id))
        
        conn.commit()
        print(f"\n[SUCCESS] Loan #{loan_id} of $20,000 issued to Customer ID {cust_id}.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()

# --- REPORTS ---
def generate_reports():
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    
    print("\n--- GENERATE REPORTS ---")
    print("1. Branch Information & Loans")
    print("2. Top 5 Personal Bankers")
    print("3. Top 5 High-Debt Accounts")
    choice = input("Select Report (1-3): ")

    try:
        if choice == '1':
            print("\n--- Branch Report ---")
            print(f"{'Branch':<15} {'CustID':<8} {'Type':<12} {'LoanAmt':<10}")
            print("-" * 50)
            cursor.execute("""
                SELECT b.BranchName, c.CustomerID, c.CustomerType, l.Amount 
                FROM Branch b
                JOIN Loan l ON b.BranchName = l.BranchName
                JOIN Customer_Loan cl ON l.LoanNumber = cl.LoanNumber
                JOIN Customer c ON cl.CustomerID = c.CustomerID
            """)
            for row in cursor.fetchall():
                print(f"{row[0]:<15} {row[1]:<8} {row[2]:<12} {row[3]:<10}")

        elif choice == '2':
            print("\n--- Top 5 Personal Bankers ---")
            print(f"{'Banker Name':<20} {'Managed Assets':<15}")
            print("-" * 40)
            cursor.execute("""
                SELECT e.Name, SUM(a.Balance) as ManagedAssets
                FROM Employee e
                JOIN IndividualCustomer ic ON e.SSN = ic.PersonalBankerSSN
                JOIN Customer_Account ca ON ic.CustomerID = ca.CustomerID
                JOIN Account a ON ca.AccountNumber = a.AccountNumber
                GROUP BY e.SSN, e.Name
                ORDER BY ManagedAssets DESC LIMIT 5
            """)
            for row in cursor.fetchall():
                print(f"{row[0]:<20} ${row[1]:,.2f}")

        elif choice == '3':
            print("\n--- Top 5 High-Debt Accounts ---")
            print(f"{'Loan #':<10} {'Branch':<15} {'Remaining Debt':<15}")
            print("-" * 45)
            cursor.execute("""
                SELECT l.LoanNumber, l.BranchName, (l.Amount - IFNULL(SUM(lp.PaymentAmount), 0)) as Debt
                FROM Loan l
                LEFT JOIN Loan_Payment lp ON l.LoanNumber = lp.LoanNumber
                GROUP BY l.LoanNumber, l.BranchName
                ORDER BY Debt DESC LIMIT 5
            """)
            for row in cursor.fetchall():
                print(f"{row[0]:<10} {row[1]:<15} ${row[2]:,.2f}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()
        input("\nPress Enter to return to menu...")

# --- MAIN MENU ---
def main():
    while True:
        print("\n=== CSE 5330 BANKING SYSTEM (CLI) ===")
        print("1. Create Business Account")
        print("2. Create Individual Account")
        print("3. Issue Loan ($20,000)")
        print("4. Generate Reports")
        print("5. Exit")
        
        choice = input("Enter choice: ")
        
        if choice == '1': create_business_account()
        elif choice == '2': create_individual_account()
        elif choice == '3': issue_loan()
        elif choice == '4': generate_reports()
        elif choice == '5': 
            print("Exiting system.")
            sys.exit()
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
