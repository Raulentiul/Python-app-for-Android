from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.pagelayout import PageLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager,Screen,FadeTransition, SwapTransition, WipeTransition, NoTransition, CardTransition,SlideTransition
from kivy.uix.textinput import TextInput
from kivy.animation import Animation
from kivy.clock import Clock

class FirstPage(Screen):   #this is the main page, the one that says Welcome
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.welcome_label = self.ids['welcome_label']  #we create an object that represents the label

    def on_enter(self):       # Start the animation when the screen is entered
        Clock.schedule_interval(self.jump_animate, 0.7)

    def on_leave(self):     # Stop the animation when the screen is left
        Clock.unschedule(self.jump_animate)

    def jump_animate(self,dt):  #We create the jump animation
        anim=Animation(pos_hint={"center_y": 0.52},duration=0.40)   #here we adjust how much the text goes up and for how long
        anim+=Animation(pos_hint={"center_y": 0.48},duration=0.30)  #-||- down
        # Start the animation
        anim.start(self.welcome_label)

class SecondPage(Screen):
    pass

class WhoAreYou(Screen):
    def save_name(self,username_input):
        self.UserName = str(username_input)    #we save in UserName the name of the user so we can use it when we talk to the person
        print(self.UserName)


#fiecare clasa de mai sus reprezinta o pagina
#o pagina noua inseamna sa creezi o clasa noua si mai jos sa o initializezi precum sunt celelalte
# ce nume primeste in ghilimele acela il folosesti cand creezi un buton sa mearga de pe o pagina anterioara la cea noua creata
#(butoanele si tot ce vezi pe pagini sunt in .kv file)
#fiecare pagina este apelata in .kv file ex: <FirstPage>,<SecondPage>

class MyApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition(duration=1))             #here u add more pages by this format
        sm.add_widget(FirstPage(name='first'))                       # sm.add_widget("className"(name='whatever name u want'))
        sm.add_widget(SecondPage(name='second'))                    #we do this so we can link the pages as we want
        sm.add_widget(WhoAreYou(name='who'))
        return sm


if __name__ == '__main__':   #rulam aplicatia
    MyApp().run()