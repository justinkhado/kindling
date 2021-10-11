# Kindling

Kindling is a Tinder-like app for finding interesting books.
Current working version deployed at: https://cpsc349-kindling.herokuapp.com/

## Getting Started

### Dependencies

* Python 3
    * flask, flask-socketio

### Installing

1. Download or clone this repository
2. (Optional) Set flask environment to `main.py`
3. (Optional) Run `python -m flask init-db` to create a fresh database

### Executing program

* Run `python main.py`
    * App runs at localhost by default

### Using

Since Kindling is based on Tinder, this application operates in a similar fashion. 
Users are prompted to create a profile upon first creating an account. Only then will a user
be able to see other user profiles. A user that is not logged in will not have access to
most URL endpoints. 

The home screen shows another user's profile that the current user
can match or decline; then, a new user's profile will appear. The application will go through
every user profile until there are no more. 

Users will have to wait until another user matches the them in order for a private chatroom to 
appear under "Matches". To test this out, one can create two profiles and match each other.
The private chatroom was built using web sockets, so the chatbox should update in real time.

## TO-DO
* remove config information from source code
* when a user updates their profile, remove corresponding entries from seen_books
* add client-side chat clear
* time of messages
* let users unmatch
* let users edit **parts** of profiles
* add author to profile
* randomize profile order
* notify users when a match occurs
* notify users when they have a new message
* improve HTML/CSS design
* refactor *everything*
