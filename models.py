from app import db
from flask_login import UserMixin
from collections import OrderedDict
from datetime import datetime
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Relationship to study sessions
    study_sessions = db.relationship('StudySession', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, username=None, email=None):
        self.username = username
        self.email = email

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    passage = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # 10 reflection questions
    question_1 = db.Column(db.Text)
    question_2 = db.Column(db.Text)
    question_3 = db.Column(db.Text)
    question_4 = db.Column(db.Text)
    question_5 = db.Column(db.Text)
    question_6 = db.Column(db.Text)
    question_7 = db.Column(db.Text)
    question_8 = db.Column(db.Text)
    question_9 = db.Column(db.Text)
    question_10 = db.Column(db.Text)
    
    passage_text = db.Column(db.Text, nullable=False)
    word_freq_json = db.Column(db.Text)  # JSON string
    bigram_freq_json = db.Column(db.Text)  # JSON string
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_questions(self):
        """Return a list of all questions"""
        return [
            self.question_1, self.question_2, self.question_3, self.question_4, self.question_5,
            self.question_6, self.question_7, self.question_8, self.question_9, self.question_10
        ]
    
    def set_questions(self, questions_list):
        """Set questions from a list"""
        question_attrs = ['question_1', 'question_2', 'question_3', 'question_4', 'question_5',
                         'question_6', 'question_7', 'question_8', 'question_9', 'question_10']
        
        for i, question in enumerate(questions_list[:10]):  # Limit to 10 questions
            if i < len(question_attrs):
                setattr(self, question_attrs[i], question)
    
    def get_word_freq(self):
        """Get word frequency as dictionary sorted by frequency"""
        if self.word_freq_json:
            word_freq = json.loads(self.word_freq_json)
            # Return as OrderedDict sorted by frequency (descending)
            return OrderedDict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True))
        return {}
    
    def set_word_freq(self, word_freq_dict):
        """Set word frequency from dictionary"""
        self.word_freq_json = json.dumps(word_freq_dict)
    
    def get_bigram_freq(self):
        """Get bigram frequency as dictionary sorted by frequency"""
        if self.bigram_freq_json:
            bigram_freq = json.loads(self.bigram_freq_json)
            # Return as OrderedDict sorted by frequency (descending)
            from collections import OrderedDict
            return OrderedDict(sorted(bigram_freq.items(), key=lambda x: x[1], reverse=True))
        return {}
    
    def set_bigram_freq(self, bigram_freq_dict):
        """Set bigram frequency from dictionary"""
        self.bigram_freq_json = json.dumps(bigram_freq_dict)
