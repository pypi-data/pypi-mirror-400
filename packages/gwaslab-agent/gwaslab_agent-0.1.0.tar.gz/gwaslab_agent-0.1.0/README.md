## GWASLab-Agent

**GWASLab-Agent** is an LLM-powered framework for automated GWAS summary statistics processing, quality control, transformation, and visualization.  
It extends the original **GWASLab** Python package with intelligent planning, multi-step workflow generation, and agent-driven execution.

GWASLab-Agent is designed to serve as an *autonomous GWAS assistant*, capable of interpreting user instructions, planning complex operations, managing file paths, and producing publication-ready summaries and figures.

<img width="1090" height="536" alt="image" src="https://github.com/user-attachments/assets/bf9b085e-5f14-43fc-9106-1ac765762db8" />



---

## Installation

1. Create a new environment (recommended)
```
# Create a clean environment with Python 3.12
conda create -n gwaslab-agent python=3.12

# Activate it
conda activate gwaslab-agent
```

2. Install GWASLab and GWASLab-Agent
```bash
pip install gwaslab
pip install gwaslab_agent
```

---

## Design of GWASLab-Agent

### SmartSumstats Object

At the core of GWASLab-Agent is the **SmartSumstats** object — an LLM-enhanced wrapper around `gl.Sumstats`.  
It integrates five coordinated sub-agents:

- **Loader** — detects file formats, parses paths, handles chromosome patterns  
- **Planner** — constructs optimal multi-step workflows  
- **Worker** — executes tasks, QC steps, and visualizations  
- **PathManager** — manages input/output paths and reference resources  
- **Summarizer** — generates structured summaries and Methods-section text  

Together, these sub-agents enable fully automated GWAS workflows with minimal user input.

---


---

## Citation

(Coming soon — please cite GWASLab and GWASLab-Agent once the corresponding manuscripts or preprints are available.)
