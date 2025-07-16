import os
import re
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.', 'danger')
            return redirect(url_for('signup'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('weather'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    weather_data = None
    error = None
    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        if not city:
            error = "City name cannot be empty."
        else:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                weather_data = {
                    'city': data['name'],
                    'country': data['sys']['country'],
                    'description': data['weather'][0]['description'].capitalize(),
                    'temp': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'wind_speed': data['wind']['speed'],
                }
            else:
                error = "Please enter a valid city name."

    return render_template('weather.html', weather=weather_data, error=error)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)