# Author: sitaktif <sitaktif AT gmail DOT com>
# This plugin calls the pynma bindings via python when somebody says your nickname, sends you a query, etc.
# Requires Weechat 0.3.0
# To make it work, you need to get pynma.py from NotifyMyAndroid website or on github - https://github.com/uskr/pynma . Just put it in the same folder as the script)
# Released under GNU GPL v2
# Heavily based on lavaramano's script "notify.py" v. 0.0.5
#
# 2011-07-22, sitaktif
#     version 0.0.1: initial release

import weechat

weechat.register("nma", "sitaktif", "0.1.0", "GPL", "nma: Receive notifications on NotifyMyAndroid app.", "", "")

# script options
settings = {
    "apikey"               : "",
    "nick_separator_left"  : "<",
    "nick_separator_right" : "> ",
    "emergency_hilights"   : "-1",
    "emergency_priv_msg"   : "0",
    "activated"            : "on",
    "show_hilights"        : "on",
    "show_priv_msg"        : "on",
    "smart_notification"   : "off",
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
    if weechat.config_get_plugin(option) == "":
        weechat.config_set_plugin(option, default_value)

if weechat.config_get_plugin("apikey") == "":
    weechat.prnt("", "You haven't set your API key. Use /set plugins.var.python.nma.apikey \"you_nma_api_token\" to fix that.")


"""
Hooks
"""

# Hook command
weechat.hook_command("nma", "Activate NotifyMyAndroid notifications", "on | off",
                      "on : Activate notifications\n"
                      "off : Desactivate notifications\n",
                      "on || off",
                      "nma_cmd_cb", "");
# Hook privmsg/hilights
weechat.hook_print("", "irc_privmsg", "", 1, "notify_show", "")

from pynma import PyNMA
p = PyNMA()
p.addkey(weechat.config_get_plugin("apikey"))


"""
Helpers
"""

def _debug(text):
    if weechat.config_get_plugin("debug") == "on":
        weechat.prnt("", text)


"""
Functions
"""

def nma_cmd_cb(data, buffer, args):
    if args in ["on", "off"]:
        weechat.prnt("", "Notify My Android notifications %sactivated" 
                % ("de" if args == "off" else ""))
        weechat.config_set_plugin('activated', args)
    else:
        weechat.prnt("", "Error: Invalid argument")
        weechat.command("", "/help nma")
    return weechat.WEECHAT_RC_OK


def notify_show(data, bufferp, uber_empty, tagsn, isdisplayed,
        ishilight, prefix, message):
    """Sends highlighted message to be printed on notification"""

    if weechat.config_get_plugin('activated') == "off":
        return weechat.WEECHAT_RC_OK

    if (weechat.config_get_plugin('smart_notification') == "on" and
            bufferp == weechat.current_buffer()):
        return weechat.WEECHAT_RC_OK
    ret = None

    notif_body = "%s%s%s%s" % (weechat.config_get_plugin('nick_separator_left'), 
            prefix, weechat.config_get_plugin('nick_separator_right'), message)

    # PM (query)
    if (weechat.buffer_get_string(bufferp, "localvar_type") == "private" and
            weechat.config_get_plugin('show_priv_msg') == "on"):
        ret = show_notification("IRC private message",
        notif_body, int(weechat.config_get_plugin("priv_msg_emergency")))
        _debug("", "Message sent: %s. Return: %s." % (notif_body, ret))

    # Highlight (your nick is quoted)
    elif (ishilight == "1" and
            weechat.config_get_plugin('show_hilights') == "on"):
        bufname = (weechat.buffer_get_string(bufferp, "short_name") or
                weechat.buffer_get_string(bufferp, "name"))
        ret = show_notification(bufname, notif_body,
                int(weechat.config_get_plugin("hilights_emergency")))
        _debug("Message sent: %s. Return: %s." % (notif_body, ret))

    if ret is not None:
        _debug("", str(ret))

    return weechat.WEECHAT_RC_OK

def show_notification(chan, message, priority):
    global p
    return p.push("[IRC]", chan, message, '', priority, batch_mode=False)

# vim: autoindent expandtab smarttab shiftwidth=4
