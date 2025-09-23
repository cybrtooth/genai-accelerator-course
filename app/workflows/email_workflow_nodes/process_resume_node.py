from core.nodes.base import Node
from core.task import TaskContext
from dotenv import load_dotenv
import os
import logging
import re
import requests

from services.nylas_service import NylasService
from schemas.nylas_email_schema import Attachment, EmailObject

load_dotenv()

# this is often where you will write the logic 

class ProcessResumeNode(Node):
    def process(self, task_context: TaskContext) -> TaskContext:
        # custom logic 
        nylas_service = NylasService()
        email_object = EmailObject(**task_context.event.data['object'])
        
        documents_found = []
        
        # Define common document MIME types for resumes
        document_types = [
            'application/pdf',
            'application/msword',  # .doc
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
            'application/rtf',  # .rtf
            'text/plain',  # .txt (sometimes used for resumes)
        ]
        
        document_extensions = ['.pdf', '.doc', '.docx', '.rtf', '.txt']
        
        # Strategy 1: Download all non-inline document attachments
        # Since ClassificationNode already identified this as a resume email,
        # any document attachment is likely the resume
        document_attachments = [
            att for att in email_object.attachments 
            if (att.content_type in document_types or 
                (att.filename and any(att.filename.lower().endswith(ext) for ext in document_extensions)))
            and not att.is_inline  # Exclude inline attachments (signatures, logos)
        ]
        
        if document_attachments:
            print(f"Found {len(document_attachments)} document attachment(s)")
            for doc_attachment in document_attachments:
                # Temporarily modify the email object to have only this attachment
                temp_email = email_object.model_copy()
                temp_email.attachments = [doc_attachment]
                
                attachment = nylas_service.download_attachment(temp_email, download=True)
                print(f'Document downloaded: {attachment["filename"]}')
                documents_found.append({
                    'type': 'attachment',
                    'filename': attachment["filename"],
                    'content': attachment
                })
        
        # Strategy 2: Detect cloud storage links in email body
        # Using more general patterns for common cloud storage services
        cloud_patterns = [
            # Microsoft SharePoint/OneDrive
            r'https://[^\s"\'<>]*(?:sharepoint\.com|1drv\.ms|onedrive\.live\.com)[^\s"\'<>]*',
            # Google Drive
            r'https://(?:drive|docs)\.google\.com[^\s"\'<>]*',
            # Dropbox
            r'https://(?:www\.)?dropbox\.com[^\s"\'<>]*',
            # Box
            r'https://[^\s"\'<>]*\.box\.com[^\s"\'<>]*',
            # iCloud
            r'https://(?:www\.)?icloud\.com[^\s"\'<>]*',
        ]
        
        cloud_links = []
        for pattern in cloud_patterns:
            matches = re.findall(pattern, email_object.body, re.IGNORECASE)
            cloud_links.extend(matches)
        
        if cloud_links:
            print(f"Found {len(cloud_links)} cloud storage link(s)")
            for link in cloud_links:
                # Clean up the link (remove any trailing HTML artifacts)
                clean_link = re.split(r'["\'>]', link)[0]
                print(f"Found cloud document link: {clean_link}")
                
                # Try to extract a filename from nearby text or use generic name
                # Look for text that looks like a filename near the link
                link_context = email_object.body[max(0, email_object.body.find(link)-100):email_object.body.find(link)+100]
                filename_pattern = r'>([^<>]+(?:\.pdf|\.doc|\.docx|\.rtf|\.txt))</a>'
                filename_match = re.search(filename_pattern, link_context, re.IGNORECASE)
                
                if filename_match:
                    filename = filename_match.group(1)
                else:
                    # Use a generic name based on the service
                    if 'sharepoint' in clean_link.lower() or 'onedrive' in clean_link.lower():
                        filename = "document_from_sharepoint.pdf"
                    elif 'google' in clean_link.lower():
                        filename = "document_from_gdrive.pdf"
                    elif 'dropbox' in clean_link.lower():
                        filename = "document_from_dropbox.pdf"
                    else:
                        filename = "document_from_cloud.pdf"
                
                documents_found.append({
                    'type': 'cloud_link',
                    'filename': filename,
                    'url': clean_link
                })
                
                # Note: Actual download would require API authentication
                print(f"Note: Cloud storage link detected. Integration with {clean_link.split('/')[2]} API required for automatic download.")
        
        if not documents_found:
            print("No documents found in email (checked attachments and cloud links)")
            logging.warning("No documents found in resume email")
        else:
            print(f"\nTotal documents found: {len(documents_found)}")
            for doc in documents_found:
                print(f"  - {doc['filename']} (type: {doc['type']})")
                
                # If it's a cloud link, try to download it
                if doc['type'] == 'cloud_link':
                    try:
                        print(f"Attempting to download from: {doc['url']}")
                        response = requests.get(doc['url'], allow_redirects=True, timeout=30)
                        if response.status_code == 200:
                            # Save the file
                            with open(doc['filename'], 'wb') as f:
                                f.write(response.content)
                            print(f"Successfully downloaded: {doc['filename']}")
                        else:
                            print(f"Failed to download (HTTP {response.status_code}). May require authentication.")
                    except Exception as e:
                        print(f"Could not download cloud file: {e}")
                        print("File may require authentication or special permissions.")
        
        # TODO: Store documents in OneDrive or SharePoint
        
        # Store document info in task context for downstream nodes
        task_context.update_node(
            node_name=self.node_name, 
            result={'documents_found': documents_found}
        )
        
        print(f'ProcessResumeNode completed - found {len(documents_found)} document(s)')
        logging.info(f'Processed {len(documents_found)} document(s)\n\n')
        return task_context