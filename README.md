# FLASHY FLASHCARDS
#### Video Demo:  https://youtu.be/s1mLrcPYNhg
#### Description:
### Summary
Flashy Flashcards is a Flask Web App enabling users to add their own flashcards and be quizzed on them. It uses the traditional flashcard approach whereby cards are stored on different 'shelves' depending on how well you remember them. The web app allows you to create different decks of cards so that flashcards can be kept organised.

## **project.py**
### **dashboard**
Retrieves the user's decks and username (for personalised greeting) and passes them to the template.
### **login**
Clears existing session, checks that all fields have been filled in (returns *apology* otherwise), then goes in to check username and password against the database. Sets the *session*'s user id and redirects to the *dashboard*.
### **logout**
Clears the session and flashes success message, redirects to Welcome page.
### **register**
Checks if the username field has been filled in, then checks if the desired username already exists (returns *apology* if that is the case). Then makes sure that password and the confirmation thereof were provided and match. Lastly, inserts the new user into the database with hashed password and redirects to the *dashboard*.
### **add**
Makes sure that front and back of the new card, as well as the deck have been provided. Then checks for existing duplicates in the database (flashes message and returns if so) and inserts the new card into the given deck, flashing success message.
Provides a list of the user's decks of cards to the template.
### **quiz**
POST: Checks the user's provided solution against the one in the database using the *Levenshtein* package. If the Levenshtein distance is less than or equal to one, the card is moved up one shelf in the database if not at the maximum (there are eight shelves). If the distance is greater, the flashcard is moved down one shelf. In each case (identical, typo, different), the according message is passed to *quiz_solution*. <br/>
GET: First this function creates a list of eight 'shelves', with all the cards of each shelf in the deck in the respective shelf, along with a list of weights. Then it loops over the two lists and adds only entries of non-empty shelves to two new lists. Lastly, using the *random* package, a shelf is selected randomly with the probabilities of each being determined by the list of weights. Cards on lower shelves are the ones that have not been remembered correctly often and low shelves are therefore more likely to be selected. A card is then picked at random from the chosen shelf and passed to the template.
### **pre_quiz**
Checks that the user has selected a deck and sets the *session*'s set id accordingly.
### **add_deck**
Checks that deck name was provided and if it already exists, then inserts the new deck into the database and flashes success message.

### **help_functions.py**
This file includes a decorator function to check if the user is logged in and to render the Welcome page together with a flashed message otherwise, as well as a Jinja filter *emojify* to convert emojis and a function to display an *apology* page with image and the provided message.

### **cards.db**
SQL database to keep track of users (id, username and password hash), flashcards (id, user id, set id, shelf, front and back of card) and decks (id, user id, name).

### **navbar.js**
JavaScript code to fix the navigation bar at the top of the page when scrolling down.

### **styles.css**
CSS to determine font style, buttons, forms and their size and position, the navigation bar including links and positioning for use in JS, the cards and position of buttons on them.

### **layout.html**
General layout to be extended to the HTML templates, including icon, navigation bar (both for logged in and non-logged in users) and Jinja code to show flashed messages and make them dismissable with Bootstrap.

## **Templates**
#### Non-logged in users:
*index.html* - simple welcome page with explanation and link to register <br/>
*login.html* - login form <br/>
*register.html* - registration form with regex for password strength
#### Logged in users:
*dashboard.html* - dashboard showing all of the user's decks in card format, links for adding more decks and to the quiz <br/>
*pre_quiz.html* - dropdown menu to select the stack of flashcards for the quiz <br/>
*quiz.html* - display of the top side of a card and an input field on another card for the user to fill in <br/>
*quiz_solution.html* - message to the user informing them about the correctness of their response and display of both sides of the card, button to next card <br/>
*add.html* - for adding new flashcards: dropdown menu of user's decks, input fields for front and back of the new card <br/>
*add_deck.html* - input field for adding a new deck <br/>
*apology.html* - meme with relevant error message and code

### Possible extensions
Possible improvements would be to enable users to upload csv-files to be converted to flashcards automatically, and to create a distinction between 'exact' flashcard decks that need to be matched precisely (as implemented with Levenshtein distance of at most 1, especially useful for foreign language vocabulary) and text or explanation based cards, where for instance the cosine similarity could be used for checking, eg using RoBERTa or a similar package. The database is set up to accommodate a 'type' for decks.
