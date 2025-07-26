#!/usr/bin/env python3
"""
Script para inicializar la base de datos y crear las tablas necesarias
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.database import engine, Base
from app.models.response_model import Response

def init_database():
    """Inicializa la base de datos creando todas las tablas"""
    print("🔄 Inicializando base de datos...")
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    print("✅ Base de datos inicializada correctamente")
    print("📊 Tablas creadas:")
    
    # Listar las tablas creadas
    inspector = engine.dialect.inspector(engine)
    tables = inspector.get_table_names()
    for table in tables:
        print(f"   - {table}")

if __name__ == "__main__":
    init_database() 