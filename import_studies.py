#!/usr/bin/env python3
"""
Import Bible study data from text file into the database
"""

import re
from datetime import datetime
from app import app, db
from models import User, StudySession
from text_analysis import analyze_text

def parse_studies_file(filename):
    """Parse the studies file and extract individual studies"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by "Study #" to get individual studies
    studies = re.split(r'Study #\d+:', content)[1:]  # Skip first empty part
    
    parsed_studies = []
    
    for study_text in studies:
        study_data = {}
        lines = study_text.strip().split('\n')
        
        # Extract study number from the beginning
        first_line = lines[0] if lines else ""
        
        # Extract passage
        passage_match = re.search(r'Passage:\s*(.+)', study_text)
        if passage_match:
            study_data['passage'] = passage_match.group(1).strip()
        
        # Extract date
        date_match = re.search(r'Date:\s*(.+)', study_text)
        if date_match:
            date_str = date_match.group(1).strip()
            try:
                study_data['date'] = datetime.strptime(date_str, '%B %d, %Y').date()
            except ValueError:
                # Try different format
                try:
                    study_data['date'] = datetime.strptime(date_str, '%B %d, %Y').date()
                except ValueError:
                    print(f"Could not parse date: {date_str}")
                    continue
        
        # Extract email
        email_match = re.search(r'Email:\s*(.+)', study_text)
        if email_match:
            study_data['email'] = email_match.group(1).strip()
        
        # Extract reflections (everything after "Reflections:")
        reflections_match = re.search(r'Reflections:\s*\n(.*?)(?=Study #|\Z)', study_text, re.DOTALL)
        if reflections_match:
            reflections_text = reflections_match.group(1).strip()
            # Split reflections into lines and filter out empty ones
            reflection_lines = [line.strip() for line in reflections_text.split('\n') 
                              if line.strip() and line.strip() != '(empty)']
            
            # Map to our 10 questions format
            questions = []
            for i in range(10):
                if i < len(reflection_lines):
                    questions.append(reflection_lines[i])
                else:
                    questions.append("")
            
            study_data['questions'] = questions
            study_data['passage_text'] = ' '.join(reflection_lines)  # Use reflections as passage text for now
        
        if 'passage' in study_data and 'date' in study_data and 'email' in study_data:
            parsed_studies.append(study_data)
    
    return parsed_studies

def import_studies():
    """Import all studies into the database"""
    
    # Parse the studies file
    studies = parse_studies_file('attached_assets/Pasted-Study-21-1-Peter-1-13-16-Passage-1-Peter-1-13-16-Date-June-21-2025-Email-bdgillihan-gmail-com--1750952777392_1750952777394.txt')
    
    print(f"Found {len(studies)} studies to import")
    
    with app.app_context():
        # Find or create user
        user_email = "bdgillihan@gmail.com"
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            user = User(username="Brian Gillihan", email=user_email)
            db.session.add(user)
            db.session.commit()
            print(f"Created user: {user.username}")
        else:
            print(f"Found existing user: {user.username}")
        
        # Import each study
        imported_count = 0
        for study_data in studies:
            try:
                # Check if study already exists
                existing = StudySession.query.filter_by(
                    user_id=user.id,
                    passage=study_data['passage'],
                    date=study_data['date']
                ).first()
                
                if existing:
                    print(f"Study already exists: {study_data['passage']} on {study_data['date']}")
                    continue
                
                # Analyze the passage text
                word_freq, bigram_freq = analyze_text(study_data['passage_text'])
                
                # Create new study session
                study = StudySession()
                study.user_id = user.id
                study.passage = study_data['passage']
                study.date = study_data['date']
                study.passage_text = study_data['passage_text']
                
                # Set questions
                study.set_questions(study_data['questions'])
                
                # Set analysis results
                study.set_word_freq(word_freq)
                study.set_bigram_freq(bigram_freq)
                
                db.session.add(study)
                db.session.commit()
                
                print(f"Imported: {study.passage} ({study.date})")
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing study {study_data.get('passage', 'Unknown')}: {str(e)}")
                db.session.rollback()
        
        print(f"Successfully imported {imported_count} studies")

if __name__ == "__main__":
    import_studies()