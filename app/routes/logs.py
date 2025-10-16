"""
ScrappingAndPdfTools
Developed : MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
Siteweb : www.myoneart.com
"""

from flask import Blueprint, render_template, request, jsonify
from app.models import get_logs, clear_old_logs

bp = Blueprint('logs', __name__, url_prefix='/logs')

@bp.route('/')
def index():
    """Affiche la page des logs"""
    type_filter = request.args.get('type')
    status_filter = request.args.get('status')
    limit = int(request.args.get('limit', 100))
    
    logs = get_logs(limit=limit, type_filter=type_filter, status_filter=status_filter)
    
    return render_template('logs.html', logs=logs, type_filter=type_filter, status_filter=status_filter)

@bp.route('/api/logs')
def get_logs_api():
    """API pour récupérer les logs en JSON"""
    type_filter = request.args.get('type')
    status_filter = request.args.get('status')
    limit = int(request.args.get('limit', 100))
    
    logs = get_logs(limit=limit, type_filter=type_filter, status_filter=status_filter)
    
    return jsonify({'success': True, 'logs': logs, 'count': len(logs)})

@bp.route('/clear-old', methods=['POST'])
def clear_old():
    """Supprime les anciens logs"""
    data = request.get_json() or {}
    days = int(data.get('days', 30))
    deleted = clear_old_logs(days=days)
    
    return jsonify({'success': True, 'deleted': deleted})
