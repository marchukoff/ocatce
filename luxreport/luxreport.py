#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Eugene Marchukov
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import collections
import copy
import json
import logging
import os
import os.path
import re
import shutil
import tempfile
import textwrap
import threading
import xml.dom.minidom
import xml.etree.ElementTree
import xml.sax.saxutils


langs = {"ar": ("arabic", 1, "ara"), "bg": ("bulgarian", 2, "bul"), "bs": ("bosnian", 46, "bos"),
         "cs": ("czech", 5, "cze"), "da": ("danish", 6, "dan"), "de": ("german", 7, "deu"), "el": ("greek", 8, "gre"),
         "en": ("english", 9, "eng"), "es": ("spanish", 10, "spa"), "et": ("estonian", 37, "est"),
         "fa": ("farsi", 41, "far"), "fi": ("finnish", 11, "fin"), "fr": ("french", 12, "fre"),
         "he": ("hebrew", 13, "heb"), "hi": ("hindi", 57, "hin"), "hr": ("croatian", 49, "cro"),
         "hu": ("hungarian", 14, "hun"), "hy": ("armenian", 43, "arm"), "id": ("indonesian", 33, "ind"),
         "it": ("italian", 16, "ita"), "ja": ("japanese", 17, "jap"), "ko": ("korean", 18, "kor"),
         "lt": ("lithuanian", 39, "lit"), "lv": ("latvian", 38, "lat"), "nl": ("dutch", 19, "dut"),
         "nn": ("norwegian", 20, "nno"), "pl": ("polish", 21, "pol"), "pt": ("portuguese", 22, "por"),
         "ro": ("romanian", 24, "rom"), "ru": ("russian", 25, "rus"), "sk": ("slovak", 27, "svk"),
         "sq": ("albanian", 28, "alb"), "sr": ("serbian", 66, "srb"), "sv": ("swedish", 29, "swe"),
         "th": ("thai", 30, "tha"), "tl": ("tagalog", 53, "tgl"), "tr": ("turkish", 31, "tur"),
         "uk": ("ukrainian", 34, "ukr"), "vi": ("vietnamese", 42, "vie"), "zh": ("chinese", 4, "chi")}

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh = logging.FileHandler('_'.join((os.path.splitext(__file__)[1], "log.txt")))
fh.setLevel(logging.WARNING)
fh.setFormatter(formatter)
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


#noinspection PyUnusedLocal
class AbstractDir(object):
    def __init__(self, name):
        if name:
            self._name = tempfile.mkdtemp(dir=name)
        else:
            self._name = tempfile.mkdtemp()


    @property
    def name(self):
        """The folder name"""
        assert os.path.exists(self._name), 'TempDir "%s" was not created' % self._name
        return self._name


    def __str__(self):
        return str(self._name)


    def __bool__(self):
        return os.path.exists(self._name)


    def exists(self):
        return self.__bool__()


    def remove(self):
        if self:
            shutil.rmtree(self._name)


# noinspection PyCompatibility,PyCompatibility
class TempDir(AbstractDir):
    def __init__(self, name='/shares/releases/xml'):
        super().__init__(name)


    def __enter__(self):
        return self.name


    # noinspection PyUnusedLocal
    def __exit__(self, *ignore):
        super().remove()


# noinspection PyCompatibility
class ExtDir(AbstractDir):
    _mutex = threading.Lock()

    def __init__(self, filename, mount_point='/shares/releases/xml'):
        self._filename = filename
        super().__init__(mount_point)


    def __enter__(self):
        ExtDir._mutex.acquire()
        os.system('/usr/local/etc/rc.d/fusefs onestart && ext4fuse %s %s' % (self._filename, self._name))
        os.system('ls -m %s' % self._name)
        return self.name


    # noinspection PyUnusedLocal
    def __exit__(self, *ignore):
        command = 'sync && '
        command += ' || '.join(
            ['/usr/local/etc/rc.d/fusefs {0}'.format(s) for s in ('onestop', 'faststop', 'forcestop')])
        os.system(command)
        super().remove()
        ExtDir._mutex.release()


class Release(object):
    def __init__(self, project_id, project_model="", apps_ectaco="", apps_other="", voice_dictionary="",
                 voice_phrasebook="", photo_text="", ulearn='', ulearn2='', feature_tts="", feature_sr="",
                 feature_gt="", feature_jibbigo="", sd_size=""):
        self.__project_id = str(project_id).strip()
        self.project_model = project_model
        self.apps_ectaco = apps_ectaco
        self.apps_other = apps_other
        self.voice_dictionary = voice_dictionary
        self.voice_phrasebook = voice_phrasebook
        self.photo_text = photo_text
        self.ulearn = ulearn
        self.ulearn2 = ulearn2
        self.feature_tts = feature_tts
        self.feature_sr = feature_sr
        self.feature_gt = feature_gt
        self.feature_jibbigo = feature_jibbigo
        self.sd_size = sd_size

        self.__facet = ['project_id', 'project_model', 'apps_ectaco', 'apps_other', 'voice_dictionary',
                        'voice_phrasebook', 'photo_text', 'ulearn', 'ulearn2', 'feature_tts', 'feature_sr',
                        'feature_gt', 'feature_jibbigo', 'sd_size']


    @property
    def facet(self):
        """The list of the class members"""
        return copy.deepcopy(self.__facet)


    @property
    def project_id(self):
        """The file name"""
        return self.__project_id


    @property
    def project_model(self):
        """The languages presented in project"""
        return self.__project_model

    #noinspection PyAttributeOutsideInit
    @project_model.setter
    def project_model(self, project_lang):
        self.__project_model = str(project_lang).strip() if project_lang else "-"


    @property
    def apps_ectaco(self):
        """The apps from Ectaco"""
        return self.__apps_ectaco


    #noinspection PyAttributeOutsideInit
    @apps_ectaco.setter
    def apps_ectaco(self, apps_ectaco):
        self.__apps_ectaco = str(apps_ectaco).strip() if apps_ectaco else "-"


    @property
    def apps_other(self):
        """The apps from all other"""
        return self.__apps_other

    #noinspection PyAttributeOutsideInit
    @apps_other.setter
    def apps_other(self, apps_other):
        self.__apps_other = str(apps_other).strip() if apps_other else "-"


    @property
    def voice_dictionary(self):
        """The languages with true voice for the Dictionary"""
        return self.__voice_dictionary

    #noinspection PyAttributeOutsideInit
    @voice_dictionary.setter
    def voice_dictionary(self, voice_dictionary):
        self.__voice_dictionary = str(voice_dictionary).strip() if voice_dictionary else "-"


    @property
    def voice_phrasebook(self):
        """The languages with true voice for the PhraseBook"""
        return self.__voice_phrasebook

    #noinspection PyAttributeOutsideInit
    @voice_phrasebook.setter
    def voice_phrasebook(self, voice_phrasebook):
        self.__voice_phrasebook = str(voice_phrasebook).strip() if voice_phrasebook else "-"


    @property
    def photo_text(self):
        """The languages for Photo Text / Input app"""
        return self.__photo_text

    #noinspection PyAttributeOutsideInit
    @photo_text.setter
    def photo_text(self, photo_text):
        s = str(photo_text).strip()
        self.__photo_text = s if s else '-'


    @property
    def ulearn(self):
        """The language pair for ULearn app"""
        return self.__ulearn

    #noinspection PyAttributeOutsideInit
    @ulearn.setter
    def ulearn(self, s):
        self.__ulearn = s.strip() if s else '-'


    @property
    def ulearn2(self):
        """The language pair for ULearn-2 app"""
        return self.__ulearn2

    #noinspection PyAttributeOutsideInit
    @ulearn2.setter
    def ulearn2(self, s):
        self.__ulearn2 = s.strip() if s else '-'


    @property
    def feature_tts(self):
        """The languages for conversion text to speech"""
        return self.__feature_tts

    #noinspection PyAttributeOutsideInit
    @feature_tts.setter
    def feature_tts(self, feature_tts):
        self.__feature_tts = str(feature_tts).strip() if feature_tts else "-"


    @property
    def feature_sr(self):
        """The Voice Typing by Google"""
        return self.__feature_sr

    #noinspection PyAttributeOutsideInit
    @feature_sr.setter
    def feature_sr(self, feature_sr):
        self.__feature_sr = str(feature_sr).strip() if feature_sr else "-"


    @property
    def feature_gt(self):
        """Data for Google Translate (Internal)"""
        return self.__feature_gt

    #noinspection PyAttributeOutsideInit
    @feature_gt.setter
    def feature_gt(self, feature_gt):
        self.__feature_gt = str(feature_gt).strip() if feature_gt else "-"


    @property
    def feature_jibbigo(self):
        """The languages for Jibbigo translator"""
        return self.__feature_jibbigo

    #noinspection PyAttributeOutsideInit
    @feature_jibbigo.setter
    def feature_jibbigo(self, feature_jibbigo):
        self.__feature_jibbigo = str(feature_jibbigo).strip() if feature_jibbigo else "-"


    @property
    def sd_size(self):
        """The size of data of SD card"""
        return self.__sd_size

    #noinspection PyAttributeOutsideInit
    @sd_size.setter
    def sd_size(self, sd_size):
        self.__sd_size = str(sd_size).strip() if sd_size else "-"


    def __repr__(self):
        return "%s(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r)" % (
            self.__class__.__name__, self.project_id, self.project_model, self.apps_ectaco, self.apps_other,
            self.voice_dictionary, self.voice_phrasebook, self.photo_text, self.ulearn, self.ulearn2, self.feature_tts,
            self.feature_sr,
            self.feature_gt, self.feature_jibbigo, self.sd_size)

    def __iadd__(self, other):
        if isinstance(other, Release):
            self.__project_id = other.project_id
            self.project_model = other.project_model
            self.apps_ectaco = other.apps_ectaco
            self.apps_other = other.apps_other
            self.voice_dictionary = other.voice_dictionary
            self.voice_phrasebook = other.voice_phrasebook
            self.photo_text = other.photo_text
            self.ulearn = other.ulearn
            self.ulearn2 = other.ulearn2
            self.feature_tts = other.feature_tts
            self.feature_sr = other.feature_sr
            self.feature_gt = other.feature_gt
            self.feature_jibbigo = other.feature_jibbigo
            self.sd_size = other.sd_size


#noinspection PyCompatibility
class Analizer(object):
    _lang_ext_gtlang = re.compile(r'c_(\w\w)_(\w\w)\.txt')
    _lang_ext_jibbigo = re.compile(r's2s-mob-(\w\w).{4}(\w\w).{9}\.s2s')
    _lang_tv_snddict = re.compile('db_(\d\d?)_.+\.snd')
    _lang_tv_sndphrb = re.compile('phr_(\d\d)\.snd')
    _lang_ulearn = re.compile('DATA(\d\d)_(\d\d)')
    _tts_svox = re.compile('svox-.{6}(\w\w).{5}\.pil')
    _languages = collections.defaultdict(lambda: ("unknown", 0, "xxx"))
    _languages.update(langs)
    _languages.update(
        {"iw": _languages["he"], "jp": _languages["ja"], "ua": _languages["uk"], "us": _languages["en"]})
    _languages_by_num = {v[1]: v[0] for v in _languages.values()}


    def __init__(self, filename):
        facet = {'_set_apps_ectaco': 'apps_ectaco', '_set_apps_other': 'apps_other', '_set_feature_tts': 'feature_tts',
                 '_set_feature_sr': 'feature_sr', '_set_feature_gt': 'feature_gt',
                 '_set_voice_dictionary': 'voice_dictionary', '_set_voice_phrasebook': 'voice_phrasebook',
                 '_set_photo_text': 'photo_text', '_set_ulearn': 'ulearn', '_set_ulearn2': 'ulearn2',
                 '_set_feature_jibbigo': 'feature_jibbigo'}
        for f in facet:
            self.__setattr__(f, set())
        self._data = collections.defaultdict(lambda: str())
        self._data['project_model'], self._data['sd_size'] = '', ''
        self._data['project_id'] = os.path.basename(filename)
        ext = os.path.splitext(filename)[1].lower()
        with TempDir() as tempdir:
            if ext in ('.7z', '.exe'):
                Analizer._unpack_7z(filename, tempdir)
            elif ext == '.zip':
                os.system('unzip %s -d %s >/dev/null 2>&1' % (name, tempdir))
            self._scan(tempdir, self._data)
        glue = lambda x: ', '.join(sorted(x, key=str.lower))
        self._data.update({facet[f]: glue(self.__getattribute__(f)) for f in facet})


    @property
    def data(self):
        return copy.deepcopy(self._data)


    # noinspection PyUnresolvedReferences
    def _scan(self, path, data, card=False):
        for root, dirs, files in os.walk(path):
            for f in files:
                name, ext = os.path.splitext(f)
                if f in ('system.img', 'userdata.img', 'ext.img'):
                    with ExtDir(os.path.join(root, f), path) as img:
                        self._scan(img, data)
                    continue
                elif f == "build.prop":
                    data['project_model'] = Analizer._get_project_model(os.path.join(root, f))
                elif f == 'sdcard.zip':
                    with TempDir(path) as sdcard:
                        os.system('unzip %s -d %s >/dev/null 2>&1' % (os.path.join(path, f), sdcard))
                        self._scan(sdcard, data, True)
                        sd_size = Analizer._get_dir_size(sdcard)
                        data['sd_size'] = '%.2f GB' % (sd_size / 1e9)
                elif f == 'sdcard.7z':
                    with TempDir(path) as sdcard:
                        Analizer._unpack_7z(os.path.join(path, f), sdcard)
                        self._scan(sdcard, data, True)
                        sd_size = Analizer._get_dir_size(sdcard)
                        data['sd_size'] = '%.2f GB' % (sd_size / 1e9)

                if ext == ".apk":
                    a, b = Analizer._get_application(f)
                    self._set_apps_ectaco.update(a)
                    self._set_apps_other.update(b)
                elif ext == ".txt":
                    if card:
                        set_ = {'{0} SD'.format(i) for i in Analizer._get_lang_ext(f, ext)}
                        self._set_feature_gt.update(set_)
                    else:
                        self._set_feature_gt.update(Analizer._get_lang_ext(f, ext))
                elif ext == ".pil":
                    self._set_feature_tts.update(Analizer._get_tts(f))
                elif ext == ".snd":
                    if card:
                        set_ = {'{0} SD'.format(i) for i in Analizer._get_lang_tv(f, 'dictionary')}
                        self._set_voice_dictionary.update(set_)
                        set_ = {'{0} SD'.format(i) for i in Analizer._get_lang_tv(f, 'phrasebook')}
                        self._set_voice_phrasebook.update(set_)
                    else:
                        self._set_voice_dictionary.update(Analizer._get_lang_tv(f, 'dictionary'))
                        self._set_voice_phrasebook.update(Analizer._get_lang_tv(f, 'phrasebook'))
                elif ext == ".s2s":
                    if card:
                        set_ = {'{0} SD'.format(i) for i in Analizer._get_lang_ext(f, ext)}
                        self._set_feature_jibbigo.update(set_)
                    else:
                        self._set_feature_jibbigo.update(Analizer._get_lang_ext(f, ext))
                elif ext == '.traineddata':
                    self._set_photo_text.update(Analizer._get_photo_text(name))
            for d in dirs:
                if d == "srec":
                    self._set_feature_sr.update(Analizer._get_feature_sr(os.path.join(root, d)))
                elif d == 'com.ectaco.ul':
                    self._set_ulearn.update(Analizer._get_lang_ulearn(os.path.join(root, d)))
                elif d == 'com.ectaco.ul2':
                    self._set_ulearn2.update(Analizer._get_lang_ulearn(os.path.join(root, d)))
        return data


    @staticmethod
    def _get_lang_ulearn(folder):
        result = set()
        for d in os.listdir(folder):
            match = Analizer._lang_ulearn.match(d)
            if match is None:
                continue
            x = int(match.group(1))
            y = int(match.group(2))
            a = Analizer._languages_by_num[x] if x in Analizer._languages_by_num else 'unknown'
            b = Analizer._languages_by_num[y] if y in Analizer._languages_by_num else 'unknown'
            result.add('-'.join((a, b)))
        return result


    @staticmethod
    def _get_lang_tv(filename, app='dictionary'):
        result = set()
        reg = Analizer._lang_tv_snddict
        if app not in ('dictionary', 'phrasebook'):
            return result
        if app == 'phrasebook':
            reg = Analizer._lang_tv_sndphrb
        for m in reg.finditer(filename):
            for n in m.groups():
                x = int(n)
                if x in Analizer._languages_by_num:
                    result.add(Analizer._languages_by_num[x])
        return result


    @staticmethod
    def _get_lang_ext(filename, ext='.txt'):
        result = set()
        reg = Analizer._lang_ext_gtlang
        if ext not in ('.txt', '.s2s'):
            return result
        elif ext == '.s2s':
            reg = Analizer._lang_ext_jibbigo
        for m in reg.finditer(filename):
            result |= {Analizer._languages[n][0] for n in m.groups()}
        return result


    @staticmethod
    def _get_tts(filename):
        tts = set()
        for m in Analizer._tts_svox.finditer(filename):
            for n in m.groups():
                tts.add(Analizer._languages[n][0])
        return tts


    @staticmethod
    def _get_application(filename):
        ectaco = """Crossword Dictionary EngLessons.apk FlashCards grammar Hangman
        Idioms IrregularVerbs JetbookReader.apk LT LTPW MT MTLauncher.apk Oxford PB
        PhotoText PhotoText PhotoTranslation PhotoTranslation PictDict.apk Sat.apk
        SpeedReading.apk ULearn ULearn2 Usatest.apk UT.apk
        """
        no_app = """AccountAndSyncSettings.apk ApplicationsProvider.apk AtciService.apk
        BackupRestoreConfirmation.apk BackupTransport.apk CalendarImporter.apk CalendarProvider.apk
        CDS_INFO.apk CertInstaller.apk com.android.backupconfirm Contacts.apk ContactsProvider.apk
        DefaultContainerService.apk Development.apk dm.apk DownloadProvider.apk DrmProvider.apk
        EctacoLiveWallpaper.apk EctacoLiveWallpaper_ics.apk EngineerCode.apk EngineerMode.apk
        EngineerModeSim.apk Exchange.apk FBReaderJ-plugin-tts.apk framework-res.apk Galaxy4.apk
        GestureBuilder.apk GmsCore.apk go.apk GoogleBackupTransport.apk GoogleContactsSyncAdapter.apk
        GoogleLoginService.apk GoogleLoginServiceICS GoogleLoginServiceICS.apk GooglePartnerSetup.apk
        GoogleQuickSearchBox.apk GoogleServicesFramework.apk GoogleServicesFrameworkICS.apk
        HoloSpiralWallpaper.apk HTMLViewer.apk KeyChain.apk Launcher2.apk LiveWallpapers.apk
        LiveWallpapersPicker.apk LuxChk.apk LuxTtsService.apk MagicSmokeWallpapers.apk MediaProvider.apk
        mediatek-res.apk MediaTekLocationProvider.apk MTKAndroidSuiteDaemon.apk MtkBt.apk
        MtkVideoLiveWallpaper.apk MtkWorldClockWidget.apk MusicFX.apk NoiseField.apk PackageInstaller.apk
        PhaseBeam.apk PicoTts.apk Protips.apk Provision.apk QuickSearchBox.apk SettingsProvider.apk
        SharedStorageBackup.apk Stk1.apk Stk2.apk SystemUI.apk TelephonyProvider.apk theme-res-mint.apk
        theme-res-mocha.apk theme-res-raspberry.apk TtsService.apk UserDictionaryProvider.apk Velvet.apk
        VisualizationWallpapers.apk VpnDialogs.apk VpnServices.apk WAPPushManager.apk VoiceSearchStub.apk
        Superuser.apk SetupWizard.apk RootExplorer.apk LatinImeDictionaryPack.apk InputDevices.apk
        GoogleEars.apk GoogleQuickSearchBoxJB.apk FusedLocation.apk ConnectivityManagerTest.apk
        BasicDreams.apk AppWizardService.apk
        """
        appnames = {"1MobileMarket.apk": "1 Mobile Market", "ApplicationsProvider.apk": "Search Applications Provider",
                    "bbc.mobile.news.ww.apk": "BBC News", "Browser.apk": "Internet",
                    "CalendarProvider.apk": "Calendar Storage", "CertInstaller.apk": "Certificate Installer",
                    "com.adobe.flashplayer-2.apk": "Adobe Flash Player 11.1",
                    "com.adobe.reader-1.apk": "Adobe Reader", "com.alensw.PicFolder-1.apk": "QuickPic",
                    "com.alphonso.pulse.apk": "Pulse", "com.badoo.mobile.apk": "Badoo",
                    "com.bytesequencing.android.dominoes.apk": "Dominoes!", "com.facebook.katana-1.apk": "Facebook",
                    "com.flyersoft.moonreader-1.apk": "Moon+ Reader", "com.fsck.k9-1.apk": "K-9 Mail",
                    "com.google.android.apps.inputmethod.cantonese.apk": "Google Cantonese Input",
                    "com.google.android.apps.inputmethod.hindi.apk": "Google Hindi Input",
                    "com.google.android.apps.inputmethod.zhuyin.apk": "Google Zhuyin Input",
                    "com.google.android.apps.translate-1.apk": "Google Translate",
                    "com.google.android.chess.apk": "Chess",
                    "com.google.android.inputmethod.japanese.apk": "Google Japanese Input",
                    "com.google.android.inputmethod.korean.apk": "Google Korean Input",
                    "com.google.android.inputmethod.latin.apk": "Google Keyboard",
                    "com.google.android.inputmethod.pinyin.apk": "Google Pinyin Input",
                    "com.google.android.voicesearch.apk": "Voice Search", "com.guardian.apk": "Guardian",
                    "com.hi5.app.apk": "Hi5", "com.icenta.sudoku.apk": "Sudoku Free",
                    "com.jayuins.mp3p_59.apk": "MePlayer Audio", "com.jibbigo.player-1.apk": "Jibbigo Translator",
                    "com.klye.ime.latin.apk": "MultiLing Keyboard", "com.livejournal.client-1.apk": "LiveJournal",
                    "com.magmamobile.game.checkers.apk": "Kings", "com.microsoft.bing.apk": "Bing",
                    "com.mobilityware.solitaire.apk": "Solitaire", "com.rmf.apk": "RMFon.pl",
                    "com.skype.raider-1.apk": "Skype", "com.twitter.android.apk": "Twitter",
                    "com.vkontakte.android-1.apk": "Vkontakte", "com.weather.Weather-1.apk": "The Weather Channel",
                    "com.workpail.inkpad.notepad.notes-1.apk": "Inkpad NotePad",
                    "com.xuvi.pretoefl.apk": "TOEFL iBT Preparation",
                    "com.zaggisworkshop.polishpress.apk": "Polska Prasa", 'com.obreey.reader.apk': 'PocketBook Reader',
                    'pl.pleng.russian-1.apk': 'Russian Translator',
                    'biz.bookdesign.librivox-1.apk': 'LibriVox Audio Books',
                    'com.anddoes.launcher-1.apk': 'Apex Launcher', 'com.android.chrome-1.apk': 'Google Chrome',
                    'com.easternspark.android.emergencynumbers-1.apk': 'World Emergency Numbers',
                    'com.ebay.mobile-1.apk': 'eBay', 'com.google.android.youtube-1.apk': 'YouTube',
                    'com.gsmdev.worldfactbook-1.apk': 'World Factbook',
                    'com.klye.ime.latin_103.apk': 'MultiLing Keyboard',
                    'com.tripadvisor.tripadvisor-1.apk': 'TripAdvisor',
                    'com.triposo.droidguide.world-1.apk': 'World Travel Guide by Triposo',
                    'imoblife.androidsensorbox-1.apk': 'Android Sensor Box',
                    "CPenService.apk": "C-Pen Core", "Crossword_ML.apk": "Linguistic Crossword",
                    "DefaultContainerService.apk": "Package Access Helper", "Dictionary_Ml.apk": "Dictionary",
                    "DictOnline.apk": "Dictionary Online", "DownloadProvider.apk": "Download Manager",
                    "DownloadProviderUi.apk": "Downloads", "DrmProvider.apk": "DRM Protected Content Storage",
                    "EMarket.apk": "ECTACO Market", "EngLessons.apk": "Video Courses 48 English Lessons",
                    "es_file_explorer.apk": "ES File Explorer", "Exchange.apk": "Exchange Services",
                    "FBReaderJ-plugin-tts.apk": "FBReader TTS plugin", "FBReaderJ.apk": "FBReader",
                    "FlashCards_ML.apk": "Learning Settings, Linguistic FlashCards, Pockets, Spell-It-Right, Translation Test",
                    "Gallery3D.apk": "Gallery", "Gazeta.apk": "Gazeta.Ru", "GmsCore.apk": "Google Play services",
                    "go.apk": "Google Search", "GTranslate.apk": "Voice Translator",
                    "Hangman_Ml.apk": "Vocabulary Builder", "Idioms_ML.apk": "Idioms",
                    "IrregularVerbs_ML.apk": "Irregular Verbs", "JetbookReader.apk": "jetBook Reader",
                    "LatinIME.apk": "Android Keyboard", "Launcher2.apk": "Launcher", "Leventhal.apk": "Video Courses",
                    "LibRu.apk": "Russian Books Online", "LiveMocha.apk": "English Online",
                    "LiveWallpapers.apk": "Android Live Wallpapers", "LT-ML.apk": "Language Teacher",
                    "LTPW-ML.apk": "Language Teacher PixWord", "LuxChk.apk": "LuxSelfTest",
                    "LuxTtsService.apk": "Lux TTS", "maildroid.apk": "MailDroid", "MediaProvider.apk": "Media Storage",
                    "miyowa.android.microsoft.wlm.apk": "Messenger WithYou",
                    "net.gordons.uscitizenship2011Edition.apk": "US Citizenship Test 2012 Edition",
                    "northern.captain.seabattle.apk": "Naval Clash", "org.wikipedia-1.apk": "Wikipedia",
                    "Oxford_Eng-Eng.apk": "English Dictionary in English",
                    "Oxford_Eng-Spa.apk": "English Dictionary in Spanish", "PB-ML.apk": "PhraseBook",
                    "PhotoText-lux2.apk": "PhotoText", "PhotoTranslation-lux2.apk": "Photo Translator",
                    "PictDict.apk": "Picture Dictionary", "pl.allegro.apk": "Allegro", "pl.gadugadu.apk": "GG",
                    "pl.onet.onethd.apk": "Onet News", "ru.odnoklassniki.android-1.apk": "Odnoklassniki",
                    "ru.yandex.searchplugin-1.apk": "Yandex Search", "Rurem.apk": "Russian TV and Video",
                    "Sat.apk": "SAT/TOEFL", "SpeedReading.apk": "SpeedReading Course", "Talk.apk": "Google Talk",
                    "tunein.player-1.apk": "TuneIn Radio", "ULearn2_Ml.apk": "U-Learn Advanced",
                    "ULearn_Ml.apk": "U-Learn", "Usatest.apk": "USA Interview", "UT.apk": "Universal Translator",
                    "Vending.apk": "Google Play Store", "VideoEditor.apk": "Movie Studio",
                    "Webinar.apk": "English Language Webinar"}
        blacklog = set(no_app.split())
        suite = set(ectaco.split())
        a = set()
        b = set()
        if filename in blacklog:
            return a, b
        name, ext = os.path.splitext(filename)
        apk = appnames[filename] if filename in appnames else name
        sup = {name.split(s)[0] for s in ('_', '-')}
        sup.add(filename)
        if sup & suite:
            a.add(apk)
        else:
            b.add(apk)
        return a, b


    @staticmethod
    def _get_dir_size(path):
        size = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                size += os.path.getsize(os.path.join(root, f))
        return size


    @staticmethod
    def _unpack_7z(src, dst):
        assert os.access(src, os.F_OK), 'file not found'
        assert os.path.isdir(dst), 'invalid directory'
        ext = os.path.splitext(src)[1].lower()
        assert ext in ('.exe', '.7z'), 'The "%s" is not a format. Known formats are EXE and 7Z.' % ext
        name = os.path.basename(src)
        if ext == '.exe':
            name = os.path.basename(".".join((str(os.path.splitext(src)[0]), "7z")))
        shutil.copy(src, os.path.join(dst, name))
        os.system('sync')
        try:
            os.chdir(dst)
            os.system("p7zip -d %s  >/dev/null 2>&1" % name)
        except FileNotFoundError as err:
            logger.error(err)


    @staticmethod
    def _get_project_model(filename):
        model = ''
        with open(filename, mode="r") as fp:
            for line in fp:
                if line.startswith("ro.product.model"):
                    model = line.split('=')[1]
                    break
        return model


    @staticmethod
    def _get_feature_sr(path):
        result = set()
        for n in os.listdir(path):
            m = n.split('-')[0]
            if m in Analizer._languages.keys():
                result.add(Analizer._languages[m][0])
        return result


    @staticmethod
    def _get_photo_text(name):
        result = tuple()
        if len(name) < 3:
            return result
        a = name[:3].lower()
        for v in Analizer._languages.values():
            if a == v[2]:
                result = v[0],
                break
        return result


#noinspection PyCompatibility
class ReleaseCollection(dict):
    _CSS_style = """
body {
    font-family: 'Helvetica Neue', Arial, Helvetica, sans-serif;
    font-size: 14px;
    line-height: 18px;
    color: #393939;
}
td {
    font-size: 12px;
    border: 1px solid silver;
    vertical-align: top;
    padding: 5px;
}
.header {
    font-size: 14px;
    font-weight: bold;
    color: #f6f6f6;
    background-color: #23719f;
}
.header2 {
    font-size: 14px;
    font-weight: bold;
    color: #f6f6f6;
    background-color: #46b946;
}
.dimmed {
    background-color: #dbdbdb;
}
"""

    #noinspection PyMethodOverriding
    def values(self):
        for project_id in self.keys():
            yield self[project_id]


    def items(self):
        for project_id in self.keys():
            yield (project_id, self[project_id])


    def __iter__(self):
        for project_id in sorted(super().keys()):
            yield project_id

    keys = __iter__


    #noinspection PyMethodMayBeStatic
    def __reversed__(self):
        for project_id in sorted(super().keys(), reverse=True):
            yield project_id


    def import_(self, path):
        if os.path.isdir(path):
            self.__import_dir(path)
            return True
        call = {'.xml': self.import_xml, '.json': self.import_json}
        ext = os.path.splitext(path)[1].lower()
        if ext in call:
            logger.info('Import data from "%s"' % os.path.basename(path))
            call[ext](path)
            return True
        else:
            logger.warning('The "%s" is not a format. Known formats are XML and JSON.' % ext)
            return False


    def export(self, filename, complete=False):
        if not any(self.keys()):
            logger.error('NO DATA to export')
            return False
        ext = os.path.splitext(filename)[1].lower()
        call = {'.xml': self.export_xml,
                '.htm': self.export_html,
                '.html': self.export_html,
                '.txt': self.export_text,
                '.json': self.export_json
        }
        if complete:
            name = os.path.splitext(filename)[0].lower()
            for f in (name + x for x in ('.xml', '.html', '.txt', '.json')):
                if not self.export(f, complete=False):
                    return False
        if ext in call:
            logger.info('Export data to "%s"' % os.path.basename(filename))
            call[ext](filename)
            if os.access(filename, os.F_OK):
                return True
            else:
                logger.warning('The "%s" was not exported.' % filename)
                return False
        else:
            logger.warning('The "%s" is not a format. Known formats are TEXT, XML, and  HTML.' % ext)
            return False


    def export_text(self, filename):
        wrapper = textwrap.TextWrapper(initial_indent="    ",
                                       subsequent_indent="    ")
        with open(filename, 'w', encoding='utf8') as fp:
            for release in self.values():
                apps_ectaco = '\n'.join(wrapper.wrap(release.apps_ectaco))
                apps_other = '\n'.join(wrapper.wrap(release.apps_other))
                dash_name = '=' * len(release.project_id)
                s = """{0.project_id}
{dash_name}
Model: {0.project_model}

Ectaco Applications
-------------------
{apps_ectaco}

3rd party Applications
----------------------
{apps_other}

- Dictionary Voice: {0.voice_dictionary}
- PhraseBook Voice: {0.voice_phrasebook}
- PhotoText Langs: {0.photo_text}
- ULearn Pairs: {0.ulearn}
- ULearn-2 Pairs: {0.ulearn2}
- TTS SVOX: {0.feature_tts}
- Google voice typing: {0.feature_sr}
- Google Translate: {0.feature_gt}
- Jibbigo: {0.feature_jibbigo}

SD card
-------
Size: {0.sd_size}

*****\n
""".format(release, dash_name=dash_name, apps_ectaco=apps_ectaco, apps_other=apps_other)
                fp.write(s)


    def export_json(self, filename):
        d = {r.project_id: {'project_id': r.project_id,
                            'project_model': r.project_model,
                            'apps_ectaco': r.apps_ectaco,
                            'apps_other': r.apps_other,
                            'voice_dictionary': r.voice_dictionary,
                            'voice_phrasebook': r.voice_phrasebook,
                            'photo_text': r.photo_text,
                            'ulearn': r.ulearn,
                            'ulearn2': r.ulearn2,
                            'feature_tts': r.feature_tts,
                            'feature_sr': r.feature_sr,
                            'feature_gt': r.feature_gt,
                            'feature_jibbigo': r.feature_jibbigo,
                            'sd_size': r.sd_size
        } for r in self.values()}
        with open(filename, 'w') as fp:
            json.dump(d, fp, indent='  ')


    def import_json(self, filename):
        if os.access(filename, os.F_OK):
            return False
        self.clear()
        with open(filename, 'r') as fp:
            d = json.load(fp)
            for key, value in d.items():
                release = Release(**value)
                self[key] = release
        if any(self.keys()):
            return True
        else:
            return False


    def import_xml(self, filename):
        if not os.access(filename, os.F_OK):
            return False

        def get_text(node_list):
            text = []
            for node in node_list:
                if node.nodeType == node.TEXT_NODE:
                    text.append(node.data)
            return "".join(text).strip()

        dom = xml.dom.minidom.parse(filename)
        self.clear()
        for element in dom.getElementsByTagName('release'):
            data = collections.defaultdict(lambda: str())
            data["project_id"] = element.getAttribute('project_id')
            data["project_model"] = element.getAttribute('project_model')
            apps_ectaco = element.getElementsByTagName('apps_ectaco')[0]
            data['apps_ectaco'] = get_text(apps_ectaco.childNodes)
            apps_other = element.getElementsByTagName('apps_other')[0]
            data['apps_other'] = get_text(apps_other.childNodes)
            voice_dictionary = element.getElementsByTagName('voice_dictionary')[0]
            data['voice_dictionary'] = get_text(voice_dictionary.childNodes)
            voice_phrasebook = element.getElementsByTagName('voice_phrasebook')[0]
            data['voice_phrasebook'] = get_text(voice_phrasebook.childNodes)
            photo_text = element.getElementsByTagName('photo_text')[0]
            data['photo_text'] = get_text(photo_text.childNodes)
            ulearn = element.getElementsByTagName('ulearn')[0]
            data['ulearn'] = get_text(ulearn.childNodes)
            ulearn2 = element.getElementsByTagName('ulearn2')[0]
            data['ulearn2'] = get_text(ulearn2.childNodes)
            feature_tts = element.getElementsByTagName('feature_tts')[0]
            data['feature_tts'] = get_text(feature_tts.childNodes)
            feature_sr = element.getElementsByTagName('feature_sr')[0]
            data['feature_sr'] = get_text(feature_sr.childNodes)
            feature_gt = element.getElementsByTagName('feature_gt')[0]
            data['feature_gt'] = get_text(feature_gt.childNodes)
            feature_jibbigo = element.getElementsByTagName('feature_jibbigo')[0]
            data['feature_jibbigo'] = get_text(feature_jibbigo.childNodes)
            sdcard = element.getElementsByTagName('sdcard')[0]
            data['sd_size'] = sdcard.getAttribute('sd_size')
            release = Release(**data)
            self[release.project_id] = release
        if any(self.keys()):
            return True
        else:
            return False


    @staticmethod
    def _export_xsl(filename):
        xslt = """<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns="http://www.w3.org/1999/xhtml">
<xsl:output method="xml" indent="yes"
    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>
<xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Releases</title>
            <style type="text/css">
                {css}
            </style>
            </head>
            <body>
                <table>
                    <xsl:apply-templates/>
                </table>
            </body>
    </html>
</xsl:template>
<xsl:template match="releases/*">
    <tr>
        <td class="header">File Name</td>
        <td class="header">Model</td>
        <td class="header">Ectaco Applications</td>
        <td class="header">3rd party Applications</td>
        <td class="header">Dictionary Voice</td>
        <td class="header">PhraseBook Voice</td>
        <td class="header">PhotoText input</td>
        <td class="header">ULearn pairs</td>
        <td class="header">ULearn-2 pairs</td>
        <td class="header">TTS SVOX</td>
        <td class="header">Google voice typing</td>
        <td class="header">Google Translate</td>
        <td class="header">Jibbigo</td>
        <td class="header2">SD: card Size</td>
    </tr>
    <tr>
        <td><xsl:value-of select="@project_id"/></td>
        <td><xsl:value-of select="@project_model"/></td>
        <xsl:apply-templates select="apps_ectaco"/>
        <xsl:apply-templates select="apps_other"/>
        <xsl:apply-templates select="voice_dictionary"/>
        <xsl:apply-templates select="voice_phrasebook"/>
        <xsl:apply-templates select="photo_text"/>
        <xsl:apply-templates select="ulearn"/>
        <xsl:apply-templates select="ulearn2"/>
        <xsl:apply-templates select="features"/>
        <xsl:apply-templates select="sdcard"/>
    </tr>
</xsl:template>
<xsl:template match="apps_ectaco">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="apps_other">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="voice_dictionary">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="voice_phrasebook">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="photo_text">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="ulearn">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="ulearn2">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="features">
    <td><xsl:value-of select="./feature_tts"/></td>
    <td><xsl:value-of select="./feature_sr"/></td>
    <td><xsl:value-of select="./feature_gt"/></td>
    <td><xsl:value-of select="./feature_jibbigo"/></td>
</xsl:template>
<xsl:template match="sdcard">
    <td class="dimmed"><xsl:value-of select="@sd_size"/></td>
</xsl:template>
</xsl:stylesheet>""".format(css=ReleaseCollection._CSS_style)
        with open(filename, mode='w') as fp:
            fp.write(xslt)


    def export_xml(self, filename):
        root = xml.etree.ElementTree.Element("releases")
        for release in self.values():
            try:
                element = xml.etree.ElementTree.Element("release", project_id=release.project_id,
                                                        project_model=release.project_model)
                apps_ectaco = xml.etree.ElementTree.SubElement(element, "apps_ectaco")
                apps_ectaco.text = release.apps_ectaco
                apps_other = xml.etree.ElementTree.SubElement(element, "apps_other")
                apps_other.text = release.apps_other
                voice_dictionary = xml.etree.ElementTree.SubElement(element, "voice_dictionary")
                voice_dictionary.text = release.voice_dictionary
                voice_phrasebook = xml.etree.ElementTree.SubElement(element, "voice_phrasebook")
                voice_phrasebook.text = release.voice_phrasebook
                photo_text = xml.etree.ElementTree.SubElement(element, 'photo_text')
                photo_text.text = release.photo_text
                ulearn = xml.etree.ElementTree.SubElement(element, 'ulearn')
                ulearn.text = release.ulearn
                ulearn2 = xml.etree.ElementTree.SubElement(element, 'ulearn2')
                ulearn2.text = release.ulearn2
                features = xml.etree.ElementTree.SubElement(element, "features")
                feature_tts = xml.etree.ElementTree.SubElement(features, "feature_tts")
                feature_tts.text = release.feature_tts
                feature_sr = xml.etree.ElementTree.SubElement(features, "feature_sr")
                feature_sr.text = release.feature_sr
                feature_gt = xml.etree.ElementTree.SubElement(features, "feature_gt")
                feature_gt.text = release.feature_gt
                feature_jibbigo = xml.etree.ElementTree.SubElement(features, "feature_jibbigo")
                feature_jibbigo.text = release.feature_jibbigo
                xml.etree.ElementTree.SubElement(element, "sdcard", sd_size=release.sd_size)
                root.append(element)
            except AttributeError as err:
                logger.error(err)
                # etree -> DOM for pretty output
        dom = xml.dom.minidom.parseString(xml.etree.ElementTree.tostring(root, encoding="UTF-8"))
        xsl = ".".join((str(os.path.splitext(filename)[0]), "xslt"))
        ins = dom.createProcessingInstruction('xml-stylesheet', 'type="text/xsl" href="%s"' % os.path.basename(xsl))
        r = dom.firstChild
        dom.insertBefore(ins, r)
        with open(filename, mode='w') as fp:
            fp.write(dom.toprettyxml())
            self._export_xsl(xsl)


    def export_html(self, filename):
        page_header = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head><title>Release Summary</title>
<meta equiv="content-type" content="text/html; charset=utf-8" />
<style>
{css}
</style></head><body>
<h3>Release Summary</h3>
<table>""".format(css=self._CSS_style)
        table_header = """<tr>
<td class="header">No.</td>
<td class="header">File Name</td>
<td class="header">Model</td>
<td class="header">Ectaco Applications</td>
<td class="header">3rd party Applications</td>
<td class="header">Dictionary Voice</td>
<td class="header">PhraseBook Voice</td>
<td class="header">PhotoText Lang</td>
<td class="header">ULearn pairs</td>
<td class="header">ULearn-2 pairs</td>
<td class="header">TTS SVOX</td>
<td class="header">Google voice typing</td>
<td class="header">Google Translate</td>
<td class="header">Jibbigo</td>
<td class="header2">SD: card Size</td>
</tr>"""
        with open(filename, mode='w') as fp:
            fp.write(page_header)
            for i, release in enumerate(self.values()):
                buff = list()
                buff.append('<tr>\n<td align="right">%i</td>' % (i + 1))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.project_id))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.project_model))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.apps_ectaco))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.apps_other))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.voice_dictionary))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.voice_phrasebook))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.photo_text))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.ulearn))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.ulearn2))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.feature_tts))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.feature_sr))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.feature_gt))
                buff.append('<td>%s</td>' % xml.sax.saxutils.escape(release.feature_jibbigo))
                buff.append('<td align="center" class="dimmed">%s</td>' % xml.sax.saxutils.escape(release.sd_size))
                buff.append('\n</tr>')
                fp.write(table_header + '\n'.join(buff))
            fp.write('</table>\n</body>\n</html>')


    def __import_dir(self, folder):
        self.clear()
        files = (os.path.join(folder, f) for f in os.listdir(folder) if f.lower().startswith(("lux2_", "sg_")))
        logger.info('Analyze folder "%s"' % os.path.basename(folder))
        for f in files:
            self.__import_file(f)


    def __import_file(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        if ext in ('.7z', '.exe', '.zip'):
            logger.info('Analyze file "%s"' % os.path.basename(filename))
            self[os.path.basename(filename)] = Release(**Analizer(filename).data)


    def refresh(self, folder='', filename=''):
        source = False
        if os.access(filename, os.F_OK):
            self.import_(filename)
            keys = set(self.keys())
            files = {f for f in os.listdir(folder) if f.lower().startswith(("lux2_", "sg_"))}
            if keys > files:
                for k in (k for k in self.keys() if k not in files):
                    self.pop(k, None)
            files -= set(self.keys())
            for f in files:
                self.__import_file(os.path.join(folder, f))
            source = True
        else:
            self.clear()
            if os.path.exists(folder):
                self.import_(folder)
                source = True
        if source:
            if self.export(filename, complete=True):
                logger.info('ALL DONE')
            else:
                logger.info('an ERROR occurred')
        else:
            logger.info('NOTHING to do')


def main():
    # test = ReleaseCollection()
    # test.refresh('/shares/releases/Lux/old', '/shares/releases/xml/testreport.xml')

    lux = ReleaseCollection()
    tlx = ReleaseCollection()

    threads = list()
    threads.append(
        threading.Thread(target=lux.refresh, args=('/shares/releases/Lux', '/shares/releases/xml/luxreport.xml')))
    threads.append(
        threading.Thread(target=tlx.refresh, args=('/shares/releases/Runbo', '/shares/releases/xml/tlxreport.xml')))
    for t in threads:
        t.start()


if __name__ == '__main__':
    main()