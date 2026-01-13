"""
Minmo CLI - 세련된 터미널 인터페이스

멀티 모드 지원:
- /plan [명령]: 지휘관(Gemini) 심층 인터뷰 기반 기획/설계 모드
- /direct [명령]: 지휘관 건너뛰고 작업자(Claude)에게 바로 전달
- /analyze [명령]: 프로젝트/파일 분석 후 리포트 출력 (수정 X)
- /free [명령]: 기본 모드, 지휘관이 판단하여 자동 라우팅
- /help: 도움말 표시
"""

import sys
import os
import io
import json
import subprocess
import signal
import time
import argparse
import re
import threading
from pathlib import Path
from typing import Optional, Tuple, Callable, Any
from enum import Enum
from dataclasses import dataclass

# Windows 콘솔 인코딩 문제 해결 (cp949 -> UTF-8)
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.table import Table
from rich.tree import Tree
from rich.markdown import Markdown
from rich.theme import Theme
from rich import box

# prompt_toolkit - 고급 CLI 입력 시스템
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style as PTStyle
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import FormattedText

from minmo import __version__
from minmo.orchestrator import MinmoOrchestrator, ensure_minmo_data_dir
from minmo.indexer import CodeIndexer
from minmo.gemini_cli_wrapper import (
    GeminiCLIWrapper,
    InterviewQuestion,
    FeatureSpec,
    PlanTask,
    PlanModeResult,
    ProjectAnalysis,
)
from minmo.scribe_mcp import (
    _get_conventions_impl as get_conventions,
    _get_architecture_info_impl as get_architecture_info,
    _save_feature_spec_impl as save_feature_spec,
    call_get_usage_stats,
    MODEL_CONTEXT_WINDOWS,
)

# ============================================================
# Minmo 커스텀 테마 - 터미널과 조화로운 색상
# ============================================================
MINMO_THEME = Theme({
    # 마크다운 스타일
    "markdown.h1": "bold bright_cyan underline",
    "markdown.h2": "bold cyan",
    "markdown.h3": "bold blue",
    "markdown.h4": "bold bright_blue",
    "markdown.code": "bright_green on grey23",
    "markdown.code_block": "bright_green on grey15",
    "markdown.link": "bright_magenta underline",
    "markdown.link_url": "dim magenta",
    "markdown.item.bullet": "cyan",
    "markdown.item.number": "cyan",
    "markdown.block_quote": "italic bright_black",
    "markdown.hr": "dim cyan",
    "markdown.strong": "bold bright_white",
    "markdown.emph": "italic bright_white",
    # AI 응답 전용 스타일
    "ai.response": "white",
    "ai.thinking": "dim italic",
    "ai.code": "bright_green",
    "ai.highlight": "bright_yellow",
})

console = Console(force_terminal=True, theme=MINMO_THEME)


def render_markdown(text: str, code_theme: str = "monokai") -> Markdown:
    """
    텍스트를 rich Markdown으로 렌더링합니다.

    Args:
        text: 마크다운 형식의 텍스트
        code_theme: 코드 블록에 사용할 Pygments 테마

    Returns:
        rich.markdown.Markdown 객체
    """
    return Markdown(text, code_theme=code_theme)


def print_ai_response(response: str, title: str = None, border_style: str = "cyan"):
    """
    AI 응답을 마크다운 형식으로 예쁘게 출력합니다.

    Args:
        response: AI 응답 텍스트 (마크다운 형식)
        title: 패널 제목 (선택)
        border_style: 테두리 색상
    """
    md = render_markdown(response)
    if title:
        console.print(Panel(md, title=title, box=box.ROUNDED, border_style=border_style))
    else:
        console.print(md)


# ============================================================
# StatusManager - 인플레이스 상태 표시 (rich.status.Status 래퍼)
# ============================================================
class StatusManager:
    """
    Gemini CLI 대기 시 인플레이스 상태 표시를 관리합니다.

    rich.status.Status를 사용하여 한 줄에서 스피너와 경과 시간을 표시합니다.
    """

    def __init__(self, console_instance: Console = None, spinner: str = "dots"):
        """
        StatusManager 초기화

        Args:
            console_instance: Rich Console 인스턴스
            spinner: 스피너 종류 (dots, arc, bouncingBar, etc.)
        """
        self.console = console_instance or console
        self.spinner = spinner
        self._status = None
        self._current_operation = ""

    def start(self, operation: str = "처리 중"):
        """상태 표시를 시작합니다."""
        self._current_operation = operation
        self._status = self.console.status(
            f"[cyan]{operation}...[/cyan] 0.0s",
            spinner=self.spinner
        )
        self._status.start()

    def update(self, operation: str, elapsed: float):
        """
        상태를 업데이트합니다 (인플레이스).

        Args:
            operation: 현재 작업 이름
            elapsed: 경과 시간 (초)
        """
        if self._status:
            self._current_operation = operation
            self._status.update(f"[cyan]{operation}...[/cyan] {elapsed:.1f}s")

    def stop(self, success: bool = True, message: str = None):
        """상태 표시를 종료합니다."""
        if self._status:
            self._status.stop()
            self._status = None

            # 완료 메시지 출력
            if message:
                if success:
                    self.console.print(f"[green]✓[/green] {message}")
                else:
                    self.console.print(f"[red]✗[/red] {message}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop(success=exc_type is None)
        return False


def create_status_callback(status_manager: StatusManager):
    """
    GeminiCLIWrapper용 상태 콜백 함수를 생성합니다.

    Args:
        status_manager: StatusManager 인스턴스

    Returns:
        on_status 콜백 함수
    """
    def on_status(operation: str, elapsed: float):
        status_manager.update(operation, elapsed)
    return on_status


# ============================================================
# 멀티 모드 시스템
# ============================================================

class MinmoMode(Enum):
    """Minmo 동작 모드"""
    FREE = "free"       # 기본 모드 - 지휘관이 자동 판단
    PLAN = "plan"       # 기획 모드 - Speckit 인터뷰 강제 활성화
    DIRECT = "direct"   # 직접 모드 - 지휘관 건너뛰기
    ANALYZE = "analyze" # 분석 모드 - 분석만 수행
    HELP = "help"       # 도움말


@dataclass
class ParsedCommand:
    """파싱된 커맨드"""
    mode: MinmoMode
    goal: str
    raw_input: str


def parse_command(user_input: str) -> ParsedCommand:
    """
    사용자 입력에서 모드와 목표를 파싱합니다.

    접두사:
    - /plan [명령]: PLAN 모드
    - /direct [명령]: DIRECT 모드
    - /analyze [명령]: ANALYZE 모드
    - /free [명령]: FREE 모드 (명시적)
    - /help: HELP 모드
    - (접두사 없음): FREE 모드 (기본)

    Args:
        user_input: 원본 사용자 입력

    Returns:
        ParsedCommand 객체
    """
    stripped = user_input.strip()

    # 명령어 패턴 매칭
    command_pattern = r'^/(\w+)(?:\s+(.*))?$'
    match = re.match(command_pattern, stripped, re.DOTALL)

    if match:
        command = match.group(1).lower()
        goal = (match.group(2) or "").strip()

        mode_map = {
            "plan": MinmoMode.PLAN,
            "direct": MinmoMode.DIRECT,
            "analyze": MinmoMode.ANALYZE,
            "free": MinmoMode.FREE,
            "help": MinmoMode.HELP,
        }

        mode = mode_map.get(command, MinmoMode.FREE)

        # 알 수 없는 명령어는 FREE 모드로 전체 입력을 목표로
        if command not in mode_map:
            return ParsedCommand(
                mode=MinmoMode.FREE,
                goal=stripped,
                raw_input=user_input
            )

        return ParsedCommand(
            mode=mode,
            goal=goal,
            raw_input=user_input
        )

    # 접두사 없음: FREE 모드
    return ParsedCommand(
        mode=MinmoMode.FREE,
        goal=stripped,
        raw_input=user_input
    )


def show_mode_panel(mode: MinmoMode, goal: str = ""):
    """
    현재 모드를 상단 패널로 표시합니다.

    Args:
        mode: 현재 동작 모드
        goal: 목표 (있는 경우)
    """
    mode_styles = {
        MinmoMode.FREE: ("FREE", "cyan", "지휘관이 요청을 분석하여 자동으로 적절한 처리 방식을 선택합니다."),
        MinmoMode.PLAN: ("PLAN", "yellow", "Speckit 인터뷰를 통해 상세 기획서를 작성하고 태스크를 분해합니다."),
        MinmoMode.DIRECT: ("DIRECT", "green", "지휘관을 건너뛰고 작업자(Claude)에게 바로 명령을 전달합니다."),
        MinmoMode.ANALYZE: ("ANALYZE", "magenta", "프로젝트를 분석하고 종합 리포트를 출력합니다. (수정 없음)"),
        MinmoMode.HELP: ("HELP", "blue", "도움말을 표시합니다."),
    }

    mode_name, color, description = mode_styles.get(mode, ("UNKNOWN", "white", ""))

    content = f"[bold {color}][MODE: {mode_name}][/bold {color}]\n"
    content += f"[dim]{description}[/dim]"

    if goal:
        # 긴 목표는 줄임
        display_goal = goal[:80] + "..." if len(goal) > 80 else goal
        content += f"\n\n[bold]목표:[/bold] {display_goal}"

    console.print(Panel(
        content,
        box=box.DOUBLE,
        border_style=color,
        padding=(0, 2)
    ))
    console.print()


def show_help_table():
    """
    /help 명령어 실행 - 각 모드의 차이점과 사용법을 테이블로 표시합니다.
    """
    console.print(Panel(
        "[bold cyan]Minmo 멀티 모드 시스템[/bold cyan]\n"
        "[dim]커맨드 접두사로 동작 모드를 선택할 수 있습니다.[/dim]",
        box=box.DOUBLE,
        border_style="cyan"
    ))
    console.print()

    # 모드 설명 테이블
    table = Table(
        title="사용 가능한 모드",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        title_style="bold"
    )

    table.add_column("명령어", style="bold yellow", width=20)
    table.add_column("모드", style="cyan", width=10)
    table.add_column("설명", style="white", no_wrap=False)
    table.add_column("사용 예시", style="dim", no_wrap=False)

    table.add_row(
        "/plan [요구사항]",
        "PLAN",
        "지휘관(Gemini)의 심층 인터뷰를 강제 활성화합니다.\n"
        "Speckit 프로세스를 거쳐 상세 설계서를 출력하고 사용자 승인을 받습니다.",
        "/plan 사용자 인증 기능 구현"
    )

    table.add_row(
        "/direct [명령]",
        "DIRECT",
        "지휘관을 건너뛰고 작업자(Claude Code)에게 바로 명령을 전달합니다.\n"
        "Scribe는 기록만 담당합니다.",
        "/direct README.md에 설치 방법 추가"
    )

    table.add_row(
        "/analyze [대상]",
        "ANALYZE",
        "지휘관이 프로젝트 전체 또는 특정 파일을 분석합니다.\n"
        "종합 리포트 형식으로 분석 결과만 보여주고 종료합니다. (수정 X)",
        "/analyze src/auth 모듈"
    )

    table.add_row(
        "/free [요청]",
        "FREE",
        "[bold]기본 모드[/bold] - 지휘관이 입력을 보고 적절한 처리 방식을 판단합니다.\n"
        "기획이 필요하면 PLAN 모드로, 간단하면 바로 실행합니다.",
        "/free 버그 수정해줘"
    )

    table.add_row(
        "[입력]",
        "FREE",
        "접두사 없이 입력하면 자동으로 FREE 모드로 동작합니다.",
        "로그인 기능 만들어줘"
    )

    console.print(table)
    console.print()

    # 추가 명령어 테이블
    extra_table = Table(
        title="기타 명령어",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )

    extra_table.add_column("명령어", style="bold yellow", width=15)
    extra_table.add_column("설명", style="white")

    extra_table.add_row("/help", "이 도움말을 표시합니다.")
    extra_table.add_row("/stats", "토큰 사용량 통계를 표시합니다.")
    extra_table.add_row("/clean", "화면을 지웁니다.")
    extra_table.add_row("/exit", "Minmo를 종료합니다.")
    extra_table.add_row("Tab", "명령어 자동완성")
    extra_table.add_row("↑↓ 화살표", "명령어 히스토리 탐색")
    extra_table.add_row("ESC", "현재 실행 중인 작업 중단")
    extra_table.add_row("Ctrl+C", "프로그램 종료")

    console.print(extra_table)
    console.print()

    # 팁
    console.print(Panel(
        "[bold]팁:[/bold]\n"
        "• 복잡한 기능 개발은 [yellow]/plan[/yellow]으로 시작하세요.\n"
        "• 단순 수정이나 파일 작업은 [green]/direct[/green]가 빠릅니다.\n"
        "• 코드베이스 이해가 필요하면 [magenta]/analyze[/magenta]를 사용하세요.\n"
        "• 모든 작업 로그는 [dim].minmo/[/dim] 폴더에 저장됩니다.",
        box=box.ROUNDED,
        border_style="dim"
    ))


# ============================================================
# prompt_toolkit 기반 고급 입력 시스템
# ============================================================

# 명령어 정의 (자동완성용)
MINMO_COMMANDS = {
    "/plan": "기획 및 설계 모드 - Speckit 인터뷰를 통해 기획서 작성",
    "/direct": "직접 실행 모드 - 지휘관 건너뛰고 Claude에게 바로 전달",
    "/analyze": "분석 모드 - 프로젝트 분석 후 리포트 출력 (수정 없음)",
    "/free": "자동 판단 모드 - 지휘관이 적절한 처리 방식 선택",
    "/stats": "토큰 사용량 통계 표시",
    "/help": "도움말 표시",
    "/clean": "화면 지우기",
    "/exit": "Minmo 종료",
}


class MinmoCompleter(Completer):
    """
    Minmo 명령어 자동완성 Completer.

    `/`를 입력하면 사용 가능한 명령어 목록을 팝업으로 표시합니다.
    """

    def get_completions(self, document: Document, complete_event):
        text = document.text_before_cursor
        word = document.get_word_before_cursor()

        # `/`로 시작하는 경우 명령어 자동완성
        if text.startswith('/'):
            # 현재 입력된 명령어 부분
            cmd_text = text.split()[0] if text.split() else text

            for cmd, description in MINMO_COMMANDS.items():
                if cmd.startswith(cmd_text):
                    # 이미 입력된 부분을 제외한 나머지를 완성
                    yield Completion(
                        cmd,
                        start_position=-len(cmd_text),
                        display=cmd,
                        display_meta=description,
                    )


class MinmoLexer(Lexer):
    """
    Minmo 입력창 문법 하이라이팅 Lexer.

    - `/`로 시작하는 명령어는 노란색으로 표시
    - 일반 텍스트는 기본 색상
    """

    def lex_document(self, document: Document):
        def get_line(lineno: int):
            line = document.lines[lineno]

            # 빈 줄
            if not line:
                return []

            # 명령어로 시작하는 경우
            if line.startswith('/'):
                parts = line.split(' ', 1)
                cmd = parts[0]

                result = []

                # 명령어 부분 (노란색)
                if cmd in MINMO_COMMANDS:
                    result.append(('class:command', cmd))
                else:
                    result.append(('class:command-unknown', cmd))

                # 나머지 부분 (기본색)
                if len(parts) > 1:
                    result.append(('', ' ' + parts[1]))

                return result

            # 일반 텍스트
            return [('', line)]

        return get_line


# prompt_toolkit 스타일 정의
MINMO_PT_STYLE = PTStyle.from_dict({
    'command': '#ffff00 bold',           # 노란색, 굵게 - 유효 명령어
    'command-unknown': '#ff8800',         # 주황색 - 알 수 없는 명령어
    'prompt': '#00ffff bold',             # 시안, 굵게 - 프롬프트
    'bottom-toolbar': 'bg:#333333 #ffffff',
})


# 전역 중단 이벤트 (ESC 키로 작업 중단용)
_abort_event = threading.Event()


def is_aborted() -> bool:
    """현재 작업이 중단되었는지 확인합니다."""
    return _abort_event.is_set()


def reset_abort():
    """중단 이벤트를 초기화합니다."""
    _abort_event.clear()


def trigger_abort():
    """작업 중단을 트리거합니다."""
    _abort_event.set()


def create_key_bindings() -> KeyBindings:
    """
    커스텀 키 바인딩을 생성합니다.

    - ESC: 현재 실행 중인 작업 중단
    """
    bindings = KeyBindings()

    @bindings.add('escape')
    def _(event):
        """ESC 키: 작업 중단 트리거"""
        trigger_abort()
        # 버퍼에 특수 마커 삽입하여 루프에서 감지
        event.app.exit(result='__ABORT__')

    @bindings.add('c-c')
    def _(event):
        """Ctrl+C: 종료"""
        event.app.exit(exception=KeyboardInterrupt())

    @bindings.add('c-d')
    def _(event):
        """Ctrl+D: 종료"""
        event.app.exit(exception=EOFError())

    return bindings


def get_bottom_toolbar():
    """하단 툴바 텍스트를 반환합니다."""
    return FormattedText([
        ('class:bottom-toolbar', ' ESC: 작업 중단 | Tab: 자동완성 | ↑↓: 히스토리 | Ctrl+C: 종료 '),
    ])


def create_prompt_session() -> PromptSession:
    """
    prompt_toolkit PromptSession을 생성합니다.

    Features:
    - 명령어 자동완성
    - 문법 하이라이팅
    - 히스토리 (Up/Down 화살표)
    - ESC 키 바인딩
    """
    # .minmo 디렉토리에 히스토리 파일 저장
    minmo_dir = ensure_minmo_data_dir()
    history_file = minmo_dir / "command_history"

    session = PromptSession(
        completer=MinmoCompleter(),
        lexer=MinmoLexer(),
        style=MINMO_PT_STYLE,
        history=FileHistory(str(history_file)),
        key_bindings=create_key_bindings(),
        bottom_toolbar=get_bottom_toolbar,
        complete_while_typing=True,
        enable_history_search=True,
    )

    return session


class AbortableTask:
    """
    중단 가능한 태스크 래퍼.

    ESC 키가 눌리면 실행 중인 작업을 중단할 수 있습니다.
    """

    def __init__(self, console_instance: Console = None):
        self.console = console_instance or console
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._result = None
        self._exception = None

    def run(self, func: Callable, *args, **kwargs) -> Any:
        """
        함수를 중단 가능한 방식으로 실행합니다.

        Args:
            func: 실행할 함수
            *args: 함수 인자
            **kwargs: 함수 키워드 인자

        Returns:
            함수 실행 결과 또는 None (중단된 경우)
        """
        reset_abort()
        self._is_running = True
        self._result = None
        self._exception = None

        def target():
            try:
                self._result = func(*args, **kwargs)
            except Exception as e:
                self._exception = e
            finally:
                self._is_running = False

        self._thread = threading.Thread(target=target, daemon=True)
        self._thread.start()

        # 중단 이벤트를 주기적으로 확인하면서 대기
        while self._thread.is_alive():
            if is_aborted():
                self.console.print("\n[yellow]작업이 사용자에 의해 중단되었습니다.[/yellow]")
                self._is_running = False
                return None
            self._thread.join(timeout=0.1)

        if self._exception:
            raise self._exception

        return self._result

    @property
    def is_running(self) -> bool:
        return self._is_running


# ASCII 아트 로고
LOGO = """
 ███╗   ███╗██╗███╗   ██╗███╗   ███╗ ██████╗
 ████╗ ████║██║████╗  ██║████╗ ████║██╔═══██╗
 ██╔████╔██║██║██╔██╗ ██║██╔████╔██║██║   ██║
 ██║╚██╔╝██║██║██║╚██╗██║██║╚██╔╝██║██║   ██║
 ██║ ╚═╝ ██║██║██║ ╚████║██║ ╚═╝ ██║╚██████╔╝
 ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝
"""


class ScribeMCPServer:
    """Scribe MCP 서버 프로세스 관리"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.script_path = Path(__file__).parent / "scribe_mcp.py"

    def start(self) -> bool:
        """MCP 서버를 백그라운드에서 시작합니다."""
        if self.process is not None:
            return True

        try:
            self.process = subprocess.Popen(
                [sys.executable, str(self.script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            # 서버 시작 대기
            time.sleep(0.5)

            if self.process.poll() is None:
                return True
            else:
                return False
        except Exception as e:
            console.print(f"[red]MCP 서버 시작 실패: {e}[/red]")
            return False

    def stop(self):
        """MCP 서버를 종료합니다."""
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None


def print_header():
    """헤더를 출력합니다."""
    try:
        logo_text = Text(LOGO, style="bold cyan")
        console.print(logo_text)
    except UnicodeEncodeError:
        # Windows cp949 등 유니코드 미지원 콘솔에서는 간단한 텍스트로 대체
        console.print("[bold cyan]MINMO[/bold cyan]")

    console.print(
        Panel(
            f"[bold white]MCP 통합 자동화 프레임워크[/bold white]\n"
            f"[dim]Version {__version__}[/dim]",
            box=box.ROUNDED,
            border_style="cyan",
            padding=(0, 2)
        )
    )
    console.print()


# ============================================================
# DisplayAI - 최종 결과 종합 표시
# ============================================================
class DisplayAI:
    """
    오케스트레이션 결과를 종합적으로 표시하는 AI 디스플레이.

    다음 정보를 수집하고 보기 좋게 출력합니다:
    - 목표 및 요구사항 요약
    - 생성된 계획 및 태스크
    - 각 태스크 실행 결과
    - 토큰 사용량 통계
    - 전체 요약
    """

    def __init__(self):
        self.console = console

    def _format_tokens(self, n: int) -> str:
        """토큰 수를 읽기 쉬운 형식으로 변환"""
        if n >= 1_000_000:
            return f"{n / 1_000_000:.1f}M"
        elif n >= 1_000:
            return f"{n / 1_000:.1f}K"
        return str(n)

    def _get_status_icon(self, status: str) -> str:
        """상태에 따른 아이콘 반환"""
        icons = {
            "completed": "[green]✓[/green]",
            "failed": "[red]✗[/red]",
            "partial": "[yellow]⚠[/yellow]",
            "pending": "[dim]○[/dim]",
            "in_progress": "[cyan]◐[/cyan]",
            "skipped": "[dim]⊘[/dim]",
        }
        return icons.get(status, "[dim]?[/dim]")

    def display(self, result: dict, show_usage: bool = True):
        """
        전체 결과를 종합적으로 표시합니다.

        Args:
            result: orchestrator.start_loop()의 반환값
            show_usage: 토큰 사용량 표시 여부
        """
        self.console.print()
        self.console.print(Panel(
            "[bold white]MINMO Display AI[/bold white]\n"
            "[dim]최종 결과 종합 리포트[/dim]",
            box=box.DOUBLE,
            border_style="bright_magenta",
            padding=(0, 2)
        ))
        self.console.print()

        # 1. 목표 요약
        self._display_goal_summary(result)

        # 2. 상세 분석 결과 (지휘관 보고서)
        self._display_detailed_analysis(result)

        # 3. 계획 표시
        self._display_plan(result)

        # 4. 태스크 실행 결과
        self._display_task_results(result)

        # 5. 토큰 사용량
        if show_usage:
            self._display_usage()

        # 6. 최종 요약
        self._display_final_summary(result)

    def _display_goal_summary(self, result: dict):
        """목표 요약 표시"""
        goal = result.get("goal", "")
        clarification = result.get("clarification", {})

        # 목표를 마크다운으로 구성
        goal_md = f"## 사용자 요청\n\n{goal}"

        if clarification:
            final_req = clarification.get("final_requirements", {})
            if final_req:
                summary = final_req.get("summary", "")
                if summary and summary != goal:
                    goal_md += f"\n\n---\n\n### 명확화된 요구사항\n\n{summary}"

        self.console.print(Panel(
            render_markdown(goal_md),
            title="[cyan]1. 목표[/cyan]",
            box=box.ROUNDED,
            border_style="cyan"
        ))
        self.console.print()

    def _display_detailed_analysis(self, result: dict):
        """상세 분석 결과 표시 (지휘관 보고서)"""
        detailed_analysis = result.get("detailed_analysis", "")

        # plan 내부에서도 찾기 (하위 호환성)
        if not detailed_analysis:
            plan = result.get("plan", {})
            if isinstance(plan, dict):
                detailed_analysis = plan.get("detailed_analysis", "")

        if not detailed_analysis:
            # 분석 보고서가 없으면 섹션 표시 안 함
            return

        self.console.print(Panel(
            render_markdown(detailed_analysis),
            title="[bright_magenta]2. 지휘관 상세 분석[/bright_magenta]",
            box=box.ROUNDED,
            border_style="bright_magenta"
        ))
        self.console.print()

    def _display_plan(self, result: dict):
        """계획 표시"""
        plan = result.get("plan", {})

        if not plan:
            self.console.print(Panel(
                "[dim]계획이 생성되지 않았습니다.[/dim]",
                title="[cyan]3. 계획[/cyan]",
                box=box.ROUNDED,
                border_style="dim"
            ))
            self.console.print()
            return

        summary = plan.get("summary", "계획 수립 완료")
        tasks = plan.get("tasks", [])

        # 계획 요약을 마크다운으로 렌더링
        # summary가 마크다운 형식이 아니면 제목으로 래핑
        if not summary.startswith("#"):
            plan_md = f"## 계획 요약\n\n{summary}"
        else:
            plan_md = summary

        self.console.print(Panel(
            render_markdown(plan_md),
            title="[cyan]3. 계획[/cyan]",
            box=box.ROUNDED,
            border_style="cyan"
        ))

        # 태스크 테이블
        if tasks:
            task_table = Table(
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan",
                title=f"태스크 목록 ({len(tasks)}개)"
            )
            task_table.add_column("#", style="dim", width=3)
            task_table.add_column("제목", style="white", no_wrap=False)
            task_table.add_column("설명", style="dim", no_wrap=False, max_width=50)

            for i, task in enumerate(tasks, 1):
                title = task.get("title", task.get("id", f"Task {i}"))
                desc = task.get("description", task.get("goal", ""))
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                task_table.add_row(str(i), title, desc)

            self.console.print(task_table)

        self.console.print()

    def _display_task_results(self, result: dict):
        """태스크 실행 결과 표시"""
        results = result.get("results", [])

        if not results:
            self.console.print(Panel(
                "[dim]실행된 태스크가 없습니다.[/dim]",
                title="[cyan]4. 실행 결과[/cyan]",
                box=box.ROUNDED,
                border_style="dim"
            ))
            self.console.print()
            return

        result_table = Table(
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
            title="태스크 실행 결과"
        )
        result_table.add_column("상태", justify="center", width=4)
        result_table.add_column("태스크 ID", style="white")
        result_table.add_column("소요 시간", justify="right", style="dim")
        result_table.add_column("수정된 파일", justify="right")
        result_table.add_column("오류", style="red", max_width=30)

        for r in results:
            status = r.get("status", "unknown")
            icon = self._get_status_icon(status)
            task_id = r.get("task_id", "unknown")
            duration = r.get("duration_seconds", 0)
            duration_str = f"{duration:.1f}s" if duration else "-"
            files_modified = r.get("files_modified", [])
            files_str = str(len(files_modified)) if files_modified else "-"
            error = r.get("error", "")
            if error and len(error) > 30:
                error = error[:27] + "..."

            result_table.add_row(icon, task_id, duration_str, files_str, error or "-")

        self.console.print(Panel(
            result_table,
            title="[cyan]4. 실행 결과[/cyan]",
            box=box.ROUNDED,
            border_style="cyan"
        ))
        self.console.print()

    def _display_usage(self):
        """토큰 사용량 표시"""
        try:
            usage_result = call_get_usage_stats(session_only=True)

            if not usage_result.get("success") or not usage_result.get("models"):
                self.console.print(Panel(
                    "[dim]세션 토큰 사용량 데이터가 없습니다.[/dim]",
                    title="[cyan]5. 토큰 사용량[/cyan]",
                    box=box.ROUNDED,
                    border_style="dim"
                ))
                self.console.print()
                return

            models = usage_result.get("models", [])
            totals = usage_result.get("totals", {})

            usage_table = Table(
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan"
            )
            usage_table.add_column("모델", style="cyan")
            usage_table.add_column("입력", justify="right", style="green")
            usage_table.add_column("출력", justify="right", style="yellow")
            usage_table.add_column("총합", justify="right", style="bold white")
            usage_table.add_column("사용률", justify="right")

            for m in models:
                usage_ratio = m.get("usage_ratio", 0)
                if usage_ratio < 25:
                    ratio_style = "green"
                elif usage_ratio < 50:
                    ratio_style = "yellow"
                else:
                    ratio_style = "red"

                usage_table.add_row(
                    m["model"],
                    self._format_tokens(m["input_tokens"]),
                    self._format_tokens(m["output_tokens"]),
                    self._format_tokens(m["total_tokens"]),
                    f"[{ratio_style}]{usage_ratio:.1f}%[/{ratio_style}]"
                )

            # 총계 행
            usage_table.add_row(
                "[bold]총계[/bold]",
                f"[bold]{self._format_tokens(totals.get('input_tokens', 0))}[/bold]",
                f"[bold]{self._format_tokens(totals.get('output_tokens', 0))}[/bold]",
                f"[bold]{self._format_tokens(totals.get('total_tokens', 0))}[/bold]",
                f"[dim]{totals.get('call_count', 0)} calls[/dim]"
            )

            self.console.print(Panel(
                usage_table,
                title="[cyan]5. 토큰 사용량 (현재 세션)[/cyan]",
                box=box.ROUNDED,
                border_style="cyan"
            ))
            self.console.print()

        except Exception:
            pass  # 사용량 표시 실패해도 계속

    def _display_final_summary(self, result: dict):
        """최종 요약 표시"""
        status = result.get("status", "unknown")
        summary = result.get("summary", {})
        detailed_analysis = result.get("detailed_analysis", "")

        total = summary.get("total", 0)
        completed = summary.get("completed", 0)
        failed = summary.get("failed", 0)

        # 태스크가 0개이지만 분석 보고서가 있는 경우
        has_analysis = bool(detailed_analysis)

        if total == 0 and has_analysis:
            status_text = "[bright_magenta bold]✓ 분석 보고서 생성 완료[/bright_magenta bold]"
            border_style = "bright_magenta"
            summary_content = f"{status_text}\n\n"
            summary_content += "[dim]지휘관이 프로젝트를 분석하고 상세 보고서를 생성했습니다.[/dim]\n"
            summary_content += "[dim]실행할 태스크가 없거나, 분석만 요청되었습니다.[/dim]"
        elif status == "completed":
            status_text = "[green bold]✓ 모든 작업 완료[/green bold]"
            border_style = "green"
            summary_content = f"{status_text}\n\n"
            if total > 0:
                success_rate = (completed / total * 100) if total > 0 else 0
                summary_content += f"[dim]총 태스크:[/dim] {total}개\n"
                summary_content += f"[green]성공:[/green] {completed}개\n"
                if failed > 0:
                    summary_content += f"[red]실패:[/red] {failed}개\n"
                summary_content += f"[dim]성공률:[/dim] {success_rate:.0f}%"
        elif status == "partial":
            status_text = "[yellow bold]⚠ 일부 작업 완료[/yellow bold]"
            border_style = "yellow"
            summary_content = f"{status_text}\n\n"
            if total > 0:
                success_rate = (completed / total * 100) if total > 0 else 0
                summary_content += f"[dim]총 태스크:[/dim] {total}개\n"
                summary_content += f"[green]성공:[/green] {completed}개\n"
                if failed > 0:
                    summary_content += f"[red]실패:[/red] {failed}개\n"
                summary_content += f"[dim]성공률:[/dim] {success_rate:.0f}%"
        else:
            status_text = "[red bold]✗ 작업 실패[/red bold]"
            border_style = "red"
            summary_content = f"{status_text}\n\n"
            if total > 0:
                summary_content += f"[dim]총 태스크:[/dim] {total}개\n"
                summary_content += f"[green]성공:[/green] {completed}개\n"
                if failed > 0:
                    summary_content += f"[red]실패:[/red] {failed}개\n"

        self.console.print(Panel(
            summary_content,
            title="[bold]6. 최종 요약[/bold]",
            box=box.DOUBLE,
            border_style=border_style
        ))
        self.console.print()


# DisplayAI 인스턴스
display_ai = DisplayAI()


def print_status_table(goal: str, status: str = "대기 중"):
    """상태 테이블을 출력합니다."""
    table = Table(box=box.ROUNDED, border_style="dim")
    table.add_column("항목", style="cyan", width=12)
    table.add_column("내용", style="white")

    table.add_row("목표", goal)
    table.add_row("상태", f"[yellow]{status}[/yellow]")

    console.print(table)
    console.print()


def run_orchestrator(goal: str, verbose: bool = True):
    """오케스트레이터를 실행합니다."""
    mcp_server = ScribeMCPServer()
    status_manager = StatusManager(console, spinner="dots")

    def on_error(error_type: str, details: dict):
        """에러 출력 콜백"""
        status_manager.stop(success=False)
        console.print(f"[red]✗ {error_type}: {details.get('error', 'Unknown')}[/red]")

    try:
        # MCP 서버 시작
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Scribe MCP 서버 시작 중...", total=None)

            if mcp_server.start():
                progress.update(task, description="[green]Scribe MCP 서버 준비 완료[/green]")
                time.sleep(0.3)
            else:
                console.print("[yellow]경고: MCP 서버를 시작할 수 없습니다. 일부 기능이 제한됩니다.[/yellow]")

        print_status_table(goal, "실행 중")
        console.print("[dim](Ctrl+C로 중단 가능)[/dim]\n")

        # StatusManager로 인플레이스 상태 표시 시작
        status_manager.start("Gemini CLI 초기화")

        # 오케스트레이터 실행 (on_status 콜백으로 인플레이스 업데이트)
        orchestrator = MinmoOrchestrator(
            on_error=on_error if verbose else None,
            on_status=create_status_callback(status_manager),
            verbose=verbose
        )

        result = orchestrator.start_loop(goal)

        # 상태 표시 완료
        status_manager.stop(success=True, message="작업 완료")

        # DisplayAI로 최종 결과 종합 표시
        display_ai.display(result, show_usage=True)

    except KeyboardInterrupt:
        status_manager.stop(success=False)
        console.print("\n[yellow]사용자에 의해 중단되었습니다.[/yellow]")
    except Exception as e:
        status_manager.stop(success=False)
        console.print(f"\n[red]오류 발생: {e}[/red]")
        import traceback
        if verbose:
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
    finally:
        mcp_server.stop()


def interactive_mode():
    """
    대화형 모드를 시작합니다.

    prompt_toolkit 기반 고급 입력 시스템:
    - 명령어 자동완성 (Tab)
    - 문법 하이라이팅
    - 히스토리 (Up/Down 화살표)
    - ESC 키로 작업 중단

    멀티 모드 시스템 지원:
    - /plan [명령]: 기획 모드
    - /direct [명령]: 직접 실행 모드
    - /analyze [대상]: 분석 모드
    - /free [요청]: 자동 판단 모드 (기본)
    - /stats: 토큰 사용량 통계
    - /help: 도움말
    - /clean: 화면 지우기
    - /exit: 종료
    """
    print_header()

    # 시작 시 간단한 도움말 표시
    console.print(
        "[cyan]대화형 모드[/cyan] - 요청을 입력하세요\n"
        "[dim]/로 시작하면 명령어 자동완성 | Tab: 완성 | ↑↓: 히스토리 | ESC: 작업 중단[/dim]\n"
    )

    # prompt_toolkit 세션 생성
    session = create_prompt_session()

    while True:
        try:
            # 중단 상태 초기화
            reset_abort()

            # prompt_toolkit으로 입력 받기
            user_input = session.prompt(
                [('class:prompt', 'minmo> ')],
            )

            # ESC로 중단된 경우
            if user_input == '__ABORT__':
                console.print("[dim]입력이 취소되었습니다.[/dim]")
                continue

            user_input = user_input.strip()

            if not user_input:
                continue

            # 종료 명령어
            if user_input.lower() in ('exit', 'quit', 'q', '/exit'):
                console.print("[dim]종료합니다.[/dim]")
                break

            # 화면 지우기
            if user_input.lower() in ('/clean', '/clear'):
                os.system('cls' if os.name == 'nt' else 'clear')
                print_header()
                continue

            # 통계 명령어 (/stats)
            if user_input.lower() == '/stats':
                console.print()
                # 간단히 stats 표시
                from minmo.scribe_mcp import call_get_usage_stats
                result = call_get_usage_stats(session_only=False)
                if result.get("success"):
                    models = result.get("models", [])
                    if models:
                        table = Table(title="토큰 사용량", box=box.ROUNDED)
                        table.add_column("모델", style="cyan")
                        table.add_column("입력", justify="right", style="green")
                        table.add_column("출력", justify="right", style="yellow")
                        table.add_column("총합", justify="right", style="bold")
                        for m in models:
                            table.add_row(
                                m["model"],
                                f"{m['input_tokens']:,}",
                                f"{m['output_tokens']:,}",
                                f"{m['total_tokens']:,}"
                            )
                        console.print(table)
                    else:
                        console.print("[dim]아직 기록된 사용량이 없습니다.[/dim]")
                else:
                    console.print(f"[red]통계 조회 실패: {result.get('error')}[/red]")
                console.print()
                continue

            console.print()

            # 커맨드 파싱
            parsed = parse_command(user_input)

            # 모드 실행 (중단 가능한 방식으로)
            execute_mode(parsed, verbose=False)

            console.print()

        except KeyboardInterrupt:
            console.print("\n[dim]종료합니다.[/dim]")
            break
        except EOFError:
            console.print("\n[dim]종료합니다.[/dim]")
            break
        except Exception as e:
            console.print(f"\n[red]오류 발생: {e}[/red]")
            continue


# ============================================================
# init 명령어 - 프로젝트 초기화
# ============================================================
def cmd_init(args):
    """프로젝트를 Minmo용으로 초기화합니다."""
    project_path = Path(args.path).resolve()

    console.print(Panel(
        f"[cyan]Minmo 프로젝트 초기화[/cyan]\n경로: {project_path}",
        box=box.ROUNDED
    ))

    try:
        # 1. .minmo 디렉토리 생성
        minmo_dir = ensure_minmo_data_dir(project_path)
        console.print(f"[green]✓[/green] .minmo 디렉토리 생성: {minmo_dir}")

        # 2. .gitignore에 .minmo/ 추가
        gitignore_path = project_path / ".gitignore"
        gitignore_entry = ".minmo/"

        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding="utf-8")

            if gitignore_entry not in content and ".minmo" not in content:
                # .gitignore에 추가
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    if not content.endswith("\n"):
                        f.write("\n")
                    f.write(f"\n# Minmo 데이터 디렉토리\n{gitignore_entry}\n")
                console.print(f"[green]✓[/green] .gitignore에 '{gitignore_entry}' 추가됨")
            else:
                console.print(f"[dim]- .gitignore에 이미 '{gitignore_entry}' 존재[/dim]")
        else:
            # .gitignore 생성
            gitignore_path.write_text(
                f"# Minmo 데이터 디렉토리\n{gitignore_entry}\n",
                encoding="utf-8"
            )
            console.print(f"[green]✓[/green] .gitignore 생성 및 '{gitignore_entry}' 추가됨")

        # 3. 완료 메시지
        console.print(Panel(
            "[green]Minmo 프로젝트 초기화 완료![/green]\n\n"
            "[dim]사용 가능한 명령어:[/dim]\n"
            "  minmo index   - 프로젝트 인덱싱\n"
            "  minmo search  - 코드 검색\n"
            "  minmo plan    - 기획/설계 모드\n"
            "  minmo run     - 작업 실행",
            box=box.ROUNDED,
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]초기화 오류: {e}[/red]")


# ============================================================
# 인덱싱 명령어
# ============================================================
def cmd_index(args):
    """프로젝트를 인덱싱합니다."""
    project_path = args.path or "."

    console.print(Panel(
        f"[cyan]프로젝트 인덱싱[/cyan]\n경로: {Path(project_path).resolve()}",
        box=box.ROUNDED
    ))

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("인덱싱 중...", total=None)

            indexer = CodeIndexer(project_path)
            stats = indexer.index_all(force=args.force)

            progress.update(task, description="[green]인덱싱 완료[/green]")

        # 결과 테이블
        table = Table(box=box.ROUNDED, border_style="green")
        table.add_column("항목", style="cyan")
        table.add_column("수량", style="white", justify="right")

        table.add_row("인덱싱됨", str(stats["indexed"]))
        table.add_row("스킵됨", str(stats["skipped"]))
        table.add_row("실패", str(stats["failed"]))
        table.add_row("총계", str(stats["indexed"] + stats["skipped"] + stats["failed"]))

        console.print(table)

        if args.watch:
            console.print("\n[yellow]파일 변경 감시 중... (Ctrl+C로 종료)[/yellow]")
            indexer.start_watching()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                indexer.stop_watching()
                console.print("\n[dim]감시 종료[/dim]")

    except Exception as e:
        console.print(f"[red]인덱싱 오류: {e}[/red]")


def cmd_search(args):
    """코드베이스에서 심볼을 검색합니다."""
    query = args.query
    project_path = args.path or "."

    try:
        indexer = CodeIndexer(project_path)
        results = indexer.search(query, limit=args.limit)

        if not results:
            console.print(f"[yellow]'{query}'에 대한 검색 결과가 없습니다.[/yellow]")
            console.print("[dim]먼저 'minmo index'를 실행해주세요.[/dim]")
            return

        console.print(Panel(
            f"[cyan]검색 결과[/cyan]: '{query}' ({len(results)}개)",
            box=box.ROUNDED
        ))

        for i, result in enumerate(results, 1):
            symbol = result.symbol

            # 심볼 타입에 따른 색상
            type_color = {
                "class": "magenta",
                "function": "green",
                "method": "blue"
            }.get(symbol.symbol_type, "white")

            # 트리 형태로 표시
            tree = Tree(f"[{type_color}]{symbol.symbol_type}[/{type_color}] [bold]{symbol.name}[/bold]")
            tree.add(f"[dim]파일:[/dim] {symbol.file_path}:{symbol.line_start}")

            if symbol.signature:
                tree.add(f"[dim]시그니처:[/dim] {symbol.signature}")

            if symbol.parent:
                tree.add(f"[dim]부모:[/dim] {symbol.parent}")

            if symbol.docstring:
                doc_preview = symbol.docstring[:100].replace("\n", " ")
                if len(symbol.docstring) > 100:
                    doc_preview += "..."
                tree.add(f"[dim]문서:[/dim] {doc_preview}")

            console.print(tree)
            if i < len(results):
                console.print()

    except Exception as e:
        console.print(f"[red]검색 오류: {e}[/red]")


def cmd_overview(args):
    """프로젝트 개요를 출력합니다."""
    project_path = args.path or "."

    try:
        indexer = CodeIndexer(project_path)
        overview = indexer.get_project_overview()

        console.print(Panel(
            f"[cyan]프로젝트 개요[/cyan]\n{overview['project_path']}",
            box=box.ROUNDED
        ))

        # 통계 테이블
        stats = overview.get("stats", {})
        if stats:
            table = Table(title="통계", box=box.ROUNDED)
            table.add_column("항목", style="cyan")
            table.add_column("수량", justify="right")

            table.add_row("파일", str(stats.get("files", 0)))
            table.add_row("클래스", str(stats.get("classes", 0)))
            table.add_row("함수", str(stats.get("functions", 0)))
            table.add_row("메서드", str(stats.get("methods", 0)))

            console.print(table)
            console.print()

        # 주요 클래스
        if overview.get("main_classes"):
            console.print("[bold]주요 클래스:[/bold]")
            for cls in overview["main_classes"][:10]:
                console.print(f"  [magenta]class[/magenta] {cls['name']} - [dim]{cls['file']}[/dim]")
            console.print()

        # 주요 함수
        if overview.get("main_functions"):
            console.print("[bold]주요 함수:[/bold]")
            for func in overview["main_functions"][:10]:
                console.print(f"  [green]def[/green] {func['name']} - [dim]{func['file']}[/dim]")

    except Exception as e:
        console.print(f"[red]개요 조회 오류: {e}[/red]")


# ============================================================
# Plan Mode 명령어
# ============================================================

def _ask_interview_question(question: InterviewQuestion) -> str:
    """인터뷰 질문을 사용자에게 마크다운으로 보여주고 답변을 받습니다."""
    # 질문 패널 표시
    focus_labels = {
        "architecture": "아키텍처",
        "data_model": "데이터 모델",
        "exception_handling": "예외 처리",
        "convention": "컨벤션",
        "integration": "통합",
        "testing": "테스트"
    }

    focus_label = focus_labels.get(question.focus.value, question.focus.value)

    # 질문을 마크다운으로 구성
    question_md = f"## {question.question}\n\n"
    if question.context:
        question_md += f"> {question.context}"

    console.print(Panel(
        render_markdown(question_md),
        title=f"[cyan]질문[/cyan] [{focus_label}]",
        box=box.ROUNDED,
        border_style="cyan"
    ))

    # 옵션 표시 (마크다운 리스트)
    if question.options:
        options_md = "### 선택 가능한 옵션\n\n"
        for i, opt in enumerate(question.options, 1):
            options_md += f"{i}. {opt}\n"
        options_md += "0. *직접 입력*"
        console.print(render_markdown(options_md))
        console.print()

        # 선택 받기
        while True:
            try:
                choice = console.input("[bold cyan]선택 (번호 또는 텍스트)>[/bold cyan] ").strip()

                if choice.isdigit():
                    idx = int(choice)
                    if idx == 0:
                        answer = console.input("[bold cyan]답변>[/bold cyan] ").strip()
                        break
                    elif 1 <= idx <= len(question.options):
                        answer = question.options[idx - 1]
                        break
                    else:
                        console.print("[red]유효하지 않은 번호입니다.[/red]")
                else:
                    # 텍스트로 직접 입력
                    answer = choice
                    break
            except KeyboardInterrupt:
                raise
    else:
        answer = console.input("[bold cyan]답변>[/bold cyan] ").strip()

    console.print()
    return answer


def _review_spec(spec: FeatureSpec) -> bool:
    """기획서를 사용자에게 마크다운으로 보여주고 승인을 받습니다."""
    # 기획서를 마크다운 문서로 구성
    md_parts = [
        f"# {spec.feature_name}",
        "",
        spec.summary,
        "",
    ]

    # 요구사항
    if spec.requirements:
        md_parts.append("## 요구사항")
        for req in spec.requirements:
            md_parts.append(f"- {req}")
        md_parts.append("")

    # 아키텍처 결정사항
    if spec.architecture_decisions:
        md_parts.append("## 아키텍처 결정")
        for dec in spec.architecture_decisions:
            md_parts.append(f"- {dec}")
        md_parts.append("")

    # 에러 핸들링
    if spec.error_handling:
        md_parts.append("## 에러 처리")
        for err in spec.error_handling:
            md_parts.append(f"- {err}")
        md_parts.append("")

    # 컨벤션
    if spec.conventions:
        md_parts.append("## 준수할 컨벤션")
        for conv in spec.conventions:
            md_parts.append(f"- {conv}")
        md_parts.append("")

    # 제외 범위
    if spec.out_of_scope:
        md_parts.append("## 범위 외 (미구현)")
        for oos in spec.out_of_scope:
            md_parts.append(f"- *{oos}*")
        md_parts.append("")

    console.print(Panel(
        render_markdown("\n".join(md_parts)),
        title="[green]기획서 생성 완료[/green]",
        box=box.ROUNDED,
        border_style="green"
    ))
    console.print()

    # 승인 여부 확인
    while True:
        choice = console.input("[bold]기획서를 승인하시겠습니까? [/bold][cyan](y/n/e=수정)[/cyan] ").strip().lower()
        if choice in ('y', 'yes'):
            return True
        elif choice in ('n', 'no'):
            return False
        elif choice in ('e', 'edit'):
            console.print("[yellow]기획서 수정은 아직 지원되지 않습니다. 다시 시작해주세요.[/yellow]")
            return False


def _review_tasks(tasks: list[PlanTask]) -> bool:
    """태스크 목록을 사용자에게 보여주고 승인을 받습니다."""
    console.print(Panel(
        f"[bold]총 {len(tasks)}개 태스크[/bold]",
        title="[cyan]작업 분해 결과[/cyan]",
        box=box.ROUNDED,
        border_style="cyan"
    ))

    for i, task in enumerate(tasks, 1):
        tree = Tree(f"[bold cyan]{i}. {task.title}[/bold cyan] ({task.id})")
        tree.add(f"[bold]목표:[/bold] {task.goal}")

        if task.files_to_modify:
            files_branch = tree.add("[bold]수정 파일:[/bold]")
            for f in task.files_to_modify:
                files_branch.add(f"[dim]{f}[/dim]")

        if task.expected_logic:
            logic_preview = task.expected_logic[:200]
            if len(task.expected_logic) > 200:
                logic_preview += "..."
            tree.add(f"[bold]예상 로직:[/bold] {logic_preview}")

        if task.dependencies:
            tree.add(f"[bold]선행 작업:[/bold] {', '.join(task.dependencies)}")

        if task.acceptance_criteria:
            criteria_branch = tree.add("[bold]완료 조건:[/bold]")
            for c in task.acceptance_criteria:
                criteria_branch.add(f"[dim]✓ {c}[/dim]")

        console.print(tree)
        console.print()

    # 승인 여부 확인
    console.print(Panel(
        "[bold yellow]중요:[/bold yellow] 승인하면 작업이 시작됩니다.\n"
        "거부하면 기획 단계를 종료하고 수정 후 다시 시작할 수 있습니다.",
        box=box.ROUNDED,
        border_style="yellow"
    ))

    while True:
        choice = console.input("[bold]모든 태스크를 승인하시겠습니까? [/bold][cyan](y/n)[/cyan] ").strip().lower()
        if choice in ('y', 'yes'):
            return True
        elif choice in ('n', 'no'):
            return False


def _generate_spec_markdown(spec: FeatureSpec, result: PlanModeResult) -> str:
    """기획서를 마크다운 문자열로 변환합니다."""
    lines = [
        f"# {spec.feature_name}",
        "",
        f"## 요약",
        spec.summary,
        "",
    ]

    if spec.requirements:
        lines.append("## 요구사항")
        for req in spec.requirements:
            lines.append(f"- {req}")
        lines.append("")

    if spec.architecture_decisions:
        lines.append("## 아키텍처 결정")
        for dec in spec.architecture_decisions:
            lines.append(f"- {dec}")
        lines.append("")

    if spec.data_model:
        lines.append("## 데이터 모델")
        lines.append("```json")
        import json
        lines.append(json.dumps(spec.data_model, indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")

    if spec.error_handling:
        lines.append("## 에러 처리")
        for err in spec.error_handling:
            lines.append(f"- {err}")
        lines.append("")

    if spec.conventions:
        lines.append("## 준수 컨벤션")
        for conv in spec.conventions:
            lines.append(f"- {conv}")
        lines.append("")

    if spec.constraints:
        lines.append("## 제약 조건")
        for con in spec.constraints:
            lines.append(f"- {con}")
        lines.append("")

    if spec.out_of_scope:
        lines.append("## 범위 외")
        for oos in spec.out_of_scope:
            lines.append(f"- {oos}")
        lines.append("")

    if result.tasks:
        lines.append("## 태스크 목록")
        for task in result.tasks:
            lines.append(f"### {task.id}: {task.title}")
            lines.append(f"- **목표:** {task.goal}")
            if task.files_to_modify:
                lines.append(f"- **파일:** {', '.join(task.files_to_modify)}")
            if task.expected_logic:
                lines.append(f"- **로직:** {task.expected_logic}")
            if task.acceptance_criteria:
                lines.append("- **완료 조건:**")
                for c in task.acceptance_criteria:
                    lines.append(f"  - {c}")
            lines.append("")

    return "\n".join(lines)


def _display_project_analysis(analysis: ProjectAnalysis):
    """프로젝트 분석 결과를 마크다운으로 표시합니다."""
    # 분석 결과를 마크다운 문서로 구성
    md_parts = [
        f"## 프로젝트 분석 결과",
        "",
        f"**경로:** `{analysis.project_path}`",
        "",
    ]

    if analysis.languages:
        md_parts.append(f"**언어:** {', '.join(analysis.languages)}")

    if analysis.frameworks:
        md_parts.append(f"**프레임워크:** {', '.join(analysis.frameworks)}")

    if analysis.structure_summary:
        md_parts.append("")
        md_parts.append("### 구조")
        md_parts.append(analysis.structure_summary)

    if analysis.conventions:
        md_parts.append("")
        md_parts.append("### 감지된 컨벤션")
        for conv in analysis.conventions:
            md_parts.append(f"- {conv}")

    if analysis.key_files:
        md_parts.append("")
        md_parts.append("### 주요 파일")
        for f in analysis.key_files[:5]:
            md_parts.append(f"- `{f}`")

    console.print(Panel(
        render_markdown("\n".join(md_parts)),
        title="[cyan]Gemini CLI 분석[/cyan]",
        box=box.ROUNDED,
        border_style="cyan"
    ))
    console.print()


def _wait_for_approve() -> bool:
    """사용자에게 'approve' 입력을 받습니다."""
    console.print(Panel(
        "[bold yellow]승인 대기 중[/bold yellow]\n\n"
        "[dim]위 태스크 목록을 검토한 후[/dim]\n"
        "[bold]'approve'[/bold][dim]를 입력하면 다음 단계로 진행합니다.[/dim]\n"
        "[dim]취소하려면 'cancel' 또는 Ctrl+C를 입력하세요.[/dim]",
        box=box.DOUBLE,
        border_style="yellow"
    ))

    while True:
        try:
            user_input = console.input("\n[bold cyan]>>> [/bold cyan]").strip().lower()

            if user_input == "approve":
                console.print("[green]승인되었습니다.[/green]")
                return True
            elif user_input in ("cancel", "exit", "quit", "n", "no"):
                console.print("[yellow]취소되었습니다.[/yellow]")
                return False
            else:
                console.print("[dim]'approve' 또는 'cancel'을 입력하세요.[/dim]")

        except KeyboardInterrupt:
            console.print("\n[yellow]취소되었습니다.[/yellow]")
            return False


def cmd_plan(args):
    """Plan Mode - Gemini CLI 기반 기획/설계 단계를 실행합니다."""
    goal = args.goal
    status_manager = StatusManager(console, spinner="dots")

    console.print(Panel(
        f"[bold cyan]Plan Mode (Gemini CLI)[/bold cyan]\n\n"
        f"[dim]Gemini CLI가 프로젝트를 분석하고 인터뷰를 진행합니다.[/dim]\n"
        f"[dim]'approve' 입력 전까지 실제 작업은 시작되지 않습니다.[/dim]",
        box=box.DOUBLE,
        border_style="cyan"
    ))
    console.print()

    console.print(f"[bold]목표:[/bold] {goal}")
    console.print()

    commander = None

    try:
        # 1. Gemini CLI Wrapper 초기화 (StatusManager 연동)
        status_manager.start("Gemini CLI 초기화")

        try:
            commander = GeminiCLIWrapper(
                verbose=args.verbose,
                on_status=create_status_callback(status_manager)
            )

            # 로그인 상태 확인
            if not commander.check_login_status():
                status_manager.stop(success=False, message="Gemini CLI 미설치 또는 미로그인")
                console.print("[yellow]경고: Gemini CLI가 설치되지 않았거나 로그인되지 않았습니다.[/yellow]")
                console.print("[dim]'npm install -g @google/gemini-cli && gemini login'을 실행하세요.[/dim]")
                return

        except Exception as e:
            status_manager.stop(success=False, message=f"초기화 오류: {e}")
            console.print("[dim]Gemini CLI가 설치되어 있는지 확인하세요.[/dim]")
            return

        # 2. 프로젝트 분석 (StatusManager가 인플레이스로 상태 업데이트)
        try:
            project_analysis = commander.analyze_project()
            status_manager.stop(success=True, message="프로젝트 분석 완료")
        except Exception as e:
            status_manager.stop(success=False, message="프로젝트 분석 실패")
            project_analysis = ProjectAnalysis(project_path=os.getcwd())

        # 분석 결과 표시
        _display_project_analysis(project_analysis)

        # 3. 인터뷰 시작
        console.print(Panel(
            "[bold]Speckit 인터뷰를 시작합니다[/bold]\n\n"
            "[dim]Gemini CLI가 아키텍처, 데이터 모델, 예외 처리, 컨벤션에 대해 질문합니다.[/dim]",
            box=box.ROUNDED,
            border_style="yellow"
        ))
        console.print()

        # 4. Plan Mode 실행
        result = commander.run_plan_mode(
            user_goal=goal,
            on_question=_ask_interview_question,
            on_spec_review=_review_spec,
            on_tasks_review=None  # 별도의 approve 워크플로우 사용
        )

        # 분석 결과 저장
        result.project_analysis = project_analysis

        # 5. 태스크 목록 표시 (승인 대기 전)
        if result.tasks:
            console.print(Panel(
                f"[bold]총 {len(result.tasks)}개 태스크 생성됨[/bold]",
                title="[cyan]태스크 목록[/cyan]",
                box=box.ROUNDED,
                border_style="cyan"
            ))

            for i, task in enumerate(result.tasks, 1):
                tree = Tree(f"[bold cyan]{i}. {task.title}[/bold cyan] ({task.id})")
                tree.add(f"[bold]목표:[/bold] {task.goal}")

                if task.files_to_modify:
                    files_branch = tree.add("[bold]수정 파일:[/bold]")
                    for f in task.files_to_modify:
                        files_branch.add(f"[dim]{f}[/dim]")

                if task.expected_logic:
                    logic_preview = task.expected_logic[:150]
                    if len(task.expected_logic) > 150:
                        logic_preview += "..."
                    tree.add(f"[bold]예상 로직:[/bold] {logic_preview}")

                if task.acceptance_criteria:
                    criteria_branch = tree.add("[bold]완료 조건:[/bold]")
                    for c in task.acceptance_criteria:
                        criteria_branch.add(f"[dim]✓ {c}[/dim]")

                console.print(tree)
                console.print()

        # 6. 승인 대기 (approve 입력 필요)
        result.approved = _wait_for_approve()

        # 7. 결과 처리
        if result.approved and result.feature_spec:
            console.print(Panel(
                "[bold green]Plan Mode 완료 - 승인됨[/bold green]\n\n"
                f"기획서: {result.feature_spec.feature_name}\n"
                f"태스크: {len(result.tasks)}개",
                box=box.DOUBLE,
                border_style="green"
            ))

            # 기획서를 specs/ 디렉토리에 저장
            spec_content = _generate_spec_markdown(result.feature_spec, result)

            # save_feature_spec 함수 직접 호출 (MCP 도구가 아닌 직접 구현)
            try:
                from pathlib import Path
                spec_dir = Path.cwd() / "specs"
                spec_dir.mkdir(parents=True, exist_ok=True)
                spec_file = spec_dir / f"{result.feature_spec.feature_name}.md"
                spec_file.write_text(spec_content, encoding="utf-8")

                console.print(f"\n[green]기획서 저장 완료:[/green] {spec_file}")
                result.spec_file_path = str(spec_file)
            except Exception as e:
                console.print(f"[yellow]기획서 저장 실패: {e}[/yellow]")

            # Scribe를 통해 기록
            try:
                from minmo.scribe_mcp import _log_event_impl as log_event
                log_event(
                    agent="commander",
                    content=f"Plan Mode 완료: {result.feature_spec.feature_name}",
                    metadata=json.dumps({
                        "feature_name": result.feature_spec.feature_name,
                        "task_count": len(result.tasks),
                        "spec_file": result.spec_file_path
                    }, ensure_ascii=False)
                )
            except Exception:
                pass

            # 실행 여부 확인
            console.print()
            execute = console.input("[bold]지금 바로 실행하시겠습니까? [/bold][cyan](y/n)[/cyan] ").strip().lower()

            if execute in ('y', 'yes'):
                console.print("\n[cyan]작업 실행을 시작합니다...[/cyan]\n")
                # TODO: 오케스트레이터로 태스크 실행
                console.print("[yellow]태스크 실행 기능은 추후 구현 예정입니다.[/yellow]")
            else:
                console.print("\n[dim]'minmo run' 명령으로 나중에 실행할 수 있습니다.[/dim]")

        else:
            console.print(Panel(
                "[bold yellow]Plan Mode 종료 - 미승인[/bold yellow]\n\n"
                "[dim]태스크가 승인되지 않았습니다.[/dim]\n"
                "[dim]요구사항을 수정하고 다시 시도해주세요.[/dim]",
                box=box.ROUNDED,
                border_style="yellow"
            ))

    except KeyboardInterrupt:
        status_manager.stop(success=False)
        console.print("\n[yellow]사용자에 의해 중단되었습니다.[/yellow]")
    except Exception as e:
        status_manager.stop(success=False)
        console.print(f"\n[red]오류 발생: {e}[/red]")
        import traceback
        if args.verbose:
            traceback.print_exc()
    finally:
        # Gemini CLI 세션 정리
        if commander:
            try:
                commander.close()
            except Exception:
                pass


# ============================================================
# 멀티 모드 실행 함수들
# ============================================================

def run_direct_mode(goal: str, verbose: bool = False):
    """
    DIRECT 모드 - 지휘관을 건너뛰고 작업자(Claude)에게 바로 명령 전달

    Args:
        goal: 실행할 명령/목표
        verbose: 상세 출력 여부
    """
    from minmo.claude_wrapper import ClaudeCodeWrapper
    from minmo.scribe_mcp import _log_event_impl as log_event

    show_mode_panel(MinmoMode.DIRECT, goal)

    if not goal:
        console.print("[red]오류: 명령이 필요합니다.[/red]")
        console.print("[dim]사용법: /direct [명령][/dim]")
        return

    status_manager = StatusManager(console, spinner="dots")

    try:
        # Scribe에 기록
        log_event(
            agent="cli",
            content=f"DIRECT 모드 시작: {goal[:100]}",
            metadata=json.dumps({"mode": "direct", "goal": goal})
        )

        status_manager.start("Claude Code 초기화")

        # Claude Code 작업자 초기화
        worker = ClaudeCodeWrapper(
            on_output=lambda msg: console.print(f"[dim]{msg}[/dim]") if verbose else None,
            verbose=verbose
        )

        status_manager.update("작업 실행", 0)

        # 단일 태스크로 실행
        task = {
            "id": "direct_task",
            "title": goal[:50],
            "description": goal,
            "goal": goal
        }

        result = worker.execute(task)
        status_manager.stop(success=True, message="작업 완료")

        # 결과 출력
        if result.output:
            console.print(Panel(
                render_markdown(result.output),
                title="[green]실행 결과[/green]",
                box=box.ROUNDED,
                border_style="green"
            ))

        if result.files_modified:
            console.print(f"\n[dim]수정된 파일: {', '.join(result.files_modified)}[/dim]")

        if result.error:
            console.print(f"\n[red]오류: {result.error}[/red]")

        # 결과 기록
        log_event(
            agent="cli",
            content=f"DIRECT 모드 완료: {result.status.value}",
            metadata=json.dumps({
                "mode": "direct",
                "status": result.status.value,
                "files_modified": result.files_modified,
                "duration": result.duration_seconds
            })
        )

    except KeyboardInterrupt:
        status_manager.stop(success=False)
        console.print("\n[yellow]사용자에 의해 중단되었습니다.[/yellow]")
    except Exception as e:
        status_manager.stop(success=False)
        console.print(f"\n[red]오류 발생: {e}[/red]")
        if verbose:
            import traceback
            traceback.print_exc()


def run_analyze_mode(goal: str, verbose: bool = False):
    """
    ANALYZE 모드 - 프로젝트/파일 분석 후 종합 리포트 출력 (수정 없음)

    Args:
        goal: 분석 대상 설명
        verbose: 상세 출력 여부
    """
    from minmo.scribe_mcp import _log_event_impl as log_event

    show_mode_panel(MinmoMode.ANALYZE, goal)

    status_manager = StatusManager(console, spinner="dots")
    commander = None

    try:
        # Scribe에 기록
        log_event(
            agent="cli",
            content=f"ANALYZE 모드 시작: {goal[:100] if goal else '프로젝트 전체'}",
            metadata=json.dumps({"mode": "analyze", "target": goal or "project"})
        )

        status_manager.start("Gemini CLI 초기화")

        # Gemini CLI Wrapper 초기화
        commander = GeminiCLIWrapper(
            verbose=verbose,
            on_status=create_status_callback(status_manager)
        )

        # 로그인 상태 확인
        if not commander.check_login_status():
            status_manager.stop(success=False, message="Gemini CLI 미설치 또는 미로그인")
            console.print("[yellow]경고: Gemini CLI가 설치되지 않았거나 로그인되지 않았습니다.[/yellow]")
            return

        # 1. 프로젝트 분석
        project_analysis = commander.analyze_project()
        status_manager.update("프로젝트 분석 완료", 0)

        # 2. 상세 분석 보고서 생성
        analysis_goal = goal or "프로젝트 전체 구조와 아키텍처를 분석해주세요."
        detailed_report = commander._generate_detailed_analysis(analysis_goal, project_analysis)

        status_manager.stop(success=True, message="분석 완료")

        # 3. 종합 리포트 출력
        console.print()
        console.print(Panel(
            "[bold magenta]MINMO 종합 분석 리포트[/bold magenta]",
            box=box.DOUBLE,
            border_style="magenta"
        ))
        console.print()

        # 프로젝트 정보
        info_md = f"""## 프로젝트 정보

**경로:** `{project_analysis.project_path}`

**언어:** {', '.join(project_analysis.languages) or '감지되지 않음'}

**프레임워크:** {', '.join(project_analysis.frameworks) or '감지되지 않음'}

**구조:** {project_analysis.structure_summary or '분석되지 않음'}
"""

        if project_analysis.key_files:
            info_md += "\n### 주요 파일\n"
            for f in project_analysis.key_files[:10]:
                info_md += f"- `{f}`\n"

        if project_analysis.conventions:
            info_md += "\n### 감지된 컨벤션\n"
            for c in project_analysis.conventions[:5]:
                info_md += f"- {c}\n"

        console.print(Panel(
            render_markdown(info_md),
            title="[cyan]1. 프로젝트 개요[/cyan]",
            box=box.ROUNDED,
            border_style="cyan"
        ))
        console.print()

        # 상세 분석 보고서
        console.print(Panel(
            render_markdown(detailed_report),
            title="[magenta]2. 상세 분석[/magenta]",
            box=box.ROUNDED,
            border_style="magenta"
        ))
        console.print()

        # 결론
        console.print(Panel(
            "[bold]분석이 완료되었습니다.[/bold]\n\n"
            "[dim]이 분석 결과를 바탕으로:[/dim]\n"
            "• [yellow]/plan[/yellow] 명령으로 새 기능을 기획하거나\n"
            "• [green]/direct[/green] 명령으로 즉시 수정을 진행할 수 있습니다.",
            box=box.ROUNDED,
            border_style="dim"
        ))

        # 결과 기록
        log_event(
            agent="cli",
            content="ANALYZE 모드 완료",
            metadata=json.dumps({
                "mode": "analyze",
                "project_path": project_analysis.project_path,
                "languages": project_analysis.languages,
                "frameworks": project_analysis.frameworks
            })
        )

    except KeyboardInterrupt:
        status_manager.stop(success=False)
        console.print("\n[yellow]사용자에 의해 중단되었습니다.[/yellow]")
    except Exception as e:
        status_manager.stop(success=False)
        console.print(f"\n[red]오류 발생: {e}[/red]")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        if commander:
            try:
                commander.close()
            except Exception:
                pass


def run_free_mode(goal: str, verbose: bool = False):
    """
    FREE 모드 - 지휘관이 입력을 분석하여 적절한 처리 방식 결정

    지휘관이 요청을 분석하고:
    - 복잡한 기능 개발 → PLAN 모드로 전환 권장
    - 단순 작업 → 바로 실행
    - 분석 요청 → 분석 결과 출력

    Args:
        goal: 사용자 요청
        verbose: 상세 출력 여부
    """
    from minmo.scribe_mcp import _log_event_impl as log_event

    show_mode_panel(MinmoMode.FREE, goal)

    if not goal:
        console.print("[red]오류: 요청이 필요합니다.[/red]")
        console.print("[dim]사용법: /free [요청] 또는 그냥 [요청] 입력[/dim]")
        return

    status_manager = StatusManager(console, spinner="dots")
    commander = None

    try:
        log_event(
            agent="cli",
            content=f"FREE 모드 시작: {goal[:100]}",
            metadata=json.dumps({"mode": "free", "goal": goal})
        )

        status_manager.start("요청 분석")

        # Gemini CLI로 요청 분석
        commander = GeminiCLIWrapper(
            verbose=verbose,
            on_status=create_status_callback(status_manager)
        )

        if not commander.check_login_status():
            status_manager.stop(success=False, message="Gemini CLI 미설치 또는 미로그인")
            console.print("[yellow]경고: Gemini CLI가 설치되지 않았거나 로그인되지 않았습니다.[/yellow]")
            console.print("[dim]DIRECT 모드로 폴백합니다...[/dim]")
            console.print()
            run_direct_mode(goal, verbose)
            return

        # 요청 유형 분석
        analyze_prompt = f"""다음 요청을 분석하고 적절한 처리 방식을 결정해주세요.

요청: {goal}

JSON 형식으로 응답:
```json
{{
    "request_type": "plan|direct|analyze|simple_answer",
    "reasoning": "판단 근거",
    "needs_planning": true/false,
    "estimated_complexity": "low|medium|high",
    "suggested_response": "간단한 답변이면 여기에 직접 답변"
}}
```

- plan: 새 기능 구현, 아키텍처 변경 등 기획이 필요한 복잡한 작업
- direct: 파일 수정, 버그 수정 등 명확한 단일 작업
- analyze: 분석 요청 (코드 분석, 구조 파악 등)
- simple_answer: 질문에 대한 간단한 답변 (코드 변경 불필요)
"""

        response = commander._run_gemini(analyze_prompt, "요청 분석")
        analysis = commander._parse_json_response(response)

        status_manager.stop(success=True, message="분석 완료")

        request_type = analysis.get("request_type", "direct")
        reasoning = analysis.get("reasoning", "")
        needs_planning = analysis.get("needs_planning", False)

        # 분석 결과 표시
        console.print(Panel(
            f"[bold]지휘관 분석 결과[/bold]\n\n"
            f"[dim]요청 유형:[/dim] {request_type}\n"
            f"[dim]판단 근거:[/dim] {reasoning[:100]}{'...' if len(reasoning) > 100 else ''}\n"
            f"[dim]기획 필요:[/dim] {'예' if needs_planning else '아니오'}",
            box=box.ROUNDED,
            border_style="cyan"
        ))
        console.print()

        # 유형에 따른 처리
        if request_type == "simple_answer":
            # 간단한 답변
            suggested = analysis.get("suggested_response", "")
            if suggested:
                console.print(Panel(
                    render_markdown(suggested),
                    title="[cyan]답변[/cyan]",
                    box=box.ROUNDED,
                    border_style="cyan"
                ))
            return

        if request_type == "plan" or needs_planning:
            # PLAN 모드 권장
            console.print(Panel(
                "[bold yellow]이 요청은 기획이 필요합니다.[/bold yellow]\n\n"
                "[dim]복잡한 기능 개발이나 아키텍처 변경은\n"
                "PLAN 모드에서 인터뷰를 통해 요구사항을 명확히 하는 것이 좋습니다.[/dim]",
                box=box.ROUNDED,
                border_style="yellow"
            ))

            switch = console.input("\n[bold]PLAN 모드로 전환하시겠습니까? [/bold][cyan](y/n)[/cyan] ").strip().lower()
            if switch in ('y', 'yes'):
                console.print()
                commander.close()
                commander = None
                # Plan 모드 직접 호출
                run_plan_mode_interactive(goal, verbose)
            else:
                console.print("[dim]DIRECT 모드로 진행합니다...[/dim]")
                console.print()
                commander.close()
                commander = None
                run_direct_mode(goal, verbose)
            return

        if request_type == "analyze":
            # ANALYZE 모드로 전환
            console.print("[dim]분석 요청으로 판단되어 ANALYZE 모드로 전환합니다...[/dim]")
            console.print()
            commander.close()
            commander = None
            run_analyze_mode(goal, verbose)
            return

        # DIRECT 모드 실행
        console.print("[dim]단순 작업으로 판단되어 바로 실행합니다...[/dim]")
        console.print()
        commander.close()
        commander = None
        run_direct_mode(goal, verbose)

    except KeyboardInterrupt:
        status_manager.stop(success=False)
        console.print("\n[yellow]사용자에 의해 중단되었습니다.[/yellow]")
    except Exception as e:
        status_manager.stop(success=False)
        console.print(f"\n[red]오류 발생: {e}[/red]")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        if commander:
            try:
                commander.close()
            except Exception:
                pass


def run_plan_mode_interactive(goal: str, verbose: bool = False):
    """
    PLAN 모드 - interactive_mode에서 호출용

    기존 cmd_plan과 유사하지만 argparse 없이 동작합니다.

    Args:
        goal: 구현할 기능 요구사항
        verbose: 상세 출력 여부
    """
    from minmo.scribe_mcp import _log_event_impl as log_event

    show_mode_panel(MinmoMode.PLAN, goal)

    if not goal:
        console.print("[red]오류: 요구사항이 필요합니다.[/red]")
        console.print("[dim]사용법: /plan [요구사항][/dim]")
        return

    status_manager = StatusManager(console, spinner="dots")
    commander = None

    try:
        log_event(
            agent="cli",
            content=f"PLAN 모드 시작: {goal[:100]}",
            metadata=json.dumps({"mode": "plan", "goal": goal})
        )

        # 1. Gemini CLI 초기화
        status_manager.start("Gemini CLI 초기화")

        commander = GeminiCLIWrapper(
            verbose=verbose,
            on_status=create_status_callback(status_manager)
        )

        if not commander.check_login_status():
            status_manager.stop(success=False, message="Gemini CLI 미설치 또는 미로그인")
            console.print("[yellow]경고: Gemini CLI가 설치되지 않았거나 로그인되지 않았습니다.[/yellow]")
            return

        # 2. 프로젝트 분석
        try:
            project_analysis = commander.analyze_project()
            status_manager.stop(success=True, message="프로젝트 분석 완료")
        except Exception:
            status_manager.stop(success=False, message="프로젝트 분석 실패")
            project_analysis = ProjectAnalysis(project_path=os.getcwd())

        _display_project_analysis(project_analysis)

        # 3. 인터뷰 시작
        console.print(Panel(
            "[bold]Speckit 인터뷰를 시작합니다[/bold]\n\n"
            "[dim]Gemini CLI가 아키텍처, 데이터 모델, 예외 처리, 컨벤션에 대해 질문합니다.[/dim]",
            box=box.ROUNDED,
            border_style="yellow"
        ))
        console.print()

        # 4. Plan Mode 실행
        result = commander.run_plan_mode(
            user_goal=goal,
            on_question=_ask_interview_question,
            on_spec_review=_review_spec,
            on_tasks_review=None
        )

        result.project_analysis = project_analysis

        # 5. 태스크 목록 표시
        if result.tasks:
            console.print(Panel(
                f"[bold]총 {len(result.tasks)}개 태스크 생성됨[/bold]",
                title="[cyan]태스크 목록[/cyan]",
                box=box.ROUNDED,
                border_style="cyan"
            ))

            for i, task in enumerate(result.tasks, 1):
                tree = Tree(f"[bold cyan]{i}. {task.title}[/bold cyan] ({task.id})")
                tree.add(f"[bold]목표:[/bold] {task.goal}")

                if task.files_to_modify:
                    files_branch = tree.add("[bold]수정 파일:[/bold]")
                    for f in task.files_to_modify:
                        files_branch.add(f"[dim]{f}[/dim]")

                if task.acceptance_criteria:
                    criteria_branch = tree.add("[bold]완료 조건:[/bold]")
                    for c in task.acceptance_criteria:
                        criteria_branch.add(f"[dim]✓ {c}[/dim]")

                console.print(tree)
                console.print()

        # 6. 승인 대기
        result.approved = _wait_for_approve()

        # 7. 결과 처리
        if result.approved and result.feature_spec:
            console.print(Panel(
                "[bold green]Plan Mode 완료 - 승인됨[/bold green]\n\n"
                f"기획서: {result.feature_spec.feature_name}\n"
                f"태스크: {len(result.tasks)}개",
                box=box.DOUBLE,
                border_style="green"
            ))

            # 기획서 저장
            spec_content = _generate_spec_markdown(result.feature_spec, result)
            try:
                spec_dir = Path.cwd() / "specs"
                spec_dir.mkdir(parents=True, exist_ok=True)
                spec_file = spec_dir / f"{result.feature_spec.feature_name}.md"
                spec_file.write_text(spec_content, encoding="utf-8")
                console.print(f"\n[green]기획서 저장 완료:[/green] {spec_file}")
            except Exception as e:
                console.print(f"[yellow]기획서 저장 실패: {e}[/yellow]")

            # 실행 여부 확인
            console.print()
            execute = console.input("[bold]지금 바로 실행하시겠습니까? [/bold][cyan](y/n)[/cyan] ").strip().lower()

            if execute in ('y', 'yes'):
                console.print("\n[cyan]DIRECT 모드로 태스크를 실행합니다...[/cyan]\n")
                # 첫 번째 태스크부터 순차 실행
                for task in result.tasks:
                    run_direct_mode(task.goal, verbose)
            else:
                console.print("\n[dim]나중에 /direct 명령으로 실행할 수 있습니다.[/dim]")
        else:
            console.print(Panel(
                "[bold yellow]Plan Mode 종료 - 미승인[/bold yellow]",
                box=box.ROUNDED,
                border_style="yellow"
            ))

    except KeyboardInterrupt:
        status_manager.stop(success=False)
        console.print("\n[yellow]사용자에 의해 중단되었습니다.[/yellow]")
    except Exception as e:
        status_manager.stop(success=False)
        console.print(f"\n[red]오류 발생: {e}[/red]")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        if commander:
            try:
                commander.close()
            except Exception:
                pass


def execute_mode(parsed_cmd: ParsedCommand, verbose: bool = False):
    """
    파싱된 커맨드를 기반으로 적절한 모드를 실행합니다.

    Args:
        parsed_cmd: 파싱된 커맨드 객체
        verbose: 상세 출력 여부
    """
    mode = parsed_cmd.mode
    goal = parsed_cmd.goal

    if mode == MinmoMode.HELP:
        show_help_table()
    elif mode == MinmoMode.PLAN:
        run_plan_mode_interactive(goal, verbose)
    elif mode == MinmoMode.DIRECT:
        run_direct_mode(goal, verbose)
    elif mode == MinmoMode.ANALYZE:
        run_analyze_mode(goal, verbose)
    elif mode == MinmoMode.FREE:
        run_free_mode(goal, verbose)
    else:
        console.print(f"[red]알 수 없는 모드: {mode}[/red]")


# ============================================================
# stats 명령어 - 토큰 사용량 통계
# ============================================================
def cmd_stats(args):
    """토큰 사용량 통계를 표시합니다."""
    print_header()

    session_only = getattr(args, "session", False)

    console.print(Panel(
        f"[bold]{'현재 세션' if session_only else '전체 누적'} 토큰 사용량[/bold]",
        title="[cyan]Minmo Stats[/cyan]",
        box=box.ROUNDED,
        border_style="cyan"
    ))
    console.print()

    # 사용량 통계 조회
    result = call_get_usage_stats(session_only=session_only)

    if not result.get("success"):
        console.print(f"[red]오류: {result.get('error', '알 수 없는 오류')}[/red]")
        return

    models = result.get("models", [])
    totals = result.get("totals", {})

    if not models:
        console.print("[dim]아직 기록된 사용량이 없습니다.[/dim]")
        console.print("[dim]minmo를 실행하면 토큰 사용량이 자동으로 기록됩니다.[/dim]")
        return

    # 모델별 사용량 테이블
    table = Table(
        title="모델별 토큰 사용량",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("모델", style="cyan", no_wrap=True)
    table.add_column("입력", justify="right", style="green")
    table.add_column("출력", justify="right", style="yellow")
    table.add_column("총합", justify="right", style="bold white")
    table.add_column("호출 수", justify="right", style="dim")
    table.add_column("최대 컨텍스트", justify="right", style="dim")
    table.add_column("사용률", justify="right")

    for model_data in models:
        model_name = model_data["model"]
        input_tokens = model_data["input_tokens"]
        output_tokens = model_data["output_tokens"]
        total_tokens = model_data["total_tokens"]
        call_count = model_data["call_count"]
        max_context = model_data["max_context"]
        usage_ratio = model_data["usage_ratio"]

        # 사용률에 따른 색상
        if usage_ratio < 25:
            ratio_color = "green"
        elif usage_ratio < 50:
            ratio_color = "yellow"
        elif usage_ratio < 75:
            ratio_color = "orange1"
        else:
            ratio_color = "red"

        # 숫자 포맷팅
        def format_number(n: int) -> str:
            if n >= 1_000_000:
                return f"{n / 1_000_000:.1f}M"
            elif n >= 1_000:
                return f"{n / 1_000:.1f}K"
            return str(n)

        table.add_row(
            model_name,
            format_number(input_tokens),
            format_number(output_tokens),
            format_number(total_tokens),
            str(call_count),
            format_number(max_context),
            f"[{ratio_color}]{usage_ratio:.1f}%[/{ratio_color}]"
        )

    console.print(table)
    console.print()

    # 총계 표시
    total_input = totals.get("input_tokens", 0)
    total_output = totals.get("output_tokens", 0)
    total_all = totals.get("total_tokens", 0)
    total_calls = totals.get("call_count", 0)

    def format_number(n: int) -> str:
        if n >= 1_000_000:
            return f"{n / 1_000_000:.1f}M"
        elif n >= 1_000:
            return f"{n / 1_000:.1f}K"
        return str(n)

    console.print(Panel(
        f"[green]입력: {format_number(total_input)}[/green] | "
        f"[yellow]출력: {format_number(total_output)}[/yellow] | "
        f"[bold white]총합: {format_number(total_all)}[/bold white] | "
        f"[dim]호출 수: {total_calls}[/dim]",
        title="[bold]총계[/bold]",
        box=box.ROUNDED,
        border_style="white"
    ))

    if session_only:
        session_id = result.get("session_id", "unknown")
        console.print(f"\n[dim]세션 ID: {session_id}[/dim]")


def main():
    """메인 진입점"""
    parser = argparse.ArgumentParser(
        prog="minmo",
        description="Minmo-Engine: MCP 통합 자동화 프레임워크"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"minmo {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령어")

    # init 명령어
    init_parser = subparsers.add_parser("init", help="프로젝트를 Minmo용으로 초기화합니다")
    init_parser.add_argument("-p", "--path", default=".", help="프로젝트 경로")

    # run 명령어 (기본)
    run_parser = subparsers.add_parser("run", help="목표를 실행합니다")
    run_parser.add_argument("goal", nargs="?", help="실행할 목표")
    run_parser.add_argument("-i", "--interactive", action="store_true", help="대화형 모드")

    # index 명령어
    index_parser = subparsers.add_parser("index", help="프로젝트를 인덱싱합니다")
    index_parser.add_argument("-p", "--path", default=".", help="프로젝트 경로")
    index_parser.add_argument("-f", "--force", action="store_true", help="전체 재인덱싱")
    index_parser.add_argument("-w", "--watch", action="store_true", help="파일 변경 감시")

    # search 명령어
    search_parser = subparsers.add_parser("search", help="코드베이스에서 검색합니다")
    search_parser.add_argument("query", help="검색 쿼리")
    search_parser.add_argument("-p", "--path", default=".", help="프로젝트 경로")
    search_parser.add_argument("-l", "--limit", type=int, default=10, help="최대 결과 수")

    # overview 명령어
    overview_parser = subparsers.add_parser("overview", help="프로젝트 개요를 표시합니다")
    overview_parser.add_argument("-p", "--path", default=".", help="프로젝트 경로")

    # plan 명령어
    plan_parser = subparsers.add_parser("plan", help="Plan Mode - 기획/설계 단계를 실행합니다")
    plan_parser.add_argument("goal", help="구현할 기능 요구사항")
    plan_parser.add_argument("-v", "--verbose", action="store_true", help="상세 출력")

    # stats 명령어
    stats_parser = subparsers.add_parser("stats", help="토큰 사용량 통계를 표시합니다")
    stats_parser.add_argument("-s", "--session", action="store_true", help="현재 세션만 표시")

    args = parser.parse_args()

    # Ctrl+C 핸들링
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    if args.command == "init":
        cmd_init(args)
    elif args.command == "index":
        cmd_index(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "overview":
        cmd_overview(args)
    elif args.command == "plan":
        print_header()
        cmd_plan(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "run":
        if args.goal and not args.interactive:
            print_header()
            run_orchestrator(args.goal)
        else:
            interactive_mode()
    else:
        # 명령어 없이 goal만 주어진 경우 또는 대화형 모드
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            # 첫 번째 인자가 명령어가 아니면 goal로 처리
            print_header()
            run_orchestrator(sys.argv[1])
        else:
            interactive_mode()


if __name__ == "__main__":
    main()
