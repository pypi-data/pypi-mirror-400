"""
Minmo-Engine: MCP 통합 자동화 프레임워크

Claude Code와 Gemini를 연동한 멀티 에이전트 오케스트레이션 시스템
"""

__version__ = "1.1.0"
__author__ = "Minmo Team"

from minmo.orchestrator import MinmoOrchestrator, ScribeMCP
from minmo.gemini_cli_wrapper import (
    GeminiCLIWrapper,
    ProjectAnalysis,
    TaskPlan,
    ClarificationQuestion,
    COMMANDER_CLI_CONSTITUTION,
    # Plan Mode
    InterviewFocus,
    InterviewQuestion,
    InterviewAnswer,
    FeatureSpec,
    PlanTask,
    PlanModeResult,
)
from minmo.claude_wrapper import (
    ClaudeCodeWrapper,
    TaskResult,
    TaskStatus,
    ExecutionContext,
    WORKER_CONSTITUTION,
)
from minmo.indexer import (
    CodeIndexer,
    CodeSymbol,
    FileIndex,
    ImportInfo,
    SearchResult,
    IndexStorage,
    SQLiteFTS5Storage,
    VectorStorage,
    PythonASTParser,
)

# 하위 호환성을 위한 별칭
GeminiWrapper = GeminiCLIWrapper
COMMANDER_CONSTITUTION = COMMANDER_CLI_CONSTITUTION

__all__ = [
    # Orchestrator
    "MinmoOrchestrator",
    "ScribeMCP",
    # Commander (Gemini CLI)
    "GeminiCLIWrapper",
    "GeminiWrapper",  # 하위 호환성
    "ProjectAnalysis",
    "TaskPlan",
    "ClarificationQuestion",
    "COMMANDER_CLI_CONSTITUTION",
    "COMMANDER_CONSTITUTION",  # 하위 호환성
    # Plan Mode
    "InterviewFocus",
    "InterviewQuestion",
    "InterviewAnswer",
    "FeatureSpec",
    "PlanTask",
    "PlanModeResult",
    # Worker (Claude Code)
    "ClaudeCodeWrapper",
    "TaskResult",
    "TaskStatus",
    "ExecutionContext",
    "WORKER_CONSTITUTION",
    # Indexer (RAG)
    "CodeIndexer",
    "CodeSymbol",
    "FileIndex",
    "ImportInfo",
    "SearchResult",
    "IndexStorage",
    "SQLiteFTS5Storage",
    "VectorStorage",
    "PythonASTParser",
]
