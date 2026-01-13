class Casting:

    @staticmethod
    def to_float(text: str) -> float | str:
        try:
            return float(text)
        except Exception:
            return text
        

    @staticmethod
    def to_int(text: str) -> float | str:
        try:
            return int(text)
        except Exception:
            return text
        
    @staticmethod
    def to_pascal_case(text: str, **kwargs):
        
        if kwargs.get('exemption') and text in kwargs.get('exemption'):
            return text
        if kwargs.get('lower') and text.upper() in kwargs.get('lower'):
            return text.lower()
        
        words = text.split()
        pascal_case_words = [word.capitalize() for word in words]
        return ' '.join(pascal_case_words)