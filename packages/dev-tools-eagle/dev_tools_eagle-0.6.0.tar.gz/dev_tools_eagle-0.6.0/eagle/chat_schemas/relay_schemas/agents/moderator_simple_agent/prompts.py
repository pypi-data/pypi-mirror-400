from eagle.utils.prompt_utils import PromptGenerator, EagleJsonOutputParser
from eagle.agents.react_agent.prompts import (
    OBJECTS_SUMMARY_STR_EN,
    OBJECTS_SUMMARY_STR_PT_BR,
    OBSERVATION_STR_PT_BR,
    OBSERVATION_STR_EN,
    PLAN_STR_PT_BR,
    PLAN_STR_EN,
    TOOLS_INTERACTIONS_STR_PT_BR,
    TOOLS_INTERACTIONS_STR_EN,
    SYSTEM_PROMPT_TUPLE_PT_BR,
    SYSTEM_PROMPT_TUPLE_EN,
    IMPORTANT_GUIDELINES_STR_PT_BR,
    IMPORTANT_GUIDELINES_STR_EN,
    NODE_VISION_PROMPT_STR_PT_BR,
    NODE_VISION_PROMPT_STR_EN,
    NodeVisionPromptOutputParser
)
from pydantic import BaseModel, Field
from typing import ClassVar, List
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

# --- MUDANÇA: Os blocos de texto genéricos são os mesmos do Report ---
# Mantemos a estrutura de apresentação do contexto para o LLM.
from eagle.chat_schemas.report_schemas.agents.moderator_simple_agent.prompts import (
    YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_PT_BR,
    YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_EN,
    THESE_ARE_THE_SOME_PARTICIPANTS_STR_PT_BR,
    THESE_ARE_THE_SOME_PARTICIPANTS_STR_EN,
    MUST_CITE_OBJECTS_SUMMARY_STR_PT_BR,
    MUST_CITE_OBJECTS_SUMMARY_STR_EN
)

OBSERVE_A_RELAY_STR_PT_BR = YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_PT_BR + \
    PLAN_STR_PT_BR + \
    OBSERVATION_STR_PT_BR + \
    OBJECTS_SUMMARY_STR_PT_BR + \
    MUST_CITE_OBJECTS_SUMMARY_STR_PT_BR + \
    TOOLS_INTERACTIONS_STR_PT_BR + \
    THESE_ARE_THE_SOME_PARTICIPANTS_STR_PT_BR + \
    IMPORTANT_GUIDELINES_STR_PT_BR + \
"""
Você está coordenando uma interação em ciclo entre os participantes.
{%- if messages_with_requester %}
Aqui está sua conversa com o DEMANDANTE:
-----------------------------------------------
{%- for message in messages_with_requester %}
{{ message.name }}: {{ message.content }}
{%- endfor %}
-----------------------------------------------
{%- else %}
Nenhuma mensagem com o demandante ainda.
{%- endif %}
{%- if messages_with_agents %}
Aqui estão as mensagens trocadas entre os PARTICIPANTES:
-----------------------------------------------------
{%- for message in messages_with_agents %}
{{ message.name }}: {{ message.content }}
{%- endfor %}
-----------------------------------------------------
{%- else %}
Nenhuma mensagem trocada entre os participantes ainda.
{%- endif %}

Agora, decida o que fazer a seguir. Você pode escolher entre:
1. **Continuar o ciclo**, se acredita que os participantes podem aprimorar ou complementar os resultados.
2. **Encerrar**, caso os resultados estejam satisfatórios para responder ao demandante.

Se decidir **continuar**, você deve analisar a tarefa do demandante e **SELECIONAR APENAS os participantes necessários** da lista acima. Em seguida, defina a ordem de execução para os participantes selecionados. Construa a ordem usando EXATAMENTE o nome descrito em {{ participants.name }}. A estrutura da resposta em JSON deve ser:
{
    "acao": "continuar_relay",
    "mensagem": "<Mensagem opcional a ser enviada aos participantes, ou string vazia se não houver>",
    "ordem": ["<Nome do primeiro participante SELECIONADO>", "<Nome do segundo participante SELECIONADO>", ...]
}

Se decidir **encerrar**, a estrutura da resposta em JSON deve ser:
{
    "acao": "encerrar_relay",
    "mensagem": "<Mensagem de encerramento, resumo ou resposta final ao demandante>"
}

RESPOSTA:
"""

OBSERVE_A_RELAY_STR_EN = YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_EN + \
    PLAN_STR_EN + \
    OBSERVATION_STR_EN + \
    OBJECTS_SUMMARY_STR_EN + \
    MUST_CITE_OBJECTS_SUMMARY_STR_EN + \
    TOOLS_INTERACTIONS_STR_EN + \
    THESE_ARE_THE_SOME_PARTICIPANTS_STR_EN + \
    IMPORTANT_GUIDELINES_STR_EN + \
"""
You are coordinating a cyclic interaction among participants.
{%- if messages_with_requester %}
Here is your conversation with the REQUESTER:
-----------------------------------------------
{%- for message in messages_with_requester %}
{{ message.name }}: {{ message.content }}
{%- endfor %}
-----------------------------------------------
{%- else %}
No messages with the requester yet.
{%- endif %}
{%- if messages_with_agents %}
Here are the messages exchanged among PARTICIPANTS:
-----------------------------------------------------
{%- for message in messages_with_agents %}
{{ message.name }}: {{ message.content }}
{%- endfor %}
-----------------------------------------------------
{%- else %}
No messages exchanged among the participants yet.
{%- endif %}

Now, decide what to do next. You can choose between:
1. **Continue the relay cycle** if you believe the participants can enhance or complement the results.
2. **End the relay** if the results are satisfactory to respond to the requester.

If you decide to **continue**, you must analyze the requester's task and **SELECT ONLY the necessary participants** from the list above. Then, define the execution order for the selected participants. Construct the order using EXACTLY the name described in {{ participants.name}}. The JSON response structure must be:
{
    "action": "continue_relay",
    "message": "<Optional message to send to participants, or an empty string if none>",
    "order": ["<Name of the first SELECTED participant>", "<Name of the second SELECTED participant>", ...]
}

If you decide to **end**, the JSON response structure must be:
{
    "action": "end_relay",
    "message": "<Final message, summary, or answer to the requester>"
}

RESPONSE:
"""

OBSERVE_A_RELAY_PROMPT_PT_BR = ChatPromptTemplate.from_messages(
    [SYSTEM_PROMPT_TUPLE_PT_BR, HumanMessagePromptTemplate.from_template(template=OBSERVE_A_RELAY_STR_PT_BR, template_format="jinja2")]
)
OBSERVE_A_RELAY_PROMPT_EN = ChatPromptTemplate.from_messages(
    [SYSTEM_PROMPT_TUPLE_EN, HumanMessagePromptTemplate.from_template(template=OBSERVE_A_RELAY_STR_EN, template_format="jinja2")]
)
NODE_VISION_PROMPT_PT_BR = ChatPromptTemplate.from_messages(
    [SYSTEM_PROMPT_TUPLE_PT_BR, HumanMessagePromptTemplate.from_template(template=YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_PT_BR + NODE_VISION_PROMPT_STR_PT_BR, template_format="jinja2")]
)
NODE_VISION_PROMPT_EN = ChatPromptTemplate.from_messages(
    [SYSTEM_PROMPT_TUPLE_EN, HumanMessagePromptTemplate.from_template(template=YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_EN + NODE_VISION_PROMPT_STR_EN, template_format="jinja2")]
)

class ObserveRelayPromptOutputSchemaEN(BaseModel):
    action: str = Field(description="Action to be taken. Can be 'continue_relay' or 'end_relay'.")
    message: str = Field(description="Message to be sent to the participants or the requester.")
    order: List[str] = Field(default_factory=list, description="List of chosen participants for this relay interaction, in order of execution.")

class ObserveRelayPromptOutputSchemaPT_BR(BaseModel):
    acao: str = Field(description="Ação a ser tomada. Pode ser 'continuar_relay' ou 'encerrar_relay'.")
    mensagem: str = Field(description="Mensagem a ser enviada aos participantes ou ao demandante.")
    ordem: List[str] = Field(default_factory=list, description="Lista de participantes escolhidos para esta interação do relay, em ordem de execução.")

class ObserveRelayPromptOutputParser(EagleJsonOutputParser):
    CONVERTION_SCHEMA: ClassVar[dict] = {
        "pt-br": {
            "class_for_parsing": ObserveRelayPromptOutputSchemaPT_BR,
            "convertion_schema": {
                "acao": {"target_key": "action", "value_mapping": {"continuar_relay": "continue_relay", "encerrar_relay": "end_relay"}},
                "mensagem": {"target_key": "message", "value_mapping": {}},
                "ordem": {"target_key": "order", "value_mapping": {}}
            }
        },
        "en": {
            "class_for_parsing": ObserveRelayPromptOutputSchemaEN,
            "convertion_schema": {
                "action": {"target_key": "action", "value_mapping": {"continue_relay": "continue_relay", "end_relay": "end_relay"}},
                "message": {"target_key": "message", "value_mapping": {}},
                "order": {"target_key": "order", "value_mapping": {}}
            }
        },
    }
    TARGET_SCHEMA: BaseModel = ObserveRelayPromptOutputSchemaEN

# Dicionário de Prompts
_PROMPTS_DICT = {
    "observe_relay": {
        "output_parser": ObserveRelayPromptOutputParser,
        "languages": {"pt-br": OBSERVE_A_RELAY_PROMPT_PT_BR, "en": OBSERVE_A_RELAY_PROMPT_EN},
    },
    "node_vision": {
        "output_parser": NodeVisionPromptOutputParser,
        "languages": {"pt-br": NODE_VISION_PROMPT_PT_BR, "en": NODE_VISION_PROMPT_EN},
    },
}
prompt_generator = PromptGenerator(prompts_dict=_PROMPTS_DICT)

