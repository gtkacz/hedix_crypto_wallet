# 🚀 Coding Exercise: The Simple Crypto Wallet

# To run:

1. Install the requirements on `requirements.txt` with whichever package manager you use.
2. Try `python src/cli.py`. If this throws import errors, try installing the `ipython` package and run `ipython src/main.py` instead.

Thank you for your interest in joining our team. We've designed a small coding exercise that
helps us understand how you approach problems, design software, and write code. This isn't a
pass/fail test but rather a starting point for our next conversation.

## 1. Problem Statement

You are tasked with building a simple **crypto wallet** that tracks the balance of various assets.
The wallet starts with no assets and processes a list of transactions to determine its final state.
The wallet must handle three types of assets: **BTC** , **ETH** , and **USD**.

**Transactions**

The input to your program will be an **initial state** (which you can assume is always an empty
wallet) and a **list of transactions**.

A transaction has three properties:

- **Type:** DEPOSIT or WITHDRAW
- **Asset:** BTC, ETH, or USD
- **Amount:** A positive decimal number

**Commands & Rules**

Your program must process the transactions **in the order they are given**.

1. **DEPOSIT:** A DEPOSIT always succeeds. It **adds** the specified amount to the wallet's
    balance for that asset.
2. **WITHDRAW:** A WITHDRAW is conditional.
    ○ **Rule:** A withdrawal can **only** be processed if the wallet holds **sufficient funds**
    ○ **Success:** If the wallet has sufficient funds, the amount is **subtracted** from the
       balance.
    ○ **Failure:** If the wallet has insufficient funds, the **entire transaction is ignored**.
       The wallet's balance remains unchanged, and the program moves to the next
       transaction.

**Objective**

Write a program that takes a list of transactions and calculates the **final balance** of all assets in
the wallet. The program should output the final state of the wallet, showing the quantity of each
asset.

**Example Run**
- **Initial State:** BTC: 0 , ETH: 0 , USD: 0
- **Transactions List:**


1. DEPOSIT BTC 1.

2. DEPOSIT USD 1000

3. WITHDRAW USD 300

4. WITHDRAW BTC 2.

5. DEPOSIT ETH 5.

6. WITHDRAW BTC 0.

**Execution:**

1. **Start:** BTC: 0 , ETH: 0 , USD: 0
2. DEPOSIT BTC 1.5: BTC: 1.5, ETH: 0 , USD: 0
3. DEPOSIT USD 1000 : BTC: 1.5, ETH: 0 , USD: 1000
4. WITHDRAW USD 300 : BTC: 1.5, ETH: 0 , USD: 700
5. WITHDRAW BTC 2.0: BTC: 1.5, ETH: 0 , USD: 700
6. DEPOSIT ETH 5.0: BTC: 1.5, ETH: 5.0, USD: 700
7. WITHDRAW BTC 0.5: BTC: 1.0, ETH: 5.0, USD: 700

**Expected Output:** BTC: 1.0, ETH: 5.0, USD: 700.

## 2. Instructions & Evaluation

- **Language:** You can solve this problem in any programming language you are comfortable with.
- **Scope:** The solution should be a simple **console/terminal application**. You don't need to build a web API, a user interface, or a database. How you handle the input (e.g., hard-coded in your main function, read from a file) is up to you. A couple of hours should be more than enough to complete the core problem.

- **Deliverable:** Please provide your solution as a runnable project (e.g., a link to a Git repository). It should include all code and tests.

**What We're Looking For**

We are far more interested in **how you think and work** than in a "perfect" or complex solution.
The problem is **intentionally small and simple**. We want you to build a solid foundation that we
can use as a starting point for our technical discussion.
During our follow-up interview, we will:

1. **Discuss Your Design:** We'll ask you to walk us through your solution, including your approach to software design (e.g., object-oriented principles) and why you structured it the way you did. We value clean, readable code that is easy to maintain.

2. **Evolve the Code:** This is the most important part. We will **work together on extensions** to this base problem. Your solution is the "launch pad" for this collaborative session.

3. **Talk About Testing:** How did you verify your solution? We value well-tested code, so please include any tests you wrote to ensure your logic is correct.