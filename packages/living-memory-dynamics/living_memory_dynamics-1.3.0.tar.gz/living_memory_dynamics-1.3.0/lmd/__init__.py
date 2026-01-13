"""Living Memory Dynamics (LMD) - A Novel Framework for Narrative-Generating Episodic Memory.

Invented by Joshua R. Thomas, January 2026.

Core Innovation: Memories are not static patterns - they are LIVING entities with:
- Internal state that evolves over time
- Narrative phase (where in the story arc)
- Valence trajectory (emotional journey, not single tag)
- Metabolic energy (how "alive" the memory is)
- Coupling field (how it interacts with other memories)

The Joshua R. Thomas Memory Equation:
    dM/dt = grad_phi(N) + sum_j(Gamma_ij * R(v_i, v_j)) + A(M, context) + kappa * eta(t)

Where:
    N(phi) = Narrative Potential (story attractor landscape)
    R(v_i, v_j) = Resonance Function (emotional coupling)
    A(M, xi) = Activation Function (contextual triggering)
    eta(t) = Creative Noise (generative stochasticity)
"""

from .living_memory import LivingMemory, ValenceTrajectory, NarrativePhase, MetabolicState
from .config import LMDConfig
from .dynamics import LMDDynamics
from .coupling import CouplingField
from .metabolism import MemoryMetabolism
from .narrative import NarrativeSynthesizer, GeneratedNarrative
from .toy_system import LMDToySystem, LMDMetrics
from .story_encoder import StoryEncoder, EncodedStory, get_sample_story
from .chaos_monitor import ChaosMonitor, ChaosMetrics, run_chaos_analysis
from .prediction import NarrativePredictor, PredictionResult, run_prediction_benchmark
from .imagination import (
    StructuredMemory,
    MemorySlot,
    SlotType,
    Transform,
    TransformType,
    TransformOps,
    WillVector,
    WillGenerator,
    MentalCanvas,
    MemoryDecomposer,
    CanvasEntity
)
from .plausibility import (
    PlausibilityField,
    PlausibilityScore,
    IdeaEvaluator,
    CreativityOptimizer
)
from .ideation import (
    IdeationEngine,
    IdeationConfig,
    IdeationResult,
    IdeationPhase,
    AutonomousIdeator,
    run_ideation_demo
)
from .safeguards import (
    IDGenerator,
    get_id_generator,
    reset_id_generator,
    RepulsionField,
    ExploredRegion,
    RealityAnchor,
    AutonomyController,
    AutonomyTrigger,
    TriggerCondition,
    ResourceBudget
)
from .heartbeat_integration import (
    HeartbeatIdeator,
    HeartbeatIdeationMetrics,
    run_long_running_demo
)
# Note: Benchmarks moved to separate benchmarks/ folder
# from benchmarks import LMDBenchmarks, run_benchmarks, BenchmarkSuite, TimingResult
from .creative_leaps import (
    CreativeLeapEngine,
    CreativeLeapConfig,
    CreativeLeap,
    LeapType,
    LeapOperator,
    AnalogicalTransfer,
    ManifoldWalker,
    OrthogonalComposer,
    VoidExtrapolator
)
from .hierarchical_ideas import (
    HierarchicalIdea,
    HierarchicalIdeaFactory,
    IdeaGrafter,
    IdeaComponent,
    ComponentType,
    RelationType,
    ComponentRelation,
    GraftOperation,
    GraftResult
)
from .curiosity_prober import (
    ActiveCuriosityProber,
    CuriosityDrivenWill,
    ProbeResult,
    ProbeStrategy,
    VoidRegion
)
from .creative_ideation import (
    CreativeIdeationEngine,
    CreativeIdeationConfig,
    CreativeIdeationResult,
    CreativeIdea,
    IdeaForm,
    run_creative_ideation_demo
)
from .language_grounding import (
    LanguageGrounding,
    GroundingConfig,
    EncoderType,
    TextCorpus,
    GroundedText,
    RetrievalResult,
    CreativeLeapDescription,
    LLMDescriber,
    create_grounding,
    SENTENCE_TRANSFORMERS_AVAILABLE,
)

__all__ = [
    # Core
    "LivingMemory",
    "ValenceTrajectory",
    "NarrativePhase",
    "MetabolicState",
    "LMDConfig",
    # Dynamics
    "LMDDynamics",
    "CouplingField",
    "MemoryMetabolism",
    # Narrative
    "NarrativeSynthesizer",
    "GeneratedNarrative",
    # Testing
    "LMDToySystem",
    "LMDMetrics",
    # Real data
    "StoryEncoder",
    "EncodedStory",
    "get_sample_story",
    # Chaos
    "ChaosMonitor",
    "ChaosMetrics",
    "run_chaos_analysis",
    # Prediction
    "NarrativePredictor",
    "PredictionResult",
    "run_prediction_benchmark",
    # Imagination
    "StructuredMemory",
    "MemorySlot",
    "SlotType",
    "Transform",
    "TransformType",
    "TransformOps",
    "WillVector",
    "WillGenerator",
    "MentalCanvas",
    "MemoryDecomposer",
    "CanvasEntity",
    # Plausibility
    "PlausibilityField",
    "PlausibilityScore",
    "IdeaEvaluator",
    "CreativityOptimizer",
    # Ideation
    "IdeationEngine",
    "IdeationConfig",
    "IdeationResult",
    "IdeationPhase",
    "AutonomousIdeator",
    "run_ideation_demo",
    # Safeguards
    "IDGenerator",
    "get_id_generator",
    "reset_id_generator",
    "RepulsionField",
    "ExploredRegion",
    "RealityAnchor",
    "AutonomyController",
    "AutonomyTrigger",
    "TriggerCondition",
    "ResourceBudget",
    # Heartbeat Integration
    "HeartbeatIdeator",
    "HeartbeatIdeationMetrics",
    "run_long_running_demo",
    # Note: Benchmarks moved to benchmarks/ folder - import from benchmarks instead
    # Creative Leaps
    "CreativeLeapEngine",
    "CreativeLeapConfig",
    "CreativeLeap",
    "LeapType",
    "LeapOperator",
    "AnalogicalTransfer",
    "ManifoldWalker",
    "OrthogonalComposer",
    "VoidExtrapolator",
    # Hierarchical Ideas
    "HierarchicalIdea",
    "HierarchicalIdeaFactory",
    "IdeaGrafter",
    "IdeaComponent",
    "ComponentType",
    "RelationType",
    "ComponentRelation",
    "GraftOperation",
    "GraftResult",
    # Curiosity Prober
    "ActiveCuriosityProber",
    "CuriosityDrivenWill",
    "ProbeResult",
    "ProbeStrategy",
    "VoidRegion",
    # Creative Ideation
    "CreativeIdeationEngine",
    "CreativeIdeationConfig",
    "CreativeIdeationResult",
    "CreativeIdea",
    "IdeaForm",
    "run_creative_ideation_demo",
    # Language Grounding
    "LanguageGrounding",
    "GroundingConfig",
    "EncoderType",
    "TextCorpus",
    "GroundedText",
    "RetrievalResult",
    "CreativeLeapDescription",
    "LLMDescriber",
    "create_grounding",
    "SENTENCE_TRANSFORMERS_AVAILABLE",
]

# CUDA acceleration (optional)
try:
    from . import cuda
    from .cuda import (
        is_cuda_available,
        get_device,
        TRITON_AVAILABLE,
        BatchCouplingComputer,
        BatchDensityEstimator,
        BatchMemoryStepper,
    )
    __all__.extend([
        "cuda",
        "is_cuda_available",
        "get_device",
        "TRITON_AVAILABLE",
        "BatchCouplingComputer",
        "BatchDensityEstimator",
        "BatchMemoryStepper",
    ])
except ImportError:
    # CUDA module not available (missing triton or torch)
    pass

__author__ = "Joshua R. Thomas"
__email__ = "mordiaky@gmail.com"
__invention_date__ = "2026-01-04"
__version__ = "1.3.0"  # Added language grounding with sentence-transformers
