from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from flask_mail import Mail, Message


app = Flask(__name__)

# =========================================================
# FLASK SECRET KEY
# =========================================================

app.secret_key = "coffee-shop-secret-key-change-this-later"


# =========================================================
# ADMIN LOGIN
# =========================================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "coffee123"


# =========================================================
# EMAIL SETTINGS
# =========================================================

# Gmail account that will SEND the emails
SENDER_EMAIL = "ushna5257@gmail.com"

# Admin email that will RECEIVE new order notifications
ADMIN_EMAIL = "ushna5257@gmail.com"


app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

app.config["MAIL_USERNAME"] = SENDER_EMAIL

# IMPORTANT:
# Use a Gmail APP PASSWORD here.
# Do NOT use your normal Gmail password.
app.config["MAIL_PASSWORD"] = "yuwtheekrywmkmuh"

app.config["MAIL_DEFAULT_SENDER"] = SENDER_EMAIL


mail = Mail(app)


# =========================================================
# PRODUCTS
# =========================================================

products = [
    {
        "id": 1,
        "name": "Cappuccino",
        "price": 450,
        "category": "Coffee",
        "image": "https://images.unsplash.com/photo-1572442388796-11668a67e53d"
    },

    {
        "id": 2,
        "name": "Espresso",
        "price": 350,
        "category": "Coffee",
        "image": "https://images.unsplash.com/photo-1510707577719-ae7c14805e7e"
    },

    {
        "id": 3,
        "name": "Latte",
        "price": 500,
        "category": "Coffee",
        "image": "https://images.unsplash.com/photo-1561882468-9110e03e0f78"
    },

    {
        "id": 4,
        "name": "Chocolate Cake",
        "price": 550,
        "category": "Dessert",
        "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587"
    },

    {
        "id": 5,
        "name": "Croissant",
        "price": 300,
        "category": "Bakery",
        "image": "https://images.unsplash.com/photo-1555507036-ab1f4038808a"
    },

    {
        "id": 6,
        "name": "Iced Coffee",
        "price": 450,
        "category": "Cold Drinks",
        "image": "https://images.unsplash.com/photo-1517701604599-bb29b565090c"
    }
]


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    featured_products = products[:4]

    return render_template(
        "index.html",
        products=featured_products
    )


# =========================================================
# MENU
# =========================================================

@app.route("/menu")
def menu():

    category = request.args.get("category")

    if category:

        filtered_products = [
            product
            for product in products
            if product["category"].lower()
            == category.lower()
        ]

    else:

        filtered_products = products

    categories = sorted(
        set(
            product["category"]
            for product in products
        )
    )

    return render_template(
        "menu.html",
        products=filtered_products,
        categories=categories
    )


# =========================================================
# ADD TO CART
# =========================================================

@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):

    product = next(
        (
            p for p in products
            if p["id"] == product_id
        ),
        None
    )

    if product is None:

        flash("Product not found.")

        return redirect(
            url_for("menu")
        )

    cart = session.get("cart", [])

    cart.append({
        "id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "image": product["image"]
    })

    session["cart"] = cart

    flash(
        f"{product['name']} added to your cart!"
    )

    return redirect(
        request.referrer or url_for("menu")
    )


# =========================================================
# CART
# =========================================================

@app.route("/cart")
def cart():

    cart = session.get("cart", [])

    total = sum(
        item["price"]
        for item in cart
    )

    return render_template(
        "cart.html",
        cart=cart,
        total=total
    )


# =========================================================
# REMOVE FROM CART
# =========================================================

@app.route("/remove-from-cart/<int:index>")
def remove_from_cart(index):

    cart = session.get("cart", [])

    if 0 <= index < len(cart):

        removed_item = cart.pop(index)

        session["cart"] = cart

        flash(
            f"{removed_item['name']} removed from cart."
        )

    return redirect(
        url_for("cart")
    )


# =========================================================
# CLEAR CART
# =========================================================

@app.route("/clear-cart")
def clear_cart():

    session["cart"] = []

    flash(
        "Your cart has been cleared."
    )

    return redirect(
        url_for("cart")
    )


# =========================================================
# CREATE ORDER ITEMS TEXT
# =========================================================

def create_order_items_text(cart):

    order_items = ""

    for item in cart:

        order_items += (
            f"• {item['name']} - "
            f"Rs. {item['price']}\n"
        )

    return order_items


# =========================================================
# SEND CUSTOMER CONFIRMATION EMAIL
# =========================================================

def send_customer_confirmation(
    customer_name,
    customer_email,
    phone,
    address,
    cart,
    total
):

    order_items = create_order_items_text(cart)

    subject = "☕ Brew & Bean - Order Confirmation"

    body = f"""
Hello {customer_name},

Thank you for ordering from Brew & Bean! ☕

We have successfully received your order.

========================================
ORDER DETAILS
========================================

{order_items}
----------------------------------------
TOTAL: Rs. {total}
----------------------------------------

CUSTOMER INFORMATION

Name: {customer_name}
Email: {customer_email}
Phone: {phone}

Delivery Address:

{address}

========================================

Your order is now being processed.

Thank you for choosing Brew & Bean!

☕ Brew & Bean
Fresh Coffee. Good Vibes.
"""

    message = Message(
        subject=subject,
        recipients=[customer_email]
    )

    message.body = body

    mail.send(message)


# =========================================================
# SEND ADMIN ORDER NOTIFICATION
# =========================================================

def send_admin_order_notification(
    customer_name,
    customer_email,
    phone,
    address,
    cart,
    total
):

    order_items = create_order_items_text(cart)

    subject = "🔔 New Coffee Shop Order Received"

    body = f"""
NEW ORDER RECEIVED
==============================

A new order has been placed on Brew & Bean.

CUSTOMER DETAILS
==============================

Name:
{customer_name}

Email:
{customer_email}

Phone:
{phone}

Delivery Address:
{address}


ORDER DETAILS
==============================

{order_items}

------------------------------
TOTAL ORDER VALUE: Rs. {total}
------------------------------


CUSTOMER EMAIL:
{customer_email}


Please prepare and process this order.

☕ Brew & Bean
Admin Order Notification
"""

    message = Message(
        subject=subject,
        recipients=[ADMIN_EMAIL]
    )

    message.body = body

    mail.send(message)


# =========================================================
# CHECKOUT
# =========================================================

@app.route(
    "/checkout",
    methods=["GET", "POST"]
)
def checkout():

    cart = session.get("cart", [])

    # -----------------------------------------
    # EMPTY CART CHECK
    # -----------------------------------------

    if not cart:

        flash(
            "Your cart is empty."
        )

        return redirect(
            url_for("menu")
        )


    # -----------------------------------------
    # CALCULATE TOTAL
    # -----------------------------------------

    total = sum(
        item["price"]
        for item in cart
    )


    # -----------------------------------------
    # PLACE ORDER
    # -----------------------------------------

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()


        # -----------------------------------------
        # VALIDATION
        # -----------------------------------------

        if (
            not name
            or not email
            or not phone
            or not address
        ):

            flash(
                "Please fill in all required fields."
            )

            return redirect(
                url_for("checkout")
            )


        # -----------------------------------------
        # SEND EMAILS
        # -----------------------------------------

        try:

            # Send confirmation to CUSTOMER
            send_customer_confirmation(
                customer_name=name,
                customer_email=email,
                phone=phone,
                address=address,
                cart=cart,
                total=total
            )


            # Send order notification to ADMIN
            send_admin_order_notification(
                customer_name=name,
                customer_email=email,
                phone=phone,
                address=address,
                cart=cart,
                total=total
            )


        except Exception as error:

            print(
                "EMAIL ERROR:",
                error
            )

            flash(
                "There was a problem sending the "
                "order confirmation. Your order was "
                "not completed. Please try again."
            )

            return redirect(
                url_for("checkout")
            )


        # -----------------------------------------
        # CLEAR CART
        # -----------------------------------------

        session["cart"] = []


        # -----------------------------------------
        # SUCCESS PAGE
        # -----------------------------------------

        return render_template(
            "checkout.html",
            success=True,
            name=name,
            email=email,
            total=total
        )


    return render_template(
        "checkout.html",
        cart=cart,
        total=total
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route(
    "/admin-login",
    methods=["GET", "POST"]
)
def admin_login():

    if session.get("admin_logged_in"):

        return redirect(
            url_for("admin")
        )


    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )


        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            session["admin_logged_in"] = True

            flash(
                "Welcome to the Admin Dashboard!"
            )

            return redirect(
                url_for("admin")
            )


        flash(
            "Invalid username or password."
        )


    return render_template(
        "admin_login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route(
    "/admin",
    methods=["GET", "POST"]
)
def admin():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    if request.method == "POST":

        name = request.form.get(
            "name"
        )

        price = request.form.get(
            "price"
        )

        category = request.form.get(
            "category"
        )

        image = request.form.get(
            "image"
        )


        if not name or not price or not category:

            flash(
                "Please fill in all required fields."
            )

            return redirect(
                url_for("admin")
            )


        try:

            price = float(price)

        except ValueError:

            flash(
                "Please enter a valid price."
            )

            return redirect(
                url_for("admin")
            )


        if products:

            new_id = max(
                product["id"]
                for product in products
            ) + 1

        else:

            new_id = 1


        if not image:

            image = (
                "https://images.unsplash.com/"
                "photo-1495474472287-4d71bcdd2085"
            )


        new_product = {
            "id": new_id,
            "name": name,
            "price": price,
            "category": category,
            "image": image
        }


        products.append(
            new_product
        )


        flash(
            f"{name} added successfully!"
        )


        return redirect(
            url_for("admin")
        )


    return render_template(
        "admin.html",
        products=products
    )


# =========================================================
# DELETE PRODUCT
# =========================================================

@app.route(
    "/admin/delete/<int:product_id>"
)
def delete_product(product_id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin_login")
        )


    global products


    product = next(
        (
            p for p in products
            if p["id"] == product_id
        ),
        None
    )


    if product:

        products = [
            p for p in products
            if p["id"] != product_id
        ]

        flash(
            f"{product['name']} deleted successfully."
        )

    else:

        flash(
            "Product not found."
        )


    return redirect(
        url_for("admin")
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin-logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    flash(
        "You have been logged out."
    )

    return redirect(
        url_for("index")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )