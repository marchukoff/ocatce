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
import sys
import os.path
import re
import shutil
import tempfile
import textwrap
import xml.dom.minidom
import xml.etree.ElementTree
import xml.sax.saxutils

from functools import wraps

# It's logger and I've use it instead of print.
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


class Settings(object):
    home = os.path.dirname(__file__)
    with open(os.path.abspath(os.path.join(home,
                     'luxreport_tasks.json'))) as fp:
        tasks = json.load(fp)
    with open(os.path.abspath(os.path.join(home,
                         'luxreport_blacklog.json'))) as fp:
        blacklog = set(json.load(fp))        
    with open(os.path.abspath(os.path.join(home,
                         'luxreport_ectaco.json'))) as fp:
        suite = set(json.load(fp))
    with open(os.path.abspath(os.path.join(home,
                         'luxreport_appnames.json'))) as fp:
        appnames = json.load(fp)        
    lang_ext_gtlang = re.compile(r'c_(\w\w)_(\w\w)\.txt')
    lang_ext_jibbigo = re.compile(
           r's2s(?:-mob)?-(\w\w).{4}(\w\w).{7,9}\.s2s')
    lang_tv_snddict = re.compile('db_(\d\d?)_.+\.snd')
    lang_tv_sndphrb = re.compile('phr_(\d\d)\.snd')
    lang_ulearn = re.compile('DATA(\d\d)_(\d\d)')
    tts_svox = re.compile('svox-.{6}(\w\w).{5}\.pil')
# take it from /our/wiki/pmwiki.php/NSG/LangId
    languages = collections.defaultdict(lambda: ("unknown", 0, "xxx"))
    languages.update({
             "ar": ("arabic", 1, "ara"),"bg": ("bulgarian", 2, "bul"),
             "bs": ("bosnian", 46, "bos"), "cs": ("czech", 5, "cze"),
             "da": ("danish", 6, "dan"), "de": ("german", 7, "deu"),
             "el": ("greek", 8, "gre"), "en": ("english", 9, "eng"),
             "es": ("spanish", 10, "spa"), "et": ("estonian", 37, "est"),
             "fa": ("farsi", 41, "far"), "fi": ("finnish", 11, "fin"),
             "fr": ("french", 12, "fre"), "he": ("hebrew", 13, "heb"),
             "hi": ("hindi", 57, "hin"), "hr": ("croatian", 49, "cro"),
             "hu": ("hungarian", 14, "hun"), "hy": ("armenian", 43, "arm"),
             "id": ("indonesian", 33, "ind"), "it": ("italian", 16, "ita"),
             "ja": ("japanese", 17, "jap"), "ko": ("korean", 18, "kor"),
             "lt": ("lithuanian", 39, "lit"), "lv": ("latvian", 38, "lat"),
             "nl": ("dutch", 19, "dut"), "nn": ("norwegian", 20, "nno"),
             "pl": ("polish", 21, "pol"), "pt": ("portuguese", 22, "por"),
             "ro": ("romanian", 24, "rom"), "ru": ("russian", 25, "rus"),
             "sk": ("slovak", 27, "svk"), "sq": ("albanian", 28, "alb"),
             "sr": ("serbian", 66, "srb"), "sv": ("swedish", 29, "swe"),
             "th": ("thai", 30, "tha"), "tl": ("tagalog", 53, "tgl"),
             "tr": ("turkish", 31, "tur"), "uk": ("ukrainian", 34, "ukr"),
             "vi": ("vietnamese", 42, "vie"), "zh": ("chinese", 4, "chi")})
    languages.update(
        {"iw": languages["he"], "jp": languages["ja"],
         "ua": languages["uk"], "us": languages["en"]})
    languages_by_num = {v[1]: v[0] for v in languages.values()}


class AbstractDir(object):
    def __init__(self, name):
        if name:
            self._name = tempfile.mkdtemp(dir=name)
        else:
            self._name = tempfile.mkdtemp()


    @property
    def name(self):
        """The folder name"""
        assert os.path.exists(self._name), '"%s" not created' % self._name
        return self._name


    def __str__(self):
        return str(self._name)


    def __bool__(self):
        return os.path.exists(self._name)


    def exists(self):
        return self.__bool__()


    def remove(self):
        try:
            shutil.rmtree(self._name)
        except OSError as err:
            logger.error('An error occured to delete %s' % self._name)
            logger.error(err)


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

    def __init__(self, filename, mount_point='/shares/releases/xml'):
        self._filename = filename
        super().__init__(mount_point)


    def __enter__(self):
        os.system('/usr/local/etc/rc.d/fusefs onestart && ext4fuse %s %s' % 
                  (self._filename, self._name))
        os.system('ls -m %s' % self._name)
        return self.name


    def __exit__(self, *ignore):
        command = 'sync && '
        command += ' || '.join(['/usr/local/etc/rc.d/fusefs {0}'.format(s)
                            for s in ('onestop', 'faststop', 'forcestop')])
        os.system(command)
        super().remove()


def stripper(method):
    @wraps(method)
    def wrapper(self, s):
        r = str(s).strip() if s else "-"
        return method(self, r)
    return wrapper


class Release(object):
    def __init__(self, project_id, project_model="", apps_ectaco="",
                 apps_other="", voice_dictionary="", voice_phrasebook="",
                 photo_text="", ulearn='', ulearn2='', feature_tts="",
                 feature_sr="", feature_gt="", feature_jibbigo="",
                 sd_size=""):
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

        self.__facet = ['project_id', 'project_model', 'apps_ectaco',
                        'apps_other', 'voice_dictionary', 'voice_phrasebook',
                        'photo_text', 'ulearn', 'ulearn2', 'feature_tts',
                        'feature_sr', 'feature_gt', 'feature_jibbigo',
                        'sd_size']


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

    # noinspection PyAttributeOutsideInit
    @project_model.setter
    @stripper
    def project_model(self, s):
        self.__project_model = s


    @property
    def apps_ectaco(self):
        """The apps from Ectaco"""
        return self.__apps_ectaco


    # noinspection PyAttributeOutsideInit
    @apps_ectaco.setter
    @stripper
    def apps_ectaco(self, s):
        self.__apps_ectaco = s


    @property
    def apps_other(self):
        """The apps from all other"""
        return self.__apps_other

    # noinspection PyAttributeOutsideInit
    @apps_other.setter
    @stripper
    def apps_other(self, s):
        self.__apps_other = s


    @property
    def voice_dictionary(self):
        """The languages with true voice for the Dictionary"""
        return self.__voice_dictionary

    # noinspection PyAttributeOutsideInit
    @voice_dictionary.setter
    @stripper
    def voice_dictionary(self, s):
        self.__voice_dictionary = s


    @property
    def voice_phrasebook(self):
        """The languages with true voice for the PhraseBook"""
        return self.__voice_phrasebook

    # noinspection PyAttributeOutsideInit
    @voice_phrasebook.setter
    @stripper
    def voice_phrasebook(self, s):
        self.__voice_phrasebook = s


    @property
    def photo_text(self):
        """The languages for Photo Text / Input app"""
        return self.__photo_text

    # noinspection PyAttributeOutsideInit
    @photo_text.setter
    @stripper
    def photo_text(self, s):
        self.__photo_text = s


    @property
    def ulearn(self):
        """The language pair for ULearn app"""
        return self.__ulearn

    # noinspection PyAttributeOutsideInit
    @ulearn.setter
    @stripper
    def ulearn(self, s):
        self.__ulearn = s


    @property
    def ulearn2(self):
        """The language pair for ULearn-2 app"""
        return self.__ulearn2

    # noinspection PyAttributeOutsideInit
    @ulearn2.setter
    @stripper
    def ulearn2(self, s):
        self.__ulearn2 = s


    @property
    def feature_tts(self):
        """The languages for conversion text to speech"""
        return self.__feature_tts

    # noinspection PyAttributeOutsideInit
    @feature_tts.setter
    @stripper
    def feature_tts(self, s):
        self.__feature_tts = s


    @property
    def feature_sr(self):
        """The Voice Typing by Google"""
        return self.__feature_sr

    # noinspection PyAttributeOutsideInit
    @feature_sr.setter
    @stripper
    def feature_sr(self, s):
        self.__feature_sr = s


    @property
    def feature_gt(self):
        """Data for Google Translate (Internal)"""
        return self.__feature_gt

    # noinspection PyAttributeOutsideInit
    @feature_gt.setter
    @stripper
    def feature_gt(self, s):
        self.__feature_gt = s


    @property
    def feature_jibbigo(self):
        """The languages for Jibbigo translator"""
        return self.__feature_jibbigo

    # noinspection PyAttributeOutsideInit
    @feature_jibbigo.setter
    @stripper
    def feature_jibbigo(self, s):
        self.__feature_jibbigo = s


    @property
    def sd_size(self):
        """The size of data of SD card"""
        return self.__sd_size

    # noinspection PyAttributeOutsideInit
    @sd_size.setter
    @stripper
    def sd_size(self, s):
        self.__sd_size = s


    def __repr__(self):
        return "%s(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r)" % (
            self.__class__.__name__, self.project_id, self.project_model,
            self.apps_ectaco, self.apps_other, self.voice_dictionary,
            self.voice_phrasebook, self.photo_text, self.ulearn, self.ulearn2,
            self.feature_tts, self.feature_sr, self.feature_gt,
            self.feature_jibbigo, self.sd_size)

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


# noinspection PyCompatibility
class Analizer(object):
    def __init__(self, filename):
        facet = {'_set_apps_ectaco': 'apps_ectaco',
                 '_set_apps_other': 'apps_other',
                 '_set_feature_tts': 'feature_tts',
                 '_set_feature_sr': 'feature_sr',
                 '_set_feature_gt': 'feature_gt',
                 '_set_voice_dictionary': 'voice_dictionary',
                 '_set_voice_phrasebook': 'voice_phrasebook',
                 '_set_photo_text': 'photo_text',
                 '_set_ulearn': 'ulearn',
                 '_set_ulearn2': 'ulearn2',
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
                os.system('unzip %s -d %s >/dev/null 2>&1' %
                          (filename, tempdir))
            self._scan(tempdir, self._data)
        glue = lambda x: ', '.join(sorted(x, key=str.lower))
        self._data.update(
                    {facet[f]: glue(self.__getattribute__(f)) for f in facet})


    @property
    def data(self):
        return copy.deepcopy(self._data)


    @staticmethod
    def _size_GB(path):
        return 1e-9 * sum([os.path.getsize(os.path.join(a, f))
                           for a, b, c in os.walk(path) for f in c])


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
                    data['project_model'] = Analizer._get_project_model(
                                                    os.path.join(root, f))
                elif f == 'sdcard.zip':
                    with TempDir(path) as sdcard:
                        os.system('unzip %s -d %s >/dev/null 2>&1' %
                                  (os.path.join(path, f), sdcard))
                        self._scan(sdcard, data, True)
                        data['sd_size'] = '%.2f GB' % Analizer._size_GB(sdcard)
                elif f == 'sdcard.7z':
                    with TempDir(path) as sdcard:
                        Analizer._unpack_7z(os.path.join(path, f), sdcard)
                        self._scan(sdcard, data, True)
                        data['sd_size'] = '%.2f GB' % Analizer._size_GB(sdcard)
                elif f.endswith('.tar.gz'):
                    with TempDir(path) as sdcard:
                        Analizer._unpack_tgz(os.path.join(path, f), sdcard)
                        self._scan(sdcard, data, True)
                        data['sd_size'] = '%.2f GB' % Analizer._size_GB(sdcard)

                if ext == ".apk":
                    if f in Settings.blacklog:
                        continue
                    else:
                        a, b = Analizer._get_application(f)
                    if a:
                        self._set_apps_ectaco.add(a)
                    if b:
                        self._set_apps_other.add(b)
                elif ext == ".txt":
                    if card:
                        set_ = {'{0} SD'.format(i)
                                for i in Analizer._get_lang_ext(f, ext)}
                        self._set_feature_gt.update(set_)
                    else:
                        self._set_feature_gt.update(
                                            Analizer._get_lang_ext(f, ext))
                elif ext == ".pil":
                    self._set_feature_tts.update(Analizer._get_tts(f))
                elif ext == ".snd":
                    if card:
                        set_ = {'{0} SD'.format(i) for i in
                                    Analizer._get_lang_tv(f, 'dictionary')}
                        self._set_voice_dictionary.update(set_)
                        set_ = {'{0} SD'.format(i) for i in
                                    Analizer._get_lang_tv(f, 'phrasebook')}
                        self._set_voice_phrasebook.update(set_)
                    else:
                        self._set_voice_dictionary.update(
                                    Analizer._get_lang_tv(f, 'dictionary'))
                        self._set_voice_phrasebook.update(
                                    Analizer._get_lang_tv(f, 'phrasebook'))
                elif ext == ".s2s":
                    if card:
                        set_ = {'{0} SD'.format(i) for i in
                                    Analizer._get_lang_ext(f, ext)}
                        self._set_feature_jibbigo.update(set_)
                    else:
                        self._set_feature_jibbigo.update(
                                            Analizer._get_lang_ext(f, ext))
                elif ext == '.traineddata':
                    self._set_photo_text.update(
                                            Analizer._get_photo_text(name))
            for d in dirs:
                if d == "srec":
                    self._set_feature_sr.update(
                            Analizer._get_feature_sr(os.path.join(root, d)))
                elif d == 'com.ectaco.ul':
                    self._set_ulearn.update(
                            Analizer._get_lang_ulearn(os.path.join(root, d)))
                elif d == 'com.ectaco.ul2':
                    self._set_ulearn2.update(
                            Analizer._get_lang_ulearn(os.path.join(root, d)))
        return data


    @staticmethod
    def _get_lang_ulearn(folder):
        result = set()
        for d in os.listdir(folder):
            match = Settings.lang_ulearn.match(d)
            if match is None:
                continue
            x = int(match.group(1))
            y = int(match.group(2))
            a, b = 'unknown', 'unknown'
            if x in Settings.languages_by_num:
                a = Settings.languages_by_num[x]
            if y in Settings.languages_by_num:
                b = Settings.languages_by_num[y]
            result.add('-'.join((a, b)))
        return result


    @staticmethod
    def _get_lang_tv(filename, app='dictionary'):
        result = set()
        reg = Settings.lang_tv_snddict
        if app not in ('dictionary', 'phrasebook'):
            return result
        if app == 'phrasebook':
            reg = Settings.lang_tv_sndphrb
        for m in reg.finditer(filename):
            for n in m.groups():
                x = int(n)
                if x in Settings.languages_by_num:
                    result.add(Settings.languages_by_num[x])
        return result


    @staticmethod
    def _get_lang_ext(filename, ext='.txt'):
        result = set()
        reg = Settings.lang_ext_gtlang
        if ext not in ('.txt', '.s2s'):
            return result
        elif ext == '.s2s':
            reg = Settings.lang_ext_jibbigo
        for m in reg.finditer(filename):
            result |= {Settings.languages[n][0] for n in m.groups()}
        return result


    @staticmethod
    def _get_tts(filename):
        tts = set()
        for m in Settings.tts_svox.finditer(filename):
            for n in m.groups():
                tts.add(Settings.languages[n][0])
        return tts


    @staticmethod
    def _get_application(filename):
        name, ext = os.path.splitext(filename)
        appnames = Settings.appnames
        apk = appnames[filename] if filename in appnames else name
        sup = {name.split(s)[0] for s in ('_', '-')}
        sup.add(filename)
        if sup & Settings.suite:
            return (apk, '')
        else:
            return ('', apk)


    @staticmethod
    def _unpack_7z(src, dst):
        assert os.access(src, os.F_OK), 'file not found'
        assert os.path.isdir(dst), 'invalid directory'
        ext = os.path.splitext(src)[1].lower()
        assert ext in ('.exe','.7z'
               ), '"%s" is not a format. Known formats are EXE and 7Z.' % ext
        name = os.path.basename(src)
        if ext == '.exe' :
            name = os.path.basename(".".join((os.path.splitext(src)[0], "7z")))
        os.system('ln -s {0} {1}'.format(src, os.path.join(dst, name)))
        try:
            os.chdir(dst)
            os.system('p7zip -d %s  >/dev/null 2>&1' % name)
        except FileNotFoundError as err:
            logger.error(err)


    @staticmethod
    def _unpack_tgz(src, dst):
        assert os.access(src, os.F_OK), 'file not found'
        assert os.path.isdir(dst), 'invalid directory'
        name = os.path.basename(src)
        shutil.move(src, os.path.join(dst, name))
        os.system('sync')
        try:
            os.chdir(dst)
            os.system('tar xzf %s' % name)
            os.remove(name)
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
            if m in Settings.languages.keys():
                result.add(Settings.languages[m][0])
        return result


    @staticmethod
    def _get_photo_text(name):
        result = tuple()
        if len(name) < 3:
            return result
        a = name[:3].lower()
        for v in Settings.languages.values():
            if a == v[2]:
                result = v[0],
                break
        return result


# noinspection PyCompatibility
class ReleaseCollection(dict):
    _TESTING = re.compile('(eval|test)', re.IGNORECASE)
    _LUX = 'ftp://backbsd.ectaco.ru/Lux'
    _SG = 'ftp://backbsd.ectaco.ru/Runbo'


    # noinspection PyMethodOverriding
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


    # noinspection PyMethodMayBeStatic
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
            logger.warning(
               '"%s" is not a format. Known formats are XML and JSON.' % ext)
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
                if ext in ('.xml', '.htm', '.html'):
                    css = 'style.css'
                    if not os.access(os.path.join(
                            os.path.dirname(filename), css), os.F_OK):
                        try:
                            shutil.copy(os.path.join(Settings.home, css),
                                os.path.join(os.path.dirname(filename), css))
                        except OSError as err:
                            logger.error("OS error: {0}".format(err))
                return True
            else:
                logger.warning('The "%s" was not exported.' % filename)
                return False
        else:
            logger.warning(
        '"%s" is not a format. Known formats are TEXT, XML, and  HTML.' % ext)
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
""".format(release, dash_name=dash_name, apps_ectaco=apps_ectaco,
           apps_other=apps_other)
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
            voice_dictionary = element.getElementsByTagName(
                                                    'voice_dictionary')[0]
            data['voice_dictionary'] = get_text(voice_dictionary.childNodes)
            voice_phrasebook = element.getElementsByTagName(
                                                    'voice_phrasebook')[0]
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
            feature_jibbigo = element.getElementsByTagName(
                                                   'feature_jibbigo')[0]
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
        <title>Releases</title>
        <meta http-equiv="content-language" content="en" />
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta http-equiv="Content-Style-Type" content="text/css" />
        <meta http-equiv="Content-Script-Type" content="application/javascript" />
        <link rel="stylesheet" href="style.css" />
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
</xsl:stylesheet>"""
        with open(filename, mode='w') as fp:
            fp.write(xslt)


    def export_xml(self, filename):
        root = xml.etree.ElementTree.Element("releases")
        for release in self.values():
            try:
                element = xml.etree.ElementTree.Element(
                                    "release", project_id=release.project_id,
                                    project_model=release.project_model)
                apps_ectaco = xml.etree.ElementTree.SubElement(
                                                       element, "apps_ectaco")
                apps_ectaco.text = release.apps_ectaco
                apps_other = xml.etree.ElementTree.SubElement(
                                                      element, "apps_other")
                apps_other.text = release.apps_other
                voice_dictionary = xml.etree.ElementTree.SubElement(
                                                element, "voice_dictionary")
                voice_dictionary.text = release.voice_dictionary
                voice_phrasebook = xml.etree.ElementTree.SubElement(
                                                element, "voice_phrasebook")
                voice_phrasebook.text = release.voice_phrasebook
                photo_text = xml.etree.ElementTree.SubElement(
                                                      element, 'photo_text')
                photo_text.text = release.photo_text
                ulearn = xml.etree.ElementTree.SubElement(element, 'ulearn')
                ulearn.text = release.ulearn
                ulearn2 = xml.etree.ElementTree.SubElement(element, 'ulearn2')
                ulearn2.text = release.ulearn2
                features = xml.etree.ElementTree.SubElement(
                                                    element, "features")
                feature_tts = xml.etree.ElementTree.SubElement(
                                                       features, "feature_tts")
                feature_tts.text = release.feature_tts
                feature_sr = xml.etree.ElementTree.SubElement(
                                                      features, "feature_sr")
                feature_sr.text = release.feature_sr
                feature_gt = xml.etree.ElementTree.SubElement(
                                                      features, "feature_gt")
                feature_gt.text = release.feature_gt
                feature_jibbigo = xml.etree.ElementTree.SubElement(
                                               features, "feature_jibbigo")
                feature_jibbigo.text = release.feature_jibbigo
                xml.etree.ElementTree.SubElement(
                                 element, "sdcard", sd_size=release.sd_size)
                root.append(element)
            except AttributeError as err:
                logger.error(err)
                # etree -> DOM for pretty output
        dom = xml.dom.minidom.parseString(
                  xml.etree.ElementTree.tostring(root, encoding="UTF-8"))
        xsl = ".".join((str(os.path.splitext(filename)[0]), "xslt"))
        ins = dom.createProcessingInstruction('xml-stylesheet',
                          'type="text/xsl" href="%s"' % os.path.basename(xsl))
        r = dom.firstChild
        dom.insertBefore(ins, r)
        with open(filename, mode='w') as fp:
            fp.write(dom.toprettyxml())
            self._export_xsl(xsl)


    def export_html(self, filename):
        def nbsp(s):
            items = s.split(', ')
            result = ', '.join(
             [i.replace(' ', '&nbsp;').replace('-', '&#8209;') for i in items])
            return result
        page_header = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head><title>Release Summary</title>
<meta http-equiv="content-language" content="en" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Script-Type" content="application/javascript" />
<link rel="stylesheet" href="style.css" />
</head><body>
<h3>Release Summary</h3>
<table>"""
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
        
        f = xml.sax.saxutils.escape
        with open(filename, mode='w') as fp:
            fp.write(page_header)
            for i, release in enumerate(self.values()):
                t = list()
                s = f(release.project_id)
                t.append('<tr>\n<td align="right">%i</td>' % (i + 1))
                if ReleaseCollection._TESTING.search(
                  release.project_id) is not None:
                    t.append('<td>%s</td>' % f(release.project_id))
                elif release.project_id.startswith('lux2'):
                    t.append('<td><a href="{0}">{1}</a></td>'.format(
                             '/'.join((ReleaseCollection._LUX, s)), s))
                elif release.project_id.startswith('SG_'):
                    t.append('<td><a href="{0}">{1}</a></td>'.format(
                             '/'.join((ReleaseCollection._SG, s)), s))
                else:
                    t.append('<td>%s</td>' % f(release.project_id))
                t.append('<td>%s</td>' % f(release.project_model))
                t.append('<td>%s</td>' % nbsp(f(release.apps_ectaco)))
                t.append('<td>%s</td>' % nbsp(f(release.apps_other)))
                t.append('<td>%s</td>' % nbsp(f(release.voice_dictionary)))
                t.append('<td>%s</td>' % nbsp(f(release.voice_phrasebook)))
                t.append('<td>%s</td>' % f(release.photo_text))
                t.append('<td>%s</td>' % nbsp(f(release.ulearn)))
                t.append('<td>%s</td>' % nbsp(f(release.ulearn2)))
                t.append('<td>%s</td>' % f(release.feature_tts))
                t.append('<td>%s</td>' % f(release.feature_sr))
                t.append('<td>%s</td>' % nbsp(f(release.feature_gt)))
                t.append('<td>%s</td>' % nbsp(f(release.feature_jibbigo)))
                t.append('<td align="center" class="dimmed">%s</td>' % 
                        nbsp(f(release.sd_size)))
                t.append('\n</tr>')
                fp.write(table_header + '\n'.join(t))
            fp.write('</table>\n</body>\n</html>')


    def __import_dir(self, folder):
        self.clear()
        files = (os.path.join(folder, f) for f in
                 os.listdir(folder) if f.lower().startswith(("lux2_", "sg_")))
        logger.info('Analyze folder "%s"' % os.path.basename(folder))
        for f in files:
            self.__import_file(f)


    def __import_file(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        if ext in ('.7z', '.exe', '.zip'):
            logger.info('Analyze file "%s"' % os.path.basename(filename))
            self[os.path.basename(filename)] = Release(
                                                   **Analizer(filename).data)


    def refresh(self, folder='', filename=''):
        source = False
        if os.access(filename, os.F_OK):
            self.import_(filename)
            keys = set(self.keys())
            files = {f for f in
                 os.listdir(folder) if f.lower().startswith(("lux2_", "sg_"))}
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
                logger.info('OK')
            else:
                logger.info('an ERROR occurred')
        else:
            logger.info('NOTHING TO DO')


def main():
    for i in Settings.tasks:
        task = ReleaseCollection()
        task.refresh(i, Settings.tasks[i])


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        logger.warning('It works for FreeBSD')
        sys.exit()
    if os.getuid() == 0:
        main()
    else:
        logger.warning('You must be the root to use this script.')
