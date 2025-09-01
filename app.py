from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import tempfile
from dotenv import load_dotenv
import pymysql

# Registra PyMySQL come driver MySQL
pymysql.install_as_MySQLdb()

# Carica le variabili d'ambiente
load_dotenv()

app = Flask(__name__)

# Configurazione CORS per permettere le richieste dal frontend
CORS(app)

# Variabile globale per il file del certificato SSL
ssl_cert_file = None

def create_ssl_cert_file():
    """Crea un file temporaneo con il certificato SSL"""
    global ssl_cert_file
    
    # Contenuto del certificato SSL di DigitalOcean (sostituisci con il tuo certificato)
    ssl_cert_content = """-----BEGIN CERTIFICATE-----
MIIDrzCCApegAwIBAgIQCDvgVpBCRrGhdWrJWZHHSjANBgkqhkiG9w0BAQUFADBh
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBD
QTAeFw0wNjExMTAwMDAwMDBaFw0zMTExMTAwMDAwMDBaMGExCzAJBgNVBAYTAlVT
MRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j
b20xIDAeBgNVBAMTF0RpZ2lDZXJ0IEdsb2JhbCBSb290IENBMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4jvhEXLeqKTTo1eqUKKPC3eQyaKl7hLOllsB
CSDMAZOnTjC3U/dDxGkAV53ijSLdhwZAAIEJzs4bg7/fzTtxRuLWZscFs3YnFo97
nh6Vfe63SKMI2tavegw5BmV/Sl0fvBf4q77uKNd0f3p4mVmFaG5cIzJLv07A6Fpt4
3C/dxC//AH2hdmoRBBYMql1GNXRor5H4idq9Joz+EkIYIvUX7Q6hL+hqkpMfT7PT
19sdl6gSzeRntwi5m3OFBqOasv+zbMUZBfHWymeMr/y7vrTC0LUq7dBMtoM1O/4g
dW7jVg/tRvoSSiicNoxBN33shbyTApOB6jtSj1etX+jkMOvJwIDAQABo2MwYTAOBg
NVHQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUA95QNVbRj
TtmVK4mG9p6AtvMxwHwYDVR0jBBgwFoAUA95QNVbRjTtmVK4mG9p6AtvMxwDQYJ
KoZIhvcNAQEFBQADggEBJucV9kwKt1l2ONwWwSlr4gfxCd6FomG7ynrAhacAi2V3
XKL5hq1DdWJ6Jcp3IlV98AVI/R3E6U3U9MSlMQ5XYFwSLCfhJW9D88Y8yV2fbf4E
1b9RqKjm7QZjT33wpm+KzD/j3vqu+3sDPXvNLtgXeOc4IufcU6iF+OJ4U7a2OPnY
CshSNUD0MYE35L5E45U4R4Y7G35QilltCaZerjwF2yRPvEL8v3puL5tYpuM7CpI
3JADv+up1sWwH/RpawNJSdR1NkzDKX5a/abAR/BC+F1j1ehBJUiWQKwhYhZfmlHM
SwlU364j77Y6I9ZbBl8QvwUsL5APwuHMJuAryWGPKqDl6K30jCyJdcThDo7Q==
-----END CERTIFICATE-----"""
    
    if not ssl_cert_content:
        return None
    
    try:
        # Crea un file temporaneo con il certificato
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.crt', delete=False)
        temp_file.write(ssl_cert_content)
        temp_file.close()
        
        ssl_cert_file = temp_file.name
        return ssl_cert_file
        
    except Exception as e:
        print(f"Errore nella creazione del file certificato: {e}")
        return None

# Configurazione del database MySQL
def get_database_url():
    # Configurazione diretta per MySQL
    username = 'doadmin'
    password = 'AVNS_q6pjJ1Aego6vWH4f1Wk'
    host = 'db-mysql-fra1-09501-do-user-24280960-0.l.db.ondigitalocean.com'
    port = '25060'
    database = 'defaultdb'
    
    # Crea il file del certificato SSL se necessario
    ssl_cert_path = create_ssl_cert_file()
    
    if ssl_cert_path:
        return f"mysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4&ssl_ca={ssl_cert_path}"
    else:
        # Fallback senza certificato specifico
        return f"mysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4&ssl_mode=REQUIRED"

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True
}

db = SQLAlchemy(app)

# Modello per i tour
class Tour(db.Model):
    __tablename__ = 'tour'
    
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(200), nullable=False)
    paese = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # tour, fly-drive, safari, cruise, adventure
    slug = db.Column(db.String(200), unique=True, nullable=False)
    prezzo = db.Column(db.Float, nullable=False)
    durata = db.Column(db.Integer)
    descrizione = db.Column(db.Text)
    immagine_principale = db.Column(db.String(500))
    immagini = db.Column(db.Text)  # JSON string per array di immagini
    punti_salienti = db.Column(db.Text)  # JSON string per array di highlights
    itinerario = db.Column(db.Text)  # JSON string per array di tappe
    incluso = db.Column(db.Text)  # JSON string per servizi inclusi
    non_incluso = db.Column(db.Text)  # JSON string per servizi non inclusi
    note = db.Column(db.Text)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_aggiornamento = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.titolo,
            'country': self.paese,
            'type': self.tipo,
            'slug': self.slug,
            'price': self.prezzo,
            'duration': self.durata,
            'description': self.descrizione,
            'mainImage': self.immagine_principale,
            'images': self.immagini.split(',') if self.immagini else [],
            'highlights': self.punti_salienti.split(',') if self.punti_salienti else [],
            'itinerary': self.itinerario.split(',') if self.itinerario else [],
            'included': self.incluso.split(',') if self.incluso else [],
            'notIncluded': self.non_incluso.split(',') if self.non_incluso else [],
            'notes': self.note,
            'created_at': self.data_creazione.isoformat() if self.data_creazione else None,
            'updated_at': self.data_aggiornamento.isoformat() if self.data_aggiornamento else None
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
            titolo=data['title'],
            paese=data['country'],
            tipo=data['type'],
            slug=data['slug'],
            prezzo=float(data['price']),
            durata=data.get('duration'),
            descrizione=data.get('description'),
            immagine_principale=data.get('mainImage'),
            immagini=','.join(data.get('images', [])),
            punti_salienti=','.join(data.get('highlights', [])),
            itinerario=','.join(data.get('itinerary', [])),
            incluso=','.join(data.get('included', [])),
            non_incluso=','.join(data.get('notIncluded', [])),
            note=data.get('notes')
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
        tour.titolo = data['title']
        tour.paese = data['country']
        tour.tipo = data['type']
        tour.slug = data['slug']
        tour.prezzo = float(data['price'])
        tour.durata = data.get('duration')
        tour.descrizione = data.get('description')
        tour.immagine_principale = data.get('mainImage')
        tour.immagini = ','.join(data.get('images', []))
        tour.punti_salienti = ','.join(data.get('highlights', []))
        tour.itinerario = ','.join(data.get('itinerary', []))
        tour.incluso = ','.join(data.get('included', []))
        tour.non_incluso = ','.join(data.get('notIncluded', []))
        tour.note = data.get('notes')
        tour.data_aggiornamento = datetime.utcnow()
        
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
        tours = Tour.query.filter_by(paese=country).all()
        return jsonify([tour.to_dict() for tour in tours])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route per ottenere tour per tipo
@app.route('/api/tours/type/<tour_type>', methods=['GET'])
def get_tours_by_type(tour_type):
    try:
        tours = Tour.query.filter_by(tipo=tour_type).all()
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
