from flask import Flask, render_template, redirect, url_for, session, flash, abort, request, jsonify
import random
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secret-key'


FAKE_USERS = {
    'jdoe': {
        'password': 'password',
        'company_name': 'John Doe Construction',
        'address': '123 Builder Lane, Los Angeles, CA 90001',
        'credit_limit': 20000.00,
        'orders': []
    },
    'reject': {
        'password': 'password',
        'company_name': 'Reject Electricals',
        'address': '456 Power Ave, Los Angeles, CA 90002',
        'credit_limit': 0.00,
        'orders': []
    },
    'fraud': {
        'password': 'password',
        'company_name': 'Fraudulent Fixtures Inc.',
        'address': '789 Shadow St, Los Angeles, CA 90003',
        'credit_limit': 20000.00,
        'orders': []
    },
    'otp': {
        'password': 'password',
        'company_name': 'One-Time Parts Co.',
        'address': '101 Supply Rd, Los Angeles, CA 90004',
        'credit_limit': 20000.00,
        'orders': []
    },
    'guestcheckout': {
        'password': 'password',
        'company_name': None,
        'address': None,
        'credit_limit': 0.00,
        'orders': []
    },
}

CURRENCY_RATES = {
    'USD': {'rate': 1.0, 'symbol': '$'},
    'GBP': {'rate': 0.82, 'symbol': '£'},
    'EUR': {'rate': 0.95, 'symbol': '€'},
}

FAKE_PRODUCTS = [
    {
        'id': 1,
        'name': 'DEWALT 20-Volt MAX Cordless Drill',
        'price': 159.00,
        'image': 'images/img1.jpg',
        'description': 'Powerful and compact for drilling and fastening in tight spaces. Features a high-performance motor that delivers 300 unit watts out (UWO) of power.',
        'reviews': [
            {'user': 'ToolMaster123', 'rating': 5, 'comment': 'Fantastic drill, gets every job done with ease. Battery life is superb!'},
            {'user': 'DIY_Dad', 'rating': 4, 'comment': 'Good value for money. A bit heavy, but very powerful.'},
            {'user': 'ProBuilder', 'rating': 5, 'comment': 'My go-to drill for all professional work. Highly recommend.'},
        ]
    },
    {
        'id': 2,
        'name': 'Ryobi ONE+ 18V Inflator/Deflator',
        'price': 79.99,
        'image': 'images/img2.jpg',
        'description': 'Inflates car tires, sports equipment, and air mattresses with ease. Also features a deflation mode for quick pack-up.',
        'reviews': [
            {'user': 'CampLover', 'rating': 5, 'comment': 'Perfect for camping trips! Inflates our air mattress in minutes.'},
            {'user': 'CarGuy', 'rating': 4, 'comment': 'Handy for car tires. A little noisy but effective.'},
        ]
    },
    {
        'id': 3,
        'name': 'Husky 6 ft. Folding Workbench',
        'price': 129.00,
        'image': 'images/img3.jpg',
        'description': 'Heavy-duty steel construction with a durable wooden top. Folds flat for easy storage and portability.',
        'reviews': [
            {'user': 'GarageGeek', 'rating': 5, 'comment': 'Solid workbench, easy to set up and fold away. Great for small spaces.'},
            {'user': 'WoodWorker', 'rating': 4, 'comment': 'Could use a bit more weight for serious woodworking, but otherwise very good.'},
        ]
    },
    {
        'id': 4,
        'name': 'Philips Hue Smart Bulb Starter Kit',
        'price': 199.00,
        'image': 'images/img4.jpg',
        'description': 'Personal wireless lighting system. Control your lights from anywhere with the Philips Hue app.',
        'reviews': [
            {'user': 'TechSavvy', 'rating': 5, 'comment': 'Transforms my living room! The colors are vibrant and integration is seamless.'},
            {'user': 'SmartHomeFan', 'rating': 4, 'comment': 'A bit pricey, but worth it for the convenience and ambiance.'},
        ]
    },
    {
        'id': 5,
        'name': 'Milwaukee M18 Fuel Sawzall',
        'price': 249.00,
        'image': 'images/img5.jpg',
        'description': 'The fastest cutting 18-Volt reciprocating saw on the market. Delivers legendary Milwaukee power and durability.',
        'reviews': [
            {'user': 'ContractorPro', 'rating': 5, 'comment': 'Unstoppable! Cuts through anything. A must-have for demo work.'},
            {'user': 'WeekendWarrior', 'rating': 5, 'comment': 'Amazingly powerful, makes quick work of tough jobs.'},
        ]
    },
    {
        'id': 6,
        'name': 'Gorilla Ladders 3-Step Ladder',
        'price': 49.97,
        'image': 'images/img6.jpeg',
        'description': 'Lightweight and sturdy aluminum construction. Features a large platform for comfortable standing.',
        'reviews': [
            {'user': 'HomeFixer', 'rating': 4, 'comment': 'Perfect height for household tasks. Folds up nicely.'},
            {'user': 'SafetyFirst', 'rating': 5, 'comment': 'Very stable, feel safe using it.'},
        ]
    },
    {
        'id': 7,
        'name': 'EGO POWER+ 56V Cordless Blower',
        'price': 219.00,
        'image': 'images/img7.jpg',
        'description': 'Industry-leading power and performance. Variable speed control and turbine fan engineering.',
        'reviews': [
            {'user': 'YardWorkHero', 'rating': 5, 'comment': 'Amazingly powerful for a cordless blower. Battery lasts long enough for my yard.'},
            {'user': 'GreenThumb', 'rating': 4, 'comment': 'Quiet and efficient. Great for clearing leaves quickly.'},
        ]
    },
    {
        'id': 8,
        'name': 'Ring Video Doorbell 4',
        'price': 179.99,
        'image': 'images/img8.jpg',
        'description': 'Improved battery life and color pre-roll video. See, hear, and speak to visitors from anywhere.',
        'reviews': [
            {'user': 'SecurityMinded', 'rating': 5, 'comment': 'Works flawlessly, excellent video quality and motion detection.'},
            {'user': 'TechieHome', 'rating': 4, 'comment': 'A bit tricky to install for a beginner, but worth it.'},
        ]
    },
    {
        'id': 9,
        'name': 'Levoit Core 300 Air Purifier',
        'price': 99.99,
        'image': 'images/img9.jpg',
        'description': 'True HEPA filter captures 99.97% of airborne particles. Quiet operation with a compact design.',
        'reviews': [
            {'user': 'AllergySufferer', 'rating': 5, 'comment': 'Helped my allergies significantly! Very quiet on low settings.'},
            {'user': 'CleanAir', 'rating': 5, 'comment': 'Noticeable difference in air quality. Great for bedrooms.'},
        ]
    },
    {
        'id': 10,
        'name': 'Anker Nebula Solar Portable Projector',
        'price': 599.00,
        'image': 'images/img10.jpg',
        'description': 'Full HD 1080p portable projector with Android TV 9.0. Cinematic viewing experience anywhere.',
        'reviews': [
            {'user': 'MovieBuff', 'rating': 5, 'comment': 'Incredible picture quality for a portable projector. Perfect for backyard movies.'},
            {'user': 'GadgetLover', 'rating': 4, 'comment': 'Battery life could be longer, but the image and sound are great.'},
        ]
    },
]

FAKE_COMPANIES = [
    {'name': 'Golden State Builders, Inc.', 'address': '123 Market St, San Francisco, CA'},
    {'name': 'Pacific Crest Construction', 'address': '456 Ocean Ave, Los Angeles, CA'},
    {'name': 'Sierra Nevada Contractors', 'address': '789 Pine Rd, Lake Tahoe, CA'},
]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You must be logged in to view this page.', 'info')
            # Redirect to login, passing the page they wanted to visit
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# Add this function to make the rates available to all templates ---
@app.context_processor
def inject_currencies():
    return dict(CURRENCY_RATES=CURRENCY_RATES, current_currency=session.get('currency', 'USD'))

# Add this custom filter to format prices ---
@app.template_filter('to_currency')
def to_currency_filter(value):
    currency_code = session.get('currency', 'USD') # Default to USD
    currency = CURRENCY_RATES.get(currency_code, CURRENCY_RATES['USD'])
    
    converted_value = value * currency['rate']
    symbol = currency['symbol']
    
    return f"{symbol}{converted_value:,.2f}"

# Add this new route to handle currency switching ---
@app.route('/set_currency/<currency>')
def set_currency(currency):
    if currency in CURRENCY_RATES:
        session['currency'] = currency
    # Redirect back to the page the user was on
    return redirect(request.referrer or url_for('index'))


@app.route('/profile')
@login_required
def profile():
    username = session['username']
    user_data = FAKE_USERS.get(username).copy()

    # This block correctly updates user_data for a returning guest
    if username == 'guestcheckout' and 'guest_company_details' in session:
        user_data.update(session['guest_company_details'])
    
    available_credit = get_available_credit(user_data)
    
    # Pass both the base user data and the calculated credit to the template
    return render_template('profile.html', user=user_data, available_credit=available_credit)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = FAKE_USERS.get(username)
        if user_data and user_data['password'] == password:
            session['username'] = username
            if username == "jdoe":
                flash(f'Welcome back, {username}!', 'success')
            
            # Check for a 'next' page in the URL and redirect there
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('guest_company_details', None)
    session['cart'] = []
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/')
def index():
    # Check if we've already shown the pop-up in this session
    popup_shown = session.get('popup_shown', False)
    if not popup_shown:
        # If not, set the flag so it doesn't show again
        session['popup_shown'] = True

    # Process products to add average ratings
    products_with_ratings = []
    for product in FAKE_PRODUCTS:
        product_copy = product.copy()
        if product_copy.get('reviews'):
            avg_rating = sum(r['rating'] for r in product_copy['reviews']) / len(product_copy['reviews'])
        else:
            avg_rating = 0
        product_copy['avg_rating'] = avg_rating
        products_with_ratings.append(product_copy)
        
    # Pass the initial state of the flag to the template
    return render_template('index.html', products=products_with_ratings, show_popup=(not popup_shown))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in FAKE_PRODUCTS if p['id'] == product_id), None)
    
    if product is None:
        abort(404)

    # Calculate average rating for display
    if product['reviews']:
        avg_rating = sum(r['rating'] for r in product['reviews']) / len(product['reviews'])
    else:
        avg_rating = 0
        
    return render_template('product_detail.html', product=product, avg_rating=avg_rating)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    
    session['cart'].append(product_id)
    session.modified = True
    
    # Instead of redirecting, return a JSON response
    return jsonify({
        'status': 'success',
        'message': 'Product added to cart!',
        'cart_count': len(session['cart'])
    })

# In your app.py, find the view_cart() function
@app.route('/cart')
def view_cart():
    cart_product_ids = session.get('cart', [])
    
    product_counts = {}
    for product_id in cart_product_ids:
        product_counts[product_id] = product_counts.get(product_id, 0) + 1
            
    cart_products = []
    for product_id, count in product_counts.items():
        product_info = next((p for p in FAKE_PRODUCTS if p['id'] == product_id), None)
        if product_info:
            cart_products.append({
                'id': product_info['id'],
                'name': product_info['name'],
                'price': product_info['price'],
                'image': product_info['image'], # ADD THIS LINE
                'quantity': count,
                'subtotal': product_info['price'] * count
            })
    
    total_price = sum(item['subtotal'] for item in cart_products)
    
    return render_template('cart.html', cart_items=cart_products, total=total_price)


@app.route('/remove_from_cart/<int:product_id>', methods=['POST']) # IMPORTANT: Add methods=['POST']
def remove_from_cart(product_id):
    if 'cart' in session and product_id in session['cart']:
        session['cart'].remove(product_id)
        session.modified = True
        
        # After removing, return the new cart status as JSON
        return jsonify({
            'status': 'success',
            'message': 'Product removed from cart.',
            'cart_count': len(session['cart'])
        })
        
    return jsonify({'status': 'error', 'message': 'Item not found in cart'}), 400


@app.route('/checkout')
@login_required
def checkout():
    payment_method = request.args.get('method', 'Unknown')
    session['payment_method'] = payment_method
    
    username = session.get('username')
    user_data = FAKE_USERS.get(username, {}).copy() # Get a mutable copy

    is_returning_guest = username == 'guestcheckout' and 'guest_company_details' in session

    if username == 'guestcheckout' and not is_returning_guest:
        # This logic now only applies to a NEW guest checkout user
        if session.get('payment_method') == 'allianz':
            return redirect(url_for('verify_otp'))
        else:
            # A new guest using CC or ACH checks out immediately
            create_new_order(username)
            session.pop('cart', None)
            flash('Success! Your order has been placed.', 'success')
            return redirect(url_for('profile'))

    if is_returning_guest:
        user_data.update(session['guest_company_details'])

    # --- Proceed with existing user-specific workflows ---
    if username == 'reject':
        flash('Payment Rejected. Your payment method was declined.', 'error')
        return redirect(url_for('view_cart'))

    elif username == 'fraud':
        company_name = user_data.get('company_name', 'Your Company')
        flash('For your security, please verify your identity to complete this transaction.', 'info')
        return redirect(url_for('verify_identity', company_name=company_name))

    elif username == 'otp':
        return redirect(url_for('verify_otp'))

    else: # This block now handles 'jdoe' AND returning 'guestcheckout' users
        if session.get('payment_method') == 'allianz':
            cart_total = get_cart_total()
            available_credit = get_available_credit(user_data)
            
            if cart_total > available_credit:
                flash(f"Credit limit exceeded. Your available credit is {available_credit:,.2f} but the order total is {cart_total:,.2f}.", 'error')
                return redirect(url_for('view_cart'))
            else:
                create_new_order(username)
                session.pop('cart', None)
                flash('Success! Your order has been placed on account.', 'success')
                return redirect(url_for('profile'))
        else:
            create_new_order(username)
            session.pop('cart', None)
            flash('Success! Your order has been placed on account.', 'success')
            return redirect(url_for('profile'))

@app.route('/verify_otp', methods=['GET', 'POST'])
@login_required
def verify_otp():
    username = session.get('username')
    # Update protection to allow both users
    if username not in ['otp', 'guestcheckout']:
        flash('Invalid access to OTP page.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        
        # Logic for 'guestcheckout'
        if username == 'guestcheckout':
            if otp_code == '1234':
                # Correct OTP, proceed to company registration
                return redirect(url_for('register_company'))
            else:
                flash('Invalid OTP code. Please try again.', 'error')
        elif username == 'otp':
            if otp_code == '1234':
                if session.get('payment_method') == 'allianz':
                    cart_total = get_cart_total()
                    username = session.get('username')
                    user_data = FAKE_USERS.get(username, {}).copy() # Get a mutable copy

                    is_returning_guest = username == 'guestcheckout' and 'guest_company_details' in session
                    if is_returning_guest:
                        user_data.update(session['guest_company_details'])
                    available_credit = get_available_credit(user_data)
                    
                    if cart_total > available_credit:
                        flash(f"Credit limit exceeded. Your available credit is {available_credit:,.2f} but the order total is {cart_total:,.2f}.", 'error')
                        return redirect(url_for('view_cart'))
                create_new_order(username) # Add the order to history
                session.pop('cart', None)
                flash('Payment verified and order confirmed!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Invalid OTP code. Please try again.', 'error')    
    return render_template('otp.html')


@app.route('/register_company', methods=['GET', 'POST'])
@login_required
def register_company():
    if session.get('username') != 'guestcheckout':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # In a real app, you'd save this form data
        return redirect(url_for('select_company'))
        
    return render_template('register_company.html')


def create_new_order(username):
    # This function creates an order and adds it to the user's history
    if 'cart' not in session or not session.get('cart'):
        return

    # Calculate total price from cart
    total_price = 0
    for product_id in session.get('cart', []):
        product = next((p for p in FAKE_PRODUCTS if p['id'] == product_id), None)
        if product:
            total_price += product['price']
    
    # Create the new order dictionary
    new_order = {
        'id': f'ORD-{random.randint(1000, 9999)}',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total': total_price,
        'status': 'Processing',
        'payment_method': session.get('payment_method', 'N/A').replace('-', ' ').title()
    }

    # Add the new order to the top of the user's order list
    if username in FAKE_USERS:
        FAKE_USERS[username]['orders'].insert(0, new_order)

@app.route('/select_company')
@login_required
def select_company():
    if session.get('username') != 'guestcheckout':
        return redirect(url_for('login'))
    return render_template('select_company.html', companies=FAKE_COMPANIES)


@app.route('/verify_identity/<company_name>')
@login_required
def verify_identity(company_name):
    """This page displays the verification options and saves the company context."""
    username = session.get('username')
    if username not in ['guestcheckout', 'fraud']:
        return redirect(url_for('login'))
    
    # Store the company name in the session for the next step
    if username == 'guestcheckout':
        session['verifying_company_name'] = company_name
    
    return render_template('verify_identity.html', company_name=company_name)

@app.route('/verification_success')
@login_required
def verification_success():
    """Handles a successful verification, saving company info and setting credit to $10k."""
    username = session.get('username')
    if username not in ['guestcheckout', 'fraud']:
        return redirect(url_for('login'))

    # If guest user, save their selected company info and new credit limit
    if username == 'guestcheckout':
        company_name = session.pop('verifying_company_name', None) # Get and clear the temp name
        if company_name:
            company_data = next((c for c in FAKE_COMPANIES if c['name'] == company_name), None)
            if company_data:
                # Save the company details with the approved credit limit
                session['guest_company_details'] = company_data
                session['guest_company_details']['credit_limit'] = 10000.00

    if session.get('payment_method') == 'allianz':
        cart_total = get_cart_total()
        username = session.get('username')
        user_data = FAKE_USERS.get(username, {}).copy() # Get a mutable copy

        is_returning_guest = username == 'guestcheckout' and 'guest_company_details' in session
        if is_returning_guest:
            user_data.update(session['guest_company_details'])
        available_credit = get_available_credit(user_data)
        
        if cart_total > available_credit:
            flash(f"Credit limit exceeded. Your available credit is {available_credit:,.2f} but the order total is {cart_total:,.2f}.", 'error')
            return redirect(url_for('view_cart'))
    create_new_order(username)
    session.pop('cart', None) 
    flash('Verification successful! Your order has been confirmed.', 'success')
    return redirect(url_for('profile'))

@app.route('/verification_failed')
@login_required
def verification_failed():
    """Handles a failed verification, saving company info and setting credit to $0."""
    username = session.get('username')
    if username not in ['guestcheckout', 'fraud']:
        return redirect(url_for('login'))

    # If guest user, save their selected company info but set credit to zero
    if username == 'guestcheckout':
        company_name = session.pop('verifying_company_name', None) # Get and clear the temp name
        if company_name:
            company_data = next((c for c in FAKE_COMPANIES if c['name'] == company_name), None)
            if company_data:
                # Save the company details with a zero credit limit
                session['guest_company_details'] = company_data
                session['guest_company_details']['credit_limit'] = 0.00

    flash('Verification failed. Your order was not processed. Please contact support.', 'error')
    return redirect(url_for('view_cart'))


@app.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    data = request.get_json()
    product_id = int(data.get('product_id'))
    new_quantity = int(data.get('quantity'))

    if 'cart' in session and product_id and new_quantity is not None:
        cart_items = session['cart']
        
        current_quantity = cart_items.count(product_id)
        diff = new_quantity - current_quantity
        
        if diff > 0:
            for _ in range(diff):
                cart_items.append(product_id)
        elif diff < 0:
            for _ in range(abs(diff)):
                if product_id in cart_items:
                    cart_items.remove(product_id)
        
        session.modified = True

        # Return the new cart count and total price
        return jsonify({
            'status': 'success',
            'message': 'Cart updated',
            'cart_count': len(session['cart']),
            'new_total': get_cart_total() # Use your helper function
        })

    return jsonify({'status': 'error', 'message': 'Invalid request'}), 400


def get_cart_total():
    """Calculates the total price of all items currently in the session cart."""
    total_price = 0
    for product_id in session.get('cart', []):
        product = next((p for p in FAKE_PRODUCTS if p['id'] == product_id), None)
        if product:
            total_price += product['price']
    return total_price

def get_available_credit(user_data):
    """Calculates a user's available credit by subtracting their Allianz orders."""
    # Start with the user's base credit limit
    initial_credit = user_data.get('credit_limit', 0)
    
    # Sum up the total of past orders paid for with Allianz Trade Pay
    spent_credit = sum(
        order['total'] for order in user_data.get('orders', [])
        if order.get('payment_method') == 'Allianz'
    )
    
    return initial_credit - spent_credit


if __name__ == '__main__':
    app.run(debug=True)