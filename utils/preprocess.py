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

def cash(number):
    string = str(number)[::-1]
    new = ""
    if type(number) == int:
        for l in range(0, len(string)):
            new += string[l]
            if l%3 == 2 and l != len(string)-1:
                new += "."
        money = new[::-1]
        return money
    else:
        string = string.split(".")
        if int(string[0]) != 0:
            for l in string[0]:
                new += l
            new += ","
        for l in range(0, len(string[1])):
            new += string[1][l]
            if l%3 == 2 and l != len(string[1])-1:
                new += "."
        money = new[::-1]
        return money


def resp_format(waiters, cashiers, zones, products, transactions, ids_conflict, maxi, mini, total_payments, correct_payments, used_time):
    resp_obj = {
        "waiters_tables": waiters,
        "cashiers_tables": cashiers,
        "zones_tables_usage": zones,
        "total_bills": transactions,
        "conflicts": ids_conflict,
        "first_open": mini,
        "last_open": maxi,
        "products_quantity": products,
        "total_payments": cash(total_payments),
        "expected_payments": cash(correct_payments),
        "avrg_used_table": f"{int(used_time//3600)}:{int(used_time%3600//60)}:{int(used_time%60)}",
        "avrg_spend_expected": cash(correct_payments/transactions),
        "avrg_spend_recived": cash(total_payments/transactions), 
        "total_loss": cash(correct_payments - total_payments),
        "avrg_loss":cash(correct_payments/transactions - total_payments/transactions)

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