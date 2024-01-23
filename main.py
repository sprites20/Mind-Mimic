"""
script_path = 'get-pip.py'

try:
    with open(script_path, 'r') as file:
        script_contents = file.read()
        exec(script_contents)
except FileNotFoundError:
    print(f"The file '{script_path}' does not exist.")
except Exception as e:
    print(f"An error occurred while executing the script: {e}")

# Continue running the rest of the script
print("The getpip.py script has been executed. Continuing with the rest of the script...")
"""
from kivy.config import Config
# Set the window size (resolution)
Config.set('graphics', 'width', '720')
Config.set('graphics', 'height', '1600')


from kivy.app import App

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.codeinput import CodeInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import NoTransition
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.filechooser import FileChooserListView

from kivy.utils import platform

from kivy.properties import ListProperty


from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.screen import MDScreen


from kivy.clock import Clock

from kivy.lang import Builder

from pygments.lexers import PythonLexer
from pygments import highlight
from pygments.formatters import HtmlFormatter
import sys
from io import StringIO

import sys
import os
import subprocess

import pip

#from jnius import autoclass, cast

kv_string = '''
<MDScreen>:
    canvas.before:
        Color:
            rgba: 0.3, 0.3, 0.3, 1  # Light gray color
        Rectangle:
            pos: self.pos
            size: self.size
<CustomComponent@BoxLayout>:
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

<CustomLabel@Label>:
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
MDScreen:
    MDNavigationLayout:
        swipe_distance: self.width / 2
        swipe_edge_width: 0
        MDScreenManager:
            id: screen_manager
            swipe: False  # Disable swipe transitions
            MDScreen:
                name: 'main_screen'
                transition: "NoTransition"  # Disable transition
                BoxLayout:
                    orientation: 'vertical'
                    size_hint: (1, 1)  # 1/3 of the width
                    pos_hint: {"top": 0.94}  # Adjust the top position here
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: '40dp'
                        Button:
                            text: 'Run Program'
                            on_press: app.run_program()
                        Button:
                            text: 'Packages'
                            on_press: app.file_viewer_screen_pressed()
                        Button:
                            text: 'LLMs'
                            #size_hint_x: 0.5
                            on_press: app.switch_screen('cgpt_screen')
                    CodeInput:
                        id: kivy_code
                        size_hint_y: 0.6
                    TextInput:
                        id: output_text
                        multiline: True
                        readonly: True
                        size_hint_y: 0.4
                        
            MDScreen:
                name: 'cohere_screen'
                BoxLayout:
                    orientation: 'vertical'
                    size_hint: (1, 1)  # Adjust the height of the button
                    pos_hint: {"top": .94}  # Adjust the vertical position of the button
                    Button:
                        text: 'Back'
                        size_hint: (1, 0.1)  # Adjust the height of the button
                        #pos_hint: {"top": 10}  # Adjust the vertical position of the button
                        on_press: app.switch_screen('main_screen')
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: '40dp'
                        Button:
                            text: 'Cohere'
                            on_press: app.switch_screen('cohere_screen')
                        Button:
                            text: 'Gemini'
                            on_press: app.switch_screen('gemini_screen')
                        Button:
                            text: 'ChatGPT'
                            #size_hint_x: 0.5
                            on_press: app.switch_screen('cgpt_screen')
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
                                    img_source: "images/cohere_logo.png"
                                    txt: "[b]Bold Text[/b] [size=12][color=#A9A9A9]Smaller Text[/color][/size]\\nMore Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text"
                                CustomComponent:
                                    img_source: "images/cohere_logo.png"
                                    txt: "[b]Bold Text[/b] [size=12][color=#A9A9A9]Smaller Text[/color][/size]\\nMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text"
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
                                        source: "images/cohere_logo.png"
                                        size_hint: None, None
                                        size: 50, 50  # Set a fixed size for the Image
                                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}  # Center the Image initially
            MDScreen:
                name: 'gemini_screen'
                BoxLayout:
                    orientation: 'vertical'
                    size_hint: (1, 1)  # Adjust the height of the button
                    pos_hint: {"top": .94}  # Adjust the vertical position of the button
                    Button:
                        text: 'Back'
                        size_hint: (1, 0.1)  # Adjust the height of the button
                        #pos_hint: {"top": 10}  # Adjust the vertical position of the button
                        on_press: app.switch_screen('main_screen')
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: '40dp'
                        Button:
                            text: 'Cohere'
                            on_press: app.switch_screen('cohere_screen')
                        Button:
                            text: 'Gemini'
                            on_press: app.switch_screen('gemini_screen')
                        Button:
                            text: 'ChatGPT'
                            #size_hint_x: 0.5
                            on_press: app.switch_screen('cgpt_screen')
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
                                    txt: "[b]Bold Text[/b] [size=12][color=#A9A9A9]Smaller Text[/color][/size]\\nMore Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text"
                                CustomComponent:
                                    img_source: "images/gemini_logo.png"
                                    txt: "[b]Bold Text[/b] [size=12][color=#A9A9A9]Smaller Text[/color][/size]\\nMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text"
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
            MDScreen:
                name: 'cgpt_screen'
                BoxLayout:
                    orientation: 'vertical'
                    size_hint: (1, 1)  # Adjust the height of the button
                    pos_hint: {"top": .94}  # Adjust the vertical position of the button
                    Button:
                        text: 'Back'
                        size_hint: (1, 0.1)  # Adjust the height of the button
                        #pos_hint: {"top": 10}  # Adjust the vertical position of the button
                        on_press: app.switch_screen('main_screen')
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: '40dp'
                        Button:
                            text: 'Cohere'
                            on_press: app.switch_screen('cohere_screen')
                        Button:
                            text: 'Gemini'
                            on_press: app.switch_screen('gemini_screen')
                        Button:
                            text: 'ChatGPT'
                            #size_hint_x: 0.5
                            on_press: app.switch_screen('cgpt_screen')
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
                                    img_source: "images/cgpt_logo.png"
                                    txt: "[b]Bold Text[/b] [size=12][color=#A9A9A9]Smaller Text[/color][/size]\\nMore Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text"
                                CustomComponent:
                                    img_source: "images/cgpt_logo.png"
                                    txt: "[b]Bold Text[/b] [size=12][color=#A9A9A9]Smaller Text[/color][/size]\\nMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal TextMore Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text More Normal Text"
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
                                        source: "images/cgpt_logo.png"
                                        size_hint: None, None
                                        size: 50, 50  # Set a fixed size for the Image
                                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}  # Center the Image initially
            MDScreen:
                name: 'path_change_screen'
                BoxLayout:
                    orientation: 'vertical'
                    size_hint: (1, 1)  # Adjust the height of the button
                    pos_hint: {"top": 0.94}  # Adjust the vertical position of the button
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: 0.1
                        Button:
                            text: 'Back'
                            size_hint: (1, 0.1)  # Adjust the height of the button
                            #pos_hint: {"top": 10}  # Adjust the vertical position of the button
                            on_press: app.switch_screen('file_viewer_screen')
                        
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: 0.1
                            TextInput:
                                id: current_directory_label
                                text: file_chooser.path
                            Button:
                                text: "Select Current Directory"
                                on_release: app.select_current_directory()
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: 0.1
                            Button:
                                text: "Internal"
                                on_release: app.select_internal()
                            Button:
                                text: "SD Card"
                                on_release: app.select_SD()
                                
                        FileChooserListView:
                            id: file_chooser
                            path: ""
            MDScreen:
                name: 'file_viewer_screen'
                BoxLayout:
                    orientation: 'vertical'
                    size_hint: (1, 1)  # Adjust the height of the button
                    pos_hint: {"top": .94}  # Adjust the vertical position of the button
                    Button:
                        text: 'Back'
                        size_hint: (1, 0.2)  # Adjust the height of the button
                        #pos_hint: {"top": 10}  # Adjust the vertical position of the button
                        on_press: app.switch_screen('main_screen')
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: 0.15
                        TextInput:
                            id: path_input
                            hint_text: 'Path'
                        Button:
                            text: 'Browse Path'
                            size_hint_x : .5
                            on_press: app.switch_screen('path_change_screen')
                        Button:
                            text: 'Add Path'
                            size_hint_x : .5
                            on_press: app.add_path()
                    BoxLayout:
                        orientation: 'vertical'
                        Label:
                            text: "Paths"
                            size_hint_y: None
                            height: 40
                        ScrollView:
                            id: paths_menu
                            GridLayout:
                                id: grid
                                cols: 1
                                size_hint_y: None
                                height: self.minimum_height
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: 0.15
                        Label:
                            text: 'Installation Path'
                            size_hint_x: None
                            width : 150
                        TextInput:
                            id: package_path_input
                            hint_text: 'Path'
                        
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: 0.15
                        Label:
                            text: 'Install Packages'
                            size_hint_x: None
                            width : 150
                        TextInput:
                            id: package_input
                            hint_text: 'Enter package name'
                        Button:
                            text: 'Install Package'
                            on_press: app.install_package(package_input.text)
                    TextInput:
                        id: installation_status
                        multiline: True
                        readonly: True
                        #size_hint_y: 0.4   
                                        
        MDTopAppBar:
            title: "Python IDE"
            elevation: 4
            pos_hint: {"top": 1}
            md_bg_color: "#e7e4c0"
            specific_text_color: "#4a4939"
'''

def install_package_2(package_name):
    try:
        pip.main('install', package_name)
        print(f"Successfully installed {package_name}")
    except Exception as e:
        print(f"Failed to install {package_name}: {e}")
        
class MyApp(MDApp):
    existing_paths = set()
    path_displayed = False 
    def build(self):
        
        """
        if platform == "android":
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            current_activity = cast('android.app.Activity', PythonActivity.mActivity)
            context = current_activity.getApplicationContext()
        """
        print("Running")
        
        self.root = Builder.load_string(kv_string)
        return self.root

    def select_internal(self):
        platform_name = platform
        
        print(platform_name)
        
        if platform_name == 'android':
            # Get the paths to the internal storage and SD card
            Environment = autoclass('android.os.Environment')
            internal_storage_path = Environment.getExternalStorageDirectory().getAbsolutePath()
            self.root.ids.file_chooser.path = internal_storage_path
            self.root.ids.path_input.text = internal_storage_path
            
    def select_SD(self):
        platform_name = platform
        
        print(platform_name)

        if platform_name == 'android':
            # Get the current context
            try:
                Context = autoclass('android.content.Context')
                StorageManager = autoclass('android.os.storage.StorageManager')
                StorageVolume = autoclass('android.os.storage.StorageVolume')
                
                context = cast('android.content.Context', PythonActivity.mActivity)
                # Java classes
                    
                # Get the storage manager
                storage_manager = context.getSystemService(Context.STORAGE_SERVICE)
                
                # Get the volume list using reflection
                get_volume_list = storage_manager.getClass().getMethod("getVolumeList")
                volumes = get_volume_list.invoke(storage_manager)
                
                # Iterate through the volumes to find the removable one
                removable_path = None
                for volume in volumes:
                    is_removable = volume.isRemovable()
                    if is_removable:
                        get_path = volume.getClass().getMethod("getPath")
                        path = get_path.invoke(volume)
                        removable_path = path
                        break
            except:
                pass
            # Create and add widgets to the layout
            if removable_path:
                try:
                    self.root.ids.file_chooser.path = removable_path
                    self.root.ids.path_input.text = removable_path
                except:
                    pass
            
            

    def load_existing_paths(self, filename):
        # Load existing paths from a file
        if not os.path.exists('existing_paths.txt'):
            # Create an empty file if it doesn't exist
            with open('existing_paths.txt', 'w'):
                pass  # This creates an empty file
        else:
            with open(filename, 'r') as file:
                paths = file.readlines()
                self.existing_paths = {path.strip() for path in paths}
                print("Loaded paths!")

    def save_existing_paths(self, filename):
        # Save existing paths to a file
        with open(filename, 'w') as file:
            file.write('\n'.join(self.existing_paths))
    def file_viewer_screen_pressed(self):
        self.switch_screen('file_viewer_screen')
        print("Displaying paths...")
        self.display_paths()
        self.path_displayed = True
    def add_path_grid(self, path_text):
        # Create a new row with a TextInput for the path and a Button to delete the row
        row_layout = BoxLayout(size_hint_y=None, height=60)
        text_input = TextInput(text=path_text, hint_text='Path', readonly=True)
        select_button = Button(text='Select', size_hint_x=.25)
        select_button.bind(on_press=self.select_path)
        delete_button = Button(text='Delete', size_hint_x=.25)
        delete_button.bind(on_press=self.remove_path)
        
        # Add the TextInput and the delete Button to the row layout
        row_layout.add_widget(text_input)
        row_layout.add_widget(select_button)
        row_layout.add_widget(delete_button)

        # Add the row layout to the GridLayout inside the ScrollView
        self.root.ids.grid.add_widget(row_layout)
    def select_path(self, instance):
        # Find the parent row_layout containing the TextInput and delete button
        row_layout = None
        for child in self.root.ids.grid.children:
            if isinstance(child, BoxLayout) and instance in child.children:
                row_layout = child
                break

        if row_layout:
            # Find the TextInput widget within the row_layout
            text_input = None
            for child in row_layout.children:
                if isinstance(child, TextInput):
                    text_input = child
                    break

            if text_input:
                path_text = text_input.text
                print(f"Printing {path_text}")

                # Check if the path exists in the set before removing
                if path_text in self.existing_paths:
                    self.root.ids.package_path_input.text = path_text
                    
    def add_path(self):
        # Get the text from the path input
        path_text = self.root.ids.path_input.text

        # Check if the path already exists
        if path_text in self.existing_paths or path_text == '' or path_text == None:
            # Path already exists, do not add it again
            return
        
        # Check if the path is a directory
        if not os.path.isdir(path_text):
            return
        # Check if the path is not already in sys.path
        sys.path.append(path_text)
        
        # Add the new path to the set of existing paths
        self.existing_paths.add(path_text)
        self.save_existing_paths('existing_paths.txt')  # Save existing paths to a file when the app is closed
        # Create a new row with a TextInput for the path and a Button to delete the row
        
        self.add_path_grid(path_text)
    
    def display_paths(self):
        if not self.path_displayed:
            self.load_existing_paths('existing_paths.txt')  # Load existing paths from a file
            print(f"Paths {self.existing_paths}")
            for path_text in self.existing_paths:
                try:
                    self.add_path_grid(path_text)
                    sys.path.append(path_text)
                    print(f"Added path: {path_text}")
                except:
                    pass
        else:
            print(f"Path displayed: {self.path_displayed}")
                    
        
    def remove_path(self, instance):
        # Find the parent row_layout containing the TextInput and delete button
        row_layout = None
        for child in self.root.ids.grid.children:
            if isinstance(child, BoxLayout) and instance in child.children:
                row_layout = child
                break

        if row_layout:
            # Find the TextInput widget within the row_layout
            text_input = None
            for child in row_layout.children:
                if isinstance(child, TextInput):
                    text_input = child
                    break

            if text_input:
                path_text = text_input.text
                print(f"Printing {path_text}")

                # Check if the path exists in the set before removing
                if path_text in self.existing_paths:
                    self.existing_paths.remove(path_text)
                    sys.path.remove(path_text)
                    print(f"Removed from sys.path : {path_text}")
                    
            # Remove the row layout from the GridLayout inside the ScrollView
            self.root.ids.grid.remove_widget(row_layout)

    def select_current_directory(self):
        new_path = self.root.ids.current_directory_label.text
        
        print(new_path)
        self.switch_screen('file_viewer_screen')
        self.root.ids.path_input.text = new_path
        
    def install_package(self, package_name):
        # Split the input string into a list of package names
        package_names = package_name.split(' ')
        """
        target_directory = ""
        # Create the target directory if it doesn't exist
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        """
        # Update the installation status label
        installation_status = self.root.ids.installation_status

        # Schedule the first update to the installation status label
        Clock.schedule_once(lambda dt: self.update_installation_status(installation_status, 'Installing packages...'))
        print(package_name)
        try:
            pip.main('install', package_name)
            print(f"Successfully installed {package_name}")
        except Exception as e:
            print(f"Failed to install {package_name}: {e}")
        """
        # Install each package to the specified directory using pip subprocess
        for package_name in package_names:
            try:
                install_package_2(target_directory, package_name)

                # If the installation is successful, print a message
                print(f"Successfully installed {package_name} to {target_directory}")

                # Update the installation status label
                Clock.schedule_once(lambda dt, package=package_name: self.update_installation_status(installation_status, f"Successfully installed {package}"))

            except subprocess.CalledProcessError as e:
                # If there's an error during installation, print the error message
                print(f"Error installing {package_name}: {e}")

                # Update the installation status label with the error message
                Clock.schedule_once(lambda dt, package=package_name, error=e: self.update_installation_status(installation_status, f"Error installing {package_name}: {error}"))
        
        #install_package_2(package_name)
        # Append the target directory to sys.path
        if target_directory not in sys.path:
            sys.path.append(target_directory)

        # Schedule the final update to the installation status label
        Clock.schedule_once(lambda dt: self.update_installation_status(installation_status, 'Installation complete'))
        """
    def update_installation_status(self, label, status):
        # Update the installation status label with the provided status
        label.text += status + '\n'
    def update_file_viewer(self):
        pass

            
    def run_program(self):
        print(self.existing_paths)
        if self.existing_paths == set():
            self.display_paths()
            print(self.existing_paths)
        kivy_code = self.root.ids.kivy_code.text

        # Capture the standard output
        sys_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        # Execute the Kivy language code
        try:
            exec(kivy_code, globals())  # Use globals() to ensure Kivy classes are accessible
        except Exception as e:
            # Display any exception that occurs during execution
            self.root.ids.output_text.text = str(e)
            return
        finally:
            # Restore the original standard output
            sys.stdout = sys_stdout

        # Set the output text with captured output
        self.root.ids.output_text.text = captured_output.getvalue()
    
    def switch_screen(self, screen_name):
        screen_manager = self.root.ids.screen_manager
        current_screen = screen_manager.current

        # Cancel the transition
        screen_manager.transition = NoTransition()

        # Switch to the target screen
        screen_manager.current = screen_name
        
        # If switching to 'file_viewer_screen', update the file viewer
        if screen_name == 'file_viewer_screen':
            self.update_file_viewer()
            
    def view_google(self,b):
        self.browser = WebView('https://chat.openai.com/',
                               enable_javascript = True,
                               enable_downloads = True,
                               enable_zoom = True)
        
    def view_local_file(self,b):
        self.browser = WebView('file://'+self.filename)

    def view_downloads(self,b):
        if self.browser:
            d = self.browser.downloads_directory()
            self.label.text = fill(d,40) + '\n'
            l = listdir(d)
            if l:
                for f in l:
                    self.label.text += f + '\n'
            else:
                self.label.text = 'No files downloaded'
        else:
            self.label.text = 'Open a browser first'
                
    def on_pause(self): 
        if self.browser:
            self.browser.pause()
        return True

    def on_resume(self):
        if self.browser:
            self.browser.resume()
        pass

    def _create_local_file(self):
        # Create a file for testing
        from android.storage import app_storage_path
        from jnius import autoclass
        from os.path import join, exists
        from os import mkdir
        
        Environment = autoclass('android.os.Environment')
        path = join(app_storage_path(), Environment.DIRECTORY_DOCUMENTS)
        if not exists(path):
            mkdir(path)
        self.filename = join(path,'from_space.html')
        with open(self.filename, "w") as f:
            f.write("<html>\n")
            f.write(" <head>\n")
            f.write(" </head>\n")
            f.write(" <body>\n")
            f.write("  <h1>Greetings Earthlings<h1>\n")
            f.write(" </body>\n")
            f.write("</html>\n")
if __name__ == "__main__":
    #MyApp().display_paths()
    MyApp().run()
    