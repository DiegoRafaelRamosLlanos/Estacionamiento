from app import create_app, db
from app.models.models import User, Vehicle, MonthlyClient

app = create_app()

# Crear todas las tablas de la base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)