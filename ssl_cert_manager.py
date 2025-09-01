# Script per gestire il certificato SSL per MySQL

import os
import tempfile
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

def create_ssl_cert_file():
    """Crea un file temporaneo con il certificato SSL"""
    ssl_cert_content = os.getenv('DB_CERTIFICATE')
    
    if not ssl_cert_content:
        print("⚠️  Nessun certificato SSL trovato in DB_CERTIFICATE")
        return None
    
    try:
        # Crea un file temporaneo con il certificato
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.crt', delete=False)
        temp_file.write(ssl_cert_content)
        temp_file.close()
        
        print(f"✅ Certificato SSL salvato in: {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        print(f"❌ Errore nella creazione del file certificato: {e}")
        return None

def cleanup_ssl_cert_file(file_path):
    """Rimuove il file temporaneo del certificato"""
    if file_path and os.path.exists(file_path):
        try:
            os.unlink(file_path)
            print(f"🧹 File certificato rimosso: {file_path}")
        except Exception as e:
            print(f"⚠️  Errore nella rimozione del file: {e}")

def test_ssl_certificate():
    """Testa il certificato SSL"""
    print("🔐 Test certificato SSL")
    print("=" * 50)
    
    ssl_cert_content = os.getenv('DB_CERTIFICATE')
    
    if not ssl_cert_content:
        print("❌ Nessun certificato SSL configurato")
        print("   Aggiungi DB_CERTIFICATE nelle variabili d'ambiente")
        return False
    
    print("✅ Certificato SSL trovato nelle variabili d'ambiente")
    print(f"📏 Lunghezza certificato: {len(ssl_cert_content)} caratteri")
    
    # Verifica che il certificato inizi con "-----BEGIN CERTIFICATE-----"
    if "-----BEGIN CERTIFICATE-----" in ssl_cert_content:
        print("✅ Formato certificato valido")
    else:
        print("⚠️  Formato certificato potrebbe non essere corretto")
    
    # Crea file temporaneo per test
    cert_file = create_ssl_cert_file()
    
    if cert_file:
        print("✅ File certificato creato con successo")
        cleanup_ssl_cert_file(cert_file)
        return True
    else:
        print("❌ Errore nella creazione del file certificato")
        return False

if __name__ == "__main__":
    print("🔐 Gestione Certificato SSL MySQL")
    print("=" * 50)
    
    test_ssl_certificate()
    
    print("\n" + "=" * 50)
    print("📋 Istruzioni per il certificato SSL:")
    print("1. Copia il contenuto del file .crt del certificato")
    print("2. Aggiungi DB_CERTIFICATE nelle variabili d'ambiente su Render")
    print("3. Incolla tutto il contenuto del certificato (inclusi BEGIN e END)")
    print("4. NON mettere il percorso del file, ma il contenuto stesso!")
    print("5. Il backend userà automaticamente il certificato personalizzato")
