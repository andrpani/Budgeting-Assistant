from data.db import BudgetingDBSQLite

db = BudgetingDBSQLite()

purchases = db.get_purchases()

purchase_items = db.get_purchase_items(purchases)

print(purchases)

print(purchase_items)
