# CSFD_movies_rating
A python script for finding a movie rating on www.csfd.cz, save it to a database and a result is displayed as a website via Flask library. 
**Description below the image.**

![Screenshot](website_movies.png)

**csfd_git.py**

This script is the heart of this project. :)
The script has these parts:
1) Truncates table csfd_movies_calendar
2) Goes to url https://new.csfd.cz/televize/horizontalne/ via Selenium library, accepts website cookies and selects tv channels on the website
    - Selenium needs to be used because of the tv channels selection on the website (I didnt find a way how to do it via requests library)
3) Goes to url https://new.csfd.cz/televize/?sort=rating&day=-i}
    - where i is a variable in for loop), i is a number of day in past (1 - yesterday, 2 - two days ago etc)
4) Gets movies data (movie name, movie url, category, tv channel, tv date, movie image url) and insert them into table csfd_movies_calendar in a database
5) Gets movies urls from the table, scraps a movie rating from the url and save it to table csfd_movies_calendar 
    - the scrapping is done via request library which is much faster than Selenium

**database**

This script requires a database running. I use MariaDB for this purpose. There needs to exist a table called *csfd_movies_calendar* in which data are saved during the script run. SQL query for a table creation:
*create table csfd_movies_calendar(
name varchar(100),
category varchar(100),
station varchar(50),
order_number integer,
movie_link varchar(300),
program_link varchar(300),
rating integer,
tv_date date,
image_link varchar(300)
);*

**web.py**

This is a Flask app used to display data from the database. When a user get url *192.168.0.39/csfd*, the function called get_movies() starts and returns data from the table *csfd_movies_calendar*. Data are pass to the html template *csfd.html* and the template is rendered with the movies data (screenshot above). A template style is defined in /static/styles/csfd.css.
POST method for url *192.168.0.39/csfd* is not allowed because it is not needed.
