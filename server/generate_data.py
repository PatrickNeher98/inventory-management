"""
Script to generate sample data spread across all months of 2025
"""
import json
import random
from datetime import datetime, timedelta

# Product catalog
products = [
    {"sku": "WDG-001", "name": "Industrial Widget Type A", "category": "Widgets", "price": 24.99},
    {"sku": "WDG-002", "name": "Industrial Widget Type B", "category": "Widgets", "price": 29.99},
    {"sku": "WDG-003", "name": "Industrial Widget Type C", "category": "Widgets", "price": 34.50},
    {"sku": "BRG-102", "name": "Steel Bearing Assembly", "category": "Components", "price": 89.50},
    {"sku": "BRG-103", "name": "Ceramic Bearing Assembly", "category": "Components", "price": 125.00},
    {"sku": "GSK-203", "name": "High-Temperature Gasket", "category": "Components", "price": 12.75},
    {"sku": "GSK-204", "name": "Standard Gasket", "category": "Components", "price": 8.50},
    {"sku": "GSK-205", "name": "Heavy Duty Gasket", "category": "Components", "price": 15.99},
    {"sku": "MTR-304", "name": "Electric Motor 5HP", "category": "Equipment", "price": 445.00},
    {"sku": "MTR-305", "name": "Electric Motor 10HP", "category": "Equipment", "price": 725.00},
    {"sku": "MTR-306", "name": "Electric Motor 3HP", "category": "Equipment", "price": 325.00},
    {"sku": "FLT-405", "name": "Oil Filter Cartridge", "category": "Consumables", "price": 8.25},
    {"sku": "FLT-406", "name": "Air Filter Cartridge", "category": "Consumables", "price": 6.50},
    {"sku": "FLT-407", "name": "Fuel Filter Cartridge", "category": "Consumables", "price": 7.75},
    {"sku": "VLV-506", "name": "Pressure Relief Valve", "category": "Components", "price": 156.00},
    {"sku": "VLV-507", "name": "Ball Valve", "category": "Components", "price": 95.00},
    {"sku": "VLV-508", "name": "Gate Valve", "category": "Components", "price": 110.50},
]

customers = [
    "Acme Manufacturing Corp", "TechBuild Industries", "Global Parts Ltd",
    "Precision Tools Inc", "Industrial Solutions Inc", "MegaCorp Industries",
    "BuildTech Co", "FastAssembly Ltd", "Quality Parts LLC", "Superior Manufacturing",
    "PrecisionWorks Inc", "Elite Systems Corp", "Advanced Components Inc",
    "ProManufacturing LLC", "TechSolutions Group", "Innovative Parts Co",
    "Premier Industries", "Dynamic Systems Ltd", "Quantum Manufacturing",
    "Apex Engineering", "Titan Products Inc", "Vanguard Systems",
    "Omega Manufacturing", "Fusion Industries", "Stellar Components Ltd",
    "Nexus Engineering", "Cascade Manufacturing", "Horizon Technologies",
    "Summit Parts Corp", "Velocity Industries"
]

warehouses = ["A", "B", "C"]
statuses = ["Delivered", "Shipped", "Processing", "Backordered"]

# Generate orders for each month of 2025
orders = []
order_id = 1

for month in range(1, 13):  # Jan to Dec
    # Generate 8-12 orders per month
    num_orders = random.randint(8, 12)

    for _ in range(num_orders):
        # Random day in the month
        day = random.randint(1, 28)  # Using 28 to avoid month-end issues
        hour = random.randint(8, 17)
        minute = random.randint(0, 59)

        order_date = f"2025-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00"

        # Expected delivery 7-14 days later
        order_datetime = datetime(2025, month, day, hour, minute)
        delivery_days = random.randint(7, 14)
        expected_delivery = order_datetime + timedelta(days=delivery_days)

        # Determine status based on date (earlier orders more likely to be delivered)
        if month <= 8:
            status = random.choices(statuses, weights=[70, 20, 5, 5])[0]
        elif month <= 10:
            status = random.choices(statuses, weights=[40, 40, 15, 5])[0]
        else:
            status = random.choices(statuses, weights=[10, 30, 40, 20])[0]

        # Select 1-3 products for the order
        num_items = random.randint(1, 3)
        order_products = random.sample(products, num_items)

        items = []
        total_value = 0
        primary_category = None

        for product in order_products:
            quantity = random.randint(50, 1000)
            item_value = quantity * product["price"]
            total_value += item_value

            if primary_category is None:
                primary_category = product["category"]

            items.append({
                "sku": product["sku"],
                "name": product["name"],
                "quantity": quantity,
                "unit_price": product["price"]
            })

        warehouse = random.choice(warehouses)

        order = {
            "id": str(order_id),
            "order_number": f"ORD-2025-{order_id:04d}",
            "customer": random.choice(customers),
            "items": items,
            "status": status,
            "warehouse": warehouse,
            "category": primary_category,
            "order_date": order_date,
            "expected_delivery": expected_delivery.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_value": round(total_value, 2)
        }

        if status == "Delivered" and month <= 10:
            actual_delivery = order_datetime + timedelta(days=random.randint(6, delivery_days + 2))
            order["actual_delivery"] = actual_delivery.strftime("%Y-%m-%dT%H:%M:%S")

        orders.append(order)
        order_id += 1

# Save to file
with open('data/orders.json', 'w') as f:
    json.dump(orders, f, indent=2)

print(f"Generated {len(orders)} orders across 12 months of 2025")

# Count orders per month
from collections import defaultdict
orders_per_month = defaultdict(int)
for order in orders:
    month = order['order_date'][5:7]
    orders_per_month[month] += 1

print("\nOrders per month:")
for month in sorted(orders_per_month.keys()):
    print(f"  {month}: {orders_per_month[month]} orders")

# Demand forecasts (static data) including restocking fields:
# unit_cost, current_stock, supplier, lead_time_days
demand_forecasts = [
    {"id": "1", "item_sku": "WDG-001", "item_name": "Industrial Widget Type A", "current_demand": 300, "forecasted_demand": 450, "trend": "increasing", "period": "Next 30 days", "unit_cost": 24.99, "current_stock": 120, "supplier": "Apex Industrial Supply", "lead_time_days": 7},
    {"id": "2", "item_sku": "BRG-102", "item_name": "Steel Bearing Assembly", "current_demand": 150, "forecasted_demand": 152, "trend": "stable", "period": "Next 30 days", "unit_cost": 48.50, "current_stock": 100, "supplier": "Northwind Bearings", "lead_time_days": 10},
    {"id": "3", "item_sku": "GSK-203", "item_name": "High-Temperature Gasket", "current_demand": 500, "forecasted_demand": 600, "trend": "increasing", "period": "Next 30 days", "unit_cost": 15.75, "current_stock": 200, "supplier": "ThermoSeal Corp", "lead_time_days": 14},
    {"id": "4", "item_sku": "MTR-304", "item_name": "Electric Motor 5HP", "current_demand": 50, "forecasted_demand": 35, "trend": "decreasing", "period": "Next 30 days", "unit_cost": 389.00, "current_stock": 40, "supplier": "Voltage Dynamics", "lead_time_days": 21},
    {"id": "5", "item_sku": "FLT-405", "item_name": "Oil Filter Cartridge", "current_demand": 800, "forecasted_demand": 950, "trend": "increasing", "period": "Next 30 days", "unit_cost": 8.40, "current_stock": 300, "supplier": "CleanFlow Parts", "lead_time_days": 5},
    {"id": "6", "item_sku": "VLV-506", "item_name": "Pressure Relief Valve", "current_demand": 120, "forecasted_demand": 121, "trend": "stable", "period": "Next 30 days", "unit_cost": 72.25, "current_stock": 150, "supplier": "Pressure Systems Ltd", "lead_time_days": 12},
    {"id": "7", "item_sku": "PSU-501", "item_name": "5V 10A Switching Power Supply", "current_demand": 250, "forecasted_demand": 252, "trend": "stable", "period": "Next 30 days", "unit_cost": 18.90, "current_stock": 200, "supplier": "Apex Industrial Supply", "lead_time_days": 9},
    {"id": "8", "item_sku": "SNR-420", "item_name": "Temperature Sensor Module", "current_demand": 180, "forecasted_demand": 182, "trend": "stable", "period": "Next 30 days", "unit_cost": 31.20, "current_stock": 170, "supplier": "Sensortech GmbH", "lead_time_days": 15},
    {"id": "9", "item_sku": "CTL-330", "item_name": "Logic Controller Board", "current_demand": 95, "forecasted_demand": 96, "trend": "stable", "period": "Next 30 days", "unit_cost": 64.00, "current_stock": 60, "supplier": "Sensortech GmbH", "lead_time_days": 18},
]

with open('data/demand_forecasts.json', 'w') as f:
    json.dump(demand_forecasts, f, indent=2)
    f.write("\n")

print(f"Generated {len(demand_forecasts)} demand forecasts")
