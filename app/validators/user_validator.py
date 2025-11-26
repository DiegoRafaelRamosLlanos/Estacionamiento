"""
Validador de datos de usuarios
"""

from app.constants.user_roles import UserRole
from app.exceptions import ValidationException


class UserValidator:
    """Valida datos relacionados con usuarios"""
    
    MIN_USERNAME_LENGTH = 3
    MIN_PASSWORD_LENGTH = 4
    MIN_NAME_LENGTH = 3
    
    @staticmethod
    def validate_username(username: str) -> str:
        """
        Valida el nombre de usuario
        
        Args:
            username: Nombre de usuario a validar
            
        Returns:
            Username normalizado (lowercase, sin espacios)
            
        Raises:
            ValidationException: Si el username es inválido
        """
        if not username:
            raise ValidationException('username', 'El nombre de usuario es obligatorio')
        
        # Normalizar
        normalized = username.lower().strip()
        
        if len(normalized) < UserValidator.MIN_USERNAME_LENGTH:
            raise ValidationException(
                'username',
                f'El nombre de usuario debe tener al menos {UserValidator.MIN_USERNAME_LENGTH} caracteres'
            )
        
        # Verificar que solo contenga letras, números y guiones bajos
        if not normalized.replace('_', '').replace('-', '').isalnum():
            raise ValidationException(
                'username',
                'El nombre de usuario solo puede contener letras, números, guiones y guiones bajos'
            )
        
        return normalized
    
    @staticmethod
    def validate_name(name: str) -> str:
        """
        Valida el nombre completo del usuario
        
        Args:
            name: Nombre a validar
            
        Returns:
            Nombre normalizado
            
        Raises:
            ValidationException: Si el nombre es inválido
        """
        if not name or not name.strip():
            raise ValidationException('name', 'El nombre completo es obligatorio')
        
        normalized = name.strip()
        
        if len(normalized) < UserValidator.MIN_NAME_LENGTH:
            raise ValidationException(
                'name',
                f'El nombre debe tener al menos {UserValidator.MIN_NAME_LENGTH} caracteres'
            )
        
        return normalized
    
    @staticmethod
    def validate_password(password: str) -> str:
        """
        Valida la contraseña
        
        Args:
            password: Contraseña a validar
            
        Returns:
            Contraseña validada
            
        Raises:
            ValidationException: Si la contraseña es inválida
        """
        if not password:
            raise ValidationException('password', 'La contraseña es obligatoria')
        
        if len(password) < UserValidator.MIN_PASSWORD_LENGTH:
            raise ValidationException(
                'password',
                f'La contraseña debe tener al menos {UserValidator.MIN_PASSWORD_LENGTH} caracteres'
            )
        
        return password
    
    @staticmethod
    def validate_role(role: str) -> str:
        """
        Valida el rol del usuario
        
        Args:
            role: Rol a validar
            
        Returns:
            Rol validado
            
        Raises:
            ValidationException: Si el rol es inválido
        """
        if not role:
            raise ValidationException('role', 'El rol es obligatorio')
        
        if not UserRole.is_valid(role):
            valid_roles = ', '.join(UserRole.get_all_values())
            raise ValidationException(
                'role',
                f'Rol inválido. Valores permitidos: {valid_roles}'
            )
        
        return role
    
    @staticmethod
    def validate_user_data(data: dict, password_required: bool = True) -> dict:
        """
        Valida datos completos de usuario
        
        Args:
            data: Dict con datos del usuario
            password_required: Si la contraseña es obligatoria
            
        Returns:
            Dict con datos validados
            
        Raises:
            ValidationException: Si algún dato es inválido
        """
        validated = {}
        
        # Validar username
        username = data.get('username')
        validated['username'] = UserValidator.validate_username(username)
        
        # Validar nombre
        name = data.get('name')
        validated['name'] = UserValidator.validate_name(name)
        
        # Validar rol
        role = data.get('role')
        validated['role'] = UserValidator.validate_role(role)
        
        # Validar contraseña (si es requerida)
        if password_required:
            password = data.get('password')
            validated['password'] = UserValidator.validate_password(password)
        
        return validated
