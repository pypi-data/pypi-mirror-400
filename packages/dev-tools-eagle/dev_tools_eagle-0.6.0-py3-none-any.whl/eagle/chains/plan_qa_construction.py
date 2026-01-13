from eagle.utils.prompt_utils import EagleJsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain_core.language_models.base import BaseLanguageModel
from pydantic import BaseModel, Field
from typing import ClassVar, List
from operator import itemgetter

# Schemas for individual plan

# Schemas for the list of plans
class PlanProcessingOutputSchemaEN(BaseModel):
    short_description: str = Field(description="Summarized description of the knowledge found in the knowledge source")
    questions: List[str] = Field(description="Questions whose answers can be found in the knowledge source.")

class PlanProcessingOutputSchemaPT_BR(BaseModel):
    descricao_sumarizada: str = Field(description="Descrição sumarizada do conhecimento encontrado na fonte de conhecimento")
    perguntas: List[str] = Field(description="Perguntas cujas respostas podem ser encontradas na fonte de conhecimento.")

# Output Parsers
class PlanProcessingOutputParser(EagleJsonOutputParser):
    """Custom output parser for the plan processing chain."""

    CONVERTION_SCHEMA: ClassVar[dict] = {
        "pt-br": {
            "class_for_parsing": PlanProcessingOutputSchemaPT_BR,
            "convertion_schema": {
                "descricao_sumarizada": {
                    "target_key": "short_description",
                    "value_mapping": {}
                },
                "perguntas": {
                    "target_key": "questions",
                    "value_mapping": {}
                }
            }
        },
        "en": {
            "class_for_parsing": PlanProcessingOutputSchemaEN,
            "convertion_schema": {
                "short_description": {
                    "target_key": "short_description",
                    "value_mapping": {}
                },
                "questions": {
                    "target_key": "questions",
                    "value_mapping": {}
                }
            }
        },
    }

    TARGET_SCHEMA: BaseModel = PlanProcessingOutputSchemaEN

# Prompts

PLAN_PROCESSING_PROMPT_STR_PT_BR = """
Observe o texto abaixo:
---------------- Fonte de conhecimento -----------------
{{ text }}
-------------------------------------------------------

Agora, com base apenas no conteúdo do texto da Fonte de Conhecimento, você precisa seguir os seguintes passos:
1 - Observando o texto, pense em **{{ number_of_questions }} perguntas** cujas respostas poderiam ser encontradas nesta fonte de conhecimento caso se quisesse construir um plano a partir dela.
2 - Pense em **uma única descrição sumarizada** do conhecimento encontrado nesta fonte de conhecimento.

Diretrizes importantes:
1 - Imagine situações variadas para diferenciar as perguntas, maximizando a extração de conhecimento do texto da Fonte de Conhecimento.

Formato de saída JSON:
{
    "descricao_sumarizada": <descrição sumarizada do conhecimento encontrado na fonte de conhecimento>,
    "perguntas": [
        <Pergunta 1>,
        <Pergunta 2>,
        ... etc, até a pergunta {{ number_of_questions }}
    ]
}
"""

PLAN_PROCESSING_PROMPT_STR_EN = """
Observe the text below:
---------------- Knowledge Source -----------------
{{ text }}
---------------------------------------------------

Now, based only on the content of the Knowledge Source text, you must follow these steps:
1 - By observing the text, think of **{{ number_of_questions }} questions** whose answers could be found in this knowledge source if you wanted to build a plan from it.
2 - Think of **a single summarized description** of the knowledge found in this knowledge source.

Important guidelines:
1 - Imagine varied situations to differentiate the questions, maximizing the extraction of knowledge from the Knowledge Source text.

JSON output format:
{
    "short_description": <summarized description of the knowledge found in the knowledge source>,
    "questions": [
        <Question 1>,
        <Question 2>,
        ... etc, up to question {{ number_of_questions }}
    ]
}
"""

# Prompt Templates
PLAN_PROCESSING_PROMPTS = {
    "en": PromptTemplate.from_template(PLAN_PROCESSING_PROMPT_STR_EN, template_format="jinja2"),
    "pt-br": PromptTemplate.from_template(PLAN_PROCESSING_PROMPT_STR_PT_BR, template_format="jinja2"),
}

def create_plan_processing_chain(
    prompt_language: str,
    llm: BaseLanguageModel,
    use_structured_output: bool = False,
) -> RunnableSequence:
    """
    Create a plan processing chain based on the provided configuration.

    Args:
        prompt_language (str): Language for the prompt (e.g., "en", "pt-br").
        model_name (str): Name of the LLM model to use.
        temperature (float): Sampling temperature for the model.
        max_tokens (int): Maximum number of tokens for the output.

    Returns:
        RunnableSequence: A chain that processes plans based on the provided configuration.
    """
    if prompt_language not in PLAN_PROCESSING_PROMPTS:
        raise ValueError(f"Unsupported prompt language: {prompt_language}")

    prompt = PLAN_PROCESSING_PROMPTS[prompt_language]
    output_parser = PlanProcessingOutputParser(
        source_lang=prompt_language,
        llm=llm,
        use_structured_output=use_structured_output
    )
    _parse = RunnableLambda(
        lambda x: output_parser.parse(x)
    )

    chain = (
        {"text": itemgetter("text"), "number_of_questions": itemgetter("number_of_questions")}
        | prompt
        | llm
        | _parse
    )

    return chain
