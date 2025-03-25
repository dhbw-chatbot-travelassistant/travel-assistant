from nicegui import ui

# Set the page to dark mode
ui.dark_mode()

# Create a container for the chatbot UI
with ui.column().classes('w-full h-screen justify-center items-center gap-4'):
    # Welcome message
    ui.label("Welcome to Travel Assistant").classes('text-2xl text-center text-white')

    # Chat display area
    chat_area = ui.column().classes('w-full max-w-lg h-96 p-4 bg-gray-800 rounded-lg overflow-y-auto shadow-md')

    # Input field and send button
    with ui.row().classes('w-full max-w-lg gap-2'):
        user_input = ui.input(placeholder="Type your message here...").classes('flex-grow')
        ui.button("Send", on_click=lambda: send_message(user_input.value)).classes('bg-blue-500 text-white')

# Function to handle sending messages
def send_message(message):
    if message.strip():
        chat_area.add(ui.label(f"You: {message}").classes('text-white'))
        user_input.value = ''  # Clear the input field
        # Add a placeholder response from the bot
        chat_area.add(ui.label("Bot: I'm here to assist you!").classes('text-gray-400'))

ui.run()