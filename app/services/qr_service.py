"""
Servicio para generación de códigos QR
"""

import qrcode
import io
import base64
from PIL import Image


class QRService:
    """Servicio para generar códigos QR"""
    
    # Configuración de QR
    QR_VERSION = 1
    QR_BOX_SIZE = 10
    QR_BORDER = 4
    
    @staticmethod
    def generate_qr_base64(data: str) -> str:
        """
        Genera un código QR y lo retorna en formato base64
        
        Args:
            data: Datos a codificar en el QR (generalmente el ID del vehículo)
            
        Returns:
            String base64 con la imagen del QR
        """
        # Crear QR
        qr = qrcode.QRCode(
            version=QRService.QR_VERSION,
            box_size=QRService.QR_BOX_SIZE,
            border=QRService.QR_BORDER
        )
        qr.add_data(str(data))
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
            data: Datos a codificar en el QR
            
        Returns:
            Imagen PIL del QR
        """
        qr = qrcode.QRCode(
            version=QRService.QR_VERSION,
            box_size=QRService.QR_BOX_SIZE,
            border=QRService.QR_BORDER
        )
        qr.add_data(str(data))
        qr.make(fit=True)
        
        return qr.make_image(fill_color="black", back_color="white")


# Instancia global del servicio
qr_service = QRService()
