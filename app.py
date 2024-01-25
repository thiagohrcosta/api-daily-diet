import bcrypt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models.user import User
from models.meal import Meal
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin123@localhost:3306/daily-diet'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

# USER ROUTES

# Create User
@app.route('/user', methods=['POST'])
def create_user():
  data = request.json
  username = data.get('username')
  password = data.get('password')

  if username and password: 
    hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
    user = User(username=username, password=hashed_password, role='user')
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User successfully created.'})

  return jsonify({'message': 'Invalid data'}), 400

# Login User
@app.route('/login', methods=['POST'])
def login():
  data = request.json
  username = data.get('username')
  password = data.get('password')

  if username and password:
    user = User.query.filter_by(username=username).first()

    if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
      login_user(user)
      print(current_user.is_authenticated)
      return jsonify({'message': 'The user signed in successfully.'})
    
  return jsonify({'message': 'Invalid credentials'}), 400

# MEAL ROUTES

# Create Meal
@app.route('/meals', methods=['POST'])
@login_required
def create_meal():
  data = request.json
  name = data.get('name')
  description = data.get('description')
  meal_date = data.get('date')
  time = data.get('time')
  is_in_diet = data.get('is_in_diet')
  user_id = current_user.id

  try:
      date_formatted = datetime.strptime(meal_date, '%m/%d/%y')
      time_formatted = datetime.strptime(time, '%H:%M').time()
  except ValueError:
      return jsonify({'message': 'Invalid date or time format'}), 400

  if name and description and date_formatted and time_formatted:
      meal = Meal(
          name=name,
          description=description,
          date=date_formatted,
          time=time_formatted,
          is_in_diet=is_in_diet,
          user_id=user_id
      )
    
      db.session.add(meal)
      db.session.commit()

      return jsonify({'message': f'The meal {name} was successfully created'})

  return jsonify({'message': 'Invalid parameters'}), 400


if __name__ == '__main__':
  app.run(debug=True)
