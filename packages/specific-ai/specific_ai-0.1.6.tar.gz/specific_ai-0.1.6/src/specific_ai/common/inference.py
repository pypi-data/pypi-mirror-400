from typing import Any, Dict, Tuple, List
from specific_ai.common.lm_response_types import AnyLMResponse, ClassificationResponse, EntityRecognitionResponse
from specific_ai.common.task_type import TaskType

import requests
import json


class Inference:
    def __init__(self, base_url: str, triton_url: str = None) -> None:
        self.base_url = base_url
        self.triton_url = triton_url


    def shutdown(self):
        pass

    def _model_inference(self, model_name: str, input_text: str) -> Tuple[List[float], Dict[str, Any]]:
        triton_base = self.triton_url if self.triton_url else f"{self.base_url}/public/triton"
        url = f"{triton_base}/v2/models/{model_name}/infer"

        payload = json.dumps({
            "inputs": [{
                "name": "input_text",
                "shape": [1, 1],
                "datatype": "BYTES",
                "data": [input_text]
            }],
            "outputs": [{
                "name": "result"
            }, 
            {
                "name": "raw_logits",
                "parameters" : { "binary_data": False }
            }]
        })
        response = requests.request("POST", url, headers={'Content-Type': 'application/json'}, data=payload)
        response.raise_for_status()
        inference_output = response.json()["outputs"]
        raw_logits = next((output["data"] for output in inference_output if output["name"] == "raw_logits"), None)
        
        try:
            model_result = next((output["data"] for output in inference_output if output["name"] == "result"), None)
            model_result = json.loads(model_result[0])
        except Exception as e:
            raise ValueError(f"Failed to parse model result: {e}")

        return raw_logits, model_result
    

    def _parse_classification_result(self, model_result: Dict[str, Any]) -> ClassificationResponse:
        return ClassificationResponse(labels=model_result['labels'])
    
    def _parse_ner_result(self, model_result: Dict[str, Any]) -> EntityRecognitionResponse:
        return EntityRecognitionResponse.model_validate(model_result['response'])
    
    def _parse_model_result(self, model_result: Dict[str, Any]) -> list[AnyLMResponse]:
        if model_result['task_type'] == TaskType.classification.value:
            return [self._parse_classification_result(model_result)]
        elif model_result['task_type'] == TaskType.ner.value:
            return [self._parse_ner_result(model_result)]
        else:
            raise ValueError(f"Unknown task type: {model_result['task_type']}")
        
    def infer(self, prompt: str, usecase_name: str, group_name: str) -> Tuple[List[AnyLMResponse], List[float]]:
        model_name = f"model_{group_name}_{usecase_name}"
        raw_logits, model_result = self._model_inference(model_name, prompt)
        return self._parse_model_result(model_result), raw_logits
