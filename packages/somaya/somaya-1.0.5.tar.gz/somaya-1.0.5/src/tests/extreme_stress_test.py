#!/usr/bin/env python3
"""
Extreme Stress Testing Framework for SOMA
Tests with massive datasets, concurrent processing, and extreme conditions
"""

import sys
import os
import time
import random
import string
import json
import csv
import statistics
import threading
import multiprocessing
from pathlib import Path
from typing import List, Dict, Any, Tuple
import psutil
import gc
import mmap
import tempfile
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import queue
import signal

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.core_tokenizer import (
    tokenize_space, tokenize_word, tokenize_char, tokenize_grammar,
    tokenize_subword, tokenize_bytes, reconstruct_from_tokens
)

class ExtremeStressTestFramework:
    """Extreme stress testing framework for SOMA under extreme conditions"""
    
    def __init__(self):
        self.results = {}
        self.performance_data = {}
        self.memory_usage = {}
        self.tokenizers = [
            'space', 'word', 'char', 'grammar', 'subword', 
            'bpe', 'syllable', 'frequency', 'byte'
        ]
        
        # Extreme test datasets
        self.extreme_datasets = {
            'gigantic': self._generate_gigantic_dataset(),
            'colossal': self._generate_colossal_dataset(),
            'massive': self._generate_massive_dataset(),
            'extreme': self._generate_extreme_dataset()
        }
        
        # Performance tracking
        self.start_time = None
        self.end_time = None
        self.test_stats = {
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'total_chars_processed': 0,
            'total_tokens_generated': 0,
            'peak_memory_usage': 0
        }
        
    def _generate_gigantic_dataset(self) -> List[str]:
        """Generate gigantic test dataset (100MB - 1GB)"""
        print("[INFO] Generating GIGANTIC dataset (100MB - 1GB)...")
        texts = []
        
        # Generate multiple very large documents
        for i in range(3):
            print(f"  Generating document {i + 1}/3...")
            # Generate a gigantic document (50MB - 300MB each)
            doc_size = random.randint(50000000, 300000000)
            document = self._generate_extreme_document(doc_size)
            texts.append(document)
            print(f"    Generated: {len(document):,} characters")
        
        return texts
    
    def _generate_colossal_dataset(self) -> List[str]:
        """Generate colossal test dataset (1GB - 10GB)"""
        print("[INFO] Generating COLOSSAL dataset (1GB - 10GB)...")
        texts = []
        
        # Generate extremely large documents
        for i in range(2):
            print(f"  Generating document {i + 1}/2...")
            # Generate a colossal document (500MB - 5GB each)
            doc_size = random.randint(500000000, 5000000000)
            document = self._generate_extreme_document(doc_size)
            texts.append(document)
            print(f"    Generated: {len(document):,} characters")
        
        return texts
    
    def _generate_massive_dataset(self) -> List[str]:
        """Generate massive test dataset (10GB - 100GB)"""
        print("[INFO] Generating MASSIVE dataset (10GB - 100GB)...")
        texts = []
        
        # Generate one extremely large document
        print("  Generating single massive document...")
        doc_size = random.randint(10000000000, 100000000000)  # 10GB - 100GB
        document = self._generate_extreme_document(doc_size)
        texts.append(document)
        print(f"    Generated: {len(document):,} characters")
        
        return texts
    
    def _generate_extreme_dataset(self) -> List[str]:
        """Generate extreme test dataset (100GB+)"""
        print("[INFO] Generating EXTREME dataset (100GB+)...")
        texts = []
        
        # Generate one extremely large document
        print("  Generating single extreme document...")
        doc_size = 200000000000  # 200GB
        document = self._generate_extreme_document(doc_size)
        texts.append(document)
        print(f"    Generated: {len(document):,} characters")
        
        return texts
    
    def _generate_extreme_document(self, target_size: int) -> str:
        """Generate an extreme document of approximately target size"""
        print(f"    Target size: {target_size:,} characters")
        
        # Use memory mapping for very large documents
        if target_size > 1000000000:  # 1GB
            return self._generate_memory_mapped_document(target_size)
        
        # Generate in chunks for large documents
        document_parts = []
        current_size = 0
        chunk_size = min(10000000, target_size // 100)  # 10MB chunks or 1% of target
        
        while current_size < target_size:
            # Generate a chunk
            chunk = self._generate_random_chunk(chunk_size)
            document_parts.append(chunk)
            current_size += len(chunk)
            
            # Progress indicator
            if current_size % (target_size // 10) == 0:
                progress = (current_size / target_size) * 100
                print(f"      Progress: {progress:.1f}% ({current_size:,}/{target_size:,})")
        
        return ''.join(document_parts)
    
    def _generate_memory_mapped_document(self, target_size: int) -> str:
        """Generate a memory-mapped document for extreme sizes"""
        print("    Using memory mapping for extreme size...")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
            temp_filename = temp_file.name
            
            # Generate content in chunks
            chunk_size = 10000000  # 10MB chunks
            current_size = 0
            
            while current_size < target_size:
                chunk = self._generate_random_chunk(chunk_size)
                temp_file.write(chunk)
                current_size += len(chunk)
                
                # Progress indicator
                if current_size % (target_size // 20) == 0:
                    progress = (current_size / target_size) * 100
                    print(f"      Progress: {progress:.1f}% ({current_size:,}/{target_size:,})")
            
            temp_file.flush()
        
        # Read the file back
        with open(temp_filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean up
        os.unlink(temp_filename)
        
        return content
    
    def _generate_random_chunk(self, chunk_size: int) -> str:
        """Generate a random chunk of text"""
        # Common words for realistic text
        words = [
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
        
        chunk_parts = []
        current_size = 0
        
        while current_size < chunk_size:
            # Generate a sentence
            sentence_length = random.randint(10, 50)
            sentence_words = [random.choice(words) for _ in range(sentence_length)]
            sentence = ' '.join(sentence_words)
            
            # Add punctuation
            if random.random() < 0.8:
                sentence += random.choice(['.', '!', '?'])
            
            # Add some special characters
            if random.random() < 0.1:
                sentence += random.choice([' @#$%^&*()', ' _+-=[]{}|', ' ;:,.<>?'])
            
            # Add some numbers
            if random.random() < 0.05:
                sentence += f' {random.randint(0, 999999)}'
            
            # Add some unicode
            if random.random() < 0.02:
                sentence += random.choice([' 你好世界', ' 🌍', ' مرحبا', ' привет'])
            
            chunk_parts.append(sentence)
            current_size += len(sentence) + 1  # +1 for space
        
        return ' '.join(chunk_parts)
    
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
    
    def test_single_text(self, text: str, tokenizer_type: str) -> Dict[str, Any]:
        """Test a single text with a tokenizer"""
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
            
            # Update stats
            self.test_stats['total_tests'] += 1
            if is_perfect:
                self.test_stats['successful_tests'] += 1
            else:
                self.test_stats['failed_tests'] += 1
            
            self.test_stats['total_chars_processed'] += len(text)
            self.test_stats['total_tokens_generated'] += len(tokens)
            self.test_stats['peak_memory_usage'] = max(self.test_stats['peak_memory_usage'], mem_after)
            
            return {
                'success': True,
                'is_perfect': is_perfect,
                'tokenize_time': tokenize_time,
                'reconstruct_time': reconstruct_time,
                'total_time': tokenize_time + reconstruct_time,
                'memory_used': mem_after - mem_before,
                'token_count': len(tokens),
                'char_count': len(text),
                'chars_per_second': len(text) / (tokenize_time + reconstruct_time) if (tokenize_time + reconstruct_time) > 0 else 0,
                'tokens_per_char': len(tokens) / len(text) if len(text) > 0 else 0
            }
            
        except Exception as e:
            self.test_stats['total_tests'] += 1
            self.test_stats['failed_tests'] += 1
            return {
                'success': False,
                'error': str(e),
                'is_perfect': False,
                'tokenize_time': 0,
                'reconstruct_time': 0,
                'total_time': 0,
                'memory_used': 0,
                'token_count': 0,
                'char_count': len(text),
                'chars_per_second': 0,
                'tokens_per_char': 0
            }
    
    def test_concurrent_processing(self, dataset_name: str, texts: List[str]) -> Dict[str, Any]:
        """Test concurrent processing with multiple threads/processes"""
        print(f"\n[INFO] Testing {dataset_name.upper()} concurrent processing...")
        print("=" * 60)
        
        results = {}
        total_chars = sum(len(text) for text in texts)
        
        print(f"[INFO] Dataset: {dataset_name}")
        print(f"[INFO] Texts: {len(texts)}")
        print(f"📏 Total characters: {total_chars:,}")
        print(f"💻 CPU cores: {multiprocessing.cpu_count()}")
        
        for tokenizer_type in self.tokenizers:
            print(f"\n[INFO] Testing {tokenizer_type.upper()} with concurrent processing...")
            
            # Test with different concurrency levels
            concurrency_levels = [1, 2, 4, 8, 16]
            tokenizer_results = {}
            
            for concurrency in concurrency_levels:
                if concurrency > multiprocessing.cpu_count():
                    continue
                
                print(f"  [INFO] Testing with {concurrency} workers...")
                
                # Prepare test data
                test_data = [(text, tokenizer_type) for text in texts]
                
                # Run concurrent tests
                start_time = time.time()
                
                if concurrency == 1:
                    # Single-threaded
                    results_list = []
                    for text, tokenizer in test_data:
                        result = self.test_single_text(text, tokenizer)
                        results_list.append(result)
                else:
                    # Multi-threaded
                    with ThreadPoolExecutor(max_workers=concurrency) as executor:
                        futures = [executor.submit(self.test_single_text, text, tokenizer) 
                                 for text, tokenizer in test_data]
                        results_list = [future.result() for future in futures]
                
                end_time = time.time()
                total_time = end_time - start_time
                
                # Calculate statistics
                successful_tests = sum(1 for r in results_list if r['success'])
                perfect_tests = sum(1 for r in results_list if r['success'] and r['is_perfect'])
                total_tokens = sum(r['token_count'] for r in results_list if r['success'])
                total_memory = sum(r['memory_used'] for r in results_list if r['success'])
                avg_chars_per_second = statistics.mean([r['chars_per_second'] for r in results_list if r['success'] and r['chars_per_second'] > 0])
                
                tokenizer_results[concurrency] = {
                    'total_time': total_time,
                    'successful_tests': successful_tests,
                    'perfect_tests': perfect_tests,
                    'total_tokens': total_tokens,
                    'total_memory': total_memory,
                    'avg_chars_per_second': avg_chars_per_second,
                    'efficiency': successful_tests / len(test_data) if test_data else 0
                }
                
                print(f"    [OK] {concurrency} workers: {avg_chars_per_second:,.0f} chars/sec")
                print(f"       Success: {successful_tests}/{len(test_data)}")
                print(f"       Perfect: {perfect_tests}/{len(test_data)}")
                print(f"       Time: {total_time:.2f}s")
            
            results[tokenizer_type] = tokenizer_results
        
        return results
    
    def test_memory_stress(self, dataset_name: str, texts: List[str]) -> Dict[str, Any]:
        """Test memory stress with large datasets"""
        print(f"\n🧠 Testing {dataset_name.upper()} memory stress...")
        print("=" * 60)
        
        results = {}
        
        for tokenizer_type in self.tokenizers:
            print(f"\n[INFO] Memory stress test: {tokenizer_type.upper()}...")
            
            # Force garbage collection
            gc.collect()
            initial_memory = self._get_memory_usage()
            
            max_memory = initial_memory
            total_tokens = 0
            successful_tests = 0
            
            for i, text in enumerate(texts):
                try:
                    # Test tokenization
                    result = self.test_single_text(text, tokenizer_type)
                    
                    if result['success']:
                        successful_tests += 1
                        total_tokens += result['token_count']
                    
                    # Track memory usage
                    current_memory = self._get_memory_usage()
                    max_memory = max(max_memory, current_memory)
                    
                    # Progress indicator
                    if (i + 1) % max(1, len(texts) // 10) == 0:
                        progress = ((i + 1) / len(texts)) * 100
                        print(f"  Progress: {progress:.1f}% - Memory: {current_memory:.1f} MB")
                    
                    # Force garbage collection periodically
                    if (i + 1) % 100 == 0:
                        gc.collect()
                
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
                'total_tokens': total_tokens,
                'successful_tests': successful_tests,
                'efficiency': successful_tests / len(texts) if texts else 0
            }
            
            print(f"  [OK] {tokenizer_type.upper()}:")
            print(f"     Memory used: {memory_used:.2f} MB")
            print(f"     Memory per char: {memory_per_char:.6f} MB")
            print(f"     Total tokens: {total_tokens:,}")
            print(f"     Success rate: {successful_tests}/{len(texts)}")
        
        return results
    
    def run_extreme_stress_tests(self):
        """Run all extreme stress tests"""
        print("[START] Starting Extreme Stress Testing for SOMA")
        print("=" * 80)
        print(f"🕐 Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💻 System: {psutil.cpu_count()} CPU cores, {psutil.virtual_memory().total // (1024**3)} GB RAM")
        print(f"🧠 Available memory: {psutil.virtual_memory().available // (1024**3)} GB")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # Test each extreme dataset
        for dataset_name, texts in self.extreme_datasets.items():
            print(f"\n[INFO] Testing {dataset_name.upper()} dataset...")
            print(f"   Texts: {len(texts)}")
            print(f"   Total size: {sum(len(text) for text in texts):,} characters")
            print(f"   Average text size: {sum(len(text) for text in texts) // len(texts):,} characters")
            
            # Run tests
            concurrent_results = self.test_concurrent_processing(dataset_name, texts)
            memory_results = self.test_memory_stress(dataset_name, texts)
            
            # Store results
            self.results[dataset_name] = {
                'concurrent': concurrent_results,
                'memory': memory_results
            }
            
            # Clear memory between tests
            gc.collect()
        
        self.end_time = time.time()
        total_time = self.end_time - self.start_time
        
        print(f"\n🎉 All extreme stress tests completed!")
        print(f"[INFO]  Total time: {total_time:.2f} seconds")
        print(f"[INFO] Total tests: {self.test_stats['total_tests']}")
        print(f"[OK] Successful: {self.test_stats['successful_tests']}")
        print(f"[ERROR] Failed: {self.test_stats['failed_tests']}")
        print(f"📏 Total chars processed: {self.test_stats['total_chars_processed']:,}")
        print(f"🔢 Total tokens generated: {self.test_stats['total_tokens_generated']:,}")
        print(f"🧠 Peak memory usage: {self.test_stats['peak_memory_usage']:.2f} MB")
        
        # Generate summary report
        self.generate_extreme_summary_report()
    
    def generate_extreme_summary_report(self):
        """Generate an extreme summary report"""
        print("\n📋 Generating Extreme Summary Report...")
        print("=" * 60)
        
        # Overall performance summary
        print("\n⚡ EXTREME PERFORMANCE SUMMARY:")
        print("-" * 40)
        
        for dataset_name, dataset_results in self.results.items():
            print(f"\n{dataset_name.upper()} Dataset:")
            concurrent_data = dataset_results['concurrent']
            
            for tokenizer, concurrency_data in concurrent_data.items():
                print(f"  {tokenizer.upper()}:")
                for concurrency, data in concurrency_data.items():
                    speed = data['avg_chars_per_second']
                    efficiency = data['efficiency']
                    print(f"    {concurrency:2d} workers: {speed:>12,.0f} chars/sec (eff: {efficiency:.2f})")
        
        # Memory efficiency summary
        print("\n🧠 EXTREME MEMORY EFFICIENCY SUMMARY:")
        print("-" * 40)
        
        for dataset_name, dataset_results in self.results.items():
            print(f"\n{dataset_name.upper()} Dataset:")
            memory_data = dataset_results['memory']
            
            for tokenizer, data in memory_data.items():
                memory_per_char = data['memory_per_char']
                efficiency = data['efficiency']
                print(f"  {tokenizer:12} {memory_per_char:>12.6f} MB/char (eff: {efficiency:.2f})")
        
        # Save detailed results
        self.save_extreme_results_to_file()
    
    def save_extreme_results_to_file(self):
        """Save extreme results to JSON file"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"extreme_stress_test_results_{timestamp}.json"
        
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
            'test_stats': self.test_stats,
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
                for name, texts in self.extreme_datasets.items()
            }
        }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"\n[INFO] Extreme results saved to: {filename}")

def main():
    """Main function to run extreme stress tests"""
    print("[START] SOMA Extreme Stress Testing Framework")
    print("=" * 80)
    print("[WARNING] WARNING: This will test with MASSIVE datasets!")
    print("[WARNING] Make sure you have sufficient memory and disk space!")
    print("=" * 80)
    
    # Check system resources
    available_memory = psutil.virtual_memory().available // (1024**3)
    if available_memory < 8:
        print("[ERROR] WARNING: Less than 8GB available memory!")
        print("   This may cause system instability!")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Create test framework
    framework = ExtremeStressTestFramework()
    
    # Run extreme stress tests
    framework.run_extreme_stress_tests()
    
    print("\n🎉 Extreme stress testing completed successfully!")
    print("[INFO] Check the generated JSON file for detailed results")

if __name__ == "__main__":
    main()
