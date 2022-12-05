from flask import render_template,redirect,request,session,flash
from flask_app import app
import re	
from flask_app.models.user import User
from flask_app.models.sighting import Sighting
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def login_page():
    return render_template('login.html')


@app.route('/register', methods=['POST'])
def register():
    dbdata = {
        'email': request.form['email']
    }
    user_in_db = User.get_by_email(dbdata)
    if user_in_db:
        flash('*email is taken*')
        return redirect ('/')
    # validate user
    if User.validate_user(request.form):
        print('registration passes')
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        print(pw_hash)
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': pw_hash 
        }
        # Call the save @classmethod on user// saves info in db
        user_id = User.save(data)
        # store user id into session
        user_in_db = User.get_by_email(data)
        session['user_id'] = user_id
        session['first_name'] = user_in_db.first_name
        print(user_id)
        return redirect('/sightings')
    else:
        print('validation failed')
        flash('validation failed')
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    data = {
        'email': request.form['email']
    }
    user_in_db = User.get_by_email(data)
    if not user_in_db:
        flash('*email/password invalid*')
        return redirect ('/')
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Invalid Email/Password")
        return redirect('/')
    # session['first_name'] = user.get_by_email(data)
    session['user_id'] = user_in_db.id
    session['first_name'] = user_in_db.first_name
    print(user_in_db.id)
    print(user_in_db)
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    return redirect('/sightings')


# @app.route('/')
# def logged_in():
#     if 'user_id' not in session:
#         flash('log in to view page')
#         return redirect('/')
    
#     return redirect('/sightings')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

    ###############user's sightings page######################
@app.route('/sightings')
def user_sightings():
    if 'user_id' not in session:
        flash('log in to view page')
        return redirect('/')
    list_sightings = Sighting.get_sightings_and_users()
    return render_template('index.html', sightings = list_sightings)

    ############################################Add sighting ##############
@app.route('/sighting/new')
def new_sighting():
    if 'user_id' not in session:
        flash('log in to view page')
        return redirect('/')
    return render_template('add_sighting.html')

@app.route('/add/sighting', methods = ['POST'])
def create_sighting():
    if Sighting.sighting_is_valid(request.form):
        print('sighting is valid')
        user_data = {
            'id': session['user_id']
        }
        current_user = User.get_user_by_id(user_data)
        sighting_data = {
                'location' : request.form['location'],
                'date_of_sighting' : request.form['date_of_sighting'],
                'number_of_birds': request.form['number_of_birds'],
                'description': request.form['description'],
                'reported_by': current_user.first_name,
                'reporter_id' : session['user_id']
            }
        Sighting.save_sighting(sighting_data)
        return redirect('/sightings')
    else:
        print('validation failed')
        flash('validation failed')
        return redirect('/sighting/new')

###################show sighting info######################
@app.route('/sighting/<int:id>')
def show_sighting(id):
    if 'first_name' not in session:
        return redirect ('/')
    data = {
        'id': id
    }
    sighting = Sighting.get_sighting_by_id(data)
    return render_template('view_sighting.html', sighting = sighting)

###############edit info###################
@app.route('/edit/sighting/<int:id>')
def edit_sighting(id):
    if 'first_name' not in session:
        return redirect ('/')
    data = {
        'id':id
    }
    sighting = Sighting.get_sighting_by_id(data)
    return render_template('edit_sighting.html', sighting = sighting)

@app.route('/update/sighting/<int:id>', methods = ['POST'])
def update_sighting(id):
    data = {
        'id':id
    }
    sighting = Sighting.get_sighting_by_id(data)
    if sighting.reported_by != session['first_name']:
        return redirect ('/')
    if Sighting.sighting_is_valid(request.form):
        print('sighting is valid')
        user_data = {
            'id': session['user_id']
        }
        current_user = User.get_user_by_id(user_data)
        sighting_data = {
                'id' : id,
                'location' : request.form['location'],
                'date_of_sighting' : request.form['date_of_sighting'],
                'number_of_birds': request.form['number_of_birds'],
                'description': request.form['description'],
                'reported_by': current_user.first_name,
                'reporter_id' : session['user_id']
            }
    Sighting.update_one(sighting_data)
    return redirect(f'/sighting/{id}')
    ###############delete###########
@app.route('/sightings/delete/<int:id>')
def delete_sighting(id):
    data = {
        'id': id
    }
    Sighting.delete_one(data)
    return redirect('/sightings')