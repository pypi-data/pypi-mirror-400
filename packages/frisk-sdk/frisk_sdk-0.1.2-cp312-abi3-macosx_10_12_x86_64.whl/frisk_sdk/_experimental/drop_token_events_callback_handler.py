from langchain_core.callbacks.base import BaseCallbackHandler


class DropTokenEvents(BaseCallbackHandler):
    """Forward everything except per-token events to avoid double streams."""

    def __init__(self, inner: BaseCallbackHandler):
        self.inner = inner

    # DROP token events (no-ops)
    def on_chat_model_stream(self, *a, **k):
        return None

    def on_llm_new_token(self, *a, **k):
        return None

    async def aon_chat_model_stream(self, *a, **k):
        return None

    async def aon_llm_new_token(self, *a, **k):
        return None

    # ----- sync -----
    def on_chat_model_start(self, *a, **k):
        return getattr(self.inner, "on_chat_model_start", lambda *a, **k: None)(*a, **k)

    def on_chat_model_end(self, *a, **k):
        return getattr(self.inner, "on_chat_model_end", lambda *a, **k: None)(*a, **k)

    def on_chat_model_error(self, *a, **k):
        return getattr(self.inner, "on_chat_model_error", lambda *a, **k: None)(*a, **k)

    def on_llm_start(self, *a, **k):
        return getattr(self.inner, "on_llm_start", lambda *a, **k: None)(*a, **k)

    def on_llm_end(self, *a, **k):
        return getattr(self.inner, "on_llm_end", lambda *a, **k: None)(*a, **k)

    def on_llm_error(self, *a, **k):
        return getattr(self.inner, "on_llm_error", lambda *a, **k: None)(*a, **k)

    # ----- async -----
    async def aon_chat_model_start(self, *a, **k):
        return await getattr(self.inner, "aon_chat_model_start", lambda *a, **k: None)(
            *a, **k
        )

    async def aon_chat_model_end(self, *a, **k):
        return await getattr(self.inner, "aon_chat_model_end", lambda *a, **k: None)(
            *a, **k
        )

    async def aon_chat_model_error(self, *a, **k):
        return await getattr(self.inner, "aon_chat_model_error", lambda *a, **k: None)(
            *a, **k
        )

    async def aon_llm_start(self, *a, **k):
        return await getattr(self.inner, "aon_llm_start", lambda *a, **k: None)(*a, **k)

    async def aon_llm_end(self, *a, **k):
        return await getattr(self.inner, "aon_llm_end", lambda *a, **k: None)(*a, **k)

    async def aon_llm_error(self, *a, **k):
        return await getattr(self.inner, "aon_llm_error", lambda *a, **k: None)(*a, **k)
