# SAGE Data 📊

**Dataset management module for SAGE benchmark suite**

Provides unified access to multiple datasets through a two-layer architecture:
- **Sources**: Physical datasets in `sage/data/sources/` (qa_base, bbh, mmlu, gpqa, locomo, orca_dpo, agent_benchmark, agent_sft, agent_tools, etc.)
- **Usages**: Logical views for experiments in `sage/data/usages/` (rag, libamm, neuromem, agent_eval)

## 🚀 Quick Start

### Installation

```bash
# Run the quickstart script (recommended)
./quickstart.sh

# Or install manually
pip install -e .

# Install with optional dependencies
pip install -e ".[all]"        # All datasets
pip install -e ".[datasets]"   # Hugging Face datasets
pip install -e ".[alignment]"  # DPO/alignment tools
pip install -e ".[agent]"      # Agent datasets
```

### Basic Usage

```python
from sage.data import DataManager

manager = DataManager.get_instance()

# Access datasets by logical usage profile
rag = manager.get_by_usage("rag")
qa_loader = rag.load("qa_base")  # already instantiated
queries = qa_loader.load_queries()

# Or fetch a specific data source directly
bbh_loader = manager.get_by_source("bbh")
tasks = bbh_loader.get_task_names()
```

## Available Datasets

| Dataset | Description | Download Required | Storage |
|---------|-------------|-------------------|---------|
| **qa_base** | Question-Answering with knowledge base | ❌ No (included) | Local files |
| **locomo** | Long-context memory benchmark | ✅ Yes (`python -m locomo.download`) | Local files (2.68MB) |
| **bbh** | BIG-Bench Hard reasoning tasks | ❌ No (included) | Local JSON files |
| **mmlu** | Massive Multitask Language Understanding | 📥 Optional (`python -m mmlu.download --all-subjects`) | On-demand or Local (~160MB) |
| **gpqa** | Graduate-Level Question Answering | ✅ Auto (Hugging Face) | On-demand (~5MB cached) |
| **orca_dpo** | Preference pairs for alignment/DPO | ✅ Auto (Hugging Face) | On-demand (varies) |
| **agent_benchmark** | Agent evaluation tasks | ❌ No (included) | Local JSON files |
| **agent_sft** | Agent supervised fine-tuning conversations | ❌ No (included) | Local JSON files |
| **agent_tools** | Agent tool catalog and schemas | ❌ No (included) | Local JSON files |

See `examples/` for detailed usage examples.

## 📁 Project Structure

```
sage/data/
├── sources/              # Physical dataset loaders
│   ├── qa_base/         # Q&A with knowledge base
│   ├── bbh/             # BIG-Bench Hard tasks
│   ├── mmlu/            # MMLU benchmark
│   ├── gpqa/            # Graduate-level Q&A
│   ├── locomo/          # Long-context memory
│   ├── orca_dpo/        # DPO preference pairs
│   ├── agent_benchmark/ # Agent evaluation tasks
│   ├── agent_sft/       # Agent SFT conversations
│   └── agent_tools/     # Agent tool catalog
└── usages/              # Logical views and profiles
    ├── rag/             # RAG experiments
    ├── libamm/          # LibAMM benchmarks
    ├── neuromem/        # Neuromem experiments
    └── agent_eval/      # Agent evaluation profiles
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed design documentation.

## 📖 Examples

```bash
python examples/qa_examples.py            # QA dataset usage
python examples/locomo_examples.py        # LoCoMo dataset usage
python examples/bbh_examples.py           # BBH dataset usage
python examples/mmlu_examples.py          # MMLU dataset usage
python examples/gpqa_examples.py          # GPQA dataset usage
python examples/orca_dpo_examples.py      # Orca DPO dataset usage
python examples/integration_example.py    # Cross-dataset integration
```

## License

MIT License - see [LICENSE](LICENSE) file.

## 🔗 Links

- **Repository**: https://github.com/intellistream/sageData
- **Issues**: https://github.com/intellistream/sageData/issues

## ❓ Common Issues

**Q: Where's the LoCoMo data?**  
A: Run `python -m locomo.download` to download it (2.68MB from Hugging Face).

**Q: How to download MMLU for offline use?**  
A: Run `python -m mmlu.download --all-subjects` to download all subjects (~160MB).

**Q: GPQA access error?**  
A: You need to accept the dataset terms on Hugging Face: https://huggingface.co/datasets/Idavidrein/gpqa

**Q: How to use Orca DPO for alignment research?**  
A: Use `DataManager.get_by_source("orca_dpo")` to get the loader, then use `format_for_dpo()` to prepare data for training.

---

**Version**: 0.2.1.0 | **Last Updated**: January 2026
