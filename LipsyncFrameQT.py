# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Wed Apr 13 16:04:35 2005

# Papagayo-NG, a lip-sync tool for use with several different animation suites
# Original Copyright (C) 2005 Mike Clifton
# Contact information at http://www.lostmarble.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# import os
import string
import time

from PySide2.QtCore import QFile
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtUiTools import QUiLoader as uic


import webbrowser
import random
import re

from WaveformViewRewrite import WaveformView
from MouthViewQT import MouthView
# end wxGlade

from AboutBoxQT import AboutBox
from LipsyncDoc import *

app_title = "Papagayo-NG"
lipsync_extension = "*.pgo"
audio_extensions = "*.wav *.mp3 *.aiff *.aif *.au *.snd *.mov *.m4a"
open_wildcard = "{} and sound files ({} {})".format(app_title, audio_extensions, lipsync_extension)
audioExtensions = "*.wav;*.mp3;*.aiff;*.aif;*.au;*.snd;*.mov;*.m4a"
save_wildcard = "{} files ({})".format(app_title, lipsync_extension)
# openWildcard = "%s and sound files|*%s;%s" % (appTitle, lipsyncExtension, audioExtensions)
# openAudioWildcard = "Sound files|%s" % (audioExtensions)
# saveWildcard = "%s files (*%s)|*%s" % (appTitle, lipsyncExtension, lipsyncExtension)


class LipsyncFrame:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        ui_path = os.path.join(get_main_dir(), "rsrc/papagayo-ng2.ui")
        self.main_window = self.load_ui_widget(ui_path)
        self.main_window.setWindowTitle("%s" % app_title)
        self.loader = None
        self.ui_file = None
        self.ui = None
        self.doc = None
        self.about_dlg = None
        self.config = QtCore.QSettings("Lost Marble", "Papagayo-NG")

        # TODO: need a good description for this stuff
        print(dir(self.main_window))
        mouth_list = list(self.main_window.mouth_view.mouths.keys())
        mouth_list.sort()
        print(mouth_list)
        for mouth in mouth_list:
            self.main_window.mouth_choice.addItem(mouth)
        self.main_window.mouth_choice.setCurrentIndex(0)
        self.main_window.mouth_choice.current_mouth = self.main_window.mouth_choice.currentText()

        self.langman = LanguageManager()
        self.langman.init_languages()
        language_list = list(self.langman.language_table.keys())
        language_list.sort()

        c = 0
        select = 0
        for language in language_list:
            self.main_window.language_choice.addItem(language)
            if language == "English":
                select = c
            c += 1
        self.main_window.language_choice.setCurrentIndex(select)

        # setup phonemeset initialisation here
        self.phonemeset = PhonemeSet()
        for name in self.phonemeset.alternatives:
            self.main_window.phoneme_set.addItem(name)
        self.main_window.phoneme_set.setCurrentIndex(0)

        # setup export initialisation here
        exporter_list = ["MOHO", "ALELO", "Images"]
        c = 0
        select = 0
        for exporter in exporter_list:
            self.main_window.export_combo.addItem(exporter)
            if exporter == "MOHO":
                select = c
            c += 1
        self.main_window.export_combo.setCurrentIndex(select)

        self.ignore_text_changes = False
        # This adds our statuses to the statusbar
        self.mainframe_statusbar_fields = [app_title, "Stopped"]
        self.play_status = QtWidgets.QLabel()
        self.play_status.setText(self.mainframe_statusbar_fields[1])
        # An empty Label to add a separator
        self.sep_status = QtWidgets.QLabel()
        self.sep_status.setText(u"")
        self.main_window.statusbar.addPermanentWidget(self.sep_status)
        self.main_window.statusbar.addPermanentWidget(self.play_status)
        self.main_window.statusbar.showMessage(self.mainframe_statusbar_fields[0])
        # Connect Events
        self.main_window.action_play.triggered.connect(self.on_play)
        self.main_window.action_stop.triggered.connect(self.on_stop)
        self.main_window.action_exit.triggered.connect(self.quit_application)
        self.main_window.action_open.triggered.connect(self.on_open)
        self.main_window.action_save.triggered.connect(self.on_save)
        self.main_window.action_save_as.triggered.connect(self.on_save_as)
        self.main_window.action_zoom_in.triggered.connect(self.main_window.waveform_view.on_zoom_in)
        self.main_window.action_zoom_out.triggered.connect(self.main_window.waveform_view.on_zoom_out)
        self.main_window.action_reset_zoom.triggered.connect(self.main_window.waveform_view.on_zoom_reset)

        self.main_window.reload_dict_button.clicked.connect(self.on_reload_dictionary)
        self.main_window.waveform_view.horizontalScrollBar().sliderMoved.connect(self.main_window.waveform_view.on_slider_change)
        self.main_window.action_help_topics.triggered.connect(self.on_help)
        self.main_window.action_about_papagayo_ng.triggered.connect(self.on_about)
        self.main_window.export_combo.currentIndexChanged.connect(self.on_export_choice)
        self.main_window.voice_name_input.textChanged.connect(self.on_voice_name)
        self.main_window.text_edit.textChanged.connect(self.on_voice_text)
        self.main_window.export_button.clicked.connect(self.on_voice_export)
        self.main_window.breakdown_button.clicked.connect(self.on_voice_breakdown)
        self.main_window.choose_imageset_button.clicked.connect(self.on_voice_image_choose)
        self.main_window.mouth_choice.currentIndexChanged.connect(self.on_mouth_choice)
        self.main_window.voice_list.itemClicked.connect(self.on_sel_voice)
        self.main_window.volume_slider.valueChanged.connect(self.change_volume)
        self.main_window.new_button.clicked.connect(self.on_new_voice)
        self.main_window.delete_button.clicked.connect(self.on_del_voice)
        self.main_window.voice_name_input.textChanged.connect(self.on_voice_name)
        self.main_window.text_edit.textChanged.connect(self.on_voice_text)

        self.cur_frame = 0
        self.timer = None
        self.wv_height = 1
        self.old_height = self.wv_height
        self.zoom_factor = 1
        self.scroll_position = 0
        self.did_resize = False
        self.wv_pen = QtGui.QPen(QtCore.Qt.darkBlue)
        self.wv_brush = QtGui.QBrush(QtCore.Qt.blue)
        self.start_time = time.time()
        self.main_window.apply_fps.clicked.connect(self.apply_changed_fps)

    def load_ui_widget(self, ui_filename, parent=None):
        loader = uic()
        file = QFile(ui_filename)
        file.open(QFile.ReadOnly)
        loader.registerCustomWidget(MouthView)
        loader.registerCustomWidget(WaveformView)
        self.ui = loader.load(file, parent)
        file.close()
        return self.ui

    def apply_changed_fps(self):
        new_fps_value = self.main_window.fps_input.value()
        print('FPS changed to: {0}'.format(str(new_fps_value)))
        old_fps_value = self.doc.fps
        resize_multiplier = new_fps_value / old_fps_value
        self.doc.fps = new_fps_value
        wfv = self.main_window.waveform_view
        # wfv.default_samples_per_frame *= resize_multiplier
        # wfv.default_sample_width *= resize_multiplier
        #
        # wfv.sample_width = wfv.default_sample_width
        # wfv.samples_per_frame = wfv.default_samples_per_frame
        wfv.samples_per_sec = self.doc.fps * wfv.samples_per_frame
        # wfv.frame_width = wfv.sample_width * wfv.samples_per_frame
        #
        # for node in wfv.main_node.descendants:
        #     node.name.after_reposition()
        #     node.name.fit_text_to_size()
        # #self.main_window.waveform_view.recalc_waveform()
        # #self.main_window.waveform_view.create_waveform()
        # if wfv.temp_play_marker:
        #     wfv.temp_play_marker.setRect(wfv.temp_play_marker.rect().x(), 1, wfv.frame_width + 1, wfv.height())
        wfv.scene().setSceneRect(wfv.scene().sceneRect().x(), wfv.scene().sceneRect().y(),
                                 wfv.sceneRect().width() * resize_multiplier, wfv.scene().sceneRect().height())
        wfv.setSceneRect(wfv.scene().sceneRect())
        wfv.scroll_position *= resize_multiplier
        wfv.scroll_position = 0
        wfv.horizontalScrollBar().setValue(wfv.scroll_position)
        wfv.set_document(self.doc, force=True)

    def close_doc_ok(self):
        if self.doc is not None:
            if not self.doc.dirty:
                return True
            dlg = QtWidgets.QMessageBox()
            dlg.setText("Save changes to this project?")
            dlg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            dlg.setDefaultButton(QtWidgets.QMessageBox.Yes)
            dlg.setIcon(QtWidgets.QMessageBox.Question)
            result = dlg.exec_()
            if result == QtWidgets.QMessageBox.Yes:
                self.on_save()
                if not self.doc.dirty:
                    self.config.setValue("LastFPS", str(self.doc.fps))
                    return True
                else:
                    return False
            elif result == QtWidgets.QMessageBox.No:
                self.config.setValue("LastFPS", str(self.doc.fps))
                return True
            elif result == QtWidgets.QMessageBox.Cancel:
                return False
        else:
            return True

    def on_open(self):
        if not self.close_doc_ok():
            return
        print(self.config.value("WorkingDir", get_main_dir()))
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self.main_window,
                                                             "Open Audio or {} File".format(app_title),
                                                             self.config.value("WorkingDir", get_main_dir()),
                                                             open_wildcard)
        if file_path:
            print(file_path)
            self.config.setValue("WorkingDir", os.path.dirname(file_path))
            print(os.path.dirname(file_path))
            self.open(file_path)

    def open(self, path):
        self.doc = LipsyncDoc(self.langman, self)
        if path.endswith(lipsync_extension[1:]):
            # open a lipsync project
            self.doc.open(path)
            while self.doc.sound is None:
                # if no sound file found, then ask user to specify one
                dlg = QtWidgets.QMessageBox(self.main_window)
                dlg.setText('Please load correct audio file')
                dlg.setWindowTitle(app_title)
                dlg.setIcon(QtWidgets.QMessageBox.Warning)
                dlg.exec_()  # This should open it as a modal blocking window
                dlg.destroy()  # Untested, might not need it
                print(self.config.value("WorkingDir", get_main_dir()))
                file_path, _ = QtWidgets.QFileDialog(self.main_window,
                                                     "Open Audio",
                                                     self.config.value("WorkingDir", get_main_dir()),
                                                     open_wildcard)
                if file_path:
                    self.config.setValue("WorkingDir", os.path.dirname(file_path))
                    self.doc.open(file_path)
        else:
            # open an audio file
            self.doc.fps = int(self.config.value("LastFPS", 24))
            self.doc.open_audio(path)
            if self.doc.sound is None:
                self.doc = None
            else:
                self.doc.voices.append(LipsyncVoice("Voice 1"))
                self.doc.current_voice = self.doc.voices[0]
                self.doc.auto_recognize_phoneme()
                # check for a .trans file with the same name as the doc
                try:
                    txt_file = open("{}.trans".format(path[0].rsplit('.', 1)[0]), 'r')  # TODO: Check if path is correct
                    for line in txt_file:
                        self.main_window.voice_list.appendRow(QtGui.QStandardItem(line))
                except:
                    pass
        if self.doc is not None:
            self.main_window.setWindowTitle("{} [{}] - {}".format(self.doc.name, path, app_title))
            self.main_window.waveform_view.first_update = True
            self.main_window.waveform_view.set_document(self.doc)
            self.main_window.mouth_view.set_document(self.doc)
            # Reenable all disabled widgets TODO: Can likely be reduced
            self.main_window.vertical_layout_right.setEnabled(True)
            self.main_window.vertical_layout_left.setEnabled(True)
            self.main_window.volume_slider.setEnabled(True)
            self.main_window.volume_slider.setValue(50)
            self.main_window.action_save.setEnabled(True)
            self.main_window.action_save_as.setEnabled(True)
            self.main_window.menu_edit.setEnabled(True)
            self.main_window.choose_imageset_button.setEnabled(False)
            if self.doc.sound is not None:
                self.main_window.action_play.setEnabled(True)
                # self.main_window.action_stop.setEnabled(True)
                self.main_window.action_zoom_in.setEnabled(True)
                self.main_window.action_zoom_out.setEnabled(True)
                self.main_window.action_reset_zoom.setEnabled(True)

            self.main_window.voice_list.clear()
            for voice in self.doc.voices:
                self.main_window.voice_list.addItem(voice.name)
            self.main_window.voice_list.setCurrentRow(0)
            self.main_window.fps_input.setValue(self.doc.fps)
            self.main_window.voice_name_input.setText(self.doc.current_voice.name)
            self.main_window.text_edit.setText(self.doc.current_voice.text)
            # reload dictionary
            self.on_reload_dictionary()

    def on_save(self):
        if self.doc is None:
            return
        if self.doc.path is None:
            self.on_save_as()
            return
        self.doc.save(self.doc.path)

    def on_save_as(self):
        if self.doc is None:
            return
        print(self.config.value("WorkingDir", get_main_dir()))
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self.main_window,
                                                             "Save {} File".format(app_title),
                                                             self.config.value("WorkingDir", get_main_dir()),
                                                             save_wildcard)
        if file_path:
            self.config.setValue("WorkingDir", os.path.dirname(file_path))
            self.doc.save(file_path)
            self.main_window.setWindowTitle("{} [{}] - {}".format(self.doc.name, file_path, app_title))

    def on_close(self):
        if self.doc is not None:
            self.config.setValue("LastFPS", str(self.doc.fps))
            del self.doc
        self.doc = None
        self.main_window.waveform_view.first_update = True
        self.main_window.waveform_view.set_document(self.doc)
        # clear voice controls
        self.main_window.voice_name_input.clear()
        self.main_window.text_edit.clear()
        self.main_window.fps_input.clear()
        self.main_window.voice_list.clear()
        # disabling widgets
        self.main_window.vertical_layout_right.setEnabled(False)
        self.main_window.vertical_layout_left.setEnabled(False)
        self.main_window.volume_slider.setEnabled(False)
        self.main_window.action_save.setEnabled(False)
        self.main_window.action_save_as.setEnabled(False)
        self.main_window.menu_edit.setEnabled(False)
        self.main_window.action_play.setEnabled(False)
        self.main_window.action_stop.setEnabled(False)
        self.main_window.action_zoom_in.setEnabled(False)
        self.main_window.action_zoom_out.setEnabled(False)
        self.main_window.action_reset_zoom.setEnabled(False)

    def on_quit(self, event=None):
        self.on_close()
        self.close(True)

    def on_help(self, event=None):
        github_path = "https://github.com/morevnaproject/papagayo-ng/issues"
        test_path = "file://{}".format(r"D:\Program Files (x86)\Papagayo\help\index.html")
        real_path = "file://{}".format(os.path.join(get_main_dir(), r"help\index.html"))
        webbrowser.open(github_path)  # TODO: Fix path

    def on_about(self, event=None):
        self.about_dlg = AboutBox()
        self.about_dlg.main_window.show()

    def on_play(self, event=None):
        if (self.doc is not None) and (self.doc.sound is not None):
            self.cur_frame = -1
            self.main_window.action_play.setEnabled(False)
            self.main_window.action_stop.setEnabled(True)
            self.doc.sound.set_cur_time(0)
            self.doc.sound.play(False)
            self.timer = QtCore.QTimer()
            self.main_window.waveform_view.temp_play_marker.setVisible(True)
            self.timer.timeout.connect(self.on_play_tick)
            # self.connect(self.timer, None, self.on_play_tick)
            self.timer.start(250.0/self.doc.fps)

    def on_stop(self, event=None):
        if (self.doc is not None) and (self.doc.sound is not None):
            self.doc.sound.stop()
            self.doc.sound.set_cur_time(0)
            self.main_window.waveform_view.temp_play_marker.setVisible(False)
            self.main_window.mouth_view.set_frame(0)
            self.main_window.waveform_view.set_frame(0)
            self.main_window.action_stop.setEnabled(False)
            self.main_window.action_play.setEnabled(True)
            self.main_window.statusbar.showMessage("Stopped")
            self.main_window.waveform_view.horizontalScrollBar().setValue(self.main_window.waveform_view.scroll_position)
            self.main_window.waveform_view.update()
            QtCore.QCoreApplication.processEvents()

    def on_play_tick(self, event=None):
        if (self.doc is not None) and (self.doc.sound is not None):
            if self.doc.sound.is_playing():
                cur_frame = int(self.doc.sound.current_time() * self.doc.fps)
                if self.cur_frame != cur_frame:
                    self.cur_frame = cur_frame
                    self.main_window.mouth_view.set_frame(self.cur_frame)
                    self.main_window.waveform_view.set_frame(self.cur_frame)
                    try:
                        fps = 1.0 / (time.time() - self.start_time)
                    except ZeroDivisionError:
                        fps = 60
                    self.main_window.statusbar.showMessage("Frame: {:d} FPS: {:d}".format((cur_frame + 1), int(fps)))
                    self.main_window.waveform_view.scroll_position = self.main_window.waveform_view.horizontalScrollBar().value()
                    self.start_time = time.time()
            else:
                self.main_window.waveform_view.temp_play_marker.setVisible(False)
                self.on_stop()
                self.timer.stop()
                del self.timer

    def change_volume(self, e):
        if self.doc and self.doc.sound:
            self.doc.sound.set_volume(int(self.main_window.volume_slider.value()))

    def on_mouth_choice(self, event=None):
        self.main_window.mouth_view.current_mouth = self.main_window.mouth_choice.currentText()
        self.main_window.mouth_view.draw_me()

    def on_export_choice(self, event=None):
        if self.main_window.export_combo.currentText() == "Images":
            self.main_window.choose_imageset_button.setEnabled(True)
        else:
            self.main_window.choose_imageset_button.setEnabled(False)

    def on_voice_name(self, event=None):
        print(self.main_window.voice_name_input.text())
        if (self.doc is not None) and (self.doc.current_voice is not None):
            self.doc.dirty = True
            self.doc.current_voice.name = self.main_window.voice_name_input.text()
            self.main_window.voice_name_input.setText(self.doc.current_voice.name)
            self.main_window.voice_list.currentItem().setText(self.doc.current_voice.name)
            self.main_window.waveform_view.first_update = True
            self.main_window.waveform_view.set_document(self.doc)

    def on_voice_text(self, event=None):
        print(self.main_window.text_edit.toPlainText())
        if self.ignore_text_changes:
            return
        if (self.doc is not None) and (self.doc.current_voice is not None):
            self.doc.dirty = True
            self.doc.current_voice.text = self.main_window.text_edit.toPlainText()

    def on_voice_breakdown(self, event=None):
        if (self.doc is not None) and (self.doc.current_voice is not None):
            language = self.main_window.language_choice.currentText()
            phonemeset_name = self.main_window.phoneme_set.currentText()
            self.phonemeset.load(phonemeset_name)
            self.doc.dirty = True
            self.doc.current_voice.run_breakdown(self.doc.soundDuration, self, language, self.langman,
                                                 self.phonemeset)
            self.main_window.waveform_view.first_update = True
            self.ignore_text_changes = True
            self.main_window.text_edit.setText(self.doc.current_voice.text)
            self.ignore_text_changes = False
            self.main_window.waveform_view.set_document(self.doc, True)

    def on_voice_export(self, event=None):
        language = self.main_window.language_choice.currentText()
        if (self.doc is not None) and (self.doc.current_voice is not None):
            exporter = self.main_window.export_combo.currentText()
            message = ""
            default_file = ""
            wildcard = ""
            if exporter == "MOHO":
                message = "Export Lipsync Data (MOHO)"
                default_file = "{}".format(self.doc.soundPath.rsplit('.', 1)[0]) + ".dat"
                wildcard = "Moho switch files (*.dat)|*.dat"
            elif exporter == "ALELO":
                fps = int(self.config.value("FPS", 24))
                if fps != 100:
                    dlg = QtWidgets.QMessageBox()
                    dlg.setText("FPS is NOT 100 continue? (You will have issues downstream.)")
                    dlg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    dlg.setDefaultButton(QtWidgets.QMessageBox.Yes)
                    dlg.setIcon(QtWidgets.QMessageBox.Question)
                    result = dlg.exec_()
                    if result == QtWidgets.QMessageBox.Yes:
                        message = "Export Lipsync Data (ALELO)"
                        default_file = "{}.txt".format(self.doc.soundPath.rsplit('.', 1)[0])
                        wildcard = "Alelo timing files (*.txt)|*.txt"
                    elif result == QtWidgets.QMessageBox.No:
                        return
                    elif result == QtWidgets.QMessageBox.Cancel:
                        return
                else:
                    message = "Export Lipsync Data (ALELO)"
                    default_file = "{}.txt".format(self.doc.soundPath.rsplit('.', 1)[0])
                    wildcard = "Alelo timing files (*.txt)|*.txt"
            elif exporter == "Images":
                    message = "Export Image Strip"
                    default_file = "{}".format(self.doc.soundPath.rsplit('.', 1)[0])
                    wildcard = ""
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self.main_window,
                                                                 message,
                                                                 self.config.value("WorkingDir", get_main_dir()),
                                                                 wildcard)
            if file_path:
                self.config.setValue("WorkingDir", os.path.dirname(file_path))
                if exporter == "MOHO":
                    self.doc.current_voice.export(file_path)
                elif exporter == "ALELO":
                    self.doc.current_voice.export_alelo(file_path, language, self.langman)
                elif exporter == "Images":
                    self.doc.current_voice.export_images(file_path, self.main_window.mouth_choice.currentText())

    def on_sel_voice(self, e):
        if not self.doc:
            return
        self.ignore_text_changes = True
        self.doc.current_voice = self.doc.voices[self.main_window.voice_list.row(self.main_window.voice_list.currentItem())]
        self.main_window.voice_name_input.setText(self.doc.current_voice.name)
        self.main_window.text_edit.setText(self.doc.current_voice.text)
        self.ignore_text_changes = False
        self.main_window.waveform_view.first_update = True
        self.main_window.waveform_view.set_document(self.doc, True)
        self.main_window.waveform_view.update()
        self.main_window.mouth_view.draw_me()

    def on_new_voice(self, event=None):
        if not self.doc:
            return
        self.doc.dirty = True
        self.doc.voices.append(LipsyncVoice("Voice {:d}".format(len(self.doc.voices) + 1)))
        self.doc.current_voice = self.doc.voices[-1]
        self.main_window.voice_list.addItem(self.doc.current_voice.name)
        self.main_window.voice_list.setCurrentRow(self.main_window.voice_list.count() - 1)
        self.ignore_text_changes = True
        self.main_window.voice_name_input.setText(self.doc.current_voice.name)
        self.main_window.text_edit.setText(self.doc.current_voice.text)
        self.ignore_text_changes = False
        self.main_window.waveform_view.first_update = True
        self.main_window.waveform_view.set_document(self.doc, True)
        self.main_window.waveform_view.update()
        self.main_window.mouth_view.draw_me()

    def on_del_voice(self, event=None):
        if (not self.doc) or (len(self.doc.voices) == 1):
            return
        self.doc.dirty = True
        new_index = self.doc.voices.index(self.doc.current_voice)
        if new_index > 0:
            new_index -= 1
        else:
            new_index = 0
        self.doc.voices.remove(self.doc.current_voice)
        self.doc.current_voice = self.doc.voices[new_index]
        self.main_window.voice_list.clear()
        for voice in self.doc.voices:
            self.main_window.voice_list.addItem(voice.name)
        self.main_window.voice_list.setCurrentRow(new_index)
        self.main_window.voice_name_input.setText(self.doc.current_voice.name)
        self.main_window.text_edit.setText(self.doc.current_voice.text)
        self.main_window.waveform_view.first_update = True
        self.main_window.waveform_view.set_document(self.doc, True)
        self.main_window.waveform_view.update()
        self.main_window.mouth_view.draw_me()

    def on_voice_image_choose(self, event=None):
        language = self.main_window.language_choice.currentText()
        if (self.doc is not None) and (self.doc.current_voice is not None):
            voiceimage_path = QtWidgets.QFileDialog.getExistingDirectory(self.main_window,
                                                                         "Choose Path for Images",
                                                                         self.config.value("MouthDir",
                                                                                           os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                                                        "rsrc/mouths/")))
            if voiceimage_path:
                self.config.setValue("MouthDir", voiceimage_path)
                print(voiceimage_path)
                supported_imagetypes = QtGui.QImageReader.supportedImageFormats()
                for directory, dir_names, file_names in os.walk(voiceimage_path):
                    print("{0}:{1}:{2}".format(str(directory), str(dir_names), str(file_names)))
                    self.main_window.mouth_view.process_mouth_dir(directory, file_names, supported_imagetypes)
                mouth_list = list(self.main_window.mouth_view.mouths.keys())
                mouth_list.sort()
                print(mouth_list)
                self.main_window.mouth_choice.clear()
                for mouth in mouth_list:
                    self.main_window.mouth_choice.addItem(mouth)
                self.main_window.mouth_choice.setCurrentIndex(0)
                self.main_window.mouth_view.current_mouth = self.main_window.mouth_choice.currentText()

    def on_reload_dictionary(self, event=None):
        print("reload the dictionary")
        lang_config = self.doc.language_manager.language_table[self.main_window.language_choice.currentText()]
        self.doc.language_manager.load_language(lang_config, force=True)

    def quit_application(self):
        sys.exit(self.app.exec_())

# end of class LipsyncFrame
