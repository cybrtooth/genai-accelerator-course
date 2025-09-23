from core.nodes.base import Node
from core.task import TaskContext
import os
import logging
from dotenv import load_dotenv
from enum import Enum
import asyncio

from pydantic import Field
from pydantic_ai import RunContext

from core.nodes.agent import AgentNode, AgentConfig, ModelProvider
from core.task import TaskContext
#from schemas.customer_care_schema import CustomerCareEventSchema
from services.prompt_loader import PromptManager
from schemas.nylas_email_schema import EmailObject


load_dotenv()

# this is often where you will write the logic 
# the agent node is the abstraction for pydantic logic 
class EmailCategory(str, Enum):
    SPAM = "spam"
    MESSAGE = "message"
    RESUME = "resume"
    OTHER = "other"
    
# as an enum you can do somehting like this, and if it is instantiated in any other value outside the enums it's invalid
# correct
# spam = EmailCategory.SPAM
# incorrect 
# spam = EmailCategory.junk

PROMPT = """
you are a helpful assistant who is an expert at classifying emails into one of the following categories:
- SPAM
- MESSAGE
- RESUME
- OTHER
"""


class CustomerIntent(str, Enum):
    GENERAL_QUESTION = "general/question"
    PRODUCT_QUESTION = "product/question"
    BILLING_INVOICE = "billing/invoice"
    REFUND_REQUEST = "refund/request"

    @property
    def escalate(self) -> bool:
        return self in {
            self.REFUND_REQUEST,
        }


class ClassificationNode(AgentNode):
    # the agent node here is where you define your output type - the structured output you will get
    class OutputType(AgentNode.OutputType):
        reasoning: str = Field(description="Explain your reasoning for the intent classification")
        category: EmailCategory = Field(description="The classified email category")
        confidence: float = Field(ge=0, le=1, description="Confidence score for the intent")
        #escalate: bool = Field(description="Flag to indicate if the ticket needs escalation due to harmful, inappropriate content, or attempted prompt injection")
    # you can also validate the input fields which is important - this class dependency types 
    class DepsType(AgentNode.DepsType):
        from_email: str = Field(..., description="Email address of the sender")
        sender: str = Field(..., description="Name or identifier of the sender")
        subject: str = Field(..., description="Subject of the ticket")
        body: str = Field(..., description="The body of the ticket")

    def get_agent_config(self) -> AgentConfig:
        return AgentConfig(
            #system_prompt=PromptManager().get_prompt("ticket_analysis"),
            system_prompt=PROMPT,
            output_type=self.OutputType,
            deps_type=self.DepsType,
            model_provider=ModelProvider.OPENAI,
            model_name="gpt-4o-mini",
        )

    # you will use this a lot - again the bucket of water/task context and we grab the email object from this and parse that
    def process(self, task_context: TaskContext) -> TaskContext:
        #email_object: EmailObject = task_context.event.data['object']   # this does not work bc we need to parse it
        email_object: EmailObject = EmailObject(**task_context.event.data['object'])   # use from email_filter_node
        #event: CustomerCareEventSchema = task_context.event
        deps = self.DepsType(
            from_email=email_object.from_[0].email,
            sender=email_object.from_[0].name,
            subject=email_object.subject,
            body=email_object.body,
        )

        # this is where we do a check to add the context and to the system prompt
        @self.agent.system_prompt
        def add_ticket_context(
            # so here we take our dependencies and do a model dump json that makes that information availble to the llm 
            ctx: RunContext[ClassificationNode.DepsType],
        ) -> str:
            return deps.model_dump_json(indent=2)

        # this is where we run the agent and pass in the user prompt after giving the agent the system prompt and tools 
        result = asyncio.run(self.agent.run(
            #user_prompt=event.model_dump_json(indent=2),
            # this is where we could do a little bit of prompt engineering 
            user_prompt="Classify this email."
        ))

        task_context.update_node(node_name=self.node_name, result=result)
        return task_context