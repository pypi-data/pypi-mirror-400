selector_template = """
As an experienced and professional database administrator, your task is to analyze a user question and a database schema to provide relevant information. The database schema consists of table descriptions, each containing multiple column descriptions. Your goal is to identify the relevant tables and columns based on the user question.

[Instruction]:
1. Discard any table schema that is not related to the user question and evidence.
2. Sort the columns in each relevant table in descending order of relevance and keep the top 6 columns.
3. Ensure that at least 3 tables are included in the final output JSON.
4. The output should be in JSON format.


Requirements:
1. If a table has less than or equal to 10 columns, mark it as "keep_all".
2. If a table is completely irrelevant to the user question and evidence, mark it as "drop_all".
3. Prioritize the columns in each relevant table based on their relevance.
4. Include all the unique identifiers and primary keys
4. Please follow the answer template as specified.


Here is a typical example:

=========
【Schema】
# Table: account
[
  (account_id, the id of the account. Value examples: [11382, 11362, 2, 1, 2367].),
  (district_id, location of branch. Value examples: [77, 76, 2, 1, 39].),
  (frequency, frequency of the acount. Value examples: ['POPLATEK MESICNE', 'POPLATEK TYDNE', 'POPLATEK PO OBRATU'].),
  (date, the creation date of the account. Value examples: ['1997-12-29', '1997-12-28'].)
]
# Table: client
[
  (client_id, the unique number. Value examples: [13998, 13971, 2, 1, 2839].),
  (gender, gender. Value examples: ['M', 'F']. And F：female . M：male ),
  (birth_date, birth date. Value examples: ['1987-09-27', '1986-08-13'].),
  (district_id, location of branch. Value examples: [77, 76, 2, 1, 39].)
]
# Table: loan
[
  (loan_id, the id number identifying the loan data. Value examples: [4959, 4960, 4961].),
  (account_id, the id number identifying the account. Value examples: [10, 80, 55, 43].),
  (date, the date when the loan is approved. Value examples: ['1998-07-12', '1998-04-19'].),
  (amount, the id number identifying the loan data. Value examples: [1567, 7877, 9988].),
  (duration, the id number identifying the loan data. Value examples: [60, 48, 24, 12, 36].),
  (payments, the id number identifying the loan data. Value examples: [3456, 8972, 9845].),
  (status, the id number identifying the loan data. Value examples: ['C', 'A', 'D', 'B'].)
]
# Table: district
[
  (district_id, location of branch. Value examples: [77, 76].),
  (A2, area in square kilometers. Value examples: [50.5, 48.9].),
  (A4, number of inhabitants. Value examples: [95907, 95616].),
  (A5, number of households. Value examples: [35678, 34892].),
  (A6, literacy rate. Value examples: [95.6, 92.3, 89.7].),
  (A7, number of entrepreneurs. Value examples: [1234, 1456].),
  (A8, number of cities. Value examples: [5, 4].),
  (A9, number of schools. Value examples: [15, 12, 10].),
  (A10, number of hospitals. Value examples: [8, 6, 4].),
  (A11, average salary. Value examples: [12541, 11277].),
  (A12, poverty rate. Value examples: [12.4, 9.8].),
  (A13, unemployment rate. Value examples: [8.2, 7.9].),
  (A15, number of crimes. Value examples: [256, 189].)
]
【Forign keys】
account.‘district_id‘ = district.‘district_id‘
client.‘district_id‘ = district.‘district_id‘

【Question】
 What is the gender of the youngest client who opened account in the lowest average salary branch?

 【Verified Queries】
Question 1: What is the district_id of the branch with the lowest average salary?
SQL
”’ sql
SELECT ‘district_id‘
FROM district
ORDER BY ‘A11‘ ASC nulls last
LIMIT 1
”’
Question 2: What is the youngest client who opened account in the lowest average
salary branch?
SQL
”’ sql
SELECT T1.‘client_id‘
FROM client AS T1
INNER JOIN district AS T2
ON T1.‘district_id‘ = T2.‘district_id‘
ORDER BY T2.‘A11‘ ASC, T1.‘birth_date‘ DESC nulls last
LIMIT 1
”’
Question 3: What is the gender of the youngest client who opened account in the lowest
average salary branch?
SQL
”’ sql
SELECT T1.‘gender‘
FROM client AS T1
INNER JOIN district AS T2
ON T1.‘district_id‘ = T2.‘district_id‘
ORDER BY T2.‘A11‘ ASC, T1.‘birth_date‘ DESC nulls last
LIMIT 1
”’

【Custom Instructions】
Later birthdate refers to younger age; A11 refers to average salary

【Answer】
```json
{{
  "account": "keep_all",
  "client": "keep_all",
  "loan": "drop_all",
  "district": ["district_id", "A11", "A2", "A4", "A6", "A7"]
}}
```
Question Solved.

==========

Here is a new example, please start answering:


【Schema】
{context}
【Forign keys】
{fk_str}
【Question】
{question}
【Verified Queries】
{verified_queries}
【Custom Instructions】
{evidence}
[Metrics]
{metrics}

【Answer】
"""


decomposer_template = """You are a highly skilled Oracle SQL Query generator.
Given a [Database schema] description, including sample values and synonyms, [Constraints],[Custom Instructions], [Verified Queries] and a [Question], you must generate a valid SQL query.
Your first step is to determine if a query in [Verified Queries] can directly answer the user's [Question]. 
Analyze and Select the Best Verified Query:
Carefully analyze the user's [Question] to understand its core intent.
Compare this intent against the 'name' and 'question' for each entry in [Verified Queries].
Select the single best match that is most semantically aligned with the user's [Question].
Generate the SQL:
If a suitable verified query is found: Strictly use the SQL from that verified query. Adapt it only by replacing placeholder values with the specific values from the user's [Question]. Do not alter the logic, columns, or tables.
If no suitable verified query is found: Proceed to generate the SQL query step-by-step using the [Database schema] and the [Constraints] below.
Donot hallucinate. If you cannot construct a valid SQL query exactly from the provided inputs, DO NOT GUESS ‑ instead respond: “Unable to generate query due to insufficient information.”

[Constraints]
Query Generation (if no verified query is used):
Analyze the [Question] and [Custom Instructions] to understand the context and requirements.
Use the [Database schema] to identify relevant tables, columns, and relationships.
Use the [Metrics] to understand the key performance indicators or metrics that need to be calculated or reported.
Use sample values and synonyms to understand the context of the [Question] and the database schema.
Prioritize specific instructions in the [Question] over any default values provided in [Custom Instructions].
Use default values from custom instructions only when the [Question] does not specify them.
Decomposition (if no verified query is used):

Decompose the [Question] into sub-questions for text-to-SQL generation using chain-of-thought reasoning.
Identify all filters, conditions, and metrics explicitly mentioned in the [Question].
Determine the relationships between tables and the necessary joins.
Define any aggregation, calculations, or transformations required.
Query Validation:

Validate that the generated SQL adheres to the following:
Includes only the tables and columns required to answer the [Question].
Applies all necessary filters, conditions, and constraints mentioned in the [Question] or [Custom Instructions].
Uses aggregation and grouping functions correctly, ensuring accurate results.
Strictly ensures that NULL values are explicitly placed last in sorting using NULLS LAST.
Null Handling:

When using CTEs, include NULLS LAST in all ORDER BY clauses of the CTE or the main query.
If the sample values of a column indicate values like None or NULL, add a condition to exclude nulls, such as WHERE <column> IS NOT NULL, or join only the necessary tables to ensure valid rows are included.
All ORDER BY clauses must explicitly include NULLS LAST, regardless of whether the SQL engine's default behavior aligns with the intent.
Example for descending order: ORDER BY column_name DESC NULLS LAST
Example for ascending order: ORDER BY column_name ASC NULLS LAST
Modular Query Construction:

Use Common Table Expressions (CTEs) to break the query into logical steps:
Filter the data to include only relevant columns and rows based on the [Question].
Sort and return the final result.

Output Requirements
Provide the final SQL query. If a verified query was not used, show the step-by-step problem-solving process first.
Ensure that the query is strictly relevant to the [Question], without any extraneous fields or calculations.
Highlight any assumptions made while generating the query.
Ensure the query is formatted for readability.

==========
[Database schema]


Table: frpm

[
(CDSCode, CDSCode. Value examples: [’01100170109835’, ’01100170112607’].),
(Charter School (Y/N), Charter School (Y/N). Value examples: [1, 0, None]. And 0: N;. 1: Y),
(Enrollment (Ages 5-17), Enrollment (Ages 5-17). Value examples: [5271.0, 4734.0].),
(Free Meal Count (Ages 5-17), Free Meal Count (Ages 5-17). Value examples: [3864.0, 2637.0].
And eligible free rate = Free Meal Count / Enrollment)
]


Table: satscores

[
(cds, California Department Schools. Value examples: [’10101080000000’,
’10101080109991’].),
(sname, school name. Value examples: [’None’, ’Middle College High’, ’John F. Kennedy
High’, ’Independence High’, ’Foothill High’].),
(NumTstTakr, Number of Test Takers in this school. Value examples: [24305, 4942, 1, 0, 280].
And number of test takers in each school),
(AvgScrMath, average scores in Math. Value examples: [699, 698, 289, None, 492]. And
average scores in Math), (NumGE1500, Number of Test Takers Whose Total SAT Scores Are
Greater or Equal to 1500. Value examples: [5837, 2125, 0, None, 191]. And Number of Test Takers
Whose Total SAT Scores Are Greater or Equal to 1500. . commonsense evidence:. . Excellence
Rate = NumGE1500 / NumTstTakr)
]
[Foreign keys]
frpm.‘CDSCode‘ = satscores.‘cds‘

[Question]
List school names of charter schools with an SAT excellence rate over the average.


[Custom Instructions]
Charter schools refers to ‘Charter School (Y/N)‘ = 1 in the table frpm;
Excellence rate =NumGE1500 / NumTstTakr

[Verified Queries】
Name: Get Average SAT Excellence Rate for Charter Schools 
Question: Get the Average Value of SAT Excellence Rate of Charter Schools 
SQL: SELECT AVG(CAST(T2."NumGE1500" AS FLOAT) / T2."NumTstTakr") FROM frpm AS T1 INNER JOIN satscores AS T2 ON T1."CDSCode" = T2."cds" WHERE T1."Charter School (Y/N)" = '1'

Name: List Charter Schools with Above-Average SAT Excellence Rate 
Question: List School Names of Charter Schools with SAT Excellence Rate Over the Average 
SQL: SELECT T2."sname" FROM frpm AS T1 INNER JOIN satscores AS T2 ON T1."CDSCode" = T2."cds" WHERE T2."sname" IS NOT NULL AND T1."Charter School (Y/N)" = '1' AND CAST(T2."NumGE1500" AS FLOAT) / T2."NumTstTakr" > ( SELECT AVG(CAST(T4."NumGE1500" AS FLOAT) / T4."NumTstTakr") FROM frpm AS T3 INNER JOIN satscores AS T4 ON T3."CDSCode" = T4."cds" WHERE T3."Charter School (Y/N)" = '1' )


Solution Template:
"'sql
SELECT T2."sname"
FROM frpm AS T1
INNER JOIN satscores AS T2
ON T1."CDSCode" = T2."cds"
WHERE T2."sname" IS NOT NULL
AND T1."Charter School (Y/N)" = '1'
AND CAST(T2."NumGE1500" AS FLOAT) / T2."NumTstTakr" > (
SELECT AVG(CAST(T4."NumGE1500" AS FLOAT) / T4."NumTstTakr")
FROM frpm AS T3
INNER JOIN satscores AS T4
ON T3."CDSCode" = T4."cds"
WHERE T3."Charter School (Y/N)" = '1'
);
"'
Question Solved.

==========
[Database schema]
{desc_str}
[Foreign keys]
{db_fk}
[Question]
{query}
[Custom Instructions]
{evidence}
[Metrics]
{metrics}
[Verified Queries]
{verified_queries}
"""

refiner_template = """
【Instruction】
When executing SQL below, some errors occurred, please fix up SQL based on query and database info.
Prioritize using the verified queries exactly as written — along with all their specified logic—when adapting or applying them to the given question if the verified query for the [Question] is available.
otherwise solve the task step by step.
Using SQL format in the code block, and indicate script type in the code block.
When you find an answer, verify the answer carefully. 
If no sql is found in [old SQL], donot generate new SQL, just return the [error] and [exception_class] as is.

【Constraints】
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values
【Query】
-- {query}

【Database info】
{desc_str}
【Foreign keys】
{fk_str}
【old SQL】
```sql
{sql}
```
【error】 
{error}
【Exception class】
{exception_class}

Now please fixup old SQL and generate new SQL again. 
【correct SQL】
"""
