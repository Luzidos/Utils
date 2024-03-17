import requests

def update_invoice_status(user_id, invoice_id, status):
    url = 'https://b7843zphhl.execute-api.us-west-2.amazonaws.com/prod'  # Use the actual URL here
    headers = {
        'x-api-key': 'CVsju5YkVA68kGdcAATjL6GjXxdYbxjr6Nhp9L2L'  # Replace YOUR_API_KEY_HERE with your actual API key
    }
    body = {
        "operation": "m.odify",
        "data": {
            "userID": user_id,
            "invoiceID": invoice_id,
            "statusOfTransaction": status
        }
    }
    
    response = requests.post(url, json=body, headers=headers)
    
    if response.status_code == 200:
        return 'Entry status updated successfully'
    else:
        # Handle potential error cases here depending on how you want to deal with them
        return 'Error updating entry status', response.status_code
