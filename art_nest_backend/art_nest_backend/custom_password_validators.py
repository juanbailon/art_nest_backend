from django.core.exceptions import ValidationError
import re

class MinimumAmountOfNumericDigitsValidator:
    """ Validates that the password contains a minimum amont of numeric digits """

    def __init__(self, min_amount_num_digits=1):
        self.min_num_digits = min_amount_num_digits

    def validate(self, password, user=None):
        # Ensure the password contains at least the specify amount of numeric digit
        num_digits = sum(char.isdigit() for char in password)
        if num_digits < self.min_num_digits:
            raise ValidationError(self.get_help_text())

    def get_help_text(self):
        return f"Your password must contain at least {self.min_num_digits} numeric digit{'s.' if self.min_num_digits>1 else '.'}"


class MinimumAmountOfSpecialCharactersValidator:
    """ Validates that the password contains a minimum amont of special characters """

    def __init__(self,
                 special_chars= "@\#%!&?|<>;,:_/~`='-.\"^$[]{}*+()",
                 regex=r"[@\\#%!&?|<>;,:_/~`='\-\.\"\^\$\[\]\{\}\*\+\(\)]",
                 min_amount=1
                ):
        self.special_chars = special_chars
        self.regex = regex
        self.min_amount = min_amount
    
    def validate(self, password, user=None):
        # Ensure the password contains at least the specify amount of special characters
        found_special_chars = re.findall(self.regex, password)

        if len(found_special_chars) < self.min_amount:
            raise ValidationError(self.get_help_text())

    def get_help_text(self):
        return f"Your password must contain at least {self.min_amount} special character{'s.' if self.min_amount==1 else '.'}  {self.special_chars}"