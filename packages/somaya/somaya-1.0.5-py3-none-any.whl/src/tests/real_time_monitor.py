#!/usr/bin/env python3
"""
Real-time Monitoring and Visualization Framework for SOMA Testing
Provides live monitoring, progress tracking, and performance visualization
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
import queue
import signal
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False
    # Windows doesn't have curses - provide fallback
    print("[WARNING] curses not available on Windows. Real-time monitoring disabled.")
    print("[INFO] Install windows-curses for Windows support: pip install windows-curses")
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.core_tokenizer import (
    tokenize_space, tokenize_word, tokenize_char, tokenize_grammar,
    tokenize_subword, tokenize_bytes, reconstruct_from_tokens
)

class RealTimeMonitor:
    """Real-time monitoring and visualization for SOMA testing"""
    
    def __init__(self):
        self.monitoring = False
        self.stats_queue = queue.Queue()
        self.performance_data = {
            'timestamps': deque(maxlen=1000),
            'memory_usage': deque(maxlen=1000),
            'cpu_usage': deque(maxlen=1000),
            'chars_per_second': deque(maxlen=1000),
            'tokens_per_second': deque(maxlen=1000),
            'accuracy': deque(maxlen=1000)
        }
        self.current_test = None
        self.test_stats = {
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'total_chars_processed': 0,
            'total_tokens_generated': 0,
            'start_time': None,
            'current_speed': 0,
            'peak_speed': 0,
            'avg_speed': 0
        }
        self.tokenizers = [
            'space', 'word', 'char', 'grammar', 'subword', 
            'bpe', 'syllable', 'frequency', 'byte'
        ]
        
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.monitoring = True
        self.test_stats['start_time'] = time.time()
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_system)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("🚀 Real-time monitoring started!")
        print("📊 Press Ctrl+C to stop monitoring")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring = False
        print("\n🛑 Real-time monitoring stopped!")
    
    def _monitor_system(self):
        """Monitor system resources in real-time"""
        while self.monitoring:
            try:
                # Get system metrics
                timestamp = time.time()
                memory_usage = psutil.virtual_memory().percent
                cpu_usage = psutil.cpu_percent()
                
                # Update performance data
                self.performance_data['timestamps'].append(timestamp)
                self.performance_data['memory_usage'].append(memory_usage)
                self.performance_data['cpu_usage'].append(cpu_usage)
                
                # Calculate current speed
                if self.test_stats['start_time']:
                    elapsed_time = timestamp - self.test_stats['start_time']
                    if elapsed_time > 0:
                        current_speed = self.test_stats['total_chars_processed'] / elapsed_time
                        self.test_stats['current_speed'] = current_speed
                        self.test_stats['peak_speed'] = max(self.test_stats['peak_speed'], current_speed)
                        
                        # Update performance data
                        self.performance_data['chars_per_second'].append(current_speed)
                        
                        # Calculate tokens per second
                        if self.test_stats['total_tokens_generated'] > 0:
                            tokens_per_second = self.test_stats['total_tokens_generated'] / elapsed_time
                            self.performance_data['tokens_per_second'].append(tokens_per_second)
                
                # Calculate accuracy
                if self.test_stats['total_tests'] > 0:
                    accuracy = (self.test_stats['successful_tests'] / self.test_stats['total_tests']) * 100
                    self.performance_data['accuracy'].append(accuracy)
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                break
    
    def update_test_stats(self, test_result: Dict[str, Any]):
        """Update test statistics"""
        self.test_stats['total_tests'] += 1
        
        if test_result.get('success', False):
            self.test_stats['successful_tests'] += 1
        else:
            self.test_stats['failed_tests'] += 1
        
        self.test_stats['total_chars_processed'] += test_result.get('char_count', 0)
        self.test_stats['total_tokens_generated'] += test_result.get('token_count', 0)
        
        # Update average speed
        if self.test_stats['start_time']:
            elapsed_time = time.time() - self.test_stats['start_time']
            if elapsed_time > 0:
                self.test_stats['avg_speed'] = self.test_stats['total_chars_processed'] / elapsed_time
    
    def display_dashboard(self):
        """Display real-time dashboard"""
        try:
            # Clear screen
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("🚀 SOMA Real-time Testing Dashboard")
            print("=" * 80)
            print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏱️  Elapsed: {self._format_time(time.time() - self.test_stats['start_time']) if self.test_stats['start_time'] else '0s'}")
            print("=" * 80)
            
            # Test statistics
            print("\n📊 TEST STATISTICS:")
            print(f"  Total Tests: {self.test_stats['total_tests']:,}")
            print(f"  Successful:  {self.test_stats['successful_tests']:,}")
            print(f"  Failed:      {self.test_stats['failed_tests']:,}")
            print(f"  Success Rate: {(self.test_stats['successful_tests'] / max(1, self.test_stats['total_tests'])) * 100:.1f}%")
            
            # Performance metrics
            print("\n⚡ PERFORMANCE METRICS:")
            print(f"  Current Speed: {self.test_stats['current_speed']:,.0f} chars/sec")
            print(f"  Peak Speed:    {self.test_stats['peak_speed']:,.0f} chars/sec")
            print(f"  Avg Speed:     {self.test_stats['avg_speed']:,.0f} chars/sec")
            print(f"  Chars Processed: {self.test_stats['total_chars_processed']:,}")
            print(f"  Tokens Generated: {self.test_stats['total_tokens_generated']:,}")
            
            # System resources
            print("\n💻 SYSTEM RESOURCES:")
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent()
            print(f"  CPU Usage: {cpu:.1f}%")
            print(f"  Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3)} GB / {memory.total // (1024**3)} GB)")
            print(f"  Available Memory: {memory.available // (1024**3)} GB")
            
            # Current test info
            if self.current_test:
                print(f"\n🧪 CURRENT TEST: {self.current_test}")
            
            # Performance graph (simplified)
            if len(self.performance_data['chars_per_second']) > 1:
                print("\n📈 PERFORMANCE TREND:")
                recent_speeds = list(self.performance_data['chars_per_second'])[-10:]
                if recent_speeds:
                    avg_recent = statistics.mean(recent_speeds)
                    print(f"  Recent Avg Speed: {avg_recent:,.0f} chars/sec")
                    
                    # Simple trend indicator
                    if len(recent_speeds) >= 2:
                        trend = recent_speeds[-1] - recent_speeds[0]
                        if trend > 0:
                            print("  Trend: 📈 Improving")
                        elif trend < 0:
                            print("  Trend: 📉 Declining")
                        else:
                            print("  Trend: ➡️ Stable")
            
            print("\n" + "=" * 80)
            print("Press Ctrl+C to stop monitoring")
            
        except Exception as e:
            print(f"❌ Dashboard error: {e}")
    
    def _format_time(self, seconds: float) -> str:
        """Format time in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds // 60:.0f}m {seconds % 60:.1f}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours:.0f}h {minutes:.0f}m"
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'test_summary': self.test_stats.copy(),
            'performance_metrics': {
                'avg_memory_usage': statistics.mean(self.performance_data['memory_usage']) if self.performance_data['memory_usage'] else 0,
                'avg_cpu_usage': statistics.mean(self.performance_data['cpu_usage']) if self.performance_data['cpu_usage'] else 0,
                'peak_memory_usage': max(self.performance_data['memory_usage']) if self.performance_data['memory_usage'] else 0,
                'peak_cpu_usage': max(self.performance_data['cpu_usage']) if self.performance_data['cpu_usage'] else 0,
                'avg_chars_per_second': statistics.mean(self.performance_data['chars_per_second']) if self.performance_data['chars_per_second'] else 0,
                'peak_chars_per_second': max(self.performance_data['chars_per_second']) if self.performance_data['chars_per_second'] else 0,
                'avg_tokens_per_second': statistics.mean(self.performance_data['tokens_per_second']) if self.performance_data['tokens_per_second'] else 0,
                'peak_tokens_per_second': max(self.performance_data['tokens_per_second']) if self.performance_data['tokens_per_second'] else 0,
                'avg_accuracy': statistics.mean(self.performance_data['accuracy']) if self.performance_data['accuracy'] else 0
            },
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'total_memory_gb': psutil.virtual_memory().total // (1024**3),
                'available_memory_gb': psutil.virtual_memory().available // (1024**3)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return report
    
    def save_performance_report(self, filename: str = None):
        """Save performance report to file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"performance_report_{timestamp}.json"
        
        report = self.generate_performance_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Performance report saved to: {filename}")
        return filename

class AdvancedTestRunner:
    """Advanced test runner with real-time monitoring"""
    
    def __init__(self):
        self.monitor = RealTimeMonitor()
        self.tokenizers = [
            'space', 'word', 'char', 'grammar', 'subword', 
            'bpe', 'syllable', 'frequency', 'byte'
        ]
    
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
            # Time the tokenization
            start_time = time.time()
            tokens = self._tokenize_text(text, tokenizer_type)
            tokenize_time = time.time() - start_time
            
            # Time the reconstruction
            start_time = time.time()
            reconstructed = reconstruct_from_tokens(tokens, tokenizer_type)
            reconstruct_time = time.time() - start_time
            
            # Check accuracy
            is_perfect = (text == reconstructed)
            
            result = {
                'success': True,
                'is_perfect': is_perfect,
                'tokenize_time': tokenize_time,
                'reconstruct_time': reconstruct_time,
                'total_time': tokenize_time + reconstruct_time,
                'token_count': len(tokens),
                'char_count': len(text),
                'chars_per_second': len(text) / (tokenize_time + reconstruct_time) if (tokenize_time + reconstruct_time) > 0 else 0,
                'tokens_per_char': len(tokens) / len(text) if len(text) > 0 else 0
            }
            
            # Update monitor
            self.monitor.update_test_stats(result)
            
            return result
            
        except Exception as e:
            result = {
                'success': False,
                'error': str(e),
                'is_perfect': False,
                'tokenize_time': 0,
                'reconstruct_time': 0,
                'total_time': 0,
                'token_count': 0,
                'char_count': len(text),
                'chars_per_second': 0,
                'tokens_per_char': 0
            }
            
            # Update monitor
            self.monitor.update_test_stats(result)
            
            return result
    
    def run_continuous_tests(self, test_texts: List[str], duration_minutes: int = 10):
        """Run continuous tests for specified duration"""
        print(f"🚀 Starting continuous testing for {duration_minutes} minutes...")
        print("📊 Real-time monitoring enabled!")
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Set up signal handler for graceful shutdown
        def signal_handler(sig, frame):
            print("\n🛑 Stopping tests...")
            self.monitor.stop_monitoring()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        test_count = 0
        
        try:
            while time.time() < end_time:
                # Select random text and tokenizer
                text = random.choice(test_texts)
                tokenizer = random.choice(self.tokenizers)
                
                # Update current test info
                self.monitor.current_test = f"{tokenizer.upper()} - {len(text)} chars"
                
                # Run test
                result = self.test_single_text(text, tokenizer)
                test_count += 1
                
                # Display dashboard every 10 tests
                if test_count % 10 == 0:
                    self.monitor.display_dashboard()
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n🛑 Tests stopped by user")
        
        finally:
            # Stop monitoring
            self.monitor.stop_monitoring()
            
            # Generate final report
            print("\n📊 Generating final performance report...")
            report_file = self.monitor.save_performance_report()
            
            print(f"\n🎉 Continuous testing completed!")
            print(f"📊 Total tests run: {test_count}")
            print(f"📈 Performance report: {report_file}")

def main():
    """Main function for real-time monitoring"""
    print("🚀 SOMA Real-time Monitoring and Testing Framework")
    print("=" * 80)
    
    # Create test runner
    runner = AdvancedTestRunner()
    
    # Generate test texts
    test_texts = [
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
    
    # Add some larger texts
    for i in range(10):
        large_text = ' '.join(['word'] * 1000) + f' {i}'
        test_texts.append(large_text)
    
    # Run continuous tests
    duration = int(input("Enter test duration in minutes (default 10): ") or "10")
    runner.run_continuous_tests(test_texts, duration)

if __name__ == "__main__":
    main()
