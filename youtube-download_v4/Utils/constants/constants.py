import os
import pathlib

RESOLUTIONS = {'Low': 18, 'Medium': 22, 'High': 137, 'Very High': 313}

CURRENT_PATH = pathlib.Path(__file__).parent.parent.parent
USER_DATA = pathlib.Path(os.path.join(os.environ['USERPROFILE'], 'documents', 'YouTubeDownloader'))
USER_WORK_DATA = USER_DATA.joinpath('logs_data')
USER_WORK_FILE_PATH = USER_WORK_DATA.joinpath('log_file.csv')

RESOURCES_PATH = CURRENT_PATH.joinpath('resources')
RESOURCES_32_PATH = RESOURCES_PATH.joinpath('32')
USER_WORK_FILE_HEADER = ['File name', 'Save location', 'Download URL', 'Only audio', 'Date']

COMBO_STYLE = {'width': 300, 'height': 40, 'corner_radius': 30, 'font': ('Times', 18, 'bold'), 'state': 'readonly',
               'dropdown_hover_color': 'blue', 'dropdown_text_color': 'lightgreen',
               'dropdown_font': ('Times', 18, 'bold'), 'dropdown_fg_color': 'darkblue'}

BUTTON_STYLE = {'text_color': 'black', 'hover_color': 'red', 'font': ('Times', 18, 'bold'),
                'corner_radius': 30, 'width': 120, 'height': 40}
