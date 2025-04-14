from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            room TEXT,
                            name TEXT,
                            date TEXT,
                            start_time TEXT,
                            end_time TEXT)''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        room = request.form['room']
        name = request.form['name']
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM bookings WHERE room=? AND date=? 
                AND ((start_time<? AND end_time>?) OR (start_time>=? AND start_time<?))
            """, (room, date, end_time, start_time, start_time, end_time))
            existing_booking = cursor.fetchone()
            
            if existing_booking:
                return "Room already booked for this time slot!"  
            
            cursor.execute("INSERT INTO bookings (room, name, date, start_time, end_time) VALUES (?, ?, ?, ?, ?)", 
                           (room, name, date, start_time, end_time))
            conn.commit()
        
        return redirect(url_for('view_bookings'))
    
    return render_template('reserve.html')

@app.route('/bookings')
def view_bookings():
    with sqlite3.connect('database.db') as conn:
        conn.row_factory = sqlite3.Row  # Fetch results as dictionaries
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings")
        bookings = cursor.fetchall()

    print([dict(row) for row in bookings])  # Debugging: Print bookings as dictionaries

    return render_template('bookings.html', bookings=bookings)


@app.route('/delete/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
        conn.commit()
    return redirect(url_for('view_bookings'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)