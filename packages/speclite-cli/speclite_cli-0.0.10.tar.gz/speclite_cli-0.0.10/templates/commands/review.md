---
description: Review the implementation for the current feature (ideally with a different AI agent).
scripts:
  sh: .speclite/scripts/check-prerequisites.sh --json
  ps: .speclite/scripts/check-prerequisites.ps1 -Json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Steps

1. **Setup**: Run `{SCRIPT}` from repo root and parse JSON for FEATURE_DIR.
   - All file paths must be absolute.
   - For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load feature context**: Read from FEATURE_DIR:
   - **Required**: spec.md (user stories with priorities) and any files it references
   - **Forbidden**: DO NOT read research.md, plan.md, or tasks.md. These files describe the implementation plan, but you MUST ignore them, only looking at the actual implemenation
   and deciding independently how well it implements the spec.

3. **Review the implmentation**:
    1. Parse any user instructions from `$ARGUMENTS` input. Combine those instructions with the steps here.
    2. Review all of the changes made in the current branch, both those already committed in the branch and any uncomitted changes.
       Determine how well those changes implement the feature spec. Flag anything that:
         - looks incorrect
         - is missing
         - could be better implemented in an alternate way
         - looks redundant, that would be better to combine with other code

4. **Report the findings**:
   - Write the review findings to a review.md file in the FEATURE_DIR directory
   - Follow the template defined in `.speclite/templates/review-template.md`
   - Categorize the review findings in whatever categories you think most appropriate. If you categorize by priority, list highest priority items first.
   - Review findings needing to be addressed should be numbered sequentially for easy reference, starting with RF001
   - Review findings that look good shouldn't be numbered
   - Add comments or findings inline
   - Include links to relevant resources or documentation
