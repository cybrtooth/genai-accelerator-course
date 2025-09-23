from core.nodes.base import Node
from core.task import TaskContext
from dotenv import load_dotenv
import os
import logging

from schemas.nylas_email_schema import EmailObject, Sender

load_dotenv()

# this is often where you will write the logic 

class EmailFilterNode(Node):
    def process(self, task_context: TaskContext) -> TaskContext:
        # custom logic 
        email_object = EmailObject(**task_context.event.data["object"])
        print(f'\n email obj in node: {email_object}')
        print(f'\n this is the attachment: {email_object.attachments} \n\n')
        
        my_email = os.getenv('EMAIL')
        #sender = Sender()
        
        # Check if email is from myself
        sender: Sender = email_object.from_[0] if email_object.from_ else None
        
        if sender.email != my_email:
            # Use task_context to stop workflow, not email_object!
            task_context.stop_workflow(reason=f'Email is not from myself {my_email}, it is from {sender}')
            logging.info(f'Skipping email from {sender}')
            return task_context
        
        logging.info(f'Processing email from {sender}')
        return task_context