"""
ScrappingAndPdfTools
Developed : MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
Siteweb : www.myoneart.com
"""

from flask import Blueprint, render_template

bp = Blueprint('contact', __name__, url_prefix='/contact')

@bp.route('/')
def index():
    """Affiche la page de contact"""
    return render_template('contact.html')
