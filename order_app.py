"""
Instructions:
1. Install required packages:
   pip install flask twilio

2. Run the app:
   python order_app.py
"""

from flask import Flask, request, render_template_string, redirect, url_for, session, send_file
from twilio.rest import Client

# Twilio credentials and numbers
account_sid = "ACbe1164e17e02827528d938e72f1c4dfd"
auth_token = "0e2d6377bd188831c33c40c8e1ea230a"
twilio_whatsapp_number = "whatsapp:+14155238886"
owner_whatsapp_number = "whatsapp:+917416777662"

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session

# Dummy food menu
food_menu = [
    {"id": 1, "name": "Pizza", "price": 250, "img": "https://images.unsplash.com/photo-1548365328-8b849e6c7b8b?w=400"},
    {"id": 2, "name": "Burgger", "price": 180, "img": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=400"},
    {"id": 3, "name": "Pasta", "price": 200, "img": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400"},
    {"id": 4, "name": "Fries", "price": 100, "img": "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?w=400"},
    {"id": 5, "name": "Salad", "price": 120, "img": "https://images.unsplash.com/photo-1510626176961-4b57d4fbad04?w=400"},
    {"id": 6, "name": "Paneer Tikka Taco", "price": 220, "img": "https://images.unsplash.com/photo-1600628422019-6c1a9b7b8c5e?w=400"},
    {"id": 7, "name": "Dragon Noodles", "price": 210, "img": "https://images.unsplash.com/photo-1504674900247-ec6b0b1b7982?w=400"},
    {"id": 8, "name": "Cheesy Nachos", "price": 160, "img": "https://images.unsplash.com/photo-1502741338009-cac2772e18bc?w=400"},
    {"id": 9, "name": "Choco Lava Cake", "price": 140, "img": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=400"},
    {"id": 10, "name": "Mango Lassi", "price": 90, "img": "https://images.unsplash.com/photo-1523987355523-c7b5b0723c6a?w=400"},
]

# HTML templates
menu_html = '''
<!doctype html>
<html lang="en">
  <head>
    <title>Food Order</title>
    <style>
      body {
        background: linear-gradient(135deg, #fffbe6 0%, #ffe5b4 100%);
        font-family: 'Segoe UI', 'Arial Rounded MT Bold', Arial, sans-serif;
        margin: 0;
        padding: 0;
      }
      .header {
        background: #ffb347;
        color: #7c3f00;
        padding: 24px 0 12px 0;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        letter-spacing: 2px;
        box-shadow: 0 2px 8px #f5c16c44;
      }
      .menu { display: flex; flex-wrap: wrap; gap: 32px; justify-content: center; margin-top: 32px; }
      .item {
        background: #fff8e1;
        border: 2px solid #ffb347;
        border-radius: 18px;
        padding: 20px 18px 18px 18px;
        width: 210px;
        text-align: center;
        box-shadow: 0 4px 16px #f5c16c22;
        transition: transform 0.15s;
      }
      .item:hover {
        transform: scale(1.04) rotate(-2deg);
        box-shadow: 0 8px 24px #f5c16c44;
      }
      img {
        width: 140px;
        height: 110px;
        object-fit: cover;
        border-radius: 12px;
        margin-bottom: 10px;
        border: 2px solid #ffb347;
        background: #fff;
      }
      .cart-link {
        float: right;
        font-size: 1.2rem;
        color: #7c3f00;
        text-decoration: none;
        font-weight: bold;
        margin-right: 32px;
      }
      .cart-link:hover { color: #d2691e; }
      .item b {
        font-size: 1.3rem;
        color: #d2691e;
        font-family: 'Arial Rounded MT Bold', Arial, sans-serif;
      }
      .item .price {
        font-size: 1.1rem;
        color: #7c3f00;
        margin-bottom: 10px;
      }
      .add-btn {
        background: #ff7043;
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 8px 18px;
        font-size: 1rem;
        font-weight: bold;
        cursor: pointer;
        margin-top: 8px;
        box-shadow: 0 2px 8px #ff704344;
        transition: background 0.2s, transform 0.1s;
      }
      .add-btn:hover {
        background: #d84315;
        transform: scale(1.07);
      }
      .logout-link {
        float: right;
        font-size: 1.1rem;
        color: #d84315;
        text-decoration: none;
        font-weight: bold;
        margin-right: 16px;
        margin-top: 4px;
      }
      .logout-link:hover { color: #7c3f00; }
    </style>
  </head>
  <body>
    <div class="header">🍔 Burger House <span style="font-size:1.2rem;">Fast Food & More</span>
      <a href="/logout" class="logout-link">Logout</a>
      <a href="/cart" class="cart-link">🛒 Cart ({{ cart_count }})</a>
    </div>
    <div class="menu">
      {% for food in food_menu %}
      <div class="item">
        <img src="{{ food.img }}" alt="{{ food.name }}"><br>
        <b>{{ food.name }}</b><br>
        <div class="price">₹{{ food.price }}</div>
        <form method="post" action="/add_to_cart">
          <input type="hidden" name="food_id" value="{{ food.id }}">
          <button type="submit" class="add-btn">Add to Cart</button>
        </form>
      </div>
      {% endfor %}
    </div>
  </body>
</html>
'''

cart_html = '''
<!doctype html>
<html lang="en">
  <head>
    <title>Your Cart</title>
    <style>
      body {
        background: linear-gradient(135deg, #fffbe6 0%, #ffe5b4 100%);
        font-family: 'Segoe UI', 'Arial Rounded MT Bold', Arial, sans-serif;
        margin: 0;
        padding: 0;
      }
      .header {
        background: #ffb347;
        color: #7c3f00;
        padding: 24px 0 12px 0;
        text-align: center;
        font-size: 2.2rem;
        font-weight: bold;
        letter-spacing: 2px;
        box-shadow: 0 2px 8px #f5c16c44;
        margin-bottom: 32px;
      }
      .cart-container {
        display: flex;
        flex-direction: column;
        align-items: center;
      }
      table {
        border-collapse: separate;
        border-spacing: 0;
        width: 70%;
        margin: 0 auto 24px auto;
        background: #fff8e1;
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 4px 16px #f5c16c22;
      }
      th, td {
        border: none;
        padding: 14px 12px;
        text-align: center;
        font-size: 1.1rem;
      }
      th {
        background: #ffb347;
        color: #7c3f00;
        font-size: 1.15rem;
        font-weight: bold;
      }
      tr:not(:last-child) td {
        border-bottom: 2px solid #ffe5b4;
      }
      img {
        width: 60px;
        height: 45px;
        object-fit: cover;
        border-radius: 10px;
        border: 2px solid #ffb347;
        background: #fff;
      }
      .center { text-align: center; }
      .order-form {
        margin-bottom: 18px;
      }
      .order-input {
        padding: 7px 12px;
        border-radius: 8px;
        border: 1.5px solid #ffb347;
        font-size: 1rem;
        margin-right: 10px;
      }
      .order-btn {
        background: #ff7043;
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 8px 18px;
        font-size: 1rem;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 2px 8px #ff704344;
        transition: background 0.2s, transform 0.1s;
      }
      .order-btn:hover {
        background: #d84315;
        transform: scale(1.07);
      }
      .back-link {
        color: #d2691e;
        font-weight: bold;
        text-decoration: none;
        font-size: 1.1rem;
        margin-top: 10px;
        display: inline-block;
      }
      .back-link:hover { color: #7c3f00; }
      .empty-msg {
        color: #7c3f00;
        font-size: 1.2rem;
        margin: 40px 0 20px 0;
        text-align: center;
      }
      .logout-link {
        float: right;
        font-size: 1.1rem;
        color: #d84315;
        text-decoration: none;
        font-weight: bold;
        margin-right: 16px;
        margin-top: 4px;
      }
      .logout-link:hover { color: #7c3f00; }
    </style>
  </head>
  <body>
    <div class="header">🍔 Burger House Cart <a href="/logout" class="logout-link">Logout</a></div>
    <div class="cart-container">
    {% if cart_items %}
    <form method="post" action="/order" class="order-form">
      <table>
        <tr><th>Item</th><th>Price</th><th>Qty</th><th>Image</th></tr>
        {% for item in cart_items %}
        <tr>
          <td>{{ item.name }}</td>
          <td>₹{{ item.price }}</td>
          <td>{{ item.qty }}</td>
          <td><img src="{{ item.img }}" alt="{{ item.name }}"></td>
        </tr>
        {% endfor %}
      </table>
      <div class="center">
        <label for="name"><b>Your Name:</b></label>
        <input type="text" name="name" id="name" required class="order-input">
        <button type="submit" class="order-btn">Order</button>
      </div>
    </form>
    {% else %}
      <div class="empty-msg">Your cart is empty. <a href="/menu" class="back-link">Go to menu</a></div>
    {% endif %}
    <a href="/menu" class="back-link">← Back to Menu</a>
    </div>
  </body>
</html>
'''

confirmation_html = '''
<!doctype html>
<html lang="en">
  <head>
    <title>Order Confirmation</title>
    <style>.center { text-align: center; margin-top: 40px; }</style>
  </head>
  <body>
    <div class="center">
      <h2>Order placed and notification sent via WhatsApp!</h2>
      <form action="/menu" method="get">
        <button type="submit">Go Back to Menu</button>
      </form>
    </div>
  </body>
</html>
'''

# Helper to get cart items from session
def get_cart_items():
    cart = session.get('cart', {})
    items = []
    for food in food_menu:
        fid = str(food['id'])
        if fid in cart:
            items.append({
                'name': food['name'],
                'price': food['price'],
                'img': food['img'],
                'qty': cart[fid]
            })
    return items

@app.route("/", methods=["GET"])
def welcome():
    with open("welcome.html", "r", encoding="utf-8") as f:
        return f.read()

@app.route("/menu", methods=["GET"])
def menu():
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    return render_template_string(menu_html, food_menu=food_menu, cart_count=cart_count)

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    food_id = request.form.get('food_id')
    cart = session.get('cart', {})
    cart[food_id] = cart.get(food_id, 0) + 1
    session['cart'] = cart
    return redirect(url_for('menu'))

@app.route("/cart", methods=["GET"])
def cart():
    cart_items = get_cart_items()
    return render_template_string(cart_html, cart_items=cart_items)

@app.route("/order", methods=["POST"])
def place_order():
    name = request.form.get("name")
    cart_items = get_cart_items()
    if not name or not cart_items:
        return redirect(url_for('cart'))
    # Prepare WhatsApp message
    items_str = "\n".join([f"- {item['name']} x{item['qty']} (₹{item['price']})" for item in cart_items])
    message_body = f"\U0001F4E6 New Food Order!\nCustomer: {name}\nItems:\n{items_str}"
    # Send WhatsApp message via Twilio
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=message_body,
        from_=twilio_whatsapp_number,
        to=owner_whatsapp_number
    )
    # Clear cart
    session['cart'] = {}
    return confirmation_html

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('welcome'))

if __name__ == "__main__":
    app.run(debug=True) 