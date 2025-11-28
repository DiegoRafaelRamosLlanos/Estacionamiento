# Guía de Instalación - Sistema de Estacionamiento

## ⚠️ IMPORTANTE: Requisitos del Sistema Operativo

**Antes de instalar el sistema, debes tener instalado en tu equipo:**

### 1. Python 3.8 o superior

**Python NO viene en requirements.txt** - Debe instalarse manualmente en el sistema operativo.

#### Windows:
1. Descargar Python desde: https://www.python.org/downloads/
2. **Importante:** Marcar la casilla "Add Python to PATH" durante la instalación
3. Verificar instalación:
   ```bash
   python --version
   # Debe mostrar: Python 3.x.x
   ```


### 2. pip (Gestor de Paquetes de Python)

**Viene incluido con Python 3.4+**, pero verificá:

```bash
pip --version
# Windows: pip --version

```

Si no está instalado:
```bash
python -m ensurepip --upgrade
```

### 3. Git (Opcional - para clonar repositorio)

#### Windows:
- Descargar desde: https://git-scm.com/download/win
- Instalar con opciones por defecto

#### Linux:
```bash
sudo apt install git
```

#### macOS:
```bash
brew install git
# O viene preinstalado con Xcode
```

---

## 📦 Instalación del Sistema

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd Estacionamiento
```

### 2. Crear Entorno Virtual (Recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto (opcional):

```
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=sqlite:///app.db
```

### 5. Inicializar la Base de Datos

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. Crear Usuario Inicial (Opcional)

```bash
python manage_users.py
```

### 7. Ejecutar el Servidor

```bash
python run.py
```

El servidor estará disponible en: http://localhost:8080

---

## 📋 Resumen de Dependencias

### Requisitos del Sistema Operativo (Instalar PRIMERO)
Estos **NO están en requirements.txt** y deben instalarse manualmente:

1. ✅ **Python 3.8+** - Lenguaje de programación
2. ✅ **pip** - Gestor de paquetes (viene con Python)
3. ✅ **Git** - Control de versiones (opcional)

### Dependencias de Python (En requirements.txt)
Estas se instalan con `pip install -r requirements.txt`:

- **Flask 3.0.0** - Framework web
- **SQLAlchemy 2.0.23** - ORM para base de datos
- **python-barcode** - Generación de códigos de barras Code128
- **Pillow** - Procesamiento de imágenes
- **python-escpos** - Impresora térmica
- **Flask-Login** - Autenticación de usuarios
- Y más... (ver requirements.txt completo)

---

## Configuración de Hardware

### Impresora Térmica

Configurar la IP en `config.py`:

```python
PRINTER_IP = '192.168.18.43'
PRINTER_PORT = 9100
```

### Lector de Códigos de Barras Honeywell

No requiere configuración adicional. Conectar vía USB y funciona como teclado.

## Solución de Problemas

### Error al instalar python-barcode

```bash
pip install --upgrade pip
pip install python-barcode[images]
```

### Error con Pillow

En Windows, puede requerir Visual C++:
- Descargar desde: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Base de datos no se crea

```bash
python
>>> from app import app, db
>>> app.app_context().push()
>>> db.create_all()
>>> exit()
```

## Estructura del Proyecto

```
Estacionamiento/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes.py
│   ├── services/
│   │   ├── barcode_service.py
│   │   ├── vehicle_service.py
│   │   └── ...
│   ├── templates/
│   └── ...
├── config.py
├── run.py
├── requirements.txt
└── README_INSTALL.md
```

## Usuarios por Defecto


**¡IMPORTANTE!** Cambiar las contraseñas después de la instalación.
