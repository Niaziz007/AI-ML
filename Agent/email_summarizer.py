import imaplib
import email
import os
import getpass
from email.header import decode_header
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
import openai
from transformers import pipeline
import configparser
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailSummarizer:
    def __init__(self, config_file='config.ini'):
        """Initialize the email summarizer with configuration."""
        self.config = configparser.ConfigParser()
        
        # Create config if it doesn't exist
        if not os.path.exists(config_file):
            self._create_default_config(config_file)
            
        self.config.read(config_file)
        self.email_account = "haseebkhan2@carecloud.com"
        self.imap_server = self.config['Email']['imap_server']
        self.summarization_method = self.config['Summarization']['method']
        
        # Download NLTK resources if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            
        if self.summarization_method == 'openai':
            openai.api_key = self.config['Summarization']['openai_api_key']
        elif self.summarization_method == 'transformer':
            self.summarizer = pipeline("summarization")
            
    def _create_default_config(self, config_file):
        """Create a default configuration file."""
        self.config['Email'] = {
            'imap_server': 'imap.carecloud.com',  # Try the domain-specific server first
            'imap_port': '993',
            'email_folder': 'INBOX',
            'use_app_password': 'false'
        }
        
        self.config['Summarization'] = {
            'method': 'extractive',  # Options: extractive, transformer, openai
            'openai_api_key': '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',  # Replace with your OpenAI API key
            'max_emails': '10',
            'summary_length': '3'  # sentences for extractive
        }
        
        with open(config_file, 'w') as f:
            self.config.write(f)
        
        logger.info(f"Created default configuration file: {config_file}")
        logger.info("Please edit it with your credentials and preferences.")
    
    def connect(self):
        """Connect to the email server."""
        try:
            # Print server info for debugging
            logger.info(f"Connecting to IMAP server: {self.imap_server}")
            
            password = getpass.getpass(f"Enter password for {self.email_account}: ")
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            
            # Set debugging level to see detailed IMAP communication
            self.mail.debug = 4
            
            logger.info(f"Attempting login for: {self.email_account}")
            self.mail.login(self.email_account, password)
            
            logger.info("Login successful")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP4 error: {str(e)}")
            if "LOGIN failed" in str(e):
                logger.error("Authentication failed. If using Microsoft 365, you may need to:")
                logger.error("1. Enable IMAP access for your account")
                logger.error("2. Create an app-specific password if MFA is enabled")
                logger.error("3. Check if your organization allows IMAP access")
            return False
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return False
    
    def get_emails(self, folder="INBOX", limit=10):
        """Fetch recent emails from specified folder."""
        try:
            self.mail.select(folder)
            status, messages = self.mail.search(None, "ALL")
            email_ids = messages[0].split()
            
            # Get the most recent emails (up to limit)
            start_idx = max(0, len(email_ids) - limit)
            recent_email_ids = email_ids[start_idx:]
            
            emails = []
            for e_id in tqdm(reversed(recent_email_ids), desc="Fetching emails"):
                status, data = self.mail.fetch(e_id, "(RFC822)")
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                subject = self._decode_subject(msg["Subject"])
                from_addr = msg["From"]
                date = msg["Date"]
                
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            try:
                                body = part.get_payload(decode=True).decode()
                                break
                            except:
                                pass
                else: 
                    try:
                        body = msg.get_payload(decode=True).decode()
                    except:
                        body = "Could not decode message body"
                
                emails.append({
                    "subject": subject,
                    "from": from_addr,
                    "date": date,
                    "body": body
                })
                
            return emails
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            return []
    
    def _decode_subject(self, subject):
        """Decode email subject."""
        if not subject:
            return ""
        decoded_headers = decode_header(subject)
        subject_parts = []
        for content, encoding in decoded_headers:
            if isinstance(content, bytes):
                if encoding:
                    try:
                        content = content.decode(encoding)
                    except:
                        content = content.decode('utf-8', errors='replace')
                else:
                    content = content.decode('utf-8', errors='replace')
            subject_parts.append(content)
        return " ".join(subject_parts)
    
    def summarize(self, emails):
        """Summarize email content using the configured method."""
        summarized_emails = []
        
        for email_data in tqdm(emails, desc="Summarizing emails"):
            body = email_data["body"].strip()
            summary = ""
            
            if not body:
                summary = "No content to summarize"
            elif self.summarization_method == "extractive":
                summary = self._extractive_summary(body)
            elif self.summarization_method == "transformer":
                summary = self._transformer_summary(body)
            elif self.summarization_method == "openai":
                summary = self._openai_summary(body)
            
            summarized_emails.append({
                "subject": email_data["subject"],
                "from": email_data["from"],
                "date": email_data["date"],
                "summary": summary
            })
            
        return summarized_emails
    
    def _extractive_summary(self, text):
        """Create an extractive summary using NLTK."""
        try:
            sentences = sent_tokenize(text)
            summary_length = min(int(self.config['Summarization']['summary_length']), len(sentences))
            
            if summary_length <= 0:
                return "Text too short to summarize"
                
            # Simple approach: return first few sentences as summary
            return " ".join(sentences[:summary_length])
        except Exception as e:
            logger.error(f"Extractive summarization error: {str(e)}")
            return "Summarization failed"
    
    def _transformer_summary(self, text):
        """Create a summary using Hugging Face transformers."""
        try:
            # Truncate input if too long
            max_length = 1024
            if len(text) > max_length:
                text = text[:max_length]
                
            result = self.summarizer(text, max_length=150, min_length=30, do_sample=False)
            return result[0]['summary_text']
        except Exception as e:
            logger.error(f"Transformer summarization error: {str(e)}")
            return "Transformer summarization failed"
    
    def _openai_summary(self, text):
        """Create a summary using OpenAI API."""
        try:
            # Truncate text if too long
            max_tokens = 4000
            if len(text) > max_tokens * 4:  # Approximate token count
                text = text[:max_tokens * 4]
                
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an email summarization assistant."},
                    {"role": "user", "content": f"Summarize this email concisely:\n\n{text}"}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI summarization error: {str(e)}")
            return "OpenAI summarization failed"
    
    def display_summaries(self, summarized_emails):
        """Display email summaries in a formatted way."""
        print("\n" + "="*80)
        print(f"EMAIL SUMMARIES FOR: {self.email_account}")
        print("="*80)
        
        for i, email_data in enumerate(summarized_emails, 1):
            print(f"\nEMAIL {i}:")
            print(f"From: {email_data['from']}")
            print(f"Date: {email_data['date']}")
            print(f"Subject: {email_data['subject']}")
            print("-"*40)
            print(f"Summary:\n{email_data['summary']}")
            print("-"*80)
    
    def close(self):
        """Close the email connection."""
        if hasattr(self, 'mail'):
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass

def main():
    summarizer = EmailSummarizer()
    if summarizer.connect():
        max_emails = int(summarizer.config['Summarization']['max_emails'])
        emails = summarizer.get_emails(limit=max_emails)
        if emails:
            summarized = summarizer.summarize(emails)
            summarizer.display_summaries(summarized)
        else:
            print("No emails found to summarize.")
    summarizer.close()

if __name__ == "__main__":
    main()