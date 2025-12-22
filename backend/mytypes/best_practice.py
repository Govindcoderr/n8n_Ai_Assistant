from abc import ABC, abstractmethod
from typing import Protocol

from .categorization import WorkflowTechniqueType

class BestPracticesDocument(ABC):
    """
    Interface for best practices documentation for a specific workflow technique
    """

    @property
    @abstractmethod
    def technique(self) -> WorkflowTechniqueType:
        """The workflow technique this documentation covers"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the documentation"""
        pass

    @abstractmethod
    def get_documentation(self) -> str:
        """
        Returns the full documentation as a markdown-formatted string
        """
        pass
