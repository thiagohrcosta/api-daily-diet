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

# Logout user
@app.route('/logout', methods=['GET'])
@login_required
def logout():
  logout_user()
  return jsonify({'message': 'User logout successfully'})

# MEAL ROUTES

# Show Meal
@app.route('/meals/<int:id_meal>', methods=['GET'])
def get_meal(id_meal):
  meal = Meal.query.get(id_meal)

  if meal:
    return {
      'name': meal.name,
      'description': meal.description,
      'date': str(meal.date),
      'time': str(meal.time),
      'is_in_diet': meal.is_in_diet,
      'user_id': meal.user_id
    }

  return jsonify({'message': 'Meal not found.'}), 400

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

# Update meal
@app.route('/meals/<int:id_meal>', methods=['PATCH'])
@login_required
def update_meal(id_meal):
  data = request.json
  meal = Meal.query.get(id_meal)

  if meal.user_id != current_user.id:
    return jsonify({'message': 'Action not allowed.'}), 403
  
  date_formatted = None
  
  try:
    date_formatted = datetime.strptime(data.get('date'), '%m/%d/%y')
    time_formatted = datetime.strptime(data.get('time'), '%H:%M').time()
  except ValueError:
    return jsonify({'message': 'Invalid date or time format'}), 400
  
  meal.name = data.get('name')
  meal.description = data.get('description')
  meal.date = date_formatted
  meal.time = time_formatted
  meal.is_in_diet = data.get('is_in_diet')
  meal.user_id = current_user.id

  db.session.commit()

  meal = Meal.query.get(id_meal)


  return jsonify({'message': f'Meal {meal.name} sucessfully updated.'})

# Delete meal
@app.route('/meals/<int:id_meal>', methods=['DELETE'])
@login_required
def delete_meal(id_meal):
  meal = Meal.query.get(id_meal)

  if current_user.id != meal.user_id:
    return jsonify({'message': 'Action not allowed'}), 403
  
  if meal:
    db.session.delete(meal)
    db.session.commit()

    return jsonify({'message': 'Meal successfully deleted.'})


# LIST USERS MEALS
@app.route('/meals/user/<int:id_user>', methods=['GET'])
def show_user_meals(id_user):
  user = User.query.get(id_user)

  if not user:
    return jsonify({'message': 'User not found'}), 400

  if user:    
    meals = Meal.query.filter_by(user_id=id_user).all()

    if len(meals) == 0:
      return jsonify({'message': 'No meals found for this user.'})

    meals_data = [{
      'id': meal.id,
      'name': meal.name,
      'description': meal.description,
      'date': meal.date.strftime('%m/%d/%y'),
      'time': meal.time.strftime('%H:%M'), 
      'is_in_diet': meal.is_in_diet
    } for meal in meals]

    return jsonify(meals_data)
  

if __name__ == '__main__':
  app.run(debug=True)
