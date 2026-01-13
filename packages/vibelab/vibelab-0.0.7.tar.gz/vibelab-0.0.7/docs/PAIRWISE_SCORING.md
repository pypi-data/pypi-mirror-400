# Pairwise Scoring Reference

## Overview

Pairwise scoring is a comparison-based evaluation method where humans indicate which of two results is better, rather than assigning absolute scores. This complements the existing 1-4 quality scoring system.

## Why Pairwise Scoring?

### Advantages
1. **Cognitive ease**: Humans are better at relative comparisons than absolute judgments
2. **Reduced calibration bias**: Different annotators may have different score thresholds, but relative preferences are more consistent
3. **Handles ties naturally**: Can express "both good", "both bad", or "no preference"
4. **Better for close cases**: When two results are similar quality, pairwise comparison is more meaningful than arguing about 3 vs 4

### Limitations
1. **Doesn't scale**: O(n²) comparisons needed for n results (mitigated by smart sampling)
2. **Transitivity violations**: A > B and B > C doesn't guarantee A > C (but this is informative!)
3. **No absolute quality**: Can't tell if all results are good or all are bad

## Data Model

### Pairwise Preference

```
pairwise_preferences:
  id: int (primary key)
  scenario_id: int (FK to scenarios) - denormalized for query efficiency
  result_a_id: int (FK to results)
  result_b_id: int (FK to results)
  preference: enum
    - 'a_better': Result A is clearly better
    - 'b_better': Result B is clearly better
    - 'tie': Both are roughly equal quality
    - 'both_good': Both are excellent (can't distinguish)
    - 'both_bad': Both are poor (can't distinguish)
  confidence: float | null (0.0-1.0, optional)
  notes: str | null
  created_at: datetime
```

### Constraints
- `result_a_id < result_b_id` (canonical ordering to prevent duplicates)
- Both results must belong to the same scenario
- Only completed results can be compared

## Preference Options

| Preference | Meaning | Impact on Ranking |
|------------|---------|-------------------|
| `a_better` | A is clearly superior | A wins, B loses |
| `b_better` | B is clearly superior | B wins, A loses |
| `tie` | Roughly equal quality | 0.5 win for each |
| `both_good` | Both excellent, can't distinguish | 0.5 win each, both get quality boost |
| `both_bad` | Both poor, can't distinguish | 0.5 win each, both get quality penalty |

## Ranking Algorithm

### Simple Win Rate (v1)
For each result, calculate:
```
win_rate = (wins + 0.5 * ties) / total_comparisons
```

### Bradley-Terry Model (future)
Maximum likelihood estimation of "true" quality scores from pairwise comparisons.
Handles transitivity violations gracefully by finding the best-fit scores.

## Judge Alignment with Pairwise Data

### Pairwise Accuracy
For each human preference where A > B:
- Check if `judge_score(A) > judge_score(B)`
- Accuracy = correct_predictions / total_preferences

### Combined Alignment Score
```
alignment = w_abs * absolute_alignment + w_pair * pairwise_accuracy

where:
  w_abs = n_absolute_samples / (n_absolute_samples + n_pairwise_samples)
  w_pair = n_pairwise_samples / (n_absolute_samples + n_pairwise_samples)
```

This weights each type of data by its sample size.

## Smart Pair Selection

The comparison queue prioritizes pairs using these heuristics:

### 1. Coverage Balance
Prioritize scenarios with fewer pairwise comparisons.

### 2. Information Gain
Prioritize pairs that would add the most information:
- Pairs not yet compared
- Pairs where judge scores are close (harder, more informative)
- Results with few total comparisons

### 3. Ranking Uncertainty
Prioritize pairs where the ranking is uncertain:
- Results with similar win rates
- Results that could "flip" with one more comparison

## UI Design

### Comparison View
Two results displayed side-by-side:
```
┌─────────────────────────────────────────────────────────┐
│ Scenario: "Fix the login bug..."                        │
├─────────────────────┬───────────────────────────────────┤
│       Result A      │          Result B                 │
│  claude-sonnet-4-...│    gpt-4o                         │
│                     │                                   │
│  [Diff Viewer]      │    [Diff Viewer]                  │
│                     │                                   │
├─────────────────────┴───────────────────────────────────┤
│                                                         │
│  [A Better]  [Both Good]  [Tie]  [Both Bad]  [B Better] │
│                                                         │
│  Notes: [____________________________________________]  │
│                                                         │
│  Progress: 12/50 comparisons    Pairs remaining: 38     │
└─────────────────────────────────────────────────────────┘
```

### Keyboard Shortcuts
- `1` or `←`: A is better
- `2`: Both good
- `3`: Tie
- `4`: Both bad  
- `5` or `→`: B is better
- `S`: Skip

## Integration with Existing Systems

### Result Detail Page
- Show pairwise win/loss record
- Link to comparison history

### Analytics Matrix
- Option to show pairwise-derived rankings alongside absolute scores

### Judge Training
- Include pairwise accuracy in alignment metrics
- Use pairwise data for few-shot examples in judge prompts

## API Endpoints

```
POST /api/pairwise
  Create a new pairwise preference

GET /api/pairwise?scenario_id=X
  List pairwise preferences, optionally filtered

GET /api/pairwise/stats
  Overall pairwise statistics

GET /api/pairwise/next
  Get next pair to compare (smart selection)

GET /api/pairwise/rankings?scenario_id=X
  Get derived rankings for a scenario

DELETE /api/pairwise/{id}
  Delete a preference
```

## Future Enhancements

1. **Multi-annotator support**: Track who made each preference, compute inter-annotator agreement
2. **Active learning**: Use model uncertainty to select maximally informative pairs
3. **Bradley-Terry rankings**: More sophisticated ranking algorithm
4. **Preference explanations**: Structured reasons (e.g., "better code style", "more complete")
5. **Batch comparison**: Compare 3+ results at once for ranking

