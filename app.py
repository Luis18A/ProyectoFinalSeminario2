from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login_screen.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard_index.html')

@app.route('/technician')
def technician():
    return render_template('technician_board.html')

@app.route('/admin')
def admin():
    return render_template('admin_analytics.html')

@app.route('/secretary')
def secretary():
    return render_template('secretary_view.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
