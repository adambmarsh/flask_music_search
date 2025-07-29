# Flask Music Search

Flask Music Search is a personal project that provides a facility to
search through a PSQL database on the LAN. The search terms are defined in a
form on a Web page and the results are displayed in a Web page as well. 

The driver behind is project was frustration with the limitations of the search
functionality in VLC and on my NAS (QNAP) and Kodi.  

## Installation

Clone the source code from https://github.com/adambmarsh/flask_music_search.

The project uses Python and uv, and a virtual environment. The requirements (dependencies) are listed in `pyproject.toml`. 
Use standard uv commands to set up a virtual environment and install the dependencies (in the directory that contains a
clone of the gitHub repository).

The project uses `gunicorn` as the WSG server, which is installed in the virtual
environment. The bash script `music-search.sh` activates that environment prior
to running the search application (Flask) that provides the database search functionality.

To install the music search as a service, please follow the instructions in the file `music-search.service`.
Otherwise, run the bash script `music-search.sh` to launch the search
application, which displays a web page. 

Note that `music-search.sh` takes two optional parameters:
 - `-i` the IP address of the server hosting the search app
 - `-p` the port on the server hosting the search app
 
 If these are not provided, the app attempts to discover the host's IP address
 by itself and the port number defaults t0 5000.

Note that Python file db_connect.py expects to find the database details in a
file .settings_db.yml, with the following structure:

``` yml
name: <name of the database>
user: <name of the database user>
password: <user's database password>
host: <ip address of the database server>
port: <port on which the database server listens for requests>

```

## Status

The project thus far has offered good scope for experimenting with: 

- Flask
- Django’s ORM 

### To-do List

- Improve the Web GUI -- presentation in the first iteration is very basic, the album comments and other repeated information is to be shown once per album
- Allow for selecting songs and/or albums to create an XSPF playlist (compatible with VLC)
- Try to make the search DB lay-out agnostic as far as possible -- DB lay-out could be read in from config, for example 



