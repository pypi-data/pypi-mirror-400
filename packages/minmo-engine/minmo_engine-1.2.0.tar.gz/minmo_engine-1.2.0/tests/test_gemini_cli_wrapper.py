"""
Tests for minmo.gemini_cli_wrapper module (Google Gen AI SDK v1.0+).

Google Gen AI SDK 기반 래퍼 테스트
"""

import os
import json
from unittest.mock import MagicMock, patch

import pytest

from minmo.gemini_cli_wrapper import (
    InterviewFocus,
    ProjectAnalysis,
    InterviewQuestion,
    InterviewAnswer,
    FeatureSpec,
    PlanTask,
    PlanModeResult,
    GeminiCLIWrapper,
    COMMANDER_CLI_CONSTITUTION,
    # Tool functions
    analyze_directory,
    read_file,
    search_code,
    get_project_conventions,
    get_project_architecture,
)


class TestInterviewFocus:
    """Tests for InterviewFocus enum."""

    def test_enum_values(self):
        assert InterviewFocus.ARCHITECTURE.value == "architecture"
        assert InterviewFocus.DATA_MODEL.value == "data_model"
        assert InterviewFocus.EXCEPTION_HANDLING.value == "exception_handling"
        assert InterviewFocus.CONVENTION.value == "convention"
        assert InterviewFocus.INTEGRATION.value == "integration"
        assert InterviewFocus.TESTING.value == "testing"


class TestProjectAnalysis:
    """Tests for ProjectAnalysis dataclass."""

    def test_create_analysis(self):
        analysis = ProjectAnalysis(
            project_path="/test/project",
            languages=["Python", "JavaScript"],
            frameworks=["FastAPI", "React"],
            structure_summary="A web application with backend and frontend",
            key_files=["main.py", "app.tsx"],
            conventions=["PEP 8", "ESLint"],
            dependencies=["fastapi", "react"],
        )

        assert analysis.project_path == "/test/project"
        assert "Python" in analysis.languages
        assert "FastAPI" in analysis.frameworks
        assert len(analysis.key_files) == 2

    def test_default_values(self):
        analysis = ProjectAnalysis(project_path="/test")

        assert analysis.languages == []
        assert analysis.frameworks == []
        assert analysis.structure_summary == ""
        assert analysis.key_files == []
        assert analysis.conventions == []
        assert analysis.dependencies == []


class TestInterviewQuestion:
    """Tests for InterviewQuestion dataclass."""

    def test_create_question(self):
        question = InterviewQuestion(
            question="Which database do you prefer?",
            focus=InterviewFocus.DATA_MODEL,
            options=["PostgreSQL", "MySQL", "SQLite"],
            context="We need a database for storing user data",
        )

        assert "database" in question.question
        assert question.focus == InterviewFocus.DATA_MODEL
        assert len(question.options) == 3
        assert question.context != ""

    def test_default_values(self):
        question = InterviewQuestion(
            question="Simple question?",
            focus=InterviewFocus.ARCHITECTURE
        )

        assert question.options == []
        assert question.context == ""


class TestInterviewAnswer:
    """Tests for InterviewAnswer dataclass."""

    def test_create_answer(self):
        question = InterviewQuestion(
            question="Which auth method?",
            focus=InterviewFocus.ARCHITECTURE,
            options=["JWT", "Session"],
        )
        answer = InterviewAnswer(question=question, answer="JWT")

        assert answer.question.question == "Which auth method?"
        assert answer.answer == "JWT"


class TestFeatureSpec:
    """Tests for FeatureSpec dataclass."""

    def test_create_spec(self):
        spec = FeatureSpec(
            feature_name="user_authentication",
            summary="User login and registration system",
            requirements=["Email login", "Password reset"],
            architecture_decisions=["Use JWT tokens"],
            data_model={"User": {"id": "int", "email": "str"}},
            error_handling=["Invalid credentials error"],
            conventions=["REST API naming"],
            constraints=["Must work offline"],
            out_of_scope=["Social login"],
        )

        assert spec.feature_name == "user_authentication"
        assert len(spec.requirements) == 2
        assert "Use JWT tokens" in spec.architecture_decisions
        assert "User" in spec.data_model

    def test_default_values(self):
        spec = FeatureSpec(feature_name="test", summary="Test feature")

        assert spec.requirements == []
        assert spec.architecture_decisions == []
        assert spec.data_model == {}
        assert spec.error_handling == []
        assert spec.conventions == []
        assert spec.constraints == []
        assert spec.out_of_scope == []


class TestPlanTask:
    """Tests for PlanTask dataclass."""

    def test_create_task(self):
        task = PlanTask(
            id="task_001",
            title="Create User model",
            goal="Define User dataclass with all fields",
            files_to_modify=["models/user.py"],
            expected_logic="Create User class with id, email, password_hash",
            dependencies=[],
            acceptance_criteria=["User class exists", "All fields defined"],
        )

        assert task.id == "task_001"
        assert task.title == "Create User model"
        assert len(task.files_to_modify) == 1
        assert len(task.acceptance_criteria) == 2

    def test_default_values(self):
        task = PlanTask(id="task_002", title="Test task", goal="Do something")

        assert task.files_to_modify == []
        assert task.expected_logic == ""
        assert task.dependencies == []
        assert task.acceptance_criteria == []


class TestPlanModeResult:
    """Tests for PlanModeResult dataclass."""

    def test_create_result(self):
        analysis = ProjectAnalysis(project_path="/test")
        spec = FeatureSpec(feature_name="test", summary="Test")
        tasks = [PlanTask(id="t1", title="Task 1", goal="Goal 1")]

        result = PlanModeResult(
            project_analysis=analysis,
            feature_spec=spec,
            tasks=tasks,
            interview_history=[],
            approved=True,
            spec_file_path="/specs/test.md",
        )

        assert result.project_analysis is not None
        assert result.feature_spec.feature_name == "test"
        assert len(result.tasks) == 1
        assert result.approved is True

    def test_default_values(self):
        result = PlanModeResult()

        assert result.project_analysis is None
        assert result.feature_spec is None
        assert result.tasks == []
        assert result.interview_history == []
        assert result.approved is False
        assert result.spec_file_path == ""


class TestToolFunctions:
    """Tests for tool functions."""

    def test_analyze_directory_not_found(self):
        result = analyze_directory("/nonexistent/path")
        assert "error" in result

    def test_read_file_not_found(self):
        result = read_file("/nonexistent/file.py")
        assert "error" in result

    def test_search_code_not_found(self):
        result = search_code("pattern", "/nonexistent/path")
        assert "error" in result

    def test_get_project_conventions(self, tmp_path):
        # Create a test pyproject.toml
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        result = get_project_conventions(str(tmp_path))
        assert "conventions" in result
        assert "Python project with modern tooling" in result["conventions"]

    def test_get_project_architecture(self, tmp_path):
        # Create test directories
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        result = get_project_architecture(str(tmp_path))
        assert "directories" in result
        assert "layers" in result


class TestGeminiCLIWrapper:
    """Tests for GeminiCLIWrapper class (Google Gen AI SDK v1.0+)."""

    @pytest.fixture
    def mock_scribe(self):
        """Mock the scribe_mcp functions."""
        with patch("minmo.gemini_cli_wrapper.log_event") as mock_log, \
             patch("minmo.gemini_cli_wrapper.init_database") as mock_init:
            mock_log.return_value = {"success": True}
            mock_init.return_value = None
            yield {"log_event": mock_log, "init_database": mock_init}

    @pytest.fixture
    def mock_genai(self):
        """Mock Google Gen AI SDK."""
        with patch("minmo.gemini_cli_wrapper.genai") as mock_genai:
            mock_client = MagicMock()
            mock_genai.Client.return_value = mock_client

            # Mock response
            mock_response = MagicMock()
            mock_candidate = MagicMock()
            mock_part = MagicMock()
            mock_part.text = '{"type": "test", "content": {}}'
            mock_part.function_call = None
            mock_candidate.content.parts = [mock_part]
            mock_response.candidates = [mock_candidate]

            mock_client.models.generate_content.return_value = mock_response

            yield {
                "genai": mock_genai,
                "client": mock_client,
                "response": mock_response,
                "part": mock_part,
            }

    @pytest.fixture
    def wrapper(self, mock_scribe, mock_genai):
        """Create a GeminiCLIWrapper instance with mocked dependencies."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
            wrapper = GeminiCLIWrapper(
                working_directory="/test/project",
                timeout_seconds=60,
                verbose=False
            )
            yield wrapper
            wrapper.close()

    def test_init_default_values(self, mock_scribe, mock_genai):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
            wrapper = GeminiCLIWrapper()

            assert wrapper.working_directory == os.getcwd()
            assert wrapper.timeout_seconds == 120
            assert wrapper.model_name == "gemini-2.5-flash"
            assert wrapper.verbose is False
            wrapper.close()

    def test_init_custom_values(self, mock_scribe, mock_genai):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
            wrapper = GeminiCLIWrapper(
                working_directory="/custom/path",
                timeout_seconds=300,
                model="gemini-2.5-pro",
                verbose=True
            )

            assert wrapper.working_directory == "/custom/path"
            assert wrapper.timeout_seconds == 300
            assert wrapper.model_name == "gemini-2.5-pro"
            assert wrapper.verbose is True
            wrapper.close()

    def test_init_without_api_key_raises_error(self, mock_scribe, mock_genai):
        """Test that missing API key raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GEMINI_API_KEY", None)
            os.environ.pop("GOOGLE_API_KEY", None)

            with pytest.raises(ValueError) as excinfo:
                GeminiCLIWrapper()
            assert "GEMINI_API_KEY" in str(excinfo.value)

    def test_init_with_api_key_param(self, mock_scribe, mock_genai):
        """Test initialization with API key parameter."""
        wrapper = GeminiCLIWrapper(api_key="my-api-key")
        assert wrapper.api_key == "my-api-key"
        wrapper.close()

    def test_tool_map_registered(self, wrapper):
        """Test that tools are registered in tool_map."""
        assert "analyze_directory" in wrapper.tool_map
        assert "read_file" in wrapper.tool_map
        assert "search_code" in wrapper.tool_map
        assert "get_project_conventions" in wrapper.tool_map
        assert "get_project_architecture" in wrapper.tool_map

    def test_check_login_status_success(self, wrapper, mock_genai):
        """Test successful login status check."""
        result = wrapper.check_login_status()
        assert result is True

    def test_check_login_status_failure(self, wrapper, mock_genai):
        """Test failed login status check."""
        mock_genai["client"].models.generate_content.side_effect = Exception("Auth failed")
        result = wrapper.check_login_status()
        assert result is False

    def test_parse_json_response_with_json_block(self, wrapper):
        """Test parsing JSON from markdown code block."""
        response = '''Here is the analysis:
```json
{"type": "test", "content": {"key": "value"}}
```
'''
        result = wrapper._parse_json_response(response)
        assert result["type"] == "test"
        assert result["content"]["key"] == "value"

    def test_parse_json_response_plain_json(self, wrapper):
        """Test parsing plain JSON."""
        response = '{"type": "plain", "content": {"data": 123}}'
        result = wrapper._parse_json_response(response)
        assert result["type"] == "plain"
        assert result["content"]["data"] == 123

    def test_parse_json_response_json_array(self, wrapper):
        """Test parsing JSON array."""
        response = '[{"id": 1}, {"id": 2}]'
        result = wrapper._parse_json_response(response)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_parse_json_response_invalid_json(self, wrapper):
        """Test parsing invalid JSON returns text content."""
        response = "This is not JSON at all"
        result = wrapper._parse_json_response(response)
        assert result["type"] == "text"
        assert result["content"] == response

    def test_analyze_project(self, wrapper, mock_genai):
        """Test project analysis."""
        mock_genai["part"].text = '''```json
{"languages": ["Python"], "frameworks": ["FastAPI"], "structure_summary": "A backend project", "key_files": ["main.py"], "conventions": ["PEP 8"], "dependencies": ["fastapi"]}
```'''

        result = wrapper.analyze_project("/test/project")

        assert result.project_path == "/test/project"
        assert "Python" in result.languages
        assert "FastAPI" in result.frameworks

    def test_generate_interview_questions(self, wrapper, mock_genai):
        """Test interview question generation."""
        mock_genai["part"].text = '''```json
{
  "questions": [
    {
      "question": "Which database do you prefer?",
      "focus": "data_model",
      "options": ["PostgreSQL", "MySQL", "SQLite"],
      "context": "Need to choose database"
    },
    {
      "question": "How should errors be handled?",
      "focus": "exception_handling",
      "options": ["Return error codes", "Throw exceptions"],
      "context": "Error handling strategy"
    }
  ]
}
```'''

        analysis = ProjectAnalysis(project_path="/test", languages=["Python"])
        questions = wrapper.generate_interview_questions(
            user_goal="Add user authentication",
            project_analysis=analysis
        )

        assert len(questions) == 2
        assert questions[0].focus == InterviewFocus.DATA_MODEL
        assert questions[1].focus == InterviewFocus.EXCEPTION_HANDLING

    def test_generate_interview_questions_invalid_focus(self, wrapper, mock_genai):
        """Test handling invalid focus value."""
        mock_genai["part"].text = '''```json
{
  "questions": [
    {
      "question": "Test question?",
      "focus": "invalid_focus",
      "options": [],
      "context": ""
    }
  ]
}
```'''

        questions = wrapper.generate_interview_questions("Test goal")

        # Should fall back to ARCHITECTURE
        assert len(questions) == 1
        assert questions[0].focus == InterviewFocus.ARCHITECTURE

    def test_generate_feature_spec(self, wrapper, mock_genai):
        """Test feature spec generation."""
        mock_genai["part"].text = '''```json
{
  "feature_name": "user_auth",
  "summary": "User authentication system",
  "requirements": ["Login", "Logout"],
  "architecture_decisions": ["Use JWT"],
  "data_model": {"User": {"id": "int"}},
  "error_handling": ["Invalid credentials"],
  "conventions": ["REST API"],
  "constraints": [],
  "out_of_scope": ["Social login"]
}
```'''

        question = InterviewQuestion(
            question="Which auth?",
            focus=InterviewFocus.ARCHITECTURE
        )
        answers = [InterviewAnswer(question=question, answer="JWT")]

        spec = wrapper.generate_feature_spec(
            user_goal="Add auth",
            interview_answers=answers,
            project_analysis=None
        )

        assert spec.feature_name == "user_auth"
        assert "Login" in spec.requirements
        assert "Use JWT" in spec.architecture_decisions

    def test_decompose_to_tasks(self, wrapper, mock_genai):
        """Test task decomposition."""
        mock_genai["part"].text = '''```json
{
  "tasks": [
    {
      "id": "task_001",
      "title": "Create User model",
      "goal": "Define User class",
      "files_to_modify": ["models/user.py"],
      "expected_logic": "Create User dataclass",
      "dependencies": [],
      "acceptance_criteria": ["Class exists"]
    },
    {
      "id": "task_002",
      "title": "Create login endpoint",
      "goal": "POST /login",
      "files_to_modify": ["routes/auth.py"],
      "expected_logic": "Validate credentials",
      "dependencies": ["task_001"],
      "acceptance_criteria": ["Endpoint works"]
    }
  ]
}
```'''

        spec = FeatureSpec(
            feature_name="user_auth",
            summary="Auth system",
            requirements=["Login"]
        )

        tasks = wrapper.decompose_to_tasks(spec)

        assert len(tasks) == 2
        assert tasks[0].id == "task_001"
        assert tasks[1].dependencies == ["task_001"]

    def test_run_plan_mode_complete_flow(self, wrapper, mock_scribe):
        """Test complete plan mode flow."""
        # Mock all internal methods
        with patch.object(wrapper, 'analyze_project') as mock_analyze, \
             patch.object(wrapper, 'generate_interview_questions') as mock_questions, \
             patch.object(wrapper, 'generate_feature_spec') as mock_spec, \
             patch.object(wrapper, 'decompose_to_tasks') as mock_tasks:

            mock_analyze.return_value = ProjectAnalysis(
                project_path="/test",
                languages=["Python"]
            )

            mock_questions.return_value = [
                InterviewQuestion(
                    question="Which database?",
                    focus=InterviewFocus.DATA_MODEL,
                    options=["PostgreSQL", "SQLite"]
                )
            ]

            mock_spec.return_value = FeatureSpec(
                feature_name="test_feature",
                summary="Test"
            )

            mock_tasks.return_value = [
                PlanTask(id="t1", title="Task 1", goal="Goal 1")
            ]

            # Callbacks
            def on_question(q):
                return "PostgreSQL"

            def on_spec_review(spec):
                return True

            def on_tasks_review(tasks):
                return True

            result = wrapper.run_plan_mode(
                user_goal="Add database",
                on_question=on_question,
                on_spec_review=on_spec_review,
                on_tasks_review=on_tasks_review
            )

            assert result.project_analysis is not None
            assert result.feature_spec.feature_name == "test_feature"
            assert len(result.tasks) == 1
            assert result.approved is True

    def test_run_plan_mode_spec_not_approved(self, wrapper, mock_scribe):
        """Test plan mode when spec is not approved."""
        with patch.object(wrapper, 'analyze_project') as mock_analyze, \
             patch.object(wrapper, 'generate_interview_questions') as mock_questions, \
             patch.object(wrapper, 'generate_feature_spec') as mock_spec:

            mock_analyze.return_value = ProjectAnalysis(project_path="/test")
            mock_questions.return_value = []
            mock_spec.return_value = FeatureSpec(feature_name="test", summary="Test")

            def on_spec_review(spec):
                return False  # Not approved

            result = wrapper.run_plan_mode(
                user_goal="Test",
                on_spec_review=on_spec_review
            )

            assert result.approved is False
            assert len(result.tasks) == 0

    def test_run_plan_mode_analysis_failure(self, wrapper, mock_scribe):
        """Test plan mode handles analysis failure gracefully."""
        with patch.object(wrapper, 'analyze_project') as mock_analyze, \
             patch.object(wrapper, 'generate_interview_questions') as mock_questions, \
             patch.object(wrapper, 'generate_feature_spec') as mock_spec, \
             patch.object(wrapper, 'decompose_to_tasks') as mock_tasks:

            mock_analyze.side_effect = Exception("Analysis failed")
            mock_questions.return_value = []
            mock_spec.return_value = FeatureSpec(feature_name="test", summary="Test")
            mock_tasks.return_value = []

            result = wrapper.run_plan_mode(user_goal="Test")

            # Should have fallback analysis
            assert result.project_analysis is not None
            assert result.project_analysis.project_path == wrapper.working_directory

    def test_context_manager(self, mock_scribe, mock_genai):
        """Test wrapper works as context manager."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
            with GeminiCLIWrapper() as wrapper:
                assert wrapper is not None
        # close() should be called automatically

    def test_log_callback(self, mock_scribe, mock_genai):
        """Test log callback is called."""
        logs = []

        def on_output(msg):
            logs.append(msg)

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
            wrapper = GeminiCLIWrapper(
                on_output=on_output,
                verbose=True
            )

            mock_genai["part"].text = '{"languages": [], "frameworks": []}'
            wrapper.analyze_project()

            wrapper.close()

        # Should have logged some messages
        assert len(logs) > 0

    def test_clarify_goal(self, wrapper, mock_genai):
        """Test goal clarification."""
        mock_genai["part"].text = '''```json
{
  "is_clear": true,
  "questions": [],
  "final_requirements": {
    "summary": "Create user login feature",
    "details": ["Login with email", "Password validation"]
  }
}
```'''

        result = wrapper.clarify_goal("Add login")

        assert result.get("is_clear") is True
        assert "final_requirements" in result

    def test_plan(self, wrapper, mock_genai):
        """Test task planning."""
        mock_genai["part"].text = '''```json
{
  "tasks": [
    {
      "id": "task_001",
      "title": "Create login endpoint",
      "goal": "POST /login",
      "files_to_modify": ["auth.py"],
      "expected_logic": "Validate and authenticate",
      "dependencies": [],
      "acceptance_criteria": ["Endpoint works"]
    }
  ]
}
```'''

        analysis = ProjectAnalysis(project_path="/test", languages=["Python"])
        plan = wrapper.plan("Add login", project_analysis=analysis)

        assert plan.goal == "Add login"

    def test_analyze_code(self, wrapper, mock_genai):
        """Test code analysis."""
        mock_genai["part"].text = '''```json
{
  "summary": "Simple Python function",
  "issues": [],
  "suggestions": ["Add type hints"],
  "complexity": "low"
}
```'''

        result = wrapper.analyze_code(
            code="def hello(): pass",
            file_path="hello.py"
        )

        assert "summary" in result

    def test_review_changes(self, wrapper, mock_genai):
        """Test change review."""
        mock_genai["part"].text = '''```json
{
  "approved": true,
  "summary": "Simple change",
  "issues": [],
  "suggestions": []
}
```'''

        result = wrapper.review_changes("+ new line\n- old line")

        assert result.get("approved") is True

    def test_reset_conversation(self, wrapper):
        """Test conversation reset."""
        # Add some history
        wrapper.conversation_history = [MagicMock(), MagicMock()]
        assert len(wrapper.conversation_history) == 2

        wrapper.reset_conversation()
        assert len(wrapper.conversation_history) == 0


class TestCommanderCLIConstitution:
    """Tests for COMMANDER_CLI_CONSTITUTION constant."""

    def test_constitution_exists(self):
        assert COMMANDER_CLI_CONSTITUTION is not None
        assert len(COMMANDER_CLI_CONSTITUTION) > 0

    def test_constitution_contains_key_principles(self):
        assert "최소주의" in COMMANDER_CLI_CONSTITUTION
        assert "명확성" in COMMANDER_CLI_CONSTITUTION
        assert "검증" in COMMANDER_CLI_CONSTITUTION

    def test_constitution_contains_json_format(self):
        assert "JSON" in COMMANDER_CLI_CONSTITUTION
        assert "type" in COMMANDER_CLI_CONSTITUTION

    def test_constitution_contains_role_info(self):
        assert "Commander" in COMMANDER_CLI_CONSTITUTION or "지휘관" in COMMANDER_CLI_CONSTITUTION
