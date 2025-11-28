"""
Servicio para generación de códigos de barras Code128
"""

import barcode
from barcode.writer import ImageWriter
import io
import base64
from PIL import Image
from config import Config


class BarcodeService:
    """Servicio para generar códigos de barras Code128"""
    
    @staticmethod
    def format_id_for_barcode(vehicle_id: int) -> str:
        """
        Formatea el ID del vehículo con padding de ceros para el lector de códigos de barras
        
        Args:
            vehicle_id: ID numérico del vehículo
            
        Returns:
            String con el ID formateado con padding (ej: "00001" para id=1)
        """
        return str(vehicle_id).zfill(Config.BARCODE_ID_LENGTH)
    
    @staticmethod
    def generate_barcode_base64(data: str) -> str:
        """
        Genera un código de barras Code128 y lo retorna en formato base64
        
        Args:
            data: Datos a codificar en el barcode (ID del vehículo, puede ser int o str)
            
        Returns:
            String base64 con la imagen del código de barras
        """
        # Formatear el ID con padding si es numérico
        formatted_data = BarcodeService.format_id_for_barcode(int(data)) if str(data).isdigit() else str(data)
        
        # Crear código de barras Code128
        code128 = barcode.get_barcode_class('code128')
        
        # Configurar writer para imagen con dimensiones apropiadas
        writer = ImageWriter()
        writer.set_options({
            'module_width': 0.3,  # Ancho de las barras
            'module_height': 15.0,  # Altura del código de barras (en mm)
            'quiet_zone': 6.5,  # Zona tranquila alrededor
            'font_size': 10,  # Tamaño de texto del ID
            'text_distance': 5.0,  # Distancia del texto a las barras
            'write_text': True,  # Mostrar el texto del ID
        })
        
        # Generar código de barras
        barcode_instance = code128(formatted_data, writer=writer)
        
        # Convertir a base64
        buffer = io.BytesIO()
        barcode_instance.write(buffer)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return img_base64
    
    @staticmethod
    def generate_barcode_image(data: str) -> Image:
        """
        Genera un código de barras Code128 y lo retorna como imagen PIL
        
        Args:
            data: Datos a codificar en el barcode (ID del vehículo, puede ser int o str)
            
        Returns:
            Imagen PIL del código de barras
        """
        # Formatear el ID con padding si es numérico
        formatted_data = BarcodeService.format_id_for_barcode(int(data)) if str(data).isdigit() else str(data)
        
        # Crear código de barras Code128
        code128 = barcode.get_barcode_class('code128')
        
        # Configurar writer
        writer = ImageWriter()
        writer.set_options({
            'module_width': 0.3,
            'module_height': 15.0,
            'quiet_zone': 6.5,
            'font_size': 10,
            'text_distance': 5.0,
            'write_text': True,
        })
        
        # Generar y retornar como imagen PIL
        barcode_instance = code128(formatted_data, writer=writer)
        buffer = io.BytesIO()
        barcode_instance.write(buffer)
        buffer.seek(0)
        
        return Image.open(buffer)


# Instancia global del servicio
barcode_service = BarcodeService()
