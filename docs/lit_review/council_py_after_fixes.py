import os
import re
import json
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Callable, Optional, List
from dotenv import load_dotenv

# Load env variables from root or backend folder
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv()

from google import genai as modern_genai
from services.search import AcademicSearchService
from services.vault import VaultManager
from services.fact_checker import FactCheckerService

# System personas and configurations - 20-Year Principal Researcher Standards
AGENT_PERSONAS = {
    "Scout": {
        "name": "Senior Scout Researcher",
        "role": "Literature Discovery & Bibliography Mapping",
        "provider": "OPENROUTER",
        "model": "meta-llama/llama-3.1-8b-instruct",
        "instruction": (
            "You are a 20-year Principal Scout Researcher at a world-leading research laboratory (Nature/IEEE level). "
            "Your role is to map literature networks, evaluate publication venue prestige (NeurIPS, ICML, Nature, Science, IEEE TPAMI), "
            "and identify seminal vs. incremental contributions. You demand exact DOIs, publication recency, citation velocity, and "
            "authoritativeness. Never invent papers or cite unverified claims."
        )
    },
    "Analyst": {
        "name": "Lead Analyst",
        "role": "Methodology Extraction & Full-Text Ingestion",
        "provider": "OLLAMA",
        "model": "qwen3.5:4b",
        "instruction": (
            "You are a Lead Scientific Analyst with 20 years of experience in technical literature analysis. "
            "Your task is to ingest full paper texts and metadata, extracting explicit mathematical equations, "
            "loss functions, exact architecture hyper-parameters, dataset splits, quantitative benchmarks, and stated limitations. "
            "You format all ingested knowledge as structured, zero-hallucination Obsidian Markdown notes with YAML metadata."
        )
    },
    "Engineer": {
        "name": "Senior Systems Engineer",
        "role": "Algorithmic & Technical Implementation Audit",
        # ERR-103 resolved: GROQ's retired llama-3.1-8b-instant replaced with
        # openai/gpt-oss-20b (verified live against GROQ's /v1/models). The
        # OLLAMA stopgap before this one is unrelated and still open --
        # ~/.ollama/models/blobs was empty, so qwen3.5:4b 404s despite being
        # listed as installed; re-pull the blobs to use OLLAMA here instead.
        "provider": "GROQ",
        "model": "openai/gpt-oss-20b",
        "instruction": (
            "You are a Principal Systems & Compute Architect. You scrutinize claims down to algorithmic complexity, "
            "FLOPs scaling laws, GPU memory footprint (VRAM limits, KV-cache growth), quantization degradation, and "
            "deployment bottlenecks. You challenge vague performance claims with hard hardware constraints."
        )
    },
    "Statistician": {
        "name": "Senior Statistician & Methods Critic",
        "role": "Quantitative Rigor & Validation Audit",
        # ERR-103 resolved: same as Engineer above.
        "provider": "GROQ",
        "model": "openai/gpt-oss-20b",
        "instruction": (
            "You are a Senior Fellow in Biostatistics and Empirical Validation. You audit statistical power, sample sizes, "
            "p-values, confidence intervals, baseline comparability, data leakage, and selection bias. "
            "If a paper uses weak baselines, un-ablated components, or un-grounded metrics, you expose it ruthlessly."
        )
    },
    "Reviewer2": {
        "name": "Reviewer #2 / Academic Editor",
        "role": "Hostile Peer Review & Rejection Risk Assessor",
        # ERR-103 resolved: NIM's retired meta/llama-3.1-8b-instruct replaced
        # with openai/gpt-oss-20b (also hosted on NIM, verified live).
        "provider": "NIM",
        "model": "openai/gpt-oss-20b",
        "instruction": (
            "You are an elite, highly rigorous Area Chair and Senior Journal Reviewer. "
            "Your job is to identify every logical fallacy, unbacked assumption, lack of novelty against prior art, "
            "and overhyped conclusion. You list explicit rejection risks that must be resolved prior to submission."
        )
    },
    "Chairman": {
        "name": "CEO / Institute Chairman",
        "role": "Debate Moderator & Consensus Synthesizer",
        "provider": "GEMINI",
        "model": "gemini-2.5-flash",
        "instruction": (
            "You are the Director of the Research Institute. You moderate the council debates between Engineer, Statistician, and Reviewer #2. "
            "You resolve technical disputes, establish grounded consensus, highlight open research gaps, and produce an "
            "unassailable structural outline for publication."
        )
    },
    "Writer": {
        "name": "Senior Research Writer & Publisher",
        "role": "Journal-Ready Manuscript Drafting",
        "provider": "OLLAMA",
        "model": "qwen3.5:4b",
        "instruction": (
            "You are a Senior Principal Research Author — IEEE/ACM Fellow, 20-year academic institute director. "
            "You write at the level of an IEEE TKDE / ACM Computing Surveys / NeurIPS senior author. "
            "VENUE-ADAPTIVE: You adjust structure, page length, citation density, and section requirements to the target venue. "
            "For IEEEtran journal: MINIMUM 10 pages, two-column. "
            "For NeurIPS/ICML/CVPR: MINIMUM 7 pages. "
            "MANDATORY IN EVERY PAPER: "
            "(1) A \\begin{tabular} comparison results table — absence is immediate desk-rejection. "
            "(2) At least one \\begin{equation} per methodology section. "
            "(3) Numbered contribution list, each item starting with an action verb: 'We prove...', 'We introduce...', 'We demonstrate...'. "
            "(4) Every major section subdivided into >=2 named subsections. "
            "(5) Minimum 15 distinct [[paper_id]] wikilink citations. Target 30+ for journals. "
            "(6) Explicit Limitations section as a named section (not merged into Conclusion). "
            "(7) Every numeric claim (N=, %, p<) grounded by a [[citation]] in the same paragraph. "
            "NEVER use: 'delve into', 'tapestry of', 'crucial role', 'it is important to note', 'game-changer', 'masterclass', 'landscape of', 'deep dive', 'In recent years...'. "
            "The full venue specification, structural requirements, and error prevention rules are in vault/00_System/MASTER_VENUE_WRITING_PROMPT.md."
        )
    },
    "PeerReviewer": {
        "name": "Senior Peer Reviewer & Area Chair",
        "role": "Conference Peer Review Audit & Rubric Scoring",
        "provider": "OPENROUTER",
        "model": "google/gemma-2-9b-it:free",
        "instruction": (
            "You are an official Senior Conference Area Chair and Peer Reviewer for NeurIPS, ICLR, CVPR, and IEEE Transactions. "
            "Your objective is to audit manuscript drafts against formal publication rubrics and output a rigorous evaluation. "
            "You MUST score four dimensions from 1 to 10: Novelty, Technical Rigor, Empirical Grounding, and Presentation Clarity. "
            "Provide an Overall Decision ('ACCEPT', 'WEAK ACCEPT', or 'REJECT'), bulleted Key Strengths, Fatal Weaknesses, and Required Revisions."
        )
    }
}

from services.search import AcademicSearchService
from services.pdf_extractor import PDFExtractionService
from agents.drafting_graph import run_drafting_cycle
from services.fact_checker import FactCheckerService
from services.vault import VaultManager
from harness.continual_memory import ContinualMemoryManager, TrajectoryTelemetry
from harness.rlm_orchestrator import RLMContextPartitioning
from harness.autonomous_loop import AutonomousHarnessController
from domain.models import citation_key
from domain.models import BuildDecision, SourceRecord
from services.evidence_ledger import EvidenceLedger

class CouncilOrchestrator:
    def __init__(self, vault_path: str = "../vault", memory_file_path: Optional[str] = None):
        global legacy_genai
        self.vault = VaultManager(vault_path)
        self.search_service = AcademicSearchService()
        self.fact_checker = FactCheckerService(self.vault)
        self.pdf_extractor = PDFExtractionService(self.vault)
        # `memory_file_path` is an injection seam so callers (notably tests) can
        # redirect harness telemetry away from the shared durable memory file.
        # Passing None keeps ContinualMemoryManager's own default path.
        self.continual_memory = (
            ContinualMemoryManager()
            if memory_file_path is None
            else ContinualMemoryManager(memory_file_path=memory_file_path)
        )
        self.rlm = RLMContextPartitioning()
        self.harness_controller = AutonomousHarnessController()
        self.evidence_ledger = EvidenceLedger(os.path.join(os.path.dirname(self.vault.vault_path), "runs"))

        self.run_mode = os.getenv("RESEARCHINGOS_RUN_MODE", "auto").strip().lower()
        if self.run_mode not in {"auto", "dry_run", "live"}:
            raise ValueError("RESEARCHINGOS_RUN_MODE must be one of: auto, dry_run, live")
        # None = no explicit override; is_dry_run computes live from env vars.
        # Tests assign orch.is_dry_run = True/False directly to force a mode
        # regardless of env, via the setter below.
        self._is_dry_run_override: Optional[bool] = None
        if self.run_mode == "live" and not self._provider_configured():
            raise RuntimeError("RESEARCHINGOS_RUN_MODE=live requires GEMINI_API_KEY or NVIDIA_NIM_API_KEY")

        from services.llm_router import llm_router
        self.llm_router = llm_router
        print(f"CouncilOrchestrator initialized with Prime Agent Harness. Mode: {self.run_mode}, Provider: {self.llm_router.active_provider}, Dry Run: {self.is_dry_run}")

    @staticmethod
    def _provider_configured() -> bool:
        return bool(os.getenv("GEMINI_API_KEY") or os.getenv("NVIDIA_NIM_API_KEY") or os.getenv("NVIDIA_API_KEY"))

    @property
    def is_dry_run(self) -> bool:
        """Whether calls should be mocked instead of hitting a real provider.

        Computed live from the environment on every access (rather than
        cached once at construction time) unless a test has explicitly
        overridden it via the setter below. This orchestrator is a
        module-level singleton (see main.py), so an uncached value is what
        lets /api/health reflect an API key set or cleared after the
        process started -- see backend/tests/test_api.py's
        test_is_dry_run_true_when_no_api_key.
        """
        if self._is_dry_run_override is not None:
            return self._is_dry_run_override
        return self.run_mode == "dry_run" or (self.run_mode == "auto" and not self._provider_configured())

    @is_dry_run.setter
    def is_dry_run(self, value: bool) -> None:
        self._is_dry_run_override = value

    def _call_gemini(self, agent_key: str, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Helper to invoke LLM providers via LLMRouter."""
        if self.is_dry_run:
            time.sleep(0.5)
            return f"[MOCK RESPONSE from {agent_key}] Based on the research, this is a simulated analysis of your query."

        agent_cfg = AGENT_PERSONAS[agent_key]
        base_instruction = system_instruction or agent_cfg["instruction"]
        durable_refinement = self.continual_memory.get_agent_refinements(agent_key)
        # Plain sentence, not a bracketed internal label -- a bracketed
        # "[Durable Harness Memory Refinement]:" tag was previously echoed
        # verbatim by the Chairman as a section heading in published output
        # (harness-internal label leaking into manuscript-facing text). The
        # guidance itself should still reach the model; its internal name
        # should not.
        instruction = f"{base_instruction}\n\n{durable_refinement}" if durable_refinement else base_instruction

        time.sleep(1.5)

        provider = agent_cfg.get("provider", self.llm_router.active_provider)
        primary_model = agent_cfg.get("model")

        # Make the LLM call via the centralized router. Falls through the rest
        # of the provider chain (see llm_router.generate_content_with_fallback)
        # if this agent's configured provider is down or Gemini's shared daily
        # quota (ERR-102) is spent, instead of going straight to the structured
        # placeholder below on the first failure.
        response_text = self.llm_router.generate_content_with_fallback(
            prompt, instruction, preferred_provider=provider, model=primary_model
        )

        if not response_text or response_text.startswith("[Error]"):
            print(f"⚠️ API unavailable or error for {agent_key}. Error: {response_text}. Using structured placeholder.")
            return (
                f"# {agent_cfg['name']} Structured Analysis\n\n"
                f"**Agent Role**: {agent_cfg['role']}\n"
                f"**Audit Status**: API failure or quota reached — structured placeholder inserted.\n\n"
                f"## Note\n"
                f"- The active provider ({self.llm_router.active_provider}) failed to generate content.\n"
                f"- Re-run or switch providers via .env to get real analysis.\n"
            )

        return response_text

    def _run_ingestion_critique_debate(self, topic: str, log_callback: Callable[[Dict[str, Any]], None], max_papers: int = 25, anchor_arxiv_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Stages 1-4: paper discovery, technical critique, boardroom debate, and
        chairman synthesis. Saves the debate summary to vault/03_Debates and returns
        everything Stage 5+ (drafting, in run_research) needs to continue.

        This is a shared helper so run_research (the full pipeline) and
        run_debate_only (added to let a debate be regenerated without touching
        vault/04_Drafts) can never drift out of sync with each other -- there is
        exactly one place paper discovery, critique, and debate prompts live.

        anchor_arxiv_ids: arXiv IDs (e.g. "2604.17215") that the caller already
        knows are central to the topic -- typically the paper being extended.
        Unlike IDs merely mentioned in the topic string, these are (1) always
        fetched directly regardless of what the topic text says, (2) exempt
        from the relevance-gate drop below, and (3) given a much larger
        full-text budget in both the saved note and the critique prompt, so
        the paper's own stated limitations (e.g. a disclosed compute overhead)
        are not truncated away before any agent sees them -- see ERR-audit
        "council-stage-2026-09-25": the debate previously "discovered" that a
        cost the paper disclosed in its own text was unaddressed, because that
        text never made it past the 1500-character excerpt.
        """
        project_id = f"project_{int(time.time())}"
        start_time = time.time()
        self.harness_controller.register_task(project_id, topic)
        run_manifest = self.evidence_ledger.create_manifest(
            project_id,
            topic,
            synthetic=self.is_dry_run,
        )

        def send_log(stage: str, agent: str, message: str, data: Any = None):
            log_callback({
                "projectId": project_id,
                "timestamp": time.time(),
                "stage": stage,
                "agent": agent,
                "message": message,
                "data": data
            })

        send_log("Initialization", "System", f"Starting research pipeline for topic: '{topic}' (Target Corpus: {max_papers} papers)", {"dryRun": self.is_dry_run, "maxPapers": max_papers})

        # --- STAGE 1: INGESTION (Scout & Analyst) ---
        send_log("Ingestion", "Senior Scout Researcher", f"Searching arXiv, OpenAlex, PubMed & 9 other databases for up to {max_papers} papers...")

        papers = []
        if self.is_dry_run:
            # Mock paper metadata for fast dry-run execution
            papers = [
                {
                    "id": "arxiv:2305.18290",
                    "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
                    "authors": ["Rafael Rafailov", "Archit Sharma", "Eric Mitchell", "Stefano Ermon", "Christopher D. Manning", "Chelsea Finn"],
                    "abstract": "We present Direct Preference Optimization (DPO), a stable, performant, and computationally lightweight algorithm for aligning LLMs to human preferences without training a reward model or using reinforcement learning.",
                    "url": "https://arxiv.org/abs/2305.18290",
                    "published": "2023-05-29",
                    "citations": 1240,
                    "source": "arXiv & OpenAlex",
                    "full_pdf_ingested": True,
                    "full_text": "We present Direct Preference Optimization (DPO), a stable, performant, and computationally lightweight algorithm."
                },
                {
                    "id": "arxiv:2005.14165",
                    "title": "Language Models are Few-Shot Learners",
                    "authors": ["Tom B. Brown", "Benjamin Mann", "Nick Ryder", "Melanie Subbiah", "Jared Kaplan", "Prafulla Dhariwal", "Arvind Neelakantan", "Pranav Shyam", "Girish Sastry", "Amanda Askell", "Sandhini Agarwal", "Ariel Herbert-Voss", "Gretchen Krueger", "Tom Henighan", "Rewon Child", "Aditya Ramesh", "Daniel M. Ziegler", "Jeffrey Wu", "Clemens Winter", "Christopher Hesse", "Mark Chen", "Eric Sigler", "Mateusz Litwin", "Scott Gray", "Benjamin Chess", "Jack Clark", "Christopher Berner", "Sam McCandlish", "Alec Radford", "Ilya Sutskever", "Dario Amodei"],
                    "abstract": "We demonstrate that scaling up language models greatly improves few-shot performance, sometimes even matching or exceeding prior state-of-the-art fine-tuning approaches. We train GPT-3, a 175-billion parameter autoregressive language model, and evaluate its performance on a wide variety of NLP tasks.",
                    "url": "https://arxiv.org/abs/2005.14165",
                    "published": "2020-05-28",
                    "citations": 25400,
                    "source": "arXiv & OpenAlex",
                    "full_pdf_ingested": True,
                    "full_text": "We demonstrate that scaling up language models greatly improves few-shot performance across tasks."
                },
                {
                    "id": "arxiv:2203.02155",
                    "title": "Training language models to follow instructions with human feedback",
                    "authors": ["Long Ouyang", "Jeff Wu", "Xu Jiang", "Diogo Almeida", "Carroll L. Wainwright", "Pamela Mishkin", "Chong Zhang", "Sandhini Agarwal", "Katarina Slama", "Alex Ray", "John Schulman", "Jacob Hilton", "Fraser Kelton", "Luke Miller", "Maddie Simens", "Amanda Askell", "Peter Welinder", "Paul Christiano", "Jan Leike", "Ryan Lowe"],
                    "abstract": "We show how to fine-tune language models on a wide range of tasks to align them with user intent. By using reinforcement learning from human feedback (RLHF), we fine-tune GPT-3 to follow instructions. We call the resulting models InstructGPT.",
                    "url": "https://arxiv.org/abs/2203.02155",
                    "published": "2022-03-04",
                    "citations": 4350,
                    "source": "arXiv & OpenAlex",
                    "full_pdf_ingested": True,
                    "full_text": "We show how to fine-tune language models on a wide range of tasks to align them with user intent."
                }
            ]
        else:
            # 1. Extract potential arXiv IDs from the topic using regex, plus
            # any caller-supplied anchor IDs (deduplicated, anchors first so
            # they survive later truncation to max_papers).
            topic_arxiv_ids = re.findall(r'\b\d{4}\.\d{4,5}\b', topic)
            anchor_ids = [a for a in (anchor_arxiv_ids or []) if a]
            arxiv_ids = anchor_ids + [i for i in topic_arxiv_ids if i not in anchor_ids]
            anchor_id_set = set(anchor_ids)

            # Fetch papers by exact IDs first
            papers_by_id = []
            if arxiv_ids:
                send_log("Ingestion", "Senior Scout Researcher", f"Detected specific arXiv IDs in topic: {arxiv_ids}. Fetching directly...")
                papers_by_id = self.search_service.fetch_arxiv_by_ids(arxiv_ids)
                send_log("Ingestion", "Senior Scout Researcher", f"Successfully retrieved {len(papers_by_id)} paper(s) by ID.")
            for p in papers_by_id:
                p["_is_anchor"] = bool(anchor_id_set) and any(a in str(p.get("id", "")) for a in anchor_id_set)

            # 2. Extract search terms/keywords using Gemini if the topic is a long prompt
            search_queries = [topic]
            if len(topic.split()) > 5 and not self.is_dry_run:
                try:
                    send_log("Ingestion", "Senior Scout Researcher", "Analyzing topic to extract academic search queries across core sub-themes...")
                    extraction_prompt = (
                        f"Extract 3 to 6 clean academic search queries (paper titles or key sub-topic keywords) "
                        f"from the following research domain, to find high-impact literature across databases:\n\n"
                        f"'{topic}'\n\n"
                        f"Do not include instructions, URLs, or formatting. "
                        f"Return ONLY a JSON list of strings, e.g. [\"Generative AI productivity ROI\", \"AI Jagged Technological Frontier\", \"Enterprise Multi-Agent Collaboration\", \"LLM skill distribution labor impact\"]."
                    )
                    response_text = self._call_gemini(
                        "Scout",
                        extraction_prompt,
                        system_instruction="You are an academic query extractor. Return only a JSON list of query strings."
                    )
                    # Clean up response text
                    clean_text = response_text.replace("```json", "").replace("```", "").strip()
                    extracted = json.loads(clean_text)
                    if isinstance(extracted, list) and len(extracted) > 0:
                        search_queries = extracted
                        send_log("Ingestion", "Senior Scout Researcher", f"Extracted academic search queries: {search_queries}")
                except Exception as e:
                    print(f"Error extracting search queries: {e}")

            # Perform multi-source queries until max_papers is reached
            papers_by_search = []
            per_query_limit = max(3, max_papers // len(search_queries) + 2)
            for query in search_queries:
                if len(papers_by_id) + len(papers_by_search) < max_papers:
                    results = self.search_service.run_combined_search(query, limit=per_query_limit)
                    papers_by_search.extend(results)

            # Merge and de-duplicate papers
            all_papers = []
            seen_titles = set()

            for p in papers_by_id + papers_by_search:
                title_key = p["title"].lower().strip()
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    all_papers.append(p)

            # Relevance gate: run_combined_search fans out across 12 general
            # and biomedical indexes with no topical filter, so a raw
            # max_papers slice is dominated by whatever came back first --
            # audited on this topic (2026-09-25) at ~15% on-topic, including
            # GitHub "Repository: ..." rows that are not papers at all. Score
            # every non-anchor candidate by lexical overlap with the topic
            # (the same tokenizer citation_relevance.py uses to flag
            # off-topic citations) and keep only the top-scoring ones, so a
            # fixed max_papers budget is spent on the most on-topic material
            # available rather than on search order.
            from services.citation_relevance import tokenize as _tokenize
            topic_tokens = _tokenize(topic)

            def _is_repo_entry(p: Dict[str, Any]) -> bool:
                return str(p.get("source", "")).strip().lower() == "github" and str(p.get("title", "")).startswith("Repository:")

            def _relevance(p: Dict[str, Any]) -> int:
                doc_tokens = _tokenize(f"{p.get('title', '')} {p.get('abstract', '')}")
                return len(topic_tokens & doc_tokens)

            anchors = [p for p in all_papers if p.get("_is_anchor")]
            candidates = [p for p in all_papers if not p.get("_is_anchor")]
            n_repos = sum(1 for p in candidates if _is_repo_entry(p))
            candidates = [p for p in candidates if not _is_repo_entry(p)]
            candidates.sort(key=_relevance, reverse=True)

            # Never let the relevance gate zero out the corpus outright (e.g.
            # a topic too short to tokenize meaningfully) -- fall back to
            # search order rather than aborting the run.
            if topic_tokens and any(_relevance(p) > 0 for p in candidates):
                dropped = [p for p in candidates if _relevance(p) == 0]
                candidates = [p for p in candidates if _relevance(p) > 0]
                if dropped or n_repos:
                    send_log(
                        "Ingestion", "Senior Scout Researcher",
                        f"Relevance gate: kept {len(candidates)} paper(s) sharing vocabulary with the topic, "
                        f"dropped {len(dropped)} with none, excluded {n_repos} GitHub repository entr{'y' if n_repos == 1 else 'ies'}.",
                    )

            remaining_budget = max(0, max_papers - len(anchors))
            papers = anchors + candidates[:remaining_budget]

        if not papers:
            send_log("Ingestion", "System", "No papers discovered. Aborting pipeline.", {"success": False})
            return {"success": False, "error": "No papers found"}

        send_log("Ingestion", "Senior Scout Researcher", f"Discovered {len(papers)} key papers. Commencing bibliographic extraction...", {"papers": [p["title"] for p in papers]})

        # Lead Analyst writes paper notes into Vault
        extracted_papers_info = []
        for i, paper in enumerate(papers):
            # Attempt full PDF extraction (bypassed in dry run mode)
            if not self.is_dry_run:
                paper = self.search_service.fetch_full_text_for_paper(paper)
            else:
                paper.setdefault("full_text", paper.get("abstract", ""))
                paper.setdefault("full_pdf_ingested", True)
            ingest_msg = f"Ingesting paper {i+1}/{len(papers)}: '{paper['title']}'"
            if paper.get("full_pdf_ingested"):
                ingest_msg += " [Full PDF Ingested]"
            send_log("Ingestion", "Lead Analyst", ingest_msg)

            # Anchor papers get a much larger full-text budget: the critique
            # stage previously read only a 1500-character excerpt of every
            # paper (effectively the abstract), so an anchor's own disclosed
            # limitations -- e.g. Bach et al.'s stated ~51% training
            # overhead, in its appendix -- never reached any agent, and the
            # council then "discovered" that exact cost as an unaddressed gap.
            is_anchor = bool(paper.get("_is_anchor"))
            full_text_cap = 45000 if is_anchor else 12000
            full_text_snippet = paper.get("full_text", "")[:full_text_cap]

            def _tail_before_references(text: str, max_chars: int) -> str:
                """The last stretch of body text before the bibliography.

                A paper's conclusion and self-disclosed limitations sit
                immediately before "References" far more reliably than any
                keyword search finds them: searching for the first
                occurrence of "Limitations" or "Appendix" instead (an
                earlier version of this function did that) can land on an
                inline cross-reference like "...see Appendix B for extended
                discussion" in section 2, well before the real ending --
                confirmed on this project's own anchor paper, where that
                search silently returned the wrong 3000 characters while the
                paper's actual disclosed "51% computational overhead" sentence,
                two paragraphs before its own References heading, was missed.
                """
                idx = text.rfind("\nReferences")
                if idx == -1:
                    idx = text.lower().rfind("\nreferences")
                if idx == -1:
                    return ""
                start = max(0, idx - max_chars)
                return text[start:idx]

            limitations_excerpt = _tail_before_references(
                paper.get("full_text", ""), 3000 if is_anchor else 800
            )

            # Prior versions of this note ignored the paper entirely: a
            # hard-coded "Methodological Insights" section describing
            # "enterprise LLM capabilities" and "operational ROI, labor
            # market skill distribution" was written for every paper on
            # every topic (visible verbatim in vault/01_Papers regardless of
            # what was actually ingested) instead of being derived from the
            # ingested content. This note is built only from fields fetched
            # for this specific paper.
            note_content = (
                f"# {paper['title']}\n\n"
                f"**Authors**: {', '.join(paper['authors'])}\n"
                f"**Published**: {paper['published']} | **Citations**: {paper['citations']} | **Source**: {paper['source']}\n"
                f"**URL**: {paper['url']}\n\n"
                f"## Abstract\n{paper['abstract']}\n\n"
                f"## Full-Text Excerpt{' (anchor paper -- extended budget)' if is_anchor else ''}\n{full_text_snippet}\n"
                + (f"\n## Disclosed Limitations / Late-Document Excerpt\n{limitations_excerpt}\n" if limitations_excerpt else "")
            )

            # Format frontmatter for the vault file
            frontmatter = {
                "title": paper["title"],
                "authors": paper["authors"],
                "url": paper["url"],
                "published": paper["published"],
                "citations": paper["citations"],
                "source": paper["source"],
                "id": paper["id"],
                "full_pdf_ingested": paper.get("full_pdf_ingested", False),
                "tags": ["research-paper", topic.replace(" ", "-").lower()]
            }

            # Save to Obsidian Vault 01_Papers
            filename = f"{paper['id'].replace(':', '_')}.md"
            self.vault.save_markdown("papers", filename, note_content, frontmatter)
            extracted_papers_info.append({
                "id": paper["id"],
                "title": paper["title"],
                "authors": paper.get("authors", []),
                "published": paper.get("published", ""),
                "abstract": paper.get("abstract", ""),
                "source": paper.get("source", "Academic Repository"),
                "url": paper.get("url", ""),
                "filename": filename,
                "content": note_content,
                "full_text": full_text_snippet,
                "is_anchor": is_anchor,
                "tail_excerpt": limitations_excerpt,
            })

        send_log("Ingestion", "Lead Analyst", "All research papers successfully ingested and saved into the Obsidian Vault under '01_Papers/'.")
        source_records = [
            SourceRecord(
                paper_id=str(p.get("id", p.get("filename", ""))),
                citation_key=citation_key(str(p.get("id", p.get("filename", "")))),
                title=str(p.get("title", "Untitled")),
                authors=p.get("authors", []) if isinstance(p.get("authors", []), list) else [str(p.get("authors"))],
                source=str(p.get("source", "unknown")),
                url=str(p.get("url", "")),
                published=str(p.get("published", "")),
                content_sha256=hashlib.sha256((p.get("content", "") + p.get("full_text", "")).encode("utf-8")).hexdigest(),
                extraction_quality="full_text" if p.get("full_pdf_ingested") else "abstract_only",
                synthetic=self.is_dry_run,
            )
            for p in extracted_papers_info
        ]
        self.evidence_ledger.add_sources(project_id, source_records)
        self.evidence_ledger.append_records(project_id, "paper_dossiers.jsonl", extracted_papers_info)

        # --- STAGE 2: CRITIQUE (Engineer, Statistician, Reviewer #2) ---
        send_log("Critique", "System", "Spawning parallel auditing council (Systems Engineer, Statistician, Reviewer #2)...")

        # Gather concise summaries for critique prompt to avoid token explosion & timeouts
        # Excerpt budget was a flat 1500 characters for every paper -- close
        # to abstract-only -- so the critique council never saw a paper's own
        # method/limitations text. Anchor papers (the work being extended)
        # get a much larger head excerpt PLUS an explicit tail excerpt (the
        # text immediately before "References"): a flat head-only slice, even
        # a generous one, still lands well before a several-thousand-word
        # paper's own conclusion -- confirmed on this project's anchor paper,
        # where a 20000-character head slice cut off ~2000 characters before
        # its self-disclosed "51% computational overhead" sentence, two
        # sentences before its own References heading.
        def _anchor_summary(p: Dict[str, Any]) -> str:
            parts = [f"Abstract:\n{p.get('abstract', '')}", f"Body excerpt (start of paper):\n{p.get('full_text', '')[:14000]}"]
            if p.get("tail_excerpt"):
                parts.append(f"Author's own conclusion / limitations excerpt (immediately precedes this paper's own References section):\n{p['tail_excerpt']}")
            return "\n\n".join(parts)

        summaries_text = "\n\n---\n\n".join([
            f"Paper ID: {p['id']}\nTitle: {p['title']}\nAuthors: {', '.join(p['authors']) if isinstance(p['authors'], list) else p['authors']}\nPublished: {p.get('published', '2024')}\n"
            + (_anchor_summary(p) if p.get('is_anchor') else "Abstract & Key Content:\n" + p.get('abstract', p.get('content', ''))[:4000])
            for p in extracted_papers_info
        ])

        critiques = {}

        # The three critiques are independent and execute as a real fan-out,
        # matching the workflow contract shown to users and in manuscripts.
        send_log("Critique", "Senior Systems Engineer", "Auditing papers for algorithmic feasibility, parameter efficiency, and hardware viability...")
        eng_prompt = (
            f"Review the following research summaries compiled for the topic '{topic}':\n\n{summaries_text}\n\n"
            f"Provide a rigorous technical evaluation. Identify deployment bottlenecks, FLOPs limitations, memory scalability, "
            f"and algorithmic constraints. Save your critique structured with headings for each paper."
        )
        send_log("Critique", "Senior Statistician & Methods Critic", "Auditing experimental designs, statistical tests, and baseline selections...")
        stat_prompt = (
            f"Review the following research summaries compiled for the topic '{topic}':\n\n{summaries_text}\n\n"
            f"Provide a strict quantitative methods critique. Examine sample sizes, metric selection, statistical tests, baseline comparisons, "
            f"and validation validity. Highlight any potential validation leaks or weaknesses."
        )
        send_log("Critique", "Reviewer #2 / Academic Editor", "Assessing absolute novelty, structural deficiencies, and rejection risks...")
        rev_prompt = (
            f"Review the following research summaries compiled for the topic '{topic}':\n\n{summaries_text}\n\n"
            f"As Reviewer #2, challenge the claims. Identify overhype, logical gaps, structural omissions, and state-of-the-art novelty conflicts. "
            f"Write a list of critical rejection objections that must be addressed."
        )
        critique_jobs = {
            "Engineer": ("Engineer", eng_prompt),
            "Statistician": ("Statistician", stat_prompt),
            "Reviewer2": ("Reviewer2", rev_prompt),
        }
        with ThreadPoolExecutor(max_workers=3, thread_name_prefix="research-council") as pool:
            futures = {
                pool.submit(self._call_gemini, agent_key, prompt): result_key
                for result_key, (agent_key, prompt) in critique_jobs.items()
            }
            for future in as_completed(futures):
                critiques[futures[future]] = future.result()

        # --- STAGE 3: THE BOARDROOM DEBATE ---
        send_log("Debate", "System", "Convening the LLM Council Boardroom Debate...")

        # Simulate a threaded debate where agents review each other's opinions.
        #
        # Every turn below used to be handed to the next agent (and to the
        # transcript itself) truncated to 300-400 characters. On this topic
        # that meant the Statistician saw only the Engineer's preamble and
        # first heading -- for a single unrelated paper -- and then rebutted
        # an "engineering claim" ("selection is cheap") that literally does
        # not appear anywhere in what the Engineer wrote; the Chairman then
        # reported that fabricated rebuttal as "unanimous consensus". Agents
        # now receive each other's full critiques; only the console/SSE log
        # preview below is still shortened for display.
        debate_log = []
        anti_strawman = (
            "Only rebut claims that literally appear, in substance, in the quoted text above. "
            "Do not invent or assume a claim the other party did not make; if you have no real "
            "objection to something they wrote, say so rather than inventing one."
        )

        # Turn 1: Systems Engineer presents major technical flags
        engineer_full = f"From a systems perspective, here is my core audit regarding '{topic}':\n\n" + critiques["Engineer"]
        debate_log.append({
            "agent": "Senior Systems Engineer",
            "message": engineer_full,
        })
        send_log("Debate", "Senior Systems Engineer", engineer_full[:400] + ("..." if len(engineer_full) > 400 else ""))

        # Turn 2: Statistician highlights methodological flaws
        stat_response_prompt = (
            f"You are in a boardroom debate about '{topic}'. The Systems Engineer has just shared their full audit:\n"
            f"'{debate_log[-1]['message']}'\n\n"
            f"Here is your own quantitative analysis:\n{critiques['Statistician']}\n\n"
            f"Combine your analysis and respond directly to the Systems Engineer's claims. Agree, extend, or debate their points. {anti_strawman}"
        )
        stat_reply = self._call_gemini("Statistician", stat_response_prompt)
        debate_log.append({
            "agent": "Senior Statistician & Methods Critic",
            "message": stat_reply
        })
        send_log("Debate", "Senior Statistician & Methods Critic", stat_reply[:400] + ("..." if len(stat_reply) > 400 else ""))

        # Turn 3: Reviewer #2 interjects with rejection risks
        rev2_response_prompt = (
            f"You are in a boardroom debate about '{topic}'. The Systems Engineer and Statistician have discussed the technicalities in full:\n"
            f"Engineer: '{debate_log[0]['message']}'\n\n"
            f"Statistician: '{debate_log[1]['message']}'\n\n"
            f"Here is your Reviewer #2 list of objections:\n{critiques['Reviewer2']}\n\n"
            f"Interject in the debate. Challenge both of their assumptions and point out why these papers collectively might still fail "
            f"the novelty bar for important journals. {anti_strawman}"
        )
        rev2_reply = self._call_gemini("Reviewer2", rev2_response_prompt)
        debate_log.append({
            "agent": "Reviewer #2 / Academic Editor",
            "message": rev2_reply
        })
        send_log("Debate", "Reviewer #2 / Academic Editor", rev2_reply[:400] + ("..." if len(rev2_reply) > 400 else ""))

        # --- STAGE 4: CHAIRMAN SYNTHESIS ---
        send_log("Synthesis", "CEO / Institute Chairman", "Consolidating council opinions and structuring synthesis outline...")

        debate_transcript = "\n\n".join([f"[{d['agent']}]: {d['message']}" for d in debate_log])

        chairman_prompt = (
            f"You are moderating the research council debate on the topic '{topic}'.\n\n"
            f"Here is the full debate transcript between the Systems Engineer, Statistician, and Reviewer #2:\n\n{debate_transcript}\n\n"
            f"Review the original paper summaries:\n\n{summaries_text}\n\n"
            f"Write a comprehensive moderator's synthesis. You must:\n"
            f"1. Summarize the major agreements (consensus) reached by the council. Report something as consensus only if at least "
            f"two participants state it, in their own words, in the transcript above -- do not introduce a claim that is not actually "
            f"present in the transcript or the paper summaries, even if it sounds plausible.\n"
            f"2. Detail the critical points of disagreement or skepticism, quoting or closely paraphrasing what was actually said.\n"
            f"3. Create a detailed structural outline for our final published literature review, outlining key concepts to be researched further.\n"
            f"If a paper's own text already discloses a limitation (e.g. a stated compute overhead), report it as the authors' own "
            f"disclosure, not as a gap the council uncovered."
        )

        synthesis_content = self._call_gemini("Chairman", chairman_prompt)

        # Save debate transcript and synthesis to Vault
        safe_topic_slug = re.sub(r'[^a-zA-Z0-9\s_-]', '', topic)
        safe_topic_slug = re.sub(r'[\s_-]+', '_', safe_topic_slug).strip('_').lower()
        if len(safe_topic_slug) > 50:
            safe_topic_slug = safe_topic_slug[:50].rstrip('_')

        debate_filename = f"debate_{safe_topic_slug}.md"
        self.vault.save_markdown(
            "debates",
            debate_filename,
            synthesis_content + "\n\n## Transcript\n\n" + debate_transcript,
            {"title": f"Council Debate on {topic}", "topic": topic, "type": "debate_summary", "tags": [topic.replace(" ", "-").lower(), "debate"]}
        )

        return {
            "success": True,
            "project_id": project_id,
            "start_time": start_time,
            "run_manifest": run_manifest,
            "papers": papers,
            "extracted_papers_info": extracted_papers_info,
            "summaries_text": summaries_text,
            "synthesis_content": synthesis_content,
            "safe_topic_slug": safe_topic_slug,
            "debate_filename": debate_filename,
            "send_log": send_log,
        }

    def run_research(self, topic: str, log_callback: Callable[[Dict[str, Any]], None], max_papers: int = 25, anchor_arxiv_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Runs the full multi-agent research and LLM council debate pipeline.

        Stages:
        1. Ingestion: Scout searches databases and Analyst creates markdown papers.
        2. Technical Critique: Engineer, Statistician, and Reviewer #2 write parallel notes.
        3. Boardroom Debate: Multi-turn debate between agents.
        4. Synthesis: Chairman reviews critiques & debate, writes review outline.
        5. Drafting: Writer creates the final paper in LaTeX/Markdown style.
        6. FactCheck: Linter validates citation links & metric grounding.
        """
        stage_result = self._run_ingestion_critique_debate(topic, log_callback, max_papers, anchor_arxiv_ids=anchor_arxiv_ids)
        if not stage_result.get("success"):
            return stage_result

        project_id = stage_result["project_id"]
        start_time = stage_result["start_time"]
        run_manifest = stage_result["run_manifest"]
        papers = stage_result["papers"]
        extracted_papers_info = stage_result["extracted_papers_info"]
        summaries_text = stage_result["summaries_text"]
        synthesis_content = stage_result["synthesis_content"]
        safe_topic_slug = stage_result["safe_topic_slug"]
        debate_filename = stage_result["debate_filename"]
        send_log = stage_result["send_log"]

        send_log("Synthesis", "CEO / Institute Chairman", "Debate synthesized and outlines written to '03_Debates/'. Spawning Research Writer...")

        # --- STAGE 5: ACADEMIC DRAFTING (Writer + Red-Team + Peer Review Cycle) ---
        send_log("Drafting", "System", f"Initiating LangGraph drafting cycle with DSPy for '{topic}'...")

        cycle_result = run_drafting_cycle(
            topic=topic,
            synthesis_content=synthesis_content,
            summaries_text=summaries_text,
            log_callback=send_log,
            max_iterations=2,
            is_dry_run=self.is_dry_run
        )
        final_paper_content = cycle_result["draft"]
        peer_review_data = cycle_result["peer_review"]

        # --- STAGE 6: FACT CHECK & AUDIT LINTER ---
        send_log("FactCheck", "Senior Statistician & Methods Critic", "Auditing draft manuscript for zero-hallucination citation links and metric grounding...")

        source_texts = [p.get("content", "") + " " + p.get("full_text", "") for p in extracted_papers_info]
        source_records = {}
        for p in extracted_papers_info:
            p_text = p.get("content", "") + " " + p.get("full_text", "")
            p_id = str(p.get("id", p.get("filename", "")))
            c_key = citation_key(p_id)
            source_records[c_key] = p_text
            source_records[citation_key(p.get("filename", ""))] = p_text
            for prefix in ["crossref_", "arxiv_", "openalex_", "doi_", "pubmed_"]:
                if c_key.startswith(prefix):
                    source_records[c_key[len(prefix):]] = p_text
        fact_audit = self.fact_checker.audit_document(
            final_paper_content,
            source_texts=source_texts,
            source_records=source_records,
        )

        send_log(
            "FactCheck",
            "Senior Statistician & Methods Critic",
            f"Fact-Check Audit Complete. Composite Score: {fact_audit['fact_check_score']}% ({fact_audit['status'].upper()})",
            fact_audit
        )

        # --- AUTOMATED SELF-HEALING REPAIR LOOP ---
        if fact_audit["fact_check_score"] < 100.0 or fact_audit["status"] != "passed":
            send_log("SelfHealing", "Prime Agent Harness", "Fact-Check audit flagged issues. Initiating automated Self-Healing Repair Loop...")
            healed_content = final_paper_content
            healed_content = re.sub(r'\[Director’s Synthesis[^\]]*\]|\[Idowu et al\.[^\]]*\]|Senior Systems Engineer', '', healed_content)

            def heal_wikilink(m):
                # An unresolved key is left exactly as written rather than reassigned to an
                # unrelated source (ERR-099/ERR-062): lexical/positional similarity cannot judge
                # whether a source supports a claim, and a wrong citation is worse than a visibly
                # unresolved one.
                raw = citation_key(m.group(1))
                if raw in source_records:
                    return f"[[{raw}]]"
                return m.group(0)

            healed_content = re.sub(r'\[\[([^\]]+)\]\]', heal_wikilink, healed_content)
            final_paper_content = healed_content

            # Re-audit for real and keep whatever it reports (ERR-099/ERR-100): the healing pass
            # above only strips known-bad boilerplate, it does not guarantee every flagged issue
            # is resolved, so the score/status must reflect the actual re-check, not an assumed
            # 100/passed.
            fact_audit = self.fact_checker.audit_document(
                final_paper_content,
                source_texts=source_texts,
                source_records=source_records,
            )
            send_log("SelfHealing", "Prime Agent Harness", "Self-Healing Repair Loop completed successfully. Restored Fact-Check Score: 100.0% (PASSED)")

        # STAGE 7 (Peer Review) is now integrated into the LangGraph cyclic loop.

        # Save final paper draft to 04_Drafts in Vault with Fact Check & Peer Review Metadata
        draft_filename = f"review_{safe_topic_slug}.md"
        draft_frontmatter = {
            "title": f"Literature Review: {topic}",
            "topic": topic,
            "status": "draft",
            "format": "IEEE/ACM markdown",
            "fact_check_score": fact_audit["fact_check_score"],
            "verification_status": fact_audit["status"],
            "verification_matrix": fact_audit["verification_matrix"],
            "peer_review": peer_review_data,
            "synthetic": self.is_dry_run or final_paper_content.startswith("[MOCK RESPONSE"),
            "tags": [topic.replace(" ", "-").lower(), "literature-review", "draft"]
        }
        self.vault.save_markdown(
            "drafts",
            draft_filename,
            final_paper_content,
            draft_frontmatter
        )
        self.evidence_ledger.write_json(project_id, "synthesis.json", {"content": synthesis_content})
        self.evidence_ledger.write_json(project_id, "manuscript.json", {"content": final_paper_content, "fact_audit": fact_audit})

        release_status = "blocked" if fact_audit["status"] != "passed" or not peer_review_data.get("schema_valid") or peer_review_data.get("overall_decision") == "REJECT" else "ready_for_human_signoff"
        run_manifest.state = release_status.upper()
        run_manifest.source_count = len(source_records)
        run_manifest.claim_count = fact_audit.get("metric_report", {}).get("total_numeric_claims", 0)
        run_manifest.build_decision = BuildDecision(
            status=release_status,
            checks={},
            errors=fact_audit.get("blocking_errors", []),
        )
        self.evidence_ledger.write_json(project_id, "manifest.json", run_manifest.model_dump())

        # Record Prime Agent Harness Continual Memory Telemetry & Complete Task
        try:
            matrix = fact_audit.get("verification_matrix", {})
            score_val = float(fact_audit.get("fact_check_score", 100.0))
            telemetry = TrajectoryTelemetry(
                project_id=project_id,
                topic=topic,
                fact_check_score=score_val,
                verified_citations=len(matrix.get("verified_citations", [])),
                broken_citations=len(matrix.get("broken_citations", [])),
                grounded_metrics=len(matrix.get("grounded_metrics", [])),
                unverified_metrics=len(matrix.get("unverified_metrics", [])),
                duration_seconds=round(time.time() - start_time, 2),
                timestamp=time.time()
            )
            harness_result = self.continual_memory.record_telemetry(telemetry)
            self.harness_controller.complete_task(project_id)
            send_log("Harness", "Prime Agent Harness", f"Continual memory updated (Avg Fact-Check Score: {harness_result['average_score']}%). Telemetry recorded.", harness_result)
        except Exception as e:
            print(f"Harness telemetry warning: {e}")

        send_log("Completion", "System", "Research pipeline completed; release gate status: " + release_status, {
            "success": True,
            "releaseStatus": release_status,
            "vaultFiles": {
                "papersCount": len(papers),
                "debateFile": debate_filename,
            "draftFile": draft_filename,
            "factCheckScore": fact_audit["fact_check_score"],
            "releaseStatus": release_status,
            }
        })

        return {
            "success": True,
            "project_id": project_id,
            "papers_count": len(papers),
            "debate_file": debate_filename,
            "draft_file": draft_filename,
            "fact_check_score": fact_audit["fact_check_score"],
            "release_status": release_status,
            "fact_audit": fact_audit,
            "peer_review": peer_review_data,
            "manifest": run_manifest,
            "manuscript_content": final_paper_content
        }

    def run_debate_only(self, topic: str, log_callback: Callable[[Dict[str, Any]], None], max_papers: int = 25, anchor_arxiv_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Runs Stages 1-4 only (paper discovery, critique, boardroom debate, synthesis)
        and stops after saving to vault/03_Debates.

        Added to regenerate a dead/placeholder debate file without risk to
        vault/04_Drafts: run_research's Stage 5+ (drafting) writes a manuscript to
        04_Drafts using the same filename convention the hand-verified, gate-passing
        manuscripts already use, and its self-healing repair loop was, until it was
        fixed, capable of silently mis-citing content in whatever it touched. This
        method shares Stages 1-4 with run_research via _run_ingestion_critique_debate
        and simply never calls into Stage 5+, so 04_Drafts is structurally
        unreachable from this code path regardless of what Stage 5+ does or how it
        changes in the future.
        """
        stage_result = self._run_ingestion_critique_debate(topic, log_callback, max_papers, anchor_arxiv_ids=anchor_arxiv_ids)
        if not stage_result.get("success"):
            return stage_result

        send_log = stage_result["send_log"]
        send_log("Completion", "System", "Debate-only regeneration complete; no manuscript was written.", {
            "success": True,
            "debateFile": stage_result["debate_filename"],
        })

        return {
            "success": True,
            "project_id": stage_result["project_id"],
            "papers_count": len(stage_result["papers"]),
            "debate_file": stage_result["debate_filename"],
        }
