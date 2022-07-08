from fastapi import FastAPI
from datetime import datetime, timedelta
from utils.preprocess import preprocess, obtain_data, get_sales

app = FastAPI()
base_url = "https://storage.googleapis.com/backupdatadev/ejercicio/ventas.json"
data = obtain_data(base_url)
general_data = preprocess(data)
sells = get_sales(data)

@app.get("/")
def initial_info():
    return {"data": general_data, "sells": sells}

@app.get("/date-info/{date}/range/{range}")
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

@app.get("/table/{n}")
def table_info(n: int):
    print(f"you requested table {n} info")
    table_data = []
    for t in data:
        if t["table"] == n:
            table_data.append(t)
    if len(table_data) > 0:
        res_obj= preprocess(table_data)
        table_sells = get_sales(table_data)
        return {"data" : res_obj, "sells": table_sells}
    else: 
        return {"body": "no data"}

@app.get("/tables/{sector}")
def table_info(sector: str):
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