import pandas as pd
import os
import json
import numpy as np


class SpendTrackerModel:
    def __init__(self):
        self.data_file = "spend_data.csv"  
        self.credit_limits_file = "credit_limits.json"
        self.columns = ["Date", "Source", "Description", "Category", "Spender", "Amount"]  # Column names
        self.credit_limits = self._load_credit_limits()
        self.budget_file = "budget_limits.json"
        self.budgets = self._load_budget_limits()

        if not os.path.exists(self.data_file):
            self._initialize_data()

    def _initialize_data(self):
        df = pd.DataFrame(columns=self.columns)
        df.to_csv(self.data_file, index=False)

    def _load_credit_limits(self):
        if os.path.exists(self.credit_limits_file):
            with open(self.credit_limits_file, "r") as file:
                return json.load(file)
        return {}
    
    def _save_credit_limits(self):
        with open(self.credit_limits_file, "w") as file:
            json.dump(self.credit_limits, file, indent=4)

    def load_data(self):
        return pd.read_csv(self.data_file)

    def save_data(self, data):
        data.to_csv(self.data_file, index=False)

    def clear_data(self):
        df = pd.DataFrame(columns=self.columns)
        self.save_data(df)

    def add_credit_limit(self, card, limit):
        self.credit_limits[card] = limit
        self._save_credit_limits()

    def delete_credit_card(self, card):
        if card in self.credit_limits:
            del self.credit_limits[card]
            self._save_credit_limits()

    def calculate_credit_summary(self):
        data = self.load_data()
        credit_usage = data.groupby("Source")["Amount"].sum().to_dict()
        credit_summary = {
            card: {
                "Used": credit_usage.get(card, 0),
                "Remaining": self.credit_limits.get(card, 0) - credit_usage.get(card, 0)
            }
            for card in self.credit_limits
        }
        return credit_summary

    def calculate_totals(self):
        data = self.load_data()
        total_expense = data["Amount"].sum()
        spender_expense = data.groupby("Spender")["Amount"].sum().to_dict()
        category_expense = data.groupby("Category")["Amount"].sum().to_dict()
        return total_expense, spender_expense, category_expense

    def calculate_monthly_expenses(self):
        data = self.load_data()
        data["Date"] = pd.to_datetime(data["Date"])
        return data.groupby(data["Date"].dt.to_period("M"))["Amount"].sum()

    def calculate_monthly_category_expenses(self):
        data = self.load_data()
        data["Date"] = pd.to_datetime(data["Date"])
        data["Month"] = data["Date"].dt.to_period("M")
        return data.groupby(["Month", "Category"])["Amount"].sum().unstack(fill_value=0)

    def calculate_monthly_spender_expenses(self):
        data = self.load_data()
        data["Date"] = pd.to_datetime(data["Date"])
        data["Month"] = data["Date"].dt.to_period("M")
        return data.groupby(["Month", "Spender"])["Amount"].sum().unstack(fill_value=0)

    def calculate_monthly_card_expenses(self):
        data = self.load_data()
        data["Date"] = pd.to_datetime(data["Date"])
        data["Month"] = data["Date"].dt.to_period("M")
        return data.groupby(["Month", "Source"])["Amount"].sum().unstack(fill_value=0)
    
    def calculate_expense_trends(self):
        data = self.load_data()
        data["Date"] = pd.to_datetime(data["Date"])
        return data.groupby(data["Date"].dt.to_period("M"))["Amount"].sum()

    def forecast_expenses(self, months_ahead=3):
        trends = self.calculate_expense_trends()
        X = np.arange(len(trends))
        y = trends.values

        if len(X) < 2: 
            return None

        # Calculate coefficients for linear regression
        X_mean = np.mean(X)
        y_mean = np.mean(y)
        slope = np.sum((X - X_mean) * (y - y_mean)) / np.sum((X - X_mean) ** 2)
        intercept = y_mean - slope * X_mean

        # Forecast future expenses
        future_indices = np.arange(len(trends), len(trends) + months_ahead)
        predictions = slope * future_indices + intercept

        forecasted_months = [(trends.index[-1] + i).strftime("%Y-%m") for i in range(1, months_ahead + 1)]
        return dict(zip(forecasted_months, predictions))
    
    def _load_budget_limits(self):
        if os.path.exists(self.budget_file):
            with open(self.budget_file, "r") as file:
                return json.load(file)
        return {}

    def _save_budget_limits(self):
        with open(self.budget_file, "w") as file:
            json.dump(self.budgets, file, indent=4)

    def set_budget_limit(self, category, limit):
        if not hasattr(self, 'budget_limits'):
            self.budget_limits = {}
        self.budget_limits[category] = limit

    def delete_budget_limit(self, category):
        if category in self.budgets:
            del self.budgets[category]
            self._save_budget_limits()

    def calculate_budget_usage(self):
        data = self.load_data()
        category_usage = data.groupby("Category")["Amount"].sum().to_dict()
        budget_summary = {
            category: {
                "Limit": self.budgets.get(category, None),
                "Used": category_usage.get(category, 0),
                "Remaining": max(0, self.budgets.get(category, 0) - category_usage.get(category, 0)),
                "Exceeded": category_usage.get(category, 0) > self.budgets.get(category, 0)
            }
            for category in self.budgets
        }
        return budget_summary
    
    def calculate_budget_summary(self, data):
        if not hasattr(self, 'budget_limits'):
            return {}

        category_usage = data.groupby("Category")["Amount"].sum().to_dict()
        budget_summary = {
            category: {
                "Used": category_usage.get(category, 0),
                "Limit": self.budget_limits.get(category, 0)
            }
            for category in self.budget_limits
        }
        return budget_summary
