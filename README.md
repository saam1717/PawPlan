# Details for developers
## Dependencies
- **Python**
  - < 3.13

- **Flet version** 
  - must be 0.85.0+
    - alt+cmd+s -> Python Interpreter -> + -> search flet and install
    - If interpreter is invalid, delete .idea folder
      - I forgot to put a .gitignore file in the repo, so the .idea folder is included in the repo. You can delete it and reconfigure your interpreter.
      
- **python-dotenv**
  > this is only for debug phase, may be changed in deployment
  - other requirements
    - Give me your email so I can add you as admin in the PawPlan project here
      - https://console.cloud.google.com
    - find PawPlan project -> APIs & Services -> Credentials -> PawPlan Client -> create your own secret
    - create .env file
      ````
      GOOGLE_CLIENT_ID=xxx
      GOOGLE_CLIENT_SECRET=xxx
      
      # fill in the details aboce
      # Google client id can be copied
      # Google client secret must be generated

- **pawplan_account.json**
  - similar to the .env file
  - Give me your email so I can add you as admin in the PawPlan project here
    - https://console.cloud.google.com
  - find PawPlan project -> IAM & admin -> Service Accounts -> click the first hyperlink -> keys -> Add Key -> Create new key -> JSON
  - place the JSON file inside PawPlan folder
  - rename to pawplan_account.json
  - ***make sure to include the JSON in .gitignore***
    - it contains sensitive information

## SCRUM
- to be updated every week
- flexible
- Link
  - https://docs.google.com/spreadsheets/d/1Zj0F4BQfUvWVpQxehL6-CPnQ8jgi2yHU6GiovQRYhGU/edit?usp=sharing

--- 

# Details for Users
> to be written yet
