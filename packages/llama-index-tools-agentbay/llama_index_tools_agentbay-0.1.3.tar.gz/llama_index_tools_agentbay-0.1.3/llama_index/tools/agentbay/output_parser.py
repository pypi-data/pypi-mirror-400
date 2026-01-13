"""Output parser for AgentBay command execution results."""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ParsedOutput:
    """Parsed output from AgentBay command execution."""

    raw_output: str
    insights: List[str]
    generated_files: List[str]
    key_values: Dict[str, str]
    errors: List[str]


class OutputParser:
    """Parser for structured output from AgentBay executions."""

    def __init__(self):
        self.file_pattern = re.compile(r"FILE_GENERATED:(.+?)(?:\n|$)")
        self.key_value_pattern = re.compile(r"^(.+?):\s*(.+)$", re.MULTILINE)

    def parse(self, output: str) -> ParsedOutput:
        """
        Parse command output to extract insights, files, and key-value pairs.

        Args:
            output: Raw stdout/stderr output from command execution.

        Returns:
            ParsedOutput object with structured data.
        """
        insights = []
        generated_files = []
        key_values = {}
        errors = []

        lines = output.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for file generation signal
            file_match = self.file_pattern.search(line)
            if file_match:
                filename = file_match.group(1).strip()
                generated_files.append(filename)
                insights.append(f"Generated file: {filename}")
                continue

            # Check for error messages
            if "error" in line.lower() or "failed" in line.lower():
                errors.append(line)
                continue

            # Try to extract key-value pairs
            kv_match = self.key_value_pattern.match(line)
            if kv_match:
                key = kv_match.group(1).strip()
                value = kv_match.group(2).strip()

                # Store in dict
                key_values[key] = value

                # Add as insight if it looks like analysis result
                if any(
                    keyword in key.lower()
                    for keyword in ["total", "top", "category", "sales", "data"]
                ):
                    insights.append(f"{key}: {value}")
                continue

            # Any other non-empty line is treated as general insight
            if len(line) > 10:
                insights.append(line)

        return ParsedOutput(
            raw_output=output,
            insights=insights,
            generated_files=generated_files,
            key_values=key_values,
            errors=errors,
        )

    def extract_file_signals(self, output: str) -> List[str]:
        """
        Extract file generation signals from output.

        Args:
            output: Raw output string.

        Returns:
            List of generated file paths.
        """
        return self.file_pattern.findall(output)

    def extract_key_value(self, output: str, key: str) -> Optional[str]:
        """
        Extract a specific key-value pair from output.

        Args:
            output: Raw output string.
            key: Key to search for.

        Returns:
            Value if found, None otherwise.
        """
        pattern = re.compile(rf"^{re.escape(key)}:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
        match = pattern.search(output)
        return match.group(1).strip() if match else None

