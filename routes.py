import os
import requests as http_client

from flask import render_template, request, redirect, url_for, flash, jsonify
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
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        word_freq, bigram_freq = analyze_text(text)
        return jsonify({'word_freq': word_freq, 'bigram_freq': bigram_freq})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fetch_passage', methods=['POST'])
@login_required
def fetch_passage():
    data = request.get_json()
    passage = (data.get('passage') or '').strip()
    if not passage:
        return jsonify({'error': 'No passage provided'}), 400

    esv_key = os.environ.get('ESV_API_KEY')
    if esv_key:
        try:
            resp = http_client.get(
                'https://api.esv.org/v3/passage/text/',
                params={
                    'q': passage,
                    'include-headings': False,
                    'include-footnotes': False,
                    'include-verse-numbers': True,
                    'include-short-copyright': False,
                    'include-passage-references': False,
                },
                headers={'Authorization': f'Token {esv_key}'},
                timeout=10,
            )
            if resp.ok:
                passages = resp.json().get('passages', [])
                if passages:
                    return jsonify({'text': passages[0].strip(), 'translation': 'ESV'})
        except Exception:
            pass

    # Fallback: bible-api.com (WEB translation, no key required)
    try:
        resp = http_client.get(
            f'https://bible-api.com/{passage}',
            params={'translation': 'web'},
            timeout=10,
        )
        if resp.ok:
            result = resp.json()
            if 'text' in result:
                return jsonify({'text': result['text'].strip(), 'translation': 'WEB'})
    except Exception:
        pass

    return jsonify({'error': 'Could not fetch passage — check the reference and try again.'}), 500

