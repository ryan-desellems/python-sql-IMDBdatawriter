from faker import Faker
import imdb
import os
import datetime
from random import *

# GLOBALS-----------------------------------
# number of top 250 movies and series to pull
NUM_TITLES = 20
# name of output file to write to
OUTFILE = open("sqlgoddatafile.sql",'w+')

#================================================================================================

def main():

    existing_cast = []
    existing_directors = []

    write_file_prestatements()

    # create a list of fake users
    users_list  = create_user_data()
    print("Users created successfully.")

    # create a list of movies, and create all sql statements
    movies_list = get_movie_info(existing_cast, existing_directors)
    print("Movies created successfully.")

    # create a list of series, and create all sql statements
    series_list = get_series_info(existing_cast, existing_directors)
    print("Series created successfully.")

    os.system('cls')

    print(str(movies_list),'\n')
    print(str(series_list),'\n')

    # create one hundred viewings, write sql statements for them
    for i in range(100):
        create_viewed_data(users_list,movies_list,series_list)
    print("Viewings created successfully.")

    OUTFILE.close()
#=================================================================================================
def write_file_prestatements():

    # statements to delete existing data
    OUTFILE.write
    ('''DELETE FROM member;
        DELETE FROM administrator;
        DELETE FROM viewed;
        DELETE FROM user;
        DELETE FROM membership;
        DELETE FROM movie;
        DELETE FROM series;
        DELETE FROM media;
        DELETE FROM director;
        insert into membership values('1','1');
        insert into membership values('2','3');
        insert into membership values('3','5');\n''')

#=================================================================================================
def get_movie_info(existing_cast_list, existing_directors_list):
    # creating instance of IMDb
    ia = imdb.IMDb()
    
    # getting top 250 movies
    search = ia.get_top250_movies()
    
    movies_list = []

    # printing only first 25 movies title
    for i in range(NUM_TITLES):

        # try to fetch data from imdb
        try:
            # get ith title from top 250
            movie_identifier = search[i].movieID

            # get details for that title
            movie = ia.get_movie(movie_identifier)

            # get title
            movie_title = movie['title']
            movie_title = movie_title.replace('\'',"")

            # get release year
            movie_release_date = movie['year']

            # get primary genre
            movie_genre = movie['genre'][0]
            
            # get imdb link
            movie_imdb_link = ia.get_imdbURL(movie)

            # get primary director name
            director_name = movie['director'][0]

            # get birth location
            director_id = movie['director'][0].personID
            try:
                director = ia.get_person(director_id)
                place = director['birth info']['birth place']
            except KeyError as ke:
                    place = get_fake_location()
                    print(f"Creating director location for {director_name}")

            # get list of cast members to parse
            cast_members = movie['cast']

            director_data = (director_name,place)

            # prevent adding duplicate directors
            if director_data in existing_directors_list:        
               print(f"not adding {director_data}")
            else:
                create_director_data(director_name,place)
                existing_directors_list.append(director_data)

            # write respective SQL statements
            create_media_data(movie_title,movie_release_date,movie_genre,movie_imdb_link,director_name,place)
            create_movie_data(movie_title,movie_release_date,movie_genre,movie_imdb_link,director_name,place)
            create_cast_data(cast_members,movie_title,movie_release_date,cast_members)

            # track movie list to create viewing data later
            movie_tuple = (movie_title,movie_release_date)
            movies_list.append(movie_tuple)       
        except imdb.IMDbError as imerr:
             print('Uh oh!')
                
    return movies_list

#=================================================================================================
def create_director_data(dname,location):

        # write insert statement for director and location of director
        write_statement = f"insert into director values ('{dname}','{location}');\n"
        OUTFILE.write(write_statement)

#=================================================================================================
def create_media_data(mtitle,mrelease_date,mgenre,mimdb_link,mdirector,mplace):

        # wrte insert statement for media
        mtitle = mtitle.replace('\'',"")
        write_statement = f"insert into media values ('{mtitle}','{mrelease_date}','{mgenre}','{mimdb_link}','{mdirector}','{mplace}');\n"
        OUTFILE.write(write_statement)

#=================================================================================================
def create_movie_data(mtitle,mrelease_date,mgenre,mimdb_link,mdirector,mplace):

        #wrte insert statement for movie
        mtitle = mtitle.replace('\'',"")
        write_statement = f"insert into movie values ('{mtitle}','{mrelease_date}','{mgenre}','{mimdb_link}','{mdirector}','{mplace}');\n"
        OUTFILE.write(write_statement)


#=================================================================================================
def create_cast_data(mcast_list,media_title,media_date,list_of_cast):

        ccdo = imdb.IMDb()

        # get at most 3 cast members for a media
        clist_size = len(mcast_list)
        if clist_size > 2:
            clist_size = 2

        print(f"Cast size is {clist_size}")
        # write insert statement for director and location of director
        for i in range(clist_size):
            
            # get cast member i from cast list
            cast_member = mcast_list[i]

            try:
                # attempt to find cast member data
                cmember = ccdo.get_person(cast_member.personID)
                cname = cmember['name']
            except KeyError as imer:
                # if fails, make up name
                cname = get_fake_name()
                print("Got fake name.")
            finally:
                try:
                    # attempt to get cast location
                    clocation =  cmember['birth info']['birth place']
                except KeyError as e:
                    # if fails, get fake location
                    clocation = get_fake_location()
                finally:
                    # if cast member isn't aleady in cast list
                    if (cname,clocation) not in list_of_cast:

                        # insert into cast
                        write_statement = f"insert into mcast values ('{cname}','{clocation}');\n"
                        OUTFILE.write(write_statement)

                        # append to cast list
                        cast_tuple = (cname,clocation)
                        list_of_cast.append(cast_tuple) 

                    #insert into worked_on, not checked for repetition as cmember may work on several media
                    write_worked_statement = f"insert into worked_on values ('{cname}','{clocation}','{media_title}','{media_date}');\n"
                    print("Write")
                    OUTFILE.write(write_worked_statement)
                


#=================================================================================================
def get_series_info(existing_cast_list,existing_directors_list):
    
    # creating instance of IMDb
    ia = imdb.IMDb()
    
    # getting top 250 movies
    search = ia.get_top250_tv()
    
    series_list = []

    # printing only first 25 series title
    for i in range(NUM_TITLES):

        # get ith series from top 250
        series_identifier = search[i].movieID

        # get series data
        series = ia.get_movie(series_identifier)

        # get season, episode info
        ia.update(series,'episodes')
        episodes = series.data['episodes']

        # get title
        series_title = series.data['title']
        series_title = series_title.replace('\'',"")

        # get num season
        season = episodes[1]

        # get num episode
        episode = season[1]
 
        # get release year
        series_release_date = episode['year']

        # get primary genre
        series_genre = series['genre'][0]

        try:
            # try to find writer name
            series_writer = series['writer'][0]['name']
        except KeyError as e:
            # if not, make one up
            series_writer = get_fake_name()
        
        # get imdb url
        series_imdb_link = ia.get_imdbURL(series)

        # get series cast list
        series_cast = series['cast']

        # make up writer location for series because IMDb isn't reliable here
        series_dlocation = get_fake_location()

        # get total number of seasons
        num_seasons = series['number of seasons']

        director_data = (series_writer,series_dlocation)

        # prevent adding duplicate directors
        if director_data not in existing_directors_list:        
            create_director_data(series_writer,series_dlocation)
            existing_directors_list.append(director_data)

        create_media_data(series_title,series_release_date,series_genre,series_imdb_link,series_writer,series_dlocation)

        # for each season
        for i in range(num_seasons):
            season = episodes[i+1]

            # for each episode
            for j in range(len(season)):

                    # create series SQL with respective season and ep
                    create_series_data(series_title,series_release_date,i+1,j+1,series_genre,series_imdb_link,series_writer,series_dlocation)
        
        create_cast_data(series_cast,series_title,series_release_date,existing_cast_list)

        # append to series list for use in viewing data
        series_title = series_title.replace('\'',"")
        series_tuple = (series_title,series_release_date)
        series_list.append(series_tuple)
        
    return series_list


#=================================================================================================
def create_series_data(stitle,srelease_date,sseason,sepisode,sgenre,simdb_link,sdirector,splace):

    #wrte insert statement for director and location of director
    stitle = stitle.replace('\'',"")
    write_statement = f"insert into series values ('{stitle}','{srelease_date}','{sseason}','{sepisode}','{sgenre}','{simdb_link}','{sdirector}','{splace}');\n"
    OUTFILE.write(write_statement)

#=================================================================================================
def create_user_data():
    
    #   create 25 different members to insert
    user_list = []

    for i in range(24):
        person = Faker()
        fname = person.first_name()
        lname = person.last_name()

        #   gets a random email ending, such as @gmail.com
        dom = person.free_email_domain()

        #   email will always be of form first.last@randomdomain.site
        email = fname + '.' + lname + '@' + dom

        #   username will be of form first initial, last name
        uname = fname[0] + lname

        #   password will be random and between length 5-12
        pword = person.password(randint(5,12))

        #   create random phone number as Faker method occasionally adds extension to phone number
        phone = str(randint(100,999)) + '-' + str(randint(100,999)) + '-' + str(randint(1000,9999))

        address = person.address()

        #   a user is either a member or admin, and will need to be specialized accordingly
        table_choices = ['member', 'admin']

        #   assign 90% probability a user is a member, and 10% probability a user is an admin
        #                                                      (note: its possible no admins or no members may be created)
        table_probabilities = [.9,.1]

        #   get the random choice into table_list
        table_list = choices(table_choices,table_probabilities)

        #   convert it to string
        table = (table_list[0])

        #   get a random membership type
        memid = str(randint(1,3))

        #   regardless of user type, user needs inserted, then insert to specialized table based on above result
        OUTFILE.write(f"insert into user values ('{email}', '{pword}','{uname}','{address}', '{phone}');\n")
        if(table == 'admin'):
            OUTFILE.write(f"insert into administrator values ('{email}','{uname}','{address}', '{phone}');\n")
        if(table == 'member'):
            OUTFILE.write(f"insert into member values ('{email}', '{uname}','{address}', '{phone}', '0', '{memid}');\n")
            
             #   append info to userlist for use in viewed 
            user_tuple = (email,uname)
            user_list.append(user_tuple)

    return user_list
#=================================================================================================
def create_viewed_data(users_list,movies_list,series_list):

    # get random date from 2022 until today
    start_date = datetime.date(2022,1,1)
    end_date = datetime.date(2022,10,17)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)

    # make the random time match SQL format
    random_hour = str(randint(0,23)).zfill(2)
    random_min  = str(randint(0,59)).zfill(2)
    random_sec  = str(randint(0,59)).zfill(2)
    random_ns   = str(randint(0,999999)).zfill(6)

    # finalize viewtime
    viewtime = f"{random_hour}:{random_min}:{random_sec}.{random_ns}"

    # get movie or series at random
    coin_flip = randint(1,2)

    # get random user
    random_user = choices(users_list)[0]

    # depending on random flip earlier, get a random movie or get a random series
    if coin_flip == 1:
        random_viewing = choice(movies_list)
    if coin_flip == 2:
        random_viewing = choice(series_list)
    
    # user this data to create a random viewing
    write_statement = f"insert into viewed values ('{random_user[0]}','{random_user[1]}','{random_date}','{viewtime}','{random_viewing[0]}','{random_viewing[1]}');\n"
    OUTFILE.write(write_statement)

#========================================================================================================================
def get_fake_location():

    # create fake location in form us city, us state, usa
    fk = Faker()
    return fk.city() + ', ' + fk.state() + ', USA'

#========================================================================================================================
def get_fake_name():

    # create fake first and last name
    fk = Faker()
    return fk.first_name() + ' ' + fk.last_name()

#========================================================================================================================

if __name__ == "__main__":
    main()