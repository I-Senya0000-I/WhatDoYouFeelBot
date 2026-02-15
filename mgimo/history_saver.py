from groq import Groq


# Примерная оценка длины текста в токенах (для русского языка)
def count_tokens(history) -> int:
    """Подсчитывает общее количество токенов в списке сообщений."""
    return len(history)


def summarize_history(history, max_tokens=8000, reserve=7900):
    """
    Обобщает содержание старых сообщений, если общий объём превышает max_tokens - reserve.

    :param messages: Список сообщений (HumanMessage, AIMessage)
    :param max_tokens: Максимальный контекст модели
    :param reserve: Сколько токенов оставить для ответа (например, 4096)
    :return: Обрезанный список сообщений
    """
    available_tokens = max_tokens - reserve  # Оставляем место для генерации
    current_tokens = count_tokens(history)
    if current_tokens <= available_tokens:
        return history  # Обрезка не нужна
    
    history_saver = Groq(
        api_key=open("./API keys/History Saver API key.txt", encoding="utf-8").read().strip(),
    )
    completion = history_saver.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
        {
            "role": "user",
            "content": open('./prompts/History Saver Prompt.md', encoding="utf-8").read() + "\n\n" + history,
        }
        ],
        temperature=0.2,
        top_p=1,
        reasoning_effort="medium",
        stream=False,
        stop=None
    )
    summarized_history: str = completion.choices[0].message.content if isinstance(completion.choices[0].message.content, str) else ""
    if len(summarized_history) > max_tokens - reserve:
        return summarized_history[:max_tokens - reserve - 13] + "...</history>"
    return summarized_history
