from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ShortURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(500), nullable=False)
    short = db.Column(db.String(10), nullable=False, unique=True)
    clicks = db.Column(db.Integer, default=0)

class IPAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    visit_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    short_url_id = db.Column(db.Integer, db.ForeignKey('short_url.id'), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

def random_string(length=10):
    result = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_link', methods=['POST'])
def add_link():
    original_url = request.form['url']
    existing_url = ShortURL.query.filter_by(original=original_url).first()

    if existing_url:
        short_url = existing_url.short
    else:
        short_url = random_string()
        new_url = ShortURL(original=original_url, short=short_url)
        db.session.add(new_url)
        db.session.commit()

    return render_template('short_url.html', short_url=short_url)

@app.route('/<short_url>')
def redirect_url(short_url):
    link = ShortURL.query.filter_by(short=short_url).first()
    if link:
        link.clicks += 1
        db.session.commit()
        ip_address = request.remote_addr
        ip_log = IPAddress(ip_address=ip_address, short_url_id=link.id)
        db.session.add(ip_log)
        db.session.commit()
        return redirect(link.original)
    else:
        flash('Invalid URL', 'danger')
        return redirect(url_for('index'))

@app.route('/view_ips/<short_url>')
def view_ips(short_url):
    link = ShortURL.query.filter_by(short=short_url).first()
    if link:
        ip_addresses = IPAddress.query.filter_by(short_url_id=link.id).all()
        return render_template('view_ips.html', ip_addresses=ip_addresses)
    else:
        flash('Invalid URL', 'danger')
        return redirect(url_for('index'))

@app.route('/urls')
def urls():
    links = ShortURL.query.all()
    return render_template('urls.html', links=links)

if __name__ == '__main__':
    app.run(debug=True)
