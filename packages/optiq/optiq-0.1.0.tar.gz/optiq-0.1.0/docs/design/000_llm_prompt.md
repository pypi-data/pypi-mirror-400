# How to feed these design docs to an LLM

Use this prompt (or adapt it) when sending any design doc to an LLM. Keep the repo path and branch accurate so the model can look up referenced files if tooling is available.

```
You are refactoring the optiq repository at /Users/TedT/optiq (branch: main) into an imitation-learning-first framework. Follow the attached design doc exactly; ask clarifying questions if anything is ambiguous. Honor all constraints and non-goals in the doc. When proposing or implementing code, keep existing functionality unless the doc explicitly allows breaking changes. Reference the cited files/lines from the doc to stay consistent. Never touch the FBX node extractor scripts or the Mixamo downloading scripts. Prefer HDF5/Parquet for datasets. Remove all Isaac/Isaac-Lab dependencies. Standardize on Mujoco + stable-baselines3. Preserve Plotly/MoviePy visualization flows and make them framework-ready. Package as a single `optiq` package with extras `[ml]`, `[rl]`, `[web]`, `[infra]`, `[viz]`.
```

When creating new design docs:
- Be explicit about goals, non-goals, and migration steps.
- Cite real code with filepath and line ranges.
- Include API signatures, data shapes, and configuration knobs.
- Call out open questions and TODOs.
