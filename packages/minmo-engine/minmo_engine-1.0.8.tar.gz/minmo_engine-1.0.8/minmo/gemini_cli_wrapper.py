"""
Gemini CLI Wrapper - Minmo-Engine의 지휘관 (Commander)
Google Gen AI SDK v1.0+ 표준을 사용하여 Plan Mode를 지원
"""

import os
import json
from typing import Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Google Gen AI SDK v1.0+ 표준 임포트
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


# ============================================================
# Gemini CLI Wrapper 클래스 (Google Gen AI SDK v1.0+)
# ============================================================
class GeminiCLIWrapper:
    """
    Gemini CLI Wrapper - 지휘관 역할

    Google Gen AI SDK v1.0+를 사용하여
    프로젝트 분석, 인터뷰, 계획 수립을 수행합니다.
    """

    # 기본 모델 설정 (최신 모델)
    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        working_directory: str | None = None,
        timeout_seconds: int = 120,
        on_output: Callable[[str], None] | None = None,
        on_error: Callable[[str, dict], None] | None = None,
        verbose: bool = False
    ):
        """
        GeminiCLIWrapper 초기화 (Google Gen AI SDK v1.0+)

        Args:
            api_key: Google API 키 (없으면 환경변수에서 로드)
            model: 사용할 모델명 (기본: gemini-2.5-flash)
            working_directory: 작업 디렉토리 (기본: 현재 디렉토리)
            timeout_seconds: 명령 타임아웃 (초)
            on_output: 출력 콜백 함수
            on_error: 에러 콜백 함수
            verbose: 상세 출력 여부
        """
        self.working_directory = working_directory or os.getcwd()
        self.timeout_seconds = timeout_seconds
        self.on_output = on_output
        self.on_error = on_error
        self.verbose = verbose
        self.model_name = model or self.DEFAULT_MODEL

        # API 키 설정
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY 또는 GOOGLE_API_KEY 환경변수를 설정하거나 "
                "api_key 매개변수를 제공해주세요."
            )

        # Google Gen AI 클라이언트 초기화
        self.client = genai.Client(api_key=self.api_key)

        # 도구 맵 초기화 (FunctionTool 직접 호출 문제 해결)
        self.tool_map: dict[str, Callable] = {}
        self._register_tools()

        # 대화 기록
        self._conversation_history: list[types.Content] = []

        # Scribe DB 초기화
        try:
            init_database()
        except Exception:
            pass

    def _register_tools(self) -> None:
        """도구 함수들을 tool_map에 등록합니다."""
        self.tool_map = {
            "analyze_directory": self._tool_analyze_directory,
            "read_file": self._tool_read_file,
            "search_code": self._tool_search_code,
            "get_project_conventions": self._tool_get_conventions,
            "get_project_architecture": self._tool_get_architecture,
        }

    # ============================================================
    # 도구 함수 구현 (tool_map에서 호출됨)
    # ============================================================

    def _tool_analyze_directory(self, path: str = ".") -> dict[str, Any]:
        """디렉토리 구조를 분석합니다."""
        target_path = Path(self.working_directory) / path
        if not target_path.exists():
            return {"error": f"경로를 찾을 수 없습니다: {path}"}

        files = []
        dirs = []

        try:
            for item in target_path.iterdir():
                if item.name.startswith('.'):
                    continue
                if item.is_file():
                    files.append(item.name)
                elif item.is_dir():
                    dirs.append(item.name)
        except PermissionError:
            return {"error": f"권한 오류: {path}"}

        return {
            "path": str(target_path),
            "files": files[:50],
            "directories": dirs[:20],
            "file_count": len(files),
            "dir_count": len(dirs)
        }

    def _tool_read_file(self, file_path: str, max_lines: int = 200) -> dict[str, Any]:
        """파일 내용을 읽습니다."""
        target_path = Path(self.working_directory) / file_path
        if not target_path.exists():
            return {"error": f"파일을 찾을 수 없습니다: {file_path}"}

        try:
            content = target_path.read_text(encoding="utf-8")
            lines = content.splitlines()

            return {
                "path": file_path,
                "content": "\n".join(lines[:max_lines]),
                "total_lines": len(lines),
                "truncated": len(lines) > max_lines
            }
        except Exception as e:
            return {"error": f"파일 읽기 오류: {str(e)}"}

    def _tool_search_code(self, query: str, file_pattern: str = "*.py") -> dict[str, Any]:
        """코드베이스에서 검색합니다."""
        import re

        results = []
        target_path = Path(self.working_directory)

        for file_path in target_path.rglob(file_pattern):
            if any(part.startswith('.') for part in file_path.parts):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                for i, line in enumerate(content.splitlines(), 1):
                    if re.search(query, line, re.IGNORECASE):
                        results.append({
                            "file": str(file_path.relative_to(target_path)),
                            "line": i,
                            "content": line.strip()[:100]
                        })

                        if len(results) >= 20:
                            break
            except Exception:
                continue

            if len(results) >= 20:
                break

        return {
            "query": query,
            "pattern": file_pattern,
            "results": results,
            "count": len(results)
        }

    def _tool_get_conventions(self) -> dict[str, Any]:
        """프로젝트 컨벤션을 분석합니다."""
        try:
            from minmo.scribe_mcp import _get_conventions_impl
            return _get_conventions_impl()
        except Exception as e:
            return {"error": f"컨벤션 분석 오류: {str(e)}"}

    def _tool_get_architecture(self) -> dict[str, Any]:
        """프로젝트 아키텍처 정보를 분석합니다."""
        try:
            from minmo.scribe_mcp import _get_architecture_info_impl
            return _get_architecture_info_impl()
        except Exception as e:
            return {"error": f"아키텍처 분석 오류: {str(e)}"}

    # ============================================================
    # 도구 정의 (Google Gen AI SDK v1.0+ 형식)
    # ============================================================

    def _get_tool_declarations(self) -> list[types.Tool]:
        """도구 선언을 반환합니다."""
        tools = [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="analyze_directory",
                        description="디렉토리 구조를 분석합니다.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "path": types.Schema(
                                    type=types.Type.STRING,
                                    description="분석할 경로 (기본: '.')"
                                )
                            }
                        )
                    ),
                    types.FunctionDeclaration(
                        name="read_file",
                        description="파일 내용을 읽습니다.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "file_path": types.Schema(
                                    type=types.Type.STRING,
                                    description="읽을 파일 경로"
                                ),
                                "max_lines": types.Schema(
                                    type=types.Type.INTEGER,
                                    description="최대 줄 수 (기본: 200)"
                                )
                            },
                            required=["file_path"]
                        )
                    ),
                    types.FunctionDeclaration(
                        name="search_code",
                        description="코드베이스에서 패턴을 검색합니다.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "query": types.Schema(
                                    type=types.Type.STRING,
                                    description="검색 쿼리 (정규식 지원)"
                                ),
                                "file_pattern": types.Schema(
                                    type=types.Type.STRING,
                                    description="파일 패턴 (기본: '*.py')"
                                )
                            },
                            required=["query"]
                        )
                    ),
                    types.FunctionDeclaration(
                        name="get_project_conventions",
                        description="프로젝트의 코딩 컨벤션을 분석합니다."
                    ),
                    types.FunctionDeclaration(
                        name="get_project_architecture",
                        description="프로젝트의 아키텍처 정보를 분석합니다."
                    )
                ]
            )
        ]
        return tools

    # ============================================================
    # 도구 호출 처리 (tool_map 사용)
    # ============================================================

    def _execute_tool_call(self, tool_call: types.FunctionCall) -> dict[str, Any]:
        """
        도구 호출을 실행합니다.
        tool_map을 사용하여 FunctionTool 직접 호출 문제를 해결합니다.
        """
        tool_name = tool_call.name
        tool_args = dict(tool_call.args) if tool_call.args else {}

        if tool_name not in self.tool_map:
            return {"error": f"알 수 없는 도구: {tool_name}"}

        try:
            tool_func = self.tool_map[tool_name]
            result = tool_func(**tool_args)
            return result
        except Exception as e:
            return {"error": f"도구 실행 오류: {str(e)}"}

    def _process_tool_calls(
        self,
        response: types.GenerateContentResponse
    ) -> tuple[list[types.Part], bool]:
        """
        응답에서 도구 호출을 처리합니다.

        Returns:
            tuple: (도구 응답 파트 리스트, 도구 호출 여부)
        """
        tool_responses = []
        has_tool_calls = False

        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.function_call:
                    has_tool_calls = True
                    result = self._execute_tool_call(part.function_call)

                    tool_responses.append(
                        types.Part.from_function_response(
                            name=part.function_call.name,
                            response=result
                        )
                    )

        return tool_responses, has_tool_calls

    # ============================================================
    # 로깅
    # ============================================================

    def _log(self, content: str, metadata: dict | None = None) -> None:
        """Scribe를 통해 로그를 기록합니다."""
        try:
            log_event(
                agent="commander",
                content=content,
                metadata=json.dumps(metadata, ensure_ascii=False) if metadata else None
            )
        except Exception:
            pass

        if self.verbose and self.on_output:
            self.on_output(f"[Commander] {content}")

    # ============================================================
    # 메시지 전송
    # ============================================================

    def _send_message(
        self,
        message: str,
        system_instruction: str | None = None,
        use_tools: bool = False,
        max_tool_rounds: int = 5
    ) -> str:
        """
        Gemini에 메시지를 보내고 응답을 받습니다.

        Args:
            message: 사용자 메시지
            system_instruction: 시스템 지시사항
            use_tools: 도구 사용 여부
            max_tool_rounds: 최대 도구 호출 라운드

        Returns:
            모델 응답 텍스트
        """
        # 설정 구성
        config = types.GenerateContentConfig(
            system_instruction=system_instruction or COMMANDER_CLI_CONSTITUTION,
            temperature=0.7,
        )

        if use_tools:
            config.tools = self._get_tool_declarations()

        # 대화 기록에 사용자 메시지 추가
        contents = self._conversation_history.copy()
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=message)]
            )
        )

        # 도구 호출 루프
        for round_num in range(max_tool_rounds):
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            if use_tools:
                tool_responses, has_tool_calls = self._process_tool_calls(response)

                if has_tool_calls:
                    # 모델 응답 추가
                    contents.append(response.candidates[0].content)

                    # 도구 응답 추가
                    contents.append(
                        types.Content(
                            role="user",
                            parts=tool_responses
                        )
                    )
                    continue

            # 도구 호출이 없으면 루프 종료
            break

        # 최종 응답 텍스트 추출
        response_text = ""
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.text:
                    response_text += part.text

        # 대화 기록 업데이트
        self._conversation_history = contents
        self._conversation_history.append(response.candidates[0].content)

        return response_text

    def _parse_json_response(self, text: str) -> dict[str, Any]:
        """응답에서 JSON을 추출하고 파싱합니다."""
        import re

        # JSON 블록 추출
        json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 순수 JSON 시도
        json_patterns = [
            r"\{[\s\S]*\}",
            r"\[[\s\S]*\]"
        ]
        for pattern in json_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue

        # 파싱 실패 시 텍스트 응답 반환
        return {"type": "text", "content": text}

    def check_login_status(self) -> bool:
        """API 키 유효성을 확인합니다."""
        try:
            # 간단한 테스트 요청
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Hello",
                config=types.GenerateContentConfig(
                    max_output_tokens=10
                )
            )
            return response is not None
        except Exception:
            return False

    # ============================================================
    # 핵심 메서드
    # ============================================================

    def analyze_project(self, project_path: str | None = None) -> ProjectAnalysis:
        """
        프로젝트 구조를 분석합니다.

        Args:
            project_path: 분석할 프로젝트 경로 (기본: 작업 디렉토리)

        Returns:
            ProjectAnalysis: 프로젝트 분석 결과
        """
        path = project_path or self.working_directory
        self._log("프로젝트 분석 시작", {"path": path})

        prompt = f"""다음 디렉토리의 프로젝트를 분석해주세요: {path}

도구를 사용하여 프로젝트 구조를 파악한 후, 다음 JSON 형식으로 응답해주세요:
```json
{{
  "type": "analysis",
  "content": {{
    "languages": ["사용된 프로그래밍 언어"],
    "frameworks": ["사용된 프레임워크"],
    "structure_summary": "프로젝트 구조 요약",
    "key_files": ["중요한 파일 경로"],
    "conventions": ["감지된 코딩 컨벤션"],
    "dependencies": ["주요 의존성"]
  }}
}}
```
"""

        response = self._send_message(prompt, use_tools=True)
        parsed = self._parse_json_response(response)

        content = parsed.get("content", {})

        analysis = ProjectAnalysis(
            project_path=path,
            languages=content.get("languages", []),
            frameworks=content.get("frameworks", []),
            structure_summary=content.get("structure_summary", ""),
            key_files=content.get("key_files", []),
            conventions=content.get("conventions", []),
            dependencies=content.get("dependencies", [])
        )

        self._log("프로젝트 분석 완료", {
            "languages": analysis.languages,
            "frameworks": analysis.frameworks
        })

        return analysis

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

        context = ""
        if project_analysis:
            context = f"""
프로젝트 정보:
- 언어: {', '.join(project_analysis.languages)}
- 프레임워크: {', '.join(project_analysis.frameworks)}
- 구조: {project_analysis.structure_summary}
- 컨벤션: {', '.join(project_analysis.conventions)}
"""

        prompt = f"""사용자 요구사항: {user_goal}

{context}

위 요구사항을 구현하기 전에 명확히 해야 할 질문을 3-7개 생성해주세요.
각 질문은 다음 영역 중 하나에 초점을 맞춥니다:
- architecture: 아키텍처, 구조
- data_model: 데이터 구조, 스키마
- exception_handling: 에러 처리
- convention: 코딩 컨벤션
- integration: 외부 시스템 연동
- testing: 테스트 전략

JSON 형식으로 응답:
```json
{{
  "type": "interview",
  "content": {{
    "questions": [
      {{
        "question": "질문 내용",
        "focus": "architecture",
        "options": ["옵션1", "옵션2", "직접 입력"],
        "context": "질문 배경"
      }}
    ]
  }}
}}
```
"""

        response = self._send_message(prompt, use_tools=True)
        parsed = self._parse_json_response(response)

        content = parsed.get("content", {})
        raw_questions = content.get("questions", [])

        questions = []
        for q in raw_questions:
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

        self._log("인터뷰 질문 생성 완료", {"count": len(questions)})
        return questions

    def generate_feature_spec(
        self,
        user_goal: str,
        interview_answers: list[InterviewAnswer],
        project_analysis: ProjectAnalysis | None = None
    ) -> FeatureSpec:
        """
        인터뷰 답변을 기반으로 기획서를 생성합니다.

        Args:
            user_goal: 사용자 목표
            interview_answers: 인터뷰 답변 목록
            project_analysis: 프로젝트 분석 결과

        Returns:
            FeatureSpec: 기획서
        """
        self._log("기획서 생성 시작", {"goal": user_goal})

        qa_text = "\n".join([
            f"Q: {ia.question.question}\nA: {ia.answer}"
            for ia in interview_answers
        ])

        context = ""
        if project_analysis:
            context = f"프로젝트: {', '.join(project_analysis.languages)} / {', '.join(project_analysis.frameworks)}"

        prompt = f"""인터뷰 결과를 바탕으로 기능 기획서를 작성해주세요.

요구사항: {user_goal}

{context}

인터뷰 내용:
{qa_text}

JSON 형식으로 기획서 작성:
```json
{{
  "type": "feature_spec",
  "content": {{
    "feature_name": "기능명_snake_case",
    "summary": "기능 요약",
    "requirements": ["요구사항 1", "요구사항 2"],
    "architecture_decisions": ["아키텍처 결정사항"],
    "data_model": {{"엔티티": {{"필드": "타입"}}}},
    "error_handling": ["에러 처리 방안"],
    "conventions": ["준수할 컨벤션"],
    "constraints": ["제약 조건"],
    "out_of_scope": ["범위 외 항목"]
  }}
}}
```
"""

        response = self._send_message(prompt, use_tools=True)
        parsed = self._parse_json_response(response)

        content = parsed.get("content", {})

        spec = FeatureSpec(
            feature_name=content.get("feature_name", "unnamed_feature"),
            summary=content.get("summary", ""),
            requirements=content.get("requirements", []),
            architecture_decisions=content.get("architecture_decisions", []),
            data_model=content.get("data_model", {}),
            error_handling=content.get("error_handling", []),
            conventions=content.get("conventions", []),
            constraints=content.get("constraints", []),
            out_of_scope=content.get("out_of_scope", [])
        )

        self._log("기획서 생성 완료", {"feature": spec.feature_name})
        return spec

    def decompose_to_tasks(
        self,
        spec: FeatureSpec,
        project_analysis: ProjectAnalysis | None = None
    ) -> list[PlanTask]:
        """
        기획서를 구체적인 태스크로 분해합니다.

        Args:
            spec: 기능 기획서
            project_analysis: 프로젝트 분석 결과

        Returns:
            태스크 목록
        """
        self._log("태스크 분해 시작", {"feature": spec.feature_name})

        spec_summary = f"""
기능: {spec.feature_name}
요약: {spec.summary}
요구사항: {', '.join(spec.requirements)}
아키텍처: {', '.join(spec.architecture_decisions)}
"""

        prompt = f"""다음 기획서를 구체적인 작업 태스크로 분해해주세요.

{spec_summary}

각 태스크는 반드시 다음을 포함해야 합니다:
- 목표 (goal)
- 수정할 파일 (files_to_modify)
- 예상 로직 (expected_logic)
- 완료 조건 (acceptance_criteria)

JSON 형식:
```json
{{
  "type": "task_list",
  "content": {{
    "tasks": [
      {{
        "id": "task_001",
        "title": "작업 제목",
        "goal": "구체적인 목표",
        "files_to_modify": ["파일1.py", "파일2.py"],
        "expected_logic": "구현할 로직 설명",
        "dependencies": [],
        "acceptance_criteria": ["완료 조건 1", "완료 조건 2"]
      }}
    ]
  }}
}}
```
"""

        response = self._send_message(prompt, use_tools=True)
        parsed = self._parse_json_response(response)

        content = parsed.get("content", {})
        raw_tasks = content.get("tasks", [])

        tasks = []
        for t in raw_tasks:
            tasks.append(PlanTask(
                id=t.get("id", f"task_{len(tasks)+1:03d}"),
                title=t.get("title", ""),
                goal=t.get("goal", ""),
                files_to_modify=t.get("files_to_modify", []),
                expected_logic=t.get("expected_logic", ""),
                dependencies=t.get("dependencies", []),
                acceptance_criteria=t.get("acceptance_criteria", [])
            ))

        self._log("태스크 분해 완료", {"count": len(tasks)})
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

        1. 프로젝트 분석
        2. 인터뷰 질문 생성 및 수집
        3. 기획서 생성
        4. 태스크 분해
        5. 사용자 승인

        Args:
            user_goal: 사용자 요구사항
            on_question: 질문 콜백 (질문 → 답변)
            on_spec_review: 기획서 리뷰 콜백
            on_tasks_review: 태스크 리뷰 콜백

        Returns:
            PlanModeResult: Plan Mode 결과
        """
        self._log("Plan Mode 시작", {"goal": user_goal})

        result = PlanModeResult()

        # 1. 프로젝트 분석
        try:
            result.project_analysis = self.analyze_project()
        except Exception as e:
            self._log(f"프로젝트 분석 실패: {str(e)}")
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

    def close(self):
        """리소스를 정리합니다."""
        self._log("GeminiCLIWrapper 종료")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
