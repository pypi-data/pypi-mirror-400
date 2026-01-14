import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sfn_blueprint import SFNAIHandler, self_correcting_sql, Context


from .config import MethodologyConfig
from .constants import format_approach_prompt
from .models import MethodologyRecommendation



class MLApproachDecisionAgent:
    def __init__(self, config: Optional[MethodologyConfig] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or MethodologyConfig()
        self.ai_handler = SFNAIHandler()

    def suggest_approach(self, domain_name, domain_description, use_case, column_insights, max_try=1) -> Tuple[MethodologyRecommendation, Dict[str, Any]]:
        """
        Suggests a machine learning approach based on the provided domain, use case, and column descriptions.
        Args:
            domain_name (str): The name of the domain.
            domain_description (str): The description of the domain.
            use_case (str): problem need to solve.
            column_descriptions (List[str]): A list of column descriptions.
            column_insights (List[str]): A list of column insights.
            max_try (int, optional): The maximum number of attempts to make the API call. Defaults to 3.

        Returns:
            MethodologyRecommendation: The suggested machine learning approach.
        
        TODO: 
            - USER prompt should consider those approaches which will be supported.
            
            
        """
        system_prompt, user_prompt = format_approach_prompt(domain_name=domain_name, domain_description=domain_description, use_case=use_case, column_insights=column_insights)
        for _ in range(max_try):
            try:
                response, cost_summary = self.ai_handler.route_to(
                    llm_provider=self.config.methodology_ai_provider,
                    configuration={
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "max_tokens": self.config.methodology_max_tokens,
                        # "temperature": self.config.methodology_temperature,
                        "text_format":MethodologyRecommendation
                    },
                    model=self.config.methodology_ai_model

                )


                return response, cost_summary

            except Exception as e:
                self.logger.error(f"Error while executing API call to {self.config.methodology_ai_provider}: {e}")

        return {}, {}
    


    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Executing data quality assessment task.")
        domain_name, domain_description, use_case, column_insights = (
            task_data["domain_name"],
            task_data["domain_description"],
            task_data["use_case"],
            task_data["column_insights"],
        )

        # Suggest an approach
        result, cost_summary = self.suggest_approach(
            domain_name=domain_name,
            domain_description=domain_description,
            use_case=use_case,
            column_insights=column_insights,
        )
        if not result:
            return {
                "success": False,
                "error": "Failed to suggest approach.",
                "agent": self.__class__.__name__
            }

        try:
            # Check if we have workflow storage information
            if 'workflow_storage_path' in task_data or 'workflow_id' in task_data:
                from sfn_blueprint import WorkflowStorageManager
                
                # Determine workflow storage path
                workflow_storage_path = task_data.get('workflow_storage_path', 'outputs/workflows')
                workflow_id = task_data.get('workflow_id', 'unknown')
                
                # Initialize storage manager
                storage_manager = WorkflowStorageManager(workflow_storage_path, workflow_id)
                storage_manager.save_agent_result(
                    agent_name=self.__class__.__name__,
                    step_name=" ",
                    data={"quality_reports": result.model_dump(), "cost_summary": cost_summary},
                    metadata={ "execution_time": datetime.now().isoformat()}
                )
                self.logger.info(" saved to workflow storage.")
        except Exception as e:
            self.logger.warning(f"Failed to save results to workflow storage: {e}")
        
        return {
                "success": True,
                "result": {
                    "approach": result ,
                    "cost_summary": cost_summary
                },
                "agent": self.__class__.__name__
            }
    
    def __call__(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.execute_task(task_data)
