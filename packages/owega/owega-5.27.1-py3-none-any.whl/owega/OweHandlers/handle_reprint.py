"""Handle /reprint."""
from ..conversation import Conversation
from ..utils import markdown_print


# reprints chat history
def handle_reprint(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    """Handle /reprint.

    Command description:
        Reprints (fancy) the conversation history.

    Usage:
        /reprint [number of messages to reprint]
    """
    # removes linter warning about unused arguments
    _, _, _ = temp_file, given, temp_is_temp

    if not silent:
        # Parse the number of messages to print
        num_messages = None
        if given.strip():
            try:
                num_messages = int(given.strip())
                if num_messages <= 0:
                    num_messages = None
            except ValueError:
                # Invalid number, just print all messages
                num_messages = None

        # Get the messages to print
        all_messages = messages.get_messages()
        if num_messages is not None:
            # Get the last N messages
            messages_to_print = all_messages[-num_messages:]
            start_index = len(all_messages) - num_messages
        else:
            messages_to_print = all_messages
            start_index = 0

        for i, message in enumerate(messages_to_print):
            actual_index = start_index + i
            ind = actual_index - 1
            ind_str = f' [ \033[90m{ind}\033[0m ]'
            if ind < 0:
                ind_str = ' [ \033[90mCONTEXT\033[0m ]'

            print()

            if message['role'] == 'system':
                print("[ \033[92mSYSTEM\033[0m ]", end="")
            elif message['role'] == 'user':
                print("[ \033[96mUSER\033[0m ]", end="")
            elif message['role'] == 'assistant':
                print("[ \033[95mOWEGA\033[0m ]", end="")
            else:
                print("[ \033[95mFUNCTION\033[0m ]", end="")
            print(ind_str)
            markdown_print(
                message['content']
                .encode('utf16', 'surrogatepass')
                .decode('utf16')
            )

        # for i, message in enumerate(messages.get_messages()):
        #     ind = i-1
        #     ind_str = f' [ \033[90m{ind}\033[0m ]'
        #     if ind < 0:
        #         ind_str = ' [ \033[90mCONTEXT\033[0m ]'

        #     print()

        #     if message['role'] == 'system':
        #         print("[ \033[92mSYSTEM\033[0m ]", end="")
        #     elif message['role'] == 'user':
        #         print("[ \033[96mUSER\033[0m ]", end="")
        #     elif message['role'] == 'assistant':
        #         print("[ \033[95mOWEGA\033[0m ]", end="")
        #     else:
        #         print("[ \033[95mFUNCTION\033[0m ]", end="")
        #     print(ind_str)
        #     markdown_print(
        #         message['content']
        #         .encode('utf16', 'surrogatepass')
        #         .decode('utf16')
        #     )

    return messages


item_reprint = {
    "fun": handle_reprint,
    "help": "reprints the conversation history with fancy markdown support",
    "commands": ["reprint"],
}
