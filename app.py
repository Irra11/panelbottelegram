import os
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import sqlite3
import requests
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configuration
BOT_TOKEN = "7159490173:AAEfsvxSCSLWiGqBCAm0uNNUEo7k11x3-UM"
DB_PATH = "orders.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id TEXT, username TEXT, udid TEXT, price TEXT, status TEXT, date TEXT)')
    conn.close()

init_db()

class Order(BaseModel):
    user_id: str
    username: str
    udid: str
    price: str

@app.post("/api/v1/save_order")
async def save_order(order: Order):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO orders (user_id, username, udid, price, status, date) VALUES (?,?,?,?,?,?)",
                 (order.user_id, order.username, order.udid, order.price, "PENDING", datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/")
async def index(request: Request):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    stats = {
        "total": len(orders),
        "done": len([o for o in orders if o['status'] == 'COMPLETED']),
        "pending": len([o for o in orders if o['status'] == 'PENDING']),
        "revenue": sum([float(o['price']) for o in orders if o['status'] == 'COMPLETED'])
    }
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "orders": orders, "stats": stats})

@app.post("/send_file/{user_id}/{order_id}")
async def send_file(user_id: str, order_id: int, file: UploadFile = File(...)):
    # 1. Send file to Telegram user
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file.filename, await file.read())}
    data = {'chat_id': user_id, 'caption': "🎁 Here is your signed application file!"}
    
    resp = requests.post(url, data=data, files=files)
    
    if resp.status_code == 200:
        # 2. Update status in database
        conn = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE orders SET status='COMPLETED' WHERE id=?", (order_id,))
        conn.commit()
        conn.close()
    
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
