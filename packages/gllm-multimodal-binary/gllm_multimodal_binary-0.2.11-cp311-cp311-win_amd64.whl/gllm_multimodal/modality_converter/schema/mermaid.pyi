from pydantic import BaseModel

class Mermaid(BaseModel):
    """Mermaid additional metadata.

    Attributes:
        diagram_type (str): type of the diagram to be generated.
        context (str): additional context to generate mermaid.
    """
    diagram_type: str | None
    context: str | None
