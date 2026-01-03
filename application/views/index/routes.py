from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
import os
import json
import requests
import time
from pathlib import Path
from .forms import LoginForm, AddItemForm

main = Blueprint("main", __name__)

# CS:GO wear float ranges
WEAR_LEVELS = {
    'FN': {'name': 'Factory New', 'min': 0.00, 'max': 0.07},
    'MW': {'name': 'Minimal Wear', 'min': 0.07, 'max': 0.15},
    'FT': {'name': 'Field-Tested', 'min': 0.15, 'max': 0.38},
    'WW': {'name': 'Well-Worn', 'min': 0.38, 'max': 0.45},
    'BS': {'name': 'Battle-Scarred', 'min': 0.45, 'max': 1.00}
}

# Load items from JSON
def load_items():
    items_path = Path(__file__).parent.parent.parent / 'static' / 'items.json'
    with open(items_path, 'r') as f:
        return json.load(f)

ITEMS = load_items()

def save_items(items):
    """Save items to JSON file"""
    items_path = Path(__file__).parent.parent.parent / 'static' / 'items.json'
    with open(items_path, 'w') as f:
        json.dump(items, f, indent=2)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_float_price(paint_index, def_index, min_float=0.00, max_float=0.07):
    """Fetch price from CSFloat with float range"""
    try:
        float_key = os.getenv('FLOAT_KEY')
        response = requests.get(
            f"https://csfloat.com/api/v1/listings?min_float={min_float}&max_float={max_float}&type=buy_now&limit=40&sort_by=lowest_price&def_index={def_index}&paint_index={paint_index}",
            headers={"Authorization": float_key},
            timeout=10
        )
        if response.status_code == 200:
            j = response.json()
            if j.get('data') and len(j['data']) > 0:
                price_cents = j['data'][0]['price']
                return price_cents / 100
        return None
    except Exception as e:
        print(f"Float error: {e}")
        return None

def get_steam_price(market_hash, wear_name):
    """Fetch price from Steam Community Market"""
    try:
        # Append wear condition to market hash: "Item Name (Wear Name)"
        modified_market_hash = market_hash + '%20%28' + wear_name.replace(' ', '%20') + '%29'
        
        response = requests.get(
            f"https://steamcommunity.com/market/priceoverview/?currency=1&appid=730&market_hash_name={modified_market_hash}",
            timeout=10
        )
        if response.status_code == 200:
            j = response.json()
            if j.get('success') and j.get('lowest_price'):
                # Parse price string like "$10.50" to float
                price_str = j['lowest_price'].replace('$', '').replace(',', '')
                return float(price_str)
        return None
    except Exception as e:
        print(f"Steam error: {e}")
        return None

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        env_username = os.getenv('LOGIN_USERNAME')
        env_password = os.getenv('LOGIN_PASSWORD')
        
        if username == env_username and password == env_password:
            session['logged_in'] = True
            return redirect(url_for('main.home'))
        else:
            time.sleep(3)  # 3 second delay on failed login
            form.username.errors.append('Invalid credentials')
    
    return render_template('login.html', form=form)

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@main.route('/')
@login_required
def home():
    return render_template('home.html', items=ITEMS, wear_levels=WEAR_LEVELS)

@main.route('/retrieve-prices', methods=['POST'])
@login_required
def retrieve_prices():
	data = request.json
	selected_items = data.get('selected_items', [])

	prices = []
	for item_data in selected_items:
		item_id = item_data['id']
		wear = item_data.get('wear', 'FN')
		
		# Find item in ITEMS list
		item = next((i for i in ITEMS if i['id'] == item_id), None)
		if not item:
			continue
		
		# Get float range for wear level
		wear_info = WEAR_LEVELS.get(wear, WEAR_LEVELS['FN'])
		
		# Get prices from both sources
		float_price = get_float_price(item['paint_index'], item['def_index'], wear_info['min'], wear_info['max'])
		steam_price = get_steam_price(item['market_hash'], wear_info['name'])
		
		price_data = {
			'item_id': item_id,
			'item_name': item['name'],
			'wear': wear,
			'wear_name': wear_info['name'],
			'float_price': float_price,
			'steam_price': steam_price,
			'difference': None
		}
		
		# Calculate difference if both prices available
		if float_price is not None and steam_price is not None:
			price_data['difference'] = round(steam_price - float_price, 2)

		prices.append(price_data)
	return jsonify({'prices': prices})

@main.route('/manage-items', methods=['GET', 'POST'])
@login_required
def manage_items():
	global ITEMS
	form = AddItemForm()
	message = None
	
	if request.method == 'POST':
		action = request.form.get('action')
		
		if action == 'add':
			if form.validate_on_submit():
				# Get highest ID and increment
				max_id = max([item['id'] for item in ITEMS], default=0)
				weapon = form.weapon.data
				skin = form.skin.data
				paint_index = form.paint_index.data
				def_index = form.def_index.data
				
				# Create full name and market hash
				full_name = f"{weapon} | {skin}"
				market_hash = requests.utils.quote(full_name)
				
				new_item = {
					'id': max_id + 1,
					'name': full_name,
					'market_hash': market_hash,
					'paint_index': paint_index,
                    'def_index': def_index
				}
				ITEMS.append(new_item)
				save_items(ITEMS)
				message = f"Item '{full_name}' added successfully"
				form = AddItemForm()  # Reset form
	
	return render_template('manage_items.html', items=ITEMS, message=message, form=form)

@main.route('/remove-item/<int:item_id>', methods=['DELETE'])
@login_required
def remove_item(item_id):
	global ITEMS
	ITEMS = [item for item in ITEMS if item['id'] != item_id]
	save_items(ITEMS)
	return jsonify({'success': True})
