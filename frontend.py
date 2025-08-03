import json
import asyncio
import websockets
from nicegui import ui, app

ws = None
input_box = None
chat_container = None

# Connect to WebSocket
async def connect_to_ws():
    global ws
    ws = await websockets.connect("ws://localhost:8000/ws", ping_interval=30, ping_timeout=30)
    asyncio.create_task(receive_messages())

# Display Chat Message with Emoji
def display_chat_message(icon: str, name: str, text: str, sent: bool):
    with ui.row().classes('w-full items-start' + (' justify-end' if sent else '')):
        if not sent:
            ui.label(icon).classes('text-2xl mr-2')
        with ui.column().classes('max-w-[75%]'):
            ui.label(name).classes('text-xs text-gray-500 mb-1 ml-1' if not sent else 'text-xs text-gray-400 mb-1 mr-1 text-right')
            ui.label(text).classes(
    'p-3 rounded-xl text-sm leading-snug break-words whitespace-pre-wrap ' +
    ('bg-blue-100 text-gray-800 self-end' if sent else 'bg-green-200 text-black')
)
        if sent:
            ui.label(icon).classes('text-2xl ml-2')

    # Scroll to bottom
    ui.run_javascript("""
        const box = document.getElementById('chat-box');
        if (box) {
            setTimeout(() => box.scrollTop = box.scrollHeight, 50);
        }
    """)

# Get Emoji for Role
def get_icon_for_role(role: str) -> str:
    return {
        "Request_Gatherer": "🤖",
        "Product_Finder": "🔍",
        "Doubt_Solver": "🧠"
    }.get(role, "🧾")

# Receive Messages
async def receive_messages():
    global ws, chat_container
    try:
        async for message in ws:
            with chat_container:
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    display_chat_message("🖥️", "Server", message, sent=False)
                    continue

                # Product List
                if isinstance(data, list) and all('url' in item for item in data):
                    for product in data:
                        with ui.card().classes("max-w-xl bg-white shadow-md rounded-xl p-4 border"):
                            ui.label(product["title"]).classes("text-lg font-semibold text-gray-900")
                            ui.label(f"₹{product['price']}").classes("text-base text-green-700 font-bold")
                            ui.label(product["summary_review"]).classes("text-sm text-gray-600 mt-1")
                            ui.label(product["details"]).classes("text-xs text-gray-500 mt-1 line-clamp-3")
                            ui.button("View Product", on_click=lambda url=product['url']: ui.navigate.to(url, new_tab=True)) \
                                .props('outline').classes("mt-3 text-blue-600")
                        ui.run_javascript("""
                            const box = document.getElementById('chat-box');
                            if (box) {
                                setTimeout(() => box.scrollTop = box.scrollHeight, 50);
                            }
                        """)
                # Role-based Messages
                elif isinstance(data, dict) and "role" in data:
                    role_map = {
                        "Request_Gatherer": "🤖 Gatherer",
                        "Product_Finder": "🔍 Finder",
                        "Doubt_Solver": "🧠 Solver"
                    }
                    display_name = role_map.get(data["role"], data["role"])
                    display_chat_message(get_icon_for_role(data["role"]), display_name, data["text"], sent=False)

                else:
                    display_chat_message("🖥️", "Server", str(data), sent=False)

    except websockets.exceptions.ConnectionClosed:
        with chat_container:
            display_chat_message("⚠️", "System", "Connection closed", sent=False)

# Send Message
async def send_message():
    global input_box, chat_container
    if ws and input_box.value.strip():
        msg = input_box.value.strip()
        with chat_container:
            display_chat_message("🙂", "You", msg, sent=True)
        await ws.send(msg)
        input_box.value = ""

# UI Page
@ui.page("/")
def main_page():
    global input_box, chat_container

    with ui.column().classes('w-full h-screen bg-gray-100 p-6 items-center justify-center'):
        with ui.card().classes('w-full max-w-4xl h-full shadow-2xl bg-white rounded-2xl flex flex-col p-6'):
            ui.label("🤖 Doraemon Assistant").classes("text-3xl font-bold text-center text-blue-800 mb-4")

            chat_container = ui.column().classes('flex-1 overflow-y-auto space-y-3 px-2').props('id=chat-box')

            with ui.row().classes('mt-4 w-full items-center gap-3'):
                input_box = ui.input(placeholder='Type your message...').props('rounded outlined').classes('flex-1')

                # Send message on Enter key press
                input_box.on('keydown.enter', lambda e: send_message())

                ui.button("Send", on_click=send_message).props('rounded').classes('bg-blue-600 text-white px-4 py-2')

app.on_startup(connect_to_ws)
ui.run()
