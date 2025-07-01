from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app import app, db
from models import StudySession
from text_analysis import analyze_text
from datetime import datetime

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get last 5 studies by the current user, sorted by updated_at DESC
    recent_studies = StudySession.query.filter_by(user_id=current_user.id)\
                                     .order_by(StudySession.updated_at.desc())\
                                     .limit(5).all()
    
    return render_template('dashboard.html', studies=recent_studies)

@app.route('/studies')
@login_required
def studies():
    # List all studies by the current user
    all_studies = StudySession.query.filter_by(user_id=current_user.id)\
                                   .order_by(StudySession.updated_at.desc())\
                                   .all()
    
    return render_template('studies.html', studies=all_studies)

@app.route('/new_study', methods=['GET', 'POST'])
@login_required
def new_study():
    if request.method == 'POST':
        try:
            # Get form data
            passage = request.form.get('passage')
            date_str = request.form.get('date')
            passage_text = request.form.get('passage_text')
            
            # Get all 10 questions
            questions = []
            for i in range(1, 11):
                question = request.form.get(f'question_{i}', '')
                questions.append(question)
            
            # Validate required fields
            if not passage or not date_str or not passage_text:
                flash('Please fill in all required fields.', 'error')
                return render_template('new_study.html')
            
            # Parse date
            study_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Analyze text
            word_freq, bigram_freq = analyze_text(passage_text)
            
            # Create new study session
            study = StudySession()
            study.user_id = current_user.id
            study.passage = passage
            study.date = study_date
            study.passage_text = passage_text
            
            # Set questions
            study.set_questions(questions)
            
            # Set analysis results
            study.set_word_freq(word_freq)
            study.set_bigram_freq(bigram_freq)
            
            # Save to database
            db.session.add(study)
            db.session.commit()
            
            flash('Study session created successfully!', 'success')
            return redirect(url_for('study_detail', id=study.id))
            
        except Exception as e:
            flash(f'Error creating study: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('new_study.html')

@app.route('/study/<int:id>')
@login_required
def study_detail(id):
    # Get study session by ID, ensuring it belongs to current user
    study = StudySession.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('study_detail.html', study=study)

@app.route('/study/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_study(id):
    # Get study session by ID, ensuring it belongs to current user
    study = StudySession.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            # Update form data
            study.passage = request.form.get('passage')
            date_str = request.form.get('date')
            study.passage_text = request.form.get('passage_text')
            
            # Get all 10 questions
            questions = []
            for i in range(1, 11):
                question = request.form.get(f'question_{i}', '')
                questions.append(question)
            
            # Validate required fields
            if not study.passage or not date_str or not study.passage_text:
                flash('Please fill in all required fields.', 'error')
                return render_template('study_detail.html', study=study, edit_mode=True)
            
            # Parse date
            study.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Re-analyze text
            word_freq, bigram_freq = analyze_text(study.passage_text)
            
            # Update questions
            study.set_questions(questions)
            
            # Update analysis results
            study.set_word_freq(word_freq)
            study.set_bigram_freq(bigram_freq)
            
            # Update timestamp
            study.updated_at = datetime.utcnow()
            
            # Save to database
            db.session.commit()
            
            flash('Study session updated successfully!', 'success')
            return redirect(url_for('study_detail', id=study.id))
            
        except Exception as e:
            flash(f'Error updating study: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('study_detail.html', study=study, edit_mode=True)

@app.route('/analyze_text', methods=['POST'])
@login_required
def analyze_text_api():
    """API endpoint for text analysis preview"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Analyze the text
        word_freq, bigram_freq = analyze_text(text)
        
        return jsonify({
            'word_freq': word_freq,
            'bigram_freq': bigram_freq
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/autosave_draft', methods=['POST'])
@login_required
def autosave_draft():
    """API endpoint for autosaving study drafts"""
    try:
        data = request.get_json()
        draft_key = f"draft_{current_user.id}_{data.get('study_id', 'new')}"
        
        # Store draft data in session or a simple cache
        # For simplicity, we'll use session storage
        session[draft_key] = {
            'passage': data.get('passage', ''),
            'date': data.get('date', ''),
            'passage_text': data.get('passage_text', ''),
            'questions': {f'question_{i}': data.get(f'question_{i}', '') for i in range(1, 11)},
            'last_saved': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Draft saved automatically',
            'timestamp': session[draft_key]['last_saved']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/load_draft', methods=['POST'])
@login_required
def load_draft():
    """API endpoint for loading saved drafts"""
    try:
        data = request.get_json()
        draft_key = f"draft_{current_user.id}_{data.get('study_id', 'new')}"
        
        if draft_key in session:
            return jsonify({
                'success': True,
                'draft': session[draft_key]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No draft found'
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
