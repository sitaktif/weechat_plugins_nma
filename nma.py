# Author: sitaktif <romainchossart AT gmail DOT com>
# This plugin calls the pynma bindings via python when somebody says your
# nickname, sends you a query, etc.
#
# Requires:
# Weechat 0.3.0
# pynma.py (NMA python bindings) - get it on NMA website, on Github as a
#   standalone or just use https://github.com/sitaktif/weechat_plugins_nma which
#   includes both nma.py (the weechat script) and pynma.py (the API). Just put
#   pynma.py it in the same folder as nma.py.
#
# License: Released under GNU GPL v2
#
# Acknowledgements: Based on lavaramano's script "notify.py" v. 0.0.5 (thanks!)
#
# 2012-05-06, sitaktif
#     version 1.0.4: Add an option to send everything in push. Also change
#     default delimiters with brackets and make lines 80 chars wide.
# 2012-05-05, sitaktif
#     version 1.0.3: Manage (non-ASCII) UTF8 chars
# 2012-01-05, Ac-town
#     version 1.0.2: Fixes a few typos I ran into and adds only_away. Only_away
#     only sends notifications if you are marked away.
# 2011-09-19, sitaktif
#     version 1.0.1: Corrected a bug with debug functions
# 2011-07-22, sitaktif
#     version 1.0.0: Initial release
#
# Todo:
# - Do not send my own messages on query channels
# - Add help on options properly with weechat_config_set_desc_plugin

import weechat as w

w.register("nma", "sitaktif", "1.0.4", "GPL2",
    "nma: Receive notifications on NotifyMyAndroid app.", "", "")

# script options
settings = {
    "apikey"               : "",
    "nick_separator_left"  : "(",
    "nick_separator_right" : ") ",
    "emergency_hilights"   : "-1",
    "emergency_priv_msg"   : "0",
    "activated"            : "on",
    "show_hilights"        : "on",
    "show_priv_msg"        : "on",
    "use_push_if_possible" : "on",
    "smart_notification"   : "off",
    "only_away"            : "off",
    "debug"                : "off",
}

#severity_t = {
    #"emergency" : 2,
    #"high" : 1,
    #"normal" : 0,
    #"moderate" : -1,
    #"low": -2
#}

"""
Init
"""

for option, default_value in settings.items():
    if w.config_get_plugin(option) == "":
        w.config_set_plugin(option, default_value)

if w.config_get_plugin("apikey") == "":
    w.prnt("", "You haven't set your API key. Use /set "
            "plugins.var.python.nma.apikey \"you_nma_api_token\" to fix that.")


"""
Hooks
"""

# Hook command
w.hook_command("nma", "Activate NotifyMyAndroid notifications",
        "on | off",
        """    on : Activate notifications
    off : Deactivate notifications\n
        """,
        "on || off",
        "nma_cmd_cb", "");
# Hook privmsg/hilights
w.hook_print("", "irc_privmsg", "", 1, "notify_show", "")

from pynma import PyNMA
p = PyNMA()
p.addkey(w.config_get_plugin("apikey"))


"""
Helpers
"""

def _debug(text):
    if w.config_get_plugin("debug") == "on":
        w.prnt("", text)


"""
Functions
"""

def nma_cmd_cb(data, buffer, args):
    if args in ["on", "off"]:
        w.prnt("", "Notify My Android notifications %sactivated"
                % ("de" if args == "off" else ""))
        w.config_set_plugin('activated', args)
    else:
        w.prnt("", "Error: Invalid argument")
        w.command("", "/help nma")
    return w.WEECHAT_RC_OK


def notify_show(data, bufferp, uber_empty, tagsn, isdisplayed,
        ishilight, prefix, message):
    """Sends highlighted message to be printed on notification"""

    if w.config_get_plugin('activated') == "off":
        return w.WEECHAT_RC_OK

    if (w.config_get_plugin('smart_notification') == "on" and
            bufferp == w.current_buffer()):
        return w.WEECHAT_RC_OK

    if (w.config_get_plugin('only_away') == "on" and not
            w.buffer_get_string(bufferp, 'localvar_away')):
        return w.WEECHAT_RC_OK

    ret = None

    notif_body = u"%s%s%s%s" % (
            w.config_get_plugin('nick_separator_left').decode('utf-8'),
            prefix.decode('utf-8'),
            w.config_get_plugin('nick_separator_right').decode('utf-8'),
            message.decode('utf-8'))

    # PM (query)
    if (w.buffer_get_string(bufferp, "localvar_type") == "private" and
            w.config_get_plugin('show_priv_msg') == "on"):
        ret = show_notification("IRC private message",
        notif_body, int(w.config_get_plugin("emergency_priv_msg")))
        _debug("Message sent: %s. Return: %s." % (notif_body, ret))

    # Highlight (your nick is quoted)
    elif (ishilight == "1" and
            w.config_get_plugin('show_hilights') == "on"):
        bufname = (w.buffer_get_string(bufferp, "short_name") or
                w.buffer_get_string(bufferp, "name"))
        ret = show_notification(bufname.decode('utf-8'), notif_body,
                int(w.config_get_plugin("emergency_hilights")))
        _debug("Message sent: %s. Return: %s." % (notif_body, ret))

    if ret is not None:
        _debug(str(ret))

    return w.WEECHAT_RC_OK


def show_notification(chan, message, priority):
    global p
    # So far, hardcoded in pynma.py...
    if w.config_get_plugin('use_push_if_possible') == "on":
        if len(chan) + len(message) < 1021: 
            chan = "%s - %s" % (chan, message)
            message = ""
    return p.push("[IRC]", chan, message, '', priority, batch_mode=False)

# vim: autoindent expandtab smarttab shiftwidth=4
