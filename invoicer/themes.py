#!/usr/bin/env python
# coding: utf-8
'''
This modules holds the various themes available for the application.
'''

# Imports #####################################################################


# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '23-MAR-2018'
__license__ = 'MIT'


# Globals #####################################################################
bs4_color_themes = [
    'black', 'blue', 'azure', 'green', 'orange', 'red', 'purple'
]


# See here https://www.w3schools.com/w3css/w3css_color_themes.asp
# `banner` is `w3-theme-d1`, and `table_header` is `w3-theme`
color_theme_data = {
    'red': {
        'banner': {'color': '#fff', 'background_color': '#f32617'},
        'table_header': {'color': '#fff', 'background_color': '#f44336'},
    },
    'khaki': {
        'banner': {'color': '#fff', 'background_color': '#ecdf6c'},
        'table_header': {'color': '#000', 'background_color': '#f0e68c'},
    },
    'blue-grey': {
        'banner': {'color': '#fff', 'background_color': '#57707d'},
        'table_header': {'color': '#fff', 'background_color': '#607d8b'},
    }
}
