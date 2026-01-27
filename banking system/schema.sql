-- Create and select the database
CREATE DATABASE IF NOT EXISTS bank_db;
USE bank_db;

-- 1. Branches
CREATE TABLE Branch (
    BranchName VARCHAR(100) PRIMARY KEY,
    City VARCHAR(100),
    Assets DECIMAL(15, 2)
);

-- 2. Employees
CREATE TABLE Employee (
    SSN VARCHAR(11) PRIMARY KEY,
    Name VARCHAR(100),
    Address VARCHAR(255),
    Phone VARCHAR(15),
    StartDate DATE,
    EmploymentLength INT, -- In months
    ManagerSSN VARCHAR(11),
    CONSTRAINT fk_manager FOREIGN KEY (ManagerSSN) REFERENCES Employee(SSN)
);

-- 3. Employee Dependents
CREATE TABLE Dependent (
    EmployeeSSN VARCHAR(11),
    DependentName VARCHAR(100),
    PRIMARY KEY (EmployeeSSN, DependentName),
    FOREIGN KEY (EmployeeSSN) REFERENCES Employee(SSN) ON DELETE CASCADE
);

-- 4. Customers (Supertype)
CREATE TABLE Customer (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerType ENUM('Individual', 'Business') NOT NULL,
    Address VARCHAR(255)
);

-- 5. Individual Customers
CREATE TABLE IndividualCustomer (
    CustomerID INT PRIMARY KEY,
    SSN VARCHAR(11) UNIQUE,
    Name VARCHAR(100),
    PersonalBankerSSN VARCHAR(11),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (PersonalBankerSSN) REFERENCES Employee(SSN)
);

-- 6. Business Customers
CREATE TABLE BusinessCustomer (
    CustomerID INT PRIMARY KEY,
    BusinessName VARCHAR(100),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE
);

-- 7. Accounts
CREATE TABLE Account (
    AccountNumber INT PRIMARY KEY,
    Balance DECIMAL(15, 2),
    LastAccessDate DATE,
    AccountType ENUM('Savings', 'Checking', 'Business')
);

-- 8. Savings Account Specifics
CREATE TABLE SavingsAccount (
    AccountNumber INT PRIMARY KEY,
    InterestRate DECIMAL(5, 2),
    FOREIGN KEY (AccountNumber) REFERENCES Account(AccountNumber) ON DELETE CASCADE
);

-- 9. Checking Account Specifics
CREATE TABLE CheckingAccount (
    AccountNumber INT PRIMARY KEY,
    OverdraftAmount DECIMAL(10, 2),
    FOREIGN KEY (AccountNumber) REFERENCES Account(AccountNumber) ON DELETE CASCADE
);

-- 10. Customer Accounts (Many-to-Many)
CREATE TABLE Customer_Account (
    CustomerID INT,
    AccountNumber INT,
    PRIMARY KEY (CustomerID, AccountNumber),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (AccountNumber) REFERENCES Account(AccountNumber)
);

-- 11. Loans
CREATE TABLE Loan (
    LoanNumber INT PRIMARY KEY,
    Amount DECIMAL(15, 2),
    BranchName VARCHAR(100),
    FOREIGN KEY (BranchName) REFERENCES Branch(BranchName)
);

-- 12. Customer Loans (Many-to-Many)
CREATE TABLE Customer_Loan (
    CustomerID INT,
    LoanNumber INT,
    PRIMARY KEY (CustomerID, LoanNumber),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (LoanNumber) REFERENCES Loan(LoanNumber)
);

-- 13. Loan Payments (Weak Entity)
CREATE TABLE Loan_Payment (
    LoanNumber INT,
    PaymentNumber INT,
    PaymentDate DATE,
    PaymentAmount DECIMAL(15, 2),
    PRIMARY KEY (LoanNumber, PaymentNumber),
    FOREIGN KEY (LoanNumber) REFERENCES Loan(LoanNumber) ON DELETE CASCADE
);

-- Table to store notifications
CREATE TABLE Notifications (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Message VARCHAR(255),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$

-- Trigger 1: Notify if balance falls below $1000
CREATE TRIGGER CheckBalanceLow
AFTER UPDATE ON Account
FOR EACH ROW
BEGIN
    IF NEW.Balance < 1000 THEN
        INSERT INTO Notifications (Message) 
        VALUES (CONCAT('Alert: Account ', NEW.AccountNumber, ' balance dropped below $1000. Interest rate may change.'));
    END IF;
END$$

-- Trigger 2: Log manager updates
CREATE TRIGGER AuditManagerUpdate
AFTER UPDATE ON Employee
FOR EACH ROW
BEGIN
    IF OLD.ManagerSSN != NEW.ManagerSSN THEN
        INSERT INTO Notifications (Message)
        VALUES (CONCAT('Manager changed for Employee ', NEW.SSN, ' from ', OLD.ManagerSSN, ' to ', NEW.ManagerSSN));
    END IF;
END$$

DELIMITER ;