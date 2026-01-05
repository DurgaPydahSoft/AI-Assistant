EXAMPLES_BY_CATEGORY = {
    "search": """
EXAMPLE: Text Search (Ambiguous fields)
User: "Find email of Satya"
Schema: users(name:String, email:String, username:String)
Output: ```json
{
  "action": "query",
  "collection": "users",
  "type": "find",
  "filter": {
    "$or": [
      { "name": { "$regex": "Satya", "$options": "i" } },
      { "email": { "$regex": "Satya", "$options": "i" } },
      { "username": { "$regex": "Satya", "$options": "i" } }
    ]
  },
  "projection": { "email": 1, "name": 1 }
}
```
[SUGGESTIONS]["What else can you find?", "List all users", "Check student records"][/SUGGESTIONS]""",

    "aggregation": """
EXAMPLE: Aggregate Summary (Count/Average)
User: "How many active CSE students?"
Schema: students(status:String, dept:String)
Output: ```json
{
  "action": "query",
  "collection": "students",
  "type": "count",
  "filter": {
    "status": { "$regex": "active", "$options": "i" },
    "dept": { "$regex": "CSE", "$options": "i" }
  }
}
```

EXAMPLE: Complex Math (Average Age)
User: "Average age in Sales?"
Schema: employees(age:Integer, dept:String)
Output: ```json
{
  "action": "query",
  "collection": "employees",
  "type": "aggregate",
  "pipeline": [
    { "$match": { "dept": { "$regex": "Sales", "$options": "i" } } },
    { "$group": { "_id": null, "avg": { "$avg": "$age" } } }
  ]
}
```""",

    "crud": """
EXAMPLE: Insert Data
User: "Add user Satya with email satya@example.com"
Output: ```json
{
  "action": "insert",
  "collection": "users",
  "document": { "name": "Satya", "email": "satya@example.com" }
}
```

EXAMPLE: Update Data
User: "Update Satya's phone to 9999999999"
Output: ```json
{
  "action": "update",
  "collection": "users",
  "filter": { "name": { "$regex": "Satya", "$options": "i" } },
  "update": { "$set": { "phone": "9999999999" } }
}
```

EXAMPLE: Delete Data
User: "Remove user with email tester@test.com"
Output: ```json
{
  "action": "delete",
  "collection": "users",
  "filter": { "email": "tester@test.com" }
}
```""",

    "iterative": """
EXAMPLE: Iterative Creation (Schema Aware)
User: "I want to add a new student"
Assistant: "Sure! Let me check what details are needed for a student record."
Output: ```json
{ "action": "get_schema", "collections": ["students"] }
```
System Result: students(name:String, rollNo:Integer, email:String, dept:String)
Assistant: "I see. To add a student, I'll need their Name, Roll Number, Email, and Department. Could you provide those?"

EXAMPLE: Mandatory Confirmation
User: "Add student Alice, Roll 101, Email alice@test.com, Dept CSE"
Assistant: "I've prepared the details for student Alice. 
- Name: Alice
- Roll No: 101
- Email: alice@test.com
- Dept: CSE
Should I proceed with adding this record to the database?"
User: "Yes, go ahead."
Output: ```json
{
  "action": "insert",
  "collection": "students",
  "document": { "name": "Alice", "rollNo": 101, "email": "alice@test.com", "dept": "CSE" }
}
```

EXAMPLE: Targeted Update with Confirmation
User: "Change Bob's department to ECE"
Assistant: "Found it. I will update Bob's department from 'CSE' to 'ECE'. Please confirm if I should execute this change."
User: "Confirmed"
Output: ```json
{
  "action": "update",
  "collection": "students",
  "filter": { "name": "Bob" },
  "update": { "$set": { "dept": "ECE" } }
}
```
"""
}
