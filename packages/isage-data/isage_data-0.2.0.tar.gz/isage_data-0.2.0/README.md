# SAGE Data 📊# SAGE Data ��



**Dataset management module for SAGE benchmark suite****Dataset management module for SAGE benchmark suite**



Provides unified access to multiple datasets through a two-layer architecture:Provides unified access to multiple datasets through a two-layer architecture:

- **Sources**: Physical datasets in `sage/data/sources/` (qa_base, bbh, mmlu, gpqa, locomo, orca_dpo, agent_benchmark, etc.)- **Sources**: Physical datasets (qa_base, bbh, mmlu, gpqa, locomo, orca_dpo)

- **Usages**: Logical views for experiments documented in `docs/usages/`- **Usages**: Logical views for experiments (rag, libamm, neuromem, agent_eval)



## 🚀 Quick Start## Quick Start



### Installation```python

from sage.data import DataManager

```bash

# Run the quickstart script (recommended)manager = DataManager.get_instance()

./quickstart.sh

# Access datasets by logical usage profile

# Or install manuallyrag = manager.get_by_usage("rag")

pip install -e .qa_loader = rag.load("qa_base")  # already instantiated

queries = qa_loader.load_queries()

# Install with optional dependencies

pip install -e ".[all]"  # All datasets# Or fetch a specific data source directly

pip install -e ".[datasets]"  # Hugging Face datasetsbbh_loader = manager.get_by_source("bbh")

pip install -e ".[alignment]"  # DPO/alignment toolstasks = bbh_loader.get_task_names()

``````



### Basic Usage## Available Datasets



```python| Dataset | Description | Download Required | Storage |

from sage.data import DataManager|---------|-------------|-------------------|---------|

| **qa_base** | Question-Answering with knowledge base | ❌ No (included) | Local files |

manager = DataManager.get_instance()| **locomo** | Long-context memory benchmark | ✅ Yes (`python -m locomo.download`) | Local files (2.68MB) |

| **bbh** | BIG-Bench Hard reasoning tasks | ❌ No (included) | Local JSON files |

# Access datasets by logical usage profile| **mmlu** | Massive Multitask Language Understanding | 📥 Optional (`python -m mmlu.download --all-subjects`) | On-demand or Local (~160MB) |

rag = manager.get_by_usage("rag")| **gpqa** | Graduate-Level Question Answering | ✅ Auto (Hugging Face) | On-demand (~5MB cached) |

qa_loader = rag.load("qa_base")| **orca_dpo** | Preference pairs for alignment/DPO | ✅ Auto (Hugging Face) | On-demand (varies) |

queries = qa_loader.load_queries()

See `examples/` for detailed usage examples.

# Or fetch a specific data source directly

bbh_loader = manager.get_by_source("bbh")## 📖 Examples

tasks = bbh_loader.get_task_names()

```bash

# Access Orca DPO for alignment researchpython examples/qa_examples.py            # QA dataset usage

from sage.data.sources.orca_dpo import OrcaDPODataLoaderpython examples/locomo_examples.py        # LoCoMo dataset usage

dpo_loader = OrcaDPODataLoader()python examples/bbh_examples.py           # BBH dataset usage

examples = dpo_loader.load_data(split="train")python examples/mmlu_examples.py          # MMLU dataset usage

```python examples/gpqa_examples.py          # GPQA dataset usage

python examples/orca_dpo_examples.py      # Orca DPO dataset usage

## 📦 Available Datasetspython examples/integration_example.py    # Cross-dataset integration

```

| Dataset | Description | Download Required | Storage | Location |

|---------|-------------|-------------------|---------|----------|## License

| **qa_base** | Question-Answering with knowledge base | ❌ No (included) | Local files | `sage/data/sources/qa_base/` |

| **locomo** | Long-context memory benchmark | ✅ Yes (`python -m locomo.download`) | Local (2.68MB) | `sage/data/sources/locomo/` |MIT License - see [LICENSE](LICENSE) file.

| **bbh** | BIG-Bench Hard reasoning tasks | ❌ No (included) | Local JSON | `sage/data/sources/bbh/` |

| **mmlu** | Massive Multitask Language Understanding | 📥 Optional | On-demand/Local (~160MB) | `sage/data/sources/mmlu/` |## 🔗 Links

| **gpqa** | Graduate-Level Question Answering | ✅ Auto (HF) | On-demand (~5MB) | `sage/data/sources/gpqa/` |

| **orca_dpo** | Preference pairs for alignment/DPO | ✅ Auto (HF) | On-demand (varies) | `sage/data/sources/orca_dpo/` |- **Repository**: https://github.com/intellistream/sageData

| **agent_benchmark** | Agent evaluation tasks | ❌ No (included) | Local files | `sage/data/sources/agent_benchmark/` |- **Issues**: https://github.com/intellistream/sageData/issues

| **agent_tools** | Tool catalog for agents | ❌ No (included) | Local files | `sage/data/sources/agent_tools/` |

| **agent_sft** | SFT conversation data | ❌ No (included) | Local files | `sage/data/sources/agent_sft/` |## ❓ Common Issues



## 📖 Examples**Q: Where's the LoCoMo data?**  

A: Run `python -m locomo.download` to download it (2.68MB from Hugging Face).

```bash

python examples/qa_examples.py            # QA dataset usage**Q: How to download MMLU for offline use?**  

python examples/locomo_examples.py        # LoCoMo dataset usageA: Run `python -m mmlu.download --all-subjects` to download all subjects (~160MB).

python examples/bbh_examples.py           # BBH dataset usage

python examples/mmlu_examples.py          # MMLU dataset usage**Q: GPQA access error?**  

python examples/gpqa_examples.py          # GPQA dataset usageA: You need to accept the dataset terms on Hugging Face: https://huggingface.co/datasets/Idavidrein/gpqa

python examples/orca_dpo_examples.py      # Orca DPO dataset usage

python examples/integration_example.py    # Cross-dataset integration**Q: How to use Orca DPO for alignment research?**  

```A: Use `DataManager.get_by_source("orca_dpo")` to get the loader, then use `format_for_dpo()` to prepare data for training.



## 📁 Project Structure---



```**Version**: 0.1.0 | **Last Updated**: December 2025

sageData/
├── quickstart.sh              # Quick setup script
├── .pre-commit-config.yaml    # Code quality hooks
├── pyproject.toml             # Package configuration
├── README.md                  # This file
├── LICENSE                    # MIT license
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md        # System architecture
│   └── usages/                # Usage profiles (rag, agent_eval, etc.)
├── sage/                      # Main package
│   └── data/
│       ├── manager.py         # DataManager singleton
│       └── sources/           # All dataset sources
│           ├── orca_dpo/      # DPO preference data
│           ├── agent_benchmark/
│           ├── agent_tools/
│           └── ...
├── examples/                  # Usage examples
└── tests/                     # Test suite
```

## 🛠️ Development

### Setup Development Environment

```bash
# Run quickstart with development dependencies
./quickstart.sh

# Or manually install dev dependencies
pip install pytest pytest-cov black flake8 isort mypy pre-commit
pre-commit install
```

### Run Tests

```bash
pytest tests/
pytest tests/ -v --cov=sage
```

### Code Quality

Pre-commit hooks automatically run on git commit:
- **ruff check**: Code linting (replaces flake8, isort, pyupgrade)
- **ruff format**: Code formatting (replaces black)
- **mypy**: Type checking

Run manually:
```bash
pre-commit run --all-files
```

## 📚 Documentation

- **Architecture**: See `docs/ARCHITECTURE.md` for system design
- **Usage Profiles**: See `docs/usages/` for experiment configurations
- **API Reference**: Use `help(DataManager)` in Python

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
A: Accept dataset terms on Hugging Face: https://huggingface.co/datasets/Idavidrein/gpqa

**Q: How to use Orca DPO for alignment research?**  
A: Import from `sage.data.sources.orca_dpo` and use `format_for_dpo()` to prepare training data.

**Q: Where did the root-level docs go?**  
A: All documentation is now in the `docs/` directory for better organization.

## 🔄 Recent Changes (v0.2.0)

- ✅ Added `quickstart.sh` for easy setup
- ✅ Added `.pre-commit-config.yaml` for code quality
- ✅ Moved `orca_dpo` to `sage/data/sources/`
- ✅ Moved documentation to `docs/` directory
- ✅ Moved usage profiles to `docs/usages/`
- ✅ Improved project structure and organization

---

**Version**: 0.2.0 | **Last Updated**: January 2026
