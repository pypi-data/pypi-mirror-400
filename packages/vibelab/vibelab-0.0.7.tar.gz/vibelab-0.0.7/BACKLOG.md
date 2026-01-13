# Backlog

This file serves a simple text-based backlog useful for maintaining lists of features and bugs. Text format means native LLM integration.



- [ ] BUG: When clicking "re-judge" on the judge configuration, there is no feedback despite the judges starting. instead, the button should change to some in progress indication
- [ ] BUG: Pricing is still broken for Cursor and openai
- [ ] BUG: it looks like repo descriptions are not getting captured.
- [ ] BUG: when running all missing items in a row of a dataset, the judge is not automatically applied (it should be)
- [ ] BUG: if I ctrl-c the process while there are active jobs or queued items, i should emit a message: "cancelling queued items, waiting for active jobs to finish, press ctrl-c again to force quit active jobs and mark as failed" (and make it work that way)

- [ ] DESIGN: The header metrics in the dashboard should be turned into a metric panel. The tiling is a bad use of space and does not look great at different screen widths
- [ ] DESIGN: the comparison matrix needs a data-oriented re-design and audit of the metric calculation algorithm - we should weight scores based on alignment, average per cell, and show relative scoring. we should emphasize time a lot more
- [ ] Design: instead of tiles, the admin page should be organized by tabs

- [ ] Feature: the `Version History` table of the judge drawer should allow users to click on older judges to view their values
- [ ] Feature: review queue that prompts the human to review the results to create better aligned judges
- [ ] Feature: the SQLite query section of the admin tool should automatically add a conditional clause filtering to the current project when printing the default select statements.
- [ ] Feature: we should be able to do pairwise scoring and analysis of scenarios
- [ ] Feature: bulk import of commits
- [ ] Feature: repo-filter instead of dataset filter
- [ ] Feature: implement a modal runner
- [ ] Feature: executable tests/evaluators
- [ ] Feature: Improve judge creating

- [ ] Devex: get fmt, lint, type check, test working in github