import cohere 
co = cohere.Client('MLZXavfC2EpNaW3dYRG5KwWPcMIvBUyabF1DPBgw') # This is your trial API key
response = co.chat( 
  message='What are the recent happenings in Ukraine?',
  prompt_truncation='auto',
  connectors=[{"id": "web-search"}]
) 
print(response)