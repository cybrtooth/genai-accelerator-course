from pathlib import Path 
import sys
import json
import asyncio

# this will let you import from any module/folder in the app directory so like the schemas below
sys.path.append(str(Path(__file__).parent.parent) + "/app")

from utils.event_loader import EventLoader 
from schemas.nylas_email_schema import EmailObject
from schemas.nylas_webhook_schema import WebhookEvent

# so now for testing 
from workflows.email_workflow import EmailWorkflow
from workflows.email_workflow_nodes.email_classification import EmailCategory 
#from workflows.email_workflow_noes.
from workflows.email_workflow_nodes.email_router_node import EmailRouterNode

spam = EmailCategory.SPAM
spam2 = EmailCategory("spam")
#junk = EmailCategory("junk")


# ---------
# load event 
# ---------

# let's grab the event and the webhook event created from nylas
# we will grab the event using its event id from the request/events folder 
event = EventLoader.load_event('1b8104b4-926c-11f0-9b32-7fc1f670b433')
#event = EventLoader.load_event('fce1a9be-926b-11f0-9b32-7fc1f670b433')  #nurse resume
print(f'this is the event: {event}')
webhook = WebhookEvent(**event)
#print(json.dumps(webhook.data, indent=2, ensure_ascii=False))
#email = EmailObject(**webhook.data['object'])
#print(event)
email: EmailObject = webhook.data['object']
print(f'\n the webhook: {webhook.model_dump_json(indent=2)}')
print(f'\n\nthe email: {email} \n')

# -------
# workflow
# -------

# the workflow validates the json event to the schema  so you can pass teh raw json event in 
workflow = EmailWorkflow()
result = workflow.run(event)
#print(f'\n result: {result} \n')
#print(f'\n the result: {result.nodes['ClassificationNode']['result'].output.category} \n')


#print(f'result: {result.model_dump_json(indent=2)} \n')
