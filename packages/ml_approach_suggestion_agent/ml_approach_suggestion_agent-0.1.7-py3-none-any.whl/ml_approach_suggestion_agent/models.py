from pydantic import BaseModel, Field , ConfigDict
from typing import Literal

class MethodologyRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    selected_methodology: Literal[ "binary_classification", "timeseries_binary_classification", "not_applicable"] = Field(..., description="The most appropriate ML approach for this problem")
    
    justification: str = Field( ..., description="Structured explanation with: business goal, prediction type, temporal dependency analysis, and methodology fit")


