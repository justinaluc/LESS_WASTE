#LESS WASTE - challenges app
___
* app created with Django, postgresQL, Bootstrap
    
* mastering django within python developer course

* taking challenges to save our planet | step by step

## Table of contents
___
* [Introduction](#introduction)
* [Technologies](#technologies)
* [Setup](#setup)
* [Launch](#launch)
* [Status](#status)
* [Plan for development](#plan-for-development)

###Introduction:
___
This app is filled with ideas for small and big steps 
one could take in order to live life at the cleaner Earth. 
One finds here challenges, statistics, tips of improvement 
towards <b> less waste </b> or even <b> zero waste</b>.

###Technologies:
___
    -> install from requirements.txt
  * django==4.0.4
  * python==3.8.10
  * psycopg2-binary==2.9.2
  * bootstrap4

###Setup:
___
To run this project, install it locally...
or come to check it out at http://justyna.pythonanywhere.com/

###Launch:
___

###Status:
___

###Plan for development:
___
+ app with user:
  + models: UserChallenge, Profile, Log
  + templates: home, register, log in, log out, user_challenges (activate, delete)
  + views with logic
  + admin site: Profile (User with points)
  
+ app with challenges:
  + models: Challenge, Category, CategoryChallenge
  + templates: show categories, show challenges in category, show challenges, show challenge details
  + views: generic
  + admin site: Challenge, Category, CategoryChallenge 

Ideas for later development:
- statistics
- add new challenge idea,
- add challenges to "my_favourite" (create new category connected only with User)
- books/ blogs to read, instagram profiles to follow
- app: saved costs (when not buying often the particular items),
- app: waste reduced in g/ kg (plastic bags, bottles, newly produced items),

  
    Scope of functionalities 
    Examples of use
    Project status 
    Sources
    Other information