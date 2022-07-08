import requests
from datetime import datetime

base_url = "https://storage.googleapis.com/backupdatadev/ejercicio/ventas.json"
def obtain_data(url):
    data = requests.get(url).json()
    return data

def preprocess(data):
    data = data
    waiters = {}
    zones = {}
    cashiers = {}
    products = {}
    ids = []
    ids_conflict = []
    maxi = datetime.strptime(data[0]["date_closed"], '%Y-%m-%d %H:%M:%S')
    mini = datetime.strptime(data[0]["date_opened"], '%Y-%m-%d %H:%M:%S')
    total_payments = 0
    correct_payments = 0
    used_time = 0
    transactions = 0

    for orden in data:
        transactions += 1
        amount = 0
        tot = 0
        used_time += datetime.strptime(orden["date_closed"], '%Y-%m-%d %H:%M:%S').timestamp() - datetime.strptime(orden["date_opened"], '%Y-%m-%d %H:%M:%S').timestamp()
        if orden["waiter"] not in waiters.keys():
            waiters[orden["waiter"]] = [orden["id"]]
        else:
            waiters[orden["waiter"]].append(orden["id"])
        if orden["cashier"] not in cashiers.keys():
            cashiers[orden["cashier"]] = [orden["id"]]
        else:
            cashiers[orden["cashier"]].append(orden["id"])
        if orden["zone"] not in zones.keys():
            zones[orden["zone"]] = {orden["table"]: 1}
        else:
            if orden["table"] not in zones[orden["zone"]].keys():
                zones[orden["zone"]][orden["table"]] = 1
            else:
                zones[orden["zone"]][orden["table"]] += 1
        for p in orden["products"]:
            tot += p["price"]*p["quantity"]
            if p["category"] not in products.keys():
                products[p["category"]] = {p["name"]: p["quantity"]}
            else:
                if p["name"] not in products[p["category"]].keys():
                    products[p["category"]][p["name"]] = p["quantity"]
                else:
                    products[p["category"]][p["name"]] += p["quantity"]
        for pago in orden["payments"]:
            amount += pago["amount"]
        if amount != orden["total"] or tot > orden["total"]:
            ids_conflict.append(orden["id"])
        total_payments += amount
        correct_payments += tot
        if datetime.strptime(orden["date_closed"], '%Y-%m-%d %H:%M:%S') > maxi:
            maxi = datetime.strptime(orden["date_closed"], '%Y-%m-%d %H:%M:%S')
        if datetime.strptime(orden["date_opened"], '%Y-%m-%d %H:%M:%S') < mini:
            mini = datetime.strptime(orden["date_opened"], '%Y-%m-%d %H:%M:%S')
    return resp_format(waiters, cashiers, zones, products, transactions, ids_conflict, maxi, mini, total_payments, correct_payments, used_time/transactions)

def resp_format(waiters, cashiers, zones, products, transactions, ids_conflict, maxi, mini, total_payments, correct_payments, used_time):
    resp_obj = {
        "waiters_tables": waiters,
        "cashiers_tables": cashiers,
        "zones_tables_usage": zones,
        "tota_bills": transactions,
        "conflicts": ids_conflict,
        "first_open": mini,
        "last_open": maxi,
        "products_quantity": products,
        "total_payments": total_payments,
        "expected_payments": correct_payments,
        "avrg_used_table": f"{int(used_time//3600)}:{int(used_time%3600//60)}:{int(used_time%60)}",
        "avrg_spend_expected": correct_payments/transactions,
        "avrg_spend_recived": total_payments/transactions
    }
    return resp_obj

def  get_sales(data):
    sales = {}
    for t in data:
        if t["date_opened"].split()[0] != t["date_closed"].split()[0]:
            print("true")
        if t["date_opened"].split()[0] not in sales.keys():
            sales[t["date_opened"].split()[0]] = [t["id"]]
        else:
            sales[t["date_opened"].split()[0]].append(t["id"])
    return sales