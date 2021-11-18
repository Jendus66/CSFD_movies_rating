from flask import Flask, request, render_template
from flask_mysqldb import MySQL

def get_movies():
    """Get movies data from database (table csfd_movies_calendar). The function return
    array with data.
    """
    query = """select name, category, station, movie_link, rating,image_link, 
date_format(max(tv_date),'%d.%m.%Y') "date", program_link from csfd_movies_calendar cmc
group by name
order by rating desc,name;"""
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    return results


# Flask database login
app = Flask(__name__)
app.config['MYSQL_HOST'] = "host"
app.config['MYSQL_USER'] = "user"
app.config['MYSQL_PASSWORD'] = "password"
app.config['MYSQL_DB'] = "db"

mysql = MySQL(app)

@app.route('/csfd', methods=['GET'])
def csfd():
    if request.method == 'GET':
        filmy = get_movies()
        return render_template('csfd.html', filmy=filmy)

if __name__ == "__main__":
    app.run(debug=False, host= '192.168.0.39')
