import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
DB_NAME = "ethiopian_menu.db"


def init_db():
    """Initializes the database and seeds it with some traditional items if empty."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                price INTEGER NOT NULL
            )
        ''')

        # Seed initial data if the table is completely fresh
        cursor.execute("SELECT COUNT(*) FROM menu")
        if cursor.fetchone()[0] == 0:
            sample_dishes = [
                ("Doro Wat", "Stew (Wat)", 350),
                ("Kitfo", "Beef", 400),
                ("Injera Beyaynetu", "Vegetarian / Fasting", 250)
            ]
            cursor.executemany("INSERT INTO menu (name, type, price) VALUES (?, ?, ?)", sample_dishes)
            conn.commit()


# Single-file HTML layout using Jinja2 templates via render_template_string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ethio Flavor Hub</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; background-color: #fcf8f2; }
        h1 { color: #1e4620; text-align: center; border-bottom: 3px solid #f9b115; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #9b2c2c; color: white; }
        .form-box { background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; margin-top: 30px; }
        input, select, button { width: 100%; padding: 10px; margin: 8px 0; box-sizing: border-box; }
        button { background-color: #1e4620; color: white; border: none; font-weight: bold; cursor: pointer; }
        button:hover { background-color: #132e15; }
    </style>
</head>
<body>

    <h1>Ethio Flavor Hub Menu</h1>

    <table>
        <tr>
            <th>Dish Name</th>
            <th>Category</th>
            <th>Price (ETB)</th>
        </tr>
        {% for dish in dishes %}
        <tr>
            <td>{{ dish[1] }}</td>
            <td>{{ dish[2] }}</td>
            <td>{{ dish[3] }} Birr</td>
        </tr>
        {% endfor %}
    </table>

    <div class="form-box">
        <h3>Add Traditional Dish</h3>
        <form action="/add" method="POST">
            <input type="text" name="name" placeholder="e.g., Shiro Wat" required>
            <select name="type">
                <option value="Stew (Wat)">Stew (Wat)</option>
                <option value="Beef">Beef Dish</option>
                <option value="Vegetarian / Fasting">Vegetarian / Fasting</option>
                <option value="Breakfast">Breakfast</option>
            </select>
            <input type="number" name="price" placeholder="Price in Birr (ETB)" required min="1">
            <button type="submit">Save Dish</button>
        </form>
    </div>

</body>
</html>
"""


@app.route('/')
def index():
    # Fetch all items from SQLite database
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM menu")
        dishes = cursor.fetchall()
    return render_template_string(HTML_TEMPLATE, dishes=dishes)


@app.route('/add', methods=['POST'])
def add_dish():
    # Capture form parameters
    name = request.form.get('name')
    dish_type = request.form.get('type')
    price = request.form.get('price')

    if name and dish_type and price:
        # Write to SQLite database
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO menu (name, type, price) VALUES (?, ?, ?)", (name, dish_type, int(price)))
            conn.commit()

    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()  # Setup database tables on startup
    app.run(debug=True)