class DeletionHelper:
    def __init__(self):
        self.messages_map = {}

    def record_message(self, chat_id: int, message_id: int):
        if chat_id not in self.messages_map:
            self.messages_map[chat_id] = []
        self.messages_map[chat_id].append(message_id)

    async def delete_all(self, chat_id: int, bot):
        msg_ids = self.messages_map.get(chat_id, [])
        for mid in msg_ids:
            try:
                await bot.delete_message(chat_id, mid)
            except:
                pass
        self.messages_map[chat_id] = []


deletion_helper = DeletionHelper()