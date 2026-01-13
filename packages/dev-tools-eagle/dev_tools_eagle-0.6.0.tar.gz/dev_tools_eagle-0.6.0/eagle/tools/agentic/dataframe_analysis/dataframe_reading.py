from typing import Optional, List, Dict, Any, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.language_models.chat_models  import BaseChatModel
import pandas as pd

from eagle.agents.specialists.data_analysis.dataframe_rows_analyst.base import (
    DataFrameRowsReaderAgent,
    prompt_generator
)
from eagle.memory.shared.shared_objects_memory import SharedObjectsMemory
from eagle.agents.react_agent.base import ReactPlanningAgent, SharedObjectsMemoryConfigSchema, ReactAgentStateCallbackManager
from eagle.chains.summarization import create_summarization_chain

class DataFrameReadingToolInput(BaseModel):
    tools_to_use: List[str] = Field(description="List of tool names important to use during the analysis.")
    analysis_demands: str = Field(description="List of important guidelines for the analysis.")
    dataframe_shared_object_id: str = Field(description="The alphanumeric 'id' (NOT THE NAME) of the dataframe object to analyze.")

class DataFrameReadingTool(BaseTool):
    # Tools properties
    name: str = "dataframe_reading_tool"
    description: str = (
        "A tool that analyzes the rows of a dataframe, searching and extracting important information as asked."
    )
    args_schema: Type[BaseModel] = DataFrameReadingToolInput
    calling_agent: ReactPlanningAgent

    max_rows_per_call: int

    not_a_dataframe_error_response_by_prompt_language: dict = {
        "en": "The object for this 'dataframe_shared_object_id' is not a DataFrame.",
        "pt-br": "O objeto referente a este 'dataframe_shared_object_id' não é um DataFrame."
    }

    shared_object_not_found_error_response_by_prompt_language: dict = {
        "en": "DataFrame not found by this 'dataframe_shared_object_id'.",
        "pt-br": "DataFrame não encontrado para este 'dataframe_shared_object_id'."
    }

    # Agents properties
    prompt_language: str
    chat_id: str
    agent_configs_by_prompt_language: dict = {
        "en": {
            "name": "Dataframe Analyst",
            "description": "An agent specialized in reading and extracting information from DataFrames.",
        },
        "pt-br": {
            "name": "Analista de Dataframe",
            "description": "Um agente especializado em ler e extrair informmações de um DataFrame.",
        }
    }
    agent_execute_important_guidelines_prompts_by_language: dict = {
        "en": "Use the tools you have to accomplish the following:\n{}",
        "pt-br": "Use as ferramentas que você tem para cumprir o seguinte:\n{}"
    }

    summarize_comments_prompts_by_language: dict = {
        "en": "The demand was this:\n{}\nThe comments about the processing of the DataFrame data, for each batch of rows read, were these:\n{}\nWhen summarizing, exclude the information that is not necessary for what was asked.",
        "pt-br": "A demanda foi a seguinte:\n{}\nOs comentários sobre o processamento dos dados do DataFrame, para cada grupo de linhas lidas, foram esses:\n{}\nAo sumarizar, exclua as informações que não sejam necessárias para o que foi demmandado."
    }
    
    tools_available: List[BaseTool] = []
    chat_history_window_size: int = 10
    shared_objects_memory: SharedObjectsMemory
    shared_objects_memory_configs: Optional[SharedObjectsMemoryConfigSchema] = SharedObjectsMemoryConfigSchema()
    has_vision: bool = False
    llm: BaseChatModel
    callback_manager: Optional[ReactAgentStateCallbackManager] = ReactAgentStateCallbackManager()

    def _run(self, **_inputs: DataFrameReadingToolInput) -> Dict[str, Any]:
        """
        Run the tool synchronously.

        Args:
            inputs (DataFrameAnalysisToolInput): Input object containing the configuration for the analysis.

        Returns:
            Dict[str, Any]: The analysis results including decisions and comments for each row.
        """
        # Extract arguments from inputs
        inputs = DataFrameReadingToolInput(**_inputs)

        inputs.tools_to_use = [x.replace("functions.", "") for x in inputs.tools_to_use]

        executing_tools = [tool if tool.name in inputs.tools_to_use else None for tool in self.tools_available]
        if executing_tools:
            execute_important_guidelines = self.agent_execute_important_guidelines_prompts_by_language[self.prompt_language].format(inputs.analysis_demands)
        else:
            execute_important_guidelines = inputs.analysis_demands

        agent_configs = {
            "agent_name": self.agent_configs_by_prompt_language[self.prompt_language]['name'],
            "chat_id": self.chat_id,
            "agent_description": self.agent_configs_by_prompt_language[self.prompt_language]['description'],
            "chat_history_window_size": self.chat_history_window_size,
            "observe_node_llm_prompt_language": self.prompt_language,
            "executing_tools": executing_tools,
            "execute_important_guidelines": execute_important_guidelines,
            "execute_node_llm": self.llm,
            "execute_node_llm_prompt_language": self.prompt_language,
            "execute_node_has_vision": self.has_vision,
            "execute_shared_objects_config": self.shared_objects_memory_configs,
            "execute_node_callback_manager": self.callback_manager,
            "dataframe_shared_object_id": inputs.dataframe_shared_object_id,
            "new_columns_proposals": []
        }

        # Prompt parser
        prompt_data = prompt_generator.generate_prompt(
            prompt_name="execute_reading",
            language=agent_configs['execute_node_llm_prompt_language'],
            llm=agent_configs['execute_node_llm'],
            use_structured_output=False
        )

        output_parser = prompt_data["output_parser"]

        # Summarization chain
        summarization_chain = create_summarization_chain(
            prompt_language=agent_configs['execute_node_llm_prompt_language'],
            llm=agent_configs['execute_node_llm']
        )

        # Checking dataframe shape from shared objects memory
        shared_object = self.shared_objects_memory.get_memory_object(
            chat_id=self.chat_id,
            object_id=inputs.dataframe_shared_object_id
        )

        if shared_object is None:
            return self.shared_object_not_found_error_response_by_prompt_language(self.prompt_language)
        if not isinstance(shared_object.object, pd.DataFrame):
            return self.not_a_dataframe_error_response_by_prompt_language(self.prompt_language)

        df = shared_object.object
        # Divide df rows based on self.max_rows_per_call
        df_length = len(df)

        comments_list = []
        for start_idx in range(0, df_length, self.max_rows_per_call):
            end_idx = min(start_idx + self.max_rows_per_call, df_length)
            idx_to_analyse = list(range(start_idx, end_idx))

            agent_config = agent_configs.copy()
            agent_config["dataframe_shared_object_list_of_idx_to_analyse"] = idx_to_analyse

            # Crie uma instância do agente com a configuração para este chunk
            agent_instance = DataFrameRowsReaderAgent(
                name=agent_config["agent_name"],
                description=agent_config["agent_description"]
            )

            agent_instance.load_memory("shared_objects", self.shared_objects_memory)

            # Execute o agente para este chunk
            if not hasattr(self.calling_agent, "_compiled_graph"):
                calling_agent_state = {
                    "messages": [
                         {
                            "role": "user",
                            "name": "User",
                            "content": execute_important_guidelines
                        }
                    ]
                }
            else:
                calling_agent_state = {
                    "messages": [
                        {
                            "role": "user",
                            "name": m.name,
                            "content": m.content
                        }
                        for m in self.calling_agent.state_snapshot.values['messages']
                    ]
                }

            agent_instance.run(
                state=calling_agent_state,
                config=agent_config
            )
            message = agent_instance.state_snapshot.values['messages'][-1]
            response = output_parser.parse(message)
            comments_list.append("--> rows idx: {}: {}".format(idx_to_analyse, response.comments))
        
        # Processing summary
        summary = summarization_chain.invoke(self.summarize_comments_prompts_by_language[self.prompt_language].format(execute_important_guidelines, "\n".join(comments_list)))

        # Final response
        return summary
