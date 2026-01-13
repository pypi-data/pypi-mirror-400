from eagle.memory.planning.base import PlanningMemory
from eagle.chains.plan_qa_construction import create_plan_processing_chain
from langchain_core.language_models.chat_models  import BaseChatModel
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field, field_validator
from langchain.chains.query_constructor.base import AttributeInfo
import asyncio
import hashlib
import os
import yaml

# Schemas
class PlanDescriptorSchema(BaseModel):
    plan: str = Field(..., description="Details of the plan")
    question: str = Field(..., description="Question derived from the plan")
    short_description: str = Field(..., description="Short description of the plan")
    source: Optional[str] = Field(None, description="Source of the plan")
    title: str = Field(..., description="Title of the plan")  # <-- Adicionado

class PossiblePlansMemoryConfigSchema(BaseModel):
    chain_llm: Optional[BaseChatModel] = Field(default=None, description="Language model for processing and checking")
    chain_llm_prompt_language: str = Field(default="pt-br", description="Language for the translation prompt")
    number_of_questions: Optional[int] = Field(
        default=None, description="Number of questions to be generated."
    )

# Memory class
class PlansQAMemory(PlanningMemory):
    """
    Memory class for managing and extracting possible plans from questions.
    """
    
    MEMORY_NAME = "eagle-qa-plans-memory"

    EMBEDDED_FIELDS = ["question", "short_description"]

    VALUE_EXAMPLE = {
        "question": "Example question",
        "plan": "Example plan",
        "short_description": "Example short description",
        "source": "Example source",
        "title": "Example title",  # <-- Adicionado
        "type": "qa_plans"
    }

    ATTRIBUTE_INFO = [
        AttributeInfo(name="value.question", type="string", description="Question derived from the memory"),
        AttributeInfo(name="value.plan", type="string", description="Plan details"),
        AttributeInfo(name="value.short_description", type="string", description="Short description of the plan"),
        AttributeInfo(name="value.source", type="string", description="Source of the plan"),
        AttributeInfo(name="value.title", type="string", description="Title of the plan"),  # <-- Adicionado
        AttributeInfo(name="value.type", type="string", description="Type of the memory"),
    ]

    def _get_namespace(self, plans_set_id):
        """Helper to build namespace tuple from plans_set_id (str or tuple)."""
        if isinstance(plans_set_id, tuple):
            return (self.MEMORY_NAME,) + plans_set_id
        else:
            return (self.MEMORY_NAME, plans_set_id)

    def put_memory(
        self,
        plans_set_id,
        plan_id: str,
        question: str,
        plan: str,
        short_description: str,
        source: str,
        title: str,  # <-- Adicionado
        ttl: Optional[float] = None,
    ) -> None:
        """
        Add a memory for a QA plan.

        Args:
            plans_set_id (str): The unique identifier for the set of plans.
            plan_id (str): The unique identifier for the plan.
            question (str): A question derived from the plan.
            plan (str): The plan details.
            short_description (str): Short description of the plan.
            source (str): The source of the plan.
            title (str): The title of the plan.  # <-- Adicionado
            ttl (Optional[float]): Time-to-live for the memory in minutes.
        """
        namespace = self._get_namespace(plans_set_id)
        value = {
            "question": question,
            "plan": plan,
            "short_description": short_description,
            "source": source,
            "title": title,  # <-- Adicionado
            "type": "qa_plans",
        }
        super().put_memory(namespace=namespace, key=plan_id, value=value, ttl=ttl)

    async def aput_memory(
        self,
        plans_set_id,
        plan_id: str,
        question: str,
        plan: str,
        short_description: str,
        source: str,
        title: str,  # <-- Adicionado
        ttl: Optional[float] = None,
    ) -> None:
        """
        Asynchronously add a memory for a QA plan.
        """
        namespace = self._get_namespace(plans_set_id)
        value = {
            "question": question,
            "plan": plan,
            "short_description": short_description,
            "source": source,
            "title": title,  # <-- Adicionado
            "type": "qa_plans",
        }
        await super().aput_memory(namespace=namespace, key=plan_id, value=value, ttl=ttl)

    def get_memory(self, plans_set_id, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a memory for a QA plan.
        """
        namespace = self._get_namespace(plans_set_id)
        item = super().get_memory(namespace=namespace, key=plan_id)
        return item.value if item else None

    async def aget_memory(self, plans_set_id, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Asynchronously retrieve a memory for a QA plan.
        """
        namespace = self._get_namespace(plans_set_id)
        item = await super().aget_memory(namespace=namespace, key=plan_id)
        return item.value if item else None

    def delete_memory(self, plans_set_id, plan_id: str) -> None:
        """
        Delete a memory for a QA plan.
        """
        namespace = self._get_namespace(plans_set_id)
        super().delete_memory(namespace=namespace, key=plan_id)

    async def adelete_memory(self, plans_set_id, plan_id: str) -> None:
        """
        Asynchronously delete a memory for a QA plan.
        """
        namespace = self._get_namespace(plans_set_id)
        await super().adelete_memory(namespace=namespace, key=plan_id)

    def delete_memories_by_namespace(self, plans_set_id) -> None:
        """
        Delete all QA plans memories in the given namespace.
        """
        namespace = self._get_namespace(plans_set_id)
        super().delete_memories_by_namespace(namespace)

    def search_memories(
        self,
        plans_set_id,
        query: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        filter_sources: Optional[List[str]] = None,
        filter_titles: Optional[List[str]] = None,  # <-- Adicionado
    ) -> List[Dict[str, Any]]:
        """
        Search for memories of QA plans.
        """
        namespace_prefix = self._get_namespace(plans_set_id)
        filter_list = []
        if filter_sources:
            filter_sources_expr = 'or(' + ','.join([f'eq("value.source", "{source}")' for source in filter_sources]) + ')'
            filter_list.append(filter_sources_expr)
        if filter_titles:
            filter_titles_expr = 'or(' + ','.join([f'eq("value.title", "{title}")' for title in filter_titles]) + ')'
            filter_list.append(filter_titles_expr)
        filter = 'and(' + ','.join(filter_list) + ')' if filter_list else None
        items = super().search_memories(
            namespace_prefix=namespace_prefix,
            query=query,
            filter=filter,
            limit=limit,
            offset=offset,
        )
        return [item.value for item in items]

    async def asearch_memories(
        self,
        plans_set_id,
        query: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        filter_sources: Optional[List[str]] = None,
        filter_titles: Optional[List[str]] = None,  # <-- Adicionado
    ) -> List[Dict[str, Any]]:
        """
        Asynchronously search for memories of QA plans.
        """
        namespace_prefix = self._get_namespace(plans_set_id)
        filter_list = []
        if filter_sources:
            filter_sources_expr = 'or(' + ','.join([f'eq("value.source", "{source}")' for source in filter_sources]) + ')'
            filter_list.append(filter_sources_expr)
        if filter_titles:
            filter_titles_expr = 'or(' + ','.join([f'eq("value.title", "{title}")' for title in filter_titles]) + ')'
            filter_list.append(filter_titles_expr)
        filter = 'and(' + ','.join(filter_list) + ')' if filter_list else None
        items = await super().asearch_memories(
            namespace_prefix=namespace_prefix,
            query=query,
            filter=filter,
            limit=limit,
            offset=offset,
        )
        return [item.value for item in items]

    async def abuild(
        self,
        plans_set_id,
        plans_descriptors: List[PlanDescriptorSchema],
        config: PossiblePlansMemoryConfigSchema = {"chain_llm": None, "number_of_questions": 5},
        ttl: Optional[float] = None,
    ) -> None:
        """
        Build and persist QA plans with processed questions and short descriptions.

        Args:
            plans_set_id (str): The unique identifier for the set of plans.
            plans_descriptors (List[PlanDescriptorSchema]): List of dicts with 'plan', 'question', 'short_description', and optional 'source'.
            config (PossiblePlansMemoryConfigSchema): Configuration for the processing chain.
            ttl (Optional[float]): Time-to-live for the memory in minutes.
        """
        config = PossiblePlansMemoryConfigSchema(**config)
        number_of_questions = config.number_of_questions or 5

        if config.chain_llm is None:
            # Just store the descriptors as they are
            for plan_descriptor in plans_descriptors:
                plan_id = hashlib.sha256(plan_descriptor.question.encode("utf-8")).hexdigest()
                await self.aput_memory(
                    plans_set_id=plans_set_id,
                    plan_id=plan_id,
                    question=plan_descriptor.question,
                    plan=plan_descriptor.plan,
                    short_description=plan_descriptor.short_description,
                    source=plan_descriptor.source or "unknown",
                    title=plan_descriptor.title,  # <-- Adicionado
                    ttl=ttl,
                )
                await asyncio.sleep(0.1)
        else:
            processing_chain = create_plan_processing_chain(
                prompt_language=config.chain_llm_prompt_language,
                llm=config.chain_llm
            )
            async def process_plan(plan_descriptor: PlanDescriptorSchema):
                source = plan_descriptor.source or "unknown"
                processed_output = await processing_chain.ainvoke({
                    "text": plan_descriptor.plan,
                    "number_of_questions": number_of_questions
                })
                short_description = processed_output["short_description"]
                for question in processed_output["questions"]:
                    plan_id = hashlib.sha256(question.encode("utf-8")).hexdigest()
                    await self.aput_memory(
                        plans_set_id=plans_set_id,
                        plan_id=plan_id,
                        question=question,
                        plan=plan_descriptor.plan,
                        short_description=short_description,
                        source=source,
                        title=plan_descriptor.title,  # <-- Adicionado
                        ttl=ttl,
                    )
                    await asyncio.sleep(0.1)
            await asyncio.gather(*(process_plan(plan) for plan in plans_descriptors))

    def build(
        self,
        plans_set_id,
        plans_descriptors: List[PlanDescriptorSchema],
        config: PossiblePlansMemoryConfigSchema = {"chain_llm": None, "number_of_questions": 5},
        ttl: Optional[float] = None,
    ) -> None:
        """
        Synchronous build method for QA plans memory.

        Args:
            plans_set_id (str): The unique identifier for the set of plans.
            plans_descriptors (List[PlanDescriptorSchema]): List of dicts with 'plan', 'question', 'short_description', and optional 'source'.
            config (PossiblePlansMemoryConfigSchema): Configuration for the processing chain.
            ttl (Optional[float]): Time-to-live for the memory in minutes.
        """
        config = PossiblePlansMemoryConfigSchema(**config)
        number_of_questions = config.number_of_questions or 5

        if config.chain_llm is None:
            for plan_descriptor in plans_descriptors:
                plan_id = hashlib.sha256(plan_descriptor.question.encode("utf-8")).hexdigest()
                self.put_memory(
                    plans_set_id=plans_set_id,
                    plan_id=plan_id,
                    question=plan_descriptor.question,
                    plan=plan_descriptor.plan,
                    short_description=plan_descriptor.short_description,
                    source=plan_descriptor.source or "unknown",
                    title=plan_descriptor.title,  # <-- Adicionado
                    ttl=ttl,
                )
        else:
            processing_chain = create_plan_processing_chain(
                prompt_language=config.chain_llm_prompt_language,
                llm=config.chain_llm
            )
            for plan_descriptor in plans_descriptors:
                source = plan_descriptor.source or "unknown"
                processed_output = processing_chain.invoke({
                    "text": plan_descriptor.plan,
                    "number_of_questions": number_of_questions
                })
                short_description = processed_output.short_description
                for question in processed_output.questions:
                    plan_id = hashlib.sha256(question.encode("utf-8")).hexdigest()
                    self.put_memory(
                        plans_set_id=plans_set_id,
                        plan_id=plan_id,
                        question=question,
                        plan=plan_descriptor.plan,
                        short_description=short_description,
                        source=source,
                        title=plan_descriptor.title,  # <-- Adicionado
                        ttl=ttl,
                    )

    def study(
        self,
        plans_set_id,
        directories: List[str],
        config: PossiblePlansMemoryConfigSchema = {"chain_llm": None, "number_of_questions": 5},
    ) -> None:
        """
        Create a set of QA plans by processing YAML files in the given directories.

        Args:
            plans_set_id (str): The unique identifier for this set of plans.
            directories (List[str]): A list of directory paths to search for YAML files.
            config (PossiblePlansMemoryConfigSchema): Configuration for the processing chain.
        """
        plans_descriptors = []
        for directory in directories:
            for filename in os.listdir(directory):
                if filename.endswith(".yaml") or filename.endswith(".yml"):
                    file_path = os.path.join(directory, filename)
                    with open(file_path, "r", encoding="utf-8") as file:
                        try:
                            data = yaml.safe_load(file)
                            source = data.get("source", "unknown").strip()
                            text = data.get("text", "").strip()
                            title = data.get("title", "").strip()
                            short_description = data.get("short_description", "").strip()
                            if text:
                                plans_descriptors.append(
                                    PlanDescriptorSchema(
                                        plan=text,
                                        question=title,
                                        short_description=short_description,
                                        source=source,
                                        title=title  # <-- Adicionado
                                    )
                                )
                        except yaml.YAMLError:
                            raise ValueError(f"Invalid YAML format in file: {file_path}")
        self.build(plans_set_id=plans_set_id, plans_descriptors=plans_descriptors, config=config)