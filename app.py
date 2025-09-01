from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

app = Flask(__name__)

# Configurazione CORS per permettere le richieste dal frontend
CORS(app)

# Configurazione del database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///tours.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modello per i tour
class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # tour, fly-drive, safari, cruise, adventure
    slug = db.Column(db.String(200), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer)
    description = db.Column(db.Text)
    mainImage = db.Column(db.String(500))
    images = db.Column(db.Text)  # JSON string per array di immagini
    highlights = db.Column(db.Text)  # JSON string per array di highlights
    itinerary = db.Column(db.Text)  # JSON string per array di tappe
    included = db.Column(db.Text)  # JSON string per servizi inclusi
    notIncluded = db.Column(db.Text)  # JSON string per servizi non inclusi
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'country': self.country,
            'type': self.type,
            'slug': self.slug,
            'price': self.price,
            'duration': self.duration,
            'description': self.description,
            'mainImage': self.mainImage,
            'images': self.images.split(',') if self.images else [],
            'highlights': self.highlights.split(',') if self.highlights else [],
            'itinerary': self.itinerary.split(',') if self.itinerary else [],
            'included': self.included.split(',') if self.included else [],
            'notIncluded': self.notIncluded.split(',') if self.notIncluded else [],
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Creazione delle tabelle
with app.app_context():
    db.create_all()

# Route per ottenere tutti i tour
@app.route('/api/tours', methods=['GET'])
def get_tours():
    try:
        tours = Tour.query.all()
        return jsonify([tour.to_dict() for tour in tours])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route per ottenere un tour specifico
@app.route('/api/tours/<int:tour_id>', methods=['GET'])
def get_tour(tour_id):
    try:
        tour = Tour.query.get_or_404(tour_id)
        return jsonify(tour.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route per creare un nuovo tour
@app.route('/api/tours', methods=['POST'])
def create_tour():
    try:
        data = request.get_json()
        
        # Validazione dei dati richiesti
        required_fields = ['title', 'country', 'type', 'slug', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} è richiesto'}), 400
        
        # Controllo se lo slug esiste già
        existing_tour = Tour.query.filter_by(slug=data['slug']).first()
        if existing_tour:
            return jsonify({'error': 'Slug già esistente'}), 400
        
        # Conversione degli array in stringhe per il database
        tour = Tour(
            title=data['title'],
            country=data['country'],
            type=data['type'],
            slug=data['slug'],
            price=float(data['price']),
            duration=data.get('duration'),
            description=data.get('description'),
            mainImage=data.get('mainImage'),
            images=','.join(data.get('images', [])),
            highlights=','.join(data.get('highlights', [])),
            itinerary=','.join(data.get('itinerary', [])),
            included=','.join(data.get('included', [])),
            notIncluded=','.join(data.get('notIncluded', [])),
            notes=data.get('notes')
        )
        
        db.session.add(tour)
        db.session.commit()
        
        return jsonify(tour.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route per aggiornare un tour
@app.route('/api/tours/<int:tour_id>', methods=['PUT'])
def update_tour(tour_id):
    try:
        tour = Tour.query.get_or_404(tour_id)
        data = request.get_json()
        
        # Validazione dei dati richiesti
        required_fields = ['title', 'country', 'type', 'slug', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} è richiesto'}), 400
        
        # Controllo se lo slug esiste già (escludendo il tour corrente)
        existing_tour = Tour.query.filter_by(slug=data['slug']).first()
        if existing_tour and existing_tour.id != tour_id:
            return jsonify({'error': 'Slug già esistente'}), 400
        
        # Aggiornamento dei campi
        tour.title = data['title']
        tour.country = data['country']
        tour.type = data['type']
        tour.slug = data['slug']
        tour.price = float(data['price'])
        tour.duration = data.get('duration')
        tour.description = data.get('description')
        tour.mainImage = data.get('mainImage')
        tour.images = ','.join(data.get('images', []))
        tour.highlights = ','.join(data.get('highlights', []))
        tour.itinerary = ','.join(data.get('itinerary', []))
        tour.included = ','.join(data.get('included', []))
        tour.notIncluded = ','.join(data.get('notIncluded', []))
        tour.notes = data.get('notes')
        tour.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(tour.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route per eliminare un tour
@app.route('/api/tours/<int:tour_id>', methods=['DELETE'])
def delete_tour(tour_id):
    try:
        tour = Tour.query.get_or_404(tour_id)
        db.session.delete(tour)
        db.session.commit()
        return jsonify({'message': 'Tour eliminato con successo'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route per ottenere tour per paese
@app.route('/api/tours/country/<country>', methods=['GET'])
def get_tours_by_country(country):
    try:
        tours = Tour.query.filter_by(country=country).all()
        return jsonify([tour.to_dict() for tour in tours])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route per ottenere tour per tipo
@app.route('/api/tours/type/<tour_type>', methods=['GET'])
def get_tours_by_type(tour_type):
    try:
        tours = Tour.query.filter_by(type=tour_type).all()
        return jsonify([tour.to_dict() for tour in tours])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route per ottenere tour per slug
@app.route('/api/tours/slug/<slug>', methods=['GET'])
def get_tour_by_slug(slug):
    try:
        tour = Tour.query.filter_by(slug=slug).first()
        if tour:
            return jsonify(tour.to_dict())
        else:
            return jsonify({'error': 'Tour non trovato'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route di health check per Render
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Server funzionante'})

# Route principale
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Go2West API',
        'version': '1.0.0',
        'endpoints': {
            'tours': '/api/tours',
            'tour_by_id': '/api/tours/<id>',
            'tours_by_country': '/api/tours/country/<country>',
            'tours_by_type': '/api/tours/type/<type>',
            'tour_by_slug': '/api/tours/slug/<slug>',
            'health': '/health'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
