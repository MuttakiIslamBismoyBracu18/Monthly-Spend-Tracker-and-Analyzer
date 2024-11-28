from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QTableWidget, QLabel, QTableWidgetItem,
    QPushButton, QScrollArea, QProgressBar, QFormLayout, QDialog, QInputDialog, QFileDialog, QLineEdit, QComboBox
)


class SpendTrackerView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monthly Spend Tracker")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload CSV/XLSX")
        self.add_expense_button = QPushButton("Add Expense Manually")
        self.credit_limit_button = QPushButton("Set Payment Method")
        self.show_summary_button = QPushButton("Show Summary")
        self.delete_row_button = QPushButton("Delete Selected Row")
        self.delete_all_button = QPushButton("Delete All Data")

        for btn in [
            self.upload_button, self.add_expense_button, self.credit_limit_button,
            self.show_summary_button, self.delete_row_button, self.delete_all_button
        ]:
            self.button_layout.addWidget(btn)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Source", "Description", "Category", "Spender", "Amount"])

        self.tabs = QTabWidget()

        self.summary_tab = QWidget()
        self.summary_tab_layout = QVBoxLayout(self.summary_tab)

        self.summary_button_layout = QHBoxLayout()
        self.summary_button_month_vs_spend = QPushButton("Show Month vs Spend")
        self.summary_button_category_spend = QPushButton("Show Category-wise Spend")
        self.summary_button_credit_usage = QPushButton("Show Credit Card Usage")
        self.summary_button_category_table = QPushButton("Show Category-wise Expense Table")
        self.summary_button_spender_table = QPushButton("Show Spender-wise Expense Table")
        self.summary_button_card_table = QPushButton("Show Card-wise Expense Table")
        self.summary_button_trends = QPushButton("Show Expense Trends")
        self.summary_button_forecast = QPushButton("Show Forecasted Expenses")

        

        for btn in [
            self.summary_button_month_vs_spend, self.summary_button_category_spend,
            self.summary_button_credit_usage, self.summary_button_category_table,
            self.summary_button_spender_table, self.summary_button_card_table,
            self.summary_button_trends, self.summary_button_forecast,
        ]:
            self.summary_button_layout.addWidget(btn)

        self.summary_scroll = QScrollArea()
        self.summary_scroll.setWidgetResizable(True)
        self.summary_scroll_widget = QWidget()
        self.summary_scroll_layout = QVBoxLayout(self.summary_scroll_widget)
        self.summary_scroll_widget.setLayout(self.summary_scroll_layout)
        self.summary_scroll.setWidget(self.summary_scroll_widget)

        self.summary_tab_layout.addLayout(self.summary_button_layout)
        self.summary_tab_layout.addWidget(self.summary_scroll)

        self.tabs.addTab(self.summary_tab, "Summary")

        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.tabs)

        self.insights_tab = QWidget()
        self.insights_tab_layout = QVBoxLayout(self.insights_tab)

        self.insights_button_layout = QHBoxLayout()
        self.insights_button_top_categories = QPushButton("Top Spending Categories")
        self.insights_button_top_spenders = QPushButton("Top Spenders")
        self.insights_button_high_expense_days = QPushButton("High-Expense Days")

        for btn in [
            self.insights_button_top_categories,
            self.insights_button_top_spenders,
            self.insights_button_high_expense_days
        ]:
            self.insights_button_layout.addWidget(btn)

        self.insights_scroll = QScrollArea()
        self.insights_scroll.setWidgetResizable(True)
        self.insights_scroll_widget = QWidget()
        self.insights_scroll_layout = QVBoxLayout(self.insights_scroll_widget)
        self.insights_scroll_widget.setLayout(self.insights_scroll_layout)
        self.insights_scroll.setWidget(self.insights_scroll_widget)

        self.insights_tab_layout.addLayout(self.insights_button_layout)
        self.insights_tab_layout.addWidget(self.insights_scroll)

        self.tabs.addTab(self.insights_tab, "Spend Insights")

        self.budget_tab = QWidget()
        self.budget_tab_layout = QVBoxLayout(self.budget_tab)

        self.tabs.addTab(self.budget_tab, "Budget Tracking")

        
        self.budget_button_set_limit = QPushButton("Set Budget Limit")
        self.budget_button_summary = QPushButton("Show Budget Summary")

        self.budget_button_layout = QHBoxLayout()
        self.budget_button_layout.addWidget(self.budget_button_set_limit)
        self.budget_button_layout.addWidget(self.budget_button_summary)
        
        self.budget_tab_layout.addLayout(self.budget_button_layout)

        
        self.budget_scroll = QScrollArea()
        self.budget_scroll.setWidgetResizable(True)
        self.budget_scroll_widget = QWidget()
        self.budget_scroll_layout = QVBoxLayout(self.budget_scroll_widget)
        self.budget_scroll_widget.setLayout(self.budget_scroll_layout)
        self.budget_scroll.setWidget(self.budget_scroll_widget)
        self.budget_tab_layout.addWidget(self.budget_scroll)


    def open_file_dialog(self):
        return QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xlsx)")[0]

    def ask_for_card_limit(self, card_name):
        if not card_name == "cash":
            card_type, ok = QInputDialog.getItem(
                self,
                "Select Card Type",
                f"Is '{card_name}' a debit or credit card?",
                ["Debit", "Credit"],
                0,
                False
            )

            if ok and card_type == "Credit":
                limit, limit_ok = QInputDialog.getText(self, "Set Credit Limit", f"Enter the credit limit for '{card_name}':")
                return limit, limit_ok
            else:
                return None, False

    def clear_summary_scroll(self):
        for i in reversed(range(self.summary_scroll_layout.count())):
            widget = self.summary_scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def add_table_to_summary(self, title, table_data):
        label = QLabel(title)
        self.summary_scroll_layout.addWidget(label)

        table = QTableWidget()
        table.setRowCount(len(table_data))
        table.setColumnCount(len(table_data.columns))
        table.setHorizontalHeaderLabels([str(col) for col in table_data.columns])
        table.setVerticalHeaderLabels([str(idx) for idx in table_data.index])

        for i, row in enumerate(table_data.itertuples()):
            for j, value in enumerate(row[1:]):  # Skip the first item (index)
                table.setItem(i, j, QTableWidgetItem(str(value)))

        self.summary_scroll_layout.addWidget(table)

    def add_chart_to_summary(self, title, chart_widget):
        label = QLabel(title)
        self.summary_scroll_layout.addWidget(label)

        self.summary_scroll_layout.addWidget(chart_widget)

    def open_add_expense_dialog(self, sources, categories, spenders):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Expense")

        layout = QFormLayout(dialog)

        year_input = QComboBox()
        year_input.addItems(["2023", "2024", "2025", "2026"]) 
        month_input = QComboBox()
        month_input.addItems([f"{i:02d}" for i in range(1, 13)])
        day_input = QComboBox()
        day_input.addItems([f"{i:02d}" for i in range(1, 32)])

        source_input = QComboBox()
        source_input.addItems(sources)

        description_input = QLineEdit()

        category_input = QComboBox()
        category_input.addItems(categories)

        spender_input = QComboBox()
        spender_input.addItems(spenders)

        amount_input = QLineEdit()
        amount_input.setPlaceholderText("Enter amount (e.g., 100.50)")

        layout.addRow("Year:", year_input)
        layout.addRow("Month:", month_input)
        layout.addRow("Day:", day_input)
        layout.addRow("Source:", source_input)
        layout.addRow("Description:", description_input)
        layout.addRow("Category:", category_input)
        layout.addRow("Spender:", spender_input)
        layout.addRow("Amount:", amount_input)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addRow(buttons_layout)

        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        dialog.year_input = year_input
        dialog.month_input = month_input
        dialog.day_input = day_input
        dialog.source_input = source_input
        dialog.description_input = description_input
        dialog.category_input = category_input
        dialog.spender_input = spender_input
        dialog.amount_input = amount_input

        return dialog
    
    def clear_insights_scroll(self):
        for i in reversed(range(self.insights_scroll_layout.count())):
            widget = self.insights_scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def add_table_to_insights(self, title, table_data):
        label = QLabel(title)
        self.insights_scroll_layout.addWidget(label)

        table = QTableWidget()
        table.setRowCount(len(table_data))
        table.setColumnCount(len(table_data.columns))
        table.setHorizontalHeaderLabels([str(col) for col in table_data.columns])
        table.setVerticalHeaderLabels([str(idx) for idx in table_data.index])

        for i, row in enumerate(table_data.itertuples()):
            for j, value in enumerate(row[1:]):  # Skip the first item (index)
                table.setItem(i, j, QTableWidgetItem(str(value)))

        self.insights_scroll_layout.addWidget(table)

    def add_chart_to_insights(self, title, chart_widget):
        label = QLabel(title)
        self.insights_scroll_layout.addWidget(label)

        self.insights_scroll_layout.addWidget(chart_widget)

    def clear_budget_scroll(self):
        for i in reversed(range(self.budget_scroll_layout.count())):
            widget = self.budget_scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def add_budget_summary(self, budget_summary):
        for category, details in budget_summary.items():
            label = QLabel(f"{category}: ${details['Used']} / ${details['Limit']}")
            progress_bar = QProgressBar()
            progress_value = int((details["Used"] / details["Limit"]) * 100) if details["Limit"] else 0
            progress_bar.setValue(progress_value)
            progress_bar.setFormat(f"{details['Used']:.2f} / {details['Limit']:.2f}")
            self.budget_scroll_layout.addWidget(label)
            self.budget_scroll_layout.addWidget(progress_bar)

    def open_budget_limit_dialog(self, categories):
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Budget Limit")

        layout = QFormLayout(dialog)

        category_input = QComboBox()
        category_input.addItems(categories)

        limit_input = QLineEdit()
        limit_input.setPlaceholderText("Enter budget limit (e.g., 500.00)")

        layout.addRow("Category:", category_input)
        layout.addRow("Limit:", limit_input)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addRow(buttons_layout)

        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        dialog.category_input = category_input
        dialog.limit_input = limit_input

        return dialog



