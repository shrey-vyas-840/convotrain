"""Provider-independent knowledge extraction interface."""

from abc import ABC, abstractmethod

from app.schemas.extraction import ExtractionInput, ExtractionOutput


class KnowledgeExtractor(ABC):
    """Application-level contract for knowledge extraction providers."""

    @abstractmethod
    def extract(self, request: ExtractionInput) -> ExtractionOutput:
        """Extract candidate knowledge facts from an owner message."""
        raise NotImplementedError