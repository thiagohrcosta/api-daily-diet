import bcrypt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required