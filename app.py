from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv
import socket


load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
    # Force IPv4 for DNS resolution
    import socket
    original_getaddrinfo = socket.getaddrinfo
    def getaddrinfo_ipv4_only(*args, **kwargs):
        return [info for info in original_getaddrinfo(*args, **kwargs) if info[0] == socket.AF_INET]
    socket.getaddrinfo = getaddrinfo_ipv4_only

    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

@app.route('/')
def index():
    return render_template('survey.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    required_fields = ['name', 'age', 'gender', 'company', 'role']
    if not all(data.get(field) for field in required_fields):
        return jsonify({'message': 'All fields are required.'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO responses (name, age, gender, company, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['name'], data['age'], data['gender'], data['company'], data['role']))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Survey submitted successfully!'})
    except Exception as e:
        print("Database error:", e)
        return jsonify({'message': 'Server error occurred.'}), 500
    
@app.route("/dbtest")
def dbtest():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return f"✅ DB is connected. Server time is: {result[0]}"
    except Exception as e:
        return f"❌ Database connection failed: {e}"    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
