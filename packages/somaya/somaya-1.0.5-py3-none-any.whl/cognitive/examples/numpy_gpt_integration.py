"""
Integration Example: SOMA Cognitive + NumPy GPT
=================================================

This example shows how to use SOMA Cognitive with your
NumPy GPT to create a powerful hybrid reasoning system.

The key insight:
    SOMA Cognitive does the THINKING (symbolic reasoning)
    NumPy GPT does the SPEAKING (natural language generation)

Run this example:
    python -m SOMA_cognitive.examples.numpy_gpt_integration
"""

import sys
from typing import Optional

# Import cognitive components
from ..integration import CognitivePipeline
from ..reasoning import HybridReasoner, StructuredContext
from ..graph import RelationType
from ..utils import ContextFormatter, PromptBuilder, ExplanationScorer


def create_knowledge_base(pipeline: CognitivePipeline):
    """Build a sample knowledge base about AI/ML."""
    
    print("Building knowledge base...")
    
    # Add facts about AI
    facts = [
        "Machine Learning is a subset of Artificial Intelligence",
        "Deep Learning is a type of Machine Learning",
        "Neural Networks are the foundation of Deep Learning",
        "Transformers are a type of Neural Network architecture",
        "Attention mechanism allows models to focus on relevant parts",
        "Self-attention computes relationships between all positions",
        "BERT uses bidirectional attention for language understanding",
        "GPT uses causal attention for text generation",
        "Transformers have largely replaced RNNs for NLP tasks",
        "Pre-training followed by fine-tuning is common in modern NLP",
    ]
    
    for fact in facts:
        pipeline.process(fact)
    
    # Add explicit relationships
    pipeline.add_fact(
        "ML is part of AI",
        relations=[("Machine Learning", RelationType.PART_OF, "Artificial Intelligence")]
    )
    
    pipeline.add_fact(
        "Deep Learning extends ML",
        relations=[("Deep Learning", RelationType.IS_A, "Machine Learning")]
    )
    
    pipeline.add_fact(
        "Transformers use attention",
        relations=[("Transformers", RelationType.USES, "attention")]
    )
    
    # Create concept hierarchy
    hierarchy = {
        "Artificial Intelligence": ["Machine Learning", "Expert Systems", "Robotics"],
        "Machine Learning": ["Supervised Learning", "Unsupervised Learning", "Deep Learning"],
        "Deep Learning": ["CNNs", "RNNs", "Transformers"],
        "Transformers": ["BERT", "GPT", "T5"],
    }
    
    pipeline.create_concept_tree("ai_concepts", "AI Concepts", hierarchy)
    
    print(f"Knowledge base built: {pipeline.get_stats()['memory']['total_objects']} facts")


class MockNumPyGPT:
    """
    Mock NumPy GPT for demonstration.
    
    Replace this with your actual SOMALanguageModel from:
    src.training.language_model_trainer
    """
    
    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """
        Generate text from prompt.
        
        In production, this would use your actual NumPy GPT:
        
            from src.training.language_model_trainer import somaLanguageModel
            
            model = SOMALanguageModel.load("model_path")
            return model.generate(prompt, max_tokens=max_tokens)
        """
        # For demo, return a simple response based on context
        if "attention" in prompt.lower():
            return (
                "Based on the provided context, attention mechanisms allow models "
                "to focus on relevant parts of the input. Self-attention computes "
                "relationships between all positions, enabling transformers to "
                "capture long-range dependencies effectively."
            )
        elif "transformer" in prompt.lower():
            return (
                "Transformers are a type of neural network architecture that have "
                "largely replaced RNNs for NLP tasks. They use attention mechanisms "
                "to process sequences in parallel. BERT uses bidirectional attention "
                "while GPT uses causal attention."
            )
        else:
            return (
                "Based on the knowledge base, this topic relates to machine learning "
                "and deep learning concepts. The system has relevant facts and "
                "inferences available for more specific queries."
            )


def demo_hybrid_qa(pipeline: CognitivePipeline, gpt: MockNumPyGPT):
    """Demonstrate hybrid question answering."""
    
    print("\n" + "="*60)
    print("HYBRID Q&A DEMO")
    print("="*60)
    
    questions = [
        "How does attention work in transformers?",
        "What is the relationship between BERT and GPT?",
        "Is deep learning a type of machine learning?",
    ]
    
    # Connect GPT to the hybrid reasoner
    pipeline.set_llm_generator(lambda prompt: gpt.generate(prompt))
    
    for question in questions:
        print(f"\n📝 Question: {question}")
        print("-" * 40)
        
        # Get answer using hybrid reasoning
        answer = pipeline.query(question)
        
        print(f"💬 Answer: {answer.answer}")
        print(f"📊 Confidence: {answer.confidence:.0%}")
        
        if answer.sources_used:
            print(f"📚 Sources: {len(answer.sources_used)}")
        
        if answer.rules_applied:
            print(f"🔧 Inference rules: {', '.join(answer.rules_applied)}")


def demo_context_generation(pipeline: CognitivePipeline):
    """Demonstrate structured context generation."""
    
    print("\n" + "="*60)
    print("CONTEXT GENERATION DEMO")
    print("="*60)
    
    # Build context without generating answer
    context = pipeline.get_context("What is deep learning?")
    
    # Format in different ways
    formatter = ContextFormatter()
    
    print("\n--- MARKDOWN FORMAT ---")
    from ..utils.formatting import OutputFormat
    print(formatter.format(context, OutputFormat.MARKDOWN)[:500] + "...")
    
    # Score the context
    from ..utils import ContextScorer
    scorer = ContextScorer()
    score = scorer.score(context)
    quality = scorer.assess_quality(context)
    
    print(f"\n📊 Context Quality: {quality} (score: {score.total:.2f})")


def demo_reasoning_trace(pipeline: CognitivePipeline):
    """Demonstrate reasoning trace and explanation."""
    
    print("\n" + "="*60)
    print("REASONING TRACE DEMO")
    print("="*60)
    
    # Process a query
    answer = pipeline.query("Is a transformer a type of neural network?")
    
    print(f"\n📝 Query: Is a transformer a type of neural network?")
    print(f"💬 Answer: {answer.answer}")
    
    print("\n--- REASONING TRACE ---")
    print(answer.explain())
    
    # Show structured context
    print("\n--- STRUCTURED CONTEXT FOR LLM ---")
    print(answer.context.to_prompt()[:800] + "...")


def demo_prompt_building(pipeline: CognitivePipeline):
    """Demonstrate different prompt types."""
    
    print("\n" + "="*60)
    print("PROMPT BUILDING DEMO")
    print("="*60)
    
    context = pipeline.get_context("attention mechanisms")
    builder = PromptBuilder()
    
    print("\n--- Q&A PROMPT ---")
    qa_prompt = builder.build_qa_prompt(context, "How does attention work?")
    print(qa_prompt[:400] + "...")
    
    print("\n--- EXPLANATION PROMPT ---")
    explain_prompt = builder.build_explain_prompt(context, "attention mechanisms")
    print(explain_prompt[:400] + "...")
    
    print("\n--- REASONING PROMPT ---")
    reason_prompt = builder.build_reason_prompt(context, "Why are transformers effective?")
    print(reason_prompt[:400] + "...")


def main():
    """Run the full integration demo."""
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║          SOMA Cognitive + NumPy GPT Integration             ║
║                                                               ║
║   Architecture:                                               ║
║   Query → Cognitive (thinking) → Context → GPT (speaking)     ║
║                                                               ║
║   The GPT becomes a SPEAKER, not a THINKER.                   ║
║   SOMA Cognitive does the reasoning!                        ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Create pipeline
    pipeline = CognitivePipeline()
    
    # Create mock GPT (replace with your actual NumPy GPT)
    gpt = MockNumPyGPT()
    
    # Build knowledge base
    create_knowledge_base(pipeline)
    
    # Run demos
    demo_hybrid_qa(pipeline, gpt)
    demo_context_generation(pipeline)
    demo_reasoning_trace(pipeline)
    demo_prompt_building(pipeline)
    
    print("\n" + "="*60)
    print("INTEGRATION COMPLETE!")
    print("="*60)
    print("""
To use with your actual NumPy GPT:

1. Import your model:
   from src.training.language_model_trainer import somaLanguageModel
   
2. Load or create model:
   model = SOMALanguageModel(vocab_size=60000, embed_dim=768, num_heads=12)
   
3. Set as generator:
   pipeline.set_llm_generator(lambda prompt: model.generate(prompt, max_tokens=200))

4. Query:
   answer = pipeline.query("Your question here")
   print(answer.answer)
   print(answer.explain())

Your NumPy GPT is now MUCH more powerful because:
- SOMA Cognitive provides structured context
- Symbolic reasoning derives new facts
- Contradictions are detected and flagged
- Explanations are grounded in evidence
    """)


if __name__ == "__main__":
    main()

