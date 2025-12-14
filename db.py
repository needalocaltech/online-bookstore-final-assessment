from flask import Flask, render_template

from flask_sqlalchemy import SQLAlchemy

# Single shared SQLAlchemy instance for the whole application
db = SQLAlchemy()
