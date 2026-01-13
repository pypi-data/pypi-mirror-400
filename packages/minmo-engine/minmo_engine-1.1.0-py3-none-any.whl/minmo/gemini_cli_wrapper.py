"""
Gemini CLI Wrapper - Minmo-Engine의 지휘관 (Commander)

pexpect를 사용하여 Gemini CLI를 제어합니다.
API KEY 불필요 - `gemini login`으로 OAuth 인증 사용
"""

import os
import re
import json
import subprocess
import shutil
from typing import Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

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
# Gemini CLI Wrapper 클래스 (pexpect 기반)
# ============================================================
class GeminiCLIWrapper:
    """
    Gemini CLI Wrapper - 지휘관 역할

    pexpect를 사용하여 Gemini CLI를 제어합니다.
    API KEY 불필요 - `gemini login`으로 OAuth 인증
    """

    def __init__(
        self,
        working_directory: str | None = None,
        timeout_seconds: int = 120,
        on_output: Callable[[str], None] | None = None,
        on_error: Callable[[str, dict], None] | None = None,
        verbose: bool = False
    ):
        """
        GeminiCLIWrapper 초기화

        Args:
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

        # Gemini CLI 경로 찾기
        self.gemini_path = self._find_gemini_cli()

        # Scribe DB 초기화
        try:
            init_database()
        except Exception:
            pass

    def _find_gemini_cli(self) -> str:
        """Gemini CLI 경로를 찾습니다."""
        # 환경변수에서 찾기
        gemini_path = os.environ.get("GEMINI_CLI_PATH")
        if gemini_path and os.path.exists(gemini_path):
            return gemini_path

        # PATH에서 찾기
        gemini_path = shutil.which("gemini")
        if gemini_path:
            return gemini_path

        # Windows에서 npm global 경로
        if os.name == "nt":
            npm_path = os.path.expandvars(r"%APPDATA%\npm\gemini.cmd")
            if os.path.exists(npm_path):
                return npm_path

        # 찾지 못한 경우 기본값 반환 (실행 시 에러 발생)
        return "gemini"

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

    def _run_gemini(self, prompt: str) -> str:
        """
        Gemini CLI를 실행하고 결과를 반환합니다.

        Args:
            prompt: Gemini에 전달할 프롬프트

        Returns:
            Gemini 응답 텍스트
        """
        self._log(f"Gemini CLI 실행: {prompt[:100]}...")

        try:
            # subprocess로 gemini CLI 실행
            result = subprocess.run(
                [self.gemini_path, prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                cwd=self.working_directory,
                encoding="utf-8",
                errors="replace"
            )

            if result.returncode != 0:
                error_msg = result.stderr or "Unknown error"
                self._log(f"Gemini CLI 에러: {error_msg}")
                if self.on_error:
                    self.on_error("gemini_cli_error", {"error": error_msg})
                return ""

            output = result.stdout.strip()
            self._log(f"Gemini CLI 응답: {len(output)} chars")

            if self.on_output and self.verbose:
                self.on_output(output)

            return output

        except subprocess.TimeoutExpired:
            self._log("Gemini CLI 타임아웃")
            if self.on_error:
                self.on_error("timeout", {"timeout_seconds": self.timeout_seconds})
            return ""

        except FileNotFoundError:
            error_msg = (
                "Gemini CLI를 찾을 수 없습니다. "
                "npm install -g @google/gemini-cli로 설치하고 "
                "gemini login으로 인증하세요."
            )
            self._log(error_msg)
            if self.on_error:
                self.on_error("not_found", {"message": error_msg})
            return ""

        except Exception as e:
            self._log(f"Gemini CLI 실행 오류: {e}")
            if self.on_error:
                self.on_error("execution_error", {"error": str(e)})
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

        return {"raw_response": text}

    def check_login_status(self) -> bool:
        """
        Gemini CLI 로그인 상태를 확인합니다.

        Returns:
            로그인되어 있으면 True
        """
        try:
            result = subprocess.run(
                [self.gemini_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

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

        # 프로젝트 구조 수집
        structure = self._collect_project_structure(target_path)

        prompt = f"""{COMMANDER_CLI_CONSTITUTION}

다음 프로젝트 구조를 분석하세요:

{structure}

JSON 형식으로 응답:
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

        response = self._run_gemini(prompt)
        data = self._parse_json_response(response)

        # content 키가 있으면 추출
        if "content" in data:
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

    def _collect_project_structure(self, path: str, max_depth: int = 3) -> str:
        """프로젝트 구조를 문자열로 수집합니다."""
        lines = []
        root_path = Path(path)

        def _walk(current: Path, depth: int, prefix: str = ""):
            if depth > max_depth:
                return

            try:
                items = sorted(current.iterdir(), key=lambda x: (x.is_file(), x.name))
            except PermissionError:
                return

            # 무시할 디렉토리
            ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}

            for item in items:
                if item.name.startswith('.') and item.name != ".gitignore":
                    continue
                if item.name in ignore_dirs:
                    continue

                if item.is_file():
                    lines.append(f"{prefix}{item.name}")
                elif item.is_dir():
                    lines.append(f"{prefix}{item.name}/")
                    _walk(item, depth + 1, prefix + "  ")

        _walk(root_path, 0)
        return "\n".join(lines[:100])  # 최대 100줄

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

        context = ""
        if project_analysis:
            context = f"""
프로젝트 정보:
- 언어: {', '.join(project_analysis.languages)}
- 프레임워크: {', '.join(project_analysis.frameworks)}
- 구조: {project_analysis.structure_summary}
"""

        prompt = f"""{COMMANDER_CLI_CONSTITUTION}

사용자 요구사항: {user_goal}
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

        response = self._run_gemini(prompt)
        data = self._parse_json_response(response)

        if "content" in data:
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

        answers_text = "\n".join([
            f"Q: {a.question.question}\nA: {a.answer}"
            for a in interview_answers
        ])

        prompt = f"""{COMMANDER_CLI_CONSTITUTION}

요구사항: {user_goal}

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

        response = self._run_gemini(prompt)
        data = self._parse_json_response(response)

        if "content" in data:
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

        prompt = f"""{COMMANDER_CLI_CONSTITUTION}

기획서:
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

        response = self._run_gemini(prompt)
        data = self._parse_json_response(response)

        if "content" in data:
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

        prompt = f"""{COMMANDER_CLI_CONSTITUTION}

다음 요구사항을 분석하고 명확화가 필요한 부분이 있는지 확인하세요.

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

        response = self._run_gemini(prompt)
        result = self._parse_json_response(response)

        if "content" in result:
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

        prompt = f"""{COMMANDER_CLI_CONSTITUTION}

다음 코드를 분석하세요.

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

        response = self._run_gemini(prompt)
        result = self._parse_json_response(response)

        if "content" in result:
            result = result["content"]

        return result

    def review_changes(
        self,
        diff: str,
        context: str | None = None
    ) -> dict[str, Any]:
        """코드 변경사항을 리뷰합니다. (orchestrator 호환)"""
        self._log("변경사항 리뷰")

        prompt = f"""{COMMANDER_CLI_CONSTITUTION}

다음 코드 변경사항을 리뷰하세요.

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

        response = self._run_gemini(prompt)
        result = self._parse_json_response(response)

        if "content" in result:
            result = result["content"]

        return result

    def close(self):
        """리소스를 정리합니다."""
        self._log("GeminiCLIWrapper 종료")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
