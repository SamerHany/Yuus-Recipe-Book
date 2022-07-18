# Yuu's Recipe Book
#### Video Demo: https://youtu.be/Ru8D6XFJAzc
#### Description:
This web app is built using Flask, Javascript, and SQL.
It's a recipe book where users can sign up for an account and start adding their favorite recipes to their recipe books.
Users can add the different ingredients with ther quantities into the recipe, and the calories corresponding to each ingredient's quantity will be automatically calculated as well as the total calories of the recipe.

___

## Files:

### styles.css
This is where all styling for the webapp lives, and it's programmed in CSS.

### apology.html
This is the error page, it's shown when a user submits missing data or for any other data validation error.
It's built with custom error messages based on the error scenario.

### index.html
This is the user's recipe book. It requires user log in.
If the user is not logged in, it redirects to the login page.
And if the user is logged in, it shows the user's recipe book.

### layout.html
This is the main template for the webapp. It acts as the skeleton of the webapp with the main components.
It contains the navigation bar, site footer, and a dynamic body depending on the page.

### login.html
This is the login page where the user can log in using their username and password.
Once the user is logged in, they get redirected to the index page to show their saved recipes in the recipe book.

### recipe.html
This is where new recipes can be added.
And existing recipes can be viewed and edited.
When this page is accessed using a GET request the webapp checks for a recipe ID parameter in the query string.
If there is no recipe ID, it shows the blank form to add a new recipe.
If there is a recipe ID, it pulls the corresponding details from the database and populates the recipe page.
The page has Javascript with a small form to add ingredients to the ingredients table, and it gets the ingredient calories using an AJAX call to a dedicated route that retreives an ingredient's details from the database.

### register.html
This is where the users can sign up for an account.
Users are required to provide a username, password, and confirm the password.
If any of the input fields are missing, the page redirects to the apology page showing the corrresponding error.

### application.py
This is the main code and logic for the webapp using Python and where all the routes/pages are programmed.

### helpers.py
This is where the helper functions are programmed like the apology function.

### project.db
This is the database that contains the following tables:
- users: saving the user login details
- users_recipes: saving the users' recipes
- recipes: saving the recipe ingredients and quantities
- ingredients: saving the ingredients' names and calories per gram

