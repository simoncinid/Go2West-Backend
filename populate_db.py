# Script per popolare il database con dati di esempio

import requests
import json

# URL del backend (cambia con l'URL di Render quando sarà deployato)
BASE_URL = "http://localhost:5000"

# Dati di esempio per i tour
sample_tours = [
    {
        "title": "New York City Break",
        "country": "usa",
        "type": "tour",
        "slug": "new-york-city-break",
        "price": 890,
        "duration": 4,
        "description": "Weekend nella Grande Mela: grattacieli iconici, Broadway e Central Park in un viaggio urbano indimenticabile.",
        "mainImage": "/images/city.jpg",
        "images": ["/images/usa.jpg", "/images/usa-parks.jpg"],
        "highlights": [
            "Visita alla Statua della Libertà",
            "Crociera nel porto di New York",
            "Broadway e Times Square",
            "Central Park e Metropolitan Museum"
        ],
        "itinerary": [
            "Arrivo a New York e check-in hotel",
            "Visita alla Statua della Libertà e Ellis Island",
            "Broadway e Times Square by night",
            "Central Park e musei, partenza"
        ],
        "included": [
            "Volo A/R da Milano",
            "Hotel 3 stelle in centro",
            "Colazione inclusa",
            "Trasferimenti aeroporto-hotel",
            "Guida locale per 2 giorni"
        ],
        "notIncluded": [
            "Pranzi e cene",
            "Ingressi ai musei",
            "Mance",
            "Assicurazione viaggio"
        ],
        "notes": "Tour ideale per un weekend lungo. Consigliato portare scarpe comode per le passeggiate."
    },
    {
        "title": "Grand Canyon Adventure",
        "country": "usa",
        "type": "fly-drive",
        "slug": "grand-canyon-adventure",
        "price": 1490,
        "duration": 8,
        "description": "Esplora il maestoso Grand Canyon con tour guidati e avventure uniche nel cuore dell'America.",
        "mainImage": "/images/usa-parks.jpg",
        "images": ["/images/north-america.jpg", "/images/drive.jpg"],
        "highlights": [
            "Vista panoramica del Grand Canyon",
            "Helicopter tour del canyon",
            "Passeggiata sul bordo del canyon",
            "Visita a Las Vegas"
        ],
        "itinerary": [
            "Arrivo a Phoenix e ritiro auto",
            "Guida verso il Grand Canyon",
            "Visita al South Rim",
            "Helicopter tour opzionale",
            "Passeggiata sul bordo del canyon",
            "Visita a Las Vegas",
            "Ritorno a Phoenix",
            "Partenza per l'Italia"
        ],
        "included": [
            "Volo A/R da Milano",
            "Auto a noleggio per 7 giorni",
            "Hotel 3 stelle",
            "Colazione inclusa",
            "Mappa e GPS"
        ],
        "notIncluded": [
            "Carburante",
            "Parcheggi",
            "Helicopter tour",
            "Pranzi e cene",
            "Assicurazione auto"
        ],
        "notes": "Tour self-drive. Patente internazionale richiesta. Consigliato prenotare l'helicopter tour in anticipo."
    },
    {
        "title": "Route 66 in Harley",
        "country": "usa",
        "type": "adventure",
        "slug": "route-66-harley",
        "price": 2890,
        "duration": 12,
        "description": "Percorri la strada più famosa d'America su una Harley Davidson, da Chicago a Los Angeles.",
        "mainImage": "/images/ride_in_harley.jpg",
        "images": ["/images/usa.jpg", "/images/drive.jpg"],
        "highlights": [
            "Harley Davidson a noleggio",
            "Route 66 completa",
            "Visita a Chicago",
            "Arrivo a Santa Monica Pier"
        ],
        "itinerary": [
            "Arrivo a Chicago e ritiro Harley",
            "Inizio Route 66",
            "Missouri e Oklahoma",
            "Texas e New Mexico",
            "Arizona e California",
            "Arrivo a Los Angeles",
            "Santa Monica Pier",
            "Ritorno Harley e partenza"
        ],
        "included": [
            "Volo A/R da Milano",
            "Harley Davidson a noleggio",
            "Hotel lungo il percorso",
            "Colazione inclusa",
            "Assicurazione moto",
            "Supporto stradale"
        ],
        "notIncluded": [
            "Carburante",
            "Pranzi e cene",
            "Mance",
            "Assicurazione viaggio"
        ],
        "notes": "Esperienza per motociclisti esperti. Patente moto richiesta. Tour guidato con supporto."
    },
    {
        "title": "Tesori Maya del Messico",
        "country": "messico",
        "type": "tour",
        "slug": "tesori-maya-messico",
        "price": 1650,
        "duration": 10,
        "description": "Dalle piramidi Maya alle spiagge di Tulum, scopri la cultura millenaria messicana.",
        "mainImage": "/images/mexico.jpg",
        "images": ["/images/mexico2.jpg", "/images/tour.jpg"],
        "highlights": [
            "Piramidi di Teotihuacan",
            "Chichen Itza",
            "Spiagge di Tulum",
            "Città del Messico"
        ],
        "itinerary": [
            "Arrivo a Città del Messico",
            "Visita Teotihuacan",
            "Città del Messico centro",
            "Volo per Cancun",
            "Chichen Itza",
            "Tulum e spiagge",
            "Ritorno a Città del Messico",
            "Partenza per l'Italia"
        ],
        "included": [
            "Volo A/R da Milano",
            "Hotel 4 stelle",
            "Mezza pensione",
            "Guida locale",
            "Trasferimenti",
            "Ingressi ai siti"
        ],
        "notIncluded": [
            "Bevande",
            "Mance",
            "Escursioni opzionali",
            "Assicurazione viaggio"
        ],
        "notes": "Tour culturale con guida esperta. Consigliato portare crema solare e cappello."
    },
    {
        "title": "Safari Kenya",
        "country": "kenya",
        "type": "safari",
        "slug": "safari-kenya",
        "price": 2200,
        "duration": 8,
        "description": "Safari fotografico nei parchi nazionali del Kenya per avvistare i Big Five.",
        "mainImage": "/images/kenya-safari.jpg",
        "images": ["/images/kenya.jpg", "/images/kenya-wildlife.jpg"],
        "highlights": [
            "Masai Mara",
            "Amboseli National Park",
            "Lake Nakuru",
            "Avvistamento Big Five"
        ],
        "itinerary": [
            "Arrivo a Nairobi",
            "Masai Mara",
            "Safari Masai Mara",
            "Amboseli",
            "Lake Nakuru",
            "Safari finale",
            "Ritorno a Nairobi",
            "Partenza per l'Italia"
        ],
        "included": [
            "Volo A/R da Milano",
            "Lodge safari",
            "Pensione completa",
            "Safari con jeep 4x4",
            "Guida esperta",
            "Permessi parchi"
        ],
        "notIncluded": [
            "Bevande alcoliche",
            "Mance",
            "Assicurazione viaggio",
            "Vaccinazioni"
        ],
        "notes": "Safari fotografico. Consigliato portare binocolo e macchina fotografica. Vaccinazioni richieste."
    }
]

def create_tour(tour_data):
    """Crea un nuovo tour nel database"""
    try:
        response = requests.post(f"{BASE_URL}/api/tours", json=tour_data)
        if response.status_code == 201:
            print(f"✅ Tour creato: {tour_data['title']}")
            return response.json()
        else:
            print(f"❌ Errore nella creazione del tour {tour_data['title']}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Errore di connessione per {tour_data['title']}: {e}")
        return None

def main():
    """Funzione principale per popolare il database"""
    print("🚀 Inizio popolamento database con tour di esempio...")
    
    created_count = 0
    for tour in sample_tours:
        result = create_tour(tour)
        if result:
            created_count += 1
    
    print(f"\n✅ Popolamento completato! Creati {created_count} tour su {len(sample_tours)}")
    
    # Mostra tutti i tour creati
    try:
        response = requests.get(f"{BASE_URL}/api/tours")
        if response.status_code == 200:
            tours = response.json()
            print(f"\n📋 Tour presenti nel database:")
            for tour in tours:
                print(f"  - {tour['title']} ({tour['country']}) - €{tour['price']}")
        else:
            print("❌ Errore nel recupero dei tour")
    except Exception as e:
        print(f"❌ Errore di connessione: {e}")

if __name__ == "__main__":
    main()
