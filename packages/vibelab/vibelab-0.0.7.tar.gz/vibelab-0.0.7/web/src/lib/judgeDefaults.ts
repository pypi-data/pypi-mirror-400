export const DEFAULT_JUDGE_GUIDANCE = `Evaluate the result against the scenario prompt and the produced patch/output.

## Scoring Guidelines
Rate the solution on a 1-4 scale:
- **4 (Perfect)**: Fully implements the required functionality. May differ in style/approach.
- **3 (Good)**: Implements core functionality with minor gaps or issues.
- **2 (Workable)**: Partially implements the functionality; needs significant improvements.
- **1 (Bad)**: Does not implement the required functionality or introduces bugs.

**Important**: An exact match is NOT required. Focus on functional equivalence - whether the solution achieves the same outcome, not whether the code looks identical.

## Evaluation Criteria
- **Correctness**: The change satisfies the prompt and is technically sound
- **Completeness**: All required parts are implemented; no obvious missing steps
- **Safety**: Avoids breaking changes, regressions, or risky assumptions
- **Clarity**: Code is readable/maintainable and aligns with existing style

Be consistent across results. If something is unclear or partially correct, explain briefly in notes.`


