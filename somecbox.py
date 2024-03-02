from kivy.config import Config
# Set the window size (resolution)
Config.set('graphics', 'width', '720')
Config.set('graphics', 'height', '1600')

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from datetime import datetime, timedelta

import google.generativeai as genai
import re

genai.configure(api_key='AIzaSyDcPR-xdnW33WioL7d-leeWr4G9W57Wxfg')
model = genai.GenerativeModel('gemini-pro')

KV = '''
<CustomComponent>:
    background_color: (0.5, 0.5, 0.5, 1)
    orientation: 'horizontal'
    size_hint_y: None  # Ensure the height is fixed based on the CustomLabel
    height: custom_label.height # Set the height of CustomComponent based on CustomLabel height
    img_source: ''
    txt: ''
    canvas.before:
        Color:
            rgba: 0.25, 0.25, 0.25, 1  # Background color
        Rectangle:
            pos: self.pos
            size: self.size
    Image:
        source: root.img_source
        size_hint: .1, None  # Disable size_hint so we can set fixed sizes
        size: 50, 50  # Set a fixed size for the image
        pos_hint: {'center_x': 0.5, 'top': 1}  # Position the image at the top of CustomComponent
        canvas.before:
            Color:
                rgba: 0.25, 0.25, 0.25, 1  # Background color
            Rectangle:
                pos: self.x, self.y - (root.height - 50)
                size: 100, root.height
    CustomLabel:
        id: custom_label  # Add an id to the CustomLabel for referencing
        text: root.txt
        height: self.texture_size[1] + 10
        on_release: app.label_clicked(self)
        on_long_press: app.show_popup()

<CustomLabel>:
    size_hint_y: None
    height: self.texture_size[1]
    text_size: self.width, None
    #padding: [10,0]
    canvas.before:
        Color:
            rgba: 0.25, .25, .25, 1  # Background color
        Rectangle:
            pos: self.pos
            size: self.size
    markup: True  # Enable markup for custom formatting
    
<TransparentBoxLayout@BoxLayout>:
    canvas.before:
        Color:
            rgba: .25, .25, .25, 1  # Set the color to transparent
        Rectangle:
            pos: self.pos
            size: self.size

MDBoxLayout:
    orientation: 'vertical'
    padding: [0,0,0,100]
    ScrollView:
        canvas.before:
            Color:
                rgba: 0.25, 0.25, 0.25, 1  # Background color
            Rectangle:
                pos: self.pos
                size: self.size

        GridLayout:
            id: grid_layout
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: '10dp'
            #padding: '30dp'
            
            CustomComponent:
                img_source: "images/gemini_logo.png"
                txt: "[b]Gemini[/b] [size=12][color=#A9A9A9]{}[/color][/size]\\nHello, how can I help you today?".format(app.current_date)
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: self.minimum_height
        TransparentBoxLayout:
            orientation: 'horizontal'
            
            size_hint_y: None
            height: self.minimum_height
            padding: dp(10)  # Add padding to the TextInput
            TextInput:
                id: text_input
                hint_text: "Type here..."  # Placeholder text
                size_hint_y: None
                size_hint_x: .9
                height: min(self.minimum_height + 25, dp(300))  # Set a maximum height of 100 density-independent pixels
                multiline: True
                pos_hint: {"top": 1}  # Position the TextInput at the top of the TransparentBoxLayout
                background_normal: ''  # Remove the default background
                background_active: ''  # Remove the default background
                background_color: .3, .3, .3, 1  # Set the background color to red with 50% opacity
                foreground_color: 1, 1, 1, 1  # Set the text color to white
        TransparentBoxLayout:
            #orientation: 'vertical'
            size_hint_x: .1
            MDIconButton:
                pos_hint: {'center_x': .5, 'center_y': 0.5}  # Center the MDIconButton initially
                size_hint: None, None
                size: 50, 50
                #pos: self.parent.center_x - self.width / 2, self.parent.center_y - self.height / 2  # Position the MDIconButton at the center of its parent
                on_release: app.button_pressed()  # Define the action to be taken when the button is released
                Image:
                    source: "images/gemini_logo.png"
                    size_hint: None, None
                    size: 50, 50  # Set a fixed size for the Image
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}  # Center the Image initially
'''
class CustomComponent(BoxLayout):
    pass

class CustomLabel(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.long_press_timeout = 0.5  # Set the long press timeout to 1 second
        self.register_event_type('on_long_press')

    def on_long_press(self):
        pass
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch = touch
            Clock.schedule_once(self._do_long_press, self.long_press_timeout)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if hasattr(self, '_touch') and self._touch is touch:
            Clock.unschedule(self._do_long_press)
            del self._touch
        return super().on_touch_up(touch)

    def _do_long_press(self, *args):
        self.dispatch('on_long_press')
    pass

class TransparentBoxLayout(BoxLayout):
    pass
class ChatBoxApp(MDApp):
    def build(self):
        return Builder.load_string(KV)
    
    @property
    def current_date(self):
        # Get the current date and time
        now = datetime.now()
        # Get the current date
        today = now.date()
        # Get yesterday's date
        yesterday = today - timedelta(days=1)
        # Check if the current date is today or yesterday
        if today.day == now.day:
            return now.strftime("Today %I:%M %p")  # %I for 12-hour clock, %p for AM/PM
        elif yesterday.day == now.day:
            return now.strftime("Yesterday %I:%M %p")
        else:
            return now.strftime("%m/%d/%y %I:%M %p")
        

    def gemini_parse_message(self, message):
        formatted_text = message.replace("\\n", "\n")
        formatted_text = formatted_text.replace("\\", "")
        return formatted_text
        
    def button_pressed(self):
        text_input = self.root.ids.text_input
        
        user_text = text_input.text

        response = model.generate_content(user_text)
        result = str(response._result)
        parsed_result = self.gemini_parse_results(result)
        
        gemini_text = self.gemini_parse_message(parsed_result["text"])
        
        user_header_text = '[b]User[/b] [size=12][color=#A9A9A9]{}[/color][/size]'.format(self.current_date)
        gemini_header_text = '[b]Gemini[/b] [size=12][color=#A9A9A9]{}[/color][/size]'.format(self.current_date)
        
        user_message = user_header_text + '\n' + user_text
        gemini_message = gemini_header_text + '\n' + gemini_text
        #print(text_input)
        
        user_custom_component = CustomComponent(img_source="images/user_logo.png", txt=user_message)
        gemini_custom_component = CustomComponent(img_source="images/gemini_logo.png", txt=gemini_message)
        
        grid_layout = self.root.ids.grid_layout
        grid_layout.add_widget(user_custom_component)
        grid_layout.add_widget(gemini_custom_component)
        
        
    def label_clicked(self, label):
        print(f"Label '{label.text}' clicked!")
        
    def show_popup(self):
        # Create a popup with buttons
        popup = Popup(title='Actions', size_hint=(None, None), size=(200, 200))
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Button(text='Action 1'))
        layout.add_widget(Button(text='Action 2'))
        popup.content = layout
        popup.open()
        
    def gemini_parse_results(self, data):
        text = ""
        try:
            text_match = re.search(r'text: "(.*?)"', data, re.DOTALL)
            if text_match:
                text = text_match.group(1)
        except:
            pass
        # Extract the safety ratings
        safety_ratings_match = re.findall(r'category: (.*?)\s+probability: (.*?)\s+}', data, re.DOTALL)
        print(safety_ratings_match)
        
        safety_ratings = [{'category': category.strip(), 'probability': probability.strip()} for category, probability in safety_ratings_match]

        # Construct the dictionary
        result = {
            'text': text,
            'safety_ratings': safety_ratings
        }
        return result
if __name__ == '__main__':
    ChatBoxApp().run()
