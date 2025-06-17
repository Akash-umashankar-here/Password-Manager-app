from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp

store = JsonStore('user_data.json')
Window.size = (360, 640)

class WelcomeScreen(Screen):
    # this screen is for showing the logo for 2 seconds
    def on_enter(self):
        Clock.schedule_once(self.switch_to_first, 2)

    def switch_to_first(self, dt):
        self.manager.current = 'first_entry'

class FirstScreen(Screen):
    #here ths will ask to create a key or use the existing one
    def confirm_key_dialogue(self):
        # Create a GridLayout for the popup content
        if self.ids.key_input.text == self.ids.confirm_input.text: 
            layout = GridLayout(cols=1, padding=10, spacing=10)
            # Create buttons
            close_button = Button(text='OK', size_hint_y=None, height=50)
            cancel_button = Button(text='Cancel', size_hint_y=None, height=50)           
            # Create and configure the popup
            self.popup = Popup(
                title="Confirm",
                content=layout,
                size_hint=(0.7, 0.4),
                auto_dismiss=False)           
            # Bind buttons
            close_button.bind(on_release=self.ok_action)
            cancel_button.bind(on_release=self.cancel_action)
            # Add buttons to the layout
            layout.add_widget(close_button)
            layout.add_widget(cancel_button)
            # Open the popup
            self.popup.open()
        else:
            self.ids.alert_message1.text = "both the fields are not same"
    def ok_action(self,*args):
        self.popup.dismiss()
        store.put(key=self.ids.key_input.text,data=[])
        self.manager.current = 'second_entry'

    def cancel_action(self, instance):
        # Dismiss the popup and switch to welcome screen
        self.popup.dismiss()
        self.manager.current = 'first_entry'
        
    def switch_to_second(self):
        self.manager.current = 'second_entry'
    
class SecondScreen(Screen):
    #asks to enter the key to acess the stored password
    def check_key(self):
        if store.exists(self.ids.key_entry.text):
            app = App.get_running_app()
            app.key = self.ids.key_entry.text
            self.manager.current = 'third_entry'
        else:
            self.ids.alert_message2.text = "enter a valid key"
            self.manager.current = 'second_entry'
class ThirdScreen(Screen):
    #this displays the passwords stored and we can add one
    def on_enter(self, *args):
        app = App.get_running_app()
        self.data_filling(app.key)
    
    def data_filling(self,key):
        container = self.ids.bt_container
        widgets_to_keep = [self.ids.add_entry]
        for widget in container.children[:]:
            if widget not in widgets_to_keep:
                container.remove_widget(widget)
        current_data = store.get(key)['data']
        total_buttons = len(current_data)
        container.height = dp(50) * (total_buttons + 1)
        for i in current_data:
            btn_username = i[1]
            btn_password = i[2]
            btn1 = Button(text= i[0],
            font_size= '16sp',
            size_hint= (0.4,None),
            pos_hint= {'x': 0},
            height=dp(50)
            )
            btn1.bind(on_press=lambda instance,pu=i[0], u=btn_username, p=btn_password: self.on_button_press(pu,u, p))            
            container.add_widget(btn1)
        
    def switch_to_fourth(self):
        self.manager.current = 'fourth_entry'
    
    def on_button_press(self,purpose,username,password):
        app = App.get_running_app()
        app.purpose = purpose
        app.username = username
        app.password = password
        self.manager.current = 'fifth_entry'
class FourthScreen(Screen):
    # asks for the purpose, username, password
    def check_entries(self):
        app = App.get_running_app()
        key = app.key
        entry = []
        purpose = self.ids.purpose.text
        username = self.ids.username.text
        password = self.ids.password.text
        if purpose and username and password:
            entry.append(purpose)
            entry.append(username)
            entry.append(password)
            current_data = store.get(key)['data']
            current_data.append(entry)
            store.put(key, data=current_data)
            self.manager.current ='third_entry'
        else:
            self.ids.alert_message3.text = "fill all the fields"

    def cancel_storing(self):
        self.manager.current = 'third_entry'

class FifthScreen(Screen):
    # to view the existing content
    def on_enter(self):
        app = App.get_running_app()
        self.username = app.username
        self.password = app.password
        self.ids.user_name.text= "Username: "+self.username
        self.ids.user_pass.text= "Password: "+self.password
    
    def edit_stored(self):
        self.manager.current = 'sixth_entry'
    
    def delete_stored(self):
        app = App.get_running_app()
        current_data = store.get(app.key)['data']
        for i,j in enumerate(current_data):
            if app.purpose in j:
                current_data.pop(i)
        store.put(app.key, data=current_data)
        self.manager.current = 'third_entry'

class SixthScreen(Screen):  
    # to edit the existing content
    def on_enter(self):
        container = self.ids.data_display
        container.clear_widgets()
        app = App.get_running_app()
        self.username = app.username
        self.password = app.password
        self.text1 = TextInput(multiline=False, font_size='18sp',size_hint_y=None, height=50)
        self.text2 = TextInput(multiline=False, font_size='18sp',size_hint_y=None, height=50)
        self.text1.text = self.username
        self.text2.text = self.password
        close_button = Button(text='OK', size_hint_y=None, height=50,pos_hint= {'right': 1})
        cancel_button = Button(text='Cancel', size_hint_y=None, height=50,pos_hint= {'x': 0}) 
        close_button.bind(on_release=self.ok_action)
        cancel_button.bind(on_release=self.cancel_action)
        container = self.ids.data_display
        container.add_widget(self.text1)
        container.add_widget(self.text2)
        container.add_widget(close_button)
        container.add_widget(cancel_button)
    
    def cancel_action(self,*args):
        self.manager.current = 'third_entry'
    
    def ok_action(self,*args):
        app = App.get_running_app()
        current_data = store.get(app.key)['data']
        for i,j in enumerate(current_data):
            if app.purpose in j:
                wanted_entry = current_data.pop(i)
        if self.text1.text == wanted_entry[1] and self.text2.text == wanted_entry[2]:
            current_data.append(wanted_entry)
            store.put(app.key, data=current_data)
            self.manager.current = 'third_entry'
        else:
            wanted_entry[1] = self.text1.text
            wanted_entry[2] = self.text2.text
            current_data.append(wanted_entry)
            store.put(app.key, data=current_data)
            self.manager.current = 'third_entry'

class MyApp(App):
    
    def build(self):
        # Create a ScreenManager
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(FirstScreen(name='first_entry'))
        sm.add_widget(SecondScreen(name='second_entry'))
        sm.add_widget(ThirdScreen(name='third_entry'))
        sm.add_widget(FourthScreen(name='fourth_entry'))
        sm.add_widget(FifthScreen(name='fifth_entry'))
        sm.add_widget(SixthScreen(name='sixth_entry'))
        return sm

if __name__ == '__main__':
    MyApp().run()