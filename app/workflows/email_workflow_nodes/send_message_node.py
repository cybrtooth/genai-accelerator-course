from core.nodes.base import Node
from core.task import TaskContext
from dotenv import load_dotenv
import os
import logging

from services.nylas_service import NylasService
from schemas.nylas_email_schema import EmailObject

load_dotenv()

# this is often where you will write the logic 

BODY = "this is a test reply email"

class SendMessageNode(Node):
    def process(self, task_context: TaskContext) -> TaskContext:
        # custom logic 
        
        nylas_service = NylasService()
        email_object = EmailObject(**task_context.event.data['object'])
        print(f'emailojb: {email_object} \n')
        email = email_object.from_[0].email
        print(f'email: {email}')
        nylas_service.send_email(grant_id=email_object.grant_id,
            to=[email],  # Wrap in list - send_email expects list[str]
            subject=email_object.subject,
            body=BODY,
            reply=True,
            reply_to_message_id=email_object.id)
        
        logging.info('in sending message node \n\n')
        print(f'in sending message node \n\n')
        return task_context