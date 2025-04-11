from nicegui import ui
import httpx

theme = {'mode': 'dark'}

def apply_styles():
    if theme['mode'] == 'dark':
        ui.query("body").style(
            "background-color: #1e1e1e; color: white; margin: 0; font-family: 'Segoe UI', sans-serif;")
    else:
        ui.query("body").style(
            "background-color: #f4f4f4; color: black; margin: 0; font-family: 'Segoe UI', sans-serif;")


def get_background_style():
    if theme['mode'] == 'dark':
        return (
            "height: 75vh;"
            "background-image: url('https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?auto=format&fit=crop&w=1950&q=80');"
            "background-blend-mode: overlay;"
            "background-color: rgba(0,0,0,0.6);"
        )
    else:
        return (
            "height: 75vh;"
            "background-image: url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1950&q=80');"
            "background-blend-mode: overlay;"
            "background-color: rgba(255,255,255,0.6);"
        )


def chat_interface(backend_url: str):
    messages = []
    thinking_label = None

    apply_styles()

    with ui.column().classes("w-full h-screen items-center justify-between relative") as main_layout:
        with ui.row().classes("justify-between items-center w-full px-6 mt-4 max-w-4xl"):
            ui.label("✈️ Tracy – Your Travel Assistant").classes(
                "text-2xl font-bold")
            ui.button("🌓 Toggle Theme", on_click=lambda: switch_theme(
                chat_container)).classes("text-sm bg-gray-600 text-white px-3 py-1 rounded")

        chat_container = ui.column().classes(
            "w-full max-w-4xl px-4 py-4 space-y-2 overflow-auto flex-1 bg-cover bg-center rounded-xl mb-2"
        ).style(get_background_style())

        async def send_message():
            user_input = input_box.value.strip()
            if not user_input:
                return

            input_box.set_value("")

            with chat_container:
                with ui.row().classes("justify-end w-full"):
                    ui.label(user_input).classes(
                        "bg-blue-500 text-white px-4 py-2 rounded-xl max-w-md self-end shadow-md")

            ui.update()
            ui.run_javascript("window.scrollTo(0, document.body.scrollHeight)")

            nonlocal thinking_label
            with chat_container:
                with ui.row().classes("justify-start w-full"):
                    thinking_label = ui.label("...").classes(
                        "bg-gray-700 text-white px-4 py-2 rounded-xl max-w-md self-start shadow-md")

            ui.update()

            response = await send_to_backend(user_input)
            thinking_label.set_text(response or "Sorry, no response.")
            ui.run_javascript("window.scrollTo(0, document.body.scrollHeight)")

        async def send_to_backend(user_prompt):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(backend_url, json={"user_prompt": user_prompt}, timeout=(10, 30))
                    if response.status_code == 200:
                        return response.json().get("answer", "No response from backend.")
                    else:
                        return f"Error: HTTP {response.status_code} - {response.text}"
            except Exception as e:
                return f"Error: {repr(e)}"

        with ui.row().classes(
            "w-full max-w-4xl px-4 py-2 rounded-t-xl items-center fixed bottom-0"
        ).style("background-color: #2c2c2c;" if theme['mode'] == 'dark' else "background-color: #ffffff;"):

            input_style = (
                "background-color: white; color: white; border: 1px solid #ccc; padding: 8px;"
                if theme['mode'] == 'light'
                else "background-color: #2c2c2c; color: white; border: none; padding: 8px;"
            )

            input_box = ui.input(placeholder="Type your message...") \
                .props("rounded filled dense input-class=text-white") \
                .classes("w-full") \
                .style("background-color: rgba(255,255,255,0.1); border: 1px solid #ccc; padding: 8px;")

            # ENTER senden
            input_box.on("keydown.enter", lambda e: send_message())

            ui.button("Send", on_click=send_message).classes(
                "bg-blue-600 text-white rounded px-4 py-2 ml-2")

    return chat_container


def switch_theme(chat_container):
    theme['mode'] = 'light' if theme['mode'] == 'dark' else 'dark'
    apply_styles()
    chat_container.style(get_background_style())
    ui.update()

# Main entry point

if __name__ in {"__main__", "__mp_main__"}:

    # get first argument from command line
    import sys
    if len(sys.argv) > 1:
        backend_url = sys.argv[1]
        chat_interface(backend_url)
        ui.run(port=8082)
    else:
        # raise an error if no argument is provided
        raise ValueError("Please provide the backend URL as an argument.")
