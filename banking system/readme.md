# CSE 5330: Banking Database System

**Course:** CSE 5330 - Database Systems (Fall 2023)
**Project:** #2 - Banking System Design & Implementation
**Tech Stack:** Python (CLI), MySQL

## Project Description
This project implements a full banking database system as required for the CSE 5330 coursework. It includes an EER-to-Relational database mapping, a normalized MySQL schema, and a Python-based Command Line Interface (CLI) for handling bank transactions and generating managerial reports.

## Features
* **Relational Database Design:** A robust schema handling Branches, Employees, Customers (Individual/Business), Accounts (Savings/Checking), and Loans.
* **Data Integrity:** Implements complex constraints, Foreign Keys, and Triggers (e.g., monitoring balance drops below $1000).
* **Interactive CLI:** A menu-driven Python interface to perform transactions without SQL knowledge.
* **Managerial Reporting:** Automated generation of complex reports:
    * Top 5 Personal Bankers by managed assets.
    * Top 5 High-Debt accounts.
    * Branch-wise loan summaries.

## How to Run

### Prerequisites
* MySQL Server 8.0
* Python 3.9+
* `mysql-connector-python`

### Installation
1.  **Setup Database:**
    Run the `schema.sql` script in your MySQL interface to create the tables and triggers:
    ```bash
    mysql -u root -p < schema.sql
    ```

2.  **Populate Dummy Data:**
    Run the Python script to generate 10 branches, 40 employees, and initial account data:
    ```bash
    python3 populate_data.py
    ```

3.  **Launch Application:**
    Start the banking interface:
    ```bash
    python3 banking_cli.py
    ```

## Transactions Supported
1.  **Create Accounts:** Supports opening both Business and Individual accounts (with initial deposit constraints).
2.  **Loan Processing:** Interface for issuing loans linked to specific branches and customers.
3.  **Reporting:** View real-time database statistics via the "Generate Reports" menu.


## 📸 Usage Demo

### 1. Main Menu Interface
The application launches a robust Command Line Interface (CLI) for easy navigation.
=== CSE 5330 BANKING SYSTEM (CLI) ===
1. Create Business Account
2. Create Individual Account
3. Issue Loan ($20,000)
4. Generate Reports
5. Exit
Enter choice: 

### 2. Transaction Example: Creating an Account
Managers can create new accounts with automatic validation constraints.
```text

--- Create Individual Account ---
Full Name: Pratyusha Adibhatla
SSN (e.g. 000-00-0000): 123-45-6780
Address: ncnhdfjkjiue

[SUCCESS] Savings Account #1021 created for 'Pratyusha Adibhatla' with $1000.
---
*Submitted for CSE 5330, Fall 2023.*