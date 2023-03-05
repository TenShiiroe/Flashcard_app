import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout 
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.image import Image
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.video import Video
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
import random
from kivy.uix.recycleview import RecycleView
from kivy.uix.carousel import Carousel
import time
import os

from gogel import DeckController

### WARNING THIS IS ONLY A VERY ROUGH SKETCH
### The program is somewhat working, but there are certainly a lot bugs
### or misbehaviors etc. use only with caution, it has file manipulation(add/ del) and google images download so beware
### This is only a working prototype, will update later


SUPPORT_VID_FORMATS = ["mp4", "avi", "mkv", "mov", "webm", "ogv"] #"flv" didn't work for me, maybe with more plugins, cant be arsed
Config.set('graphics', 'resizable', True)
img_name_path = {
    "cat": "cat.jpg",
    "dog": "dog.jpg",
    "water": "water.jpg",
    "fire": "fire.jpg",
    "earth": "earth.gif",
    "video": "vid.mp4",
    "button": "Btn_background.gif",
    "nyan cat": "nyc.gif",
    "cato gifo": "cat.gif",
    "colors": "color.gif",
}

BaseShowcaseRatio = 3 #display images in 4x4 or 3x3 or 2x2 layout, abse is 3x3 (will be added in the settings)

deckManager = DeckController()


Window.size = (960 * 9/16, 960)
Window.top = 30
Window.minimum_width = 200
Window.minimum_height = 200*(16/9)
"""  Is it worth to imports and use tkinter just to get screen size?

import tkinter as tk
root = tk.Tk()

width_px = root.winfo_screenwidth()
height_px = root.winfo_screenheight()
print(height_px, width_px)
Window.size = (width_px, height_px)
"""

class WindowManager(ScreenManager):
    pass


class DeckAddScreen(Screen): 
    

    def downloadImages(self):
        query = self.ids.downloadQuery.text
        name = self.ids.deckName.text
        if name == "":
            self.ids.progressBarPercentage.text = "please input deck name"
            return  # TODO handle error
        if query == "":
            self.ids.progressBarPercentage.text = "please input something to download"
            return  # TODO handle error

        parsed = [x.strip() for x in query.split(",")]
        self.ids.listOfImages.text = "--".join(parsed)  # all texts update too late - after make deck (make deck makes app freeze? multithread? :()
        self.ids.downloadProgressBar.max = 3 * len(parsed)
        self.ids.progressBarPercentage.text = "Deck making in the progress"
        deckManager.makeDeck(parsed,name)  # hope I don't need to multithread for real progressbar :)
        self.ids.progressBarPercentage.text = "Deck complete"
        self.ids.downloadProgressBar.value = 3 * len(parsed)


class DeckEditScreen(Screen): 
    DeckName = StringProperty()

    def on_enter(self, *args):
        super().on_enter(*args)
        print("the name is ", self.DeckName)
        self.ids.deckShowcaseID.DeckName = self.DeckName
        self.ids.deckShowcaseID.refreshShowcase()


    def playDeck(self):
        app = App.get_running_app()
        imScreen = app.root.get_screen("ImageScreen")
        print("the name is ", self.DeckName)
        imScreen.deckName = self.DeckName
        imScreen.change_image()


    def deleteDeck(self):
        deckToDel = deckManager.getDeckByName(self.DeckName)
        if not deckToDel:
            print("deck not found")  # todo add error handle
        deckToDel.deleteDeck()
        deckManager.decks.remove(deckToDel)


class deckShowcase(Carousel):
    DeckName = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    
    def refreshShowcase(self):
        deckManager.loadDecks()
        print("the carousel name is", self.DeckName)
        print(deckManager.decks, self.DeckName)
        currDeck = deckManager.getDeckByName(self.DeckName)
        if not currDeck:
            print("no dedk loaded")
            return  # Tdodo some kind of error handler

        self.clear_widgets()
        Card_paths = currDeck.getAllPaths()
        for i in range(0, len(Card_paths), BaseShowcaseRatio**2):
            grid = GridLayout(rows=BaseShowcaseRatio, cols=BaseShowcaseRatio, spacing=10, padding=30)
            for j in range(BaseShowcaseRatio**2):
                if i+j < len(Card_paths):
                    image = Image(source=Card_paths[i+j])
                    grid.add_widget(image)

            self.add_widget(grid)





class DeckButton(Button):
    rootWidget = ObjectProperty()
    def on_release(self, **kwargs):
        super().on_release(**kwargs)
        self.rootWidget.switchToEdit(self.text)


class ScrollerCardList(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def refreshView(self):
        deckManager.loadDecks()
        self.data = [{"text": str(x.name), "rootWidget": self} for x in deckManager.decks]

    def switchToEdit(self, deckName):
        app = App.get_running_app()
        app.root.current = "DeckEditScreen"
        app.root.transition.direction = "left"
        app.root.get_screen("DeckEditScreen").DeckName = deckName





class DeckManageScreen(Screen): 
    def on_enter(self, *args):
        super().on_enter(*args)
        self.ids.CardListID.refreshView()




class ImageScreen(Screen):  #maybe popup later?
    randPath = StringProperty()  # TODO remove obsolete properties, make it more readable/ better
    vidPath = StringProperty()
    animDelay = NumericProperty(-1)
    btnOpacity = NumericProperty(0)
    vidOpacity = NumericProperty(0)
    hint = StringProperty()
    deckName = StringProperty()

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_enter(self, *args):
        print(self.hint)

    def change_image(self):
        self.animDelay = -1
        self.btnOpacity = 0
        self.vidOpacity = 0
        print(self.deckName)
        if len(deckManager.getDeckByName(self.deckName).cards) == 0:

            App.get_running_app().stop()
            #Window.grab_mouse() TODO exploit- easter egg AHAHAHAHHA
            #Window.show_cursor = False #more minigames??? AMOGUS??!!
            Window.set_title("heeelo")
            #Window.hide() #TODO save user data then exit 
            Window.close()
            return
        card = random.choice(deckManager.getDeckByName(self.deckName).cards)
        random_path = random.choice(card.paths)
        print(random_path)
        card.paths.remove(random_path) #key error shouldn't happen
        if len(card.paths) == 0:
            deckManager.getDeckByName(self.deckName).cards.remove(card)

        if random_path.split(".")[-1] == "gif":
            self.animDelay = 0.04   
            self.btnOpacity = 1
        if random_path.split(".")[-1] in SUPPORT_VID_FORMATS:
            self.vidOpacity = 1
            self.vidPath = random_path
            
        else:
            self.randPath = random_path 
        self.hint = "".join(os.path.basename(random_path).split("_")[:-1]).strip()

    def gif_btn(self):
        print("heeelo")
        self.animDelay = 0.04 if self.animDelay == -1 else -1



class MainScreen(Screen):
    isGuest = BooleanProperty(True)
    canContinue = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_pre_enter(self):
        print(f"aa{self.manager.get_screen('ImageScreen').hint}aa", self.manager.get_screen("ImageScreen").hint == "", self.manager.get_screen("ImageScreen").hint is None, type(self.manager.get_screen('ImageScreen').hint))
        self.canContinue = (self.manager.get_screen("ImageScreen").hint != "")

class LoginScreen(Screen): 
    pass

class SettingsScreen(Screen): 
    pass


class ImageApp(App):

    def __init__(self, **kwargs):
        super(ImageApp, self).__init__(**kwargs)
        self.sm = ScreenManager()

    def build(self):
        #Builder.load_file("Button.kv")
        self.title = "Image App"
        #self.icon = "cat.jpg" TODO AHAHAHAHAH graphics :(
        appScreens = (LoginScreen, ImageScreen , MainScreen, SettingsScreen, DeckManageScreen, DeckAddScreen, DeckEditScreen)
        for i in appScreens:
            self.sm.add_widget(i(name = i.__name__))
        return self.sm


if __name__ == "__main__":
    ImageApp().run()
