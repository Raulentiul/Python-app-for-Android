from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.textinput import TextInput
from kivy_garden.mapview import MapView, MapSource, MapMarker
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime, timedelta
import os
from kivy.uix.image import Image
################points and profile info####################
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
    # Calculate the date and time one week in the past
    one_week_ago = now - timedelta(weeks=1)
    # Check if the current time is later than the reference time
    if last_completion_time < one_week_ago:
        return True
    else:
        return False

def profile():   #function to pick a user's data from where it was left off and used in log in page
    global UserName
    global total_user_points
    global streak
    global last_completion_time
    if os.path.getsize('userprogress.txt') == 0:  #if folder is empty, add the default data for the user
        with open('userprogress.txt','w') as f:
            f.write(f'{UserName},{total_user_points},{streak}\n')
    ok=1
    with open('userprogress.txt','r') as f:  #we read the file and search for the user to take it's data
        for line in f:
            values = line.strip().split(',')
            if len(values) != 3:
                continue  # skip this line if it doesn't contain three values
            name, points, streaks = values
            if name==UserName:    #if we find the user and it's data we save it's data in the global variables
                total_user_points=int(points)
                streak=format(round(float(streaks),2),'.2f')
                ok=0   #we end
    if ok==1:
        with open('userprogress.txt','a') as f:  #if the user was just created we need to add it
            f.write(f'{UserName},{total_user_points},{streak}\n')

def update_data():    #Function to update data when changing something like getting points
    global UserName
    global total_user_points
    global streak
    #Finally we update user's new data
    # Open the file in read mode and read all lines into a list
    with open('userprogress.txt', 'r') as f:
        lines = f.readlines()
    # Modify the line that matches the username
    for i, line in enumerate(lines):
        name, _, _ = line.strip().split(',')
        if name == UserName:
            lines[i] = f'{UserName},{total_user_points},{streak}\n'
            break
    # Open the file in write mode and write the modified lines back to the file
    with open('userprogress.txt', 'w') as f:
        f.writelines(lines)

############################################################
# Main page with a label that animates by moving up and down
class FirstPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.welcome_label = self.ids['welcome_label']

    def on_enter(self):
        Clock.schedule_interval(self.jump_animate, 0.7)

    def on_leave(self):
        Clock.unschedule(self.jump_animate)

    def jump_animate(self, dt):
        anim = Animation(pos_hint={"center_y": 0.52}, duration=0.40)
        anim += Animation(pos_hint={"center_y": 0.48}, duration=0.30)
        anim.start(self.welcome_label)

# Empty screen
class SecondPage(Screen):
    pass

# Screen with a text input for the user to enter their name
class WhoAreYou(Screen):
    def check_login(self, username_input, password_input):
        LogIn = {}  # Declare LogIn as a local variable
        global UserName
        with open('userdata.txt', 'r') as f:
            for line in f:
                username, password, name = line.strip().split(',')
                LogIn[username] = password
        # Check if the username and password provided by the user match the ones in the LogIn dictionary
        if username_input in LogIn and password_input == LogIn[username_input]:    #if the login credentials exist
            with open('userdata.txt','r') as f:       #we redo the search as above
                for line in f:
                    username, password, name = line.strip().split(',')
                    if username==username_input:  #when we find the profile we take it's Name
                        UserName = str(name)      #based on the name we are going to save the progress
            self.parent.current = 'main'
            profile()
        else:
            wrong_credentials = Popup(title="Error", content=Label(text="Invalid e-mail or password!",color='black'), background='images/green.png', title_color=(51/255,102/255,0,1),
                                      title_size=25,
                                      size_hint=(0.5, 0.5))
            wrong_credentials.open()

class CreateAccount(Screen):
    def save_account(self,email,password,name):
        global UserName
        email = str(email)
        password = str(password)
        name=str(name)
        with open('userdata.txt', 'a') as f:   #we open the file as append so we can keep on adding
            f.write(f'{email},{password},{name}\n')
        self.parent.current = 'who'

# Map screen with markers and associated messages
flag_for_1execution = True  #i use this flag to not be able to click and create infinite instances of marker descriptions
class Map(Screen):     #you need to install mapview    (pip install mapview)                 #also install garden (garden install mapview ) in terminal
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        mapview = MapView(  #this is the map and i set the coordinates of timisoara
            lat=45.755778,
            lon=21.229327,
            zoom=11,
            map_source=MapSource(max_zoom=18, min_zoom=12))          #here i set the zoom limits so you cannot zoom out to globe level

        marker_text={}  #this dictionary keeps track of what message has every marker
        markerpopups = {}  #this dictionary will keep track of every marker on the map and what to popup

        ############################################################
        # function to take me back on first page
        main_page_btn = Button(text="Back", pos_hint={'x': 0, 'y': 1}, size=(50,50), size_hint=(0.1, 0.1))
        mapview.add_widget(main_page_btn)
        def on_main_page_btn_click(instance):
            self.parent.current = 'main'
        main_page_btn.bind(on_press=on_main_page_btn_click)
        ###################################################################

        ######## Function that is executed when we double click the map ###########
        def on_click(instance, touch):
            if instance.collide_point(*touch.pos) and touch.is_double_tap:                     # Get the latitude and longitude of the click and only get the coordinates if it is a click, not zoom or pan
                lat, lon = mapview.get_latlon_at(*touch.pos)   #we get latitude and longitude of the coords
                marker = MapMarker(lat=lat, lon=lon)            # created a marker and added it to the MapView
                mapview.add_marker(marker)
                #mapview.center_on(lat, lon)   #with this function we could make the screen focus on where we click
                x,y=touch.pos
                # creating two buttons for the marker (one to set an activity there and one to remove the marker and cancel the action)
                btn = btn = Button(text="What's happening here?",pos=(x+25,y), color=(0.2, 1, 0.1, 1), size_hint=(0.1, 0.1), size=(300,50), background_color=(0, 0, 0, 0.7), font_size=20)
                #if we click this button we can add info on that point
                removebtn= Button(text="X",pos=(x-75,y) ,color= (0, 0, 0, 1),size_hint= (0.1, 0.1),size=(50,50),background_color= (1, 1, 1, 1),font_size=20)
                # if we click this button we close the marker creation

                screen_width = Window.width  #we save the sizes of the screen
                screen_height = Window.height
                ##########################################################
                def on_btn_click(instance):  #in this function we say what will happen when we will click the button
                    global flag_for_1execution #we initialize the global flag in this function

                    if flag_for_1execution is False:   #i use this variable to fix the bug where i can create infinite TextInputs
                        return

                    flag_for_1execution=True

                    global markerinput       #we create a text input to save what is described at that marker
                    global savebtn           #and the save button to save what we wrote

                    markerinput = TextInput(text="Enter description here",size_hint= (0.3, 0.3),pos_hint= {'center_x': 1, 'center_y': 1}, background_color=(0,1,0,0.6),foreground_color= 'black',size=(400,150))
                    mapview.add_widget(markerinput)
                    savebtn=Button(text="Save",pos_hint= {'center_x': 0.6, 'center_y': 0.3} ,color= (0, 0, 0, 1),size_hint= (0.3, 0.1),size=(400,50),background_color= (0, 1, 0, 0.6),font_size=20)
                    mapview.add_widget(savebtn)         #we add those widgets

                    flag_for_1execution=False    #we remake the flag false so we cannot keep on clicking and getting infinite instances of markers
                    ########## this function tells what happens when we press save #############
                    def on_savebtn_click(instance):  #here we say what happend when we click save
                        global flag_for_1execution
                        on_removebtn_click(instance)     #we close everything related to the marker with this function
                        #savedmarker variable represents the green saved marker
                        savedmarker = MapMarker(lat=lat, lon=lon,source='images/savedmarker.png',size_hint=(0.01, 0.01))  # created a marker and added it to the MapView
                        mapview.add_marker(savedmarker)                                                         #here we replace the red marker with a green one that means here something is saved

                        marker_text[savedmarker] = markerinput.text  # we use dictionaries so that every marker has it's own input text and to be able to save multiple working markers

                        # Create a vertical BoxLayout to hold the text and buttons
                        marker_popup_layout = BoxLayout(orientation='vertical')
                        # Create a Label for displaying text
                        label = Label(text=marker_text[savedmarker],color=(32/255,32/255,32/255,1))
                        # Add the Label to the layout
                        marker_popup_layout.add_widget(label)
                        # Create a BoxLayout to hold those 2 buttons
                        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
                        # Create the "Delete" button
                        delete_button = Button(text='Delete', size_hint=(0.5, 1))
                        #Add delete button function and binded it
                        def on_delete_click(instance):
                            mapview.remove_marker(savedmarker)
                            markerpopups[savedmarker].dismiss()
                        delete_button.bind(on_press=on_delete_click)
                        # Create the "Save" button
                        complete_button = Button(text='Completed', size_hint=(0.5, 1))
                        #Create the complete button function and add points
                        def action_completed(instance):
                            on_delete_click(instance)   #if action completed we delete everything
                            global total_user_points
                            global streak
                            global UserName
                            global last_completion_time
                            reward_label=Label(text='You won {points_reward} points',color=(32/255,32/255,32/255,1),font_size=30)   #create custom text for popup method 1
                            reward_label.text = reward_label.text.format(points_reward=100 * float(streak))
                            if last_completion_time is not None and week_has_passed(
                                    last_completion_time):  # if a week from last completion has passed
                                streak = 1  # reset the streak
                            else:
                                streak_formatted = format(round(float(streak), 2), '.2f')
                                streak = float(streak_formatted) + 0.2
                            last_completion_time = datetime.now()
                            total_points_formatted = format(round(float(total_user_points), 2), '.2f')
                            total_user_points = int(float(total_points_formatted) + 100 * float(streak))
                            ###########################################################
                            #update user progress
                            update_data()
                            #################################################################
                            reward_popup=Popup(title="Congratulations "+str(UserName)+"!",    #create custom text for popup Method 2
                                      title_color=(51/255,102/255,0,1),     #we set what to pop up when we click the saved marker
                                      title_size=25,
                                      size_hint=(0.5, 0.5),
                                      content=reward_label,
                                      background='images/green.png')
                            reward_popup.open()   #we open the reward popup
                        complete_button.bind(on_press=action_completed)   #we bind the function to completed button

                        # Add the buttons to the layout
                        button_layout.add_widget(delete_button)
                        button_layout.add_widget(complete_button)
                        # Add the button layout to the main layout
                        marker_popup_layout.add_widget(button_layout)

                        markerpopups[savedmarker] = Popup(title="What's going on here?",  #we set what to pop up when we click the saved marker
                                                          title_color=(0.1, 0, 0.1, 1),
                                                          content=marker_popup_layout,
                                                          size_hint=(0.5, 0.5),
                                                          background='images/green.png')   #popup backrgound wich is an image

                        savedmarker.bind(on_release=markerpopups[savedmarker].open)    #we tell when the functions activates (on click)
                        flag_for_1execution=True       #after something was saved we can create another marker
                    savebtn.bind(on_press=on_savebtn_click)     #we bind the function instructions to the 'on_press' so that it knows to execute the function when we press the button
                btn.bind(on_press=on_btn_click)     #same, this tells that the above function will be activated if button btn is clicked
                # Add the button as a widget to the MapView
                mapview.add_widget(btn)  #makes the buttons visible
                mapview.add_widget(removebtn) #same
                ###############################################
                def on_removebtn_click(instance):  # function to remove the marker and the buttons from the MapView
                    try:
                        mapview.remove_widget(markerinput)   #if those were created, delete them too
                        mapview.remove_widget(savebtn)
                    except:
                        pass
                    global flag_for_1execution
                    flag_for_1execution=True
                    # Remove the other widgets from the MapView
                    mapview.remove_widget(btn)     #always delete those when pressing x
                    mapview.remove_marker(marker)
                    mapview.remove_widget(removebtn)
                ############################################### end of on_removebtn_click function
                ################################################################## end of on_savebtn_click function
                removebtn.bind(on_press=on_removebtn_click)  #this tell that the above function will be activated if button removebtn is clicked
        mapview.bind(on_touch_down=on_click) #this activates the big on_click function
        self.add_widget(mapview)    #we add whole mapview to screen
        ########################################################################### end of on_click function

class MainPage(Screen):
        pass

class Profile(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global UserName
        global total_user_points
        global streak
        global last_completion_time

        layout = BoxLayout(orientation='vertical', padding=10)
        title_label = Label(text='My Profile', font_size=30, size_hint=(1, 0.1),pos_hint={'center_x':0.2,'center_y':0.5},color=('green'),bold=True)
        background = Image(source='images/green.png', allow_stretch=True, keep_ratio=False, size=self.size, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.name_label = Label(text=self.get_name_label_text(), font_size=23, size_hint=(1, 0.1),pos_hint={'center_x':0.2,'center_y':0.5},color=('green'))
        self.points_label = Label(text=self.get_points_label_text(), font_size=23, size_hint=(1, 0.1),pos_hint={'center_x':0.2,'center_y':0.5},color=('green'))
        self.streak_label = Label(text=self.get_streak_label_text(), font_size=23, size_hint=(1,0.1),pos_hint={'center_x':0.2,'center_y':0.5},color=('green'))
        self.activity_label=Label(text=self.get_activity_label_text(), font_size=23, size_hint=(1,0.1),pos_hint={'center_x':0.35,'center_y':0.5},color=('green'))
        back_button = Button(text='Back', size_hint=(1, 0.1), background_color=(1, 1, 1, 0.03), color='black')
        def on_back_button_press(instance):
            self.parent.current = 'main'
        back_button.bind(on_press=on_back_button_press)
        layout.add_widget(title_label)
        layout.add_widget(self.name_label)
        layout.add_widget(self.points_label)
        layout.add_widget(self.streak_label)
        layout.add_widget(self.activity_label)
        layout.add_widget(back_button)
        self.add_widget(background)
        self.add_widget(layout)
     ######################## i don't know why all of this was necessary but without it it just refused to work and update the global variables
        Clock.schedule_interval(self.update_labels, 1)   # we set a clock for the update labels function wich we keep on resetting

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
        return f'Last Activity Done: {last_completion_time}'
  #################################################################

class MyApp(App):
        def build(self):
            sm = ScreenManager(transition=FadeTransition())         # Screen manager to switch between screens
            sm.add_widget(FirstPage(name='first'))                  #this is how we add the classes as screens
            sm.add_widget(SecondPage(name='second'))                #each one has a 'name' that we use to go from one to another
            sm.add_widget(WhoAreYou(name='who'))
            sm.add_widget(MainPage(name='main'))
            sm.add_widget(Profile(name='profile'))
            sm.add_widget(Map(name='map'))
            sm.add_widget(CreateAccount(name='create'))
            return sm

if __name__ == '__main__':
    MyApp().run()