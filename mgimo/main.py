from groq import Groq
import interview_logger
import history_saver


if __name__ == "__main__":
    construct = Groq(api_key=open("./API keys/Construct API key.txt", encoding="utf-8").read().strip())
    inland_empire = Groq(api_key=open("./API keys/Inland Empire API key.txt", encoding="utf-8").read().strip())

    full_log = ""
    summarized_history = ""

    for question_index, question in enumerate(interview_logger.read_questions('./interview/questions.xml'), start=1):
        completion = inland_empire.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
            {
                "role": "user",
                "content": open("./prompts/Inland Empire Prompt.md", encoding="utf-8").read() + open("./prompts/Prompt Skeleton.md", encoding="utf-8").read() + summarized_history + question,
            }
            ],
            temperature=0.2,
            top_p=1,
            reasoning_effort="medium",
            stream=False,
            stop=None
        )
        inland_empire_response: str = completion.choices[0].message.content if isinstance(completion.choices[0].message.content, str) else ""

        completion = construct.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
            {
                "role": "user",
                "content": open("./prompts/Construct Main Prompt.md", encoding="utf-8").read() + open("./prompts/Prompt Skeleton.md", encoding="utf-8").read() + summarized_history + inland_empire_response + "\n\n" + "<question>" + question + "</question>",
            }
            ],
            temperature=0.2,
            top_p=1,
            reasoning_effort="medium",
            stream=False,
            stop=None
        )
        construct_response: str = completion.choices[0].message.content if isinstance(completion.choices[0].message.content, str) else ""
        
        full_log += "<question>" + question + "</question>" + inland_empire_response + construct_response
        summarized_history = history_saver.summarize_history(full_log)
        
        interview_logger.append_to_log('./interview/interview_log.xml', question, inland_empire_response, completion.choices[0].message.content)
