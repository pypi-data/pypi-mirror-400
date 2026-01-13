"""
Gemini CLI Wrapper - Minmo-Engine의 지휘관 (Commander)

Google Gen AI SDK v1.0+ 기반 구현
- from google import genai
- from google.genai import types
"""

import os
import re
import json
from typing import Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from google import genai
from google.genai import types

from minmo.scribe_mcp import _log_event_impl as log_event, init_database


# ============================================================
# 헌법 (Constitution) - Commander용 시스템 프롬프트
# ============================================================
COMMANDER_CLI_CONSTITUTION = """[MINMO COMMANDER 원칙 - 반드시 준수]

당신은 Minmo-Engine의 **지휘관(Commander)**입니다.
개발 작업을 계획하고, 요구사항을 분석하며, 작업자에게 명확한 지시를 내립니다.

## 핵심 원칙 (절대 위반 금지)

### 1. 최소주의 원칙
- **요청받은 것만 개발하라.** 추가 기능, "있으면 좋을" 기능은 절대 제안하지 마라.
- **추측하지 마라.** 불확실하면 반드시 질문하라.
- **과도한 주석 금지.** 코드가 스스로 설명하게 하라.

### 2. 명확성 원칙
- **모호한 요구사항은 즉시 명확화하라.** 가정하지 말고 질문하라.
- **구체적인 작업 단위로 분해하라.** "로그인 기능 구현"이 아니라 세부 단계로.
- **기술 선택에는 근거를 제시하라.**

### 3. 검증 원칙
- **기존 코드를 먼저 분석하라.** 중복 구현을 피하라.
- **변경 전 영향 범위를 파악하라.** 사이드 이펙트를 예측하라.
- **사용자 확인 없이 큰 변경을 하지 마라.**

## 응답 형식
항상 JSON 형식으로 응답하세요:
```json
{
  "type": "plan|interview|analysis|task_list",
  "content": { ... }
}
```
"""


# ============================================================
# 데이터 클래스
# ============================================================
class InterviewFocus(Enum):
    """인터뷰 질문 초점 영역"""
    ARCHITECTURE = "architecture"
    DATA_MODEL = "data_model"
    EXCEPTION_HANDLING = "exception_handling"
    CONVENTION = "convention"
    INTEGRATION = "integration"
    TESTING = "testing"


@dataclass
class ProjectAnalysis:
    """프로젝트 분석 결과"""
    project_path: str
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    structure_summary: str = ""
    key_files: list[str] = field(default_factory=list)
    conventions: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class InterviewQuestion:
    """인터뷰 질문"""
    question: str
    focus: InterviewFocus
    options: list[str] = field(default_factory=list)
    context: str = ""


@dataclass
class InterviewAnswer:
    """인터뷰 답변"""
    question: InterviewQuestion
    answer: str


@dataclass
class FeatureSpec:
    """기능 기획서"""
    feature_name: str
    summary: str
    requirements: list[str] = field(default_factory=list)
    architecture_decisions: list[str] = field(default_factory=list)
    data_model: dict[str, Any] = field(default_factory=dict)
    error_handling: list[str] = field(default_factory=list)
    conventions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)


@dataclass
class PlanTask:
    """분해된 태스크"""
    id: str
    title: str
    goal: str
    files_to_modify: list[str] = field(default_factory=list)
    expected_logic: str = ""
    dependencies: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)


@dataclass
class PlanModeResult:
    """Plan Mode 결과"""
    project_analysis: ProjectAnalysis | None = None
    feature_spec: FeatureSpec | None = None
    tasks: list[PlanTask] = field(default_factory=list)
    interview_history: list[InterviewAnswer] = field(default_factory=list)
    approved: bool = False
    spec_file_path: str = ""


@dataclass
class TaskPlan:
    """작업 계획 (orchestrator 호환용)"""
    goal: str
    tasks: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    estimated_complexity: str = "medium"


@dataclass
class ClarificationQuestion:
    """명확화 질문 (orchestrator 호환용)"""
    question: str
    context: str = ""
    options: list[str] = field(default_factory=list)


# ============================================================
# 도구 함수들 (Function Calling용)
# ============================================================
def analyze_directory(path: str, max_depth: int = 3) -> dict[str, Any]:
    """디렉토리 구조를 분석합니다."""
    target = Path(path)
    if not target.exists():
        return {"error": f"Path not found: {path}"}

    files = []
    dirs = []
    ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".minmo"}

    def _walk(current: Path, depth: int):
        if depth > max_depth:
            return
        try:
            for item in sorted(current.iterdir()):
                if item.name.startswith('.') and item.name not in [".gitignore", ".env.example"]:
                    continue
                if item.name in ignore_dirs:
                    continue

                rel_path = str(item.relative_to(target))
                if item.is_file():
                    files.append(rel_path)
                elif item.is_dir():
                    dirs.append(rel_path)
                    _walk(item, depth + 1)
        except PermissionError:
            pass

    _walk(target, 0)
    return {"path": path, "files": files[:100], "directories": dirs[:50]}


def read_file(file_path: str, max_lines: int = 200) -> dict[str, Any]:
    """파일 내용을 읽습니다."""
    try:
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.split("\n")

        if len(lines) > max_lines:
            content = "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"

        return {"file_path": file_path, "content": content, "line_count": len(lines)}
    except Exception as e:
        return {"error": str(e)}


def search_code(pattern: str, path: str = ".", file_extension: str = "") -> dict[str, Any]:
    """코드에서 패턴을 검색합니다."""
    results = []
    target = Path(path)

    if not target.exists():
        return {"error": f"Path not found: {path}"}

    ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}

    def _search(current: Path):
        if len(results) >= 50:
            return
        try:
            for item in current.iterdir():
                if item.name in ignore_dirs:
                    continue
                if item.is_file():
                    if file_extension and not item.suffix == file_extension:
                        continue
                    try:
                        content = item.read_text(encoding="utf-8", errors="replace")
                        for i, line in enumerate(content.split("\n"), 1):
                            if pattern.lower() in line.lower():
                                results.append({
                                    "file": str(item),
                                    "line": i,
                                    "content": line.strip()[:200]
                                })
                                if len(results) >= 50:
                                    return
                    except Exception:
                        pass
                elif item.is_dir():
                    _search(item)
        except PermissionError:
            pass

    _search(target)
    return {"pattern": pattern, "matches": results}


def get_project_conventions(path: str = ".") -> dict[str, Any]:
    """프로젝트 컨벤션을 분석합니다."""
    target = Path(path)
    conventions = []

    # 설정 파일들 확인
    config_files = {
        "pyproject.toml": "Python project with modern tooling",
        "setup.py": "Python project with setuptools",
        "package.json": "Node.js project",
        "tsconfig.json": "TypeScript project",
        ".eslintrc": "ESLint configured",
        ".prettierrc": "Prettier configured",
        "ruff.toml": "Ruff linter configured",
        ".flake8": "Flake8 linter configured",
        "mypy.ini": "MyPy type checking",
    }

    for filename, description in config_files.items():
        if (target / filename).exists():
            conventions.append(description)

    # 네이밍 패턴 분석
    py_files = list(target.glob("**/*.py"))[:10]
    naming_patterns = []

    for py_file in py_files:
        if py_file.name.startswith("test_"):
            naming_patterns.append("test_ prefix for tests")
        if "_" in py_file.stem and py_file.stem.islower():
            naming_patterns.append("snake_case for files")

    return {
        "conventions": list(set(conventions)),
        "naming_patterns": list(set(naming_patterns))[:5]
    }


def get_project_architecture(path: str = ".") -> dict[str, Any]:
    """프로젝트 아키텍처를 분석합니다."""
    target = Path(path)

    # 주요 디렉토리 구조 분석
    directories = []
    layers = []

    common_patterns = {
        "src": "Source code directory",
        "lib": "Library code",
        "tests": "Test files",
        "test": "Test files",
        "docs": "Documentation",
        "scripts": "Utility scripts",
        "api": "API layer",
        "models": "Data models",
        "services": "Business logic",
        "utils": "Utility functions",
        "core": "Core functionality",
    }

    for dir_name, description in common_patterns.items():
        if (target / dir_name).exists():
            directories.append({"name": dir_name, "purpose": description})
            layers.append(description)

    return {
        "directories": directories,
        "layers": layers,
        "project_type": "Python" if (target / "pyproject.toml").exists() else "Unknown"
    }


# ============================================================
# Gemini CLI Wrapper 클래스 (Google Gen AI SDK v1.0+)
# ============================================================
class GeminiCLIWrapper:
    """
    Gemini CLI Wrapper - 지휘관 역할

    Google Gen AI SDK v1.0+ 기반 구현
    """

    # 도구 정의 (types.Tool 형식)
    TOOLS = [
        types.Tool(function_declarations=[
            types.FunctionDeclaration(
                name="analyze_directory",
                description="디렉토리 구조를 분석합니다",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "path": types.Schema(type=types.Type.STRING, description="분석할 디렉토리 경로"),
                        "max_depth": types.Schema(type=types.Type.INTEGER, description="최대 탐색 깊이 (기본: 3)")
                    },
                    required=["path"]
                )
            ),
            types.FunctionDeclaration(
                name="read_file",
                description="파일 내용을 읽습니다",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "file_path": types.Schema(type=types.Type.STRING, description="읽을 파일 경로"),
                        "max_lines": types.Schema(type=types.Type.INTEGER, description="최대 라인 수 (기본: 200)")
                    },
                    required=["file_path"]
                )
            ),
            types.FunctionDeclaration(
                name="search_code",
                description="코드에서 패턴을 검색합니다",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "pattern": types.Schema(type=types.Type.STRING, description="검색할 패턴"),
                        "path": types.Schema(type=types.Type.STRING, description="검색 경로 (기본: .)"),
                        "file_extension": types.Schema(type=types.Type.STRING, description="파일 확장자 필터")
                    },
                    required=["pattern"]
                )
            ),
            types.FunctionDeclaration(
                name="get_project_conventions",
                description="프로젝트 컨벤션을 분석합니다",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "path": types.Schema(type=types.Type.STRING, description="프로젝트 경로 (기본: .)")
                    }
                )
            ),
            types.FunctionDeclaration(
                name="get_project_architecture",
                description="프로젝트 아키텍처를 분석합니다",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "path": types.Schema(type=types.Type.STRING, description="프로젝트 경로 (기본: .)")
                    }
                )
            ),
        ])
    ]

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash",
        working_directory: str | None = None,
        timeout_seconds: int = 120,
        on_output: Callable[[str], None] | None = None,
        on_error: Callable[[str, dict], None] | None = None,
        verbose: bool = False
    ):
        """
        GeminiCLIWrapper 초기화

        Args:
            api_key: Gemini API 키 (없으면 환경변수에서 로드)
            model: 사용할 모델 (기본: gemini-2.5-flash)
            working_directory: 작업 디렉토리 (기본: 현재 디렉토리)
            timeout_seconds: 요청 타임아웃 (초)
            on_output: 출력 콜백 함수
            on_error: 에러 콜백 함수
            verbose: 상세 출력 여부
        """
        # API 키 설정
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY 또는 GOOGLE_API_KEY 환경변수를 설정하거나 "
                "api_key 파라미터를 전달하세요."
            )

        self.model_name = model
        self.working_directory = working_directory or os.getcwd()
        self.timeout_seconds = timeout_seconds
        self.on_output = on_output
        self.on_error = on_error
        self.verbose = verbose

        # Google Gen AI 클라이언트 초기화
        self.client = genai.Client(api_key=self.api_key)

        # 도구 함수 매핑 (tool_call.name -> 실제 함수)
        self.tool_map: dict[str, Callable] = {
            "analyze_directory": analyze_directory,
            "read_file": read_file,
            "search_code": search_code,
            "get_project_conventions": get_project_conventions,
            "get_project_architecture": get_project_architecture,
        }

        # 대화 히스토리
        self.conversation_history: list[types.Content] = []

        # Scribe DB 초기화
        try:
            init_database()
        except Exception:
            pass

    def _log(self, content: str, metadata: dict | None = None) -> None:
        """로그를 기록합니다."""
        if self.verbose and self.on_output:
            self.on_output(content)

        try:
            log_event(
                agent="commander",
                content=content,
                metadata=json.dumps(metadata or {}, ensure_ascii=False)
            )
        except Exception:
            pass

    def _send_message(
        self,
        message: str,
        use_tools: bool = True,
        system_instruction: str | None = None
    ) -> str:
        """
        Gemini에 메시지를 보내고 응답을 받습니다.

        Args:
            message: 전송할 메시지
            use_tools: 도구 사용 여부
            system_instruction: 시스템 지시문

        Returns:
            응답 텍스트
        """
        self._log(f"메시지 전송: {message[:100]}...")

        # 사용자 메시지 추가
        self.conversation_history.append(
            types.Content(role="user", parts=[types.Part.from_text(text=message)])
        )

        # 설정 구성
        config = types.GenerateContentConfig(
            system_instruction=system_instruction or COMMANDER_CLI_CONSTITUTION,
            tools=self.TOOLS if use_tools else None,
            temperature=0.7,
        )

        try:
            # 응답 생성
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=self.conversation_history,
                config=config,
            )

            # 응답 처리
            result_text = ""

            for candidate in response.candidates:
                for part in candidate.content.parts:
                    # 텍스트 응답
                    if part.text:
                        result_text += part.text

                    # 함수 호출 처리
                    if part.function_call:
                        tool_name = part.function_call.name
                        tool_args = dict(part.function_call.args) if part.function_call.args else {}

                        self._log(f"도구 호출: {tool_name}", {"args": tool_args})

                        # tool_map에서 함수 찾아 실행
                        if tool_name in self.tool_map:
                            tool_result = self.tool_map[tool_name](**tool_args)
                        else:
                            tool_result = {"error": f"Unknown tool: {tool_name}"}

                        # 함수 응답 추가
                        self.conversation_history.append(
                            types.Content(
                                role="model",
                                parts=[types.Part.from_function_call(
                                    name=tool_name,
                                    args=tool_args
                                )]
                            )
                        )
                        self.conversation_history.append(
                            types.Content(
                                role="user",
                                parts=[types.Part.from_function_response(
                                    name=tool_name,
                                    response=tool_result
                                )]
                            )
                        )

                        # 도구 실행 후 계속 대화
                        return self._send_message("도구 실행 결과를 바탕으로 계속하세요.", use_tools=use_tools)

            # 모델 응답 히스토리에 추가
            if result_text:
                self.conversation_history.append(
                    types.Content(role="model", parts=[types.Part.from_text(text=result_text)])
                )

            self._log(f"응답 수신: {len(result_text)} chars")
            return result_text

        except Exception as e:
            self._log(f"API 오류: {e}")
            if self.on_error:
                self.on_error("api_error", {"error": str(e)})
            return ""

    def _parse_json_response(self, text: str) -> dict[str, Any]:
        """
        응답에서 JSON을 추출합니다.

        Args:
            text: 응답 텍스트

        Returns:
            파싱된 JSON 딕셔너리
        """
        if not text:
            return {}

        # ```json ... ``` 블록 찾기
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 순수 JSON 시도
        text = text.strip()
        if text.startswith('{') or text.startswith('['):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

        # JSON 객체 찾기
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return {"type": "text", "content": text}

    def check_login_status(self) -> bool:
        """
        API 연결 상태를 확인합니다.

        Returns:
            연결 가능하면 True
        """
        try:
            # 간단한 테스트 요청
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Hello",
                config=types.GenerateContentConfig(
                    max_output_tokens=10
                )
            )
            return bool(response.candidates)
        except Exception:
            return False

    def reset_conversation(self) -> None:
        """대화 히스토리를 초기화합니다."""
        self.conversation_history = []

    # ============================================================
    # 프로젝트 분석 메서드
    # ============================================================

    def analyze_project(self, project_path: str | None = None) -> ProjectAnalysis:
        """
        프로젝트 구조를 분석합니다.

        Args:
            project_path: 프로젝트 경로 (기본: 작업 디렉토리)

        Returns:
            프로젝트 분석 결과
        """
        target_path = project_path or self.working_directory
        self._log(f"프로젝트 분석: {target_path}")
        self.reset_conversation()

        prompt = f"""다음 프로젝트를 분석하세요: {target_path}

analyze_directory와 get_project_conventions 도구를 사용하여 분석한 후,
JSON 형식으로 응답해주세요:

```json
{{
    "languages": ["사용된 언어들"],
    "frameworks": ["사용된 프레임워크들"],
    "structure_summary": "프로젝트 구조 요약",
    "key_files": ["주요 파일들"],
    "conventions": ["감지된 코드 컨벤션"],
    "dependencies": ["주요 의존성"]
}}
```
"""

        response = self._send_message(prompt, use_tools=True)
        data = self._parse_json_response(response)

        # content 키가 있으면 추출
        if "content" in data and isinstance(data["content"], dict):
            data = data["content"]

        return ProjectAnalysis(
            project_path=target_path,
            languages=data.get("languages", []),
            frameworks=data.get("frameworks", []),
            structure_summary=data.get("structure_summary", ""),
            key_files=data.get("key_files", []),
            conventions=data.get("conventions", []),
            dependencies=data.get("dependencies", [])
        )

    # ============================================================
    # Plan Mode 메서드
    # ============================================================

    def generate_interview_questions(
        self,
        user_goal: str,
        project_analysis: ProjectAnalysis | None = None
    ) -> list[InterviewQuestion]:
        """
        사용자 목표를 분석하여 인터뷰 질문을 생성합니다.

        Args:
            user_goal: 사용자의 요구사항
            project_analysis: 프로젝트 분석 결과

        Returns:
            인터뷰 질문 목록 (3-7개)
        """
        self._log("인터뷰 질문 생성", {"goal": user_goal})
        self.reset_conversation()

        context = ""
        if project_analysis:
            context = f"""
프로젝트 정보:
- 언어: {', '.join(project_analysis.languages)}
- 프레임워크: {', '.join(project_analysis.frameworks)}
- 구조: {project_analysis.structure_summary}
"""

        prompt = f"""사용자 요구사항: {user_goal}
{context}

다음 영역에 대해 3-7개의 심층 질문을 생성하세요:
- architecture: 아키텍처 결정
- data_model: 데이터 모델
- exception_handling: 예외 처리
- convention: 코드 컨벤션
- integration: 통합/연동
- testing: 테스트 전략

JSON 형식으로 응답:
```json
{{
    "questions": [
        {{
            "question": "질문 내용",
            "focus": "architecture|data_model|exception_handling|convention|integration|testing",
            "options": ["선택지1", "선택지2"],
            "context": "질문 배경"
        }}
    ]
}}
```
"""

        response = self._send_message(prompt, use_tools=False)
        data = self._parse_json_response(response)

        if "content" in data and isinstance(data["content"], dict):
            data = data["content"]

        questions = []
        for q in data.get("questions", []):
            try:
                focus = InterviewFocus(q.get("focus", "architecture"))
            except ValueError:
                focus = InterviewFocus.ARCHITECTURE

            questions.append(InterviewQuestion(
                question=q.get("question", ""),
                focus=focus,
                options=q.get("options", []),
                context=q.get("context", "")
            ))

        return questions

    def generate_feature_spec(
        self,
        user_goal: str,
        interview_answers: list[InterviewAnswer],
        project_analysis: ProjectAnalysis | None = None
    ) -> FeatureSpec:
        """
        인터뷰 결과를 바탕으로 기획서를 생성합니다.

        Args:
            user_goal: 사용자 요구사항
            interview_answers: 인터뷰 답변 목록
            project_analysis: 프로젝트 분석 결과

        Returns:
            기능 기획서
        """
        self._log("기획서 생성", {"goal": user_goal})
        self.reset_conversation()

        answers_text = "\n".join([
            f"Q: {a.question.question}\nA: {a.answer}"
            for a in interview_answers
        ])

        prompt = f"""요구사항: {user_goal}

인터뷰 결과:
{answers_text}

위 정보를 바탕으로 기획서를 생성하세요.

JSON 형식으로 응답:
```json
{{
    "feature_name": "기능명",
    "summary": "기능 요약",
    "requirements": ["요구사항1", "요구사항2"],
    "architecture_decisions": ["아키텍처 결정1"],
    "data_model": {{}},
    "error_handling": ["에러 처리 전략"],
    "conventions": ["따를 컨벤션"],
    "constraints": ["제약 조건"],
    "out_of_scope": ["범위 외 항목"]
}}
```
"""

        response = self._send_message(prompt, use_tools=False)
        data = self._parse_json_response(response)

        if "content" in data and isinstance(data["content"], dict):
            data = data["content"]

        return FeatureSpec(
            feature_name=data.get("feature_name", user_goal[:50]),
            summary=data.get("summary", user_goal),
            requirements=data.get("requirements", []),
            architecture_decisions=data.get("architecture_decisions", []),
            data_model=data.get("data_model", {}),
            error_handling=data.get("error_handling", []),
            conventions=data.get("conventions", []),
            constraints=data.get("constraints", []),
            out_of_scope=data.get("out_of_scope", [])
        )

    def decompose_to_tasks(
        self,
        spec: FeatureSpec,
        project_analysis: ProjectAnalysis | None = None
    ) -> list[PlanTask]:
        """
        기획서를 태스크로 분해합니다.

        Args:
            spec: 기능 기획서
            project_analysis: 프로젝트 분석 결과

        Returns:
            태스크 목록
        """
        self._log("태스크 분해", {"feature": spec.feature_name})
        self.reset_conversation()

        prompt = f"""기획서:
- 기능명: {spec.feature_name}
- 요약: {spec.summary}
- 요구사항: {', '.join(spec.requirements)}
- 아키텍처: {', '.join(spec.architecture_decisions)}

위 기획서를 구체적인 태스크로 분해하세요.

JSON 형식으로 응답:
```json
{{
    "tasks": [
        {{
            "id": "task_001",
            "title": "태스크 제목",
            "goal": "태스크 목표",
            "files_to_modify": ["수정할 파일"],
            "expected_logic": "예상 로직",
            "dependencies": ["선행 태스크 ID"],
            "acceptance_criteria": ["완료 조건"]
        }}
    ]
}}
```
"""

        response = self._send_message(prompt, use_tools=False)
        data = self._parse_json_response(response)

        if "content" in data and isinstance(data["content"], dict):
            data = data["content"]

        tasks = []
        for t in data.get("tasks", []):
            tasks.append(PlanTask(
                id=t.get("id", f"task_{len(tasks)+1:03d}"),
                title=t.get("title", ""),
                goal=t.get("goal", ""),
                files_to_modify=t.get("files_to_modify", []),
                expected_logic=t.get("expected_logic", ""),
                dependencies=t.get("dependencies", []),
                acceptance_criteria=t.get("acceptance_criteria", [])
            ))

        return tasks

    def run_plan_mode(
        self,
        user_goal: str,
        on_question: Callable[[InterviewQuestion], str] | None = None,
        on_spec_review: Callable[[FeatureSpec], bool] | None = None,
        on_tasks_review: Callable[[list[PlanTask]], bool] | None = None
    ) -> PlanModeResult:
        """
        Plan Mode 전체 흐름을 실행합니다.

        Args:
            user_goal: 사용자 요구사항
            on_question: 질문 콜백 (질문 → 답변)
            on_spec_review: 기획서 리뷰 콜백
            on_tasks_review: 태스크 리뷰 콜백

        Returns:
            Plan Mode 결과
        """
        self._log("Plan Mode 시작", {"goal": user_goal})
        result = PlanModeResult()

        # 1. 프로젝트 분석
        try:
            result.project_analysis = self.analyze_project()
        except Exception as e:
            self._log(f"프로젝트 분석 실패: {e}")
            result.project_analysis = ProjectAnalysis(project_path=self.working_directory)

        # 2. 인터뷰 질문 생성
        questions = self.generate_interview_questions(
            user_goal=user_goal,
            project_analysis=result.project_analysis
        )

        # 3. 인터뷰 수행
        for q in questions:
            if on_question:
                answer = on_question(q)
            else:
                answer = q.options[0] if q.options else "확인"

            result.interview_history.append(InterviewAnswer(question=q, answer=answer))

        # 4. 기획서 생성
        result.feature_spec = self.generate_feature_spec(
            user_goal=user_goal,
            interview_answers=result.interview_history,
            project_analysis=result.project_analysis
        )

        # 5. 기획서 리뷰
        if on_spec_review:
            spec_approved = on_spec_review(result.feature_spec)
            if not spec_approved:
                self._log("기획서 미승인")
                return result

        # 6. 태스크 분해
        result.tasks = self.decompose_to_tasks(
            spec=result.feature_spec,
            project_analysis=result.project_analysis
        )

        # 7. 태스크 리뷰 및 승인
        if on_tasks_review:
            result.approved = on_tasks_review(result.tasks)
        else:
            result.approved = False

        self._log("Plan Mode 완료", {
            "approved": result.approved,
            "task_count": len(result.tasks)
        })

        return result

    # ============================================================
    # Orchestrator 호환 메서드
    # ============================================================

    def init_project(
        self,
        project_path: str,
        file_list: list[str] | None = None
    ) -> ProjectAnalysis:
        """프로젝트를 초기화하고 분석합니다. (orchestrator 호환)"""
        return self.analyze_project(project_path)

    def clarify_goal(
        self,
        user_goal: str,
        on_question: Callable[[ClarificationQuestion], str] | None = None
    ) -> dict[str, Any]:
        """모호한 요구사항을 명확화합니다. (orchestrator 호환)"""
        self._log(f"요구사항 명확화: {user_goal[:100]}")
        self.reset_conversation()

        prompt = f"""다음 요구사항을 분석하고 명확화가 필요한 부분이 있는지 확인하세요.

요구사항: {user_goal}

JSON 형식으로 응답:
```json
{{
    "is_clear": true/false,
    "questions": [
        {{"question": "질문 내용", "context": "배경 설명", "options": ["선택지1", "선택지2"]}}
    ],
    "final_requirements": {{
        "summary": "명확화된 요구사항 요약",
        "details": ["세부 사항1", "세부 사항2"]
    }}
}}
```
"""

        response = self._send_message(prompt, use_tools=False)
        result = self._parse_json_response(response)

        if "content" in result and isinstance(result["content"], dict):
            result = result["content"]

        # 질문이 있고 콜백이 있으면 질문 수행
        if not result.get("is_clear", True) and on_question and result.get("questions"):
            answers = []
            for q_data in result["questions"]:
                question = ClarificationQuestion(
                    question=q_data.get("question", ""),
                    context=q_data.get("context", ""),
                    options=q_data.get("options", [])
                )
                answer = on_question(question)
                answers.append({"question": question.question, "answer": answer})

            result["answers"] = answers

        return result

    def plan(
        self,
        user_goal: str,
        project_analysis: ProjectAnalysis | None = None
    ) -> TaskPlan:
        """목표를 분석하고 작업 계획을 수립합니다. (orchestrator 호환)"""
        self._log(f"작업 계획 수립: {user_goal[:100]}")

        # 프로젝트 분석이 없으면 수행
        if project_analysis is None:
            project_analysis = self.analyze_project()

        # 간단한 FeatureSpec 생성
        spec = FeatureSpec(
            feature_name=user_goal[:50],
            summary=user_goal,
            requirements=[user_goal]
        )

        # 태스크 분해
        plan_tasks = self.decompose_to_tasks(spec, project_analysis)

        # TaskPlan 형식으로 변환
        tasks = []
        for pt in plan_tasks:
            tasks.append({
                "id": pt.id,
                "title": pt.title,
                "description": pt.goal,
                "goal": pt.goal,
                "files_to_modify": pt.files_to_modify,
                "expected_logic": pt.expected_logic,
                "dependencies": pt.dependencies,
                "acceptance_criteria": pt.acceptance_criteria
            })

        return TaskPlan(
            goal=user_goal,
            tasks=tasks,
            summary=f"{len(tasks)}개의 태스크로 분해됨",
            estimated_complexity="medium" if len(tasks) <= 5 else "high"
        )

    def analyze_code(
        self,
        code: str,
        file_path: str,
        question: str | None = None
    ) -> dict[str, Any]:
        """코드를 분석합니다. (orchestrator 호환)"""
        self._log(f"코드 분석: {file_path}")
        self.reset_conversation()

        prompt = f"""다음 코드를 분석하세요.

파일: {file_path}
{f"질문: {question}" if question else ""}

```
{code[:3000]}
```

JSON 형식으로 응답:
```json
{{
    "summary": "코드 요약",
    "issues": ["발견된 이슈들"],
    "suggestions": ["개선 제안"],
    "complexity": "low/medium/high"
}}
```
"""

        response = self._send_message(prompt, use_tools=False)
        result = self._parse_json_response(response)

        if "content" in result and isinstance(result["content"], dict):
            result = result["content"]

        return result

    def review_changes(
        self,
        diff: str,
        context: str | None = None
    ) -> dict[str, Any]:
        """코드 변경사항을 리뷰합니다. (orchestrator 호환)"""
        self._log("변경사항 리뷰")
        self.reset_conversation()

        prompt = f"""다음 코드 변경사항을 리뷰하세요.

{f"컨텍스트: {context}" if context else ""}

```diff
{diff[:5000]}
```

JSON 형식으로 응답:
```json
{{
    "approved": true/false,
    "summary": "변경사항 요약",
    "issues": ["발견된 이슈들"],
    "suggestions": ["개선 제안"]
}}
```
"""

        response = self._send_message(prompt, use_tools=False)
        result = self._parse_json_response(response)

        if "content" in result and isinstance(result["content"], dict):
            result = result["content"]

        return result

    def close(self):
        """리소스를 정리합니다."""
        self._log("GeminiCLIWrapper 종료")
        self.conversation_history = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
