#!/usr/bin/env python3
"""
Add a simple endpoint to manually send messages via the server
Add this to your main.py file
"""

# Add this to your main.py file:

"""
@app.post("/send-test-message")
async def send_test_message():
    '''Send a test message to Waldo manually'''
    
    try:
        # Waldo's number from the logs
        phone_number = "56940035815@s.whatsapp.net"
        message = "🤖 Manual test message from alarm system server!"
        
        print(f"📤 Manual send request to {phone_number}")
        success = await whatsapp_service.send_text_message(phone_number, message)
        
        if success:
            return {"status": "success", "message": "Message sent to Waldo"}
        else:
            return {"status": "error", "message": "Failed to send message"}
            
    except Exception as e:
        print(f"❌ Manual send error: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/send-test-message")  
async def send_test_message_get():
    '''Send a test message via GET request (easier to test in browser)'''
    return await send_test_message()
"""

print("Add the above code to your main.py file, then you can:")
print("1. Deploy the update")
print("2. Visit: https://whatsapp-sonoff-automation.onrender.com/send-test-message")
print("3. This will send a message directly through the server's WHAPI connection")