"""Attack Planner - Uses Chain-of-Thought reasoning to plan attacks."""

from typing import Any
import logging
import json
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
logger=logging.getLogger(__name__)

ATTACK_PLANNING_PROMPT = """You are a security expert analyzing an API endpoint for vulnerabilities.
Endpoint: {method} {path}
Parameters: {parameters}
Request Body: {body}

Analyze this endpoint and suggest attack vectors. Consider:
1. Parameter types and names (id, user, query suggest different attacks)
2. HTTP method (POST/PUT more likely to have injection points)
3. Authentication requirements

Return a prioritized list of attacks to try. 
You must respond ONLY with a valid JSON array of objects. Do not include markdown formatting or explanations outside the JSON.
Each object must have the following keys:
- "type" (string, e.g., "sql_injection", "xss", "idor", "path_traversal")
- "name" (string, short name of the attack)
- "description" (string, what the attack does)
- "payload" (dict or string, the actual payload to send)
- "target_param" (string, the parameter or body field to target)
- "expected_status" (integer, expected HTTP status if vulnerable, e.g., 500)
- "priority" (string, "high", "medium", or "low")
"""

PAYLOAD_SUGGESTION_PROMPT = """You are an expert penetration tester.
Given the attack type '{attack_type}' and the context of the endpoint '{context}',
suggest a list of 5 specific, creative payloads to test for vulnerabilities.

Respond ONLY with a valid JSON array of strings representing the payloads. Do not include markdown blocks.
"""

REASONING_PROMPT = """You are an API security tester.
How would you test a field named '{field_name}' of type '{field_type}' for vulnerabilities?
Provide a concise, 1-2 sentence reasoning."""

class AttackPlanner:
    """Plan attacks based on API structure and context.
    
    Uses LLM reasoning to:
    - Understand endpoint semantics
    - Select appropriate attack profiles
    - Plan multi-step attack chains
    - Adapt based on responses
    """
    
    def __init__(self, endpoints: list[dict[str, Any]], toys_path: str = "toys/",llm_provider: str = "anthropic",model: str = "claude-3-5-sonnet-20241022",temperature: float = 0.7) -> None:
        """Initialize the attack planner.
        
        Args:
            endpoints: List of parsed API endpoints
            toys_path: Path to the attack profiles directory
        """
        self.endpoints = endpoints
        self.toys_path = toys_path
        self.attack_profiles: list[dict[str, Any]] = []

        self.llm_provider=llm_provider.lower()
        self.model=model
        self.temperature=temperature
        self.llm=self._init_llm()

    def _init_llm(self)->Any:
        if self.llm_provider=='anthropic':
            return ChatAnthropic(model="claude-3-5-sonnet-20241022",temperature=self.temperature)
        elif self.llm_provider=='openai':
            return ChatOpenAI(model="gpt-5",temperature=self.temperature)
        elif self.llm_provider == "ollama":
            return ChatOllama(model="llama3.1", temperature=self.temperature)
        else:
            logger.warning(f"Unknown LLM provider {self.llm_provider}. Falling back to Claude.")
            return ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=self.temperature)
    def load_attack_profiles(self) -> None:
        """Load all attack profiles from the toys directory."""
        # TODO: Load YAML files from toys/
        # raise NotImplementedError("Attack profile loading not yet implemented")
        pass
    
    def plan_attacks(self, endpoint: dict[str, Any]) -> list[dict[str, Any]]:
        """Plan attacks for a specific endpoint.
        
        Args:
            endpoint: Endpoint definition from OpenAPI parser
            
        Returns:
            List of planned attacks with payloads and expected behaviors
        """
        
        
        path = endpoint.get("path", "")
        method = endpoint.get("method", "GET")
        params = endpoint.get("parameters", [])
        body = endpoint.get("requestBody", {})
        cache_key = f"{method}:{path}:{str(params)}:{str(body)}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        prompt = ChatPromptTemplate.from_template(ATTACK_PLANNING_PROMPT)
        parser=JsonOutputParser()
        chain = prompt | self.llm | parser
        try:
            attacks = chain.invoke({
                "method": method,
                "path": path,
                "parameters": json.dumps(params),
                "body": json.dumps(body)
            })
            if isinstance(attacks, list):
                priority_map = {"high": 0, "medium": 1, "low": 2}
                attacks.sort(key=lambda x: priority_map.get(str(x.get("priority", "low")).lower(), 3))
                
                self._cache[cache_key] = attacks
                return attacks
        except Exception as e:
            logger.warning(f"LLM attack planning failed: {e}. Falling back to rule-based.")

        attacks = []
        if params or body:
            attacks.append({
                "type": "sql_injection",
                "name": "Basic SQLi Probe",
                "description": "Injects a basic SQL payload to test for errors",
                "payload": {"q": "' OR 1=1 --"}, # Simplified payload assumption
                "target_param": "q" if params else "body",
                "expected_status": 500
            })
        self._cache[cache_key] = attacks  
        return attacks
    def suggest_payloads(self, attack_type: str, context: dict[str, Any]) -> list[str]:
        """Generate context-specific payloads using LLM intelligence."""
        prompt = ChatPromptTemplate.from_template(PAYLOAD_SUGGESTION_PROMPT)
        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            payloads = chain.invoke({
                "attack_type": attack_type,
                "context": json.dumps(context)
            })
            if isinstance(payloads, list):
                return payloads
        except Exception as e:
            logger.warning(f"LLM payload suggestion failed: {e}")
            
        # fallback
        return ["' OR 1=1 --", "<script>alert(1)</script>", "../../../etc/passwd"]
    def reason_about_field(self, field_name: str, field_type: str) -> str:
        """Use LLM to reason about potential vulnerabilities for a field.
        
        Example:
            field_name="age", field_type="integer"
            Returns: "I'll test negative numbers, zero, extremely large values, and strings"
        
        Args:
            field_name: Name of the field
            field_type: Data type of the field
            
        Returns:
            Reasoning about what to test"""
        
        prompt = ChatPromptTemplate.from_template(REASONING_PROMPT)
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "field_name": field_name,
                "field_type": field_type
            })
            return response.content
        except Exception as e:
            logger.warning(f"LLM field reasoning failed: {e}")
            return f"Test '{field_name}' of type '{field_type}' with boundary values and injection strings."
