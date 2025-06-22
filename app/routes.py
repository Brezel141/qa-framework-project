#routes.py
from flask import request, jsonify, render_template, redirect, url_for, flash, session, current_app as app
from .models import db, Bug, User

# ---------------------------------------------------------------------------
# API Routes (for automated tests and programmatic interactions)
# IL TUO CODICE ESISTENTE VA BENISSIMO QUI
# ---------------------------------------------------------------------------

@app.route('/api/bugs', methods=['POST'])
def create_bug():
    """API endpoint to create a new bug."""
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Missing title'}), 400
    
    new_bug = Bug(title=data['title'], description=data.get('description'), priority=data.get('priority', 'Medium'))
    db.session.add(new_bug)
    db.session.commit()
    
    return jsonify({'message': 'Bug created successfully', 'id': new_bug.id}), 201

@app.route('/api/bugs/<int:id>', methods=['GET'])
def get_bug(id):
    """API endpoint to get a bug by its ID."""
    bug = Bug.query.get_or_404(id)
    return jsonify({
        'id': bug.id,
        'title': bug.title,
        'description': bug.description,
        'priority': bug.priority,
        'status': bug.status
    })

# NOTA: Ho modificato leggermente questa rotta per essere più RESTful
@app.route('/api/bugs/<int:id>', methods=['PUT'])
def update_bug(id):
    """API endpoint to update a bug by its ID."""
    bug = Bug.query.get_or_404(id)
    data = request.get_json()
    
    bug.title = data.get('title', bug.title)
    bug.description = data.get('description', bug.description)
    bug.priority = data.get('priority', bug.priority)
    bug.status = data.get('status', bug.status)
    
    db.session.commit()
    return jsonify({'message': f'Bug {id} updated successfully'})

@app.route('/api/bugs/<int:id>', methods=['DELETE'])
def delete_bug(id):
    """API endpoint to delete a bug by its ID."""
    bug = Bug.query.get_or_404(id)
    db.session.delete(bug)
    db.session.commit()
    
    return jsonify({'message': f'Bug {id} deleted successfully'})

# Le rotte API per gli utenti sono utili per i test, le lasciamo
@app.route('/api/register', methods=['POST'])
def api_register_user():
    """API endpoint to register a new user."""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    user = User(username=data['username'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully', 'id': user.id}), 201

@app.route('/api/login', methods=['POST'])
def api_login_user():
    """API endpoint to log in a user."""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

# ---------------------------------------------------------------------------
# UI Routes (for human users using the browser)
# QUESTA È LA PARTE NUOVA
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    """Redirect to dashboard if logged in, otherwise to login page."""
    # Se l'utente è loggato, mostragli la dashboard, altrimenti la pagina di login
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and logic."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another one.', 'danger')
            return redirect(url_for('register'))
            
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    # Se il metodo è GET, mostra semplicemente la pagina
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and logic."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Log out the current user and clear the session."""
    session.clear() # Pulisce tutti i dati della sessione
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Show the dashboard with the list of bugs. Only accessible if logged in."""
    # Proteggi questa pagina: se l'utente non è loggato, mandalo al login
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    bugs = Bug.query.all() # Prendi tutti i bug dal DB
    return render_template('dashboard.html', bugs=bugs)

# Aggiungiamo anche una rotta per creare un bug dalla UI
@app.route('/add_bug', methods=['POST'])
def add_bug_from_ui():
    """Add a new bug from the dashboard UI. Only accessible if logged in."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form['title']
    description = request.form.get('description', '')
    priority = request.form.get('priority', 'Medium')

    new_bug = Bug(title=title, description=description, priority=priority, user_id=session['user_id'])
    db.session.add(new_bug)
    db.session.commit()

    flash('New bug has been created!', 'success')
    return redirect(url_for('dashboard'))