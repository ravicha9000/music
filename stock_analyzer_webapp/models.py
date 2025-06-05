from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy. This would typically be done in app.py
# db = SQLAlchemy()
# For this conceptual step, we'll define it here.
# In a real app, ensure db instance is created and configured in app.py
# and then imported here: from . import db or from yourapp import db

db = SQLAlchemy() # Placeholder initialization

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, index=True) # To group messages by conversation
    user_query = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Optional: if you have users

    def __repr__(self):
        return f'<ChatMessage id={self.id} session_id={self.session_id} user_query="{self.user_query[:50]}...">'

class User(db.Model): # Optional: Example User model if authentication is added
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Add other fields like password_hash, email etc.
    messages = db.relationship('ChatMessage', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

# Conceptual API Routes (to be implemented in app.py or a dedicated routes file)
# These are just comments here for planning purposes.

# POST /api/chat_history
# - Body: { session_id, user_query, ai_response }
# - Saves a new chat message to the database.
# - Returns: { message_id } or success status.

# GET /api/chat_history/<session_id>
# - Params: session_id
# - Returns: List of chat messages for that session.
# - Could add pagination parameters (page, per_page).

# GET /api/chat_sessions
# - Returns: List of unique session_ids (perhaps for an admin view or user history).

# DELETE /api/chat_message/<message_id>
# - Deletes a specific message (e.g., for moderation or user request).

# PATCH /api/chat_message/<message_id>
# - Updates a message (e.g., user feedback on AI response, correction).
