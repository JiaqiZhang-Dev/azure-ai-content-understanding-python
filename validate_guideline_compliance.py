"""Validate extracted API knowledge against the official Azure SDK design guidelines.

The script combines Azure AI Search (to retrieve authoritative guidelines) and
Azure OpenAI (to reason over potential violations). It expects the raw analyzer
result JSON that is produced by ``archboard_review_meeting_processor.py`` and
writes a structured compliance report to disk.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import find_dotenv, load_dotenv

# Environment ---------------------------------------------------------------
load_dotenv(find_dotenv())
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# Data models --------------------------------------------------------------
@dataclass
class KnowledgeRecord:
    segment_id: str
    segment_topic: str
    title: str
    problem: str
    recommended_solution: str
    category: str
    start_timestamp: str
    end_timestamp: str
    summary_path: str


@dataclass
class GuidelineDocument:
    title: str
    content: str
    context_id: Optional[str]
    chunk_id: Optional[str]
    headers: Dict[str, Optional[str]]
    score: float
    raw: Dict[str, Any]


@dataclass
class ValidationFinding:
    record: KnowledgeRecord
    compliance_status: str
    explanation: str
    supporting_guidelines: List[Dict[str, Any]]


# Parsing helpers ----------------------------------------------------------
def _extract_value(field_obj: Any) -> Any:
    """Recursively unwrap analyzer field objects."""
    if not isinstance(field_obj, dict):
        return field_obj

    field_type = field_obj.get("type")
    if field_type == "array":
        return [_extract_value(item) for item in field_obj.get("valueArray", [])]
    if field_type == "object":
        return {k: _extract_value(v) for k, v in field_obj.get("valueObject", {}).items()}
    if field_type == "string":
        return field_obj.get("valueString", "")
    if field_type == "number":
        return field_obj.get("valueNumber")
    return field_obj.get("value", field_obj)


def load_knowledge_records(raw_result_path: Path, limit: Optional[int] = None) -> List[KnowledgeRecord]:
    logging.info("Loading analyzer result from %s", raw_result_path)
    with raw_result_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    base_name = raw_result_path.stem.replace("_raw_result", "")
    summary_path = raw_result_path.with_name(f"{base_name}_summary.md")

    contents = payload.get("result", {}).get("contents", [])
    if not contents:
        return []

    fields = contents[0].get("fields", {})
    segments_field = fields.get("Segments", {})
    segments_raw = _extract_value(segments_field)

    records: List[KnowledgeRecord] = []
    for segment in segments_raw or []:
        knowledges = segment.get("Knowledges", [])
        for knowledge in knowledges:
            record = KnowledgeRecord(
                segment_id=segment.get("SegmentId", "unknown"),
                segment_topic=segment.get("SegmentTopic", ""),
                title=knowledge.get("Title", ""),
                problem=knowledge.get("Problem", ""),
                recommended_solution=knowledge.get("RecommendedSolution", ""),
                category=knowledge.get("Category", ""),
                start_timestamp=knowledge.get("StartTimestamp", ""),
                end_timestamp=knowledge.get("EndTimestamp", ""),
                summary_path=str(summary_path),
            )
            records.append(record)
            if limit and len(records) >= limit:
                return records

    return records


# Azure AI Search client ---------------------------------------------------
class AzureSearchClient:
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        index_name: str,
        api_version: str = "2023-11-01",
        semantic_configuration: Optional[str] = None,
    ) -> None:
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]
        self.endpoint = endpoint
        self.api_key = api_key
        self.index = index_name
        self.api_version = api_version
        self.semantic_configuration = semantic_configuration

    def search(self, query: str, top: int = 5) -> List[GuidelineDocument]:
        url = f"{self.endpoint}/indexes/{self.index}/docs/search?api-version={self.api_version}"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }
        body: Dict[str, Any] = {
            "search": query,
            "top": top,
            "queryType": "semantic" if self.semantic_configuration else "simple",
            "select": "title,chunk,context_id,chunk_id,header_1,header_2,header_3,ordinal_position",
            "answers": "none",
            "captions": "extractive" if self.semantic_configuration else None,
        }
        body["filter"] = (
            "(context_id eq 'azure-sdk-guidelines') and "
            "((search.ismatch('python_*', 'title')) or (search.ismatch('general_*', 'title')))"
        )
        if not self.semantic_configuration:
            body.pop("captions")
        else:
            body["semanticConfiguration"] = self.semantic_configuration

        response = requests.post(url, headers=headers, json=body, timeout=30)
        response.raise_for_status()
        data = response.json()

        documents: List[GuidelineDocument] = []
        for doc in data.get("value", []):
            documents.append(
                GuidelineDocument(
                    title=doc.get("title", ""),
                    content=doc.get("chunk", doc.get("content", "")),
                    context_id=doc.get("context_id"),
                    chunk_id=doc.get("chunk_id"),
                    headers={
                        "header_1": doc.get("header_1"),
                        "header_2": doc.get("header_2"),
                        "header_3": doc.get("header_3"),
                    },
                    score=float(doc.get("@search.score", 0.0)),
                    raw=doc,
                )
            )
        return documents


# Azure OpenAI client ------------------------------------------------------
class AzureOpenAIClient:
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment: str,
        api_version: str = "2024-06-01",
        temperature: float = 0.1,
        max_tokens: int = 500,
    ) -> None:
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment = deployment
        self.api_version = api_version
        self.temperature = temperature
        self.max_tokens = max_tokens

    def review(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        url = (
            f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions"
            f"?api-version={self.api_version}"
        )
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": {"type": "json_object"},
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        message = result["choices"][0]["message"]["content"].strip()
        try:
            return json.loads(message)
        except json.JSONDecodeError:
            logging.error("Model response was not valid JSON: %s", message)
            raise


# Validator ----------------------------------------------------------------
class GuidelineValidator:
    SYSTEM_PROMPT = (
        "You are an Azure SDK design governance reviewer. "
        "Compare the extracted knowledge against the official Azure SDK design"
        " guidelines. "
        "Return JSON with `status` (Compliant, NeedsReview, Violation),"
        " `rationale`, and `referencedGuidelines` (array of {id|title|url})."
    )

    def __init__(
        self,
        search_client: AzureSearchClient,
        llm_client: AzureOpenAIClient,
        top_guidelines: int = 5,
    ) -> None:
        self.search_client = search_client
        self.llm_client = llm_client
        self.top_guidelines = top_guidelines

    def validate(self, record: KnowledgeRecord) -> ValidationFinding:
        query_bits = [record.title, record.problem, record.recommended_solution]
        query = " ".join(bit for bit in query_bits if bit).strip()
        guidelines = self.search_client.search(query or record.segment_topic, top=self.top_guidelines)

        guidelines_blob = []
        for idx, doc in enumerate(guidelines, 1):
            header_path = "/".join(
                [h for h in [doc.headers.get("header_1"), doc.headers.get("header_2"), doc.headers.get("header_3")] if h]
            )
            guidelines_blob.append(
                f"Guideline {idx}: {doc.title}\nContext: {doc.context_id or 'n/a'} | Headers: {header_path or 'n/a'}\n"
                f"Score: {doc.score:.2f}\n{doc.content}\nChunk ID: {doc.chunk_id or 'n/a'}"
            )
        if not guidelines_blob:
            guidelines_blob.append("No search results were returned. Use general Azure SDK design judgment.")

        user_prompt = f"""
Extracted knowledge from Azure AI Content Understanding:
Segment: {record.segment_id} - {record.segment_topic}
Category: {record.category}
Source window: {record.start_timestamp} - {record.end_timestamp}
Title: {record.title}
Problem statement: {record.problem}
Recommended solution: {record.recommended_solution}

Relevant Azure SDK guidelines from search:
{os.linesep.join(guidelines_blob)}

Classify whether the extracted knowledge conflicts with the official guidelines.
Output JSON with the schema described in the system instructions.
""".strip()

        llm_response = self.llm_client.review(self.SYSTEM_PROMPT, user_prompt)
        status = llm_response.get("status", "NeedsReview")
        rationale = llm_response.get("rationale", "")
        refs = llm_response.get("referencedGuidelines", [])

        supporting = []
        for ref in refs:
            if isinstance(ref, dict):
                supporting.append(ref)
            else:
                supporting.append({"title": str(ref)})

        return ValidationFinding(
            record=record,
            compliance_status=status,
            explanation=rationale,
            supporting_guidelines=supporting,
        )


# Reporting ----------------------------------------------------------------
def build_report(
    findings: List[ValidationFinding],
    input_path: Path,
    summary_path: Optional[str],
    search_index: str,
    output_dir: Path,
) -> Path:
    status_counts: Dict[str, int] = {}
    for finding in findings:
        status_counts[finding.compliance_status] = status_counts.get(finding.compliance_status, 0) + 1

    summary_file = Path(summary_path) if summary_path else None
    summary_base = (
        summary_file.stem
        if summary_file
        else input_path.stem.replace("_raw_result", "_summary")
    )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{summary_base}_validation.json"

    report = {
        "metadata": {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "inputFile": str(input_path),
            "summaryFile": str(summary_file) if summary_file else None,
            "searchIndex": search_index,
            "totalFindings": len(findings),
            "statusCounts": status_counts,
        },
        "items": [
            {
                "knowledge": asdict(finding.record),
                "complianceStatus": finding.compliance_status,
                "explanation": finding.explanation,
                "supportingGuidelines": finding.supporting_guidelines,
            }
            for finding in findings
        ],
    }

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    logging.info("Compliance report written to %s", output_path)
    return output_path


# CLI ----------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to a *_raw_result.json file or a directory containing such files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/validation"),
        help="Directory to write per-summary validation reports",
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional cap on number of knowledge items to validate")
    parser.add_argument("--top-guidelines", type=int, default=5, help="Number of Azure AI Search results to pass to the reviewer")
    return parser.parse_args()


def resolve_input_files(target: Path) -> List[Path]:
    if target.is_dir():
        files = sorted(target.glob("*_raw_result.json"))
        if not files:
            raise FileNotFoundError(f"No *_raw_result.json files found in {target}")
        return files
    if not target.exists():
        raise FileNotFoundError(f"Input path does not exist: {target}")
    return [target]


def resolve_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value


def main() -> None:
    args = parse_args()

    search_client = AzureSearchClient(
        endpoint=resolve_env("AZURE_SEARCH_ENDPOINT"),
        api_key=resolve_env("AZURE_SEARCH_API_KEY"),
        index_name=resolve_env("AZURE_SEARCH_INDEX"),
        semantic_configuration=os.getenv("AZURE_SEARCH_SEMANTIC_CONFIG"),
    )
    llm_client = AzureOpenAIClient(
        endpoint=resolve_env("AOAI_CHAT_COMPLETIONS_ENDPOINT"),
        api_key=resolve_env("AOAI_CHAT_COMPLETIONS_API_KEY"),
        deployment=resolve_env("AOAI_CHAT_COMPLETIONS_DEPLOYMENT"),
        api_version=os.getenv("AOAI_CHAT_COMPLETIONS_API_VERSION", "2024-06-01"),
    )
    validator = GuidelineValidator(search_client, llm_client, top_guidelines=args.top_guidelines)

    raw_result_files = resolve_input_files(args.input)
    for raw_file in raw_result_files:
        records = load_knowledge_records(raw_file, limit=args.limit)
        if not records:
            logging.warning("No knowledge items found in %s", raw_file)
            continue

        findings: List[ValidationFinding] = []
        for idx, record in enumerate(records, 1):
            logging.info("[%s] Validating knowledge item %d/%d", raw_file.name, idx, len(records))
            try:
                findings.append(validator.validate(record))
            except Exception as exc:  # noqa: BLE001
                logging.error("Validation failed for segment %s (%s): %s", record.segment_id, record.title, exc)

        if not findings:
            logging.warning("No findings produced for %s; check logs for earlier errors", raw_file)
            continue

        summary_path = records[0].summary_path if records else None
        build_report(findings, raw_file, summary_path, search_client.index, args.output_dir)


if __name__ == "__main__":
    main()
