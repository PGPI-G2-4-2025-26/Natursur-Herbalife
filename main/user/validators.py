from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import (
    MinimumLengthValidator, 
    NumericPasswordValidator, 
    CommonPasswordValidator,
    UserAttributeSimilarityValidator
)

_common_checker = CommonPasswordValidator()


class CustomUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        if password.isdigit():
            return

        if password.lower().strip() in _common_checker.passwords:
            return

        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("La contraseña se parece demasiado a tus datos personales."),
                code='password_too_similar',
            )

class CustomMinimumLengthValidator(MinimumLengthValidator):
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("La contraseña debe tener al menos %(min_length)d caracteres."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

class CustomNumericPasswordValidator(NumericPasswordValidator):
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("La contraseña no puede contener solo números."),
                code='password_entirely_numeric',
            )

class CustomCommonPasswordValidator(CommonPasswordValidator):
    def validate(self, password, user=None):
        if password.isdigit():
            return

        if password.lower().strip() in self.passwords:
            raise ValidationError(
                _("Esa contraseña es muy común y fácil de adivinar."),
                code='password_too_common',
            )