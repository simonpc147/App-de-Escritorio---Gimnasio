from models.database import Database

def main():
    # Probar conexión a la base de datos
    db = Database()
    
    if db.connect():
        print("🎉 Todo funcionando correctamente")
        db.disconnect()
    else:
        print("💥 Fallo en la conexión")

if __name__ == "__main__":
    main()
