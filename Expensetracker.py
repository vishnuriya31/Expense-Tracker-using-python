import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import sys

def settle_balances(balances):
    """
    Compute settlement transactions from net balances.
    Positive balance means the member should receive money,
    negative balance means the member owes money.
    """
    creditors = [(person, amount) for person, amount in balances.items() if amount > 0]
    debtors = [(person, -amount) for person, amount in balances.items() if amount < 0]
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)

    transactions = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor, debt = debtors[i]
        creditor, credit = creditors[j]
        payment = min(debt, credit)
        transactions.append((debtor, creditor, payment))
        # Update remaining amounts
        debtors[i] = (debtor, debt - payment)
        creditors[j] = (creditor, credit - payment)
        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1
    return transactions

class ExpenseSplitterGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Expense Splitter")

        # Ask for group members using a simple dialog.
        self.members = self.ask_members()
        if not self.members:
            messagebox.showerror("Error", "No members entered. Exiting.")
            sys.exit(0)

        # Initialize net balances and expense records.
        self.balances = {member: 0.0 for member in self.members}
        self.expenses = []

        # Build the GUI components.
        self.create_widgets()

    def ask_members(self):
        # Prompt the user to input group members separated by commas.
        members_str = simpledialog.askstring("Group Members", "Enter the names of group members separated by commas:")
        if members_str:
            members = [name.strip() for name in members_str.split(",") if name.strip()]
            return members
        else:
            return []

    def create_widgets(self):
        # --- Add Expense Section ---
        add_frame = tk.LabelFrame(self.master, text="Add Expense", padx=10, pady=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        # Payer selection (dropdown)
        tk.Label(add_frame, text="Payer:").grid(row=0, column=0, sticky="e")
        self.payer_var = tk.StringVar(value=self.members[0])
        self.payer_menu = ttk.OptionMenu(add_frame, self.payer_var, self.members[0], *self.members)
        self.payer_menu.grid(row=0, column=1, sticky="w")

        # Amount entry field
        tk.Label(add_frame, text="Amount:").grid(row=1, column=0, sticky="e")
        self.amount_entry = tk.Entry(add_frame)
        self.amount_entry.grid(row=1, column=1, sticky="w")

        # Expense description field
        tk.Label(add_frame, text="Description:").grid(row=2, column=0, sticky="e")
        self.desc_entry = tk.Entry(add_frame)
        self.desc_entry.grid(row=2, column=1, sticky="w")

        # Button to add expense
        add_button = tk.Button(add_frame, text="Add Expense", command=self.add_expense)
        add_button.grid(row=3, column=0, columnspan=2, pady=5)

        # --- Current Balances Section ---
        balance_frame = tk.LabelFrame(self.master, text="Current Balances", padx=10, pady=10)
        balance_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.balance_text = tk.Text(balance_frame, height=10, width=50, state="disabled")
        self.balance_text.pack()

        # --- Settle Up Section ---
        settle_frame = tk.LabelFrame(self.master, text="Settle Up", padx=10, pady=10)
        settle_frame.pack(fill="both", expand=True, padx=10, pady=5)

        settle_button = tk.Button(settle_frame, text="Compute Settlements", command=self.compute_settlements)
        settle_button.pack(pady=5)

        self.settle_text = tk.Text(settle_frame, height=10, width=50, state="disabled")
        self.settle_text.pack()

        # Display initial balances.
        self.update_balances_display()

    def add_expense(self):
        payer = self.payer_var.get()
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid numeric amount.")
            return

        description = self.desc_entry.get()
        expense = {"payer": payer, "amount": amount, "description": description}
        self.expenses.append(expense)

        # Split the expense equally among all members.
        split = amount / len(self.balances)
        for member in self.balances:
            if member == payer:
                self.balances[member] += (amount - split)
            else:
                self.balances[member] -= split

        messagebox.showinfo("Expense Added", "Expense added successfully!")
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.update_balances_display()

    def update_balances_display(self):
        self.balance_text.config(state="normal")
        self.balance_text.delete("1.0", tk.END)
        for member, balance in self.balances.items():
            if balance > 0:
                self.balance_text.insert(tk.END, f"{member} should receive: ${balance:.2f}\n")
            elif balance < 0:
                self.balance_text.insert(tk.END, f"{member} owes: ${-balance:.2f}\n")
            else:
                self.balance_text.insert(tk.END, f"{member} is settled.\n")
        self.balance_text.config(state="disabled")

    def compute_settlements(self):
        transactions = settle_balances(self.balances)
        self.settle_text.config(state="normal")
        self.settle_text.delete("1.0", tk.END)
        if not transactions:
            self.settle_text.insert(tk.END, "Everyone is settled up!\n")
        else:
            for debtor, creditor, amount in transactions:
                self.settle_text.insert(tk.END, f"{debtor} pays {creditor}: ${amount:.2f}\n")
        self.settle_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseSplitterGUI(root)
    root.mainloop()
