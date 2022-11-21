from mivp_agent.const import KEY_ID, KEY_EPISODE_MGR_REPORT, KEY_EPISODE_MGR_STATE
from mivp_agent.util.parse import parse_report

FAKE_PAUSE_STATE = {
    KEY_ID: 'felix',
    'MOOS_TIME': 16923.012,
    'NAV_X': 98.0,
    'NAV_Y': 40.0,
    'NAV_HEADING': 180,
    KEY_EPISODE_MGR_REPORT: parse_report('NUM=0,DURATION=60.57,SUCCESS=false,WILL_PAUSE=false'),
    KEY_EPISODE_MGR_STATE: 'PAUSED'
}

FAKE_RUNNING_STATE = {
    KEY_ID: 'felix',
    'MOOS_TIME': 16923.012,
    'NAV_X': 98.0,
    'NAV_Y': 40.0,
    'NAV_HEADING': 180,
    KEY_EPISODE_MGR_REPORT: parse_report('NUM=0,DURATION=60.57,SUCCESS=false,WILL_PAUSE=false'),
    KEY_EPISODE_MGR_STATE: 'RUNNING'
}