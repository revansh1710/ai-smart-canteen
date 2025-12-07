from flask import Flask, render_template, request, redirect, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from models import db, User, Reservation
from flask import render_template, request, redirect, session, flash
from datetime import datetime
from ml_model import predict_popular_meal, predict_rush_hour
from flask import request, redirect, render_template, session, flash, url_for
from models import db, Meal
from flask_migrate import Migrate


meal_data = [
    {"name": "Chicken Biryani", "price": 8.50, "img": "chicken_biryani.jpg", "desc": "Spicy and flavorful rice with tender chicken pieces.", "initial_stock": 10},
    {"name": "Veg Fried Rice", "price": 6.00, "img": "veg_fried_rice.jpg", "desc": "Classic fried rice loaded with fresh vegetables.", "initial_stock": 10},
    {"name": "Paneer Butter Masala", "price": 7.50, "img": "paneer_butter_masala.jpg", "desc": "Soft paneer cubes cooked in rich buttery tomato gravy.", "initial_stock": 10},
    {"name": "Grilled Sandwich", "price": 4.00, "img": "grilled_sandwich.jpg", "desc": "Crispy grilled bread stuffed with cheese and veggies.", "initial_stock": 10},
    {"name": "Pasta Alfredo", "price": 7.00, "img": "pasta_alfredo.jpg", "desc": "Creamy Alfredo pasta with herbs and parmesan.", "initial_stock": 10},
    {"name": "Chicken Wrap", "price": 5.50, "img": "chicken_wrap.jpg", "desc": "Soft wrap filled with grilled chicken and sauces.", "initial_stock": 10},
    {"name": "American Cheese Potato", "price": 4.50, "img": "American_Cheese_Potato.jpg", "desc": "Golden crispy potato wedges topped with melted American cheese.", "initial_stock": 10},
    {"name": "Honey Chicken", "price": 9.00, "img": "honey_chicken.jpg", "desc": "Juicy chicken glazed in a sweet honey sauce.", "initial_stock": 10},
    {"name": "Chocolate Milkshake", "price": 3.50, "img": "chocolate_milkshake.jpg", "desc": "Rich and creamy chocolate milkshake topped with whipped cream.", "initial_stock": 10},
    {"name": "Black Forest Pastry", "price": 4.00, "img": "Black forest Pastry.jpg", "desc": "Delicious chocolate sponge cake layered with cherries and cream.", "initial_stock": 10},
    {"name": "Chicken Noodles", "price": 6.50, "img": "chicken_noodles.jpg", "desc": "Stir-fried noodles with tender chicken and vegetables.", "initial_stock": 10},
    {"name": "Chicken Pizza", "price": 10.00, "img": "chicken_pizza.jpg", "desc": "Crispy pizza base topped with chicken, cheese, and herbs.", "initial_stock": 10}
]

app = Flask(__name__)
app.secret_key = 'anything-you-want'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///canteen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)


# ------------------ MODELS ------------------



# --- Only create admin after tables exist ---
def create_admin():
    with app.app_context():
        db.create_all()  # Create tables first
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                first_name='Admin',
                last_name='User',
                email='admin@example.com',
                mobile='0000000000',
                password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")
        else:
            print("Admin already exists.")




# ------------------ ROUTES ------------------

def get_meal_stock():
    """Get stock for all meals from the database"""
    stock_dict = {}
    meals = Meal.query.all()  # Fetch from DB
    for meal in meals:
        reserved_count = Reservation.query.filter_by(meal_name=meal.name, status='Approved').count()
        stock_dict[meal.name] = meal.stock - reserved_count
    return stock_dict




@app.route('/menu')
def menu():
    if 'user_id' not in session:
        return redirect('/login')

    meals = Meal.query.all()
    stock_dict = get_meal_stock()  # use this instead of meal.stock
    is_admin = session.get('is_admin', False)

    return render_template('menu.html', meals=meals, stock_dict=stock_dict, is_admin=is_admin)


@app.route('/admin/menu')
def admin_dashboard_menu():  
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')

    meals = Meal.query.all()
    stock_dict = get_meal_stock()  # use this instead of meal.stock

    return render_template('menu.html', meals=meals, stock_dict=stock_dict, is_admin=True)



@app.route('/')
def home():
    return redirect('/login')


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form['identifier']   # email OR mobile
        password = request.form['password']

        user = User.query.filter(
            (User.email == identifier) | (User.mobile == identifier)
        ).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin  # store admin status

            # Redirect based on role
            if user.is_admin:
                return redirect("/admin")
            else:
                return redirect("/student")
        else:
            return render_template("login.html", error="Invalid login details")

    return render_template("login.html")




# ---------- SIGNUP ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Use .get() to avoid KeyError
        first_name = request.form.get('first_name', '').strip()
        last_name  = request.form.get('last_name', '').strip()
        email      = request.form.get('email', '').strip()
        mobile     = request.form.get('mobile', '').strip()
        password   = request.form.get('password', '').strip()

        # Basic validation
        if not all([first_name, last_name, email, mobile, password]):
            return render_template('signup.html', error="All fields are required.")

        # Check if user exists
        if User.query.filter_by(email=email).first() or User.query.filter_by(mobile=mobile).first():
            return render_template('signup.html', error="User already exists.")

        # Hash password and create user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        # Redirect to login
        return redirect('/login')

    # GET request
    return render_template('signup.html')




# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/student')
def student_dashboard():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect('/login')

    user = User.query.get(session['user_id'])
    reservations = Reservation.query.filter_by(user_id=user.id).all()

    # Only consider approved reservations for stats
    approved_reservations = Reservation.query.filter_by(status='Approved').all()

    # Most popular meals (approved only)
    popular = (
        db.session.query(Reservation.meal_name, func.count(Reservation.meal_name))
        .filter(Reservation.status == 'Approved')
        .group_by(Reservation.meal_name)
        .order_by(func.count(Reservation.meal_name).desc())
        .limit(5)
        .all()
    )

    # Busiest time slots (approved only)
    busy = (
        db.session.query(Reservation.time_slot, func.count(Reservation.time_slot))
        .filter(Reservation.status == 'Approved')
        .group_by(Reservation.time_slot)
        .order_by(func.count(Reservation.time_slot).desc())
        .limit(5)
        .all()
    )

    # Total price of approved reservations
    total_price = sum(r.price for r in reservations if r.status == 'Approved')

    # ML Predictions (pass approved reservations)
    approved_reservations = Reservation.query.filter_by(status='Approved').all()
    prediction_popular = predict_popular_meal(approved_reservations)
    prediction_rush = predict_rush_hour(approved_reservations)

    return render_template(
        'student_dashboard.html',
        user=user,
        reservations=reservations,
        popular=popular,
        busy=busy,
        total_price=total_price,
        prediction_popular=prediction_popular,
        prediction_rush=prediction_rush
    )




# ---------- RESERVE A MEAL ----------
@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])  

    # Fetch meals from DB, not from meal_data
    meals = Meal.query.all()
    stock_dict = get_meal_stock()

    if request.method == 'POST':
        meal_name = request.form['meal']
        time_slot = request.form['time_slot']

        meal = Meal.query.filter_by(name=meal_name).first()
        if not meal:
            flash('Meal not found')
            return redirect('/reserve')

        if stock_dict[meal_name] <= 0:
            flash(f"Sorry, {meal_name} is out of stock today!")
            return redirect('/reserve')

        stock_dict[meal_name] -= 1

        new_res = Reservation(
            user_id=user.id,
            meal_name=meal_name,
            date=datetime.today().date(),
            time_slot=time_slot,
            price=meal.price,
            status='Approved'
        )
        db.session.add(new_res)
        db.session.commit()

        flash(f"Reservation successful for {meal_name}. Remaining stock: {stock_dict[meal_name]}")
        return redirect('/student')

    return render_template('reserve.html', meals=meals, stock_dict=stock_dict, user=user)




# ---------- CANCEL RESERVATION ----------
@app.route('/cancel_reservation', methods=['POST'])
def cancel_reservation():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect('/login')

    res_id = request.form['res_id']
    res = Reservation.query.get(res_id)

    # Compare user_id, not the user object
    if res and res.user_id == session['user_id']:
        db.session.delete(res)
        db.session.commit()
        flash(f'Reservation for {res.meal_name} cancelled.')
    else:
        flash('You cannot cancel this reservation.')

    return redirect('/student')




# ---------- ADMIN DASHBOARD ----------
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')

    reservations = Reservation.query.order_by(Reservation.id.asc()).all()
    users = User.query.all()

    return render_template('admin_dashboard.html', reservations=reservations, users=users)


# Add to cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect('/login')

    meal_name = request.form['meal_name']
    meal_price = float(request.form['meal_price'])
    time_slot = request.form['time_slot']
    date_obj = datetime.strptime(request.form['date'], '%Y-%m-%d').date()

    new_res = Reservation(
        user_id=session['user_id'],
        meal_name=meal_name,
        price=meal_price,
        time_slot=time_slot,
        date=date_obj,
        status='Pending'
    )

    db.session.add(new_res)
    db.session.commit()

    flash(f"{meal_name} added to your cart!")
    return redirect('/cart')




# View cart
@app.route('/cart')
def cart():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect('/login')

    # Get all pending reservations for this user
    reservations = Reservation.query.filter_by(
        user_id=session['user_id'], status='Pending'
    ).all()

    # Calculate total price
    total_price = sum(r.price for r in reservations)

    return render_template('cart.html', reservations=reservations, total_price=total_price)





# Payment route (Stripe example)
@app.route('/pay', methods=['POST'])
def pay():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect('/login')

    method = request.form.get("payment_method")
    amount = float(request.form.get("amount", 0))

    if amount <= 0:
        flash("Invalid amount!")
        return redirect('/cart')

    # DEBUG PRINT
    print("PAYMENT METHOD:", method)

    # --- CARD ---
    if method == "card":
        card_number = request.form.get("card_number")
        exp_date = request.form.get("exp_date")
        cvv = request.form.get("cvv")

        if not (card_number and exp_date and cvv):
            flash("Please fill all card details.")
            return redirect('/cart')

        if len(card_number) != 16:
            flash("Invalid card number!")
            return redirect('/cart')

        if len(cvv) != 3:
            flash("Invalid CVV!")
            return redirect('/cart')

        flash("Card payment successful! ✔")


    # --- CASH ---
    elif method == "cash":
        flash("Cash payment selected! ✔")


    # Update the reservations
    reservations = Reservation.query.filter(
        Reservation.user_id == session['user_id'],
        Reservation.status.ilike("pending")
    ).all()

    print("PENDING RESERVATIONS:", reservations)

    for r in reservations:
        r.status = "Approved"
        r.payment_method = method 

    db.session.commit()

    flash("Payment successful! Your reservations are confirmed.")
    return redirect('/student')




@app.route('/admin/menu/add', methods=['GET', 'POST'])
def add_meal():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        desc = request.form['desc']
        stock = int(request.form['stock'])
        image = request.files['image']

        image_filename = image.filename
        image.save(f'static/images/{image_filename}')

        new_meal = Meal(name=name, price=price, description=desc, stock=stock, img=image_filename)
        db.session.add(new_meal)
        db.session.commit()
        flash('Meal added successfully!')
        return redirect('/admin/menu')

    return render_template('add_meal.html')


@app.route('/admin/menu/edit/<int:meal_id>', methods=['GET', 'POST'])
def edit_meal(meal_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')

    meal = Meal.query.get_or_404(meal_id)
    if request.method == 'POST':
        meal.name = request.form['name']
        meal.price = float(request.form['price'])
        meal.description = request.form['desc']
        meal.stock = int(request.form['stock'])
        
        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                image.save(f'static/images/{image.filename}')
                meal.img = image.filename

        db.session.commit()
        flash('Meal updated successfully!')
        return redirect('/admin/menu')

    return render_template('edit_meal.html', meal=meal)


@app.route('/admin/menu/delete/<int:meal_id>', methods=['POST'])
def delete_meal(meal_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')

    meal = Meal.query.get_or_404(meal_id)
    db.session.delete(meal)
    db.session.commit()
    flash('Meal deleted successfully!')
    return redirect('/admin/menu')

@app.route('/admin/meals')
def admin_meals():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/admin-login')

    meals = Meal.query.all()
    return render_template('admin_meals.html', meals=meals)


def sync_meals():
    """Ensure DB has all meals from meal_data"""
    for m in meal_data:
        existing = Meal.query.filter_by(name=m['name']).first()
        if not existing:
            meal = Meal(
                name=m['name'],
                price=m['price'],
                description=m['desc'],
                stock=m['initial_stock'],
                img=m['img']
            )
            db.session.add(meal)
    db.session.commit()


# ------------------ RUN APP ------------------
if __name__ == "__main__":
    create_admin()  # create admin if not exists
    with app.app_context():
        db.create_all()   # make sure tables exist
        sync_meals()      # populate DB with initial meals if missing
    app.run(debug=True)


