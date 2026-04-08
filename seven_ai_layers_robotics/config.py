import json
import threading
import tomllib
from pathlib import Path
import os
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = get_project_root()
# WORKSPACE_ROOT = PROJECT_ROOT / "workspace"
def _env(key: str, default: Any = None) -> Any:
    v = os.getenv(key)
    return default if v is None or v == "" else v


def _env_int(key: str, default: int) -> int:  
    v = _env(key, None)
    return int(v) if v is not None else default

class DatabaseSettings(BaseModel):  
    host: str = Field("127.0.0.1", description="DB host")
    port: int = Field(3306, description="DB port")
    user: str = Field("root", description="DB user")
    password: str = Field("", description="DB password")
    database: str = Field("", description="DB name")
    charset: str = Field("utf8mb4", description="DB charset")



class ReasoningDatabaseSettings(BaseModel): 
    """Configuration for Reasoning module input database"""
    host: str = Field("127.0.0.1", description="DB host")
    port: int = Field(3306, description="DB port")
    user: str = Field("root", description="DB user")
    password: str = Field("", description="DB password")
    database: str = Field("", description="DB name")
    charset: str = Field("utf8mb4", description="DB charset")
    table: str = Field("experiments_data_daily", description="DB table")


class ReasoningOutputDatabaseSettings(BaseModel):  
    """Configuration for Reasoning module output database"""
    host: str = Field("127.0.0.1", description="DB host")
    port: int = Field(3306, description="DB port")
    user: str = Field("root", description="DB user")
    password: str = Field("", description="DB password")
    database: str = Field("", description="DB name")
    charset: str = Field("utf8mb4", description="DB charset")
    table: str = Field("report_optimised", description="DB table")


class ReasoningLLMSettings(BaseModel):  #  NEW
    """Configuration for Reasoning module LLM"""
    base_url: str = Field("http://localhost:8000", description="Local LLM API URL")
    dashscope_api_key: str = Field("", description="DashScope API key")
    dashscope_model: str = Field("qwen-plus", description="DashScope model name")
    temperature: float = Field(0.7, description="Sampling temperature")
    timeout: int = Field(120, description="Request timeout in seconds")


class ReasoningGenerationSettings(BaseModel): 
    """Configuration for Reasoning module report generation"""
    total_runs: int = Field(15, description="Default number of reports to generate")
    max_workers: int = Field(10, description="Maximum concurrent workers")


class GeneratingDatabaseSettings(BaseModel):  
    """Configuration for Generating module input database"""
    host: str = Field("127.0.0.1", description="DB host")
    port: int = Field(3306, description="DB port")
    user: str = Field("root", description="DB user")
    password: str = Field("", description="DB password")
    database: str = Field("", description="DB name")
    charset: str = Field("utf8mb4", description="DB charset")


class GeneratingOutputDatabaseSettings(BaseModel): 
    """Configuration for Generating module output database"""
    host: str = Field("127.0.0.1", description="DB host")
    port: int = Field(3306, description="DB port")
    user: str = Field("root", description="DB user")
    password: str = Field("", description="DB password")
    database: str = Field("", description="DB name")
    charset: str = Field("utf8mb4", description="DB charset")


class GeneratingLLMSettings(BaseModel):  
    """Configuration for Generating module LLM"""
    base_url: str = Field("https://dashscope.aliyuncs.com/compatible-mode/v1", description="DashScope API base URL")
    dashscope_api_key: str = Field("", description="DashScope API key")
    dashscope_model: str = Field("qwen-plus", description="DashScope model name")
    deepseek_api_key: str = Field("", description="DeepSeek API key")
    deepseek_base_url: str = Field("https://api.deepseek.com/v1/chat/completions", description="DeepSeek base URL")
    deepseek_model: str = Field("deepseek-reasoner", description="DeepSeek model name")
    temperature: float = Field(0.7, description="Sampling temperature")
    timeout: int = Field(120, description="Request timeout in seconds")


class GeneratingGenerationSettings(BaseModel):  
    """Configuration for Generating module report generation"""
    total_runs: int = Field(15, description="Default number of reports to generate")
    max_workers: int = Field(10, description="Maximum concurrent workers")


class LearningDatabaseSettings(BaseModel):  
    """Configuration for Learning module database"""
    host: str = Field("127.0.0.1", description="DB host")
    port: int = Field(3306, description="DB port")
    user: str = Field("root", description="DB user")
    password: str = Field("", description="DB password")
    database: str = Field("exp_data", description="DB name")
    charset: str = Field("utf8mb4", description="DB charset")


class LearningLLMSettings(BaseModel):  
    """Configuration for Learning module LLM"""
    model: str = Field("qwen-plus", description="LLM model name")
    base_url: str = Field("https://dashscope.aliyuncs.com/compatible-mode/v1", description="DashScope API base URL")
    api_key: str = Field("", description="DashScope API key")
    max_tokens: int = Field(4096, description="Maximum tokens per request")
    temperature: float = Field(0.0, description="Sampling temperature")


class EvaluationLLMSettings(BaseModel): 
    """Configuration for Evaluation module LLM"""
    deepseek_api_key: str = Field("", description="DeepSeek API key")
    deepseek_base_url: str = Field("https://dashscope.aliyuncs.com/compatible-mode/v1", description="DeepSeek base URL")
    deepseek_model: str = Field("deepseek-r1", description="DeepSeek model")
    qwen_api_key: str = Field("", description="Qwen API key")
    qwen_base_url: str = Field("https://dashscope.aliyuncs.com/compatible-mode/v1", description="Qwen base URL")
    qwen_model: str = Field("qwen-max", description="Qwen model")
    gpt5_api_key: str = Field("", description="GPT-5 API key")
    gpt5_base_url: str = Field("https://api.llldan.org/v1/", description="GPT-5 base URL")
    gpt5_model: str = Field("gpt-5", description="GPT-5 model")
    default_llm_key: str = Field("qwen", description="Default LLM provider key")


class EvaluationPredictorSettings(BaseModel):  
    """Configuration for Evaluation module predictor"""
    base_model_dir: str = Field(
        "data/predictor_inputs",
        description="Base directory for predictor models"
    )

    def get_model_config(self, project_root: Path) -> dict:
        """Get model configuration with full paths"""
        base_dir = project_root / "seven_ai_layers_robotics" / "evaluation" / self.base_model_dir
        return {
            "ff": {
                "encoding": base_dir / "ff" / "encoding_mappings_20250612_FF.json",
                "col": base_dir / "ff" / "xgb_col_FF.pkl",
                "scaler": base_dir / "ff" / "xgb_scaler_FF.pkl",
                "model": base_dir / "ff" / "xgb_model_FF.pkl",
            },
            "jsc": {
                "encoding": base_dir / "jsc" / "encoding_mappings_20250612_Jsc.json",
                "col": base_dir / "jsc" / "xgb_col_Jsc.pkl",
                "scaler": base_dir / "jsc" / "xgb_scaler_Jsc.pkl",
                "model": base_dir / "jsc" / "xgb_model_Jsc.pkl",
            },
            "pce": {
                "encoding": base_dir / "pce" / "encoding_mappings_20250710.json",
                "col": base_dir / "pce" / "xgb_col_PCE.pkl",
                "scaler": base_dir / "pce" / "xgb_scaler_PCE.pkl",
                "model": base_dir / "pce" / "xgb_model_PCE.pkl",
            },
            "voc": {
                "encoding": base_dir / "voc" / "encoding_mappings_20250612_Voc.json",
                "col": base_dir / "voc" / "xgb_col_Voc.pkl",
                "scaler": base_dir / "voc" / "xgb_scaler_Voc.pkl",
                "model": base_dir / "voc" / "xgb_model_Voc.pkl",
            }
        }


class EvaluationSettings(BaseModel):  
    """Configuration for Evaluation module"""
    # Data file paths
    compound_mapping: str = Field(
        "data/compound_mapping.json",
        description="Path to compound mapping JSON"
    )
    materials_dict: str = Field(
        "data/materials_dict_2025_11_11.pickle",
        description="Path to materials dictionary pickle"
    )
    rubric_path: str = Field(
        "data/five_dimension_rubrics_new_zhao.json",
        description="Path to evaluation rubrics JSON"
    )

    # All indicators
    recipe_indicators: list = Field(
        default_factory=lambda: [
            "recipe_integrity",
            "formula_rationality",
            "parameter_rationality",
            "performance_rationality",
            "recipe_recommendation",
            "experimental_validation"
        ],
        description="All recipe evaluation indicators"
    )
    mechanism_indicators: list = Field(
        default_factory=lambda: [
            "domain_knowledge",
            "mechanism_integrity",
            "mechanism_interpretation",
            "mechanism_comprehensiveness",
            "mechanism_coherence"
        ],
        description="All mechanism evaluation indicators"
    )

    # Custom indicators
    recipe_custom: list = Field(
        default_factory=lambda: [
            "recipe_integrity",
            "formula_rationality",
            "parameter_rationality",
            "experimental_validation"
        ],
        description="Custom recipe indicators"
    )
    mechanism_custom: list = Field(
        default_factory=lambda: [
            "domain_knowledge",
            "mechanism_integrity",
            "mechanism_interpretation",
            "mechanism_comprehensiveness",
            "mechanism_coherence"
        ],
        description="Custom mechanism indicators"
    )

    # Indicator weights
    indicator_weight: dict = Field(
        default_factory=lambda: {
            "recipe_integrity": 0.05,
            "formula_rationality": 0.05,
            "parameter_rationality": 0.05,
            "performance_rationality": 0,
            "recipe_recommendation": 0,
            "experimental_validation": 0.35,
            "domain_knowledge": 0.1,
            "mechanism_integrity": 0.1,
            "mechanism_interpretation": 0.1,
            "mechanism_comprehensiveness": 0.1,
            "mechanism_coherence": 0.1
        },
        description="Weights for evaluation indicators"
    )

    # System prompt for scoring
    system_prompt: str = Field(
        default="""\nYou are an expert reviewer of perovskite-solar-cell research papers and a strict but fair grader.\n\nYour task:\n- Read a JSON rubric and a JSON object containing one model-generated report.\n- Assign integer scores and short comments for each rubric dimension.\n- Follow the rubric exactly and be slightly conservative.\n- Respond ONLY with a single valid JSON object, with no markdown and no extra text.\n""",
        description="System prompt for evaluation scoring"
    )


class LLMSettings(BaseModel):
    model: str = Field(..., description="Model name")
    base_url: str = Field(..., description="API base URL")
    api_key: str = Field(..., description="API key")
    max_tokens: int = Field(4096, description="Maximum number of tokens per request")
    max_input_tokens: Optional[int] = Field(
        None,
        description="Maximum input tokens to use across all requests (None for unlimited)",
    )
    temperature: float = Field(1.0, description="Sampling temperature")
    # api_type: str = Field(..., description="Azure, Openai, or Ollama")
    # api_version: str = Field(..., description="Azure Openai version if AzureOpenai")
    api_type: Optional[str] = Field(None, description="Azure/OpenAI/Ollama/AWS etc.")  
    api_version: Optional[str] = Field(None, description="Azure OpenAI api version") 


class ProxySettings(BaseModel):
    server: str = Field(None, description="Proxy server address")
    username: Optional[str] = Field(None, description="Proxy username")
    password: Optional[str] = Field(None, description="Proxy password")


class SearchSettings(BaseModel):
    engine: str = Field(default="Google", description="Search engine the llm to use")
    fallback_engines: List[str] = Field(
        default_factory=lambda: ["DuckDuckGo", "Baidu", "Bing"],
        description="Fallback search engines to try if the primary engine fails",
    )
    retry_delay: int = Field(
        default=60,
        description="Seconds to wait before retrying all engines again after they all fail",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of times to retry all engines when all fail",
    )
    lang: str = Field(
        default="en",
        description="Language code for search results (e.g., en, zh, fr)",
    )
    country: str = Field(
        default="us",
        description="Country code for search results (e.g., us, cn, uk)",
    )


class RunflowSettings(BaseModel):
    use_data_analysis_agent: bool = Field(
        default=False, description="Enable data analysis agent in run flow"
    )


class BrowserSettings(BaseModel):
    headless: bool = Field(False, description="Whether to run browser in headless mode")
    disable_security: bool = Field(
        True, description="Disable browser security features"
    )
    extra_chromium_args: List[str] = Field(
        default_factory=list, description="Extra arguments to pass to the browser"
    )
    chrome_instance_path: Optional[str] = Field(
        None, description="Path to a Chrome instance to use"
    )
    wss_url: Optional[str] = Field(
        None, description="Connect to a browser instance via WebSocket"
    )
    cdp_url: Optional[str] = Field(
        None, description="Connect to a browser instance via CDP"
    )
    proxy: Optional[ProxySettings] = Field(
        None, description="Proxy settings for the browser"
    )
    max_content_length: int = Field(
        2000, description="Maximum length for content retrieval operations"
    )


class SandboxSettings(BaseModel):
    """Configuration for the execution sandbox"""

    use_sandbox: bool = Field(False, description="Whether to use the sandbox")
    image: str = Field("python:3.12-slim", description="Base image")
    work_dir: str = Field("/workspace", description="Container working directory")
    memory_limit: str = Field("512m", description="Memory limit")
    cpu_limit: float = Field(1.0, description="CPU limit")
    timeout: int = Field(300, description="Default command timeout (seconds)")
    network_enabled: bool = Field(
        False, description="Whether network access is allowed"
    )


class DaytonaSettings(BaseModel):
    # daytona_api_key: str
    daytona_api_key: Optional[str] = Field(None, description="Daytona API key") 
    daytona_server_url: Optional[str] = Field(
        "https://app.daytona.io/api", description=""
    )
    daytona_target: Optional[str] = Field("us", description="enum ['eu', 'us']")
    sandbox_image_name: Optional[str] = Field("whitezxj/sandbox:0.1.0", description="")
    sandbox_entrypoint: Optional[str] = Field(
        "/usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf",
        description="",
    )
    # sandbox_id: Optional[str] = Field(
    #     None, description="ID of the daytona sandbox to use, if any"
    # )
    VNC_password: Optional[str] = Field(
        "123456", description="VNC password for the vnc service in sandbox"
    )


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server"""

    type: str = Field(..., description="Server connection type (sse or stdio)")
    url: Optional[str] = Field(None, description="Server URL for SSE connections")
    command: Optional[str] = Field(None, description="Command for stdio connections")
    args: List[str] = Field(
        default_factory=list, description="Arguments for stdio command"
    )


class MCPSettings(BaseModel):
    """Configuration for MCP (Model Context Protocol)"""

    server_reference: str = Field(
        "app.mcp.server", description="Module reference for the MCP server"
    )
    servers: Dict[str, MCPServerConfig] = Field(
        default_factory=dict, description="MCP server configurations"
    )

    @classmethod
    def load_server_config(cls) -> Dict[str, MCPServerConfig]:
        """Load MCP server configuration from JSON file"""
        config_path = PROJECT_ROOT / "config" / "mcp.json"

        try:
            config_file = config_path if config_path.exists() else None
            if not config_file:
                return {}

            with config_file.open() as f:
                data = json.load(f)
                servers = {}

                for server_id, server_config in data.get("mcpServers", {}).items():
                    servers[server_id] = MCPServerConfig(
                        type=server_config["type"],
                        url=server_config.get("url"),
                        command=server_config.get("command"),
                        args=server_config.get("args", []),
                    )
                return servers
        except Exception as e:
            raise ValueError(f"Failed to load MCP server config: {e}")


class RecipeQALLMSettings(BaseModel):  # ✅ NEW
    """Configuration for RecipeQA module LLM"""
    base_url: str = Field("https://dashscope.aliyuncs.com/compatible-mode/v1", description="DashScope API base URL")
    dashscope_api_key: str = Field("", description="DashScope API key")
    dashscope_model: str = Field("qwen-plus", description="DashScope model name")
    temperature: float = Field(0.4, description="Sampling temperature")
    timeout: int = Field(60, description="Request timeout in seconds")


class DeepSeekSettings(BaseModel):  # ✅ NEW
    """Configuration for DeepSeek LLM"""
    api_key: str = Field("", description="DeepSeek API key")
    base_url: str = Field("https://api.deepseek.com/v1/chat/completions", description="DeepSeek API base URL")
    model: str = Field("deepseek-reasoner", description="DeepSeek model name")
    temperature: float = Field(0.3, description="Sampling temperature")
    timeout: int = Field(120, description="Request timeout in seconds")


class AppConfig(BaseModel):
    llm: Dict[str, LLMSettings]
    sandbox: Optional[SandboxSettings] = Field(
        None, description="Sandbox configuration"
    )
    browser_config: Optional[BrowserSettings] = Field(
        None, description="Browser configuration"
    )
    search_config: Optional[SearchSettings] = Field(
        None, description="Search configuration"
    )
    mcp_config: Optional[MCPSettings] = Field(None, description="MCP configuration")
    run_flow_config: Optional[RunflowSettings] = Field(
        None, description="Run flow configuration"
    )
    daytona_config: Optional[DaytonaSettings] = Field(
        None, description="Daytona configuration"
    )
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)  
    # services: EvaluatorSettings = Field(default_factory=EvaluatorSettings)    
    reasoning_database: Optional[ReasoningDatabaseSettings] = Field(None, description="Reasoning input database")  
    reasoning_output_database: Optional[ReasoningOutputDatabaseSettings] = Field(None, description="Reasoning output database") 
    reasoning_llm: Optional[ReasoningLLMSettings] = Field(None, description="Reasoning LLM")  
    reasoning_generation: Optional[ReasoningGenerationSettings] = Field(None, description="Reasoning generation")  
    generating_database: Optional[GeneratingDatabaseSettings] = Field(None, description="Generating input database")  
    generating_output_database: Optional[GeneratingOutputDatabaseSettings] = Field(None, description="Generating output database")  
    generating_llm: Optional[GeneratingLLMSettings] = Field(None, description="Generating LLM")  
    generating_generation: Optional[GeneratingGenerationSettings] = Field(None, description="Generating generation") 
    learning_database: Optional[LearningDatabaseSettings] = Field(None, description="Learning database")  
    learning_llm: Optional[LearningLLMSettings] = Field(None, description="Learning LLM")  
    evaluation_llm: Optional[EvaluationLLMSettings] = Field(None, description="Evaluation LLM")  
    evaluation_predictor: Optional[EvaluationPredictorSettings] = Field(None, description="Evaluation Predictor")  
    evaluation: Optional[EvaluationSettings] = Field(None, description="Evaluation Module Settings")  
    recipeqa_llm: Optional[RecipeQALLMSettings] = Field(None, description="RecipeQA LLM")  
    deepseek: Optional[DeepSeekSettings] = Field(None, description="DeepSeek LLM")  
    class Config:
        arbitrary_types_allowed = True


class Config:
    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._config = None
                    self._load_initial_config()
                    self._initialized = True

    @staticmethod
    def _get_config_path() -> Path:
        root = PROJECT_ROOT
        config_path = root  / "config.toml"
        # print(f"Config path: {config_path}")
        if config_path.exists():
            return config_path
        example_path = root  / "config.example.toml"
        if example_path.exists():
            return example_path
        raise FileNotFoundError("No configuration file found in config directory")

    def _load_config(self) -> dict:
        config_path = self._get_config_path()
        with config_path.open("rb") as f:
            return tomllib.load(f)

    def _load_initial_config(self):
        raw_config = self._load_config()

        db_cfg = raw_config.get("database", {}) or {}
        svc_cfg = raw_config.get("services", {}) or {}

        database_settings = DatabaseSettings(
            host=_env("DB_HOST", db_cfg.get("host", "127.0.0.1")),
            port=_env_int("DB_PORT", int(db_cfg.get("port", 3306))),
            user=_env("DB_USER", db_cfg.get("user", "root")),
            password=_env("DB_PASSWORD", db_cfg.get("password", "")),
            database=_env("DB_NAME", db_cfg.get("database", "")),
            charset=_env("DB_CHARSET", db_cfg.get("charset", "utf8mb4")),
        )

     
        # Load Reasoning module configuration
        reasoning_db_cfg = raw_config.get("reasoning_database", {}) or {}
        reasoning_output_db_cfg = raw_config.get("reasoning_output_database", {}) or {}
        reasoning_llm_cfg = raw_config.get("reasoning_llm", {}) or {}
        reasoning_gen_cfg = raw_config.get("reasoning_generation", {}) or {}

        reasoning_database_settings = ReasoningDatabaseSettings(
            host=reasoning_db_cfg.get("host", "127.0.0.1"),
            port=reasoning_db_cfg.get("port", 3306),
            user=reasoning_db_cfg.get("user", "root"),
            password=reasoning_db_cfg.get("password", ""),
            database=reasoning_db_cfg.get("database", ""),
            charset=reasoning_db_cfg.get("charset", "utf8mb4"),
            table=reasoning_db_cfg.get("table", "experiments_data_daily"),
        )

        reasoning_output_database_settings = ReasoningOutputDatabaseSettings(
            host=reasoning_output_db_cfg.get("host", reasoning_db_cfg.get("host", "127.0.0.1")),
            port=reasoning_output_db_cfg.get("port", reasoning_db_cfg.get("port", 3306)),
            user=reasoning_output_db_cfg.get("user", reasoning_db_cfg.get("user", "root")),
            password=reasoning_output_db_cfg.get("password", reasoning_db_cfg.get("password", "")),
            database=reasoning_output_db_cfg.get("database", reasoning_db_cfg.get("database", "")),
            charset=reasoning_output_db_cfg.get("charset", "utf8mb4"),
            table=reasoning_output_db_cfg.get("table", "report_optimised"),
        )

        reasoning_llm_settings = ReasoningLLMSettings(
            base_url=reasoning_llm_cfg.get("base_url", "http://localhost:8000"),
            dashscope_api_key=reasoning_llm_cfg.get("dashscope_api_key", ""),
            dashscope_model=reasoning_llm_cfg.get("dashscope_model", "qwen-plus"),
            temperature=reasoning_llm_cfg.get("temperature", 0.7),
            timeout=reasoning_llm_cfg.get("timeout", 120),
        )

        reasoning_generation_settings = ReasoningGenerationSettings(
            total_runs=reasoning_gen_cfg.get("total_runs", 15),
            max_workers=reasoning_gen_cfg.get("max_workers", 10),
        )

        # Load Generating module configuration
        generating_db_cfg = raw_config.get("generating_database", {}) or {}
        generating_output_db_cfg = raw_config.get("generating_output_database", {}) or {}
        generating_llm_cfg = raw_config.get("generating_llm", {}) or {}
        generating_gen_cfg = raw_config.get("generating_generation", {}) or {}

        generating_database_settings = GeneratingDatabaseSettings(
            host=generating_db_cfg.get("host", "127.0.0.1"),
            port=generating_db_cfg.get("port", 3306),
            user=generating_db_cfg.get("user", "root"),
            password=generating_db_cfg.get("password", ""),
            database=generating_db_cfg.get("database", ""),
            charset=generating_db_cfg.get("charset", "utf8mb4"),
        )

        generating_output_database_settings = GeneratingOutputDatabaseSettings(
            host=generating_output_db_cfg.get("host", generating_db_cfg.get("host", "127.0.0.1")),
            port=generating_output_db_cfg.get("port", generating_db_cfg.get("port", 3306)),
            user=generating_output_db_cfg.get("user", generating_db_cfg.get("user", "root")),
            password=generating_output_db_cfg.get("password", generating_db_cfg.get("password", "")),
            database=generating_output_db_cfg.get("database", generating_db_cfg.get("database", "")),
            charset=generating_output_db_cfg.get("charset", "utf8mb4"),
        )

        generating_llm_settings = GeneratingLLMSettings(
            base_url=generating_llm_cfg.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            dashscope_api_key=generating_llm_cfg.get("dashscope_api_key", ""),
            dashscope_model=generating_llm_cfg.get("dashscope_model", "qwen-plus"),
            deepseek_api_key=generating_llm_cfg.get("deepseek_api_key", ""),
            deepseek_base_url=generating_llm_cfg.get("deepseek_base_url", "https://api.deepseek.com/v1/chat/completions"),
            deepseek_model=generating_llm_cfg.get("deepseek_model", "deepseek-reasoner"),
            temperature=generating_llm_cfg.get("temperature", 0.7),
            timeout=generating_llm_cfg.get("timeout", 120),
        )

        # Load Learning module configuration
        learning_db_cfg = raw_config.get("learning_database", {}) or {}
        learning_llm_cfg = raw_config.get("learning_llm", {}) or {}

        learning_database_settings = LearningDatabaseSettings(
            host=learning_db_cfg.get("host", "127.0.0.1"),
            port=learning_db_cfg.get("port", 3306),
            user=learning_db_cfg.get("user", "root"),
            password=learning_db_cfg.get("password", ""),
            database=learning_db_cfg.get("database", ""),
            charset=learning_db_cfg.get("charset", "utf8mb4"),
        )

        learning_llm_settings = LearningLLMSettings(
            model=learning_llm_cfg.get("model", "qwen-plus"),
            base_url=learning_llm_cfg.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            api_key=learning_llm_cfg.get("api_key", ""),
            max_tokens=learning_llm_cfg.get("max_tokens", 4096),
            temperature=learning_llm_cfg.get("temperature", 0.0),
        )

        # Load Evaluation module LLM configuration
        evaluation_llm_cfg = raw_config.get("evaluation_llm", {}) or {}
        evaluation_predictor_cfg = raw_config.get("evaluation_predictor", {}) or {}
        evaluation_cfg = raw_config.get("evaluation", {}) or {}
        
        # Load RecipeQA module LLM configuration
        recipeqa_llm_cfg = raw_config.get("recipeqa_llm", {}) or {}
        # Load DeepSeek configuration
        deepseek_cfg = raw_config.get("deepseek", {}) or {}

        evaluation_llm_settings = EvaluationLLMSettings(
            deepseek_api_key=evaluation_llm_cfg.get("deepseek_api_key", ""),
            deepseek_base_url=evaluation_llm_cfg.get("deepseek_base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            deepseek_model=evaluation_llm_cfg.get("deepseek_model", "deepseek-r1"),
            qwen_api_key=evaluation_llm_cfg.get("qwen_api_key", ""),
            qwen_base_url=evaluation_llm_cfg.get("qwen_base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            qwen_model=evaluation_llm_cfg.get("qwen_model", "qwen-max"),
            gpt5_api_key=evaluation_llm_cfg.get("gpt5_api_key", ""),
            gpt5_base_url=evaluation_llm_cfg.get("gpt5_base_url", "https://api.llldan.org/v1/"),
            gpt5_model=evaluation_llm_cfg.get("gpt5_model", "gpt-5"),
            default_llm_key=evaluation_llm_cfg.get("default_llm_key", "qwen"),
        )

        evaluation_predictor_settings = EvaluationPredictorSettings(
            base_model_dir=evaluation_predictor_cfg.get("base_model_dir", "data/predictor_inputs"),
        )

        evaluation_settings = EvaluationSettings(
            compound_mapping=evaluation_cfg.get("compound_mapping", "data/compound_mapping.json"),
            materials_dict=evaluation_cfg.get("materials_dict", "data/materials_dict_2025_11_11.pickle"),
            rubric_path=evaluation_cfg.get("rubric_path", "data/five_dimension_rubrics_new_zhao.json"),
            recipe_indicators=evaluation_cfg.get("recipe_indicators", [
                "recipe_integrity",
                "formula_rationality",
                "parameter_rationality",
                "performance_rationality",
                "recipe_recommendation",
                "experimental_validation"
            ]),
            mechanism_indicators=evaluation_cfg.get("mechanism_indicators", [
                "domain_knowledge",
                "mechanism_integrity",
                "mechanism_interpretation",
                "mechanism_comprehensiveness",
                "mechanism_coherence"
            ]),
            recipe_custom=evaluation_cfg.get("recipe_custom", [
                "recipe_integrity",
                "formula_rationality",
                "parameter_rationality",
                "experimental_validation"
            ]),
            mechanism_custom=evaluation_cfg.get("mechanism_custom", [
                "domain_knowledge",
                "mechanism_integrity",
                "mechanism_interpretation",
                "mechanism_comprehensiveness",
                "mechanism_coherence"
            ]),
            indicator_weight=evaluation_cfg.get("indicator_weight", {
                "recipe_integrity": 0.05,
                "formula_rationality": 0.05,
                "parameter_rationality": 0.05,
                "performance_rationality": 0,
                "recipe_recommendation": 0,
                "experimental_validation": 0.35,
                "domain_knowledge": 0.1,
                "mechanism_integrity": 0.1,
                "mechanism_interpretation": 0.1,
                "mechanism_comprehensiveness": 0.1,
                "mechanism_coherence": 0.1
            }),
            system_prompt=evaluation_cfg.get("system_prompt", """\nYou are an expert reviewer of perovskite-solar-cell research papers and a strict but fair grader.\n\nYour task:\n- Read a JSON rubric and a JSON object containing one model-generated report.\n- Assign integer scores and short comments for each rubric dimension.\n- Follow the rubric exactly and be slightly conservative.\n- Respond ONLY with a single valid JSON object, with no markdown and no extra text.\n"""),
        )

        recipeqa_llm_settings = RecipeQALLMSettings(
            base_url=recipeqa_llm_cfg.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            dashscope_api_key=recipeqa_llm_cfg.get("dashscope_api_key", ""),
            dashscope_model=recipeqa_llm_cfg.get("dashscope_model", "qwen-plus"),
            temperature=recipeqa_llm_cfg.get("temperature", 0.4),
            timeout=recipeqa_llm_cfg.get("timeout", 60),
        )

        deepseek_settings = DeepSeekSettings(
            api_key=deepseek_cfg.get("api_key", ""),
            base_url=deepseek_cfg.get("base_url", "https://api.deepseek.com/v1/chat/completions"),
            model=deepseek_cfg.get("model", "deepseek-reasoner"),
            temperature=deepseek_cfg.get("temperature", 0.3),
            timeout=deepseek_cfg.get("timeout", 120),
        )

        generating_generation_settings = GeneratingGenerationSettings(
            total_runs=generating_gen_cfg.get("total_runs", 15),
            max_workers=generating_gen_cfg.get("max_workers", 10),
        )



        base_llm = raw_config.get("llm", {})
        llm_overrides = {
            k: v for k, v in raw_config.get("llm", {}).items() if isinstance(v, dict)
        }

        default_settings = {
            "model": base_llm.get("model"),
            "base_url": base_llm.get("base_url"),
            "api_key": base_llm.get("api_key"),
            "max_tokens": base_llm.get("max_tokens", 4096),
            "max_input_tokens": base_llm.get("max_input_tokens"),
            "temperature": base_llm.get("temperature", 1.0),
            "api_type": base_llm.get("api_type", ""),
            "api_version": base_llm.get("api_version", ""),
        }

        # handle browser config.
        browser_config = raw_config.get("browser", {})
        browser_settings = None

        if browser_config:
            # handle proxy settings.
            proxy_config = browser_config.get("proxy", {})
            proxy_settings = None

            if proxy_config and proxy_config.get("server"):
                proxy_settings = ProxySettings(
                    **{
                        k: v
                        for k, v in proxy_config.items()
                        if k in ["server", "username", "password"] and v
                    }
                )

            # filter valid browser config parameters.
            valid_browser_params = {
                k: v
                for k, v in browser_config.items()
                if k in BrowserSettings.__annotations__ and v is not None
            }

            # if there is proxy settings, add it to the parameters.
            if proxy_settings:
                valid_browser_params["proxy"] = proxy_settings

            # only create BrowserSettings when there are valid parameters.
            if valid_browser_params:
                browser_settings = BrowserSettings(**valid_browser_params)

        search_config = raw_config.get("search", {})
        search_settings = None
        if search_config:
            search_settings = SearchSettings(**search_config)
        sandbox_config = raw_config.get("sandbox", {})
        if sandbox_config:
            sandbox_settings = SandboxSettings(**sandbox_config)
        else:
            sandbox_settings = SandboxSettings()
        daytona_config = raw_config.get("daytona", {})
        if daytona_config:
            daytona_settings = DaytonaSettings(**daytona_config)
        else:
            daytona_settings = DaytonaSettings()

        mcp_config = raw_config.get("mcp", {})
        mcp_settings = None
        if mcp_config:
            # Load server configurations from JSON
            mcp_config["servers"] = MCPSettings.load_server_config()
            mcp_settings = MCPSettings(**mcp_config)
        else:
            mcp_settings = MCPSettings(servers=MCPSettings.load_server_config())

        run_flow_config = raw_config.get("runflow")
        if run_flow_config:
            run_flow_settings = RunflowSettings(**run_flow_config)
        else:
            run_flow_settings = RunflowSettings()
        config_dict = {
            "database": database_settings,  
            # "services": services_settings, 
            "reasoning_database": reasoning_database_settings, 
            "reasoning_output_database": reasoning_output_database_settings,  
            "reasoning_llm": reasoning_llm_settings, 
            "reasoning_generation": reasoning_generation_settings,  
            "generating_database": generating_database_settings, 
            "generating_output_database": generating_output_database_settings, 
            "generating_llm": generating_llm_settings,  
            "generating_generation": generating_generation_settings,  
            "learning_database": learning_database_settings,  
            "learning_llm": learning_llm_settings,  
            "evaluation_llm": evaluation_llm_settings,  
            "evaluation_predictor": evaluation_predictor_settings, 
            "evaluation": evaluation_settings,  
            "recipeqa_llm": recipeqa_llm_settings,  
            "deepseek": deepseek_settings,  
            "llm": {
                "default": default_settings,
                **{
                    name: {**default_settings, **override_config}
                    for name, override_config in llm_overrides.items()
                },
            },
            "sandbox": sandbox_settings,
            "browser_config": browser_settings,
            "search_config": search_settings,
            "mcp_config": mcp_settings,
            "run_flow_config": run_flow_settings,
            "daytona_config": daytona_settings,
        }

        self._config = AppConfig(**config_dict)

    @property
    def llm(self) -> Dict[str, LLMSettings]:
        return self._config.llm

    @property
    def sandbox(self) -> SandboxSettings:
        return self._config.sandbox

    @property
    def daytona(self) -> DaytonaSettings:
        return self._config.daytona_config

    @property
    def browser_config(self) -> Optional[BrowserSettings]:
        return self._config.browser_config

    @property
    def search_config(self) -> Optional[SearchSettings]:
        return self._config.search_config

    @property
    def mcp_config(self) -> MCPSettings:
        """Get the MCP configuration"""
        return self._config.mcp_config

    @property
    def run_flow_config(self) -> RunflowSettings:
        """Get the Run Flow configuration"""
        return self._config.run_flow_config

    # @property
    # def workspace_root(self) -> Path:
    #     """Get the workspace root directory"""
    #     return WORKSPACE_ROOT
    @property
    def database(self) -> DatabaseSettings:  
        return self._config.database

    # @property
    # def services(self) -> EvaluatorSettings:  
    #     return self._config.services

    @property
    def reasoning_database(self) -> ReasoningDatabaseSettings: 
        return self._config.reasoning_database

    @property
    def reasoning_output_database(self) -> ReasoningOutputDatabaseSettings:  
        return self._config.reasoning_output_database

    @property
    def reasoning_llm(self) -> ReasoningLLMSettings: 
        return self._config.reasoning_llm

    @property
    def reasoning_generation(self) -> ReasoningGenerationSettings:  
        return self._config.reasoning_generation

    @property
    def generating_database(self) -> GeneratingDatabaseSettings:  
        return self._config.generating_database

    @property
    def generating_output_database(self) -> GeneratingOutputDatabaseSettings: 
        return self._config.generating_output_database

    @property
    def generating_llm(self) -> GeneratingLLMSettings:  
        return self._config.generating_llm

    @property
    def generating_generation(self) -> GeneratingGenerationSettings: 
        return self._config.generating_generation

    @property
    def learning_database(self) -> LearningDatabaseSettings: 
        return self._config.learning_database

    @property
    def learning_llm(self) -> LearningLLMSettings:  
        return self._config.learning_llm

    @property
    def evaluation_llm(self) -> EvaluationLLMSettings: 
        return self._config.evaluation_llm

    @property
    def evaluation_predictor(self) -> EvaluationPredictorSettings:  
        return self._config.evaluation_predictor

    @property
    def evaluation(self) -> EvaluationSettings:  
        return self._config.evaluation

    @property
    def recipeqa_llm(self) -> RecipeQALLMSettings:  
        return self._config.recipeqa_llm

    @property
    def deepseek(self) -> DeepSeekSettings:  
        return self._config.deepseek

    def get_evaluation_data_path(self, relative_path: str) -> Path:
        """Get the full path for evaluation data files

        Args:
            relative_path: Relative path from evaluation module root (app/tool/RLM/Evaluation)

        Returns:
            Full path to the file
        """
        eval_module_root = PROJECT_ROOT / "seven_ai_layers_robotics" / "evaluation" 
        return eval_module_root / relative_path
    @property
    def root_path(self) -> Path:
        """Get the root path of the application"""
        return PROJECT_ROOT


config = Config()
