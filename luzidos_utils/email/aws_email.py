from luzidos_utils.aws_io.s3 import read as s3_read

# PUBLIC FUNCTIONS
# THESE ARE CALLED BY ANDRES

def upload_unread_messages_to_s3(user_id, query):
    """Get messages from the user's mailbox.
    Uploads all of the unread messages to s3 in the format that I chose
    It also uploads all of its relevant attachments to s3
    It also applies ocr to the attachments and uploads the ocr data to s3
    Args:
        query: The query string used to filter messages.  read/unread
    Returns:
        A dictionary of messages.
    """
    pass
    # Pseudocode

    # Get the email
    # agent_email = s3_read.get_email(user_id)

    # Get the unread messages
    # unread_messages = amazone_ses.get_unread_messages(agent_email, query)

    # Upload the unread messages to s3
    # ask andres

    # Upload the attachments to s3
    # ask andres

    # Apply ocr to the attachments
    # ask andres

    # Upload the ocr data to s3
    # ask andres

    # return threads of the unread emails



def send_message(sender, to, subject, body, attachments=None, cc=None, thread_id=None, message_id=None):
    pass

def reply_to_message(thread_id, body, attachments=None, reply_all=False):
    pass


# PRIVATE FUNCTIONS
# THESE ARE HELPER FUNCTIONS THAT ARE CALLED BY THE PUBLIC FUNCTIONS

if __name__ == "__main__":
    pass
    # Example usage
    # upload_unread_messages_to_s3("123", "unread")
    # send_message("me", "you", "hello", "world")
    # reply_to_message("123", "hello")  