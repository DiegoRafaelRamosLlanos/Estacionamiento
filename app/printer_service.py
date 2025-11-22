"""
Servicio de impresión de tickets para impresora térmica Ser Force TP85K
Utiliza comandos ESC/POS para imprimir tickets de entrada y salida
"""

from escpos.printer import Network
from escpos.exceptions import Error as EscposError
from datetime import datetime
import io
import base64
from PIL import Image
from config import Config

class PrinterService:
    """Servicio para manejar impresión de tickets térmicos"""
    
    def __init__(self):
        self.enabled = Config.PRINTER_ENABLED
        self.printer_type = Config.PRINTER_TYPE
        self.printer_ip = Config.PRINTER_IP
        self.printer_port = Config.PRINTER_PORT
        self.timeout = Config.PRINTER_TIMEOUT
        self.printer = None
    
    def _connect(self):
        """Conectar a la impresora"""
        if not self.enabled:
            return False
        
        try:
            if self.printer_type == 'network':
                self.printer = Network(
                    self.printer_ip,
                    port=self.printer_port,
                    timeout=self.timeout
                )
                return True
            else:
                raise ValueError(f"Tipo de impresora no soportado: {self.printer_type}")
        except Exception as e:
            print(f"Error conectando a impresora: {e}")
            return False
    
    def _disconnect(self):
        """Desconectar de la impresora"""
        if self.printer:
            try:
                self.printer.close()
            except:
                pass
            self.printer = None
    
    def _print_header(self):
        """Imprimir encabezado del ticket"""
        self.printer.set(align='center', bold=True, width=2, height=2)
        self.printer.text("ESTACIONAMIENTO\n")
        self.printer.set(align='center', bold=False)
        self.printer.text("================================\n")
    
    def _print_qr_from_base64(self, qr_base64):
        """Imprimir código QR desde base64"""
        try:
            # Decodificar imagen base64
            img_data = base64.b64decode(qr_base64)
            img = Image.open(io.BytesIO(img_data))
            
            # Convertir a formato compatible
            img = img.convert('1')  # Convertir a blanco y negro
            
            # Imprimir imagen
            self.printer.set(align='center')
            self.printer.image(img, impl='bitImageColumn')
            self.printer.text("\n")
        except Exception as e:
            print(f"Error imprimiendo QR: {e}")
            # Si falla, imprimir el ID como texto
            self.printer.set(align='center', bold=True)
            self.printer.text(f"ID: {qr_base64[:10]}\n")
    
    def print_entry_ticket(self, vehicle):
        """
        Imprimir ticket de entrada
        
        Args:
            vehicle: Objeto Vehicle con los datos del vehículo
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.enabled:
            return (False, "Impresora deshabilitada")
        
        try:
            # Conectar a impresora
            if not self._connect():
                return (False, "No se pudo conectar a la impresora")
            
            # Encabezado
            self._print_header()
            
            # Tipo de ticket
            self.printer.set(align='center', bold=True)
            self.printer.text("*** TICKET DE ENTRADA ***\n\n")
            
            # Código QR
            if vehicle.qr_code:
                self._print_qr_from_base64(vehicle.qr_code)
            
            # Información del vehículo
            self.printer.set(align='left', bold=False)
            self.printer.text(f"ID: {vehicle.id}\n")
            self.printer.text(f"Patente: {vehicle.plate}\n")
            
            # Tipo de vehículo
            vehicle_icon = "Auto" if vehicle.type == 'auto' else "Moto"
            self.printer.text(f"Tipo: {vehicle_icon}\n")
            
            # Fecha y hora
            entry_time = vehicle.entry_time.strftime('%d/%m/%Y %H:%M:%S')
            self.printer.text(f"Entrada: {entry_time}\n")
            
            # Operador
            self.printer.text(f"Operador: {vehicle.operator_name}\n")
            
            # Cliente mensual
            if vehicle.is_monthly:
                self.printer.text("\n")
                self.printer.set(align='center', bold=True)
                self.printer.text("*** CLIENTE MENSUAL ***\n")
                self.printer.set(align='left', bold=False)
            else:
                # Tarifas
                self.printer.text("\n")
                self.printer.text("TARIFAS:\n")
                if vehicle.type == 'auto':
                    self.printer.text("1ra hora: $500\n")
                    self.printer.text("c/15 min: $125\n")
                else:
                    self.printer.text("1ra hora: $300\n")
                    self.printer.text("c/15 min: $75\n")
            
            # Pie de página
            self.printer.text("\n")
            self.printer.set(align='center')
            self.printer.text("================================\n")
            self.printer.text("Conserve este ticket\n")
            self.printer.text("Gracias por su visita\n")
            self.printer.text("\n\n")
            
            # Cortar papel
            self.printer.cut()
            
            # Desconectar
            self._disconnect()
            
            return (True, "Ticket impreso correctamente")
            
        except EscposError as e:
            self._disconnect()
            return (False, f"Error de impresora: {str(e)}")
        except Exception as e:
            self._disconnect()
            return (False, f"Error inesperado: {str(e)}")
    
    def print_exit_ticket(self, vehicle):
        """
        Imprimir ticket de salida
        
        Args:
            vehicle: Objeto Vehicle con los datos del vehículo
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.enabled:
            return (False, "Impresora deshabilitada")
        
        try:
            # Conectar a impresora
            if not self._connect():
                return (False, "No se pudo conectar a la impresora")
            
            # Encabezado
            self._print_header()
            
            # Tipo de ticket
            self.printer.set(align='center', bold=True)
            self.printer.text("*** TICKET DE SALIDA ***\n\n")
            
            # Información del vehículo
            self.printer.set(align='left', bold=False)
            self.printer.text(f"ID: {vehicle.id}\n")
            self.printer.text(f"Patente: {vehicle.plate}\n")
            
            # Tipo de vehículo
            vehicle_icon = "Auto" if vehicle.type == 'auto' else "Moto"
            self.printer.text(f"Tipo: {vehicle_icon}\n")
            
            # Fechas y horas
            entry_time = vehicle.entry_time.strftime('%d/%m/%Y %H:%M:%S')
            exit_time = vehicle.exit_time.strftime('%d/%m/%Y %H:%M:%S')
            
            self.printer.text("\n")
            self.printer.text(f"Entrada:  {entry_time}\n")
            self.printer.text(f"Salida:   {exit_time}\n")
            
            # Calcular tiempo de permanencia
            time_diff = vehicle.exit_time - vehicle.entry_time
            total_minutes = int(time_diff.total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            
            self.printer.text(f"Tiempo:   {hours}h {minutes}min\n")
            
            # Operadores
            self.printer.text("\n")
            self.printer.text(f"Op. Entrada: {vehicle.operator_name}\n")
            self.printer.text(f"Op. Salida:  {vehicle.exit_operator_name}\n")
            
            # Total a pagar
            self.printer.text("\n")
            self.printer.text("================================\n")
            
            if vehicle.is_monthly:
                self.printer.set(align='center', bold=True, width=2, height=2)
                self.printer.text("CLIENTE MENSUAL\n")
                self.printer.set(align='center', bold=True)
                self.printer.text("SIN CARGO\n")
            else:
                self.printer.set(align='center', bold=True, width=2, height=2)
                self.printer.text(f"TOTAL: ${vehicle.total_cost}\n")
            
            # Pie de página
            self.printer.set(align='center', bold=False)
            self.printer.text("================================\n")
            self.printer.text("Gracias por su visita\n")
            self.printer.text("Vuelva pronto\n")
            self.printer.text("\n\n")
            
            # Cortar papel
            self.printer.cut()
            
            # Desconectar
            self._disconnect()
            
            return (True, "Ticket impreso correctamente")
            
        except EscposError as e:
            self._disconnect()
            return (False, f"Error de impresora: {str(e)}")
        except Exception as e:
            self._disconnect()
            return (False, f"Error inesperado: {str(e)}")
    
    def test_connection(self):
        """
        Probar conexión con la impresora
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.enabled:
            return (False, "Impresora deshabilitada en configuración")
        
        try:
            if not self._connect():
                return (False, "No se pudo conectar a la impresora")
            
            # Imprimir ticket de prueba
            self.printer.set(align='center', bold=True)
            self.printer.text("TEST DE IMPRESORA\n")
            self.printer.set(align='center', bold=False)
            self.printer.text("================================\n")
            self.printer.text(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            self.printer.text(f"IP: {self.printer_ip}\n")
            self.printer.text("Conexion exitosa!\n")
            self.printer.text("================================\n")
            self.printer.text("\n\n")
            self.printer.cut()
            
            self._disconnect()
            return (True, "Conexión exitosa - Ticket de prueba impreso")
            
        except Exception as e:
            self._disconnect()
            return (False, f"Error: {str(e)}")


# Instancia global del servicio
printer_service = PrinterService()


def test_printer_connection():
    """Función auxiliar para probar la conexión desde línea de comandos"""
    success, message = printer_service.test_connection()
    print(f"{'✓' if success else '✗'} {message}")
    return success


if __name__ == "__main__":
    # Permitir ejecutar este archivo directamente para probar
    test_printer_connection()
