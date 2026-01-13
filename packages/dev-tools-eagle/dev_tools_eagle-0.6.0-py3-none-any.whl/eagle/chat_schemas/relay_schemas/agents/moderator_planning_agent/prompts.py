from eagle.utils.output import convert_schema
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
from typing import ClassVar, List, Optional
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_PT_BR = """
Você coordena duas conversas: uma com o **DEMANDANTE** e outra com os **PARTICIPANTES**.
{%- if messages_with_requester %}
Abaixo, sua conversa com o **DEMANDANTE**:
-----------------------------------------------
{%- for message in messages_with_requester %}
{{ message.name }}: {{ message.content }}
{%- endfor %}
-----------------------------------------------
{%- else %}
Nenhuma mensagem trocada com o demandante ainda.
{%- endif %}
{%- if messages_with_agents %}
Abaixo, as mensagens trocadas entre os **PARTICIPANTES**:
-----------------------------------------------------
{%- for message in messages_with_agents %}
{{ message.name }}: {{ message.content }}
{%- endfor %}
-----------------------------------------------------
{%- else %}
Nenhuma mensagem trocada entre os participantes ainda.
{%- endif %}
"""

YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_EN = """
You are coordinating two conversations: one with the **REQUESTER** and another with the **PARTICIPANTS**.
{%- if messages_with_requester %}
Below is your conversation with the **REQUESTER**:
-----------------------------------------------
{%- for message in messages_with_requester %}
{{ message.name }}: {{ message.content }}
{%- endfor %}
-----------------------------------------------
{%- else %}
No messages exchanged with the requester yet.
{%- endif %}
{%- if messages_with_agents %}
Below are the messages exchanged between the **PARTICIPANTS**:
-----------------------------------------------------
{%- for message in messages_with_agents %}
{{ message.name }}: {{ message.content }}
{%- endfor %}
-----------------------------------------------------
{%- else %}
No messages exchanged between the participants yet.
{%- endif %}
"""

THESE_ARE_THE_SOME_PARTICIPANTS_STR_PT_BR = """
{%- if participants %}
Abaixo, uma descrição dos **PARTICIPANTES** (o seu "pool" de especialistas disponíveis):
-----------------------------------------------------
{%- for participant in participants %}
Nome: {{ participant.name }}
Descrição: {{ participant.description }}
{%- endfor %}
-----------------------------------------------------
{%- endif %}
"""

THESE_ARE_THE_SOME_PARTICIPANTS_STR_EN = """
{%- if participants %}
Below is a description of the **PARTICIPANTS** (your available pool of specialists):
-----------------------------------------------------
{%- for participant in participants %}
Name: {{ participant.name }}
Description: {{ participant.description }}
{%- endfor %}
-----------------------------------------------------
{%- endif %}
"""

MUST_CITE_OBJECTS_SUMMARY_STR_PT_BR = """
{%- if must_cite_objects_summary %}
Caso você decisa ENCERRAR parar a conversa com os **PARTICIPANTES** e dirigir-se para o **DEMANDANTE**, os seguintes objetos devem ser citados na resposta, com os respectivos IDs:
--------------- Objetos a serem citados-----------------
{{ must_cite_objects_summary }}
--------------------------------------------------------
{%- endif %}
"""

MUST_CITE_OBJECTS_SUMMARY_STR_EN = """
{%- if must_cite_objects_summary %}
If you decide to END the the conversation with the **PARTICIPANTS** and direct it to the **REQUESTER**, the following objects must be cited in the response, with their respective IDs:
--------------- Objects to be cited-----------------
{{ must_cite_objects_summary }}
--------------------------------------------------------
{%- endif %}
"""

# --- 2. PROMPT DO NÓ DE OBSERVAÇÃO (observe_relay) ---
OBSERVE_A_RELAY_STR_PT_BR = YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_PT_BR + \
    PLAN_STR_PT_BR + \
    OBSERVATION_STR_PT_BR + \
    OBJECTS_SUMMARY_STR_PT_BR + \
    MUST_CITE_OBJECTS_SUMMARY_STR_PT_BR + \
    TOOLS_INTERACTIONS_STR_PT_BR + \
    THESE_ARE_THE_SOME_PARTICIPANTS_STR_PT_BR + \
    IMPORTANT_GUIDELINES_STR_PT_BR + \
"""
Agora, decida o que fazer a seguir. Você pode escolher entre as seguintes opções:
1. Caso as demandas do DEMANDANTE ainda não tenham sido atendidas e precisem da colaboração dos PARTICIPANTES, você deve continuar para a etapa de PLANEJAMENTO. Nesse caso, o retorno em json deve ter a seguinte estrutura:
{
    "acao": "continuar_com_participantes",
    "mensagem": <Algumas observações importantes para a etapa seguinte de planejamento.>
}

2. Caso as demandas do DEMANDANTE tenham sido atendidas OU NÃO TENHAM RELAÇÃO com os participantes, você pode responder diretamente. Nesse caso, o retorno em json deve ter a seguinte estrutura:
{
    "acao": "continuar_com_demandante",
    "mensagem": <Mensagem a ser enviada ao DEMANDANTE com a resposta final.>
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
Now, decide what to do next. You can choose between the following options:
1. If the REQUESTER's demands have not yet been met and require collaboration from the PARTICIPANTS, you must proceed to the PLANNING step. In this case, the JSON return must have the following structure:
{
    "action": "continue_with_participants",
    "message": <Some important observations for this next planning step.>
}

2. If the REQUESTER's demands have been met OR DO NOT RELATE to the participants, you can respond directly. In this case, the JSON return must have the following structure:
{
    "action": "continue_with_requester",
    "message": <Message to be sent to the REQUESTER with the final answer.>
}

RESPONSE:
"""

# --- 3. PROMPT DO NÓ DE PLANEJAMENTO (plan_relay) ---
PLAN_A_RELAY_STR_PT_BR = YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_PT_BR + \
    PLAN_STR_PT_BR + \
    OBSERVATION_STR_PT_BR + \
    OBJECTS_SUMMARY_STR_PT_BR + \
    MUST_CITE_OBJECTS_SUMMARY_STR_PT_BR + \
    TOOLS_INTERACTIONS_STR_PT_BR + \
    THESE_ARE_THE_SOME_PARTICIPANTS_STR_PT_BR + \
    IMPORTANT_GUIDELINES_STR_PT_BR + \
"""
Agora, retorne com uma das seguintes saídas:
1. Caso tenha pensado em um plano, retorne um json com a seguinte estrutura:
{
    "acao": "executar",
    "mensagem": <Escreva aqui seu PLANO para prosseguir.>,
    "nomes_participantes_do_plano": [...lista com os nomes EXATOS dos participantes da execução do PLANO descrito na chave 'mensagem'...]
}
O PLANO deve ter o formato de to-do list, com passos numerados... (etc.)
... (Resto do prompt de planejamento do 'report_prompts-PLANNING.py')

RESPOSTA:
"""

PLAN_A_RELAY_STR_EN = YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_EN + \
    PLAN_STR_EN + \
    OBSERVATION_STR_EN + \
    OBJECTS_SUMMARY_STR_EN + \
    MUST_CITE_OBJECTS_SUMMARY_STR_EN + \
    TOOLS_INTERACTIONS_STR_EN + \
    THESE_ARE_THE_SOME_PARTICIPANTS_STR_EN + \
    IMPORTANT_GUIDELINES_STR_EN + \
"""
Now, return with one of the following outputs:
1. If you have thought of a plan, return a json with the following structure:
{
    "action": "execute",
    "message": <Write your PLAN to proceed here.>,
    "plan_participant_names": [...list with the EXACT names of the participants involved in the execution of the PLAN described in the 'message' key...]
}
The PLAN must be in the format of a to-do list, with numbered steps... (etc.)
... (Rest of the planning prompt from 'report_prompts-PLANNING.py')

RESPOSTA:
"""

# --- 4. PROMPT DO NÓ DE EXECUÇÃO (execute_relay) ---
EXECUTE_A_RELAY_STR_PT_BR = YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_PT_BR + \
    PLAN_STR_PT_BR + \
    OBSERVATION_STR_PT_BR + \
    OBJECTS_SUMMARY_STR_PT_BR + \
    MUST_CITE_OBJECTS_SUMMARY_STR_PT_BR + \
    TOOLS_INTERACTIONS_STR_PT_BR + \
    THESE_ARE_THE_SOME_PARTICIPANTS_STR_PT_BR + \
    IMPORTANT_GUIDELINES_STR_PT_BR + \
"""
Você está na etapa de EXECUÇÃO. Seu plano está definido.
Agora, decida a próxima ação tática com base no seu plano. Você pode:

1. **Iniciar um ciclo Relay**, se o seu plano indica que múltiplos participantes precisam colaborar em sequência. Analise a tarefa e SELECIONE APENAS os participantes necessários. A estrutura da resposta em JSON deve ser:
{
    "acao": "continuar_com_participantes_relay",
    "mensagem": "<Mensagem opcional a ser enviada aos participantes no início do ciclo>",
    "ordem": ["<Nome do primeiro participante SELECIONADO>", "<Nome do segundo>", ...]
}

2. **Falar com o Demandante**, se o seu plano indica que a colaboração terminou ou não é mais necessária e você já tem uma resposta. A estrutura da resposta em JSON deve ser:
{
    "acao": "continuar_com_demandante",
    "mensagem": "<Mensagem de encerramento, resumo ou resposta final ao demandante>"
}

RESPOSTA:
"""

EXECUTE_A_RELAY_STR_EN = YOU_ARE_IN_A_CONVERSATION_WITH_A_REQUESTER_AND_AGENTS_STR_EN + \
    PLAN_STR_EN + \
    OBSERVATION_STR_EN + \
    OBJECTS_SUMMARY_STR_EN + \
    MUST_CITE_OBJECTS_SUMMARY_STR_EN + \
    TOOLS_INTERACTIONS_STR_EN + \
    THESE_ARE_THE_SOME_PARTICIPANTS_STR_EN + \
    IMPORTANT_GUIDELINES_STR_EN + \
"""
You are in the EXECUTION step. Your plan is set.
Now, decide the next tactical action based on your plan. You can:

1. **Start a Relay cycle**, if your plan indicates that multiple participants need to collaborate in sequence. Analyze the task and SELECT ONLY the necessary participants. The JSON response structure must be:
{
    "action": "continue_with_participants_relay",
    "message": "<Optional message to send to participants at the start of the cycle>",
    "order": ["<Name of the first SELECTED participant>", "<Name of the second>", ...]
}

2. **Talk to the Requester**, if your plan indicates collaboration is finished or no longer needed and you have an answer. The JSON response structure must be:
{
    "action": "continue_with_requester",
    "message": "<Final message, summary, or answer to the requester>"
}

RESPONSE:
"""


# --- 5. SCHEMAS E PARSERS ---
class ObserveRelayPromptOutputSchemaEN(BaseModel):
    action: str = Field(description="Action to be taken. Can be 'continue_with_participants' or 'continue_with_requester'.")
    message: str = Field(description="Observations for the next step or final message to the requester.")

class ObserveRelayPromptOutputSchemaPT_BR(BaseModel):
    acao: str = Field(description="Ação a ser tomada. Pode ser 'continuar_com_participantes' ou 'continuar_com_demandante'.")
    mensagem: str = Field(description="Observações para a próxima etapa ou mensagem final ao demandante.")

class ObserveRelayPromptOutputParser(EagleJsonOutputParser):
    CONVERTION_SCHEMA: ClassVar[dict] = {
        "pt-br": {"class_for_parsing": ObserveRelayPromptOutputSchemaPT_BR, "convertion_schema": {"acao": {"target_key": "action", "value_mapping": {"continuar_com_participantes": "continue_with_participants", "continuar_com_demandante": "continue_with_requester"}}, "mensagem": {"target_key": "message", "value_mapping": {}}}},
        "en": {"class_for_parsing": ObserveRelayPromptOutputSchemaEN, "convertion_schema": {"action": {"target_key": "action", "value_mapping": {"continue_with_participants": "continue_with_participants", "continue_with_requester": "continue_with_requester"}}, "message": {"target_key": "message", "value_mapping": {}}}},
    }
    TARGET_SCHEMA: BaseModel = ObserveRelayPromptOutputSchemaEN

# Schema/Parser para PLAN
class PlanRelayPromptOutputSchemaEN(BaseModel):
    action: str = Field(description="Action to be taken. Can be 'execute' or 'nothing'.")
    message: str = Field(description="Message containing the plan or internal thoughts.")
    plan_participant_names: Optional[list[str]] = Field(default=None, description="List of exact names of participants involved in the plan execution.")

class PlanRelayPromptOutputSchemaPT_BR(BaseModel):
    acao: str = Field(description="Ação a ser tomada. Pode ser 'executar' ou 'nada'.")
    mensagem: str = Field(description="Mensagem contendo o plano ou pensamentos internos.")
    nomes_participantes_do_plano: Optional[list[str]] = Field(default=None, description="Lista com os nomes exatos dos participantes envolvidos na execução do plano.")

class PlanRelayPromptOutputParser(EagleJsonOutputParser):
    CONVERTION_SCHEMA: ClassVar[dict] = {
        "pt-br": {"class_for_parsing": PlanRelayPromptOutputSchemaPT_BR, "convertion_schema": {"acao": {"target_key": "action", "value_mapping": {"executar": "execute", "nada": "nothing"}}, "mensagem": {"target_key": "message", "value_mapping": {}}, "nomes_participantes_do_plano": {"target_key": "plan_participant_names", "value_mapping": {}}}},
        "en": {"class_for_parsing": PlanRelayPromptOutputSchemaEN, "convertion_schema": {"action": {"target_key": "action", "value_mapping": {"execute": "execute", "nothing": "nothing"}}, "message": {"target_key": "message", "value_mapping": {}}, "plan_participant_names": {"target_key": "plan_participant_names", "value_mapping": {}}}},
    }
    TARGET_SCHEMA: BaseModel = PlanRelayPromptOutputSchemaEN

# Schema/Parser para EXECUTE
class ExecuteRelayPromptOutputSchemaEN(BaseModel):
    action: str = Field(description="Action to be taken. Can be 'continue_with_participants_relay' or 'continue_with_requester'.")
    message: str = Field(description="Message to be sent to participants or requester.")
    order: Optional[List[str]] = Field(default_factory=list, description="List of chosen participants for the relay cycle, in order of execution.")

class ExecuteRelayPromptOutputSchemaPT_BR(BaseModel):
    acao: str = Field(description="Ação a ser tomada. Pode ser 'continuar_com_participantes_relay' ou 'continuar_com_demandante'.")
    mensagem: str = Field(description="Mensagem a ser enviada aos participantes ou ao demandante.")
    ordem: Optional[List[str]] = Field(default_factory=list, description="Lista de participantes escolhidos para o ciclo de relay, em ordem de execução.")

class ExecuteRelayPromptOutputParser(EagleJsonOutputParser):
    CONVERTION_SCHEMA: ClassVar[dict] = {
        "pt-br": {"class_for_parsing": ExecuteRelayPromptOutputSchemaPT_BR, "convertion_schema": {"acao": {"target_key": "action", "value_mapping": {"continuar_com_participantes_relay": "continue_with_participants_relay", "continuar_com_demandante": "continue_with_requester"}}, "mensagem": {"target_key": "message", "value_mapping": {}}, "ordem": {"target_key": "order", "value_mapping": {}}}},
        "en": {"class_for_parsing": ExecuteRelayPromptOutputSchemaEN, "convertion_schema": {"action": {"target_key": "action", "value_mapping": {"continue_with_participants_relay": "continue_with_participants_relay", "continue_with_requester": "continue_with_requester"}}, "message": {"target_key": "message", "value_mapping": {}}, "order": {"target_key": "order", "value_mapping": {}}}},
    }
    TARGET_SCHEMA: BaseModel = ExecuteRelayPromptOutputSchemaEN

# --- 6. DICIONÁRIO FINAL DE PROMPTS ---
_PROMPTS_DICT = {
    "observe_relay": {
        "output_parser": ObserveRelayPromptOutputParser,
        "languages": {
            "pt-br": ChatPromptTemplate.from_messages([SYSTEM_PROMPT_TUPLE_PT_BR, HumanMessagePromptTemplate.from_template(template=OBSERVE_A_RELAY_STR_PT_BR, template_format="jinja2")]),
            "en": ChatPromptTemplate.from_messages([SYSTEM_PROMPT_TUPLE_EN, HumanMessagePromptTemplate.from_template(template=OBSERVE_A_RELAY_STR_EN, template_format="jinja2")]),
        },
    },
    "plan_relay": {
        "output_parser": PlanRelayPromptOutputParser,
        "languages": {
            "pt-br": ChatPromptTemplate.from_messages([SYSTEM_PROMPT_TUPLE_PT_BR, HumanMessagePromptTemplate.from_template(template=PLAN_A_RELAY_STR_PT_BR, template_format="jinja2")]),
            "en": ChatPromptTemplate.from_messages([SYSTEM_PROMPT_TUPLE_EN, HumanMessagePromptTemplate.from_template(template=PLAN_A_RELAY_STR_EN, template_format="jinja2")]),
        },
    },
    "execute_relay": {
        "output_parser": ExecuteRelayPromptOutputParser,
        "languages": {
            "pt-br": ChatPromptTemplate.from_messages([SYSTEM_PROMPT_TUPLE_PT_BR, HumanMessagePromptTemplate.from_template(template=EXECUTE_A_RELAY_STR_PT_BR, template_format="jinja2")]),
            "en": ChatPromptTemplate.from_messages([SYSTEM_PROMPT_TUPLE_EN, HumanMessagePromptTemplate.from_template(template=EXECUTE_A_RELAY_STR_EN, template_format="jinja2")]),
        },
    },
    "node_vision": {
        "output_parser": NodeVisionPromptOutputParser,
        "languages": {
            "pt-br": NODE_VISION_PROMPT_STR_PT_BR,
            "en": NODE_VISION_PROMPT_STR_EN,
        },
    },
}

prompt_generator = PromptGenerator(prompts_dict=_PROMPTS_DICT)