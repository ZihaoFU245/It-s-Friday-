import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from backend.modules import GmailClient

gm = GmailClient()
msgs = gm.list_messages(1)
print("Gmails: ", msgs)
id = msgs[0].get('id')
em = gm.get_message(id)
print(em)

