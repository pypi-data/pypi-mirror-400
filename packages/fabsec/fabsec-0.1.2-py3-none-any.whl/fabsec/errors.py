# fabsec/errors.py
class FabSecError(Exception):
    """Erreur de base SDK FabSec."""
    pass


class FabSecHTTPError(FabSecError):
    def __init__(self, status_code: int, detail, response_text: str = ""):
        super().__init__(f"FabSec HTTP {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail
        self.response_text = response_text
