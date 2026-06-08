"""
🍽️  Restaurant Ordering System
"""

menu = {
    "Starters": {
        1: {"name": "Garlic Bread",         "price": 3.99},
        2: {"name": "Tomato Soup",          "price": 4.99},
        3: {"name": "Chicken Wings (6 pcs)","price": 7.99},
        4: {"name": "Caesar Salad",         "price": 6.49},
    },
    "Main Course": {
        5: {"name": "Grilled Chicken",      "price": 14.99},
        6: {"name": "Beef Burger",          "price": 12.99},
        7: {"name": "Margherita Pizza",     "price": 13.49},
        8: {"name": "Pasta Carbonara",      "price": 11.99},
        9: {"name": "Fish & Chips",         "price": 13.99},
    },
    "Desserts": {
        10: {"name": "Chocolate Lava Cake", "price": 5.99},
        11: {"name": "Vanilla Ice Cream",   "price": 3.99},
        12: {"name": "Cheesecake",          "price": 5.49},
    },
    "Drinks": {
        13: {"name": "Soft Drink",          "price": 2.49},
        14: {"name": "Fresh Orange Juice",  "price": 3.49},
        15: {"name": "Coffee",              "price": 2.99},
        16: {"name": "Sparkling Water",     "price": 1.99},
    },
}

TAX_RATE = 0.08   # 8% tax
SEPARATOR = "=" * 52


def display_menu():
    """Print the full restaurant menu."""
    print(f"\n{SEPARATOR}")
    print(" " * 15 + "🍽️  BISTRO BELLE  🍽️")
    print(SEPARATOR)
    for category, items in menu.items():
        print(f"\n  ── {category} ──")
        for item_id, details in items.items():
            print(f"   [{item_id:>2}]  {details['name']:<26} ${details['price']:.2f}")
    print(f"\n{SEPARATOR}")


def get_all_items():
    """Return a flat dict {item_id: details} for quick lookup."""
    return {item_id: details
            for items in menu.values()
            for item_id, details in items.items()}


def take_order():
    """Interactively collect the customer's order. Returns list of (item, qty)."""
    all_items = get_all_items()
    order = {}   # {item_id: quantity}

    print("\nEnter item numbers to add them to your order.")
    print("Type  'done'  when finished  |  'view'  to see your cart  |  'menu'  to reprint the menu.\n")

    while True:
        raw = input("  Add item (number): ").strip().lower()

        if raw == "done":
            if not order:
                print("  ⚠️  Your cart is empty. Please add at least one item.")
                continue
            break

        if raw == "menu":
            display_menu()
            continue

        if raw == "view":
            print_cart(order, all_items)
            continue

        # Validate numeric input
        if not raw.isdigit():
            print("  ❌  Please enter a valid item number, 'done', 'view', or 'menu'.")
            continue

        item_id = int(raw)
        if item_id not in all_items:
            print(f"  ❌  Item [{item_id}] not found. Check the menu and try again.")
            continue

        # Ask for quantity
        qty_raw = input(f"     How many × {all_items[item_id]['name']}? ").strip()
        if not qty_raw.isdigit() or int(qty_raw) < 1:
            print("  ❌  Please enter a valid quantity (1 or more).")
            continue

        qty = int(qty_raw)
        order[item_id] = order.get(item_id, 0) + qty
        print(f"  ✅  {qty} × {all_items[item_id]['name']} added to cart.")

    return order, all_items


def print_cart(order, all_items):
    """Display current cart contents."""
    if not order:
        print("  🛒  Cart is empty.")
        return
    print(f"\n  {'─'*40}")
    print("   🛒  YOUR CART")
    print(f"  {'─'*40}")
    for item_id, qty in order.items():
        item = all_items[item_id]
        subtotal = item["price"] * qty
        print(f"   {qty} × {item['name']:<26} ${subtotal:.2f}")
    print(f"  {'─'*40}\n")


def print_receipt(order, all_items, customer_name):
    """Print a formatted receipt."""
    subtotal = sum(all_items[iid]["price"] * qty for iid, qty in order.items())
    tax      = subtotal * TAX_RATE
    total    = subtotal + tax

    print(f"\n{SEPARATOR}")
    print(" " * 18 + "🧾  RECEIPT")
    print(SEPARATOR)
    print(f"  Customer : {customer_name}")
    print(f"  {'─'*48}")
    for item_id, qty in order.items():
        item = all_items[item_id]
        line_total = item["price"] * qty
        print(f"  {qty} × {item['name']:<28} ${line_total:>6.2f}")
    print(f"  {'─'*48}")
    print(f"  {'Subtotal':<38} ${subtotal:>6.2f}")
    print(f"  {'Tax (8%)':<38} ${tax:>6.2f}")
    print(f"  {'─'*48}")
    print(f"  {'TOTAL':<38} ${total:>6.2f}")
    print(SEPARATOR)
    print("   Thank you for dining with us! Enjoy your meal 😊")
    print(f"{SEPARATOR}\n")


def ask_another_order():
    """Ask if a new order should be placed."""
    ans = input("  New order? (yes / no): ").strip().lower()
    return ans in ("yes", "y")


def main():
    print(f"\n{SEPARATOR}")
    print("   Welcome to Bistro Belle! 🌟")
    print(SEPARATOR)

    while True:
        customer_name = input("\n  Please enter your name: ").strip()
        if customer_name:
            break
        print("  ⚠️  Name cannot be empty.")

    display_menu()
    order, all_items = take_order()
    print_receipt(order, all_items, customer_name)

    if ask_another_order():
        main()
    else:
        print("  Goodbye! Have a wonderful day! 👋\n")


if __name__ == "__main__":
    main()