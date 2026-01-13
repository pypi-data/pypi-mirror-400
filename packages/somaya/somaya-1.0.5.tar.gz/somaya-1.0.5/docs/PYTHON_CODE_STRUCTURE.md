# Python Code Structure Report

**Total Python Files:** 87

## Root Directory Files

- `main.py` (93 lines)
- `run.py` (173 lines)
- `soma_cli.py` (703 lines)
- `setup.py` (53 lines)
- `start.py` (94 lines)
- `train_soma_complete.py` (729 lines)

## Directory Structure

### `enhanced_semantic_trainer/` (4 files)
- `__init__.py` (8 lines)
- `enhanced_trainer.py` (716 lines)
- `example_train.py` (71 lines)
- `example_use.py` (78 lines)

### `enhanced_semantic_trainer/examples/` (3 files)
- `advanced_usage.py` (107 lines)
- `basic_usage.py` (92 lines)
- `compare_with_basic.py` (85 lines)

### `examples/` (16 files)
- `compare_neighbors.py` (104 lines)
- `comprehensive_vector_store_example.py` (2834 lines)
- `comprehensive_vector_store_example2.py` (3309 lines)
- `embedding_example.py` (262 lines)
- `eval_embedding_quality.py` (178 lines)
- `integrate_source_map_workflow.py` (190 lines)
- `integration_with_transformers.py` (253 lines)
- `quick_start_integration.py` (29 lines)
- `search_examples.py` (681 lines)
- `test_data_interpreter.py` (135 lines)
- `test_full_workflow_500k.py` (1195 lines)
- `test_soma_source_map.py` (308 lines)
- `train_soma_60k_vocab.py` (109 lines)
- `train_semantic_embeddings.py` (145 lines)
- `use_semantic_embeddings.py` (144 lines)
- `use_vector_store.py` (345 lines)

### `soma/` (3 files)
- `__init__.py` (23 lines)
- `cli.py` (159 lines)
- `soma.py` (557 lines)

### `soma/utils/` (4 files)
- `__init__.py` (28 lines)
- `config.py` (149 lines)
- `logging_config.py` (66 lines)
- `validation.py` (154 lines)

### `src/` (3 files)
- `__init__.py` (1 lines)
- `demo_complete_workflow.py` (561 lines)
- `soma_sources.py` (666 lines)

### `src/cli/` (3 files)
- `__init__.py` (1 lines)
- `decode_demo.py` (178 lines)
- `main.py` (94 lines)

### `src/compression/` (2 files)
- `__init__.py` (1 lines)
- `compression_algorithms.py` (88 lines)

### `src/core/` (4 files)
- `__init__.py` (1 lines)
- `base_tokenizer.py` (182 lines)
- `core_tokenizer.py` (3203 lines)
- `parallel_tokenizer.py` (169 lines)

### `src/embeddings/` (6 files)
- `__init__.py` (31 lines)
- `embedding_generator.py` (714 lines)
- `inference_pipeline.py` (274 lines)
- `semantic_trainer.py` (432 lines)
- `vector_store.py` (472 lines)
- `weaviate_vector_store.py` (384 lines)

### `src/examples/` (5 files)
- `demo_enhanced_tokenization.py` (140 lines)
- `demo_stable_system.py` (203 lines)
- `demo_universal_files.py` (174 lines)
- `evaluate_semantics.py` (75 lines)
- `KrishnaTokenizer_Tutorial.ipynb` (Jupyter notebook)

### `src/integration/` (3 files)
- `__init__.py` (20 lines)
- `source_map_integration.py` (178 lines)
- `vocabulary_adapter.py` (301 lines)

### `src/interpretation/` (2 files)
- `__init__.py` (1 lines)
- `data_interpreter.py` (369 lines)

### `src/performance/` (4 files)
- `__init__.py` (1 lines)
- `comprehensive_performance_test.py` (246 lines)
- `test_accuracy.py` (182 lines)
- `test_organized_outputs.py` (73 lines)

### `src/servers/` (8 files)
- `admin_config.py` (89 lines)
- `api_server.py` (276 lines)
- `error_handling.py` (124 lines)
- `job_manager.py` (369 lines)
- `lightweight_server.py` (359 lines)
- `main_server.py` (1173 lines)
- `simple_server.py` (190 lines)

### `src/training/` (4 files)
- `dataset_downloader.py` (178 lines)
- `language_model_trainer.py` (432 lines)
- `vocabulary_builder.py` (301 lines)

### `src/utils/` (2 files)
- `__init__.py` (1 lines)
- `unique_identifier.py` (59 lines)

### `weaviate_codes/` (4 files)
- `__init__.py` (7 lines)
- `example_usage.py` (483 lines)
- `test_connection.py` (52 lines)
- `weaviate_vector_store.py` (382 lines)

## Summary

- **Total Python files:** 87
- **Total lines of code:** ~33,000
- **Main directories:** 
  - `soma/` - Core package (pip installable)
  - `src/` - Source code modules
  - `examples/` - Example scripts
  - `enhanced_semantic_trainer/` - Enhanced trainer
  - `weaviate_codes/` - Weaviate integration

## Notes

This structure follows Python packaging best practices:
- `soma/` is the main package that can be installed via `pip install`
- `src/` contains modular source code organized by functionality
- `examples/` provides usage examples
- Each directory has a clear, single purpose
- Imports use standard Python package structure

**To regenerate this report, run:**
```bash
python scripts/organize_python_files.py
```

