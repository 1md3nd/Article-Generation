article_from_topic_template = """As a creative article writer.
{format_instructions}

Under no circumstances are you allowed to use double quotes inside any keys or values (important).
The only time you will use double quotes ever is to wrap the key and values only (important).

Please ensure that all keys and values are wrapped in double quotes as shown in the example. Avoid using double quotes within the content of any key or value.

Content:
    Topic: {topic}
    Description: {description}
    Author(s): {authors}

Best Practices:

- Start with an engaging introduction that hooks the reader.
- Provide detailed exploration of the key aspects of the topic.
- Incorporate quotes or insights from relevant interviews or experts.
- Ensure the tone and style align with the magazine's audience.
- End with a strong conclusion that reinforces the article's main points

Generate Article:
"""
# under no circumstances are you allowed to use double quotes inside any keys or values (important).
# the only time you will use double quotes ever is to wrap the key and values only (important).
# example : your data should be like this :   curly_bracket_open "key" : "the value will 'come' here 'like' this without any double quotes", "key2":"value2","key3":["value3", "val4", "val5"] curly_bracket_close.

article_from_context_template = """"As a creative article writer. You will be given a article_context of a article, now rewrite the article with given format_instruction and Best Practices.
{format_instructions}

Under no circumstances are you allowed to use double quotes inside any keys or values (important).
The only time you will use double quotes ever is to wrap the key and values only (important).

Please ensure that all keys and values are wrapped in double quotes as shown in the example. Avoid using double quotes within the content of any key or value.

Content:
    Context : {article_context}

Best Practices:

- Start with an engaging introduction that hooks the reader.
- Provide detailed exploration of the key aspects of the topic.
- Incorporate quotes or insights from relevant interviews or experts.
- Ensure the tone and style align with the magazine's audience.
- End with a strong conclusion that reinforces the article's main points

Generate Article:
"""



fake_image_urls = ['https://res.cloudinary.com/dgmew67pv/image/upload/v1713618317/ikozbjd8lzlmfmqh9db4.png','https://res.cloudinary.com/dgmew67pv/image/upload/v1713449898/d42gn2g3glquxxkhrjrk.png']

