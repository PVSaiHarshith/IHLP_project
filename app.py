from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(), nullable=False)
    short_url = db.Column(db.String(10), nullable=False, unique=True)
    ip = db.Column(db.String(), nullable=False)

def generate_short_url():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def create_database_tables():
    with app.app_context():
        db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']
        short_url = generate_short_url()
        ip = request.remote_addr
        new_url = URL(long_url=long_url, short_url=short_url, ip=ip)
        db.session.add(new_url)
        db.session.commit()
        return f"Short URL: {request.url_root}{short_url}"
    return render_template('index.html')

@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    long_url = URL.query.filter_by(short_url=short_url).first().long_url
    return redirect(long_url)

if __name__ == '__main__':
    create_database_tables()
    app.run(debug=True)
