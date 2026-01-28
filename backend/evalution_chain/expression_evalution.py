from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel

from .base import create_evaluator_chain, invoke_evaluator_chain
from backend.evalution_chain.evalution import EvaluationInput


# ---------- SCHEMA ----------

class ExpressionsViolation(BaseModel):
    type: Literal["critical", "major", "minor"]
    description: str
    pointsDeducted: float = Field(ge=0)


class ExpressionsResult(BaseModel):
    score: float = Field(ge=0, le=1)
    violations: List[ExpressionsViolation]
    analysis: str = Field(
        description="Brief analysis of expression syntax and usage"
    )

# ---------- SYSTEM PROMPT ----------
system_prompt = """
You are an expert n8n workflow evaluator focusing specifically on EXPRESSION SYNTAX and CORRECTNESS.
Your task is to evaluate whether expressions correctly reference nodes and data using proper n8n syntax.

## Correct n8n Expression Syntax

### Modern Syntax (Preferred)
The correct n8n expression syntax uses `{{ $('Node Name').item.json.field }}` format

**Valid patterns:**
- Single item: `={{ $('Node Name').item.json.fieldName }}`
- All items: `={{ $('Node Name').all() }}`
- First/last item: `={{ $('Node Name').first().json.field }}` or `={{ $('Node Name').last().json.field }}`
- Array index: `={{ $('Node Name').all()[0].json.fieldName }}`
- Previous node: `={{ $json.fieldName }}` or `={{ $input.item.json.field }}`
- String with text: `="Text prefix {{ expression }} text suffix"`
- String with date: `="Report - {{ $now.format('MMMM d, yyyy') }}"`

### Special Tool Node Pattern
- Tool nodes (ending with "Tool") with ai_tool connections support $fromAI
- Format: `={{ $fromAI('parameterName', 'description', 'type', defaultValue) }}`

### Valid JavaScript in Expressions
- Array methods
- String operations
- Math operations
- Conditional logic

## Important: The = Prefix
- REQUIRED for expressions: `={{ expression }}`
- REQUIRED for mixed text/expressions

## Evaluation Criteria

### DO NOT penalize:
- Alternative but valid syntax
- Working but non-optimal expressions
- String concatenation styles

### Violations:

**Critical (-40 to -50):**
- Invalid JS syntax
- Non-existent nodes/fields
- Using $fromAI outside tool nodes
- Syntax errors

**Major (-20 to -25):**
- Missing = prefix
- Undefined variables
- Wrong data paths

**Minor (-5 to -10):**
- Outdated syntax
- Inefficient expressions
- Style-only issues

## Scoring
1. Start at 100
2. Deduct per violation
3. Min score = 0
4. Normalize to 0–1

Focus on execution correctness, not style.
""".strip()


# ---------- HUMAN TEMPLATE ----------

human_template = """
Evaluate the expression syntax of this workflow:

<user_prompt>
{userPrompt}
</user_prompt>

<generated_workflow>
{generatedWorkflow}
</generated_workflow>

{referenceSection}

Provide an expressions evaluation with score, violations, and brief analysis.
""".strip()


# ---------- CHAIN FACTORY ----------

def createExpressionsEvaluatorChain(llm: BaseChatModel):
    return create_evaluator_chain(
        llm,
        ExpressionsResult,
        system_prompt,
        human_template,
    )


# ---------- PUBLIC EVALUATION FUNCTION ----------

def evaluateExpressions(
    llm: BaseChatModel,
    input: EvaluationInput,
) -> ExpressionsResult:

    raw_result = invoke_evaluator_chain(
        createExpressionsEvaluatorChain(llm),
        input,
    )
    # print(f"Raw Result: {raw_result}")
    # print(f"Expressions Evaluation Parsed Result: {ExpressionsResult(**raw_result)}")
    #  invoke_evaluator_chain returns dict → convert explicitly
    return ExpressionsResult(**raw_result)
