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
```""",

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
```"""
}
