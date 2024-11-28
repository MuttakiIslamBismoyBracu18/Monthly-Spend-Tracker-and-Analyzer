from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QLabel, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QHBoxLayout, QComboBox, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd


class SpendTrackerController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.tabs.setCurrentIndex(0)

        self.view.upload_button.clicked.connect(self.upload_data)
        self.view.add_expense_button.clicked.connect(self.add_expense)
        self.view.show_summary_button.clicked.connect(self.show_summary_buttons)
        self.view.delete_row_button.clicked.connect(self.delete_row)
        self.view.delete_all_button.clicked.connect(self.delete_all_data)
        self.view.credit_limit_button.clicked.connect(self.manage_credit_limits)

        self.view.summary_button_month_vs_spend.clicked.connect(self.show_month_vs_spend_chart)
        self.view.summary_button_category_spend.clicked.connect(self.show_category_spend_chart)
        self.view.summary_button_credit_usage.clicked.connect(self.show_credit_usage_chart)
        self.view.summary_button_category_table.clicked.connect(self.show_category_table)
        self.view.summary_button_spender_table.clicked.connect(self.show_spender_table)
        self.view.summary_button_card_table.clicked.connect(self.show_card_table)
        self.view.summary_button_trends.clicked.connect(self.show_expense_trends)
        self.view.summary_button_forecast.clicked.connect(self.show_forecasted_expenses)

        self.view.summary_button_layout.addWidget(self.view.show_summary_button)
        

        self.view.budget_button_set_limit.clicked.connect(self.set_budget_limit)
        self.view.budget_button_summary.clicked.connect(self.show_budget_summary)

        self.view.insights_button_top_categories.clicked.connect(self.show_top_categories_chart)
        self.view.insights_button_top_spenders.clicked.connect(self.show_top_spenders_chart)
        self.view.insights_button_high_expense_days.clicked.connect(self.show_high_expense_days_table)


        self.enable_manual_edit()

        self.refresh_table()

    def refresh_table(self):
        data = self.model.load_data()
        self.view.table.setRowCount(len(data))
        for i, row in data.iterrows():
            for j, value in enumerate(row):
                if isinstance(value, float):
                    self.view.table.setItem(i, j, QTableWidgetItem(f"{value:.2f}"))
                else:
                    self.view.table.setItem(i, j, QTableWidgetItem(str(value)))

    def enable_manual_edit(self):
        self.view.table.setEditTriggers(self.view.table.AllEditTriggers)
        self.view.table.itemChanged.connect(self.save_manual_changes)

    def save_manual_changes(self, item):
        row, col = item.row(), item.column()
        value = item.text()
        data = self.model.load_data()

        try:
            if col < len(self.model.columns):
                if data.dtypes.iloc[col] == "float64":
                    data.iat[row, col] = float(value) 
                elif data.dtypes.iloc[col] == "int64":
                    data.iat[row, col] = int(value)
                else:
                    data.iat[row, col] = value 
            self.model.save_data(data)
        except ValueError as e:
            QMessageBox.warning(self.view, "Error", f"Invalid input: {e}")
            self.refresh_table()

    def upload_data(self):
        file_path = self.view.open_file_dialog()
        if file_path:
            try:
                if file_path.endswith(".csv"):
                    data = pd.read_csv(file_path)
                elif file_path.endswith(".xlsx"):
                    data = pd.read_excel(file_path)
                else:
                    QMessageBox.warning(self.view, "Error", "Unsupported file type!")
                    return

                self.model.save_data(data)

                unique_sources = data["Source"].unique()
                for source in unique_sources:
                    if source.lower() != "cash" and "debit" not in source.lower():
                        if source not in self.model.credit_limits:
                            limit, ok = self.view.ask_for_card_limit(source)
                            if ok:
                                self.model.add_credit_limit(source, float(limit))  # Cast to float

                self.refresh_table()
            except Exception as e:
                QMessageBox.warning(self.view, "Error", f"Failed to load data: {e}")


    def add_expense(self):
        dialog = self.view.open_add_expense_dialog(
            sources=list(self.model.credit_limits.keys()),
            categories=["Food", "Rent", "Car", "Grocery", "Shopping", "OTT", "Tour", "Job", "Miscellaneous"],
            spenders=["Muttaki", "Sum"]
        )
        if dialog.exec_():
            date = f"{dialog.year_input.currentText()}-{dialog.month_input.currentText()}-{dialog.day_input.currentText()}"
            new_row = {
                "Date": date,
                "Source": dialog.source_input.currentText(),
                "Description": dialog.description_input.text(),
                "Category": dialog.category_input.currentText(),
                "Spender": dialog.spender_input.currentText(),
                "Amount": float(dialog.amount_input.text())
            }
            data = self.model.load_data()
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
            self.model.save_data(data)

            self.refresh_table()

    def delete_row(self):

        selected_row = self.view.table.currentRow()
        if selected_row >= 0:
            data = self.model.load_data()
            data = data.drop(index=selected_row).reset_index(drop=True)
            self.model.save_data(data)
            self.refresh_table()

    def delete_all_data(self):
        confirmation = QMessageBox.question(
            self.view, "Confirm Delete", "Are you sure you want to delete all data?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.Yes:
            self.model.clear_data()
            self.refresh_table()

    def manage_credit_limits(self):
        dialog = QDialog(self.view)
        dialog.setWindowTitle("Manage Credit/Debit Cards")
        layout = QVBoxLayout(dialog)

        form_layout = QFormLayout()
        card_name_input = QLineEdit()
        card_limit_input = QLineEdit()
        card_limit_input.setPlaceholderText("Enter limit (e.g., 5000)")

        form_layout.addRow("Card Name:", card_name_input)
        form_layout.addRow("Card Limit:", card_limit_input)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add/Update Card")
        delete_button = QPushButton("Delete Card")
        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)

        cards_combo = QComboBox()
        cards_combo.addItems(list(self.model.credit_limits.keys()))
        cards_combo.setEditable(True)

        cards_combo.currentIndexChanged.connect(
            lambda: card_limit_input.setText(
                str(self.model.credit_limits.get(cards_combo.currentText(), ""))
            )
        )

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addWidget(QLabel("Existing Cards:"))
        layout.addWidget(cards_combo)

        add_button.clicked.connect(lambda: self.add_or_update_card(card_name_input, card_limit_input, dialog))
        delete_button.clicked.connect(lambda: self.delete_card(cards_combo, dialog))

        dialog.setLayout(layout)
        dialog.exec_()

    def add_or_update_card(self, card_name_input, card_limit_input, dialog):
        card_name = card_name_input.text().strip()
        try:
            card_limit = float(card_limit_input.text())
            if card_name:
                self.model.add_credit_limit(card_name, card_limit)
                QMessageBox.information(dialog, "Success", f"Card '{card_name}' updated successfully.")
            else:
                QMessageBox.warning(dialog, "Error", "Card name cannot be empty.")
        except ValueError:
            QMessageBox.warning(dialog, "Error", "Invalid limit. Please enter a numeric value.")

    def delete_card(self, cards_combo, dialog):
        card_name = cards_combo.currentText().strip()
        if card_name:
            self.model.delete_credit_card(card_name)
            QMessageBox.information(dialog, "Success", f"Card '{card_name}' deleted successfully.")

    def enable_manual_edit(self):
        self.view.table.setEditTriggers(self.view.table.AllEditTriggers)
        self.view.table.itemChanged.connect(self.save_manual_changes)

    def save_manual_changes(self, item):
        row, col = item.row(), item.column()
        value = item.text()
        data = self.model.load_data()

        try:
            if col < len(self.model.columns):
                if data.dtypes.iloc[col] == "float64":
                    data.iat[row, col] = float(value)
                elif data.dtypes.iloc[col] == "int64":
                    data.iat[row, col] = int(value)
                else:
                    data.iat[row, col] = value
            self.model.save_data(data)
        except ValueError as e:
            QMessageBox.warning(self.view, "Error", f"Invalid input: {e}")
            self.refresh_table()

    def show_summary_buttons(self):
        self.view.clear_summary_scroll()
        self.view.summary_scroll.setMinimumHeight(400)  # Allows resizing manually
        self.view.summary_scroll.setMinimumWidth(600)
        label = QLabel("Click a button to view specific charts or tables.")
        self.view.summary_scroll_layout.addWidget(label)

    def show_month_vs_spend_chart(self):
        data = self.model.load_data()
        data["Date"] = pd.to_datetime(data["Date"])
        month_expense = data.groupby(data["Date"].dt.to_period("M"))["Amount"].sum()

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.bar(month_expense.index.astype(str), month_expense.values, color="skyblue")
        ax.set_title("Month vs Spend")
        ax.set_xlabel("Month")
        ax.set_ylabel("Expense")
        canvas = FigureCanvas(fig)

        self.view.clear_summary_scroll()
        self.view.add_chart_to_summary("Month vs Spend", canvas)

    def show_category_spend_chart(self):
        data = self.model.load_data()
        category_expense = data.groupby("Category")["Amount"].sum()

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.pie(
            category_expense.values,
            labels=category_expense.index,
            autopct='%1.1f%%',
            startangle=140,
            textprops={'fontsize': 8} 
        )
        ax.set_title("Category-wise Spend", fontsize=16) 
        canvas = FigureCanvas(fig)

        self.view.clear_summary_scroll()
        self.view.add_chart_to_summary("Category-wise Spend", canvas)

    def show_credit_usage_chart(self):
        credit_summary = self.model.calculate_credit_summary()

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        cards = list(credit_summary.keys())
        used = [credit_summary[card]["Used"] for card in cards]
        remaining = [credit_summary[card]["Remaining"] for card in cards]

        bar_width = 0.4
        x = range(len(cards))
        ax.bar(x, used, bar_width, label="Used Credit", color="tomato")
        ax.bar(x, remaining, bar_width, bottom=used, label="Available Credit", color="lightgreen")
        ax.set_xticks(x)
        ax.set_xticklabels(cards, rotation=45)
        ax.set_title("Credit Card Usage")
        ax.legend()
        canvas = FigureCanvas(fig)

        self.view.clear_summary_scroll()
        self.view.add_chart_to_summary("Credit Card Usage", canvas)

    def show_category_table(self):
        data = self.model.load_data()
        data["Date"] = pd.to_datetime(data["Date"])
        category_table = data.groupby(["Category", data["Date"].dt.to_period("M")])["Amount"].sum().unstack(fill_value=0)
        category_table = category_table.astype(float).round(2)
        self.view.clear_summary_scroll()
        self.view.add_table_to_summary("Category-wise Expense by Month", category_table)

    def show_spender_table(self):
        data = self.model.load_data()
        data["Date"] = pd.to_datetime(data["Date"])
        spender_table = data.groupby(["Spender", data["Date"].dt.to_period("M")])["Amount"].sum().unstack(fill_value=0)
        spender_table = spender_table.astype(float).round(2)
        self.view.clear_summary_scroll()
        self.view.add_table_to_summary("Spender-wise Expense by Month", spender_table)

    def show_card_table(self):
        data = self.model.load_data()
        data["Date"] = pd.to_datetime(data["Date"])
        card_table = data.groupby(["Source", data["Date"].dt.to_period("M")])["Amount"].sum().unstack(fill_value=0)
        card_table = card_table.astype(float).round(2)
        self.view.clear_summary_scroll()
        self.view.add_table_to_summary("Card-wise Expense by Month", card_table)


    def show_expense_trends(self):
        trends = self.model.calculate_expense_trends()

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.plot(trends.index.astype(str), trends.values, marker="o", linestyle="-", color="blue")
        ax.set_title("Monthly Expense Trends")
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Expense")
        ax.grid(True)

        canvas = FigureCanvas(fig)
        self.view.clear_summary_scroll()
        self.view.add_chart_to_summary("Expense Trends", canvas)

    def show_forecasted_expenses(self):
        trends = self.model.calculate_expense_trends()
        forecast = self.model.forecast_expenses(months_ahead=3)

        if not forecast:
            QMessageBox.warning(self.view, "Insufficient Data", "Not enough data to forecast expenses.")
            return

        forecast_months = list(forecast.keys())
        forecast_values = list(forecast.values())

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        ax.plot(trends.index.astype(str), trends.values, marker="o", linestyle="-", label="Historical", color="blue")
        ax.plot(forecast_months, forecast_values, marker="x", linestyle="--", label="Forecasted", color="orange")

        ax.set_title("Expense Trends & Forecasting")
        ax.set_xlabel("Month")
        ax.set_ylabel("Expense")
        ax.legend()
        ax.grid(True)

        canvas = FigureCanvas(fig)
        self.view.clear_summary_scroll()
        self.view.add_chart_to_summary("Expense Forecasting", canvas)

    def show_top_categories_chart(self):
        data = self.model.load_data()
        category_expense = data.groupby("Category")["Amount"].sum().sort_values(ascending=False).head(5)

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.bar(category_expense.index, category_expense.values, color="coral")
        ax.set_title("Top Spending Categories")
        ax.set_xlabel("Category")
        ax.set_ylabel("Total Expense")
        ax.tick_params(axis='x', rotation=45)
        canvas = FigureCanvas(fig)

        self.view.clear_insights_scroll()
        self.view.add_chart_to_insights("Top Spending Categories", canvas)

    def show_top_spenders_chart(self):
        data = self.model.load_data()
        spender_expense = data.groupby("Spender")["Amount"].sum()

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.pie(
            spender_expense.values,
            labels=spender_expense.index,
            autopct='%1.1f%%',
            startangle=140,
            textprops={'fontsize': 8}
        )
        ax.set_title("Top Spenders")
        canvas = FigureCanvas(fig)

        self.view.clear_insights_scroll()
        self.view.add_chart_to_insights("Top Spenders", canvas)

    def show_high_expense_days_table(self):
        data = self.model.load_data()
        data["Date"] = pd.to_datetime(data["Date"])
        high_expense_days = data.groupby("Date")["Amount"].sum().sort_values(ascending=False).head(5).reset_index()

        high_expense_days.rename(columns={"Date": "Date", "Total Expense": "Amount"}, inplace=True)
        high_expense_days["Date"] = high_expense_days["Date"].dt.strftime("%Y-%m-%d")

        self.view.clear_insights_scroll()
        self.view.add_table_to_insights("High-Expense Days", high_expense_days)

    def set_budget_limit(self):
        data = self.model.load_data()
        categories = data["Category"].unique().tolist()

        dialog = self.view.open_budget_limit_dialog(categories)
        if dialog.exec_():
            category = dialog.category_input.currentText()
            try:
                limit = float(dialog.limit_input.text())
                self.model.set_budget_limit(category, limit)
            except ValueError:
                QMessageBox.warning(self.view, "Error", "Please enter a valid numeric limit.")

    def show_budget_summary(self):
        data = self.model.load_data()
        data["Date"] = pd.to_datetime(data["Date"])
        latest_month = data["Date"].dt.to_period("M").max()
        latest_month_data = data[data["Date"].dt.to_period("M") == latest_month]
        budget_summary = self.model.calculate_budget_summary(latest_month_data)

        self.view.clear_budget_scroll()
        self.view.add_budget_summary(budget_summary)

