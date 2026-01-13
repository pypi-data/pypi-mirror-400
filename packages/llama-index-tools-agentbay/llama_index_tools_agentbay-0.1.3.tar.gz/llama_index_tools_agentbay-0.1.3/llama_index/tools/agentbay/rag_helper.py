"""RAG helper utilities for AgentBay tools."""

from typing import List, Dict, Any
from datetime import datetime
import json

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.schema import TextNode

from .output_parser import OutputParser


class InsightExtractor:
    """Extract insights from AgentBay command outputs for RAG indexing."""

    @staticmethod
    def extract_insights_from_output(
        output: str, task_description: str = "", stage: str = ""
    ) -> List[Document]:
        """
        Extract insights from command output and convert to Documents.

        Args:
            output: The raw output from a command execution.
            task_description: Optional description of the task that generated this output.
            stage: Optional stage identifier (e.g., "data_generation", "analysis").

        Returns:
            List of unique Document objects containing extracted insights.
        """
        parser = OutputParser()
        parsed = parser.parse(output)
        files = parsed.generated_files
        key_values = parsed.key_values

        documents = []
        timestamp = datetime.now().isoformat()

        # Track what we've already added to avoid duplicates
        seen_texts = set()

        def add_document(text: str, doc_type: str, extra_metadata: Dict[str, Any] = None) -> None:
            """Helper to add document with deduplication."""
            text_key = text.strip().lower()
            if text_key and text_key not in seen_texts:
                seen_texts.add(text_key)
                metadata = {
                    "type": doc_type,
                    "timestamp": timestamp,
                }
                if stage:
                    metadata["stage"] = stage
                if extra_metadata:
                    metadata.update(extra_metadata)
                documents.append(Document(text=text, metadata=metadata))

        # Add task description if provided
        if task_description:
            add_document(
                f"Task: {task_description}",
                "task_description"
            )

        # Combine key-value pairs into a summary if multiple exist
        if len(key_values) > 1:
            # Create a combined summary document
            summary_parts = []
            for key, value in key_values.items():
                if isinstance(value, dict):
                    # For structured data, keep it readable
                    summary_parts.append(f"{key}: {json.dumps(value)}")
                else:
                    summary_parts.append(f"{key}: {value}")

            combined_text = "Analysis results: " + ", ".join(summary_parts)
            add_document(combined_text, "combined_results", {"key_values": key_values})

        # Also add individual key-value pairs for specific queries
        for key, value in key_values.items():
            if isinstance(value, dict):
                # For JSON data, create a structured insight
                text = f"{key}: {json.dumps(value)}"
                add_document(text, "structured_data", {"key": key, "value": value})
            else:
                # For simple key-value pairs
                text = f"{key}: {value}"
                add_document(text, "key_value", {"key": key, "value": str(value)})

        # Add generated files summary if multiple files
        if len(files) > 1:
            files_text = f"Generated files: {', '.join(files)}"
            add_document(files_text, "files_summary", {"files": files})

        # Add individual file paths
        for file_path in files:
            add_document(
                f"Generated file: {file_path}",
                "generated_file",
                {"file_path": file_path}
            )

        # Add general insights (but avoid duplicates with key-values and files)
        for insight in parsed.insights:
            if insight and len(insight.strip()) > 10:
                # Skip if it's already covered by key-values or files
                insight_lower = insight.strip().lower()
                is_duplicate = (
                    insight_lower.startswith("generated file:") or
                    any(f"{k}:".lower() in insight_lower for k in key_values.keys())
                )
                if not is_duplicate:
                    add_document(insight, "general_insight")

        return documents


class AgentBayRAGManager:
    """Manage RAG index for AgentBay execution results."""

    def __init__(self):
        """Initialize RAG manager."""
        self.documents: List[Document] = []
        self.index: VectorStoreIndex = None

    def add_execution_result(
        self, output: str, task_description: str = "", stage: str = ""
    ) -> List[Document]:
        """
        Add execution result to RAG index.

        Args:
            output: The raw output from a command execution.
            task_description: Optional description of the task.
            stage: Optional stage identifier (e.g., "data_generation", "analysis").

        Returns:
            List of extracted documents.
        """
        new_docs = InsightExtractor.extract_insights_from_output(
            output, task_description, stage
        )
        self.documents.extend(new_docs)

        # Rebuild index with all documents
        if self.documents:
            self.index = VectorStoreIndex.from_documents(self.documents)

        return new_docs

    def query(self, question: str) -> str:
        """
        Query the RAG index.

        Args:
            question: The question to ask.

        Returns:
            Answer from the RAG system.
        """
        if not self.index:
            return "No data has been indexed yet. Please run some analysis first."

        query_engine = self.index.as_query_engine()
        response = query_engine.query(question)
        return str(response)

    def get_all_insights(self) -> List[str]:
        """
        Get all insights as text.

        Returns:
            List of insight texts.
        """
        return [doc.text for doc in self.documents]

    def clear(self):
        """Clear all documents and index."""
        self.documents = []
        self.index = None


def create_rag_manager() -> AgentBayRAGManager:
    """
    Create a new RAG manager instance.

    Returns:
        AgentBayRAGManager instance.

    Example:
        >>> from llama_index.tools.agentbay import create_rag_manager
        >>> rag = create_rag_manager()
        >>> rag.add_execution_result(output, "Data analysis task")
        >>> answer = rag.query("What was the total sales?")
    """
    return AgentBayRAGManager()

