# Instalación Completa desde Cero - Sistema de Estacionamiento

Esta guía asume que estás instalando en un **equipo completamente nuevo sin Python**.

---

## 🖥️ PASO 1: Instalar Requisitos del Sistema Operativo

### Windows

#### 1.1. Instalar Python

1. Ir a: https://www.python.org/downloads/
2. Descargar **Python 3.11** o superior (recomendado)
3. Ejecutar el instalador
4. ✅ **MUY IMPORTANTE:** Marcar "Add Python to PATH"
5. Click "Install Now"
6. Esperar a que termine
7. Verificar:
   ```cmd
   python --version
   ```
   Debe mostrar: `Python 3.11.x`

#### 1.2. Instalar Git (Opcional)

1. Ir a: https://git-scm.com/download/win
2. Descargar instalador
3. Instalar con opciones por defecto
4. Verificar:
   ```cmd
   git --version
   ```

## 📦 PASO 2: Obtener el Sistema

### Opción A: Con Git (Recomendado)

```bash
git clone <url-del-repositorio>
cd Estacionamiento
```

### Opción B: Sin Git (Descargar ZIP)

1. Descarga el ZIP del repositorio
2. Extrae en una carpeta
3. Abre terminal/cmd en esa carpeta

---

## 🐍 PASO 3: Crear Entorno Virtual

**¿Por qué?** Aísla las dependencias de este proyecto de otros proyectos Python.

### Windows:

```cmd
python -m venv venv
venv\Scripts\activate
```

Verás `(venv)` al inicio de la línea de comandos.

### Linux/Mac:

```bash
python3 -m venv venv
source venv/bin/activate
```

Verás `(venv)` al inicio de la línea.

---

## 📥 PASO 4: Instalar Dependencias de Python

**IMPORTANTE:** El entorno virtual debe estar activado `(venv)`

```bash
pip install -r requirements.txt
```

Esto instalará **automáticamente**:
- Flask
- SQLAlchemy
- python-barcode
- Pillow
- python-escpos
- Y todas las demás dependencias listadas en requirements.txt

**Tiempo estimado:** 2-5 minutos dependiendo de conexión a internet.

---

## ✅ PASO 5: Verificar Instalación

```bash
python verificar_instalacion.py
```

**Salida esperada:**

```
============================================================
VERIFICACIÓN DE DEPENDENCIAS - Sistema de Estacionamiento
============================================================

✓ Flask                    INSTALADO
✓ SQLAlchemy               INSTALADO
✓ python-barcode           INSTALADO
✓ Pillow                   INSTALADO
...

Total: 13/13 dependencias instaladas

✅ Todas las dependencias están instaladas correctamente
```

Si hay errores, volver a ejecutar:
```bash
pip install -r requirements.txt
```

---

## 🗄️ PASO 6: Inicializar Base de Datos

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

Esto crea el archivo `app.db` con las tablas necesarias.

---

## 👤 PASO 7: Crear Usuarios (Opcional)

```bash
python manage_users.py
```

Seguir las instrucciones en pantalla para crear usuarios operadores.

---

## 🚀 PASO 8: Iniciar el Servidor

```bash
python run.py
```

**Salida esperada:**

```
======================================================================
🚀 SERVIDOR DE ESTACIONAMIENTO INICIADO
======================================================================

📍 Acceso LOCAL (desde esta PC):
   http://127.0.0.1:8080
   http://localhost:8080

📱 Acceso desde CELULAR/TABLET (misma red WiFi):
   http://192.168.x.x:8080
======================================================================
```

---

## 🌐 PASO 9: Acceder al Sistema

1. Abrir navegador
2. Ir a: http://localhost:8080
3. Login con usuario y contraseña configurados

**¡El sistema está funcionando!** 🎉

---

## 🔧 Configuración Adicional

### Impresora Térmica

Editar `config.py`:

```python
PRINTER_ENABLED = True
PRINTER_IP = '192.168.18.43'  # Cambiar a la IP de tu impresora
PRINTER_PORT = 9100
```

Probar conexión:
```bash
python test_printer.py
```

### Lector de Códigos de Barras Honeywell

1. Conectar vía USB
2. Funciona automáticamente como teclado
3. No requiere configuración adicional

---

## 📝 Comandos Resumidos

### Instalación Completa - Windows

```cmd
REM 1. Instalar Python desde python.org (marcar "Add to PATH")

REM 2. Clonar repositorio
git clone <url>
cd Estacionamiento

REM 3. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

REM 4. Instalar dependencias
pip install -r requirements.txt

REM 5. Verificar
python verificar_instalacion.py

REM 6. Inicializar BD
python -c "from app import app, db; app.app_context().push(); db.create_all()"

REM 7. Iniciar servidor
python run.py
```

### Instalación Completa - Linux/Mac

```bash
# 1. Instalar Python
sudo apt install python3 python3-pip python3-venv git  # Ubuntu/Debian
# O
brew install python3 git  # macOS

# 2. Clonar repositorio
git clone <url>
cd Estacionamiento

# 3. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Verificar
python verificar_instalacion.py

# 6. Inicializar BD
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# 7. Iniciar servidor
python run.py
```

---

## ❓ Preguntas Frecuentes

### ¿Python viene en requirements.txt?

**NO.** Python es un requisito del sistema operativo que debe instalarse manualmente. `requirements.txt` solo contiene librerías/paquetes de Python que se instalan con `pip`.

### ¿Necesito instalar Git?

**Opcional.** Puedes:
- Con Git: `git clone <url>`
- Sin Git: Descargar el repositorio como ZIP

### ¿Qué es el entorno virtual (venv)?

Es una carpeta aislada que contiene las dependencias específicas de este proyecto, sin afectar otros proyectos Python en tu sistema.

### ¿Puedo usar Python 2.x?

**NO.** El sistema requiere Python 3.8 o superior.

### ¿Dónde se guardan los datos?

En el archivo `app.db` (base de datos SQLite) que se crea automáticamente en la carpeta del proyecto.

---

## 🆘 Solución de Problemas

### Error: "python no se reconoce como comando"

**Causa:** Python no está en PATH.

**Solución Windows:**
1. Desinstalar Python
2. Reinstalar marcando "Add Python to PATH"

**Solución Linux/Mac:**
- Usar `python3` en lugar de `python`
- Agregar alias: `alias python=python3`

### Error: "No module named 'barcode'"

**Causa:** Dependencias no instaladas.

**Solución:**
```bash
pip install -r requirements.txt
```

### Error: "Cannot connect to printer"

**Solución:**
1. Verificar que la impresora esté encendida
2. Verificar IP en `config.py`
3. Probar: `ping 192.168.18.43`

---

## ✅ Checklist Final

- [ ] Python 3.8+ instalado y en PATH
- [ ] pip funcionando
- [ ] Git instalado (opcional)
- [ ] Repositorio clonado/descargado
- [ ] Entorno virtual creado y activado `(venv)`
- [ ] Dependencias instaladas sin errores
- [ ] Verificación exitosa
- [ ] Base de datos creada
- [ ] Servidor iniciado correctamente
- [ ] Acceso web funcional
- [ ] Login funcional

**Si todos los items están marcados, ¡la instalación es exitosa!** ✅
