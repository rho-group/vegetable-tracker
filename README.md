# RHO vegetable-tracker
## Idea
Application with focus on eating versatile vegetables, fruits, berries and others without extra load on mental health from tracking macros. The basis for our project was studies on how eating 30 different plant in a week based products improves your gut health and brain functions. We wanted the application to track only how many different vegetables user eats and not stress about macros and how much vegetables the user consumes. We hope our project inspires people to pay more attention to how much vegetables they eat in fun and easy way.

- The basis for our data was open data from Fineli database, which you can access here: https://fineli.fi/fineli/en/avoin-data \
- Other data we have used we collected ourselves.\
- The database is ran in Azure webservice with Azure PostgreSQL database. \
- We used Jupiter Notebook to clean the data to usable format.\
- The backend of our application is made using Python and the frontend was made using HTML, CSS and JavaScript.
## How to run the project locally
- To run the application locally, you need to set up PostgreSQL database. The tables can be made with `create_table_scripts_all_included.sql`\
- After this you can populate the vegetable and inseason tables with the .csv files found in our `nutrition data`-folder.\
- You can install all required Python modules using `requirements.txt`\
- You need to set the database parameter in the app.py code to correspond to your database informations.

## Contributors
This project was made as part of Data Engineering training in April 2025. The members working on this project were:\
[Katri Järvinen](https://github.com/KatriJar)\
[Niina Ahola](https://github.com/niianni)\
[Salla Kivistö](https://github.com/Slothay)

