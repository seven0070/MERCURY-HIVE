from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.schemas.gateway import GatewayRequest, GatewayResponse
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ModelGateway(ABC):
    @abstractmethod
    def generate_response(self, request: GatewayRequest) -> GatewayResponse:
        pass

class OpenAIGateway(ModelGateway):
    def generate_response(self, request: GatewayRequest) -> GatewayResponse:
        # In a real implementation this would use openai library
        # For now, if we don't have a key, we fall back or simulate
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            logger.warning("No OPENAI_API_KEY found, using simulation mode.")
            return self._simulate_response(request)

        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        api_messages = [{"role": "system", "content": request.system_prompt}]
        api_messages.extend(request.messages)

        try:
            response = client.chat.completions.create(
                model=request.model if request.model != "default" else "gpt-4o-mini",
                messages=api_messages,
                temperature=request.temperature
            )

            return GatewayResponse(
                content=response.choices[0].message.content,
                model_used=response.model,
                usage=dict(response.usage) if response.usage else {}
            )
        except Exception as e:
            logger.error(f"OpenAI API Error: {str(e)}")
            raise

    def _simulate_response(self, request: GatewayRequest) -> GatewayResponse:
        last_message = request.messages[-1]["content"] if request.messages else ""
        return GatewayResponse(
            content=f"[SIMULATED LLM RESPONSE] Processed: {last_message}",
            model_used="simulated-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )

class StubModelGateway(ModelGateway):
    def generate_response(self, request: GatewayRequest) -> GatewayResponse:
        last_message = request.messages[-1]["content"] if request.messages else ""
        return GatewayResponse(
            content=f"[STUB LLM RESPONSE] Processed: {last_message}",
            model_used="stub",
            usage={}
        )

# Factory to get gateway based on config
def get_gateway() -> ModelGateway:
    # We can control this via settings in the future
    if hasattr(settings, 'USE_STUB_GATEWAY') and settings.USE_STUB_GATEWAY:
        return StubModelGateway()
    return OpenAIGateway()

gateway = get_gateway()
