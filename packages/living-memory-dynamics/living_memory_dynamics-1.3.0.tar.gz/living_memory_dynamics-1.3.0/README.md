# Living Memory Dynamics (LMD)

> **A Novel Framework for Narrative-Generating Episodic Memory with Creative Leaps and Language Grounding**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/license-Custom-orange.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.3.0-green.svg)]()

## What Makes LMD Different?

Traditional memory systems store static embeddings. **LMD treats memories as living entities** that:

- **Breathe**: Memories have metabolic energy (vivid, active, dormant, fading, ghost)
- **Feel**: Emotional trajectories, not single valence tags
- **Tell Stories**: Narrative phases (setup → conflict → climax → resolution)
- **Resonate**: Memories couple and influence each other through resonance fields
- **Create**: Generate novel ideas through internal creative leaps

## The Joshua R. Thomas Memory Equation

```
dM/dt = ∇φ(N) + Σⱼ Γᵢⱼ R(vᵢ, vⱼ) + A(M, ξ) + κη(t)
```

Where:
- `∇φ(N)` = Narrative potential (story attractor landscape)
- `R(vᵢ, vⱼ)` = Resonance function (emotional coupling between memories)
- `A(M, ξ)` = Activation function (contextual triggering)
- `κη(t)` = Creative noise (generative stochasticity)

## Creative Leaps (v1.1.0)

LMD doesn't just store—it **invents**. Four internal operators enable human-like creative jumps:

| Operator | What It Does | Example |
|----------|-------------|---------|
| **Analogical Transfer** | Transplants patterns between distant domains | "dragon fire" + "glass refraction" → "prismatic breath weapon" |
| **Manifold Walker** | Diffuses through embedding space | Gradual concept morphing |
| **Orthogonal Composer** | Gram-Schmidt perpendicular merges | Combines concepts along independent axes |
| **Void Extrapolator** | Ray-traces into unexplored territory | Discovers genuinely novel concepts |

```python
from lmd import CreativeLeapEngine, LivingMemory

engine = CreativeLeapEngine(content_dim=256)
memories = [LivingMemory.create(embedding) for embedding in my_embeddings]

# Generate creative leaps
leaps = engine.batch_leap(memories, n_leaps=5, dopamine=0.8)
for leap in leaps:
    print(f"{leap.leap_type}: novelty={leap.novelty:.2f}")
```

## Language Grounding (v1.3.0)

**The Problem**: LMD creates ideas as vectors - you can't read what they mean.

**The Solution**: Language Grounding bridges vectors and human-readable text.

```
Text Input --> Embedding --> Creative Leap --> New Embedding --> Text Output
"dragon"   --> [0.2, 0.8..] --> ORTHOGONAL --> [0.5, 0.3..] --> "prismatic creature"
```

### Does LMD work without Language Grounding?

**Yes!** Language Grounding is **100% optional**. Core LMD works fine without it:
- Core LMD: `pip install living-memory-dynamics` (vectors only)
- With Language: `pip install living-memory-dynamics[language]` (text in/out)

### Quick Example

```python
from lmd import create_grounding, CreativeLeapEngine

# Create grounding (downloads MiniLM model ~80MB first time)
grounding = create_grounding(encoder="minilm")

# Encode text to embeddings
dragon = grounding.encode("fire-breathing dragon")
glass = grounding.encode("crystalline glass structure")

# Build a corpus for decoding
grounding.add_to_corpus("fire-breathing dragon")
grounding.add_to_corpus("crystalline glass structure")
grounding.add_to_corpus("stained glass window")
grounding.add_to_corpus("dragon scales armor")

# Blend two concepts
blended = (dragon + glass) / 2
blended = blended / blended.norm()

# Decode back to text
result = grounding.decode(blended, top_k=3)
print(result.interpolated_description)
# Output: "blend of 'crystalline glass structure' (50%) and 'fire-breathing dragon' (50%)"
```

### Generate New Ideas with Text Output

```python
# Create leap engine matching embedding dimension
engine = CreativeLeapEngine(content_dim=grounding.embedding_dim)

# Encode source concepts
sources = [
    grounding.encode("volcanic eruption").cpu(),
    grounding.encode("frozen ice sculpture").cpu(),
    grounding.encode("rainbow spectrum").cpu(),
]

# Generate creative leap
leap = engine.leap(sources, dopamine=0.7)

# Describe what was created
description = grounding.describe_leap(
    leap_type=leap.leap_type.name,
    sources=sources,
    result=leap.embedding,
)
print(description.synthesized_description)
# Output: "Extrapolated beyond 'volcanic eruption' + 'frozen ice' + 'rainbow' into [novel concept]"
print(f"Novelty: {description.novelty_score}")
# Output: "Novelty: 1.0" (completely new!)
```

### Ground Living Memories to Readable Text

```python
from lmd import LivingMemory, ValenceTrajectory, NarrativePhase

# Create a memory from text
embedding = grounding.encode("ancient dragon guarding treasure")
memory = LivingMemory(
    id="memory_0",
    content=embedding,
    energy=0.8,
    valence=ValenceTrajectory(points=torch.tensor([0.5, 0.7, 0.6])),
    phase=NarrativePhase.SETUP,
)

# Later, decode what the memory represents
grounded = grounding.ground_memory(memory)
print(grounded.text)
# Output: "blend of 'ancient dragon guarding treasure' (64%) and 'ancient mythical creature' (36%)"
```

### Run the Full Demo

```bash
# Install with language support
pip install living-memory-dynamics[language]

# Run the demo
python -c "from lmd.examples import language_grounding; language_grounding.main()"
# Or clone and run:
git clone https://github.com/mordiaky/LMD.git
cd LMD
pip install -e ".[language]"
python examples/language_grounding.py
```

## Installation

```bash
# Core only (vectors, no text)
pip install living-memory-dynamics

# With language grounding (text in/out)
pip install living-memory-dynamics[language]

# With GPU acceleration (Triton CUDA kernels)
pip install living-memory-dynamics[cuda]

# Everything (language + cuda + dev tools)
pip install living-memory-dynamics[all]
```

Or from source:

```bash
git clone https://github.com/mordiaky/LMD.git
cd LMD
pip install -e ".[language]"  # or [all] for everything
```

## Quick Start

### 1. Create Living Memories

```python
import torch
from lmd import LivingMemory, ValenceTrajectory, NarrativePhase

# Memories are born with energy, emotion, and narrative phase
memory = LivingMemory(
    id="memory_001",
    content=torch.randn(256),  # Embedding vector
    energy=1.0,  # Metabolic energy (0-2)
    valence=ValenceTrajectory.from_arc(onset=0.3, peak=0.9, resolution=0.6),
    phase=NarrativePhase.SETUP
)
```

### 2. Let Memories Evolve

```python
from lmd import LMDDynamics, LMDConfig

config = LMDConfig(content_dim=256)
dynamics = LMDDynamics(config)

# Step the system forward
for t in range(100):
    dynamics.step(memories, dt=0.01)
    # Memories naturally evolve, couple, and generate narratives
```

### 3. Generate Creative Ideas

```python
from lmd import CreativeIdeationEngine, CreativeIdeationConfig

config = CreativeIdeationConfig(content_dim=256)
engine = CreativeIdeationEngine(config)

# Ideate with dopamine modulation
result = engine.ideate(memories, dopamine=0.7, n_ideas=10)

for idea in result.ideas[:5]:
    print(f"Form: {idea.form}, Novelty: {idea.novelty:.2f}, Score: {idea.total_score:.2f}")
```

### 4. Hierarchical Ideas with Grafting

```python
from lmd import HierarchicalIdeaFactory, IdeaGrafter

factory = HierarchicalIdeaFactory(content_dim=256)
grafter = IdeaGrafter(content_dim=256)

# Create tree-structured ideas
dragon = factory.from_embedding(dragon_embedding, depth=3)
crystal = factory.from_embedding(crystal_embedding, depth=3)

# Graft components between ideas
result = grafter.swap_component(dragon, crystal.root, target_id="fire_component")
# Result: dragon with crystalline properties
```

## Architecture

```
lmd/
├── living_memory.py       # Core LivingMemory datastructure
├── dynamics.py            # LMDDynamics engine
├── coupling.py            # Memory resonance fields
├── metabolism.py          # Energy dynamics
├── narrative.py           # Story generation
├── imagination.py         # Mental canvas & transforms
├── plausibility.py        # Reality grounding
├── creative_leaps.py      # 4 creative operators
├── hierarchical_ideas.py  # Tree-structured ideas
├── curiosity_prober.py    # Void exploration
├── creative_ideation.py   # Unified ideation engine
├── language_grounding.py  # Text <-> embedding bridge (v1.3.0)
└── safeguards.py          # Repulsion, anchoring, budgets
```

## Benchmarks

| Operation | Throughput | Memory |
|-----------|-----------|--------|
| Memory Evolution | ~10,000 steps/s | O(n) |
| Analogical Transfer | ~500 leaps/s | O(n²) |
| Orthogonal Composition | ~800 leaps/s | O(n) |
| Void Extrapolation | ~600 leaps/s | O(n) |
| Full Ideation Cycle | ~50 ideas/s | O(n²) |

*Benchmarked on NVIDIA GeForce RTX 5080 (16GB VRAM), CUDA 13.1, 256-dim embeddings, 100 memories*

## Key Features

- **No LLM Required**: All operations are internal to embedding space
- **Emergent Narratives**: Stories arise from memory dynamics
- **Creative Recombination**: Generates novel ideas by operating on stored memories (not from nothing)
- **Biologically Inspired**: Metabolic states, resonance, narrative arcs
- **GPU Accelerated**: Full CUDA support via Triton kernels
- **Thread Safe**: Concurrent access supported

## Research Paper

See [RESEARCH_PAPER_LMD.md](./docs/RESEARCH_PAPER_LMD.md) for the full technical paper including:
- Mathematical foundations
- Algorithm pseudocode
- Comprehensive benchmarks
- Comparison with existing systems

## Examples

```bash
# Run any example
python examples/<example_name>.py
```

| Example | Description | Requires |
|---------|-------------|----------|
| [basic_usage.py](examples/basic_usage.py) | Create and evolve memories | Core |
| [creative_leaps.py](examples/creative_leaps.py) | Generate inventions | Core |
| [hierarchical_ideas.py](examples/hierarchical_ideas.py) | Tree-structured concepts | Core |
| [language_grounding.py](examples/language_grounding.py) | Text in/out with real output | `[language]` |

## License

This project uses a custom license that allows free use for research and personal projects while reserving commercial rights. See [LICENSE](LICENSE) for details.

For commercial licensing inquiries, please contact the author.

## Citation

If you use LMD in your research, please cite:

```bibtex
@software{lmd2026,
  author = {Thomas, Joshua R.},
  title = {Living Memory Dynamics: A Novel Framework for Narrative-Generating Episodic Memory},
  year = {2026},
  version = {1.3.0},
  url = {https://github.com/mordiaky/LMD}
}
```

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

---

*Invented by Joshua R. Thomas, January 2026*

*Contact: mordiaky@gmail.com*
