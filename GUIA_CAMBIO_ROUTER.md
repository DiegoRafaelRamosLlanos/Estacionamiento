# Guía: Cambiar Configuración de Impresora al Cambiar de Router

## 📡 ¿Cuándo Necesito Esta Guía?

Cuando cambies de router o red y la impresora deje de funcionar. Esto sucede porque:

- **Router actual:** 192.168.18.X
- **Router nuevo:** 192.168.1.X (o cualquier otra subred)
- **Impresora:** Configurada en 192.168.18.43 (NO puede comunicarse con la nueva red)

---

## 🔍 PASO 1: Identificar la Nueva Subred del Router

### Opción A: Ver IP de Tu PC

1. **Windows - CMD:**
   ```cmd
   ipconfig
   ```
   
   Buscar la línea que dice:
   ```
   IPv4 Address. . . . . . . . . . . : 192.168.X.YYY
                                        ^^^^^^^^^^^
                                        Esta es tu subred
   ```

2. **Ejemplos comunes:**
   - `192.168.1.15` → Subred: **192.168.1.X**
   - `192.168.0.25` → Subred: **192.168.0.X**
   - `192.168.18.5` → Subred: **192.168.18.X** (actual)

### Opción B: Ver Configuración del Router

Acceder a la configuración del router (usualmente http://192.168.1.1 o http://192.168.0.1)

---

## 🖨️ PASO 2: Reconfigurar IP de la Impresora

### Método 1: Usando el Panel de Impresión de Prueba

La impresora **Ser Force TP85K** tiene un botón de FEED que imprime la configuración.

#### 2.1. Imprimir Configuración Actual

1. Apagar la impresora
2. Mantener presionado el botón **FEED**
3. Encender la impresora (sin soltar FEED)
4. Soltar FEED cuando empiece a imprimir
5. Se imprimirá un ticket con:
   ```
   IP Address: 192.168.18.43
   Subnet Mask: 255.255.255.0
   Gateway: 192.168.18.1
   ```

#### 2.2. Configurar Nueva IP

**IMPORTANTE:** La impresora NO tiene interfaz web. Debes usar uno de estos métodos:

---

### Método 2: Usando Herramienta de Configuración del Fabricante

Muchas impresoras ESC/POS vienen con una herramienta de Windows.

1. **Buscar en la caja/CD** de la impresora un software llamado:
   - "Printer Setup Utility"
   - "Network Configuration Tool"
   - "IP Config Tool"

2. **Si no tienes el CD:**
   - Buscar en la página del fabricante: http://www.serforceltd.com
   - O herramienta genérica: https://www.star-m.jp/products/s_print/sdk/starprnt_sdk.htm

3. **Usar la herramienta:**
   - Conectar impresora y PC a la **misma red**
   - Abrir la herramienta
   - Detectar impresora
   - Cambiar IP a la nueva subred

---

### Método 3: Configuración Manual por Cable USB (Recomendado)

Si la impresora soporta configuración por USB:

#### 3.1. Conectar Impresora por USB

1. Conectar cable USB de la impresora a la PC
2. Windows instalará drivers automáticamente

#### 3.2. Usar python-escpos para Configurar

Crear un script temporal:

```python
# config_printer_ip.py
from escpos.printer import Usb

# Conectar por USB (ajustar vendor_id y product_id según tu impresora)
# Estos IDs se encuentran en: Panel de Control > Dispositivos > Propiedades de la impresora
printer = Usb(0x0416, 0x5011)  # Cambiar por los IDs de tu impresora

# Configurar nueva IP
# NOTA: Los comandos específicos varían según el modelo
# Este es un ejemplo genérico

nueva_ip = "192.168.1.43"  # CAMBIAR: Nueva IP en la subred del router nuevo
gateway = "192.168.1.1"     # CAMBIAR: IP del router nuevo
mascara = "255.255.255.0"   # Usualmente este valor no cambia

print(f"Configurando impresora:")
print(f"  IP: {nueva_ip}")
print(f"  Gateway: {gateway}")
print(f"  Máscara: {mascara}")

# Imprimir confirmación
printer.text(f"Nueva configuración:\n")
printer.text(f"IP: {nueva_ip}\n")
printer.text(f"Gateway: {gateway}\n")
printer.text(f"Máscara: {mascara}\n\n")
printer.cut()

printer.close()

print("✓ Configuración enviada a la impresora")
print("  Reinicia la impresora para aplicar cambios")
```

**Ejecutar:**
```bash
python config_printer_ip.py
```

---

### Método 4: Resetear a DHCP (Temporal)

Si nada funciona, configurar la impresora en modo DHCP temporalmente:

1. **Resetear impresora a valores de fábrica:**
   - Apagar impresora
   - Mantener FEED + botón de power
   - Esperar 10 segundos
   - Encender la impresora

2. **Configurar DHCP:**
   - La impresora recibirá IP automática del router
   - Imprimir ticket de prueba para ver la nueva IP
   - Anotar la IP asignada

3. **Hacer la IP estática en el router:**
   - Acceder al router (192.168.1.1)
   - Buscar "DHCP Reservations" o "IP estática"
   - Asignar la IP permanentemente a la MAC de la impresora

---

## 🔧 PASO 3: Actualizar Configuración del Sistema

### 3.1. Editar config.py

Abrir `c:\Users\Ramos\Estacionamiento\config.py` y cambiar:

**Antes (Router 192.168.18.X):**
```python
PRINTER_IP = '192.168.18.43'
```

**Después (Router 192.168.1.X - EJEMPLO):**
```python
PRINTER_IP = '192.168.1.43'  # CAMBIAR: Usar la IP que configuraste
```

### 3.2. Guardar y Reiniciar

1. Guardar el archivo `config.py`
2. Reiniciar el servidor:
   ```bash
   # Si está corriendo, presionar Ctrl+C
   # Luego:
   python run.py
   ```

---

## ✅ PASO 4: Verificar Conexión

### 4.1. Probar Ping

```cmd
ping 192.168.1.43
```

**Resultado esperado:**
```
Reply from 192.168.1.43: bytes=32 time<1ms TTL=64
Reply from 192.168.1.43: bytes=32 time<1ms TTL=64
```

Si dice "Request timed out", la impresora NO está en la red.

### 4.2. Probar Impresión desde el Sistema

```bash
python test_printer.py
```

**Resultado esperado:**
```
✓ Conexión exitosa - Ticket de prueba impreso
```

---

## 📋 Tabla de Referencia Rápida

| Componente | Qué Cambiar | Dónde Cambiarlo |
|------------|-------------|-----------------|
| **Router** | Nada (automático) | - |
| **PC** | Nada (recibe IP automática) | - |
| **Impresora** | IP fija | Panel de impresora / Herramienta config |
| **config.py** | `PRINTER_IP` | `c:\Users\Ramos\Estacionamiento\config.py` |

---

## 🎯 Ejemplos de Escenarios Comunes

### Escenario 1: Router TP-Link Nuevo (192.168.0.X)

```
Router nuevo IP: 192.168.0.1
PC obtiene IP: 192.168.0.15 (automático)

Configurar impresora:
  IP: 192.168.0.43
  Gateway: 192.168.0.1
  Máscara: 255.255.255.0

Actualizar config.py:
  PRINTER_IP = '192.168.0.43'
```

### Escenario 2: Hotspot del Celular (192.168.43.X)

```
Hotspot IP: 192.168.43.1
PC obtiene IP: 192.168.43.25 (automático)

Configurar impresora:
  IP: 192.168.43.43
  Gateway: 192.168.43.1
  Máscara: 255.255.255.0

Actualizar config.py:
  PRINTER_IP = '192.168.43.43'
```

### Escenario 3: Red Empresarial (10.0.0.X)

```
Router IP: 10.0.0.1
PC obtiene IP: 10.0.0.150 (automático)

Configurar impresora:
  IP: 10.0.0.43
  Gateway: 10.0.0.1
  Máscara: 255.255.255.0

Actualizar config.py:
  PRINTER_IP = '10.0.0.43'
```

---

## 📞 Información del Modelo de Impresora

**Modelo:** Ser Force TP85K
**Tipo:** Impresora térmica ESC/POS
**Puerto de red:** 9100 (ESC/POS estándar)

**Botones:**
- FEED: Avance de papel / Configuración
- POWER: Encendido/Apagado

**Conectividad:**
- Ethernet (RJ45)
- USB (opcional, según modelo)

---

## ⚠️ Notas Importantes

1. **La IP de la impresora debe terminar diferente** a la IP de tu PC:
   - ✅ PC: 192.168.1.15, Impresora: 192.168.1.43
   - ❌ PC: 192.168.1.43, Impresora: 192.168.1.43 (CONFLICTO)

2. **Usar IP fuera del rango DHCP del router:**
   - Routers suelen asignar: 192.168.1.100 - 192.168.1.200
   - Usar para impresora: 192.168.1.43 (fuera del rango)

3. **El último número (.43) es arbitrario:**
   - Puedes usar .43, .50, .100, etc.
   - Solo debe ser único en la red

4. **El puerto 9100 NO cambia:**
   - Es estándar para impresoras ESC/POS
   - Solo cambiar si el manual indica otro

---

## 🔄 Procedimiento Completo Resumido

```
1. Conectar a nuevo router
   ↓
2. Ver nueva subred de la PC (ipconfig)
   ↓
3. Configurar impresora en la nueva subred
   ↓
4. Actualizar config.py con la nueva IP
   ↓
5. Probar ping a la impresora
   ↓
6. Ejecutar test_printer.py
   ↓
7. ✓ Listo!
```

---

## 📝 Checklist Post-Cambio de Router

- [ ] Verificar IP de la PC con `ipconfig`
- [ ] Anotar nueva subred (ej: 192.168.1.X)
- [ ] Reconfigurar IP de impresora
- [ ] Actualizar `PRINTER_IP` en `config.py`
- [ ] Probar ping a la impresora
- [ ] Ejecutar `python test_printer.py`
- [ ] Reiniciar servidor `python run.py`
- [ ] Probar registro de vehículo con impresión
- [ ] Confirmar que el ticket se imprime ✓

---

## 🆘 Solución de Problemas

### Problema: "Impresora no responde al ping"

**Causas posibles:**
1. IP configurada incorrectamente
2. Impresora en red diferente
3. Firewall bloqueando

**Soluciones:**
1. Verificar IP con ticket de prueba de la impresora
2. Verificar que PC e impresora estén en el mismo router
3. Desactivar firewall temporalmente

### Problema: "Cannot connect to printer"

**Verificar:**
```bash
# 1. Ping funciona?
ping 192.168.1.43

# 2. Puerto abierto?
telnet 192.168.1.43 9100

# 3. IP correcta en config.py?
type config.py | findstr PRINTER_IP
```

### Problema: "Impresora imprime caracteres raros"

**Causa:** Codificación incorrecta o comando ESC/POS no soportado.

**Solución:** 
- Verificar que sea impresora ESC/POS compatible
- Actualizar drivers
- Revisar manual de la impresora

---

¿Necesitas ayuda con algún paso específico? 🔧
