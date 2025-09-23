from typing import Optional
import logging
from core.nodes.base import Node
from core.nodes.router import BaseRouter, RouterNode
from core.task import TaskContext

from workflows.email_workflow_nodes.handle_spam_node import HandleSpamNode
from workflows.email_workflow_nodes.send_message_node import SendMessageNode
from workflows.email_workflow_nodes.process_resume_node import ProcessResumeNode
from workflows.email_workflow_nodes.email_classification import EmailCategory


class EmailRouterNode(BaseRouter):
    def __init__(self):
        self.routes = [
            EmailRoute()
        ]
        self.fallback = SendMessageNode()


class EmailRoute(RouterNode):
    # logic goes in here and decides really to return the handlespam node or return something else. Take syntax and logic from test_workflow
    def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
        category = task_context.nodes['ClassificationNode']['result'].output.category
        #output: FilterSpamNode.OutputType = task_context.nodes["FilterSpamNode"]["result"].output
        #if not output.is_human and output.confidence > 0.8:
        #    return CloseTicketNode()
        print(f'This is the category: {category}')
        if category == EmailCategory.SPAM: 
            logging.info("spam category") 
            return HandleSpamNode()
        elif category == EmailCategory.RESUME:
            logging.info("Resume category") 
            print('going to resume router - currently in email router node \n')
            return ProcessResumeNode()
        elif category == EmailCategory.MESSAGE:
            logging.info("Message category")
            return SendMessageNode()
        elif category == EmailCategory.OTHER:
            logging.info("other category. Don't do anything for other emails.")
            return None
        return None


# class SendMessageRouter(RouterNode):
#     def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
#         analysis = task_context.nodes["DetermineTicketIntentNode"]["result"].output
#         if analysis.intent.escalate or analysis.escalate:
#             return EscalateTicketNode()
#         return None


# class ResumeRouter(RouterNode):
#     def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
#         analysis = task_context.nodes["DetermineTicketIntentNode"]["result"].output
#         if analysis.intent == CustomerIntent.BILLING_INVOICE:
#             return ProcessInvoiceNode()
#         return None