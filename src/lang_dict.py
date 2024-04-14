
import logging

class LangDict():

    LANG_DICT = {
        "en": "english",
        "fr": "francais"
    }

    DICT = {
        "add": {
            "en": "add",
            "fr": "ajouter",
        },
        "save": {
            "en": "save",
            "fr": "sauvegarder",
        },
        "cancel": {
            "en": "cancel",
            "fr": "annuler",
        },
        "edit": {
            "en": "edit",
            "fr": "modifier",
        },
        "settings": {
            "en": "settings",
            "fr": "paramètres",
        },
        "language": {
            "en": "language",
            "fr": "langue",
        },
        "debug": {
            "en": "debug",
            "fr": "débogage",
        },
        "operation": {
            "en": "operation",
            "fr": "operation",
        },
        "date": {
            "en": "date",
            "fr": "date",
        },
        "select": {
            "en": "select",
            "fr": "selectionner",
        },
        "tier": {
            "en": "tier",
            "fr": "tiers",
        },
        "category": {
            "en": "category",
            "fr": "categorie",
        },
        "description": {
            "en": "description",
            "fr": "description",
        },
        "amount": {
            "en": "amount",
            "fr": "montant",
        },
    }

    def __init__(self, lang_key: str = "en"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.lang_key: str = "en"
        self.set_lang(lang_key)

    def get_lang(self):
        return self.lang_key

    def set_lang(self, lang_key: str):
        for (key, _) in self.LANG_DICT.items():
            if lang_key == key:
                self.lang_key = lang_key
                return
        self.logger.warn("Unknown language key %s", lang_key)

    def get(self, key: str, lang_key: str = ""):
        if key not in self.DICT:
            self.logger.warn("Unknown key %s", key)
            return key
        if lang_key:
            if lang_key not in self.DICT[key]:
                self.logger.warn("Unknown language key %s", lang_key)
                return key
            return self.DICT[key][lang_key]
        return self.DICT[key][self.lang_key]
