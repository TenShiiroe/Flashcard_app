from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.image import Image
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
import random
from kivy.uix.recycleview import RecycleView
from kivy.uix.carousel import Carousel
import time
import os
import threading
from gogel import DeckController, Img_downloader

### WARNING THIS IS ONLY A VERY ROUGH SKETCH
### The program is somewhat working, but there are certainly a lot of bugs
### or misbehaviors etc. use only with caution, it has file manipulation(add/ del) and google images download so beware
### This is only a working prototype, will update later

SUPPORT_VID_FORMATS = ["mp4", "avi", "mkv", "mov", "webm", "ogv"] #"flv" didn't work for me, maybe with more plugins
Config.set('graphics', 'resizable', True)

BaseShowcaseRatio = 3 #display images in 4x4 or 3x3 or 2x2 layout, abse is 3x3 (will be added in the settings)
deckManager = DeckController()

Window.size = (960 * 9/16, 960)
Window.top = 30
Window.minimum_width = 200
Window.minimum_height = 200*(16/9)


class WindowManager(ScreenManager):
    pass


class DeckAddScreen(Screen): 
    def updateProgressBarIDK(self, fc):

        while self.ids.downloadProgressBar.value < fc:
            accFc = Img_downloader.fileCount()
            self.ids.downloadProgressBar.value = accFc
            self.ids.progressBarPercentage.text = f"Deck making in the progress - {round((accFc/fc)*100, 2)}%"
            time.sleep(0.1)
        self.ids.downloadProgressBar.value = fc
        self.ids.progressBarPercentage.text = "Deck complete"


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
        self.ids.downloadProgressBar.value = 0
        self.ids.progressBarPercentage.text = "Deck making in the progress - 0%"
        t1 = threading.Thread(target=deckManager.makeDeck, args=(parsed, name))  # Didnt help :( - cool
        t1.daemon = True
        t1.start()

        t2 = threading.Thread(target=(self.updateProgressBarIDK), args=([3 * len(parsed)]))
        t2.daemon = True
        t2.start()
        

class DeckEditScreen(Screen): 
    DeckName = StringProperty()

    def on_enter(self, *args):
        super().on_enter(*args)
        self.ids.deckShowcaseID.DeckName = self.DeckName
        self.ids.deckShowcaseID.refreshShowcase()


    def playDeck(self):
        app = App.get_running_app()
        imScreen = app.root.get_screen("ImageScreen")
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
        currDeck = deckManager.getDeckByName(self.DeckName)
        if not currDeck:
            print("no deck loaded")
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

    def change_image(self):
        self.animDelay = -1
        self.btnOpacity = 0
        self.vidOpacity = 0
        currDeck = deckManager.getDeckByName(self.deckName)
        if len(currDeck.cards) == 0:

            App.get_running_app().stop()
            Window.set_title("heeelo")
            #Window.hide() #TODO save user data then exit 
            Window.close()
            return
        random_path = random.choice(currDeck.getAllPaths())
        card = currDeck.getCardByPath(random_path)  # theoretically error/ None shouldnt happen

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
        self.hint = "".join(os.path.basename(random_path).split("\\")[-1].split(".")[:-1]).strip()

    def gif_btn(self):
        self.animDelay = 0.04 if self.animDelay == -1 else -1  # TODO maybe other speed options


class MainScreen(Screen):
    canContinue = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_pre_enter(self):
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
        self.title = "Image App"
        #self.icon = "xx.jpg" potentional future logo
        appScreens = (LoginScreen, ImageScreen , MainScreen, SettingsScreen, DeckManageScreen, DeckAddScreen, DeckEditScreen)
        for i in appScreens:
            self.sm.add_widget(i(name = i.__name__))
        return self.sm


if __name__ == "__main__":
    ImageApp().run()
