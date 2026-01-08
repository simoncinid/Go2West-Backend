from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import tempfile
from dotenv import load_dotenv
import pymysql
import base64
import io
from openai import OpenAI
import json
import re

# Registra PyMySQL come driver MySQL.
pymysql.install_as_MySQLdb()

# Carica le variabili d'ambiente
load_dotenv()

app = Flask(__name__)

# Configurazione CORS per permettere le richieste dal frontend
CORS(app)

# Variabile globale per il file del certificato SSL
ssl_cert_file = None

def create_ssl_cert_file():
    """Crea un file temporaneo con il certificato SSL dalla variabile d'ambiente"""
    global ssl_cert_file
    
    # Ottieni il certificato dalla variabile d'ambiente
    ssl_cert_content = os.environ.get('DB_CERTIFICATE')
    
    if not ssl_cert_content:
        print("Variabile d'ambiente DB_CERTIFICATE non trovata")
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

# Inizializza OpenAI client con gestione errori
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai_client = None
CHATBOT_ENABLED = False

try:
    if OPENAI_API_KEY:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        CHATBOT_ENABLED = True
        print("✅ OpenAI client inizializzato correttamente")
    else:
        print("⚠️ OPENAI_API_KEY non trovata. Funzionalità chatbot disabilitate.")
        print("   Per abilitare il chatbot, configura la variabile d'ambiente OPENAI_API_KEY su Render.")
except Exception as e:
    print(f"❌ Errore nell'inizializzazione OpenAI client: {e}")
    print("   Il server continuerà a funzionare senza le funzionalità del chatbot.")
    openai_client = None
    CHATBOT_ENABLED = False

# ID del vector store e assistant
VECTOR_STORE_ID = "vs_68f350c542d88191a4026139f8bae406"
ASSISTANT_ID = "asst_cxykjx2GVPkdYqmHXhRrD6D5"

# Modello per i tour
class Tour(db.Model):
    __tablename__ = 'tours'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(200), unique=True, nullable=False)
    heroImage = db.Column(db.LargeBinary)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    carouselImage1 = db.Column(db.LargeBinary)
    carouselImage2 = db.Column(db.LargeBinary)
    carouselImage3 = db.Column(db.LargeBinary)
    program = db.Column(db.JSON)
    image1 = db.Column(db.LargeBinary)
    image2 = db.Column(db.LargeBinary)
    image3 = db.Column(db.LargeBinary)
    image4 = db.Column(db.LargeBinary)
    image5 = db.Column(db.LargeBinary)
    prices = db.Column(db.JSON)
    included = db.Column(db.JSON)
    included_text = db.Column(db.Text)  # Testo unico per included quando included_mode = 'unique'
    included_mode = db.Column(db.Enum('unique', 'list'), default='list')  # 'unique' per testo unico, 'list' per lista
    notIncluded = db.Column(db.JSON)
    notIncluded_text = db.Column(db.Text)  # Testo unico per notIncluded quando notIncluded_mode = 'unique'
    notIncluded_mode = db.Column(db.Enum('unique', 'list'), default='list')  # 'unique' per testo unico, 'list' per lista
    duration = db.Column(db.String(100))  # Cambiato da Integer a String per permettere testo libero
    type = db.Column(db.Enum('city breaks', 'fly and drive', 'ride in harley', 'tour guidato', 'luxury travel', 'camper adventure', 'extra', 'tour guidati (di gruppo)', 'fly & drive (individuali)', 'under canvas usa', 'ranch usa e canada', 'camper adventures', 'scoperta in treno'), nullable=False)
    destination = db.Column(db.Enum('USA', 'Canada', 'Messico', 'America Centrale', 'Sud America', 'Caraibi', 'Polinesia Francese'), nullable=False)
    destinations = db.Column(db.JSON)  # Array JSON di destinazioni multiple
    countries = db.Column(db.JSON)  # Array JSON di paesi
    geographic_area = db.Column(db.String(100))  # Es: "Sud America", "Nord America", "Centro America", "Oceania"
    notes = db.Column(db.Text)
    dates = db.Column(db.JSON)
    dates_text = db.Column(db.Text)  # Testo unico per dates quando dates_mode = 'unique'
    dates_mode = db.Column(db.Enum('unique', 'structured'), default='structured')  # 'unique' per testo unico, 'structured' per JSON strutturato
    minPrice = db.Column(db.Numeric(10, 2))
    pasti = db.Column(db.Text)
    itinerario = db.Column(db.Text)
    itinerario_mode = db.Column(db.Enum('unique', 'days'), default='days')  # 'unique' per testo unico, 'days' per giorni
    mapImage = db.Column(db.LargeBinary)  # Immagine della cartina con l'itinerario
    pdfUrl = db.Column(db.LargeBinary)  # PDF del tour
    is_promotion = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'heroImage': bool(self.heroImage),
            'title': self.title,
            'description': self.description,
            'carouselImage1': bool(self.carouselImage1),
            'carouselImage2': bool(self.carouselImage2),
            'carouselImage3': bool(self.carouselImage3),
            'program': self.program,
            'image1': bool(self.image1),
            'image2': bool(self.image2),
            'image3': bool(self.image3),
            'image4': bool(self.image4),
            'image5': bool(self.image5),
            'prices': self.prices,
            'included': self.included,
            'includedText': self.included_text,
            'includedMode': self.included_mode,
            'notIncluded': self.notIncluded,
            'notIncludedText': self.notIncluded_text,
            'notIncludedMode': self.notIncluded_mode,
            'duration': self.duration,
            'type': self.type,
            'destination': self.destination,
            'destinations': self.destinations if self.destinations else [],
            'countries': self.countries if self.countries else [],
            'notes': self.notes,
            'dates': self.dates,
            'datesText': self.dates_text,
            'datesMode': self.dates_mode,
            'minPrice': float(self.minPrice) if self.minPrice else None,
            'pasti': self.pasti,
            'itinerario': self.itinerario,
            'itinerarioMode': self.itinerario_mode,
            'geographicArea': self.geographic_area,
            'mapImage': bool(self.mapImage),
            'pdfUrl': bool(self.pdfUrl),  # Restituisce True se esiste, False altrimenti
            'isPromotion': self.is_promotion,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Modello per i file dei tour nel vector store
class TourFile(db.Model):
    __tablename__ = 'tour_files'
    
    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tours.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    vector_store_file_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazione con Tour
    tour = db.relationship('Tour', backref=db.backref('tour_file', uselist=False, cascade='all, delete-orphan'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'tour_id': self.tour_id,
            'filename': self.filename,
            'vector_store_file_id': self.vector_store_file_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Funzioni per la gestione del vector store e file .txt

def generate_tour_txt_content(tour):
    """Genera il contenuto del file .txt per un tour"""
    content = f"""TOUR: {tour.title}
CODICE: {tour.code}
DESTINAZIONE: {tour.destination}
TIPO DI VIAGGIO: {tour.type}
DURATA: {tour.duration} giorni
PREZZO MINIMO: €{tour.minPrice if tour.minPrice else 'Da definire'}

DESCRIZIONE:
{tour.description or 'Nessuna descrizione disponibile'}

"""

    # Programma
    if tour.program:
        content += "PROGRAMMA DI VIAGGIO:\n"
        if isinstance(tour.program, list):
            for i, day in enumerate(tour.program, 1):
                if isinstance(day, dict):
                    content += f"Giorno {i}: {day.get('title', '')}\n"
                    content += f"{day.get('description', '')}\n\n"
                else:
                    content += f"Giorno {i}: {day}\n\n"
        else:
            content += f"{tour.program}\n\n"

    # Itinerario
    if tour.itinerario:
        content += f"ITINERARIO:\n{tour.itinerario}\n\n"

    # Prezzi
    if tour.prices:
        content += "PREZZI:\n"
        if isinstance(tour.prices, list):
            for price in tour.prices:
                if isinstance(price, dict):
                    content += f"- {price.get('category', '')}: €{price.get('price', '')}\n"
                else:
                    content += f"- {price}\n"
        else:
            content += f"{tour.prices}\n"
        content += "\n"

    # Incluso
    if tour.included:
        content += "INCLUSO NEL PREZZO:\n"
        if isinstance(tour.included, list):
            for item in tour.included:
                content += f"- {item}\n"
        else:
            content += f"{tour.included}\n"
        content += "\n"

    # Non incluso
    if tour.notIncluded:
        content += "NON INCLUSO NEL PREZZO:\n"
        if isinstance(tour.notIncluded, list):
            for item in tour.notIncluded:
                content += f"- {item}\n"
        else:
            content += f"{tour.notIncluded}\n"
        content += "\n"

    # Pasti
    if tour.pasti:
        content += f"PASTI:\n{tour.pasti}\n\n"

    # Date disponibili
    if tour.dates:
        content += "DATE DISPONIBILI:\n"
        if isinstance(tour.dates, list):
            for date in tour.dates:
                content += f"- {date}\n"
        else:
            content += f"{tour.dates}\n"
        content += "\n"

    # Note
    if tour.notes:
        content += f"NOTE AGGIUNTIVE:\n{tour.notes}\n\n"

    # Stato promozione
    if tour.is_promotion:
        content += "QUESTO TOUR È ATTUALMENTE IN PROMOZIONE!\n\n"

    content += f"Creato il: {tour.created_at.strftime('%d/%m/%Y') if tour.created_at else 'N/A'}\n"
    content += f"Ultimo aggiornamento: {tour.updated_at.strftime('%d/%m/%Y') if tour.updated_at else 'N/A'}\n"

    return content

def create_tour_file_in_vector_store(tour):
    """Crea un file .txt nel vector store per un tour"""
    if not CHATBOT_ENABLED or not openai_client:
        return {
            'success': False,
            'error': 'Chatbot non abilitato - OPENAI_API_KEY mancante'
        }
    
    try:
        # PRIMA: Rimuovi il file vecchio se esiste (senza eliminare il record dal database)
        existing_tour_file = TourFile.query.filter_by(tour_id=tour.id).first()
        if existing_tour_file and existing_tour_file.vector_store_file_id:
            try:
                # Rimuovi il file dal vector store
                openai_client.beta.vector_stores.files.delete(
                    vector_store_id=VECTOR_STORE_ID,
                    file_id=existing_tour_file.vector_store_file_id
                )
                
                # Elimina anche il file da OpenAI
                openai_client.files.delete(existing_tour_file.vector_store_file_id)
                
                print(f"✅ Rimosso file vecchio dal vector store per tour {tour.id}")
                
            except Exception as e:
                print(f"⚠️ Errore nella rimozione del file vecchio per tour {tour.id}: {e}")
                # Continua comunque con la creazione del nuovo file
        
        # Genera il contenuto del file
        content = generate_tour_txt_content(tour)
        
        # Nome del file
        filename = f"tour_{tour.id}_{tour.code}.txt"
        
        # Crea un file temporaneo
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Carica il nuovo file nel vector store
            with open(temp_file_path, 'rb') as file_to_upload:
                vector_file = openai_client.files.create(
                    file=file_to_upload,
                    purpose='assistants'
                )
            
            # Aggiungi il nuovo file al vector store
            openai_client.beta.vector_stores.files.create(
                vector_store_id=VECTOR_STORE_ID,
                file_id=vector_file.id
            )
            
            # Salva nel database
            if existing_tour_file:
                # Aggiorna il record esistente con il nuovo file ID
                existing_tour_file.filename = filename
                existing_tour_file.vector_store_file_id = vector_file.id
                existing_tour_file.updated_at = datetime.utcnow()
            else:
                # Crea un nuovo record
                tour_file = TourFile(
                    tour_id=tour.id,
                    filename=filename,
                    vector_store_file_id=vector_file.id
                )
                db.session.add(tour_file)
            
            db.session.commit()
            
            return {
                'success': True,
                'filename': filename,
                'file_id': vector_file.id
            }
            
        finally:
            # Rimuovi il file temporaneo
            os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"Errore nella creazione del file nel vector store: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def delete_tour_file_from_vector_store(tour_id):
    """Elimina un file dal vector store"""
    if not CHATBOT_ENABLED or not openai_client:
        return {
            'success': False,
            'error': 'Chatbot non abilitato - OPENAI_API_KEY mancante'
        }
    
    try:
        # Trova il record nel database
        tour_file = TourFile.query.filter_by(tour_id=tour_id).first()
        
        if not tour_file or not tour_file.vector_store_file_id:
            return {'success': True, 'message': 'Nessun file da eliminare'}
        
        try:
            # Rimuovi il file dal vector store
            openai_client.beta.vector_stores.files.delete(
                vector_store_id=VECTOR_STORE_ID,
                file_id=tour_file.vector_store_file_id
            )
            
            # Elimina anche il file da OpenAI
            openai_client.files.delete(tour_file.vector_store_file_id)
            
        except Exception as e:
            print(f"Errore nell'eliminazione del file da OpenAI: {e}")
            # Continua comunque con l'eliminazione dal database
        
        # Elimina il record dal database
        db.session.delete(tour_file)
        db.session.commit()
        
        return {'success': True, 'message': 'File eliminato con successo'}
        
    except Exception as e:
        print(f"Errore nell'eliminazione del file dal vector store: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# Creazione delle tabelle
with app.app_context():
    db.create_all()

# Route per ottenere tutti i tour
@app.route('/api/tours', methods=['GET'])
def get_tours():
    try:
        # Controlla se è richiesto il filtro per le promozioni
        promotion_filter = request.args.get('promotion')
        
        if promotion_filter and promotion_filter.lower() == 'true':
            # Restituisci solo i tour in promozione
            tours = Tour.query.filter_by(is_promotion=True).all()
        else:
            # Restituisci tutti i tour
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
        required_fields = ['title', 'type', 'destination']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} è richiesto'}), 400
        
        # Genera il code automaticamente se non fornito
        code = data.get('code')
        if not code:
            code = data['title'].lower().replace(' ', '-').replace('à', 'a').replace('è', 'e').replace('é', 'e').replace('ì', 'i').replace('ò', 'o').replace('ù', 'u')
        
        # Controllo se il code esiste già
        existing_tour = Tour.query.filter_by(code=code).first()
        if existing_tour:
            return jsonify({'error': 'Code già esistente'}), 400
        
        # Gestione della modalità itinerario
        itinerario_mode = data.get('itinerarioMode', 'days')
        print(f"DEBUG CREATE: itinerarioMode ricevuto: '{itinerario_mode}', tipo: {type(itinerario_mode)}")
        program = None
        itinerario = None
        
        if itinerario_mode == 'unique':
            # Se è modalità unique, salva solo il testo e azzera program
            itinerario = data.get('itinerario')
            program = None
            print(f"DEBUG CREATE: Salvato in modalità UNIQUE, itinerario: {itinerario[:50] if itinerario else 'None'}...")
        else:
            # Se è modalità days, salva solo program e azzera itinerario
            program = data.get('program')
            itinerario = None
            print(f"DEBUG CREATE: Salvato in modalità DAYS, program ha {len(program.get('days', [])) if program else 0} giorni")
        
        # Gestione delle modalità per dates, included, notIncluded
        dates_mode = data.get('datesMode', 'structured')
        dates_data = None
        dates_text_data = None
        if dates_mode == 'unique':
            dates_text_data = data.get('datesText')
            dates_data = None
        else:
            dates_data = data.get('dates')
            dates_text_data = None
        
        included_mode = data.get('includedMode', 'list')
        included_data = None
        included_text_data = None
        if included_mode == 'unique':
            included_text_data = data.get('includedText')
            included_data = None
        else:
            included_data = data.get('included')
            included_text_data = None
        
        notIncluded_mode = data.get('notIncludedMode', 'list')
        notIncluded_data = None
        notIncluded_text_data = None
        if notIncluded_mode == 'unique':
            notIncluded_text_data = data.get('notIncludedText')
            notIncluded_data = None
        else:
            notIncluded_data = data.get('notIncluded')
            notIncluded_text_data = None
        
        # Creazione del tour con la nuova struttura (senza immagini, caricate separatamente)
        tour = Tour(
            code=code,
            title=data['title'],
            description=data.get('description'),
            program=program,
            prices=data.get('prices'),
            included=included_data,
            included_text=included_text_data,
            included_mode=included_mode,
            notIncluded=notIncluded_data,
            notIncluded_text=notIncluded_text_data,
            notIncluded_mode=notIncluded_mode,
            duration=data.get('duration'),
            type=data['type'],
            destination=data['destination'],
            destinations=data.get('destinations'),
            countries=data.get('countries'),
            geographic_area=data.get('geographicArea'),
            notes=data.get('notes'),
            dates=dates_data,
            dates_text=dates_text_data,
            dates_mode=dates_mode,
            minPrice=data.get('minPrice'),
            pasti=data.get('pasti'),
            itinerario=itinerario,
            itinerario_mode=itinerario_mode,
            is_promotion=data.get('isPromotion', False)
        )
        
        db.session.add(tour)
        db.session.commit()
        
        # Crea il file nel vector store
        vector_result = create_tour_file_in_vector_store(tour)
        if not vector_result['success']:
            print(f"Errore nella creazione del file vector store per tour {tour.id}: {vector_result.get('error')}")
        
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
        required_fields = ['title', 'type', 'destination']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} è richiesto'}), 400
        
        # Genera il code automaticamente se non fornito
        code = data.get('code')
        if not code:
            code = data['title'].lower().replace(' ', '-').replace('à', 'a').replace('è', 'e').replace('é', 'e').replace('ì', 'i').replace('ò', 'o').replace('ù', 'u')
        
        # Controllo se il code esiste già (escludendo il tour corrente)
        existing_tour = Tour.query.filter_by(code=code).first()
        if existing_tour and existing_tour.id != tour_id:
            return jsonify({'error': 'Code già esistente'}), 400
        
        # Gestione della modalità itinerario
        itinerario_mode = data.get('itinerarioMode', 'days')
        print(f"DEBUG UPDATE: itinerarioMode ricevuto: '{itinerario_mode}', tipo: {type(itinerario_mode)}")
        print(f"DEBUG UPDATE: chiavi nel data: {list(data.keys())}")
        
        if itinerario_mode == 'unique':
            # Se è modalità unique, salva solo il testo e azzera program
            tour.itinerario = data.get('itinerario')
            tour.program = None
            print(f"DEBUG UPDATE: Salvato in modalità UNIQUE, itinerario: {tour.itinerario[:50] if tour.itinerario else 'None'}...")
        else:
            # Se è modalità days, salva solo program e azzera itinerario
            tour.program = data.get('program')
            tour.itinerario = None
            print(f"DEBUG UPDATE: Salvato in modalità DAYS, program ha {len(tour.program.get('days', [])) if tour.program else 0} giorni")
        
        # Gestione delle modalità per dates, included, notIncluded
        dates_mode = data.get('datesMode', 'structured')
        if dates_mode == 'unique':
            tour.dates_text = data.get('datesText')
            tour.dates = None
        else:
            tour.dates = data.get('dates')
            tour.dates_text = None
        tour.dates_mode = dates_mode
        
        included_mode = data.get('includedMode', 'list')
        if included_mode == 'unique':
            tour.included_text = data.get('includedText')
            tour.included = None
        else:
            tour.included = data.get('included')
            tour.included_text = None
        tour.included_mode = included_mode
        
        notIncluded_mode = data.get('notIncludedMode', 'list')
        if notIncluded_mode == 'unique':
            tour.notIncluded_text = data.get('notIncludedText')
            tour.notIncluded = None
        else:
            tour.notIncluded = data.get('notIncluded')
            tour.notIncluded_text = None
        tour.notIncluded_mode = notIncluded_mode
        
        # Aggiornamento dei campi (senza immagini, caricate separatamente)
        tour.code = code
        tour.title = data['title']
        tour.description = data.get('description')
        tour.prices = data.get('prices')
        tour.duration = data.get('duration')
        tour.type = data['type']
        tour.destination = data['destination']
        tour.destinations = data.get('destinations')
        tour.countries = data.get('countries')
        tour.geographic_area = data.get('geographicArea')
        tour.notes = data.get('notes')
        tour.minPrice = data.get('minPrice')
        tour.pasti = data.get('pasti')
        tour.itinerario_mode = itinerario_mode
        tour.is_promotion = data.get('isPromotion', False)
        tour.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Aggiorna il file nel vector store
        vector_result = create_tour_file_in_vector_store(tour)
        if not vector_result['success']:
            print(f"Errore nell'aggiornamento del file vector store per tour {tour.id}: {vector_result.get('error')}")
        
        return jsonify(tour.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route per eliminare un tour
@app.route('/api/tours/<int:tour_id>', methods=['DELETE'])
def delete_tour(tour_id):
    try:
        tour = Tour.query.get_or_404(tour_id)
        
        # Elimina il file dal vector store prima di eliminare il tour
        vector_result = delete_tour_file_from_vector_store(tour_id)
        if not vector_result['success']:
            print(f"Errore nell'eliminazione del file vector store per tour {tour_id}: {vector_result.get('error')}")
        
        db.session.delete(tour)
        db.session.commit()
        return jsonify({'message': 'Tour eliminato con successo'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route per ottenere tour per destinazione
@app.route('/api/tours/destination/<destination>', methods=['GET'])
def get_tours_by_destination(destination):
    try:
        tours = Tour.query.filter_by(destination=destination).all()
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

# Route per ottenere tour per destinazione e tipo
@app.route('/api/tours/destination/<destination>/type/<tour_type>', methods=['GET'])
def get_tours_by_destination_and_type(destination, tour_type):
    try:
        tours = Tour.query.filter_by(destination=destination, type=tour_type).all()
        return jsonify([tour.to_dict() for tour in tours])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route per ottenere tour per code
@app.route('/api/tours/code/<code>', methods=['GET'])
def get_tour_by_code(code):
    try:
        tour = Tour.query.filter_by(code=code).first()
        if tour:
            return jsonify(tour.to_dict())
        else:
            return jsonify({'error': 'Tour non trovato'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route per ottenere tour per area geografica
@app.route('/api/tours/area/<geographic_area>', methods=['GET'])
def get_tours_by_area(geographic_area):
    try:
        tours = Tour.query.filter_by(geographic_area=geographic_area).all()
        return jsonify([tour.to_dict() for tour in tours])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route per aggiornare solo lo stato promozione di un tour
@app.route('/api/tours/<int:tour_id>/promotion', methods=['PUT'])
def update_tour_promotion(tour_id):
    try:
        tour = Tour.query.get_or_404(tour_id)
        data = request.get_json()
        
        # Aggiorna solo il campo is_promotion
        if 'isPromotion' in data:
            tour.is_promotion = bool(data['isPromotion'])
            tour.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Stato promozione aggiornato con successo',
                'tour': tour.to_dict()
            })
        else:
            return jsonify({'error': 'Campo isPromotion richiesto'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route per servire le immagini
@app.route('/api/tours/<int:tour_id>/image/<path:image_type>', methods=['GET'])
def get_tour_image(tour_id, image_type):
    try:
        tour = Tour.query.get_or_404(tour_id)
        
        # Mappa i tipi di immagine ai campi del modello
        image_fields = {
            'hero': tour.heroImage,
            'carousel1': tour.carouselImage1,
            'carousel2': tour.carouselImage2,
            'carousel3': tour.carouselImage3,
            'image1': tour.image1,
            'image2': tour.image2,
            'image3': tour.image3,
            'image4': tour.image4,
            'image5': tour.image5,
            'map': tour.mapImage
        }
        
        if image_type not in image_fields:
            return jsonify({'error': 'Tipo di immagine non valido'}), 400
        
        image_data = image_fields[image_type]
        
        if not image_data:
            return jsonify({'error': 'Immagine non trovata'}), 404
        
        # Determina il tipo MIME basato sui primi byte
        if image_data.startswith(b'\xff\xd8\xff'):
            mimetype = 'image/jpeg'
        elif image_data.startswith(b'\x89PNG'):
            mimetype = 'image/png'
        elif image_data.startswith(b'GIF'):
            mimetype = 'image/gif'
        elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:
            mimetype = 'image/webp'
        else:
            mimetype = 'image/jpeg'  # Default
        
        return Response(image_data, mimetype=mimetype)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route per caricare un'immagine
@app.route('/api/tours/<int:tour_id>/image/<path:image_type>', methods=['POST'])
def upload_tour_image(tour_id, image_type):
    try:
        tour = Tour.query.get_or_404(tour_id)
        
        # Verifica che ci sia un file nell'upload
        if 'image' not in request.files:
            return jsonify({'error': 'Nessun file immagine fornito'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Nessun file selezionato'}), 400
        
        # Leggi i dati del file
        image_data = file.read()
        
        # Le immagini vengono salvate così come sono (senza ridimensionamento)
        # TODO: Aggiungere ridimensionamento quando Pillow sarà disponibile
        
        # Mappa i tipi di immagine ai campi del modello
        image_fields = {
            'hero': 'heroImage',
            'carousel1': 'carouselImage1',
            'carousel2': 'carouselImage2',
            'carousel3': 'carouselImage3',
            'image1': 'image1',
            'image2': 'image2',
            'image3': 'image3',
            'image4': 'image4',
            'image5': 'image5',
            'map': 'mapImage'
        }
        
        # Debug: stampa il tipo di immagine ricevuto
        print(f"DEBUG: Tipo immagine ricevuto: '{image_type}', Tipi validi: {list(image_fields.keys())}")
        print(f"DEBUG: image_type in image_fields: {image_type in image_fields}")
        
        if image_type not in image_fields:
            print(f"ERRORE: Tipo immagine '{image_type}' non trovato nei tipi validi")
            return jsonify({'error': f'Tipo di immagine non valido: {image_type}. Tipi validi: {list(image_fields.keys())}'}), 400
        
        # Aggiorna il campo dell'immagine
        setattr(tour, image_fields[image_type], image_data)
        tour.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"SUCCESS: Immagine {image_type} caricata con successo per tour {tour_id}")
        return jsonify({'message': f'Immagine {image_type} caricata con successo'})
    except Exception as e:
        db.session.rollback()
        print(f"ERRORE nel caricamento immagine: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Route per eliminare un'immagine
@app.route('/api/tours/<int:tour_id>/image/<path:image_type>', methods=['DELETE'])
def delete_tour_image(tour_id, image_type):
    try:
        tour = Tour.query.get_or_404(tour_id)
        
        # Mappa i tipi di immagine ai campi del modello
        image_fields = {
            'hero': 'heroImage',
            'carousel1': 'carouselImage1',
            'carousel2': 'carouselImage2',
            'carousel3': 'carouselImage3',
            'image1': 'image1',
            'image2': 'image2',
            'image3': 'image3',
            'image4': 'image4',
            'image5': 'image5',
            'map': 'mapImage'
        }
        
        if image_type not in image_fields:
            return jsonify({'error': f'Tipo di immagine non valido: {image_type}'}), 400
        
        # Verifica che l'immagine esista
        image_field = image_fields[image_type]
        if not getattr(tour, image_field):
            return jsonify({'error': 'Immagine non trovata'}), 404
        
        # Elimina l'immagine impostandola a None
        setattr(tour, image_field, None)
        tour.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"SUCCESS: Immagine {image_type} eliminata con successo per tour {tour_id}")
        return jsonify({'message': f'Immagine {image_type} eliminata con successo'})
    except Exception as e:
        db.session.rollback()
        print(f"ERRORE nell'eliminazione immagine: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Route per servire il PDF
@app.route('/api/tours/<int:tour_id>/pdf', methods=['GET'])
def get_tour_pdf(tour_id):
    try:
        tour = Tour.query.get_or_404(tour_id)
        
        if not tour.pdfUrl:
            return jsonify({'error': 'PDF non trovato'}), 404
        
        # Determina il tipo MIME per PDF
        mimetype = 'application/pdf'
        
        return Response(tour.pdfUrl, mimetype=mimetype, headers={
            'Content-Disposition': f'inline; filename=tour_{tour_id}.pdf'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route per caricare un PDF
@app.route('/api/tours/<int:tour_id>/pdf', methods=['POST'])
def upload_tour_pdf(tour_id):
    try:
        tour = Tour.query.get_or_404(tour_id)
        
        # Verifica che ci sia un file nell'upload
        if 'pdf' not in request.files:
            return jsonify({'error': 'Nessun file PDF fornito'}), 400
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'error': 'Nessun file selezionato'}), 400
        
        # Verifica che sia un PDF
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Il file deve essere un PDF'}), 400
        
        # Leggi i dati del file
        pdf_data = file.read()
        
        # Verifica che i primi byte siano quelli di un PDF
        if not pdf_data.startswith(b'%PDF'):
            return jsonify({'error': 'Il file non è un PDF valido'}), 400
        
        # Aggiorna il campo del PDF
        tour.pdfUrl = pdf_data
        tour.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"SUCCESS: PDF caricato con successo per tour {tour_id}")
        return jsonify({
            'message': 'PDF caricato con successo',
            'pdfUrl': f'/api/tours/{tour_id}/pdf'
        })
    except Exception as e:
        db.session.rollback()
        print(f"ERRORE nel caricamento PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Route per eliminare un PDF
@app.route('/api/tours/<int:tour_id>/pdf', methods=['DELETE'])
def delete_tour_pdf(tour_id):
    try:
        tour = Tour.query.get_or_404(tour_id)
        
        # Verifica che il PDF esista
        if not tour.pdfUrl:
            return jsonify({'error': 'PDF non trovato'}), 404
        
        # Elimina il PDF impostandolo a None
        tour.pdfUrl = None
        tour.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"SUCCESS: PDF eliminato con successo per tour {tour_id}")
        return jsonify({'message': 'PDF eliminato con successo'})
    except Exception as e:
        db.session.rollback()
        print(f"ERRORE nell'eliminazione PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Route per il chatbot AI
@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    if not CHATBOT_ENABLED or not openai_client:
        return jsonify({
            'error': 'Chatbot non disponibile. Contatta direttamente l\'agenzia per informazioni sui tour.',
            'status': 'error'
        }), 503
    
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Messaggio richiesto'}), 400
        
        # Utilizza l'assistant esistente
        assistant_id = ASSISTANT_ID
        
        # Crea un thread per la conversazione
        thread = openai_client.beta.threads.create()
        
        # Aggiungi il messaggio dell'utente
        openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        
        # Esegui l'assistant
        run = openai_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        # Attendi il completamento
        import time
        while run.status in ['queued', 'in_progress']:
            time.sleep(1)
            run = openai_client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        
        if run.status == 'completed':
            # Ottieni la risposta
            messages = openai_client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            assistant_message = None
            for message in messages.data:
                if message.role == 'assistant':
                    assistant_message = message.content[0].text.value
                    break
            
            return jsonify({
                'response': assistant_message,
                'status': 'success'
            })
        else:
            return jsonify({
                'error': f'Errore nell\'elaborazione: {run.status}',
                'status': 'error'
            }), 500
            
    except Exception as e:
        print(f"Errore nel chatbot: {e}")
        return jsonify({'error': str(e)}), 500

# Route per sincronizzare tutti i tour esistenti con il vector store
@app.route('/api/sync-vector-store', methods=['POST'])
def sync_vector_store():
    if not CHATBOT_ENABLED or not openai_client:
        return jsonify({
            'error': 'Chatbot non abilitato - OPENAI_API_KEY mancante',
            'status': 'error'
        }), 503
    
    try:
        tours = Tour.query.all()
        success_count = 0
        error_count = 0
        
        for tour in tours:
            result = create_tour_file_in_vector_store(tour)
            if result['success']:
                success_count += 1
            else:
                error_count += 1
                print(f"Errore sincronizzazione tour {tour.id}: {result.get('error')}")
        
        return jsonify({
            'message': 'Sincronizzazione completata',
            'success_count': success_count,
            'error_count': error_count,
            'total_tours': len(tours)
        })
        
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
        'version': '2.0.0',
        'endpoints': {
            'tours': '/api/tours',
            'tours_promotions': '/api/tours?promotion=true',
            'tour_by_id': '/api/tours/<id>',
            'tours_by_destination': '/api/tours/destination/<destination>',
            'tours_by_type': '/api/tours/type/<type>',
            'tours_by_destination_and_type': '/api/tours/destination/<destination>/type/<type>',
            'tour_by_code': '/api/tours/code/<code>',
            'update_promotion': '/api/tours/<id>/promotion',
            'get_image': '/api/tours/<id>/image/<image_type>',
            'upload_image': '/api/tours/<id>/image/<image_type>',
            'delete_image': '/api/tours/<id>/image/<image_type>',
            'get_pdf': '/api/tours/<id>/pdf',
            'upload_pdf': '/api/tours/<id>/pdf',
            'delete_pdf': '/api/tours/<id>/pdf',
            'health': '/health'
        },
        'destinations': ['USA', 'Canada', 'Messico', 'America Centrale', 'Sud America', 'Caraibi', 'Polinesia Francese'],
        'types': ['city breaks', 'fly and drive', 'ride in harley', 'tour guidato', 'luxury travel', 'camper adventure', 'extra', 'tour guidati (di gruppo)', 'fly & drive (individuali)', 'under canvas usa', 'ranch usa e canada', 'camper adventures', 'scoperta in treno'],
        'image_types': ['hero', 'carousel1', 'carousel2', 'carousel3', 'image1', 'image2', 'image3', 'image4', 'image5', 'map']
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
