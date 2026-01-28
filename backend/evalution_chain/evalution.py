
from typing import List, Optional, Literal, Any
from pydantic import BaseModel, Field, ConfigDict


# Placeholder for SimpleWorkflow
# Replace this with your real workflow model if you have one
class SimpleWorkflow(BaseModel):
    model_config = ConfigDict(extra="allow")


# Violation Schema
class Violation(BaseModel):
    type: Literal["critical", "major", "minor"]
    description: str
    pointsDeducted: float = Field(ge=0)


# Category Score
class CategoryScore(BaseModel):
    violations: List[Violation]
    score: float = Field(ge=0, le=1)


# Structural Similarity
class StructuralSimilarityScore(CategoryScore):
    applicable: bool = Field(
        description="Whether this category was evaluated (based on reference workflow availability)"
    )

# Efficiency Score

class EfficiencyScore(CategoryScore):
    redundancyScore: float = Field(ge=0, le=1, description="Score for avoiding redundant operations")
    pathOptimization: float = Field(ge=0, le=1, description="Score for optimal execution paths")
    nodeCountEfficiency: float = Field(ge=0, le=1, description="Score for using minimal nodes")


# Maintainability Score
class MaintainabilityScore(CategoryScore):
    nodeNamingQuality: float = Field(ge=0, le=1, description="Score for descriptive node naming")
    workflowOrganization: float = Field(ge=0, le=1, description="Score for logical workflow structure")
    modularity: float = Field(ge=0, le=1, description="Score for reusable and modular components")



# Best Practices Score
class BestPracticesScore(CategoryScore):
    techniques: Optional[List[str]] = Field(
        default=None,
        description="Workflow techniques identified for this evaluation",
    )


# Main Evaluation Result
class EvaluationResult(BaseModel):
    overallScore: float = Field(
        ge=0,
        le=1,
        description="Weighted average score across all categories (0-1)",
    )

    functionality: CategoryScore
    connections: CategoryScore
    expressions: CategoryScore
    nodeConfiguration: CategoryScore
    structuralSimilarity: StructuralSimilarityScore
    efficiency: EfficiencyScore
    dataFlow: CategoryScore
    maintainability: MaintainabilityScore
    bestPractices: BestPracticesScore

    summary: str = Field(description="2-3 sentences summarizing strengths and weaknesses")
    criticalIssues: Optional[List[str]] = Field(
        default=None,
        description="Issues that prevent workflow from functioning",
    )



# Test Case
class TestCase(BaseModel):
    id: str
    name: str
    prompt: str
    referenceWorkflow: Optional[SimpleWorkflow] = None
    referenceWorkflows: Optional[List[SimpleWorkflow]] = None


# Evaluation Input

class EvaluationInput(BaseModel):
    userPrompt: str
    generatedWorkflow: SimpleWorkflow
    referenceWorkflow: Optional[SimpleWorkflow] = None
    referenceWorkflows: Optional[List[SimpleWorkflow]] = None
    preset: Optional[Literal["strict", "standard", "lenient"]] = None
