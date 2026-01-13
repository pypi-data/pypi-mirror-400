from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from pydantic import BaseModel, Field
from typing import Dict, List, Any, ClassVar
from eagle.agents.react_agent.prompts import (
    YOU_ARE_IN_A_CONVERSATION_STR_EN,
    YOU_ARE_IN_A_CONVERSATION_STR_PT_BR,
    PLAN_STR_EN,
    PLAN_STR_PT_BR,
    OBSERVATION_STR_EN,
    OBSERVATION_STR_PT_BR,
    TOOLS_INTERACTIONS_STR_EN,
    TOOLS_INTERACTIONS_STR_PT_BR,
    OBJECTS_SUMMARY_STR_EN,
    OBJECTS_SUMMARY_STR_PT_BR,
    SYSTEM_PROMPT_TUPLE_EN,
    SYSTEM_PROMPT_TUPLE_PT_BR,
    IMPORTANT_GUIDELINES_STR_EN,
    IMPORTANT_GUIDELINES_STR_PT_BR
)
from eagle.utils.prompt_utils import PromptGenerator, EagleJsonOutputParser

# Output Schemas

class DataFrameRowsObservePromptOutputSchema(BaseModel):
    pass

class DataFrameRowsAnalystExecutePromptOutputSchemaEN(BaseModel):
    rows_to_maintain: List[int] = Field(
        description="The indices of the rows that should be maintained."
    )
    rows_to_delete: List[int] = Field(
        description="The indices of the rows that should be removed."
    )
    new_columns: Dict[str, List[Any]] = Field(
        description="Dictionary where each key is a new column name and the value is a list of values for the maintained rows."
    )
    comments: str = Field(
        description="General comments about the decisions made."
    )


class DataFrameRowsAnalystExecutePromptOutputSchemaPT_BR(BaseModel):
    linhas_a_manter: List[int] = Field(
        description="Os índices das linhas que devem ser mantidas."
    )
    linhas_a_excluir: List[int] = Field(
        description="Os índices das linhas que devem ser removidas."
    )
    novas_colunas: Dict[str, List[Any]] = Field(
        description="Dicionário onde cada chave é o nome de uma nova coluna e o valor é uma lista de valores para as linhas mantidas."
    )
    comentarios: str = Field(
        description="Comentários gerais sobre as decisões tomadas."
    )

class DataFrameRowsReaderExecutePromptOutputSchemaEN(BaseModel):
    comments: str = Field(
        description="General comments about the decisions made."
    )

class DataFrameRowsReaderExecutePromptOutputSchemaPT_BR(BaseModel):
    comentarios: str = Field(
        description="Comentários gerais sobre as decisões tomadas."
    )

# Output Parsers

class DataFrameRowsObservePromptOutputParser(EagleJsonOutputParser):
    CONVERTION_SCHEMA: ClassVar[dict] = {
        "pt-br": {
            "class_for_parsing": DataFrameRowsObservePromptOutputSchema,
            "convertion_schema": {
                "observacao": {
                    "target_key": "observation",
                    "value_mapping": {}
                }
            }
        },
        "en": {
            "class_for_parsing": DataFrameRowsObservePromptOutputSchema,
            "convertion_schema": {
                "observation": {
                    "target_key": "observation",
                    "value_mapping": {}
                }
            }
        }
    }
    TARGET_SCHEMA: BaseModel = DataFrameRowsObservePromptOutputSchema

class DataFrameRowsAnalystExecutePromptOutputParser(EagleJsonOutputParser):
    CONVERTION_SCHEMA: ClassVar[dict] = {
        "pt-br": {
            "class_for_parsing": DataFrameRowsAnalystExecutePromptOutputSchemaPT_BR,
            "convertion_schema": {
                "linhas_a_manter": {
                    "target_key": "rows_to_maintain",
                    "value_mapping": {}
                },
                "linhas_a_excluir": {
                    "target_key": "rows_to_delete",
                    "value_mapping": {}
                },
                "novas_colunas": {
                    "target_key": "new_columns",
                    "value_mapping": {}
                },
                "comentarios": {
                    "target_key": "comments",
                    "value_mapping": {}
                }
            }
        },
        "en": {
            "class_for_parsing": DataFrameRowsAnalystExecutePromptOutputSchemaEN,
            "convertion_schema": {
                "rows_to_maintain": {
                    "target_key": "rows_to_maintain",
                    "value_mapping": {}
                },
                "rows_to_delete": {
                    "target_key": "rows_to_delete",
                    "value_mapping": {}
                },
                "new_columns": {
                    "target_key": "new_columns",
                    "value_mapping": {}
                },
                "comments": {
                    "target_key": "comments",
                    "value_mapping": {}
                }
            }
        }
    }
    TARGET_SCHEMA: BaseModel = DataFrameRowsAnalystExecutePromptOutputSchemaEN

class DataFrameRowsReaderExecutePromptOutputParser(EagleJsonOutputParser):
    CONVERTION_SCHEMA: ClassVar[dict] = {
        "pt-br": {
            "class_for_parsing": DataFrameRowsReaderExecutePromptOutputSchemaPT_BR,
            "convertion_schema": {
                "comentarios": {
                    "target_key": "comments",
                    "value_mapping": {}
                }
            }
        },
        "en": {
            "class_for_parsing": DataFrameRowsReaderExecutePromptOutputSchemaEN,
            "convertion_schema": {
                "comments": {
                    "target_key": "comments",
                    "value_mapping": {}
                }
            }
        }
    }
    TARGET_SCHEMA: BaseModel = DataFrameRowsReaderExecutePromptOutputSchemaEN

# Prompt Strings

DATAFRAME_ROWS_OBSERVE_PROMPT_STR_PT_BR = """
Aqui estão as linhas da tabela que você deve analisar:

{{ dataframe_representation }}

"""

DATAFRAME_ROWS_OBSERVE_PROMPT_STR_EN = """
Here are the rows of the table you should analyze:

{{ dataframe_representation }}

"""

PROPOSE_NEW_COLUMNS_PROMPT_STR_PT_BR = """
{% if new_columns_proposals %}
Para cada linha, proponha novas colunas conforme o esquema abaixo:
```
{{ new_columns_proposals }}
```
{% endif %}
"""

PROPOSE_NEW_COLUMNS_PROMPT_STR_EN = """
{% if new_columns_proposals %}
For each row, propose new columns following the schema below:
```
{{ new_columns_proposals }}
```
{% endif %}
"""

DATAFRAME_ROWS_ANALYST_EXECUTE_PROMPT_STR_PT_BR = OBSERVATION_STR_PT_BR + \
"""
Analise as linhas do DataFrame/Tabela da 'Observação' e, para cada linha, execute as ações necessárias e decida se ela deve ser mantida ou excluída de acordo com o que foi pedido, além de adicionar, se for o caso, novas colunas de acordo com as ações executadas. Justifique sua decisão para cada linha.
""" + \
    PROPOSE_NEW_COLUMNS_PROMPT_STR_PT_BR + \
    PLAN_STR_PT_BR + \
    OBJECTS_SUMMARY_STR_PT_BR + \
    TOOLS_INTERACTIONS_STR_PT_BR + \
    IMPORTANT_GUIDELINES_STR_PT_BR + \
"""
Retorne um JSON com a seguinte estrutura:
{
    "linhas_a_manter": [...<os índices das linhas que devem ser mantidas>],
    "linhas_a_excluir": [...<os índices das linhas que devem ser removidas>],
    "novas_colunas": {
        "<nome da nova coluna>": [...<valores da nova coluna, levando em conta apenas as linhas a serem mantidas>]
        "<nome de outra nova coluna>": [...],
        ... etc
    },
    "comentarios": "Comentários gerais sobre as fontes das informações e eventuais problemas encontrados para processar a informação."
}
"""

DATAFRAME_ROWS_ANALYST_EXECUTE_PROMPT_STR_EN = OBSERVATION_STR_EN + \
"""
Analyze the rows of the DataFrame/Table from the 'Observation' and, for each row, decide whether it should be maintained or deleted according to what was requested. Justify your decision for each row.
""" + \
    PROPOSE_NEW_COLUMNS_PROMPT_STR_EN + \
    PLAN_STR_EN + \
    OBJECTS_SUMMARY_STR_EN + \
    TOOLS_INTERACTIONS_STR_EN + \
    IMPORTANT_GUIDELINES_STR_EN + \
"""
Return a JSON with the following structure:
{
    "rows_to_maintain": [...<the indices of the rows that should be maintained>],
    "rows_to_delete": [...<the indices of the rows that should be removed>],
    "new_columns": {
        "<new column name>": [...<values of the new column, considering only the rows to maintain>],
        "<another new column name>": [...],
        ... etc
    },
    "comments": "General comments about the sources of information and any issues encountered while processing the information."
}
"""

DATAFRAME_ROWS_READER_EXECUTE_PROMPT_STR_PT_BR = OBSERVATION_STR_PT_BR + \
"""
Analise as linhas do DataFrame/Tabela da 'Observação' e, para cada linha, execute as ações necessárias, leia, reflita sobre o que foi pedido e responda de acordo.
""" + \
    PLAN_STR_PT_BR + \
    OBJECTS_SUMMARY_STR_PT_BR + \
    TOOLS_INTERACTIONS_STR_PT_BR + \
    IMPORTANT_GUIDELINES_STR_PT_BR + \
"""
Retorne um JSON com a seguinte estrutura:
{
    "comentarios": <Comentários gerais sobre reflexões de acordo com o que foi pedido, além das fontes das informações e eventuais problemas encontrados para processar a informação. Faça referência aos dados que identificam cada linha, para ficar clara a situação de cada uma frente ao que foi demandado para sua análise. **RETORNE UMA STRING VAZIA CASO AS LINHAS ANALISADAS NÃO SE APLIQUEM QUANTO AO QUE FOI DEMANDADO!**>
}
"""

DATAFRAME_ROWS_READER_EXECUTE_PROMPT_STR_EN = OBSERVATION_STR_EN + \
"""
Analyze the rows of the DataFrame/Table from the 'Observation' and, for each row, perform the necessary actions, read, reflect on what was requested, and respond accordingly.
""" + \
    PLAN_STR_EN + \
    OBJECTS_SUMMARY_STR_EN + \
    TOOLS_INTERACTIONS_STR_EN + \
    IMPORTANT_GUIDELINES_STR_EN + \
"""
Return a JSON with the following structure:
{
    "comments": <General comments about reflections according to what was requested, as well as the sources of information and any issues encountered while processing the information. Make reference to the data that identifies each row, to make the situation of each one clear in relation to what was requested for your analysis. **RETURN AN EMPTY STRING IF THE ANALYZED ROWS DO NOT APPLY TO WHAT WAS REQUESTED!**>
}
"""

# Prompts

DATAFRAME_ROWS_OBSERVE_PROMPT_PT_BR = PromptTemplate.from_template(
    template=DATAFRAME_ROWS_OBSERVE_PROMPT_STR_PT_BR,
    template_format="jinja2"
)

DATAFRAME_ROWS_OBSERVE_PROMPT_EN = PromptTemplate.from_template(
    template=DATAFRAME_ROWS_OBSERVE_PROMPT_STR_EN,
    template_format="jinja2"
)

DATAFRAME_ROWS_ANALYST_EXECUTE_PROMPT_PT_BR = ChatPromptTemplate.from_messages([
    SYSTEM_PROMPT_TUPLE_PT_BR,
    HumanMessagePromptTemplate.from_template(
        template=YOU_ARE_IN_A_CONVERSATION_STR_PT_BR + DATAFRAME_ROWS_ANALYST_EXECUTE_PROMPT_STR_PT_BR,
        template_format="jinja2"
    ),
])

DATAFRAME_ROWS_ANALYST_EXECUTE_PROMPT_EN = ChatPromptTemplate.from_messages([
    SYSTEM_PROMPT_TUPLE_EN,
    HumanMessagePromptTemplate.from_template(
        template=YOU_ARE_IN_A_CONVERSATION_STR_EN + DATAFRAME_ROWS_ANALYST_EXECUTE_PROMPT_STR_EN,
        template_format="jinja2"
    ),
])

DATAFRAME_ROWS_READER_EXECUTE_PROMPT_PT_BR = ChatPromptTemplate.from_messages([
    SYSTEM_PROMPT_TUPLE_PT_BR,
    HumanMessagePromptTemplate.from_template(
        template=YOU_ARE_IN_A_CONVERSATION_STR_PT_BR + DATAFRAME_ROWS_READER_EXECUTE_PROMPT_STR_PT_BR,
        template_format="jinja2"
    ),
])

DATAFRAME_ROWS_READER_EXECUTE_PROMPT_EN = ChatPromptTemplate.from_messages([
    SYSTEM_PROMPT_TUPLE_EN,
    HumanMessagePromptTemplate.from_template(
        template=YOU_ARE_IN_A_CONVERSATION_STR_EN + DATAFRAME_ROWS_READER_EXECUTE_PROMPT_STR_EN,
        template_format="jinja2"
    ),
])

# Prompts dictionary for prompt_generator

PROMPTS_DICT = {
    "observe": {
        "output_parser": None,
        "languages": {
            "pt-br": DATAFRAME_ROWS_OBSERVE_PROMPT_PT_BR,
            "en": DATAFRAME_ROWS_OBSERVE_PROMPT_EN,
        },
    },
    "execute_analysis": {
        "output_parser": DataFrameRowsAnalystExecutePromptOutputParser,
        "languages": {
            "pt-br": DATAFRAME_ROWS_ANALYST_EXECUTE_PROMPT_PT_BR,
            "en": DATAFRAME_ROWS_ANALYST_EXECUTE_PROMPT_EN,
        },
    },
    "execute_reading": {
        "output_parser": DataFrameRowsReaderExecutePromptOutputParser,
        "languages": {
            "pt-br": DATAFRAME_ROWS_READER_EXECUTE_PROMPT_PT_BR,
            "en": DATAFRAME_ROWS_READER_EXECUTE_PROMPT_EN,
        },

    }
}

# If you use a PromptGenerator, you can initialize it here:
prompt_generator = PromptGenerator(prompts_dict=PROMPTS_DICT)
