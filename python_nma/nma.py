# Author: sitaktif <sitaktif AT gmail DOT com>
# This plugin calls the pynma bindings via python when somebody says your nickname, sends you a query, etc.
# To make it work, you may need to download: pynma.py from NotifyMyAndroid website.
# Requires Weechat 0.3.0
# Released under GNU GPL v2
# Heavily based on lavaramano's script "notify.py" v. 0.0.5
#
# 2011-07-22, sitaktif
#     version 0.0.1: initial release

# SCRIPTING NOTES:
#
# Tags (most commonly used):
#  no_filter, no_highlight, no_log, log0..log9 (log level),
#  notify_none, notify_message, notify_private, notify_highlight,
#  nick_xxx (xxx is nick in message),
#  irc_xxx (xxx is command name or number, see /server raw),
#  irc_numeric, irc_error, irc_action, irc_ctcp, irc_ctcp_reply, irc_smart_filter, away_info.
#
# Buffer local vars (list them):
# /buffer localvar

import weechat

weechat.register("nma", "sitaktif", "0.0.1", "GPL", "nma: Receive notifications ", "", "")

# script options
settings = {
    "apikey"               : "",
    "show_hilights"        : "on",
    "hilights_emergency"   : -1,
    "show_priv_msg"        : "on",
    "priv_msg_emergency"   : 0,
    "nick_separator_left"  : "<",
    "nick_separator_right" : "> ",
    "smart_notification"   : "off",
}

#urgencies = {
    #"emergency" : 2,
    #"high" : 1,
    #"normal" : 0,
    #"moderate" : -1,
    #"low": -2
#}

# Init everything
for option, default_value in settings.items():
    if weechat.config_get_plugin(option) == "":
        weechat.config_set_plugin(option, default_value)

# Hook privmsg/hilights
weechat.hook_print("", "irc_privmsg", "", 1, "notify_show", "")

from pynma import PyNMA
p = PyNMA()
p.addkey(weechat.config_get_plugin("apikey"))

# Functions
def notify_show(data, bufferp, uber_empty, tagsn, isdisplayed,
        ishilight, prefix, message):
    """Sends highlighted message to be printed on notification"""

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
        weechat.prnt("", "Message sent: %s. Return: %s." % (notif_body, ret))

    # Highlight (your nick is quoted)
    elif (ishilight == "1" and
            weechat.config_get_plugin('show_hilights') == "on"):
        bufname = (weechat.buffer_get_string(bufferp, "short_name") or
                weechat.buffer_get_string(bufferp, "name"))
        ret = show_notification(bufname, notif_body,
                int(weechat.config_get_plugin("hilights_emergency")))
        weechat.prnt("", "Message sent: %s. Return: %s." % (notif_body, ret))

    if ret is not None:
        weechat.prnt("", str(ret))

    return weechat.WEECHAT_RC_OK

def show_notification(chan, message, priority):
    global p
    return p.push("[IRC]", chan, message, '', priority, batch_mode=False)

# vim: autoindent expandtab smarttab shiftwidth=4
