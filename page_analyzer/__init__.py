import os

from dotenv import load_dotenv

from page_analyzer.app import app
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
__all__ = ('app', 'DATABASE_URL',)
