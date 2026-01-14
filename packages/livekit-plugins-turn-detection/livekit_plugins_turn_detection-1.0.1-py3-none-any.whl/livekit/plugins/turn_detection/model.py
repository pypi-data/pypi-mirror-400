import asyncio
import json
import os
import string
import time

import numpy as np
import onnxruntime as ort
from livekit.agents import ChatContext, ChatMessage, llm
from livekit.agents.inference_runner import _InferenceRunner
from livekit.agents.ipc.inference_executor import InferenceExecutor
from livekit.agents.job import get_job_context
from transformers import DebertaV2Tokenizer

from .constants import LANGUAGE_CODE, ONNX_FILENAME
from .log import logger


class _TurnDetectionRunner(_InferenceRunner):
    """Inference runner for Vietnamese turn detection model."""

    INFERENCE_METHOD = "turn_detection"

    def initialize(self) -> None:
        """Load Vietnamese model."""

        logger.info("Loading Vietnamese turn detection model")

        model_dir = os.path.join(os.path.dirname(__file__), "onnx_model")
        self._tokenizer = DebertaV2Tokenizer.from_pretrained(model_dir)
        self._max_length = 256

        model_path = os.path.join(model_dir, ONNX_FILENAME)
        self._session = ort.InferenceSession(
            model_path, providers=["CPUExecutionProvider"]
        )

        logger.info(
            "Vietnamese model loaded",
            extra={
                "language": LANGUAGE_CODE,
                "model_dir": model_dir,
                "model_path": model_path,
                "max_length": self._max_length,
            }
        )

    def run(self, data: bytes) -> bytes | None:
        """Execute inference on Vietnamese text."""
        try:
            data_json = json.loads(data)
            sentence = data_json["sentence"]

            if not sentence:
                return json.dumps({"probability": 0.0}).encode()

            # Tokenize matching inference_onnx.py
            inputs = self._tokenizer(
                sentence,
                max_length=self._max_length,
                padding="max_length",
                truncation=True,
                return_tensors="np",
            )

            input_dict = {
                "input_ids": inputs["input_ids"],
                "attention_mask": inputs["attention_mask"],
            }

            # Run inference
            outputs = self._session.run(None, input_dict)
            logits = outputs[0][0]

            # Apply softmax
            probabilities = self._softmax(logits)
            eou_probability = round(float(probabilities[1]), 3)

            logger.debug(
                "Turn detection completed",
                extra={
                    "probability": eou_probability,
                    "sentence_length": len(sentence),
                    "sentence": sentence,
                },
            )

            return json.dumps({"probability": eou_probability}).encode()

        except Exception as e:
            logger.error(f"Error during Vietnamese turn detection: {e}")
            return json.dumps({"probability": 0.0, "error": str(e)}).encode()

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        """Compute softmax values."""
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum()


_InferenceRunner.register_runner(_TurnDetectionRunner)


class TurnDetectionModel:
    """
    Turn Detection model.
    """

    def __init__(
        self,
        *,
        threshold: float = 0.5,
        inference_executor: InferenceExecutor | None = None,
        **kwargs
    ) -> None:
        """
        Initialize Turn Detection model.

        Args:
            threshold: Detection threshold (0.0-1.0). Defaults to 0.7.
            inference_executor: Optional custom inference executor.
            **kwargs: Ignored.
        """
        self._threshold = threshold
        self._executor = inference_executor or get_job_context().inference_executor

    @property
    def threshold(self) -> float:
        """Get the current detection threshold."""
        return self._threshold

    @property
    def provider(self) -> str:
        return "ggroup"

    async def supports_language(self, language: str) -> bool:
        """
        Check if the model supports the given language.

        Args:
            language: Language code to check (e.g., 'en', 'fr', 'es')

        Returns:
            bool: True if this model is configured for the given language
        """
        return language.lower() == LANGUAGE_CODE

    @property
    def language(self) -> str:
        """Get language code."""
        return LANGUAGE_CODE

    @property
    def model(self) -> str:
        return "turn_detection"

    def _inference_method(self) -> str:
        """Get inference method name."""
        return _TurnDetectionRunner.INFERENCE_METHOD

    async def unlikely_threshold(self, language: str | None) -> float | None:
        """
        Get the threshold for language.
        """
        return self._threshold

    def _get_text_content(self, message: ChatMessage) -> str:
        """Helper to safely extract text content from a message."""
        if hasattr(message, "text_content"):
            return message.text_content or ""
        
        content = message.content
        if isinstance(content, list):
            return " ".join([c.text if hasattr(c, "text") else str(c) for c in content])
        return str(content)

    def _clean_text(self, text: str) -> str:
        """Lowercase and remove punctuation."""
        return text.lower().translate(str.maketrans("", "", string.punctuation)).strip()

    def _get_last_user_message(self, chat_ctx: ChatContext) -> str:
        """
        Extract the last user message and preceding assistant context.
        Formats as: "assistant_context [SEP] user_message"
        """
        messages = chat_ctx.items
        user_message = None
        assistant_message = None
        user_idx = -1

        # Find last user message
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].role == "user":
                user_message = messages[i]
                user_idx = i
                break
        
        if not user_message:
            return ""

        # Find preceding assistant message
        if user_idx > 0:
            for i in range(user_idx - 1, -1, -1):
                if messages[i].role == "assistant":
                    assistant_message = messages[i]
                    break

        # Process user text
        user_text = self._clean_text(self._get_text_content(user_message))
        if not user_text:
            return ""

        # Process assistant text if exists
        result = user_text
        if assistant_message:
            assistant_text = self._clean_text(self._get_text_content(assistant_message))
            if assistant_text:
                result = f"{assistant_text} [SEP] {user_text}"

        return result

    async def predict_end_of_turn(
        self,
        chat_ctx: llm.ChatContext,
        *,
        timeout: float | None = 10.0,
    ) -> float:
        """
        Predict the probability of end-of-turn for the given chat context.

        This method extracts the last user message and runs inference to determine
        if the user has finished their turn.

        Args:
            chat_ctx: The chat context to analyze
            timeout: Maximum time to wait for inference (seconds). Defaults to 3.0.

        Returns:
            float: Probability score between 0.0 and 1.0, where higher values
                   indicate higher confidence that the turn has ended.

        Raises:
            asyncio.TimeoutError: If inference takes longer than timeout
            RuntimeError: If inference execution fails

        Example:
            ```python
            probability = await model.predict_end_of_turn(chat_ctx)
            if probability >= model.threshold:
                print("End of turn detected!")
            ```
        """
        start_time = time.time()

        try:
            # Extract the last user message
            sentence = self._get_last_user_message(chat_ctx)

            if not sentence:
                logger.debug("No user message found in chat context")
                return 0.0

            json_data = json.dumps({"sentence": sentence}).encode()

            result = await asyncio.wait_for(
                self._executor.do_inference(self._inference_method(), json_data),
                timeout=timeout,
            )

            result_json = json.loads(result.decode())
            probability = result_json.get("probability", 0.0)
            probability = round(probability, 3)

            duration = time.time() - start_time
            logger.debug(
                f"Predict EOT Finished: {probability >= self.threshold}",
                extra={
                    "probability": probability,
                    "threshold": self.threshold,
                    "sentence": sentence,
                    "duration": duration
                }
            )
            return probability

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            logger.error(
                "Turn detection inference timeout",
                extra={"duration": duration, "timeout": timeout},
            )
            raise

        except Exception as e:
            duration = time.time() - start_time
            logger.exception(
                f"Error during turn detection: {e}",
                extra={"duration": duration, "error": str(e)},
            )
            return 0.0