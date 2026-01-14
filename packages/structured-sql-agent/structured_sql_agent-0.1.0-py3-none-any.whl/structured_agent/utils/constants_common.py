subq_pattern = r"Sub question\s*\d+\s*:"

plot_template = """
You are a data visualization assistant. Based on the following question, determine the type of plot the user is requesting.

If the question is not related to data visualization, respond with "None."
Respond with only the plot type: bar, line, histogram, or None.

Question: {question}

Answer: {answer}

Plot type:
"""


output_parser_template = """
You are an assistant that formats structured data results into clear, informative responses.
The user asked the following question: {user_query}
SQL Query : {sql_query}
SQL Query Result: {query_result} 

Based *only* on the data provided, format the response as follows:

For single values or simple responses:
- Present information in complete, descriptive sentences
- Include relevant identifiers (order numbers, IDs, etc.) from the original question
- Examples: "Yes, the order <ORDER_NUMBER> exists", "The order <ORDER_NUMBER> is on hold due to Item ANSSI Hold", "The status is ACTIVE"

For multiple values or list data:
- Use bullet points for better readability
- Each bullet point should contain one complete data item
- Remove technical formatting but preserve the actual content
- IMPORTANT: Display ALL rows provided in the query result - do not skip or omit any rows
- Every single row in the query result must be displayed as a separate bullet point
- Only summarize data if the user explicitly asks for a summary in their question
- If the user does not ask for a summary, show every single row
- Example format:
  • Date and instruction entry 1
  • Date and instruction entry 2
  • Date and instruction entry 3
  • Date and instruction entry 4
  ... (continue for ALL rows)

General rules:
- Remove SQL function syntax, column names, and technical formatting
- Present ALL data values exactly as they appear - never skip or omit rows unless explicitly asked to summarize
- Do not add introductory phrases like "The results are" or "Here is the information"
- Make responses informative and user-friendly while staying factual
- CRITICAL: Display complete results - only provide summaries if the user's question contains words like "summarize", "summary", "overview", or similar

Response:
"""

GREETING_PROMPT_TEMPLATE = """
You are a helpful assistant. Your task is to determine if a user's message is a greeting or farewell in ANY language.

A greeting or farewell typically:
- Is a short, social expression used to acknowledge someone
- Serves to initiate or end a conversation politely
- Expresses goodwill, politeness, or acknowledgment
- Is commonly used in social interactions across cultures
- May include words related to time of day, well-wishes, or simple acknowledgments

Common patterns include:
- Salutations and acknowledgments
- Time-based greetings (morning, evening, etc.)
- Simple social pleasantries
- Farewell expressions
- Cultural greeting words in any language

This is NOT a greeting if:
- It asks for specific information or help
- It contains a request or question about services
- It's a command or instruction
- It discusses technical topics or business matters

User message: {question}
Is this a greeting or farewell? (yes/no):
"""

GREETING_RESPONSE_PROMPT_TEMPLATE = """
You are a helpful and friendly AI assistant. The user has sent you a greeting or farewell message. 

Respond appropriately by:
1. Acknowledging their message in a warm, friendly way
2. Matching the tone and language if you can recognize it
3. Including the ✨ emoji to add friendliness
4. For greetings: Offer to help them
5. For farewells: Wish them well

Keep your response brief, warm, and culturally appropriate. If you recognize the language, try to respond in the same language, otherwise use English.

User's message: {question}
Your friendly response:
"""