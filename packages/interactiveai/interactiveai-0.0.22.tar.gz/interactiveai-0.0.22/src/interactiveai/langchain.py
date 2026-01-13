"""
InteractiveAI LangChain integration module.

Re-exports LangChain-related components from langfuse.
"""

from langfuse.langchain import CallbackHandler

__all__ = ["CallbackHandler"]
