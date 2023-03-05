from google_images_download import google_images_download # Download images
import shutil  # Copy files
import os  # Group images
from typing import List, Optional, Dict  # typecheck


DATA_FOLDER = "_data"
DIR = f"{DATA_FOLDER}\\_downloads"  # Folder with downloaded images
DECKS_BASE = f"{DATA_FOLDER}\\_decks"  # Folder with decks
BASE_PIC_LIMIT = 3  # the base amount of cards for each keyword to be downloaded 


#TODO add regex to search
#TODO del from deck = delete image? || "unlinked image" - can be reassigned to deck

"""
Base class for storing images/ cards
"""
class Image(object):
    def __init__(self, name: str, path: str) -> None:
        self.name: str = name
        self.paths: List[str] = [path]


    def addPath(self, path: str) -> None:
        if os.path.exists(path):
            self.paths.append(path)
            return
        print("Invalid path - doesn't exist")


    def deleteCard(self) -> None:  # TODO add proper destructor, hande errors
        for path in self.paths:
            os.remove(path)
        self.paths = []
        

    def removePath(self, path: str) -> None:
        if path in self.paths:
            self.paths.remove(path)
            os.remove(path)
            return
        print("path doesn't exist")

"""
Base class for grouping images/ cards
"""
class Deck(object):
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.timesPlayed: int = 0
        self.cards: List[Image] = []


    def deleteDeck(self) -> None:  # TODO add proper destructor, handle errors
        for card in self.cards:
            card.deleteCard()
        shutil.rmtree(f"{DECKS_BASE}\\{self.name}")


    def getAllPaths(self) -> List[str]:
        return list(path for card in self.cards for path in card.paths)


    def addCard(self, image: Image) -> None:
        possibleCopy = self.getCardByName(image.name)
        if possibleCopy is None:
            self.cards.append(image)
        else:
            for path in image.paths:
                possibleCopy.addPath(path)
        

    def getCardByName(self, name: str) -> Optional[Image]:
        for card in self.cards:
            if card.name == name:
                return card
        return None


    def getCardByPath(self, path: str) -> Optional[Image]:
        for card in self.cards:
            if path in card.paths:
                return card
        return None


"""
Class for managing decks and their operations
"""
class DeckController(object):
    def __init__(self) -> None:
        self.decks: List[Deck] = []


    def getDeckByName(self, name: str) -> Optional[Deck]:
        for deck in self.decks:
            if deck.name == name:
                return deck
        return None


    def loadDecks(self) -> int:
        if not os.path.exists(f"{DECKS_BASE}"):
            return -1  # No decks aviable to load 

        self.decks = []
        for deck in os.listdir(DECKS_BASE):
            _tmpAdd = self.dirToDeck(deck)
            if _tmpAdd is not None:
                self.decks.append(_tmpAdd)
        return 0


    @staticmethod
    def scanForImages() -> int:
        if not os.path.exists(DIR):
            print("Unable to find any downloaded images")
            return -1  # Didn't download anything

        for filename in os.listdir(DIR):
            file = os.path.join(DIR, filename)
            
            if os.path.isdir(file):  
                DeckController._groupImages(file)
        return 0


    @staticmethod
    def _groupImages(imgDir: str) -> None:
        if not os.path.exists(f"{DIR}\\__temp_transfer"):
            os.mkdir(f"{DIR}\\__temp_transfer")

        for count, possibleImg in enumerate(os.listdir(imgDir)):
            filePath = os.path.join(imgDir, possibleImg)
            end = possibleImg.split(".")[-1]  # Could use os.path.splitext(possible_img)
            if os.path.isfile(filePath):
                shutil.copyfile(filePath, f"{DIR}\\__temp_transfer\\{os.path.basename(imgDir)}_{count}.{end}", follow_symlinks=True)


    def BuildDeck(self, deckName: str) -> Optional[Deck]:
        if not os.path.exists(f"{DIR}\\__temp_transfer"):
            return None
        
        for imgName in os.listdir(f"{DIR}\\__temp_transfer"):
            imgPath = os.path.join(f"{DIR}\\__temp_transfer", imgName)
            shutil.copyfile(imgPath, f"{DECKS_BASE}\\{deckName}\\{imgName}", follow_symlinks=True)
        return self.dirToDeck(deckName)


    def dirToDeck(self, deckName: str) -> Optional[Deck]:
        if not os.path.exists(f"{DECKS_BASE}\\{deckName}"):
            return None

        deck = Deck(deckName)
        for fileName in os.listdir(f"{DECKS_BASE}\\{deckName}"):
            filePath = os.path.join(f"{DECKS_BASE}\\{deckName}", fileName)
            imgAnswer = ("".join(fileName.split("_")[:-1])).strip()  # remove number,extension and trailing whitespaces
            deck.addCard(Image(imgAnswer, filePath))
        return deck


    def makeDeck(self, query: List[str], name: str) -> Optional[Deck]:
        if not os.path.exists(f"{DECKS_BASE}\\{name}"):
            os.makedirs(f"{DECKS_BASE}\\{name}")
        else:
            print("trying to alter existing deck")
            return None  # Deck already exists

        Img_downloader.googleDownloadPics(query)
        if DeckController.scanForImages() == -1:
            return None
        returnValue =  self.BuildDeck(name)
        Img_downloader.clearDownloads()
        return returnValue
  
  

"""
"Static" class for downloading and basic image managing
"""
class Img_downloader(object):
    @staticmethod
    def googleDownloadPics(search_keys: List[str], limit: int = BASE_PIC_LIMIT) -> None:
        Img_downloader.clearDownloads()
        response = google_images_download.googleimagesdownload()
        arguments = {"keywords": f'{",".join(search_keys)}',
                    "limit": limit,
                    "output_directory": f"{DIR}"
                    }
        response.download(arguments)

    @staticmethod
    def clearDownloads() -> None:
        if os.path.exists(DIR):
            shutil.rmtree(DIR)  # wipe all downloaded files + temp transfer // basically clear cache?








    