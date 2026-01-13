from __future__ import annotations

import re
from dataclasses import dataclass, field
from uuid import UUID
from typing import cast

from attp_client.client import ATTPClient
from attp_client.interfaces.inference.enums.message_type import MessageTypeEnum
from attp_client.interfaces.inference.message import IMessageDTOV2
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, VSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.widgets import Frame, TextArea

from agenthub.copilot.tools import CopilotTools


@dataclass(frozen=True)
class _ChatEntry:
    id: UUID
    name: str


@dataclass
class _CopilotSession:
    name: str
    chat_id: UUID


@dataclass
class _CopilotState:
    mode: str = "roam"
    chats: list[_ChatEntry] = field(default_factory=list)
    selected_index: int = 0
    session: _CopilotSession | None = None
    messages: dict[UUID, list[tuple[str, str]]] = field(default_factory=dict)

    def current_chat_id(self) -> UUID | None:
        return self.session.chat_id if self.session else None

    def current_messages(self) -> list[tuple[str, str]]:
        chat_id = self.current_chat_id()
        if not chat_id:
            return []
        return self.messages.setdefault(chat_id, [])


class _CopilotTUI:
    def __init__(self, state: _CopilotState) -> None:
        self.state = state
        self.sidebar = TextArea(read_only=True, scrollbar=True)
        self.chat_area = TextArea(read_only=True, scrollbar=True)
        self.input_area = TextArea(height=5, multiline=True)
        self.status_control = FormattedTextControl(text="")

        self.sidebar_frame = Frame(self.sidebar, title="Copilot Sessions")
        self.chat_frame = Frame(self.chat_area, title="Agent Copilot")
        self.input_frame = Frame(self.input_area, title="Input")

        self.root = VSplit(
            [
                self.sidebar_frame,
                HSplit(
                    [
                        self.chat_frame,
                        self.input_frame,
                        Window(height=1, content=self.status_control),
                    ],
                    padding=0,
                ),
            ],
            padding=1,
            width=None,
        )

    def build_layout(self) -> Layout:
        return Layout(self.root, focused_element=self.sidebar)

    def set_mode(self, mode: str) -> None:
        self.state.mode = mode
        if mode == "insert":
            self.input_area.read_only = False
        else:
            self.input_area.read_only = True

    def update_sidebar(self) -> None:
        lines: list[str] = []
        if not self.state.chats:
            lines.append("No chats found.")
        else:
            for idx, chat in enumerate(self.state.chats):
                prefix = ">" if idx == self.state.selected_index else " "
                lines.append(f"{prefix} {idx + 1:>2}. {chat.name}")
        lines.append("")
        lines.append("Esc: roam | Enter: insert")
        lines.append("Tab: next pane | /exit to quit")
        lines.append("/refresh, /select <n>, /new <name>")
        self.sidebar.text = "\n".join(lines)

    def update_chat(self) -> None:
        lines: list[str] = []
        for role, message in self.state.current_messages()[-300:]:
            lines.append(f"{role}: {message}")
        if not lines:
            lines.append("Start the conversation below.")
        self.chat_area.text = "\n".join(lines)
        # Auto-scroll to the bottom for the latest messages.
        self.chat_area.buffer.cursor_position = len(self.chat_area.text)

    def update_status(self) -> None:
        active = self.state.session.name if self.state.session else "none"
        self.status_control.text = f"mode={self.state.mode} | chat={active}"

    def refresh(self) -> None:
        self.update_sidebar()
        self.update_chat()
        self.update_status()


def _append_tool_messages(
    messages: list[tuple[str, str]], response: IMessageDTOV2
) -> None:
    if response.tool_called:
        messages.append(("system", f"[tool] {response.tool_called.name}"))
    if response.tool_status:
        messages.append(("system", f"[tool-status] {response.tool_status}"))
    if response.tool_started_input:
        messages.append(("system", f"[tool-input] {response.tool_started_input}"))
    if response.tool_finished_output:
        messages.append(("system", f"[tool-output] {response.tool_finished_output}"))
    if response.tool_error_detail:
        messages.append(("system", f"[tool-error] {response.tool_error_detail}"))


async def run_copilot_tui(
    client: ATTPClient,
    agent_name: str,
    chat_name: str | None = None,
) -> None:
    tools = CopilotTools(client)
    await tools.attach_all()

    async def _fetch_chats() -> list[_ChatEntry]:
        try:
            response = await client.chats.get_chats()
            return [
                _ChatEntry(id=getattr(chat, "id"), name=getattr(chat, "name", ""))
                for chat in response.items
            ]  # type: ignore[arg-type]
        except Exception:
            return []

    async def _create_chat(name: str) -> _ChatEntry:
        chat_response = await client.inference.create_chat(
            name=name,
            agent_name=agent_name,
        )
        return _ChatEntry(id=UUID(str(chat_response["id"])), name=name)

    chats = await _fetch_chats()

    selected_chat: _ChatEntry | None = None
    if chat_name:
        selected_chat = await _create_chat(chat_name)
        chats = [c for c in chats if c.id != selected_chat.id]
        chats.insert(0, selected_chat)
    else:
        if chats:
            selected_chat = chats[0]
        else:
            selected_chat = await _create_chat("Agent Copilot Session")
            chats.append(selected_chat)

    chat_id = selected_chat.id
    selected_index = next((idx for idx, c in enumerate(chats) if c.id == chat_id), 0)

    state = _CopilotState(
        chats=chats,
        selected_index=selected_index,
        session=_CopilotSession(name=selected_chat.name, chat_id=chat_id),
    )
    ui = _CopilotTUI(state)
    ui.set_mode("roam")
    ui.refresh()

    async def _switch_session(chat: _ChatEntry) -> None:
        state.session = _CopilotSession(name=chat.name, chat_id=chat.id)
        state.selected_index = next((idx for idx, c in enumerate(state.chats) if c.id == chat.id), 0)
        state.messages.setdefault(chat.id, [])
        ui.refresh()

    async def _refresh_chats(preserve_selection: bool = True) -> None:
        fetched = await _fetch_chats()
        if fetched:
            state.chats = fetched
        if preserve_selection and state.session and not any(c.id == state.session.chat_id for c in state.chats):
            state.chats.insert(0, _ChatEntry(id=state.session.chat_id, name=state.session.name))
        if preserve_selection and state.session:
            for idx, chat in enumerate(state.chats):
                if chat.id == state.session.chat_id:
                    state.selected_index = idx
                    break
        ui.refresh()

    async def _create_and_switch(name: str) -> None:
        new_chat = await _create_chat(name)
        state.chats = [c for c in state.chats if c.id != new_chat.id]
        state.chats.insert(0, new_chat)
        await _switch_session(new_chat)

    async def _handle_command(text: str) -> bool:
        lower = text.lower()
        if lower == "/refresh":
            await _refresh_chats()
            return True
        if lower.startswith("/select"):
            match = re.match(r"/select\s+(\d+)", text)
            if match:
                idx = int(match.group(1)) - 1
                if 0 <= idx < len(state.chats):
                    await _switch_session(state.chats[idx])
            return True
        if lower.startswith("/new"):
            name = text.split(" ", 1)[1].strip() if " " in text else "Agent Copilot Session"
            await _create_and_switch(name or "Agent Copilot Session")
            return True
        return False

    async def _stream_response(app, user_text: str) -> None:
        if not state.session:
            return

        message = IMessageDTOV2(
            content=user_text,
            message_type=MessageTypeEnum.USER_MESSAGE,
            chat_id=state.session.chat_id,
        )

        try:
            response = await client.inference.invoke_chat_inference(
                messages=[message],
                chat_id=state.session.chat_id,
                timeout=20000,
                stream=True,
            )

            if hasattr(response, "__aiter__"):
                state.current_messages().append(("copilot", ""))
                reply_index = len(state.current_messages()) - 1

                async for chunk in response:  # type: ignore[operator]
                    _append_tool_messages(state.current_messages(), chunk)
                    content = chunk.content if isinstance(chunk.content, str) else str(chunk.content or "")
                    if content:
                        role, existing = state.current_messages()[reply_index]
                        state.current_messages()[reply_index] = (role, existing + content)
                    ui.refresh()
                    app.invalidate()
                return

            resp_msg = cast(IMessageDTOV2, response)
            _append_tool_messages(state.current_messages(), resp_msg)
            reply = resp_msg.content if isinstance(resp_msg.content, str) else str(resp_msg.content)
            state.current_messages().append(("copilot", reply))
        except Exception as exc:
            state.current_messages().append(("copilot", f"Error: {exc}"))
        finally:
            ui.refresh()
            app.invalidate()

    kb = KeyBindings()

    @kb.add("escape")
    def _to_roam(event) -> None:
        ui.set_mode("roam")
        event.app.layout.focus(ui.sidebar)
        ui.refresh()
        event.app.invalidate()

    @kb.add("c-c")
    @kb.add("c-q")
    def _quit(event) -> None:
        event.app.exit()

    @kb.add("tab")
    def _focus_next(event) -> None:
        event.app.layout.focus_next()

    @kb.add("s-tab")
    def _focus_prev(event) -> None:
        event.app.layout.focus_previous()

    @kb.add("up")
    def _move_up(event) -> None:
        if event.app.layout.current_control == ui.sidebar.control:
            state.selected_index = max(0, state.selected_index - 1)
            ui.refresh()
            event.app.invalidate()

    @kb.add("down")
    def _move_down(event) -> None:
        if event.app.layout.current_control == ui.sidebar.control:
            state.selected_index = min(len(state.chats) - 1, state.selected_index + 1)
            ui.refresh()
            event.app.invalidate()

    @kb.add("enter")
    async def _enter(event) -> None:
        if state.mode == "insert":
            text = ui.input_area.text.strip()
            if not text:
                return
            if text.lower() in {"/exit", "/quit"}:
                event.app.exit()
                return
            if text.startswith("/"):
                if await _handle_command(text):
                    ui.input_area.text = ""
                    ui.refresh()
                    event.app.invalidate()
                return
            if not state.session:
                state.current_messages().append(("system", "No chat selected."))
                ui.refresh()
                event.app.invalidate()
                return
            ui.input_area.text = ""
            state.current_messages().append(("you", text))
            ui.refresh()
            event.app.invalidate()
            await _stream_response(event.app, text)
            return

        if event.app.layout.current_control == ui.sidebar.control:
            if 0 <= state.selected_index < len(state.chats):
                selected = state.chats[state.selected_index]
                await _switch_session(selected)
                event.app.invalidate()
                return

        ui.set_mode("insert")
        event.app.layout.focus(ui.input_area)
        ui.refresh()
        event.app.invalidate()

    @kb.add("c-j")
    def _insert_newline(event) -> None:
        if state.mode == "insert":
            ui.input_area.buffer.insert_text("\n")

    app = Application(
        layout=ui.build_layout(),
        key_bindings=kb,
        full_screen=True,
        mouse_support=True,
    )

    ui.refresh()
    with patch_stdout(raw=True):
        await app.run_async()
