import logging

from duowen_agent.agents.component.base import BaseComponent
from duowen_agent.llm import BaseAIChat, MessagesSet
from duowen_agent.llm.tokenizer import tokenizer
from duowen_agent.utils.core_utils import stream_to_string
from duowen_agent.utils.string_template import StringTemplate


class Summarization(BaseComponent):

    _default_summary_prompt = StringTemplate(
        """<role>
Context Extraction Assistant
</role>

<primary_objective>
Your sole objective in this task is to extract the highest quality/most relevant context from the conversation history below.
</primary_objective>

<objective_information>
You're nearing the total number of input tokens you can accept, so you must extract the highest quality/most relevant pieces of information from your conversation history.
This context will then overwrite the conversation history presented below. Because of this, ensure the context you extract is only the most important information to your overall goal.
</objective_information>

<instructions>
The conversation history below will be replaced with the context you extract in this step. Because of this, you must do your very best to extract and record all of the most important context from the conversation history.
You want to ensure that you don't repeat any actions you've already completed, so the context you extract from the conversation history should be focused on the most important information to your overall goal.
</instructions>

The user will message you with the full message history you'll be extracting context from, to then replace. Carefully read over it all, and think deeply about what information is most important to your overall goal that should be saved:

With all of this in mind, please carefully read over the entire conversation history, and extract the most important and relevant context to replace it so that you can free up space in the conversation history.
Respond ONLY with the extracted context. Do not include any additional information, or text before or after the extracted context.

<messages>
Messages to summarize:
{messages}
</messages>"""
    )

    def __init__(
        self,
        llm_instance: BaseAIChat,
        summary_prompt: StringTemplate = None,
        trim_tokens_to_summarize: int = 4000,
        messages_to_keep: int = 4,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.llm_instance = llm_instance
        self.kwargs = kwargs
        if summary_prompt is None:
            self._summary_prompt = self._default_summary_prompt
        else:
            self._summary_prompt = summary_prompt

        self.trim_tokens_to_summarize = trim_tokens_to_summarize
        self.messages_to_keep = messages_to_keep

    def run(self, messages: MessagesSet) -> MessagesSet:
        """Run the summarization component.

        Args:
            messages (MessagesSet): The messages to summarize.

        Returns:
            str: The summarized messages.
        """

        if (
            tokenizer.messages_len(messages) <= self.trim_tokens_to_summarize
            or len(messages) <= self.messages_to_keep
        ):
            return messages

        messages_to_summarize = MessagesSet(messages[: -self.messages_to_keep])
        messages_to_preserve = MessagesSet(messages[-self.messages_to_keep :])

        # 2. 生成摘要
        prompt_str = self._summary_prompt.format(
            messages=messages_to_summarize.get_format_messages()
        )

        summary_text = stream_to_string(self.llm_instance.chat_for_stream(prompt_str))

        if not summary_text or len(summary_text.strip()) < 10:  # 简单验证
            logging.warning(
                "Summarization resulted in an empty or too short response. Aborting summarization and returning original messages."
            )
            return messages

        summary_message = {
            "role": "system",
            "content": f"Summary of earlier conversation:\n{summary_text.strip()}",
        }

        new_messages = MessagesSet([summary_message]) + messages_to_preserve

        return new_messages
