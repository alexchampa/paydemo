from flask import Flask, render_template, redirect, url_for, session, flash, abort, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secret-key'


FAKE_USERS = {
    'jdoe': {
        'password': 'password',
        'company_name': 'John Doe Construction',
        'address': '123 Builder Lane, Los Angeles, CA 90001',
        'credit_limit': 50000.00,
        'orders': [
            {'id': 'ORD-1001', 'date': '2025-09-28', 'total': 159.00, 'status': 'Shipped'},
            {'id': 'ORD-1005', 'date': '2025-10-02', 'total': 49.97, 'status': 'Processing'},
        ]
    },
    'reject': {
        'password': 'password',
        'company_name': 'Reject Electricals',
        'address': '456 Power Ave, Los Angeles, CA 90002',
        'credit_limit': 10000.00,
        'orders': []
    },
    'fraud': {
        'password': 'password',
        'company_name': 'Fraudulent Fixtures Inc.',
        'address': '789 Shadow St, Los Angeles, CA 90003',
        'credit_limit': 0.00,
        'orders': [
            {'id': 'ORD-1002', 'date': '2025-09-29', 'total': 219.00, 'status': 'On Hold'},
        ]
    },
    'otp': {
        'password': 'password',
        'company_name': 'One-Time Parts Co.',
        'address': '101 Supply Rd, Los Angeles, CA 90004',
        'credit_limit': 25000.00,
        'orders': []
    },
    'guestcheckout': {
        'password': 'password',
        'company_name': 'Guest Services',
        'address': '111 Guest Pass, Los Angeles, CA 90005',
        'credit_limit': 500.00,
        'orders': []
    },
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

@app.route('/profile')
def profile():
    # Make sure user is logged in
    if 'username' not in session:
        flash('You must be logged in to view your profile.', 'error')
        return redirect(url_for('login'))

    username = session['username']
    user_data = FAKE_USERS.get(username)

    if not user_data:
        # This case is unlikely if session is managed properly, but it's safe to have
        flash('User not found.', 'error')
        return redirect(url_for('logout'))

    return render_template('profile.html', user=user_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = FAKE_USERS.get(username)
        # Check if user exists and password is correct
        if user_data and user_data['password'] == password:
            session['username'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
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

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    
    session['cart'].append(product_id)
    session.modified = True
    flash(f'Product added to your cart!', 'success')
    return redirect(url_for('index'))

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

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        if product_id in session['cart']:
            session['cart'].remove(product_id)
            session.modified = True
            flash('Product removed from your cart.', 'info')
            
    return redirect(url_for('view_cart'))

@app.route('/checkout')
def checkout():
    session.pop('cart', None)
    flash('Success! Your B2B order has been placed on account.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)