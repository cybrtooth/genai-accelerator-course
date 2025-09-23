from core.schema import WorkflowSchema, NodeConfig
from core.workflow import Workflow

from schemas.nylas_webhook_schema import WebhookEvent
from workflows.email_workflow_nodes.email_filter_node import EmailFilterNode
from workflows.email_workflow_nodes.email_classification import ClassificationNode
from workflows.email_workflow_nodes.email_router_node import EmailRouterNode

from workflows.email_workflow_nodes.handle_spam_node import HandleSpamNode
from workflows.email_workflow_nodes.send_message_node import SendMessageNode
from workflows.email_workflow_nodes.process_resume_node import ProcessResumeNode

# so as an event schema this class takes in a webhook event 
class EmailWorkflow(Workflow):
    workflow_schema = WorkflowSchema(
        description="",
        event_schema=WebhookEvent,
        start=EmailFilterNode,
        nodes=[
            NodeConfig(
                node=EmailFilterNode,
                connections=[ClassificationNode],
                description="Filter for emails that are only from me.",
                parallel_nodes=[],
            ),
            NodeConfig(
                node=ClassificationNode,
                connections=[EmailRouterNode],
                description="Classify the email into a category",
                parallel_nodes=[],
            ),
            NodeConfig(
                node=EmailRouterNode,
                connections=[HandleSpamNode, SendMessageNode, ProcessResumeNode],
                description="Route to the appropriate node based on email category classification",
                parallel_nodes=[],
                is_router=True
            ),
        ],
    )