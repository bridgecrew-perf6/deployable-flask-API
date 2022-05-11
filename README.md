# deployable-flask-API
deployable-flask-API

# Instructions
- To create the database:
1. Get inside flask shell
2. Import the database  
```from src.database import db```
3. Create the database from columns:  
```db.create_all()```
- To check if it's all good, try:   
```db```
- If you want to delete the database, use: 
```db.drop_all()```


