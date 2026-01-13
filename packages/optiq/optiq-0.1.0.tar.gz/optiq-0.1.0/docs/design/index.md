# Design Documents

This section contains detailed design documents and architectural decisions for optiq. These documents provide insight into the reasoning behind major design choices and future development plans.

## Framework Architecture

### [LLM Prompt Engineering](000_llm_prompt.md)
Initial design exploration and prompt engineering for the framework concept.

### [Framework Refactor](001_framework_refactor.md)
Major architectural refactoring decisions and component separation.

### [Data Pipeline Design](002_data_pipeline.md)
Design of the data processing pipeline from FBX to training datasets.

### [Models and RL Integration](003_models_and_rl.md)
Design decisions for model architectures and RL integration strategies.

## Infrastructure & Packaging

### [Packaging, Visualization & Infrastructure](004_packaging_viz_infra.md)
Infrastructure design including packaging, visualization, and deployment.

### [DeIsaac MuJoCo Integration](005_deisaac_mujoco.md)
Integration design with MuJoCo physics engine and DeIsaac framework.

### [CLI Framework](006_cli_framework.md)
Command-line interface design and architecture.

### [Data Model Interfaces](007_data_model_interfaces.md)
Design of data structures and model interfaces.

## RL & Training

### [RL Bootstrap with SB3](008_rl_bootstrap_sb3.md)
Reinforcement learning bootstrapping using Stable-Baselines3.

### [Packaging Extras](009_packaging_extras.md)
Optional dependencies and packaging strategy.

### [Models Registry & Configs](010_models_registry_and_configs.md)
Model registry system and configuration management.

### [Visualization Standardization](011_viz_standardization.md)
Standardization of visualization components and APIs.

## Development & Operations

### [CLI Commands Detailed](012_cli_commands_detailed.md)
Detailed specification of CLI command interfaces.

### [Migration Checklist](013_migration_checklist.md)
Migration planning and checklist for major version updates.

### [Dataset Schema](014_dataset_schema.md)
Dataset format specifications and schema design.

### [SB3 Weight Transfer](015_sb3_weight_transfer.md)
Weight transfer mechanisms for Stable-Baselines3 integration.

### [Training Configs & Losses](016_training_configs_and_losses.md)
Training configuration design and loss function specifications.

### [Retargeting & BC](017_retargeting_and_bc.md)
Motion retargeting and behavior cloning methodologies.

### [RL Integration Detailed](018_rl_integration_detailed.md)
Detailed design for reinforcement learning integration.

## Reading Guide

### For New Contributors
Start with documents 000-003 to understand the core framework philosophy and architecture.

### For RL Researchers
Focus on documents 008, 015, 017, and 018 for RL-specific design decisions.

### For Infrastructure Developers
Review documents 004, 009, and 012 for packaging and deployment concerns.

### For Data Scientists
Documents 002, 007, and 014 contain data pipeline and format specifications.

## Contributing

These design documents are living artifacts. When making significant changes:

1. **Update relevant design docs** to reflect new decisions
2. **Add new documents** for major new features
3. **Reference design docs** in pull request descriptions
4. **Keep docs current** with implementation changes

## Legacy Documents

Some earlier documents may contain outdated information. Always cross-reference with the current codebase and recent issues/PRs for the most up-to-date information.

---

**📝 Note**: These documents are primarily for internal development reference. For user-facing documentation, see the [User Guide](../user-guide/index.md).
