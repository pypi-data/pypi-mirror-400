"""
The Forge - Development & SDLC Module.

Provides agents for software development automation:
- ArchitectAgent: Translates requirements into system designs
- EngineerAgent: Generates and refines code
- QualityAgent: Creates and runs tests
"""

from openfoundry.forge.agents.architect import ArchitectAgent
from openfoundry.forge.agents.engineer import EngineerAgent
from openfoundry.forge.agents.quality import QualityAgent

__all__ = [
    "ArchitectAgent",
    "EngineerAgent",
    "QualityAgent",
]
