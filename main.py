from fastapi import FastAPI
from datetime import datetime, timedelta
from utils.preprocess import preprocess, obtain_data, get_sales, cash

app = FastAPI()
base_url = "https://storage.googleapis.com/backupdatadev/ejercicio/ventas.json"
data = obtain_data(base_url)
general_data = preprocess(data)
sells = get_sales(data)

@app.get("/")
def initial_info():
    return {"data": general_data, "sells": sells}

@app.get("info/date/{date}/range/{range}")
def week_info(date: str, range: int = 7):
    initial = datetime.strptime(date, '%Y-%m-%d')
    final = initial + timedelta(days=range)
    date_data = []
    for t in data:
        if final > datetime.strptime(t["date_closed"], '%Y-%m-%d %H:%M:%S') > initial:
            date_data.append(t)
    if len(date_data) > 0:
        print(f"you requested the {initial} to {final} info")
        res_obj = preprocess(date_data) 
        date_sells = get_sales(date_data)
        return {"data" : res_obj, "sells": date_sells}
    else: 
        return {"body": "no data"}

@app.get("/worker/{name}")
def person_info(name: str):
    print(f"you requested {name} info")
    name_data = []
    for t in data:
        if t["waiter"] == name or t["cashier"] == name:
            name_data.append(t)
    if len(name_data) > 0:
        res_obj= preprocess(name_data)
        person_sells = get_sales(name_data)
        return {"data" : res_obj, "sells": person_sells}
    else: 
        return {"body": "no data"}

@app.get("/tables/{sector}")
def sector_info(sector: str):
    print(f"you requested info from the {sector} sector")
    tables_data = []
    for t in data:
        if t["zone"] == sector:
            tables_data.append(t)
    if len(tables_data) > 0:
        res_obj= preprocess(tables_data)
        tables_sells = get_sales(tables_data)
        return {"data" : res_obj, "sells": tables_sells}
    else: 
        return {"body": "no data"}

@app.get("/{date}")
def date_info(date: str):
    print(f"you requested info from the {date} sector")
    res_data = {}
    d_data = []
    for t in data:
        if t["date_opened"].split(" ")[0] == date:
            res_data[t["id"]] = t
            d_data.append(t)
    if len(res_data.keys()) > 0:
        information = preprocess(d_data)
        return {"data" : res_data, "info": information}
    else: 
        return {"body": "no data"}

@app.get("/{date}/{worker}")
def date_worker_info(date: str, worker: str):
    print(f"you requested info from the {date} sector of {worker}")
    res_data = {}
    d_data = []
    for t in data:
        if t["date_opened"].split(" ")[0] == date and (t["waiter"] == worker or t["cashier"] == worker):
            res_data[t["id"]] = t
            d_data.append(t)
    if len(res_data.keys()) > 0:
        information = preprocess(d_data)
        return {"data" : res_data, "info": information}
    else: 
        return {"body": "no data"}

@app.get("/single/table/{date}/{n}")
def table_info(date: str, n: str):
    print(f"you requested {date} table {n} info")
    res_data = {}
    table_data = []
    for t in data:
        if t["table"] == int(n) and t["date_opened"].split(" ")[0] == date:
            res_data[t["id"]] = t
            table_data.append(t)
    if len(res_data.keys()) > 0:
        information= preprocess(table_data)
        return {"data" : res_data, "info": information}
    else: 
        return {"body": "no data"}

@app.get("/products/from/{category}/until/{date}")
def category_info(category: str, date: str):
    print(f"you requested the {category} products until {date}")
    initial = datetime.strptime(date, '%Y-%m-%d')
    final = initial + timedelta(days=1)
    res_data = {}
    cate_data = []
    quantity = {}
    for t in data:
        if datetime.strptime(t["date_closed"], '%Y-%m-%d %H:%M:%S') < final:
            for orden in t["products"]:
                if orden["category"] == category:
                    if orden["name"] not in quantity.keys():
                        quantity[orden["name"]] = [cash(orden["price"]), orden["quantity"]]
                    else:
                        quantity[orden["name"]][1] += orden["quantity"]
    for t in data:
        if datetime.strptime(t["date_closed"], '%Y-%m-%d %H:%M:%S') < final:
            for orden in t["products"]:
                if orden["category"] == category:
                    res_data[t["id"]] = t
                    cate_data.append(t)
    if len(res_data.keys()) > 0:
        information= preprocess(cate_data)
        return {"data" : res_data, "info": information, "cantidades": quantity}
    else: 
        return {"body": "no data"}

@app.get("/get/specific/bill/information/id/{id}")
def bill_info(id: str):
    print(f"you requested {id} bill")
    found = False
    for d in data:
        if d["id"] == id:
            var = d
            found = True
    if found:
        return {"transaction" : var}
    else: 
        return {"body": "no data"}