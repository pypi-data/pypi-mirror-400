"""
Formatting utilities for context and prompts.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from ..reasoning import StructuredContext, HybridAnswer


class OutputFormat(Enum):
    """Output format types."""
    PLAIN = "plain"
    MARKDOWN = "markdown"
    JSON = "json"
    PROMPT = "prompt"


class ContextFormatter:
    """
    Format structured context for different uses.
    
    Supports:
    - Plain text
    - Markdown
    - JSON
    - LLM prompt format
    
    Example:
        formatter = ContextFormatter()
        
        # For display
        text = formatter.format(context, OutputFormat.MARKDOWN)
        
        # For LLM
        prompt = formatter.format(context, OutputFormat.PROMPT)
    """
    
    def format(
        self,
        context: StructuredContext,
        output_format: OutputFormat = OutputFormat.PLAIN
    ) -> str:
        """
        Format context to specified format.
        
        Args:
            context: StructuredContext to format
            output_format: Desired output format
            
        Returns:
            Formatted string
        """
        if output_format == OutputFormat.PLAIN:
            return self._format_plain(context)
        elif output_format == OutputFormat.MARKDOWN:
            return self._format_markdown(context)
        elif output_format == OutputFormat.JSON:
            import json
            return json.dumps(context.to_dict(), indent=2)
        else:
            return self._format_prompt(context)
    
    def _format_plain(self, context: StructuredContext) -> str:
        """Format as plain text."""
        lines = [f"Query: {context.query}", ""]
        
        if context.relevant_facts:
            lines.append("Facts:")
            for fact in context.relevant_facts:
                lines.append(f"  - {fact.get('content', '')}")
            lines.append("")
        
        if context.inferences:
            lines.append("Inferences:")
            for inf in context.inferences:
                lines.append(f"  - {inf.get('source', '?')} {inf.get('relation', '?')} {inf.get('target', '?')}")
            lines.append("")
        
        if context.contradictions:
            lines.append("Warnings:")
            for cont in context.contradictions:
                lines.append(f"  ! {cont.get('description', '')}")
            lines.append("")
        
        lines.append(f"Confidence: {context.confidence:.0%}")
        
        return "\n".join(lines)
    
    def _format_markdown(self, context: StructuredContext) -> str:
        """Format as markdown."""
        lines = [f"# Query: {context.query}", ""]
        
        if context.relevant_facts:
            lines.append("## Facts")
            for fact in context.relevant_facts:
                lines.append(f"- {fact.get('content', '')}")
            lines.append("")
        
        if context.inferences:
            lines.append("## Inferences")
            for inf in context.inferences:
                lines.append(f"- **{inf.get('source', '?')}** → *{inf.get('relation', '?')}* → **{inf.get('target', '?')}**")
                lines.append(f"  - Confidence: {inf.get('confidence', 0):.0%}")
            lines.append("")
        
        if context.reasoning_paths:
            lines.append("## Reasoning Paths")
            for i, path in enumerate(context.reasoning_paths, 1):
                lines.append(f"### Path {i}")
                steps = path.get('steps', [])
                lines.append(" → ".join(steps))
            lines.append("")
        
        if context.hierarchy:
            lines.append("## Hierarchy")
            path = context.hierarchy.get('path', [])
            lines.append(f"Position: {' > '.join(path)}")
            lines.append("")
        
        if context.contradictions:
            lines.append("## ⚠️ Warnings")
            for cont in context.contradictions:
                lines.append(f"- {cont.get('description', '')}")
            lines.append("")
        
        lines.append(f"---\n*Confidence: {context.confidence:.0%}*")
        
        return "\n".join(lines)
    
    def _format_prompt(self, context: StructuredContext) -> str:
        """Format as LLM prompt."""
        return context.to_prompt()


class PromptBuilder:
    """
    Build prompts for different LLM tasks.
    
    Provides templates for:
    - Question answering
    - Explanation generation
    - Summarization
    - Reasoning
    
    Example:
        builder = PromptBuilder()
        
        prompt = builder.build_qa_prompt(context, question)
        response = llm.generate(prompt)
    """
    
    # Prompt templates
    TEMPLATES = {
        "qa": """You are a knowledgeable assistant. Use ONLY the provided context to answer the question.
If the context doesn't contain enough information, say so.

{context}

Question: {question}

Answer:""",

        "explain": """You are an expert at explaining concepts clearly.
Based on the following knowledge, explain the topic in simple terms.

{context}

Topic to explain: {topic}

Explanation:""",

        "summarize": """Summarize the following knowledge concisely.

{context}

Summary:""",

        "reason": """You are a logical reasoner. Based on the following facts and inferences,
provide a step-by-step reasoning for the question.

{context}

Question: {question}

Step-by-step reasoning:""",

        "validate": """Review the following knowledge for consistency and accuracy.
Point out any issues or contradictions.

{context}

Validation:""",
    }
    
    def __init__(self, custom_templates: Optional[Dict[str, str]] = None):
        """
        Initialize prompt builder.
        
        Args:
            custom_templates: Additional templates to add
        """
        self.templates = self.TEMPLATES.copy()
        if custom_templates:
            self.templates.update(custom_templates)
    
    def build_qa_prompt(
        self,
        context: StructuredContext,
        question: Optional[str] = None
    ) -> str:
        """Build question-answering prompt."""
        q = question or context.query
        ctx = context.to_prompt()
        return self.templates["qa"].format(context=ctx, question=q)
    
    def build_explain_prompt(
        self,
        context: StructuredContext,
        topic: str
    ) -> str:
        """Build explanation prompt."""
        ctx = context.to_prompt()
        return self.templates["explain"].format(context=ctx, topic=topic)
    
    def build_summarize_prompt(self, context: StructuredContext) -> str:
        """Build summarization prompt."""
        ctx = context.to_prompt()
        return self.templates["summarize"].format(context=ctx)
    
    def build_reason_prompt(
        self,
        context: StructuredContext,
        question: Optional[str] = None
    ) -> str:
        """Build reasoning prompt."""
        q = question or context.query
        ctx = context.to_prompt()
        return self.templates["reason"].format(context=ctx, question=q)
    
    def build_custom_prompt(
        self,
        template_name: str,
        context: StructuredContext,
        **kwargs
    ) -> str:
        """Build prompt from custom template."""
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        ctx = context.to_prompt()
        return self.templates[template_name].format(context=ctx, **kwargs)

