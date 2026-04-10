import random
import string
from datetime import datetime

def generate_activation_code(prenom: str) -> str:
    """
    Génère un code unique : ES-ANNÉE-PRENOM-XXXX
    Ex: ES-2025-JEAN-4X7K
    """
    year = datetime.now().year
    prenom_clean = prenom.upper()[:6].replace(" ", "")
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ES-{year}-{prenom_clean}-{suffix}"
