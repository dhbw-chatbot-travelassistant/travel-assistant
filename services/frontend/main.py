from nicegui import ui

widget_style = "bg-gray-800 text-white px-4 py-4 rounded-md"


# Global styles for iOS-like design
def apply_styles():
    ui.query("body").style("background-color: #121212; color: white;")
    ui.query(".chat-bubble").style("padding: 10px 15px; border-radius: 20px; max-width: 60%; display: inline-block;")

# Chat UI
def chat_interface():
    messages = []  # List to store chat messages

    with ui.column().classes("w-full h-screen items-center justify-center relative space-y-4"):
        # Title and subtitle
        ui.label("Tracy").classes("text-2xl font-bold text-center")
        ui.label("Your travel assistant").classes("text-sm text-gray-400 mb-4 text-center")

        # Prompt suggestion widgets
        with ui.column().classes("w-full max-w-6xl grid grid-cols-3 gap-4 bg-transparent p-4 rounded-lg"):
            ui.button("Find Flights", on_click=lambda: send_prompt("Find me flights to Paris")).classes(widget_style)
            ui.button("Book Hotels", on_click=lambda: send_prompt("Book a hotel in New York")).classes(widget_style)
            ui.button("Plan Itinerary", on_click=lambda: send_prompt("Plan a 3-day itinerary in Tokyo")).classes(widget_style)
            ui.button("Find Restaurants", on_click=lambda: send_prompt("Find restaurants in Rome")).classes(widget_style)
            ui.button("Check Weather", on_click=lambda: send_prompt("What's the weather in London?")).classes(widget_style)
            ui.button("Currency Exchange", on_click=lambda: send_prompt("What's the exchange rate for USD to EUR?")).classes(widget_style)

        # Chat container (initially hidden)
        chat_container = ui.column().classes("w-full max-w-6xl p-4 space-y-2 overflow-auto flex-1 bg-gray-800 rounded-lg mt-4").style("display: none;")

        def update_chat_container_visibility():
            """Show or hide the chat container based on the presence of messages."""
            if messages:
                chat_container.style("display: block;")
            else:
                chat_container.style("display: none;")

        def send_message():
            user_input = input_box.value
            if user_input:
                messages.append(user_input)  # Add message to the list
                with chat_container:
                    ui.label(user_input).classes("chat-bubble bg-blue-500 text-white self-end")
                    ui.label("Thinking...").classes("chat-bubble bg-gray-700 text-white self-start")
                input_box.set_value("")
                update_chat_container_visibility()
                ui.update()

        def send_prompt(prompt):
            messages.append(prompt)  # Add prompt to the list
            with chat_container:
                ui.label(f"You: {prompt}").classes("chat-bubble bg-blue-500 text-white self-end")
                ui.label("Thinking...").classes("chat-bubble bg-gray-700 text-white self-start")
            update_chat_container_visibility()
            ui.update()

        # Input box and send button
        with ui.row().classes("w-full max-w-6xl px-4 mx-auto bg-gray-700 text-white rounded-xl items-center px-3"):
            input_box = ui.input(placeholder="Start typing...").classes(
                "flex-grow bg-transparent border-none outline-none text-white"
            )
            ui.button("Send", on_click=send_message).classes("bg-blue-500 text-white px-4 py-2 rounded-lg ml-2")

apply_styles()
chat_interface()
ui.run()