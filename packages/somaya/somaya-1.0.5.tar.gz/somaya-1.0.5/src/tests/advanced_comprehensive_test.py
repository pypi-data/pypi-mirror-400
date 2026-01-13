#!/usr/bin/env python3
"""
Advanced Comprehensive Testing Framework for SOMA
Tests with massive datasets, performance analysis, and detailed reporting
"""

import sys
import os
import time
import random
import string
import json
import csv
import statistics
from pathlib import Path
from typing import List, Dict, Any, Tuple
import psutil
import gc

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.core_tokenizer import (
    tokenize_space, tokenize_word, tokenize_char, tokenize_grammar,
    tokenize_subword, tokenize_bytes, reconstruct_from_tokens
)

class AdvancedTestFramework:
    """Advanced testing framework for comprehensive SOMA evaluation"""
    
    def __init__(self):
        self.results = {}
        self.performance_data = {}
        self.memory_usage = {}
        self.tokenizers = [
            'space', 'word', 'char', 'grammar', 'subword', 
            'bpe', 'syllable', 'frequency', 'byte'
        ]
        
        # Test datasets
        self.test_datasets = {
            'small': self._generate_small_dataset(),
            'medium': self._generate_medium_dataset(),
            'large': self._generate_large_dataset(),
            'huge': self._generate_huge_dataset(),
            'massive': self._generate_massive_dataset(),
            'extreme': self._generate_extreme_dataset()
        }
        
        # Performance tracking
        self.start_time = None
        self.end_time = None
        
    def _generate_small_dataset(self) -> List[str]:
        """Generate small test dataset (1KB - 10KB)"""
        texts = [
            'Hello, world!',
            'This is a test sentence with various characters.',
            'Special chars: @#$%^&*()_+-=[]{}|;:,.<>?',
            'Numbers: 12345.67890 and 9876543210',
            'Unicode: 你好世界 🌍 مرحبا بالعالم',
            'Mixed: Hello 123 @#$ 世界 🌍',
            'Empty spaces:   multiple    spaces   here   ',
            'Newlines:\nThis has\nmultiple\nlines',
            'Tabs:\tThis\tuses\ttabs\tfor\tseparation',
            'Very long word: supercalifragilisticexpialidocious'
        ]
        return texts
    
    def _generate_medium_dataset(self) -> List[str]:
        """Generate medium test dataset (10KB - 100KB)"""
        texts = []
        
        # Generate random paragraphs
        for _ in range(50):
            paragraph = self._generate_random_paragraph(200, 500)
            texts.append(paragraph)
        
        # Add some structured text
        texts.extend([
            self._generate_code_snippet(),
            self._generate_json_data(),
            self._generate_xml_data(),
            self._generate_csv_data()
        ])
        
        return texts
    
    def _generate_large_dataset(self) -> List[str]:
        """Generate large test dataset (100KB - 1MB)"""
        texts = []
        
        # Generate multiple large documents
        for _ in range(20):
            # Generate a large document (5KB - 50KB each)
            doc_size = random.randint(5000, 50000)
            document = self._generate_random_document(doc_size)
            texts.append(document)
        
        return texts
    
    def _generate_huge_dataset(self) -> List[str]:
        """Generate huge test dataset (1MB - 10MB)"""
        texts = []
        
        # Generate very large documents
        for _ in range(10):
            # Generate a huge document (100KB - 1MB each)
            doc_size = random.randint(100000, 1000000)
            document = self._generate_random_document(doc_size)
            texts.append(document)
        
        return texts
    
    def _generate_massive_dataset(self) -> List[str]:
        """Generate massive test dataset (10MB - 100MB)"""
        texts = []
        
        # Generate extremely large documents
        for _ in range(5):
            # Generate a massive document (2MB - 20MB each)
            doc_size = random.randint(2000000, 20000000)
            document = self._generate_random_document(doc_size)
            texts.append(document)
        
        return texts
    
    def _generate_extreme_dataset(self) -> List[str]:
        """Generate extreme test dataset (100MB+)"""
        texts = []
        
        # Generate one extremely large document
        # This will be processed in chunks to avoid memory issues
        doc_size = 100000000  # 100MB
        document = self._generate_random_document(doc_size)
        texts.append(document)
        
        return texts
    
    def _generate_random_paragraph(self, min_words: int, max_words: int) -> str:
        """Generate a random paragraph with specified word count"""
        word_count = random.randint(min_words, max_words)
        words = []
        
        # Common English words for more realistic text
        common_words = [
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'she', 'or', 'an',
            'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
            'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
            'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him',
            'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some',
            'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look',
            'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after',
            'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even',
            'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most',
            'us', 'is', 'was', 'are', 'been', 'has', 'had', 'were', 'said',
            'each', 'which', 'their', 'said', 'if', 'will', 'up', 'other',
            'about', 'out', 'many', 'then', 'them', 'can', 'only', 'other',
            'new', 'some', 'what', 'time', 'very', 'when', 'much', 'then',
            'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water',
            'been', 'call', 'who', 'oil', 'its', 'now', 'find', 'long', 'down',
            'day', 'did', 'get', 'come', 'made', 'may', 'part'
        ]
        
        for _ in range(word_count):
            word = random.choice(common_words)
            # Add some variation
            if random.random() < 0.1:  # 10% chance of punctuation
                word += random.choice(['.', ',', '!', '?', ';', ':'])
            if random.random() < 0.05:  # 5% chance of numbers
                word += str(random.randint(0, 999))
            words.append(word)
        
        # Join with spaces and add some structure
        paragraph = ' '.join(words)
        
        # Add some random punctuation and formatting
        if random.random() < 0.3:
            paragraph = paragraph.capitalize()
        if random.random() < 0.2:
            paragraph += '.'
        
        return paragraph
    
    def _generate_random_document(self, target_size: int) -> str:
        """Generate a random document of approximately target size"""
        document_parts = []
        current_size = 0
        
        while current_size < target_size:
            # Generate a paragraph
            paragraph = self._generate_random_paragraph(50, 200)
            document_parts.append(paragraph)
            current_size += len(paragraph)
            
            # Add some structure
            if random.random() < 0.1:  # 10% chance of section break
                document_parts.append('\n\n---\n\n')
                current_size += 6
        
        return '\n\n'.join(document_parts)
    
    def _generate_code_snippet(self) -> str:
        """Generate a code snippet for testing"""
        return '''
def fibonacci(n):
    """Calculate the nth Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"fibonacci({i}) = {fibonacci(i)}")

# This is a comment with special characters: @#$%^&*()
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
result = sum(x**2 for x in numbers if x % 2 == 0)
print(f"Sum of squares of even numbers: {result}")
'''
    
    def _generate_json_data(self) -> str:
        """Generate JSON data for testing"""
        data = {
            "users": [
                {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25},
                {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "age": 35}
            ],
            "settings": {
                "theme": "dark",
                "language": "en",
                "notifications": True,
                "special_chars": "@#$%^&*()_+-=[]{}|;:,.<>?"
            },
            "unicode_text": "Hello 世界 🌍 مرحبا بالعالم",
            "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "nested": {
                "level1": {
                    "level2": {
                        "level3": "deep nesting test"
                    }
                }
            }
        }
        return json.dumps(data, indent=2)
    
    def _generate_xml_data(self) -> str:
        """Generate XML data for testing"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<root>
    <users>
        <user id="1">
            <name>John Doe</name>
            <email>john@example.com</email>
            <age>30</age>
        </user>
        <user id="2">
            <name>Jane Smith</name>
            <email>jane@example.com</email>
            <age>25</age>
        </user>
    </users>
    <settings>
        <theme>dark</theme>
        <language>en</language>
        <notifications>true</notifications>
        <special_chars>@#$%^&amp;*()_+-=[]{}|;:,.&lt;&gt;?</special_chars>
    </settings>
    <unicode_text>Hello 世界 🌍 مرحبا بالعالم</unicode_text>
</root>'''
    
    def _generate_csv_data(self) -> str:
        """Generate CSV data for testing"""
        return '''Name,Age,Email,City,Special_Chars
John Doe,30,john@example.com,New York,"@#$%^&*()"
Jane Smith,25,jane@example.com,Los Angeles,"_+-=[]{}|"
Bob Johnson,35,bob@example.com,Chicago,";:,.<>?"
Alice Brown,28,alice@example.com,Houston,"Hello 世界 🌍"
Charlie Wilson,42,charlie@example.com,Phoenix,"مرحبا بالعالم"'''
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def _tokenize_text(self, text: str, tokenizer_type: str) -> List[Dict]:
        """Tokenize text using specified tokenizer"""
        if tokenizer_type == 'space':
            return tokenize_space(text)
        elif tokenizer_type == 'word':
            return tokenize_word(text)
        elif tokenizer_type == 'char':
            return tokenize_char(text)
        elif tokenizer_type == 'grammar':
            return tokenize_grammar(text)
        elif tokenizer_type == 'subword':
            return tokenize_subword(text, 3, 'fixed')
        elif tokenizer_type == 'bpe':
            return tokenize_subword(text, 3, 'bpe')
        elif tokenizer_type == 'syllable':
            return tokenize_subword(text, 3, 'syllable')
        elif tokenizer_type == 'frequency':
            return tokenize_subword(text, 3, 'frequency')
        elif tokenizer_type == 'byte':
            return tokenize_bytes(text)
        else:
            raise ValueError(f"Unknown tokenizer type: {tokenizer_type}")
    
    def test_reconstruction_accuracy(self, dataset_name: str, texts: List[str]) -> Dict[str, Any]:
        """Test reconstruction accuracy for a dataset"""
        print(f"\n[INFO] Testing {dataset_name.upper()} dataset reconstruction accuracy...")
        print("=" * 60)
        
        results = {}
        total_texts = len(texts)
        total_chars = sum(len(text) for text in texts)
        
        print(f"[INFO] Dataset: {dataset_name}")
        print(f"[INFO] Texts: {total_texts}")
        print(f"📏 Total characters: {total_chars:,}")
        print(f"📏 Average text length: {total_chars // total_texts:,} chars")
        
        for tokenizer_type in self.tokenizers:
            print(f"\n[INFO] Testing {tokenizer_type.upper()} tokenization...")
            
            perfect_count = 0
            total_tokens = 0
            processing_times = []
            memory_usage = []
            
            for i, text in enumerate(texts):
                try:
                    # Memory before
                    mem_before = self._get_memory_usage()
                    
                    # Time the tokenization
                    start_time = time.time()
                    tokens = self._tokenize_text(text, tokenizer_type)
                    tokenize_time = time.time() - start_time
                    
                    # Time the reconstruction
                    start_time = time.time()
                    reconstructed = reconstruct_from_tokens(tokens, tokenizer_type)
                    reconstruct_time = time.time() - start_time
                    
                    # Memory after
                    mem_after = self._get_memory_usage()
                    
                    # Check accuracy
                    is_perfect = (text == reconstructed)
                    if is_perfect:
                        perfect_count += 1
                    
                    # Collect metrics
                    total_tokens += len(tokens)
                    processing_times.append(tokenize_time + reconstruct_time)
                    memory_usage.append(mem_after - mem_before)
                    
                    # Progress indicator
                    if (i + 1) % max(1, total_texts // 10) == 0:
                        progress = ((i + 1) / total_texts) * 100
                        print(f"  Progress: {progress:.1f}% ({i + 1}/{total_texts})")
                    
                    # Show errors for first few texts
                    if not is_perfect and i < 3:
                        print(f"  [ERROR] Error in text {i + 1}:")
                        print(f"    Original: {repr(text[:100])}...")
                        print(f"    Reconstructed: {repr(reconstructed[:100])}...")
                        print(f"    Length diff: {len(text)} vs {len(reconstructed)}")
                
                except Exception as e:
                    print(f"  [ERROR] ERROR in {tokenizer_type} for text {i + 1}: {e}")
                    continue
            
            # Calculate statistics
            accuracy = (perfect_count / total_texts) * 100
            avg_processing_time = statistics.mean(processing_times) if processing_times else 0
            avg_memory_usage = statistics.mean(memory_usage) if memory_usage else 0
            chars_per_second = total_chars / sum(processing_times) if processing_times else 0
            
            results[tokenizer_type] = {
                'accuracy': accuracy,
                'perfect_count': perfect_count,
                'total_texts': total_texts,
                'total_tokens': total_tokens,
                'total_chars': total_chars,
                'avg_processing_time': avg_processing_time,
                'avg_memory_usage': avg_memory_usage,
                'chars_per_second': chars_per_second,
                'tokens_per_char': total_tokens / total_chars if total_chars > 0 else 0
            }
            
            print(f"  [OK] {tokenizer_type.upper()}: {accuracy:.1f}% accuracy")
            print(f"     Perfect: {perfect_count}/{total_texts}")
            print(f"     Speed: {chars_per_second:,.0f} chars/sec")
            print(f"     Tokens: {total_tokens:,} ({total_tokens/total_chars:.2f} per char)")
            print(f"     Memory: {avg_memory_usage:.2f} MB avg")
        
        return results
    
    def test_performance_benchmark(self, dataset_name: str, texts: List[str]) -> Dict[str, Any]:
        """Run performance benchmark tests"""
        print(f"\n⚡ Running {dataset_name.upper()} performance benchmark...")
        print("=" * 60)
        
        results = {}
        total_chars = sum(len(text) for text in texts)
        
        for tokenizer_type in self.tokenizers:
            print(f"\n🏃 Benchmarking {tokenizer_type.upper()}...")
            
            # Warm up
            if texts:
                try:
                    self._tokenize_text(texts[0], tokenizer_type)
                except Exception:
                    pass
            
            # Benchmark
            times = []
            memory_usage = []
            
            for text in texts:
                try:
                    mem_before = self._get_memory_usage()
                    start_time = time.time()
                    
                    tokens = self._tokenize_text(text, tokenizer_type)
                    reconstructed = reconstruct_from_tokens(tokens, tokenizer_type)
                    
                    end_time = time.time()
                    mem_after = self._get_memory_usage()
                    
                    times.append(end_time - start_time)
                    memory_usage.append(mem_after - mem_before)
                    
                except Exception as e:
                    print(f"  [ERROR] Error: {e}")
                    continue
            
            if times:
                total_time = sum(times)
                chars_per_second = total_chars / total_time
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                avg_memory = statistics.mean(memory_usage)
                
                results[tokenizer_type] = {
                    'total_time': total_time,
                    'avg_time': avg_time,
                    'min_time': min_time,
                    'max_time': max_time,
                    'chars_per_second': chars_per_second,
                    'avg_memory_usage': avg_memory,
                    'total_chars': total_chars
                }
                
                print(f"  [OK] {tokenizer_type.upper()}:")
                print(f"     Speed: {chars_per_second:,.0f} chars/sec")
                print(f"     Total time: {total_time:.3f}s")
                print(f"     Avg time: {avg_time:.3f}s")
                print(f"     Memory: {avg_memory:.2f} MB avg")
            else:
                print(f"  [ERROR] {tokenizer_type.upper()}: No successful runs")
        
        return results
    
    def test_memory_efficiency(self, dataset_name: str, texts: List[str]) -> Dict[str, Any]:
        """Test memory efficiency with large datasets"""
        print(f"\n🧠 Testing {dataset_name.upper()} memory efficiency...")
        print("=" * 60)
        
        results = {}
        
        for tokenizer_type in self.tokenizers:
            print(f"\n[INFO] Memory test: {tokenizer_type.upper()}...")
            
            # Force garbage collection
            gc.collect()
            initial_memory = self._get_memory_usage()
            
            max_memory = initial_memory
            total_tokens = 0
            
            for i, text in enumerate(texts):
                try:
                    tokens = self._tokenize_text(text, tokenizer_type)
                    reconstructed = reconstruct_from_tokens(tokens, tokenizer_type)
                    
                    total_tokens += len(tokens)
                    current_memory = self._get_memory_usage()
                    max_memory = max(max_memory, current_memory)
                    
                    # Progress indicator
                    if (i + 1) % max(1, len(texts) // 10) == 0:
                        progress = ((i + 1) / len(texts)) * 100
                        print(f"  Progress: {progress:.1f}% - Memory: {current_memory:.1f} MB")
                
                except Exception as e:
                    print(f"  [ERROR] Error: {e}")
                    continue
            
            # Final memory check
            gc.collect()
            final_memory = self._get_memory_usage()
            
            memory_used = max_memory - initial_memory
            memory_per_char = memory_used / sum(len(text) for text in texts) if texts else 0
            
            results[tokenizer_type] = {
                'initial_memory': initial_memory,
                'max_memory': max_memory,
                'final_memory': final_memory,
                'memory_used': memory_used,
                'memory_per_char': memory_per_char,
                'total_tokens': total_tokens
            }
            
            print(f"  [OK] {tokenizer_type.upper()}:")
            print(f"     Memory used: {memory_used:.2f} MB")
            print(f"     Memory per char: {memory_per_char:.6f} MB")
            print(f"     Total tokens: {total_tokens:,}")
        
        return results
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("[START] Starting Advanced Comprehensive SOMA Testing")
        print("=" * 80)
        print(f"[INFO] Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[INFO] System: {psutil.cpu_count()} CPU cores, {psutil.virtual_memory().total // (1024**3)} GB RAM")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # Test each dataset
        for dataset_name, texts in self.test_datasets.items():
            print(f"\n[INFO] Testing {dataset_name.upper()} dataset...")
            print(f"   Texts: {len(texts)}")
            print(f"   Total size: {sum(len(text) for text in texts):,} characters")
            
            # Run tests
            accuracy_results = self.test_reconstruction_accuracy(dataset_name, texts)
            performance_results = self.test_performance_benchmark(dataset_name, texts)
            memory_results = self.test_memory_efficiency(dataset_name, texts)
            
            # Store results
            self.results[dataset_name] = {
                'accuracy': accuracy_results,
                'performance': performance_results,
                'memory': memory_results
            }
            
            # Clear memory between tests
            gc.collect()
        
        self.end_time = time.time()
        total_time = self.end_time - self.start_time
        
        print(f"\n[SUCCESS] All tests completed!")
        print(f"[INFO]  Total time: {total_time:.2f} seconds")
        print(f"[INFO] Results saved for analysis")
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print("\n📋 Generating Summary Report...")
        print("=" * 60)
        
        # Overall accuracy summary
        print("\n[INFO] RECONSTRUCTION ACCURACY SUMMARY:")
        print("-" * 40)
        
        for dataset_name, dataset_results in self.results.items():
            print(f"\n{dataset_name.upper()} Dataset:")
            accuracy_data = dataset_results['accuracy']
            
            for tokenizer, data in accuracy_data.items():
                accuracy = data['accuracy']
                status = "[OK] PERFECT" if accuracy == 100.0 else f"[WARNING]  {accuracy:.1f}%"
                print(f"  {tokenizer:12} {status:15} ({data['perfect_count']}/{data['total_texts']})")
        
        # Performance summary
        print("\n⚡ PERFORMANCE SUMMARY:")
        print("-" * 40)
        
        for dataset_name, dataset_results in self.results.items():
            print(f"\n{dataset_name.upper()} Dataset:")
            performance_data = dataset_results['performance']
            
            for tokenizer, data in performance_data.items():
                speed = data['chars_per_second']
                print(f"  {tokenizer:12} {speed:>12,.0f} chars/sec")
        
        # Memory efficiency summary
        print("\n🧠 MEMORY EFFICIENCY SUMMARY:")
        print("-" * 40)
        
        for dataset_name, dataset_results in self.results.items():
            print(f"\n{dataset_name.upper()} Dataset:")
            memory_data = dataset_results['memory']
            
            for tokenizer, data in memory_data.items():
                memory_per_char = data['memory_per_char']
                print(f"  {tokenizer:12} {memory_per_char:>12.6f} MB/char")
        
        # Save detailed results
        self.save_results_to_file()
    
    def save_results_to_file(self):
        """Save detailed results to JSON file"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"comprehensive_test_results_{timestamp}.json"
        
        # Prepare results for JSON serialization
        json_results = {}
        for dataset_name, dataset_results in self.results.items():
            json_results[dataset_name] = {}
            for test_type, test_results in dataset_results.items():
                json_results[dataset_name][test_type] = {}
                for tokenizer, data in test_results.items():
                    json_results[dataset_name][test_type][tokenizer] = data
        
        # Add metadata
        json_results['metadata'] = {
            'test_timestamp': timestamp,
            'total_test_time': self.end_time - self.start_time,
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'total_memory_gb': psutil.virtual_memory().total // (1024**3),
                'available_memory_gb': psutil.virtual_memory().available // (1024**3)
            },
            'test_datasets': {
                name: {
                    'text_count': len(texts),
                    'total_chars': sum(len(text) for text in texts)
                }
                for name, texts in self.test_datasets.items()
            }
        }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"\n[INFO] Detailed results saved to: {filename}")

def main():
    """Main function to run comprehensive tests"""
    print("[START] SOMA Advanced Comprehensive Testing Framework")
    print("=" * 80)
    
    # Create test framework
    framework = AdvancedTestFramework()
    
    # Run comprehensive tests
    framework.run_comprehensive_tests()
    
    print("\n[SUCCESS] Testing completed successfully!")
    print("[INFO] Check the generated JSON file for detailed results")

if __name__ == "__main__":
    main()
