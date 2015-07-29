###################################
#    Created on Jul 29, 2015
#
#    @author: Grant Mercer
#
###################################

from Tkconstants import LEFT, END, RIGHT
import collections
import tkMessageBox
from Tkinter import Toplevel, Entry, Button, BOTH, Frame, \
    Label, BOTTOM, TOP, X, RIDGE, Checkbutton, IntVar, OptionMenu, StringVar

import constants
from sqlalchemy import or_
from db import db, DatabasePolygon
from tools.tools import center, get_shape_ranges, Observer
from tools.treelistbox import TreeListBox
from tools.tooltip import create_tool_tip
from log.log import logger
import re

class Query(Observer):
    """
    Observer object that holds a *ranges* dictionary which can be used
    to query the database once updated. Notifies it's parent upon ranges
    being changed
    """
    def __init__(self):
        Observer.__init__(self)
        self._ranges = {}

    @property
    def ranges(self):
        return self._ranges

    @ranges.setter
    def ranges(self, n_ranges):
        self._ranges = n_ranges
        self.notify()

class AdvancedSearchDialog(Toplevel):
    """
    A dialog for advanced searching, notifying `ImportDialog` when search parameters have
    been chosen and entered. Uses the observer design pattern to notify ``ImportDialog``
    when the ranges have been changed from an invalid state to valid.

    :param parent: The class to attach the observer to
    :param root: The base widget for ``Toplevel``
    """

    def __init__(self, parent, root):
        Toplevel.__init__(self, root)

        self.title = 'Advanced search'
        self.transient(root)
        self.shared_data = Query()
        self.shared_data.attach(parent)

        center(self, (constants.IMADVWIDTH, constants.IMADVHEIGHT))

        window_frame = Frame(self)
        window_frame.pack(fill=BOTH, expand=True)
        top_window_frame = Frame(window_frame)
        top_window_frame.pack(side=TOP, fill=X, expand=False)
        Label(top_window_frame, text='Filter by: ').pack(side=LEFT, padx=15, pady=5)
        Label(top_window_frame, text='Leave fields untouched that you do not wish to search by',
              font=('Helvetica', 8)).pack(side=RIGHT, padx=15, pady=5)
        bottom_window_frame = Frame(window_frame)
        bottom_window_frame.pack(side=TOP, fill=BOTH, expand=False, padx=15)
        bottom_window_frame.config(highlightthickness=1)
        bottom_window_frame.config(highlightbackground='grey')
        Label(bottom_window_frame, text='Plot ').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        Label(bottom_window_frame, text='Date ').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        Label(bottom_window_frame, text='Time Range ').grid(row=2, column=0, padx=5, pady=5, sticky='w')
        Label(bottom_window_frame, text='Latitude Range ').grid(row=3, column=0, padx=5, pady=5, sticky='w')
        Label(bottom_window_frame, text='File ').grid(row=4, column=0, padx=5, pady=5, sticky='w')

        self.plots = StringVar()
        self.am_pm = StringVar()
        self.plot_entry = OptionMenu(bottom_window_frame, self.plots, 'backscattered', 'depolarized', 'vfm')
        self.plot_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w', columnspan=3)

        self.date_entry = Entry(bottom_window_frame, width=25)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w', columnspan=4)
        self.date_entry.insert(END, '0000-00-00')

        self.b_time_entry = Entry(bottom_window_frame, width=10)
        self.b_time_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.b_time_entry.insert(END, '00:00:00')
        Label(bottom_window_frame, text='to').grid(row=2, column=2, pady=5, sticky='w')
        self.e_time_entry = Entry(bottom_window_frame, width=10)
        self.e_time_entry.grid(row=2, column=3, padx=5, pady=5, sticky='w')
        self.e_time_entry.insert(END, '00:00:00')

        self.am_pm_menu = OptionMenu(bottom_window_frame, self.am_pm, 'am', 'pm')
        self.am_pm_menu.grid(row=2, column=4, pady=5, sticky='w')

        self.b_lat_entry = Entry(bottom_window_frame, width=10)
        self.b_lat_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        self.b_lat_entry.insert(END, '0.0')
        Label(bottom_window_frame, text='to').grid(row=3, column=2, pady=5, sticky='w')
        self.e_lat_entry = Entry(bottom_window_frame, width=10)
        self.e_lat_entry.grid(row=3, column=3, padx=5, pady=5, sticky='w')
        self.e_lat_entry.insert(END, '0.0')

        self.file_entry = Entry(bottom_window_frame, width=25)
        self.file_entry.grid(row=4, column=1, padx=5, pady=5, sticky='w', columnspan=4)

        bottom_button_frame = Frame(window_frame)
        bottom_button_frame.pack(side=TOP, fill=BOTH, expand=False)

        Button(bottom_button_frame, text='Search', command=self.parse_ranges).\
            pack(side=LEFT, padx=15, pady=10)

    def parse_ranges(self):
        """
        Command for the search button, upon the user clicking the search button this function
        will perform a number of regex parsing to ensure all fields contain valid numbers, then
        sets the observers range dictionary to the valid fields and destroys AdvancedSearchDialog.
        If any fields are invalid, an error will be displayed and the function will return, keeping
        the window open and allowing the user to fix their error.
        """
        date = self.date_entry.get()
        r_date = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
        valid_entries = dict()
        if r_date.match(date) is None:
            logger.error('Invalid date entered \'%s\'' % date)
            tkMessageBox.showerror('Invalid entry', 'Invalid date \'%s\' entered,' % date +
                                   ' must match year-mo-day format')
            return
        valid_entries['date'] = date

        beg_time = self.b_time_entry.get()
        r_time = re.compile('[0-9]{2}:[0-9]{2}:[0-9]{2}')
        if r_time.match(beg_time) is None:
            logger.error('Invalid beginning time range entered \'%s\'' % beg_time)
            tkMessageBox.showerror('Invalid entry', 'Invalid beginning time range' +
                                   ' \'%s\', must match hr:mn:sc format' % beg_time)
            return
        valid_entries['btime'] = beg_time

        end_time = self.e_time_entry.get()
        if r_time.match(end_time) is None:
            logger.error('Invalid ending time range entered \'%s\'' % end_time)
            tkMessageBox.showerror('Invalid entry', 'Invalid ending time range' +
                                   ' \'%s\', must match hr:mn:sc format' % end_time)
            return
        valid_entries['etime'] = end_time

        beg_lat = self.b_lat_entry.get()
        r_lat = re.compile('[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?')
        if r_lat.match(beg_lat) is None:
            logger.error('Invalid beginning lat range entered \'%s\'' % beg_lat)
            tkMessageBox.showerror('Invalid entry', 'Invalid beginning latitude range' +
                                   ' \'%s\', must be a valid number(e.g. -2.3 , 4, 0.0)'
                                   % beg_lat)
            return
        valid_entries['blat'] = beg_lat

        end_lat = self.e_lat_entry.get()
        if r_lat.match(end_lat) is None:
            logger.error('Invalid ending lat range entered \'%s\'' % end_lat)
            tkMessageBox.showerror('Invalid field', 'Invalid ending latitude range' +
                                   ' \'%s\', must be valid number(e.g. -2.3, 4, 0.0'
                                   % end_lat)
            return
        valid_entries['elat'] = end_lat

        # update ranges dictionary which will call ImportDialog receive()
        self.shared_data.ranges = valid_entries
        self.destroy()
