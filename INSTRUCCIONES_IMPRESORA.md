# INSTRUCCIONES PARA CONFIGURAR LA IMPRESORA EN TU RED

## Problema Actual
- Tu PC está en la red: 192.168.1.x
- La impresora está en: 192.168.0.31
- No pueden comunicarse porque están en redes diferentes

## Solución: Configurar la impresora para tu red

### PASO 1: Conectar temporalmente a la red de la impresora

1. Abre "Configuración de red" en Windows
2. Ve a "Cambiar opciones del adaptador"
3. Click derecho en tu adaptador de red → Propiedades
4. Selecciona "Protocolo de Internet versión 4 (TCP/IPv4)" → Propiedades
5. Anota tu configuración actual (para restaurarla después)
6. Cambia temporalmente a:
   - Dirección IP: 192.168.0.100
   - Máscara de subred: 255.255.255.0
   - Puerta de enlace: 192.168.0.1
7. Click OK

### PASO 2: Verificar conexión con la impresora

Abre PowerShell y ejecuta:
```powershell
ping 192.168.0.31
```

Si responde, continúa al Paso 3.

### PASO 3: Acceder a la configuración web de la impresora

1. Abre un navegador web
2. Ve a: http://192.168.0.31
3. Busca la sección "Network Settings" o "Ethernet Settings"
4. Cambia la configuración a:
   - IP Address: 192.168.1.100 (o cualquier IP libre en tu red)
   - Subnet Mask: 255.255.255.0
   - Gateway: 192.168.1.1 (tu router)
   - DHCP: OFF (desactivado)
5. Guarda los cambios
6. Reinicia la impresora

### PASO 4: Restaurar la configuración de tu PC

1. Vuelve a "Propiedades de TCP/IPv4"
2. Restaura tu configuración original
   O selecciona "Obtener una dirección IP automáticamente"
3. Click OK

### PASO 5: Verificar nueva conexión

```powershell
ping 192.168.1.100
```

### PASO 6: Actualizar config.py

Cambia en config.py:
```python
PRINTER_ENABLED = True
PRINTER_TYPE = 'network'
PRINTER_IP = '192.168.1.100'  # La nueva IP que configuraste
```

### PASO 7: Probar

```bash
python test_printer.py
```

---

## Alternativa: Usar DHCP (más fácil pero menos confiable)

Si tu router tiene DHCP activo:

1. Conecta la impresora a tu red
2. Imprime la página de auto-test desde la impresora (mantén presionado el botón FEED)
3. Busca la IP que le asignó el DHCP
4. Usa esa IP en config.py
5. **Importante**: Reserva esa IP en tu router para que no cambie

---

## ¿Necesitas ayuda?

Si no te sientes cómodo cambiando la configuración de red, puedo:
1. Deshabilitar temporalmente la impresora (PRINTER_ENABLED = False)
2. El sistema funcionará sin impresión hasta que configures la red
3. Cuando esté lista, solo cambias a True

¿Qué prefieres hacer?
