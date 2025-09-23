from core.nodes.base import Node
from core.task import TaskContext
from dotenv import load_dotenv
import os
import logging

from schemas.nylas_email_schema import EmailObject
from services.nylas_service import NylasService

load_dotenv()

# this is often where you will write the logic 

class HandleSpamNode(Node):
    def process(self, task_context: TaskContext) -> TaskContext:
        # custom logic 
        nylas_service = NylasService()
        email_object = EmailObject(**task_context.event.data["object"])
        
        #nylas_service.delete_email(email_object)
        print(f'email deleted (not actually) \n')
        
        logging.info('in handle spam node \n\n')
        print(f'in handle spam node \n\n')
        return task_context