import configparser


class OSGLanguageConfig:
    def __init__(self, langfile, default_language='DE'):
        self._cfg = configparser.ConfigParser()
        self._cfg.read(langfile, encoding='utf-8')
        self.__selected_language = default_language

    def get(self, item, language=None):
        if language is None: language = self.__selected_language
        return self._cfg[language].get(item)

    def set_language(self, language):
        self.__selected_language = language.upper()


class OSGConfig(configparser.ConfigParser):
    def __init__(self, cfgfile):
        super(OSGConfig, self).__init__()
        self.read(cfgfile, encoding='utf-8')


class OSGConfigManager:
    def __init__(self, cfgfile):
        self._config = OSGConfig(cfgfile)
        self._lang_cfg = OSGLanguageConfig(self._get_lang_cfg_file())

    def _get_lang_cfg_file(self):
        return self._config['CONFIGS'].get('lang_cfg_file')

    def lang_set_german(self):
        self._lang_cfg.set_language('DE')

    def lang_set_english(self):
        self._lang_cfg.set_language('EN')

    def lang_get_string(self, item):
        return self._lang_cfg.get(item)
