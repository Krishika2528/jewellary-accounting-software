from flask import Flask, render_template, request, redirect, jsonify
import json, os

app = Flask(__name__)

PRODUCTS_FILE = 'data.json'
PURCHASE_FILE = 'purchase.json'
SALES_FILE = 'sales.json'
CUSTOMER_FILE = 'customers.json'

def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, 'r') as f:
        return json.load(f)

def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def update_product_quantity(product_name, quantity_change, weight_change=0.0):
    data = load_data(PRODUCTS_FILE)
    found = False
    for item in data:
        if item['product'].lower() == product_name.lower():
            item['quantity'] += quantity_change
            item['weight'] += weight_change
            found = True
            break
    if not found:
        data.append({
            "product": product_name,
            "quantity": quantity_change,
            "weight": weight_change
        })
    save_data(PRODUCTS_FILE, data)

def load_customers():
    if not os.path.exists(CUSTOMER_FILE):
        return []
    try:
        return load_data(CUSTOMER_FILE)
    except json.JSONDecodeError:
        return []

def save_customer_if_new(name, contact):
    customers = load_customers()
    for customer in customers:
        if customer['name'].lower() == name.lower() or customer['contact'] == contact:
            return
    customers.append({"name": name, "contact": contact})
    save_data(CUSTOMER_FILE, customers)

@app.route('/get_customer', methods=['POST'])
def get_customer():
    data = request.json
    name = data.get('name', '').strip().lower()
    contact = data.get('contact', '').strip()
    customers = load_customers()

    for c in customers:
        if name and c['name'].lower() == name:
            return jsonify({"contact": c['contact']})
        if contact and c['contact'] == contact:
            return jsonify({"name": c['name']})
    return jsonify({})

@app.route('/', methods=['GET', 'POST'])
def product_page():
    if request.method == 'POST':
        selected_product = request.form['product']
        quantity = int(request.form['quantity'])
        weight = float(request.form['weight'])
        action = request.form.get('action')

        item = {
            "product": selected_product,
            "quantity": quantity,
            "weight": weight
        }

        if action == 'add':
            data = load_data(PRODUCTS_FILE)
            data.append(item)
            save_data(PRODUCTS_FILE, data)
            return redirect('/')

        # Get additional fields
        name = request.form['customer_name']
        contact = request.form['customer_contact']
        amount = float(request.form['amount'])
        payment_method = request.form['payment_method']
        purity_percentage = float(request.form['purity_percentage'])
        purity = weight * (purity_percentage / 100)

        # Save customer
        save_customer_if_new(name, contact)

        item.update({
            "name": name,
            "contact": contact,
            "amount": amount,
            "payment_method": payment_method,
            "purity_percentage": purity_percentage,
            "purity": purity
        })

        if action == 'purchase':
            purchases = load_data(PURCHASE_FILE)
            purchases.append(item)
            save_data(PURCHASE_FILE, purchases)
            update_product_quantity(selected_product, quantity, weight)
            return redirect('/purchase')

        elif action == 'sales':
            sales = load_data(SALES_FILE)
            sales.append(item)
            save_data(SALES_FILE, sales)
            update_product_quantity(selected_product, -quantity, -weight)
            return redirect('/sales')

    items = load_data(PRODUCTS_FILE)
    return render_template('index.html', items=items)

# Product Edit/Delete
@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    data = load_data(PRODUCTS_FILE)
    if item_id >= len(data): return redirect('/')
    if request.method == 'POST':
        data[item_id]['product'] = request.form['product']
        data[item_id]['quantity'] = request.form['quantity']
        data[item_id]['weight'] = request.form['weight']
        save_data(PRODUCTS_FILE, data)
        return redirect('/')
    return render_template('edit.html', item=data[item_id])

@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    data = load_data(PRODUCTS_FILE)
    if 0 <= item_id < len(data):
        del data[item_id]
        save_data(PRODUCTS_FILE, data)
    return redirect('/')

@app.route('/purchase', methods=['GET', 'POST'])
def show_purchases():
    purchases = load_data(PURCHASE_FILE)

    if request.method == 'POST':
        form = request.form
        product = form['product']
        quantity = int(form['quantity'])
        weight = float(form['weight'])
        name = form['name']
        contact = form['contact']
        amount = float(form['amount'])
        payment_method = form['payment_method']
        purity_percentage = float(form['purity_percentage'])
        purity = weight * (purity_percentage / 100)

        new_purchase = {
            "product": product,
            "quantity": quantity,
            "weight": weight,
            "name": name,
            "contact": contact,
            "amount": amount,
            "payment_method": payment_method,
            "purity_percentage": purity_percentage,
            "purity": purity
        }

        purchases.append(new_purchase)
        save_data(PURCHASE_FILE, purchases)
        update_product_quantity(product, quantity, weight)
        save_customer_if_new(name, contact)

        return redirect('/purchase')

    return render_template(
        'purchase.html',
        purchases=purchases,
        total_weight=round(sum(float(p['weight']) for p in purchases if 'weight' in p), 2),
        total_amount=round(sum(float(p['amount']) for p in purchases if 'amount' in p), 2)
    )

@app.route('/purchase/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_purchase(item_id):
    data = load_data(PURCHASE_FILE)
    if item_id >= len(data): return redirect('/purchase')
    if request.method == 'POST':
        data[item_id]['product'] = request.form['product']
        data[item_id]['quantity'] = request.form['quantity']
        data[item_id]['weight'] = request.form['weight']
        save_data(PURCHASE_FILE, data)
        return redirect('/purchase')
    return render_template('edit_purchase.html', item=data[item_id])

@app.route('/purchase/delete/<int:item_id>')
def delete_purchase(item_id):
    data = load_data(PURCHASE_FILE)
    if 0 <= item_id < len(data):
        del data[item_id]
        save_data(PURCHASE_FILE, data)
    return redirect('/purchase')

@app.route('/sales', methods=['GET', 'POST'])
def sales_page():
    sales = load_data(SALES_FILE)

    if request.method == 'POST':
        form = request.form
        product = form['product']
        quantity = int(form['quantity'])
        weight = float(form['weight'])
        name = form['name']
        contact = form['contact']
        amount = float(form['amount'])
        payment_method = form['payment_method']
        purity_percentage = float(form['purity_percentage'])
        purity = weight * (purity_percentage / 100)

        new_sale = {
            "product": product,
            "quantity": quantity,
            "weight": weight,
            "name": name,
            "contact": contact,
            "amount": amount,
            "payment_method": payment_method,
            "purity_percentage": purity_percentage,
            "purity": purity
        }

        sales.append(new_sale)
        save_data(SALES_FILE, sales)
        update_product_quantity(product, -quantity, -weight)
        save_customer_if_new(name, contact)

        return redirect('/sales')

    total_sold_weight = sum(item['weight'] for item in sales)
    return render_template('sales.html', sales=sales, total_weight=total_sold_weight)

@app.route('/sales/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_sale(item_id):
    data = load_data(SALES_FILE)
    if item_id >= len(data):
        return redirect('/sales')

    old_sale = data[item_id]

    if request.method == 'POST':
        old_quantity = int(old_sale['quantity'])
        old_weight_per_unit = float(old_sale['weight'])
        old_total_weight = old_quantity * old_weight_per_unit

        # 🧼 Revert old sale impact
        update_product_quantity(old_sale['product'], old_quantity, old_total_weight)

        # 🔄 Apply new changes
        new_product = request.form['product']
        new_quantity = int(request.form['quantity'])
        new_weight_per_unit = float(request.form['weight'])
        new_total_weight = new_quantity * new_weight_per_unit

        # Update sales record
        data[item_id] = {
            "product": new_product,
            "quantity": new_quantity,
            "weight": new_weight_per_unit
        }
        save_data(SALES_FILE, data)

        # 🚀 Apply new sale impact
        update_product_quantity(new_product, -new_quantity, -new_total_weight)

        return redirect('/sales')

    return render_template('edit_sales.html', item=old_sale)


@app.route('/sales/delete/<int:item_id>')
def delete_sale(item_id):
    data = load_data(SALES_FILE)
    if 0 <= item_id < len(data):
        deleted_sale = data.pop(item_id)
        save_data(SALES_FILE, data)
        update_product_quantity(deleted_sale['product'], int(deleted_sale['quantity']))
    return redirect('/sales')

if __name__ == '__main__':
    app.run(debug=True)
