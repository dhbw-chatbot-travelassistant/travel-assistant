from nicegui import ui
import httpx  # Import HTTP client for API calls

MOCK_API_URL = "http://127.0.0.1:8080/mock/backend/getResponse"  # Mock backend route

widget_style = "bg-gray-800 text-white px-4 py-4 rounded-md"

# Global styles for iOS-like design
def apply_styles():
    ui.query("body").style("background-color: #121212; color: white;")
    ui.query(".chat-bubble").style("padding: 10px 15px; border-radius: 20px; max-width: 60%; display: inline-block;")

# Chat UI
def chat_interface():
    messages = []  # List to store chat messages
    thinking_label = None  # To store the "thinking" message widget reference

    with ui.column().classes("w-full h-screen items-center justify-center relative space-y-4"):
        # Title and subtitle
        ui.label("Tracy").classes("text-2xl font-bold text-center")
        ui.label("Your travel assistant").classes("text-sm text-gray-400 mb-4 text-center")

        # Chat container (initially hidden)
        chat_container = ui.column().classes("w-full max-w-6xl p-4 space-y-2 overflow-auto flex-1 bg-gray-800 rounded-lg mt-4").style("display: none;")

        def update_chat_container_visibility():
            """Show or hide the chat container based on the presence of messages."""
            if messages:
                chat_container.style("display: block;")
            else:
                chat_container.style("display: none;")

        async def send_message():
            user_input = input_box.value.strip()
            if user_input:
                messages.append(user_input)  # Add message to the list
                with chat_container:
                    ui.label(user_input).classes("chat-bubble bg-blue-500 text-white self-end")  # User message
                    nonlocal thinking_label
                    thinking_label = ui.label("Thinking...").classes("chat-bubble bg-gray-700 text-white self-start")  # Placeholder for response

                input_box.set_value("")  # Clear input box
                update_chat_container_visibility()  # Show chat container after message is sent
                ui.update()

                # Send user input to mock backend
                response = await send_to_backend(user_input)

                # Update UI with mock backend response
                if response:
                    thinking_label.set_text(response)  # Replace "Thinking..." with real response
                else:
                    thinking_label.set_text("Sorry, I couldn't get a response.")  # Handle errors

                ui.update()

        async def send_to_backend(user_prompt):
            """Send a GET request to the mock backend and return the response."""
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(MOCK_API_URL, params={"user_prompt": user_prompt}, timeout=10.0)
                    if response.status_code == 200:
                        return response.json().get("answer", "No response from backend.")
                    else:
                        return f"Error: {response.status_code}"
            except Exception as e:
                return f"Error: {str(e)}"

        # Input box and send button
        with ui.row().classes("w-full max-w-6xl px-4 mx-auto bg-gray-700 text-white rounded-xl items-center px-3"):
            input_box = ui.input(placeholder="Start typing...").classes(
                "flex-grow bg-transparent border-none outline-none text-white"
            )
            ui.button("Send", on_click=send_message).classes("bg-blue-500 text-white px-4 py-2 rounded-lg ml-2")

apply_styles()
chat_interface()
ui.run(port=8082)
