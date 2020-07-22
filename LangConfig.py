"""
Created: 22.07.2020 08:35
Author: Dominik
Module: LangConfig.py
Project: python-modules
Description:
"""
import configparser


class LanguageConfig:
    def __init__(self, langfile, default_language='DE'):
        self._cfg = configparser.ConfigParser()
        self._cfg.read(langfile, encoding='utf-8')
        self.__selected_language = default_language

    def get(self, item, language=None):
        if language is None: language = self.__selected_language
        return self._cfg[language].get(item)

    def set_language(self, language):
        self.__selected_language = language.upper()
