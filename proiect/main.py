from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.textinput import TextInput
from kivy_garden.mapview import MapView, MapSource, MapMarker, MapLayer
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime, timedelta
import os
import json
from kivy.uix.image import Image
import mysql.connector

os.environ["KIVY_ORIENTATION"] = "Portrait"

mydb = mysql.connector.connect(host="sql11.freesqldatabase.com",
                                    database="sql11590631",
                                    user="sql11590631",
                                    password="ulTQ2a85l2")

mycursor=mydb.cursor()

################points and profile info####################
Window.size=(360,640)
scWidth = Window.size[0]
scHeight = Window.size[1]



new_email=""
new_password=""
UserName=""
LogIn = {}  # Initialize the LogIn dictionary
Password = ""
Name= ""
total_user_points=0
streak=1
last_completion_time=None
def week_has_passed(last_completition_time):     ####checks streak time (1 week)
    now = datetime.now()
    # Calculate the date and time one week in the future
    last_completion_time = str(last_completition_time)
    time_limit = datetime.strptime(last_completion_time, "%Y-%m-%d %H:%M:%S.%f") + timedelta(days=8)
    # Check if the current time is later than the reference time
    if now > time_limit:
        return True
    else:
        return False

def profile():   #function to pick a user's data from where it was left off and used in log in page
    global UserName
    global total_user_points
    global streak
    global last_completion_time
    if os.path.getsize('userprogress.txt') == 0:  #if folder is empty, add the default data for the user
        with open('userprogress.txt', 'w') as f:
            f.write(f'{UserName},{total_user_points},{streak},{last_completion_time}\n')
    ok = 1
    with open('userprogress.txt', 'r') as f:  # we read the file and search for the user to take it's data
        for line in f:
            values = line.strip().split(',')
            if len(values) != 4:
                continue  # skip this line if it doesn't contain three values
            name, points, streaks, time = values
            if name == UserName:  # if we find the user and it's data we save it's data in the global variables
                total_user_points = int(points)
                streak = format(round(float(streaks), 2), '.2f')
                last_completion_time = time
                ok = 0  # we end
    if ok == 1:
        with open('userprogress.txt', 'a') as f:  # if the user was just created we need to add it
            f.write(f'{UserName},{total_user_points},{streak},{"1000-01-01 20:10:1.6969"}\n')
        profile()

def update_data():    #Function to update data when changing something like getting points
    global UserName
    global total_user_points
    global streak
    global last_completion_time
    #Finally we update user's new data
    # Open the file in read mode and read all lines into a list
    with open('userprogress.txt', 'r') as f:
        lines = f.readlines()
    # Modify the line that matches the username
    for i, line in enumerate(lines):
        name, _, _, _ = line.strip().split(',')
        if name == UserName:
            lines[i] = f'{UserName},{total_user_points},{streak},{last_completion_time}\n'
            break
    # Open the file in write mode and write the modified lines back to the file
    with open('userprogress.txt', 'w') as f:
        f.writelines(lines)
############################################################
# Main page with a label that animates by moving up and down
global UserEmail
class WhoAreYou(Screen):
    def check_login(self, username_input, password_input):
        global UserName
        global UserEmail
        userf = username_input
        passf = password_input
        if userf and passf:
            mycursor.execute("select * from people_accounts where email = '{0}'".format(userf))
            result = mycursor.fetchall()
            if result:
                UserEmail = result[0][1]
                if result[0][2] == passf:
                    self.parent.current = 'map'
                    UserName = str(result[0][0])
                    profile()
                else:
                    wrong_credentials = Popup(title="Error",
                                              content=Label(text="Invalid e-mail or password!",
                                                            color='green'),
                                              background='images/green.png',
                                              title_color=(51 / 255, 102 / 255, 0, 1),
                                              title_size=25,
                                              size_hint=(0.7, 0.3))
                    wrong_credentials.open()
            else:
                wrong_credentials = Popup(title="Error",
                                          content=Label(text="Invalid e-mail or password!",
                                                        color='green'),
                                          background='images/green.png',
                                          title_color=(51 / 255, 102 / 255, 0, 1),
                                          title_size=25,
                                          size_hint=(0.7, 0.3))
                wrong_credentials.open()
        else:
            wrong_credentials = Popup(title="Error",
                                      content=Label(text="Please fill all the blank spaces!",
                                                    color='black'),
                                      background='images/green.png',
                                      title_color=(51 / 255, 102 / 255, 0, 1),
                                      title_size=25,
                                      size_hint=(0.7, 0.3))
            wrong_credentials.open()

class CreateAccount(Screen):
    def save_account(self, email, password, name):
        global UserName
        emailf = str(email)
        passwordf = str(password)
        namef = str(name)
        if emailf and passwordf and namef:
            try:
                mycursor.execute("insert into people_accounts (name,email,password) values (%s, %s, %s)",
                                 (namef, emailf, passwordf))
                self.parent.current = 'who'
            except:
                error_popup = Popup(title="Error",
                                    title_color=(51 / 255, 102 / 255, 0, 1),
                                    title_size=25,
                                    content=Label(text="Email already in use!", color="black"),
                                    background='images/green.png',
                                    size_hint=(0.7, 0.3))
                error_popup.open()
            mydb.commit()
        else:
            error_popup = Popup(title="Error",
                                title_color=(51 / 255, 102 / 255, 0, 1),
                                title_size=25,
                                content=Label(text="Please fill all the blank spaces", color="black"),
                                background='images/green.png',
                                size_hint=(0.7, 0.3))
            error_popup.open()

# Map screen with markers and associated messages
flag_for_1execution = True
marker_info = {}  # dictionary to store saved marker information
flag_for_1execution = True  #i use this flag to not be able to click and create infinite instances of marker descriptions
deleted_marker=False #i create a flag to know if i deleted a created marker so it won't get saved in the file

latitude=None
longitude=None
CENTER_MAP_FLAG=0

class Map(Screen):     #you need to install mapview    (pip install mapview)                 #also install garden (garden install mapview ) in terminal
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = FloatLayout(size_hint=(1, 1),
                             pos_hint={'x': 0, 'y': 0},)

        mapview = MapView(  #this is the map and i set the coordinates of timisoara
            lat=45.755778,
            lon=21.229327,

            zoom=10,
            map_source=MapSource("https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",max_zoom=18,
                             min_zoom=12))  # here i set the zoom limits so you cannot zoom out to globe level

        def center_map(self):
            global CENTER_MAP_FLAG
            global latitude
            global longitude
            if CENTER_MAP_FLAG==1:
                mapview.center_on(latitude,longitude)
                mapview.zoom=15
                CENTER_MAP_FLAG=0
        self.bind(on_enter=center_map)

        marker_text={}  #this dictionary keeps track of what message has every marker
        markerpopups = {}  #this dictionary will keep track of every marker on the map and what to popup
        marker_popup = {}


        add_page_btn = Button(pos=(0, 0), background_normal='images/plus_buton_stanga.png',
                               size=(scWidth / 2, scHeight / 7))

        profile_page_btn = Button(pos=(scWidth / 2, 0), background_normal='images/user_buton_dreapta.png',
                                  size=(scWidth / 2, scHeight / 7))

        list_page_btn = Button(pos=((scWidth / 2 - scWidth / 8), scHeight / 50),
                              background_normal='images/map_middle_button.png',
                              size=(scWidth / 4, scWidth / 4), border=(-1, -1, -1, -1))



        mapview.add_widget(add_page_btn)
        mapview.add_widget(profile_page_btn)
        mapview.add_widget(list_page_btn)

        def on_profile_page_btn_click(instance):
            self.parent.current = 'profile'
        profile_page_btn.bind(on_press=on_profile_page_btn_click)

        def on_add_page_btn_click(instance):
            popup_feature = Popup(title="Error",
                                  content=(Label(text="You must be an ONG to use this feature",
                                                 color='green')),
                                 title_color='green',
                                 title_size=20,
                                 size_hint=(0.8, 0.5),
                                 background='images/green.png')
            popup_feature.open()
        add_page_btn.bind(on_press=on_add_page_btn_click)

        def on_list_page_btn_click(instance):
            self.parent.current = 'list'
        list_page_btn.bind(on_press=on_list_page_btn_click)




        def load_markers():
            with open("marker_data.json", "r") as f:
                data = json.load(f)
            marker_info = data["markers"]
            global marker_popup
            for uid, marker_data in marker_info.items():
                user = marker_data["user"]
                lat = marker_data["lat"]
                lon = marker_data["lon"]
                description = marker_data["description"]

                # create a MapMarkerPopup for the marker
                marker_saved = MapMarker(lat=lat,lon=lon,source='images/savedmarker.png', size_hint=(0.01, 0.01))

                mapview.add_marker(marker_saved)

                marker_popup_layout = BoxLayout(orientation='vertical')

                # Create a Label for displaying text
                label = Label(text=description, color=(133/255, 160/255, 129/255, 1))

                marker_popup_layout.add_widget(label)

                button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))

                delete_button = Button(text='Delete', size_hint=(0.5, 1),background_color=(185/255, 206/255, 163/255,1))

                complete_button = Button(text='Completed', size_hint=(0.5, 1),background_color=(185/255, 206/255, 163/255,1))

                button_layout.add_widget(delete_button)
                button_layout.add_widget(complete_button)

                marker_popup_layout.add_widget(button_layout)

                markerpopups[marker_saved] = Popup(title="What's going on here?",
                                                  # we set what to pop up when we click the saved marker
                                                  title_color=(165/255,186/255,167/255,1),
                                                  content=marker_popup_layout,
                                                  size_hint=(0.8, 0.5),
                                                  background_color=(185/255, 206/255, 163/255,1))  # popup backrgound wich is an image
                marker_saved.bind(on_release=markerpopups[marker_saved].open)

            def delete_marker(marker):

                mapview.remove_marker(marker)  # remove the marker from the map
                markerpopups[marker].dismiss()

                # load the data from the file
                with open("marker_data.json", "r") as f:
                    data = json.load(f)
                marker_info = data["markers"]

                # find the marker in the data and delete it
                for uid, marker_data in marker_info.items():
                    if marker_data["lat"] == marker.lat and marker_data["lon"] == marker.lon:
                        marker_info.pop(uid, None)
                        break

                # save the updated data back to the file
                with open("marker_data.json", "w") as f:
                    data["markers"] = marker_info
                    json.dump(data, f)

                empty_map=MapLayer()
                mapview.add_layer(empty_map)

                mapview.active_layer=empty_map
                self.__init__()

            def delete_button1(instance):
                # get the marker data for the marker associated with the delete button
                with open("marker_data.json", "r") as f:
                    data = json.load(f)
                marker_info = data["markers"]
                for uid, marker_data in marker_info.items():
                    if marker_data["lat"] == instance.marker.lat and marker_data["lon"] == instance.marker.lon:
                        # check if the user value in the marker data is the same as the UserName variable
                        if marker_data["user"] == UserName:
                            delete_marker(instance.marker)  # delete the marker
                            try:
                                markerpopups[instance.marker].dismiss()  # close the popup
                            except:
                                pass
                        else:
                            not_allowed_popup=Popup(title="Error",content=(Label(text="You didn`t create this activity.\nYou cannot delete it!",color='green')),title_color='green',     #we set what to pop up when we click the saved marker
                                      title_size=30,
                                      size_hint=(0.8, 0.5),
                                      background='images/green.png')
                            not_allowed_popup.open()
                        break
            # update the delete button to call delete_button1 when clicked
            delete_button.bind(on_press=delete_button1)

            # add a marker attribute to the delete button
            delete_button.marker = marker_saved

            ######################          #################################


            def completed(marker):
                delete_marker(marker)
                global total_user_points
                global streak
                global UserName
                global last_completion_time
                reward_label = Label(text='You won {points_reward} points', color='green',
                                     font_size=15)  # create custom text for popup method 1
                if week_has_passed(last_completion_time):
                    streak = 1.00
                    streak_formatted = format(round(float(streak), 2), '.2f')
                    streak = float(streak_formatted)
                else:
                    streak_formatted = format(round(float(streak), 2), '.2f')
                    streak = float(streak_formatted)
                last_completion_time = datetime.now()
                total_points_formatted = format(round(float(total_user_points), 2), '.2f')
                total_user_points = int(float(total_points_formatted) + 100 * float(streak))
                reward_label.text = reward_label.text.format(points_reward=100 * streak)
                streak = float(streak_formatted) + 0.2
                ###########################################################
                # update user progress
                update_data()
                #################################################################
                reward_popup = Popup(title="Congratulations " + str(UserName) + "!",
                                     # create custom text for popup Method 2
                                     title_color='green',
                                     # we set what to pop up when we click the saved marker
                                     title_size=20,
                                     size_hint=(0.8, 0.5),
                                     content=reward_label,
                                     background='images/green.png')
                reward_popup.open()  # we open the reward popup
            def completed_marker(instance):

                with open("marker_data.json", "r") as f:
                    data = json.load(f)
                marker_info = data["markers"]
                for uid, marker_data in marker_info.items():
                    if marker_data["lat"] == instance.marker.lat and marker_data["lon"] == instance.marker.lon:
                        # check if the user value in the marker data is the same as the UserName variable
                        if marker_data["user"] != UserName:
                            completed(instance.marker)  # delete the marker
                            try:
                                markerpopups[instance.marker].dismiss()  # close the popup
                            except:
                                pass
                        else:
                            not_allowed1_popup = Popup(title="Error", content=(Label(
                                text="You created this activity.\nYou cannot complete it!",
                                color='green')),
                                                       title_color='green',
                                                       # we set what to pop up when we click the saved marker
                                                       title_size=30,
                                                       size_hint=(.8, 0.5),

                                                       background='images/green.png')
                            not_allowed1_popup.open()
                        break


            ##############################################################################
            # for each marker in marker_info, create a delete button and bind it to delete_button1

            for uid, marker_data in marker_info.items():
                marker_saved = MapMarker(lat=marker_data["lat"], lon=marker_data["lon"],
                                         source='images/savedmarker.png', size_hint=(0.01, 0.01))

                mapview.add_marker(marker_saved)

                marker_popup_layout = BoxLayout(orientation='vertical',size_hint=(1,1))

                # Create a Label for displaying text
                label = Label(text=marker_data["description"], color='green')

                marker_popup_layout.add_widget(label)
                button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
                delete_button = Button(text='Delete', size_hint=(0.2, 0.1), background_color = (214, 233, 202, 0.03),color='green')
                complete_button = Button(text='Done', size_hint=(0.2, 0.1),background_color = (214, 233, 202, 0.03),color='green')
                button_layout.add_widget(delete_button)
                button_layout.add_widget(complete_button)
                marker_popup_layout.add_widget(button_layout)

                markerpopups[marker_saved] = Popup(title="What's going on here?",
                                                   # we set what to pop up when we click the saved marker
                                                   title_color='green',
                                                   content=marker_popup_layout,
                                                   size_hint=(0.5, 0.5),
                                                   background='images/green.png')  # popup
                # bind the marker to the popup
                marker_saved.bind(on_release=markerpopups[marker_saved].open)
                # update the delete button to call delete_button1 when clicked
                delete_button.bind(on_press=delete_button1)
                complete_button.bind(on_press=completed_marker)
                delete_button.marker = marker_saved
                complete_button.marker = marker_saved
            delete_button.bind(on_press=delete_button1)
        with open("marker_data.json", "r") as f:
            data = json.load(f)
        marker_info = data["markers"]
        # check if the marker_info dictionary is empty
        if marker_info:
            load_markers()

        def on_click(instance, touch):
            if instance.collide_point(
                    *touch.pos) and touch.is_double_tap:  # Get the latitude and longitude of the click and only get the coordinates if it is a click, not zoom or pan
                lat, lon = mapview.get_latlon_at(*touch.pos)  # we get latitude and longitude of the coords
                marker = MapMarker(lat=lat, lon=lon, )  # created a marker and added it to the MapView
                mapview.add_marker(marker)
                # mapview.center_on(lat, lon)   #with this function we could make the screen focus on where we click
                x, y = touch.pos
                # creating two buttons for the marker (one to set an activity there and one to remove the marker and cancel the action)
                btn = Button(text="What`s here?", pos=(x + 30, y + 10), color=(133 / 255, 160 / 255, 129 / 255, 1),
                             bold=True, size_hint=(0.1, 0.1), size=(100, 30),
                             background_color=(185 / 255, 206 / 255, 163 / 255, 1), font_size=9, background_normal=(""))
                # if we click this button we can add info on that point
                removebtn = Button(text="x", pos=(x - 45, y + 10), color=(133 / 255, 160 / 255, 129 / 255, 1),
                                   size_hint=(0.1, 0.1), size=(30, 30),
                                   background_color=(185 / 255, 206 / 255, 163 / 255, 1), font_size=20,
                                   background_normal=(""))
                # if we click this button we close the marker creation

                screen_width = Window.width  # we save the sizes of the screen
                screen_height = Window.height

                # ##pop upul
                # box = BoxLayout(orientation='vertical', padding=(10))
                #
                # box.add_widget(TextInput(text="Name of event", background_color=(0, 0, 1, 0)))
                # save_btn = Button(text='Save', size_hint=(0.1, 0.1), pos_hint={'center_x': 0.5, 'center_y': 1},
                #                   background_color=(0, 0, 1, 0),
                #                   color='black')
                # box.add_widget(save_btn)
                # add_event = Popup(title="Event",
                #                   content=box,
                #                   background='images/green.png', title_color=(51 / 255, 102 / 255, 0, 1),
                #                   title_size=25,
                #                   size_hint=(0.5, 0.5))
                # add_event.open()
                #
                # save_btn.bind(on_press=add_event.dismiss)
                ##########################################################

                def on_btn_click(instance):  # in this function we say what will happen when we will click the button
                    global flag_for_1execution  # we initialize the global flag in this function
                    global deleted_marker
                    if flag_for_1execution is False:  # i use this variable to fix the bug where i can create infinite TextInputs
                        return

                    flag_for_1execution = True

                    global markerinput  # we create a text input to save what is described at that marker
                    global savebtn  # and the save button to save what we wrote

                    markerinput = TextInput(hint_text="Enter description here",

                                            size=(scWidth / 2, scHeight / 2),
                                            pos=(scWidth / 4, scHeight / 4),
                                            background_color=(185 / 255, 206 / 255, 163 / 255, 1)
                                            )

                    savebtn = Button(text="Save",
                                     pos=(scWidth / 4, scHeight / 4),
                                     color=(0, 0, 0, 1),
                                     size_hint=(1, 1),
                                     size=(scWidth / 2, 15),
                                     background_normal=(""),
                                     background_color=(185 / 255, 206 / 255, 163 / 255, 1),
                                     font_size=20)

                    # we add those widgets
                    mapview.add_widget(markerinput)
                    mapview.add_widget(savebtn)
                    flag_for_1execution = False  # we remake the flag false so we cannot keep on clicking and getting infinite instances of markers

                    ########## this function tells what happens when we press save #############
                    def on_savebtn_click(instance):  # here we say what happend when we click save
                        global deleted_marker
                        deleted_marker = False
                        global flag_for_1execution
                        on_removebtn_click(instance)  # we close everything related to the marker with this function
                        # savedmarker variable represents the green saved marker
                        savedmarker = MapMarker(lat=lat, lon=lon, source='images/savedmarker.png',
                                                size_hint=(0.01, 0.01))  # created a marker and added it to the MapView
                        mapview.add_marker(savedmarker)  # here we replace the red marker with a green one that means here something is saved

                        marker_text[savedmarker] = markerinput.text  # we use dictionaries so that every marker has it's own input text and to be able to save multiple working markers

                        # Create a vertical BoxLayout to hold the text and buttons
                        marker_popup_layout = BoxLayout(orientation='vertical')

                        # Create a Label for displaying text
                        label = Label(text=marker_text[savedmarker],  color=(32 / 255, 32 / 255, 32 / 255, 1))

                        # Add the Label to the layout
                        marker_popup_layout.add_widget(label)

                        # Create a BoxLayout to hold those 2 buttons
                        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
                        # Create the "Delete" button

                        markerpopups[savedmarker] = Popup(title="What's going on here?",
                                                          # we set what to pop up when we click the saved marker
                                                          title_color=(0.1, 0, 0.1, 1),
                                                          content=marker_popup_layout,
                                                          size_hint=(0.5, 0.5),

                                                          background_color=(165 / 255, 186 / 255, 167 / 255,
                                                                            1))  # popup backrgound wich is an image

                        savedmarker.bind(on_release=markerpopups[
                            savedmarker].open)  # we tell when the functions activates (on click)
                        flag_for_1execution = True  # after something was saved we can create another marker

                        #######################################
                        def save_markers():
                            with open("marker_data.json", "r") as f:
                                data = json.load(f)
                            marker_info = data["markers"]

                            marker_info[savedmarker.uid] = {
                                # here i make a dictionary with all of the new markers info to save it for next time
                                "user": UserName,
                                "lat": lat,
                                "lon": lon,
                                "description": marker_text[savedmarker],

                            }
                            # save marker information to a file

                            with open("marker_data.json", "w") as f:
                                data = {"markers": marker_info}
                                json.dump(data, f)

                        save_markers()
                        load_markers()

                    #################################

                    savebtn.bind(
                        on_press=on_savebtn_click)  # we bind the function instructions to the 'on_press' so that it knows to execute the function when we press the button

                btn.bind(
                    on_press=on_btn_click)  # same, this tells that the above function will be activated if button btn is clicked
                # Add the button as a widget to the MapView
                mapview.add_widget(btn)  # makes the buttons visible
                mapview.add_widget(removebtn)  # same

                ###############################################
                def on_removebtn_click(instance):  # function to remove the marker and the buttons from the MapView
                    global deleted_marker
                    deleted_marker = True
                    try:
                        mapview.remove_widget(markerinput)  # if those were created, delete them too
                        mapview.remove_widget(savebtn)
                    except:
                        pass
                    global flag_for_1execution
                    flag_for_1execution = True
                    # Remove the other widgets from the MapView
                    mapview.remove_widget(btn)  # always delete those when pressing x
                    mapview.remove_marker(marker)
                    mapview.remove_widget(removebtn)

                ############################################### end of on_removebtn_click function
                ################################################################## end of on_savebtn_click function
                removebtn.bind(
                    on_press=on_removebtn_click)  # this tell that the above function will be activated if button removebtn is clicked

        mapview.bind(on_touch_down=on_click)  # this activates the big on_click function
        self.add_widget(layout)  # we add whole mapview to screen
        # Clock.schedule_interval(refresh_function, 1)
        ########################################################################### end of on_click function









        self.add_widget(mapview)    #we add whole mapview to screen
        ########################################################################### end of on_click function





class Profile(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global UserName
        global total_user_points
        global streak
        global last_completion_time

        layout = FloatLayout(size=(scWidth, scHeight))

        plus_page_btn = Button(pos_hint={'x': 0, 'y': 0}, background_normal='images/plus_buton_stanga.png',
                               size_hint=(0.5, 0.14))
        profile_page_btn = Button(pos_hint={'x': 0.5, 'y': 0}, background_normal='images/user_buton_dreapta.png',
                                  size_hint=(0.5, 0.14))
        map_page_btn = Button(pos_hint={'center_x': 0.5, 'y': 0.02}, background_normal='images/map_middle_button.png',
                              size_hint=(0.25, (0.25 * (scWidth / scHeight))), border=(-1, -1, -1, -1))

        title_label = Label(text='My Profile', font_size=30, size_hint=(0.2, 0.2),
                            pos_hint={'center_x': 0.5, 'center_y': 0.9}, color=('green'), bold=True)
        background = Image(source='images/green.png', allow_stretch=True, keep_ratio=False, size=self.size,
                           pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.name_label = Label(text=self.get_name_label_text(), font_size=23, size_hint=(1, 0.1),
                                pos_hint={'center_x': 0.5, 'center_y': 0.8}, color=('green'))
        self.points_label = Label(text=self.get_points_label_text(), font_size=23, size_hint=(1, 0.1),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.7}, color=('green'))
        self.streak_label = Label(text=self.get_streak_label_text(), font_size=23, size_hint=(1, 0.1),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.6}, color=('green'))
        self.activity_label = Label(text=self.get_activity_label_text(), font_size=23, size_hint=(1, 0.1),
                                    pos_hint={'center_x': 0.5, 'center_y': 0.5}, color=('green'))
        logout_button = Button(text='Log Out', pos_hint={'center_x': 0.9, 'center_y': 0.9}, size_hint=(0.3, 0.2),
                             background_color=(214, 233, 202, 0.03), color='green')

        rewards_button = Button(pos_hint={'center_x': 0.1, 'center_y': 0.9}, size_hint=(0.3, 0.15),
                             background_normal='images/reward.png')

        def on_logout_button_press(instance):
            self.parent.current = 'who'

        logout_button.bind(on_press=on_logout_button_press)

        def on_rewards_button_press(instance):
            self.parent.current = 'rewards'
        rewards_button.bind(on_press=on_rewards_button_press)

        def on_map_button_press(instance):

            self.parent.current = 'map'

        map_page_btn.bind(on_press=on_map_button_press)

        def on_plus_page_btn_click(instance):
            popup_feature = Popup(title="Error",
                                  content=(Label(text="You must be an ONG to use this feature",
                                                 color='green')),
                                 title_color='green',
                                 title_size=20,
                                 size_hint=(0.8, 0.5),
                                 background='images/green.png')
            popup_feature.open()
        plus_page_btn.bind(on_press=on_plus_page_btn_click)


        layout.add_widget(title_label)
        layout.add_widget(self.name_label)
        layout.add_widget(self.points_label)
        layout.add_widget(self.streak_label)
        layout.add_widget(self.activity_label)
        layout.add_widget(logout_button)
        layout.add_widget(rewards_button)
        layout.add_widget(plus_page_btn)
        layout.add_widget(profile_page_btn)
        layout.add_widget(map_page_btn)

        self.add_widget(background)
        self.add_widget(layout)
        ######################## i don't know why all of this was necessary but without it it just refused to work and update the global variables
        Clock.schedule_interval(self.update_labels,
                                1)  # we set a clock for the update labels function wich we keep on resetting

    def update_labels(self, dt):          #the function we keep on resetting
        self.name_label.text = self.get_name_label_text()    #here we update the text of each label with the functions
        self.points_label.text = self.get_points_label_text()
        self.streak_label.text = self.get_streak_label_text()
        self.activity_label.text = self.get_activity_label_text()
    def get_name_label_text(self):
        return f'Name: {UserName}'   #here we add the variable to complete the text
    def get_points_label_text(self):
        return f'Total Points: {total_user_points}'
    def get_streak_label_text(self):
        return f'Streak: {streak}'
    def get_activity_label_text(self):
        return f'Last Activity Done: \n{last_completion_time}'
  #################################################################

class Rewards(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        background = Image(source='images/green.png', allow_stretch=True,
                           keep_ratio=False,
                           size=self.size,
                           pos_hint={'center_x': 0.5, 'center_y': 0.5})

        self.add_widget(background)


        # Create a grid layout to hold the rewards
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None, pos_hint={'x': 0.05, 'center_y': 0.5})
        self.grid.bind(minimum_height=self.grid.setter('height'))


        # Add the grid layout to the ScrollView
        self.add_widget(self.grid)
        title_label = Label(text='Rewards', font_size=30, size_hint=(0.2, 0.2),
                            pos_hint={'center_x': 0.5, 'center_y': 0.9}, color=('green'), bold=True)
        self.add_widget(title_label)
        profile_page_btn = Button(pos_hint={'x': 0.5, 'y': 0}, background_normal='images/user_buton_dreapta.png',
                                  size_hint=(0.5, 0.14))
        def on_profile_button_press(instance):
            self.parent.current = 'profile'
        profile_page_btn.bind(on_press=on_profile_button_press)
        self.add_widget(profile_page_btn)

        plus_page_btn = Button(pos_hint={'x': 0, 'y': 0}, background_normal='images/plus_buton_stanga.png',
                               size_hint=(0.5, 0.14))
        def on_plus_page_btn_click(instance):
            popup_feature = Popup(title="Error",
                                 title_color='green',
                                 content=(Label(text="You must be an ONG to use this feature",
                                                 color='green')),
                                 title_size=20,
                                 size_hint=(0.8, 0.5),
                                 background='images/green.png')
            popup_feature.open()
        plus_page_btn.bind(on_press=on_plus_page_btn_click)
        self.add_widget(plus_page_btn)

        map_page_btn = Button(pos_hint={'center_x': 0.5, 'y': 0.02}, background_normal='images/map_middle_button.png',
                              size_hint=(0.25, (0.25 * (scWidth / scHeight))), border=(-1, -1, -1, -1))
        def on_map_button_press(instance):
            self.parent.current = 'map'
        map_page_btn.bind(on_press=on_map_button_press)
        self.add_widget(map_page_btn)



        # Add some rewards to the grid
        self.add_reward("Reward 1", 100)
        self.add_reward("Reward 2", 200)
        self.add_reward("Reward 3", 300)
        self.add_reward("Reward 4", 400)
        self.add_reward("Reward 5", 500)

        back_button = Button(text='Back',pos_hint={'center_x': 0.9, 'center_y': 0.9}, size_hint=(0.2, 0.1), background_color=(214, 233, 202, 0.03), color='green')
        def on_back_button_press(instance):
            self.parent.current = 'profile'
        back_button.bind(on_press=on_back_button_press)
        self.add_widget(back_button)

    def add_reward(self, name, points):
        # Create a container layout for the reward
        container = GridLayout(cols=2, spacing=10, size_hint_y=None, height=60)
        container.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Create a label for the reward name
        label = Label(text=name, size_hint_x=None, width=75, color='green', bold="true")
        container.add_widget(label)

        # Create an unlock button for the reward
        button = Button(text=f"Unlock ({points} points)", size_hint_x=None, width=200,
                        background_color=(214, 233, 202, 0.03), color='green')
        button.bind(on_release=lambda btn: self.on_unlock(points))
        container.add_widget(button)

        # Add the container to the grid
        self.grid.add_widget(container)
        back_button = Button()

    def on_unlock(self, points):
        global UserName
        global total_user_points

        # Check if the user has enough points to unlock the reward
        if total_user_points >= points:
            # Deduct the points from the user's balance
            total_user_points -= points

            # Display the reward code in a popup
            popup = Popup(title="Reward unlocked!", content=(Label(text="Your reward code is 29Q9RU9VR", color='green')),
                          title_color=(51 / 255, 102 / 255, 0, 1),
                          # we set what to pop up when we click the saved marker
                          title_size=25,
                          size_hint=(0.8, 0.5),
                          background='images/green.png')
            popup.open()
            update_data()
        else:
            # Display a message if the user doesn't have enough points
            popup = Popup(title="Not enough points!", content=(
                Label(text="You don't have enough points \n    to unlock this reward.", color='green')),
                          title_color=(51 / 255, 102 / 255, 0, 1),
                          # we set what to pop up when we click the saved marker
                          title_size=25,
                          size_hint=(0.8, 0.5),
                          background='images/green.png')
            popup.open()

map_instance=Map()
class List(Map,Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ## background
        background = Image(source='images/green.png', allow_stretch=True,
                           keep_ratio=False,
                           size=self.size,
                           pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(background)
        ##making of the list
        # Create a scrollable view
        scroll = ScrollView()
        self.add_widget(scroll)

        # Create a box layout to add the list elements to
        root = FloatLayout()
        box = BoxLayout(orientation='vertical', spacing=20, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        scroll.add_widget(box)

        profile_page_btn = Button(pos_hint={'x': 0.5, 'y': 0}, background_normal='images/user_buton_dreapta.png',
                                  size_hint=(0.5, 0.14))
        def on_profile_button_press(instance):
            self.parent.current = 'profile'
        profile_page_btn.bind(on_press=on_profile_button_press)
        self.add_widget(profile_page_btn)

        plus_page_btn = Button(pos_hint={'x': 0, 'y': 0}, background_normal='images/plus_buton_stanga.png',
                               size_hint=(0.5, 0.14))
        def on_plus_page_btn_click(instance):
            popup_feature = Popup(title="Error",
                                  content=(Label(text="You must be an ONG to use this feature",
                                                 color='green')),
                                 title_color='green',
                                 title_size=20,
                                 size_hint=(0.8, 0.5),
                                 background='images/green.png')
            popup_feature.open()
        plus_page_btn.bind(on_press=on_plus_page_btn_click)
        self.add_widget(plus_page_btn)

        map_page_btn = Button(pos_hint={'center_x': 0.5, 'y': 0.02}, background_normal='images/lista_middle_button.png',
                              size_hint=(0.25, (0.25 * (scWidth / scHeight))), border=(-1, -1, -1, -1))
        def on_map_button_press(instance):
            self.parent.current = 'map'
        map_page_btn.bind(on_press=on_map_button_press)
        self.add_widget(map_page_btn)



        ## making of the function
        def add_marker_to_list(user,lat,lon,description):
            elements_box=BoxLayout(orientation='horizontal', spacing=20, size_hint_y=None)

            label=Label(text='Created by: '+user+'\n'+description,halign='center', valign='middle', color='green')
            elements_box.add_widget(label)

            link_button=Button(text='Show me', size_hint=(.5,.5), background_color=(214, 233, 202, 0.03), color='green')
            ######################

            def take_me_there(lat,lon,instance):
                global CENTER_MAP_FLAG
                CENTER_MAP_FLAG=1
                global latitude
                global longitude
                latitude=lat
                longitude=lon
                self.parent.current='map'
                self.manager.get_screen('map').__init__

            ######################
            link_button.bind(on_press=lambda x: take_me_there(lat,lon,x))
            elements_box.add_widget(link_button)

            box.add_widget(elements_box)

        ##calling the function for every marker
        def load_list(self):
            box.clear_widgets()
            with open("marker_data.json", "r") as f:
                data = json.load(f)
            marker_info = data["markers"]
            for uid, marker_data in marker_info.items():
                user = marker_data["user"]
                lat = marker_data["lat"]
                lon = marker_data["lon"]
                description = marker_data["description"]
                add_marker_to_list(user, lat, lon, description)
        self.bind(on_enter=load_list)



class MyApp(App):
        def build(self):
            sm = ScreenManager(transition=FadeTransition())         # Screen manager to switch between screens
            sm.add_widget(WhoAreYou(name='who'))
            sm.add_widget(Map(name='map'))
            sm.add_widget(Profile(name='profile'))
            sm.add_widget(CreateAccount(name='create'))
            sm.add_widget(Rewards(name='rewards'))
            sm.add_widget(List(name='list'))

            return sm

if __name__ == '__main__':
    MyApp().run()