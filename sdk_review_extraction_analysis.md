# Improving AI-Extracted SDK API Review Guidelines

## Background

We use an AI pipeline to extract reusable API/SDK design guidelines from architect review meeting recordings. The pipeline:

1. **`archboard_review_meeting_processor.py`** — Uses Azure Content Understanding with a custom analyzer template (`review_meeting_processor.json`) to segment meetings and extract "Knowledges" (Problem/Solution/Category)
2. **`process_review_meeting_result.py`** — Converts raw JSON output into markdown summary files
3. **`validate_guideline_compliance.py`** — Uses Azure AI Search + Azure OpenAI to validate extracted knowledge against official Azure SDK design guidelines

An architect reviewed the extracted output and provided detailed feedback. This document analyzes the feedback and proposes improvements.

**Reference**:
- Extracted doc: [Content Understanding review summary](https://github.com/JiaqiZhang-Dev/azure-ai-content-understanding-python/blob/da889abe3aa6585f471e9e57773e4e9abde59e42/output/Azure_SDK_Review___Beta_SDK_for_Azure_AI_Content_Understanding_20250820_140608_Meeting_Recording_summary.md)
- Pipeline repo: [azure-ai-content-understanding-python](https://github.com/JiaqiZhang-Dev/azure-ai-content-understanding-python/tree/da889abe3aa6585f471e9e57773e4e9abde59e42)

### Platform Constraints

The extraction step runs on **Azure Content Understanding** (`prebuilt-videoAnalyzer`), a managed service that performs speech-to-text, visual analysis, and structured extraction in a single pass. This is not a freely tunable LLM prompt — key constraints include:

- **Field description limit**: Each field's `description` is capped at **1,024 characters**. Current descriptions already use 400–600 chars, limiting how much instruction can be packed into a single field.
- **Video-first model**: The underlying model excels at extracting content from video/audio. It is less suited for nuanced domain-specific *classification* tasks (e.g., distinguishing "client SDK" from "REST API" design) that require expert knowledge not present in the video.
- **No strict field count limit**: Additional fields can be added, but more fields per Knowledge item increases the extraction burden and may degrade output quality on other fields.

These constraints directly inform which improvements belong in the analyzer template vs. a post-processing step.

---

## Architect Feedback Summary

> **TLDR** — The evaluation has extracted some interesting and useful info but it seems to be struggling to filter the guidance into advice that is generally applicable across services, and is actionable specifically in a client SDK.

### Positive Examples
- "Avoid Ambiguous String-Based Parameters" (Storage)
- "Avoid Using Strings for Byte Data" (Storage)
- "Differentiate API Endpoints for URL and Binary Data" (Content Understanding)
- "Add Overloads for Mutually Exclusive Parameters" (Content Understanding)

### Issues Identified
1. REST API design vs client SDK API design guidance mixed together
2. Service-specific advice presented as universally applicable
3. Some guidelines are incorrect (e.g., LRO handling recommends status-checking APIs instead of poller rehydration)
4. Some recommendations lack context to be actionable
5. Code generation issues mixed in
6. Duplicates and overlap between guidelines
7. Forced before/after code snippets are sometimes arbitrary
8. Non-API/SDK content included (e.g., "Managing Large API Repositories")
9. Vague actions like "brainstorm solutions" instead of concrete recommendations
10. Some entries read like meeting summary notes, not guidelines

---

## Root Cause Analysis

| # | Architect Feedback | Root Cause Stage |
|---|---|---|
| 1 | REST API vs Client SDK guidance mixed | **Extraction prompt** — no classification axis |
| 2 | Service-specific advice presented as universal | **Extraction prompt** — forces generalization |
| 3 | Some guidelines are incorrect (e.g., LRO) | **No expert knowledge grounding** during extraction |
| 4 | Insufficient context to apply recommendations | **Extraction prompt** — strips context too aggressively |
| 5 | Code gen issues mixed in | **Extraction prompt** — no exclusion filter |
| 6 | Duplicates and overlap | **No deduplication** post-processing |
| 7 | Forced before/after code not always appropriate | **Extraction prompt** — makes code snippets mandatory |
| 8 | "Manage Threading" — arbitrary examples | **Extraction prompt** — forces code snippets |
| 9 | Non-API/SDK content (repo management, etc.) | **Extraction prompt** — Category filter too loose |
| 10 | Vague actions ("brainstorm solutions") | **Extraction prompt** — no quality gate |
| 11 | Reads like meeting notes, not guidelines | **Extraction prompt** — insufficient framing |

**Key Insight**: ~8 of 11 issues trace back to the **extraction prompt** (`review_meeting_processor.json`). The remaining 3 need **post-processing steps**. However, due to platform constraints (see above), only a subset of prompt-level fixes are suitable for the analyzer template — the rest are better addressed by a post-processing classification pass using a text-based LLM.

---

## Proposed Improvements

### Layer 1: Improve the Extraction Prompt (Analyzer Template)

The analyzer template can be improved, but changes must respect the platform constraints. Classification fields (Scope, Applicability, Confidence) are moved to Layer 2 where a text-based LLM can perform them more reliably on already-extracted text.

#### A. Make code snippets optional

Current `RecommendedSolution` description:
> "Provide generic BEFORE/AFTER code examples"

Proposed:
> "If a clear BEFORE/AFTER code pattern exists, include it. If the guideline is about a design principle or process that doesn't have a simple code representation, describe the principle without forcing code examples. Not all guidelines need code snippets."

**Fixes**: Issues 7, 8.

#### B. Add `SourceContext` field

The video understanding model is well-suited to summarize what it heard/saw — this is content extraction, not domain classification.

```json
"SourceContext": {
  "type": "string",
  "method": "generate",
  "description": "Brief description of the specific scenario/service that triggered this discussion. E.g., 'Discussion about Content Understanding SDK where models return JSON strings instead of typed objects'. This helps readers understand the original context without which the guideline may be hard to apply."
}
```

**Fixes**: Issue 4 — preserves context so guidelines are understandable.

#### C. Add explicit exclusion rules

Add to the `Knowledges` array description. Note: the combined description (existing + exclusions) must stay under the **1,024-character limit**. The version below is trimmed to fit (~810 chars total):

```
"Do NOT extract the following as guidelines:
 - Meeting logistics, scheduling, or process discussions
 - Service-specific usage tips (how to use a particular service feature)
 - Items with no concrete, actionable recommendation
 - Items where the action is 'brainstorm', 'discuss further', or 'explore'
 - Repository management, CI/CD, or operational concerns
 - Demo walkthroughs or hero scenario presentations without design feedback"
```

**Fixes**: Issues 8, 9, 10, 11.

> **Note on Scope/Applicability/Confidence fields**: These were originally proposed as analyzer template fields but have been moved to Layer 2. The video understanding model extracts content from spoken conversation — distinguishing "client SDK" vs "REST API" vs "codegen" requires Azure SDK domain expertise that is more reliably applied by a text-based LLM operating on the extracted text. Similarly, Confidence self-assessment is unreliable in a structured extraction model (the LRO issue was the model being *confidently wrong*, not low-confidence).

---

### Layer 2: Add a Post-Processing Refinement Pass

A new script between `process_review_meeting_result.py` and the final output. This layer leverages a text-based LLM (Azure OpenAI) which is better suited for domain-specific classification than the video understanding model.

#### A. Classification and quality gate pass (NEW)

A single LLM call per guideline that performs both classification and quality filtering on the already-extracted text. This replaces the original plan of adding Scope/Applicability/Confidence fields to the analyzer template, where the video understanding model lacks the domain expertise to classify reliably.

For each extracted guideline, use an LLM to:

**Classify:**
```
Given this extracted guideline:
  Title: {title}
  Problem: {problem}
  Solution: {solution}
  SourceContext: {source_context}

Classify the following:
1. Scope: 'CLIENT_SDK' | 'REST_API' | 'CODE_GENERATION' | 'SERVICE_SPECIFIC'
2. Applicability: 'UNIVERSAL' | 'CONDITIONAL (describe which)' | 'SERVICE_SPECIFIC'
3. Confidence: 'HIGH' | 'MEDIUM' | 'LOW'
```

**Filter (quality gate):**
```
Answer YES/NO:
1. Is this about CLIENT SDK API surface design (not REST API, not code gen)?
2. Is the recommendation concrete and actionable (not "brainstorm" or "discuss")?
3. Would a developer know exactly what to do differently after reading this?
4. Is this generalizable beyond the specific service discussed?

If any answer is NO, mark as FILTERED with the reason.
```

Combining both into a single prompt keeps cost manageable (~50 LLM calls for 5 recordings × ~10 guidelines each).

**Fixes**: Issues 1, 2, 5, 9, 10, 11.

#### B. Accuracy cross-check (enhance existing validation)

The existing `validate_guideline_compliance.py` already checks against official guidelines. Enhance to also:
- Flag guidelines that **contradict** official guidance (the LRO issue)
- Distinguish "new insight not in guidelines" (valuable!) from "conflicts with guidelines" (dangerous)
- Mark contradictions with `CONTRADICTION` status for mandatory human review

This is the **only fix for Issue 3** (incorrect guidelines). No analyzer template change can address this — it requires cross-referencing extracted content against authoritative sources.

**Fixes**: Issue 3.

#### C. Deduplication across recordings

After processing multiple recordings, use simple text similarity (e.g., `difflib.SequenceMatcher` on Title + Problem text) to identify near-duplicates. At the current scale of ~5 recordings, this is sufficient. An embedding-based approach can be considered later if the corpus grows significantly (50+ recordings).

For each cluster of similar guidelines:
1. Note frequency ("Seen in 3/5 reviews")
2. Keep the most complete version as the canonical guideline
3. Merge any unique details from duplicates into the canonical version

**Fixes**: Issue 6.

#### D. Context enrichment

For guidelines marked as lacking context:
- Pull in the original transcript snippet using timestamps (already available in `transcriptPhrases` from the raw result JSON)
- Add a "When to apply" section derived from the service category
- If the item has no clear solution, apply default: "Consult the SDK architecture team for service-specific guidance"

**Fixes**: Issues 4, 10.

---

### Layer 3: Restructure the Output Format

#### A. Tiered output

```markdown
## Tier 1: Confirmed Universal Guidelines
High confidence, cross-service, applicable to any Azure SDK.

## Tier 2: Conditional Guidelines
Applies to specific scenarios (e.g., services with LROs, file-handling APIs).

## Tier 3: Emerging Patterns
Seen only once, interesting but needs more evidence from other reviews.

## Appendix: Service-Specific Notes
Interesting discussion, but not generalizable as SDK guidance.
```

#### B. Flexible guideline structure

Not all items need before/after code. Proposed structure:

```markdown
### Guideline: Avoid Ambiguous String-Based Parameters
- **Scope**: Client SDK  |  **Applicability**: Universal  |  **Confidence**: High
- **Seen in**: 3 reviews (Storage, Content Understanding, Language)
- **Original Context**: Discussed during Storage review regarding blob metadata keys...
- **Problem**: [description]
- **Recommendation**: [description]
- **Code Example** *(if applicable)*: [BEFORE/AFTER only when a clear pattern exists]
- **Default Action**: If unsure how to apply → consult the SDK architecture team.
```

#### C. Default action for vague items

Instead of allowing "brainstorm solutions" as a recommendation:

> If the guideline doesn't have a clear actionable solution, the default recommendation is: **"Consult the SDK architecture team for service-specific guidance on this topic."**

---

### Layer 4: Downstream Code Changes (Required)

Adding new fields to the analyzer template or post-processing output is not useful unless the consuming scripts are updated.

#### A. Update `process_review_meeting_result.py`

Currently reads only `Title`, `Problem`, `RecommendedSolution`, `Category`, and timestamps from each Knowledge item. Must be updated to:
- Parse and render `SourceContext` (from Layer 1B)
- Parse and render `Scope`, `Applicability`, `Confidence` (from Layer 2A post-processing output)
- Implement the tiered output format (Layer 3A) using classification results
- Support flexible guideline structure with optional code snippets (Layer 3B)

#### B. Update `validate_guideline_compliance.py`

The `KnowledgeRecord` dataclass has fixed fields (`segment_id`, `segment_topic`, `title`, `problem`, `recommended_solution`, `category`, `start_timestamp`, `end_timestamp`, `summary_path`). Must be updated to:
- Add `source_context` field
- Add `scope`, `applicability`, `confidence` fields (from post-processing)
- Update the validation prompt to leverage these new fields for better accuracy checking

---

### Evaluation Framework

The proposed changes need measurable success criteria to avoid iterating blindly.

#### Metrics to track
- **Precision**: % of Tier 1 guidelines that an architect rates as correct and useful (target: >80%)
- **Filter rate**: % of extracted items filtered out by the quality gate (healthy range: 20–40%; if >50%, extraction is too noisy; if <10%, the filter isn't working)
- **Contradiction rate**: % of items flagged as contradicting official guidelines (target: 0% in Tier 1 after human review)
- **Default-action rate**: % of items falling back to "consult the architecture team" (target: <10%; higher means the pipeline isn't generating enough actionable guidance)

#### Evaluation process
1. After implementing Phase 1+2, re-run the pipeline on the same 5 recordings
2. Have the architect re-score a sample of the output using the same criteria as the original feedback
3. Compare precision/filter rates against the baseline (current output)

---

## Priority Summary

| Priority | Change | Effort | Impact | Fixes |
|----------|--------|--------|--------|-------|
| 🔴 P0 | Make code snippets optional in analyzer template (1A) | Low | High | Issues 7, 8 |
| 🔴 P0 | Add exclusion rules to Knowledges description (1C) | Low | High | Issues 8, 9, 10, 11 |
| 🔴 P0 | Add SourceContext field to analyzer template (1B) | Low | Medium | Issue 4 |
| 🟡 P1 | Add classification + quality gate post-processing pass (2A) | Medium | High | Issues 1, 2, 5, 9, 10, 11 |
| 🟡 P1 | Accuracy cross-check with contradiction detection (2B) | Medium | High | Issue 3 |
| 🟡 P1 | Update downstream scripts for new fields (4A, 4B) | Medium | Required | Enables all above |
| 🟢 P2 | Deduplication with simple text similarity (2C) | Low | Medium | Issue 6 |
| 🟢 P2 | Context enrichment from transcript (2D) | Low | Medium | Issues 4, 10 |
| 🟢 P2 | Tiered output format with flexibility (3A, 3B, 3C) | Medium | Medium | Overall UX |

### Recommended phasing

1. **Phase 1** (P0 — analyzer template): Apply 1A, 1B, 1C. Low effort, no new scripts needed.
2. **Phase 2** (P1 — post-processing): Build the classification + quality gate script (2A), enhance validation for contradictions (2B), and update downstream scripts (4A, 4B).
3. **Phase 3** (P2 — polish): Add deduplication (2C), context enrichment (2D), and tiered output formatting (3A–3C).

**Biggest bang for the buck**: The P0 template changes are low-effort quick wins, but the **P1 post-processing classification pass (2A)** is the most impactful single change — it addresses 6 of 11 issues and works on already-extracted text where a text-based LLM can apply domain expertise reliably.
