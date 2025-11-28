"""
Servicio para generación de códigos QR
"""

import qrcode
import io
import base64
from PIL import Image
from config import Config


class QRService:
    """Servicio para generar códigos QR"""
    
    # Configuración de QR
    QR_VERSION = 1
    QR_BOX_SIZE = 10
    QR_BORDER = 4
    
    @staticmethod
    def format_id_for_qr(vehicle_id: int) -> str:
        """
        Formatea el ID del vehículo con padding de ceros para el lector QR
        
        Args:
            vehicle_id: ID numérico del vehículo
            
        Returns:
            String con el ID formateado con padding (ej: "00001" para id=1)
        """
        return str(vehicle_id).zfill(Config.QR_ID_LENGTH)
    
    @staticmethod
    def generate_qr_base64(data: str) -> str:
        """
        Genera un código QR y lo retorna en formato base64
        
        Args:
            data: Datos a codificar en el QR (ID del vehículo, puede ser int o str)
            
        Returns:
            String base64 con la imagen del QR
        """
        # Formatear el ID con padding si es numérico
        formatted_data = QRService.format_id_for_qr(int(data)) if str(data).isdigit() else str(data)
        
        # Crear QR
        qr = qrcode.QRCode(
            version=QRService.QR_VERSION,
            box_size=QRService.QR_BOX_SIZE,
            border=QRService.QR_BORDER
        )
        qr.add_data(formatted_data)
        qr.make(fit=True)
        
        # Generar imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return img_base64
    
    @staticmethod
    def generate_qr_image(data: str) -> Image:
        """
        Genera un código QR y lo retorna como imagen PIL
        
        Args:
            data: Datos a codificar en el QR (ID del vehículo, puede ser int o str)
            
        Returns:
            Imagen PIL del QR
        """
        # Formatear el ID con padding si es numérico
        formatted_data = QRService.format_id_for_qr(int(data)) if str(data).isdigit() else str(data)
        
        qr = qrcode.QRCode(
            version=QRService.QR_VERSION,
            box_size=QRService.QR_BOX_SIZE,
            border=QRService.QR_BORDER
        )
        qr.add_data(formatted_data)
        qr.make(fit=True)
        
        return qr.make_image(fill_color="black", back_color="white")


# Instancia global del servicio
qr_service = QRService()
