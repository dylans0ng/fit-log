from flask import Flask, render_template, redirect, request, url_for, render_template_string, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from sqlalchemy import create_engine, inspect, desc
from sqlalchemy import and_

from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./main-db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'SOME KEY'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

bcrypt = Bcrypt(app)

db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)  

# Create the "Accounts" model
class Accounts(UserMixin, db.Model):
    __tablename__ = 'accounts'

    # Primary key
    accounts_id = db.Column('accounts_id', db.Integer, primary_key=True)

    # Other fields
    first_name = db.Column('first_name', db.String(15), nullable=False)
    last_name = db.Column('last_name', db.String(25), nullable=False)
    age = db.Column('age', db.Integer, nullable=False)
    account_email = db.Column('account_email', db.String, unique=True, nullable=False)
    account_password = db.Column('account_password', db.String, nullable=False)
    
    # An account can have many workouts (1 to many)
    workouts = db.relationship('Workout', backref='accounts') # Creates an "accounts" attribute to the child table, which is "workout"

    def get_id(self):
        return self.accounts_id

    def __repr__(self):
        return f'Account with the name of {self.first_name} {self.last_name} is {self.age} years old with an account id of {self.accounts_id}'
    
class WorkoutTimes(db.Model):
    __tablename__ = 'workout_times'

    # Primary key
    workout_time_of_day_id = db.Column('workout_time_of_day_id', db.Integer, primary_key=True)

    # Other fields
    workout_time_of_day = db.Column('workout_time_of_day', db.String(10), unique=True, nullable=False)
    time_of_day_description = db.Column('time_of_day_description', db.String, nullable=False)

    # Establishing the one to one relationship with the "Workout" table
    workout = db.relationship('Workout', backref='workout_times', uselist=False) # Saying "uselist=False" makes this a one-to-one

    def __init__(self, workout_time_of_day, time_of_day_description):
        self.workout_time_of_day = workout_time_of_day
        self.time_of_day_description = time_of_day_description

    def __repr__(self):
        return f'Workout time of day: ({self.workout_time_of_day})'

# Create a "Workout" model
class Workout(db.Model):
    __tablename__ = 'workout'

    # Primary key
    workout_id = db.Column('workout_id', db.Integer, primary_key=True)

    # Foreign keys
    accounts_id = db.Column(db.Integer, db.ForeignKey('accounts.accounts_id'), nullable=False)
    workout_time_of_day = db.Column(db.Integer, db.ForeignKey('workout_times.workout_time_of_day_id'), nullable=False)

    # Other fields
    workout_date = db.Column('Workout Date', db.String(15)) # Change this to a "Date" data type later and figure out how to declare this as a "datetime" format

    # A workout can have many exercises (1 to many)
    exercises = db.relationship('Exercises', backref='workouts')

    def __init__(self, accounts_id, workout_date, workout_time_of_day):
        self.accounts_id = accounts_id
        self.workout_date = workout_date
        self.workout_time_of_day = workout_time_of_day

    def __repr__(self):
        return f'(Workout Date: {self.workout_date})'
    
class ExerciseTypes(db.Model):
    __tablename__ = 'exercise_types'

    # Primary key
    exercise_type_id = db.Column('exercise_type_id', db.Integer, primary_key=True)

    # Other fields
    exercise_type = db.Column('exercise_type', db.String, unique=True, nullable=False)

    # Establish the one to one relationship with the "Exercises" table
    exercise = db.relationship('Exercises', backref='exercise_types', uselist=False)

    def __init__(self, exercise_type):
        self.exercise_type = exercise_type
        

    def __repr__(self):
        return f'(Type of Exercise: {self.exercise_type})'
    
# Create an "Exercises" model
class Exercises(db.Model):
    __tablename__ = 'exercises'

    # Primary key
    exercise_id = db.Column('exercise_id', db.Integer, primary_key=True)

    # Foreign keys
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.workout_id'), nullable=False)
    exercise_type_id = db.Column(db.Integer, db.ForeignKey('exercise_types.exercise_type_id'), nullable=False)

    # Other fields
    exercise_name = db.Column('exercise_name', db.String(50), nullable=False)
    number_of_sets = db.Column('number_of_sets', db.Integer, nullable=False)

    # An exercise can have many sets (1 to many)
    sets = db.relationship('Sets', backref='exercises')

    def __init__(self, workout_id, exercise_type_id, exercise_name, number_of_sets):
        self.workout_id = workout_id
        self.exercise_type_id = exercise_type_id
        self.exercise_name = exercise_name
        self.number_of_sets = number_of_sets

    def __repr__(self):
        return f'{self.number_of_sets} sets of {self.exercise_name}!'

class Sets(db.Model):
    __tablename__ = 'sets'

    # Primary key
    set_id = db.Column('set_id', db.Integer, primary_key=True)

    # Foreign key
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.exercise_id'), nullable=False)

    # Other fields
    set_number = db.Column('set_number', db.Integer, nullable=False)
    number_of_reps = db.Column('number_of_reps', db.Integer, nullable=False)
    weight_in_lbs = db.Column('weight_in_lbs', db.Integer, nullable=False)

    def __init__(self, exercise_id, set_number, number_of_reps, weight_in_lbs):
        self.exercise_id = exercise_id
        self.set_number = set_number
        self.number_of_reps = number_of_reps
        self.weight_in_lbs = weight_in_lbs

    def __repr__(self):
        return f'(Set Number: {self.set_number}), {self.number_of_reps} reps of {self.weight_in_lbs} pounds'

# Function that returns the list of tables in the database
def get_tables():
    engine = db.engine
    inspector = inspect(engine)

    tables = inspector.get_table_names()
    return tables

with app.app_context(): # While the app is running...
    tables = get_tables()
    
    if not tables: # If there are no tables in the database, then create all the tables.
        db.create_all()

    # Manually populate the "Workout Times" and "Exercise Types" tables
    morning = WorkoutTimes(workout_time_of_day='Morning', time_of_day_description='Testing')
    afternoon = WorkoutTimes(workout_time_of_day='Afternoon', time_of_day_description='Testing Testing')
    evening = WorkoutTimes(workout_time_of_day='Evening', time_of_day_description='Testing testing testing')

    morning_exists = WorkoutTimes.query.filter_by(workout_time_of_day='Morning').first()
    afternoon_exists = WorkoutTimes.query.filter_by(workout_time_of_day='Afternoon').first()
    evening_exists = WorkoutTimes.query.filter_by(workout_time_of_day='Evening').first()

    if not morning_exists:
        db.session.add(morning)
        db.session.commit()

    if not afternoon_exists:
        db.session.add(afternoon)
        db.session.commit()

    if not evening_exists:
        db.session.add(evening)
        db.session.commit()

    chest = ExerciseTypes(exercise_type='Chest')
    shoulders = ExerciseTypes(exercise_type='Shoulders')
    triceps = ExerciseTypes(exercise_type='Triceps')
    back = ExerciseTypes(exercise_type='Back')
    biceps = ExerciseTypes(exercise_type='Biceps')
    traps = ExerciseTypes(exercise_type='Traps')
    legs = ExerciseTypes(exercise_type='Legs')
    cardio = ExerciseTypes(exercise_type='Cardio')
    abs = ExerciseTypes(exercise_type='Abs')

    chest_exists = ExerciseTypes.query.filter_by(exercise_type='Chest').first()
    shoulders_exists = ExerciseTypes.query.filter_by(exercise_type='Shoulders').first()
    triceps_exists = ExerciseTypes.query.filter_by(exercise_type='Triceps').first()
    back_exists = ExerciseTypes.query.filter_by(exercise_type='Back').first()
    biceps_exists = ExerciseTypes.query.filter_by(exercise_type='Biceps').first()
    traps_exists = ExerciseTypes.query.filter_by(exercise_type='Traps').first()
    legs_exists = ExerciseTypes.query.filter_by(exercise_type='Legs').first()
    cardio_exists = ExerciseTypes.query.filter_by(exercise_type='Cardio').first()
    abs_exists = ExerciseTypes.query.filter_by(exercise_type='Abs').first()

    if not chest_exists:
        db.session.add(chest)
        db.session.commit()

    if not shoulders_exists:
        db.session.add(shoulders)
        db.session.commit()

    if not triceps_exists:
        db.session.add(triceps)
        db.session.commit()

    if not back_exists:
        db.session.add(back)
        db.session.commit()

    if not biceps_exists:
        db.session.add(biceps)
        db.session.commit()

    if not traps_exists:
        db.session.add(traps)
        db.session.commit()

    if not legs_exists:
        db.session.add(legs)
        db.session.commit()

    if not cardio_exists:
        db.session.add(cardio)
        db.session.commit()

    if not abs_exists:
        db.session.add(abs)
        db.session.commit()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html') # Prints out the user's full name only when they are logged in

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    elif request.method == 'POST':

        first_name = request.form['firstName']
        last_name = request.form['lastName']
        age = request.form['age']
        signup_email = request.form['email']
        signup_password = request.form['psw']

        hashed_signup_password = bcrypt.generate_password_hash(signup_password) # Hashes the password

        signup_email_exists = Accounts.query.filter(Accounts.account_email == signup_email).first()

        if not signup_email_exists: # If the sign up email does not exist in the database...
            # Adds the user input into the "Accounts" table
            account_db = Accounts(first_name=first_name, last_name=last_name, age=age, account_email=signup_email, account_password=hashed_signup_password)
            db.session.add(account_db)
            db.session.commit()
        else: # If the sign up email already exists in the database...
            print("You already have an email registered with us!")

        return redirect(url_for('index'))

# Given the accounts_id, return the Account associated with it (REQUIRED FOR THE FLASK-LOGIN LIBRARY!!!)
@login_manager.user_loader
def load_user(accounts_id):
    return db.session.get(Accounts, accounts_id)

@app.route('/account', methods=['GET', 'POST'])    
def account():
    if request.method == 'GET':
        return render_template('account.html')

    elif request.method == 'POST':
    
        login_email = request.form['email']
        login_password = request.form['psw']

        # Checks if the email and password that the user put in is inside the "Accounts" table
        correct_user = Accounts.query.filter(Accounts.account_email == login_email).first()
        
        # If the user's hashed password corresponds to the correct unhashed login password...
        if correct_user is not None and bcrypt.check_password_hash(correct_user.account_password, login_password):
            login_user(correct_user)
            return redirect(url_for('index')) 
        else:
            flash('Invalid email or password!', 'danger') # Flashes the red warning, which is handled in "account.html"
            return render_template('account.html') 

@app.route('/logout')
@login_required # Only works when you are logged in
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/log', methods=['GET', 'POST'])
def log():
    # Gets the id of the account that is currently logged in
    account_id = Accounts.get_id(load_user(db.session.query(Accounts.accounts_id).first())) 
    
    if request.method == 'GET':
        return render_template('log.html')
    
    elif request.method == 'POST':
        workout_date = request.form['workoutDate']
        time_of_day = request.form['workoutTimeOfDay']

        exercises = []
        exercises_num = request.form.get('numberOfExercises')
        
        for i in range(0, int(exercises_num)):
            exercise = {} # Creates an empty dictionary for each individual exercise
            reps_and_weights = [] # Creates an empty list for the reps and weights for each individual set

            type_of_exercise = request.form[f'typeOfExercise{i+1}']
            exercise_name = request.form[f'exerciseName{i+1}']
            total_sets = request.form[f'setsForExercise{i+1}']

            # Gets the Exercise Type ID based on what Exercise Type it is
            exercise_type_id = int(db.session.query(ExerciseTypes.exercise_type_id).filter(ExerciseTypes.exercise_type == type_of_exercise).scalar())

            exercise['Exercise Type ID'] = exercise_type_id # Creates a key-value pair
            exercise['Exercise Name'] = exercise_name # Creates a key-value pair
            exercise['Total Number of Sets'] = total_sets # Creates a key-value pair

            for j in range(0, int(total_sets)):
                reps = request.form[f'numberOfRepsFor_{i+1}_{j+1}']
                weight = request.form[f'totalWeightFor_{i+1}_{j+1}']

                # Adds each individual set to the list called "reps_and_weights"
                reps_and_weights.append({'Set Number': j+1, 'Reps': reps, 'Weight': weight}) 

            exercise['Sets'] = reps_and_weights # Creates a key-value pair

            exercises.append(exercise) # Appends the exercise dictionary into the "exercises" list

        workout_db = Workout(accounts_id=account_id, workout_date=workout_date, workout_time_of_day=time_of_day)

        # Adds the workout to the "Workout" table BEFORE adding the exercises to the "Exercises" table
        db.session.add(workout_db)
        db.session.commit()

        for row in exercises:
            # Gets the workout_id by getting the most recent workout_id value in the "Workout" table and getting the 0th index because .first() returns a tuple
            exercise_db = Exercises(workout_id=db.session.query(Workout.workout_id).order_by(desc(Workout.workout_id)).first()[0], exercise_type_id=row['Exercise Type ID'], exercise_name=row['Exercise Name'], number_of_sets=row['Total Number of Sets'])
            
            # Adds each exercise to the "Exercises" table BEFORE adding each set to the "Sets" table
            db.session.add(exercise_db)
            db.session.commit()

            for set_num in range(0, len(row['Sets'])):
                # Gets the exercise_id by getting the most recent exercise_id value in the "Exercises" table and getting the 0th index of the tuple
                sets_db = Sets(exercise_id=db.session.query(Exercises.exercise_id).order_by(desc(Exercises.exercise_id)).first()[0], set_number=row['Sets'][set_num]['Set Number'], number_of_reps=row['Sets'][set_num]['Reps'],
                               weight_in_lbs=row['Sets'][set_num]['Weight'])
                
                db.session.add(sets_db)
                db.session.commit()
        
        return render_template('log.html')

@app.route('/calendar', methods=['GET'])
def calendar():
    return render_template('calendar.html')

@app.route('/<day>-<month>-<year>')
def day_progress(day, month, year):
    month_number = datetime.strptime(month, '%B').month # Gets the month number based on the name of the month
    if month_number < 10:
        month_number = '0' + str(month_number) # Adds a 0 to the beginning of the month number to easily compare it to the values in the Exercises table

    full_date = str(month_number) + '-' + str(day) + '-' + str(year) # Gets the full date in a clean format to be used as a filter for the "Workout" table

    # Gets the account id of the user currently logged in
    account_id = Accounts.get_id(load_user(db.session.query(Accounts.accounts_id).first())) 

    # Gets all the workout ids as a list format BASED ON the account_id and the date that the user clicked on the calendar
    workout_ids = [workout.workout_id for workout in Workout.query.filter(and_(Workout.accounts_id == account_id, 
                                                                               Workout.workout_date == full_date)).all()]
    
    # Contains all the exercises based on the workout ids in the workout_ids list
    exercises = Exercises.query.filter(Exercises.workout_id.in_(workout_ids)).all()

    # Gets a list of all the exercise ids inside "exercises"
    exercise_ids = [exercise.exercise_id for exercise in exercises]

    # Gets all the sets that are associated with the exercise ids 
    sets = Sets.query.filter(Sets.exercise_id.in_(exercise_ids)).all()

    # Displays the date, each individual exercise name, and all the sets for the exercises. 
    # Uses "exercise_id" to make sure that the sets correspond to the correct exercise.
    html_content = """
    {% extends 'base.html' %}

    {% block title %}Daily Log{% endblock %}

    {% block style %}
        .center {
            text-align: center;
        }

        #date {
            font-weight: bold;
        
            color: white;
            text-shadow:
                2px 2px 0 #000,
                -2px 2px 0 #000,
                -2px -2px 0 #000,
                2px -2px 0 #000;
        }

        #exercisesLogPage {
            min-height: 100vh;

            background-image: url('{{ url_for('static', filename='images/calendar.png') }}'); 
            background-repeat: no-repeat;
            background-size: 100% 100%;
            background-attachment: scroll;
        }

        #exercisesContainer {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        #exerciseName {
            background-color: lightgray;
            width: 70vh;

            text-transform: uppercase;
            font-size: 30px;

            margin-top: 0px;
            margin-bottom: 0px;
        }

        #set {
            background-color: #dee0ea;
            width: 70vh;

            margin-top: 0px;
            margin-bottom: 0px;

            font-size: 20px;
            text-indent: 15px;
        }

        #rep, #weight {
            background-color: lightblue;
            width: 70vh;

            margin-top: 0px;
            margin-bottom: 0px;

            text-indent: 30px;
        }

    {% endblock %}

    {% block content %}
        <div id="exercisesLogPage">
            <h1 class='center' id='date'>{{ year }} {{ month }} {{ day }}</h1>

            <div id="exercisesContainer">
                {% for exercise in exercises %}
                    <p class='center' id='exerciseName'>#{{ loop.index }}: {{ exercise.exercise_name }}</p>
            
                    {% for set in sets %}

                        {% if set.exercise_id == exercise.exercise_id %}
                            <p id='set'>Set #{{ set.set_number }}</p>
                            <p id='rep'>Number of Reps: {{set.number_of_reps}}</p>
                            <p id='weight'>Weight: {{set.weight_in_lbs}} lbs</p>

                            <br>
                        {% endif %}

                    {% endfor %}
                {% endfor %}
            </div>
        </div>

    {% endblock %}
    """

    return render_template_string(html_content, day=day, month=month, year=year, exercises=exercises, sets=sets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)