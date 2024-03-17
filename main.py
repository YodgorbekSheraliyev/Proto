from flask import Flask, jsonify
import psycopg2
import requests

app = Flask(__name__)

# Heroku PostgreSQL database connection
DATABASE_URL = "postgres://u5n1q6udoiquuj:p85d60a7dbe8832e9a7e9ea3835b56cb3e027558618a477ba9cd3ad4f632ef1a3@ceu9lmqblp8t3q.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dfsveoilfa8jto"

# Function to fetch weather data from OpenWeatherMap API
def fetch_weather_data(city):
    try:
        api_key = "e31c6b0d086360e914790bc080b3e50d"
        city = "York"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        return data
    except Exception as e:
        print("Error fetching weather data:", e)
        return None

# Function to insert or update weather data into PostgreSQL database
def insert_or_update_weather_data(city, temperature, description):
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO weather_data (city, temperature, description) VALUES (%s, %s, %s) ON CONFLICT (city) DO UPDATE SET temperature = EXCLUDED.temperature, description = EXCLUDED.description", (city, temperature, description))
        conn.commit()
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print("Error inserting or updating weather data:", e)

# Function to fetch the latest weather data from the database
def get_latest_weather_data():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM weather_data WHERE city = %s", ("YourCityName",))
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        print("Error fetching latest weather data:", e)
        return None

@app.route('/')
def index():
    return 'Weather App'

@app.route('/weather', methods=['GET'])
def get_weather():
    # Fetch weather data from API
    city = "York"
    weather_data = fetch_weather_data(city)
    if weather_data:
        temperature = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        # Insert or update weather data into the database
        insert_or_update_weather_data(city, temperature, description)
    # Fetch latest weather data from the database
    data = get_latest_weather_data()
    if data:
        city, temperature, description = data
        weather = {
            'city': city,
            'temperature': temperature,
            'description': description
        }
        return jsonify(weather), 200
    else:
        return jsonify({'error': 'No data available'}), 404

if __name__ == '__main__':
    app.run(debug=True)
