from cmk.gui.i18n import _
from cmk.gui.plugins.wato import (
    rulespec_registry,
    HostRulespec,
    CheckParameterRulespecWithItem,
    RulespecGroupCheckParametersApplications
)
from cmk.gui.valuespec import Integer, Dictionary, Tuple, TextAscii

def _item_spec_squid():
    return TextAscii(
        title="Squid"
    )

def _parameter_valuespec_squid():
    return Dictionary(
            elements = [
                ( "client_reqps",
                   Tuple(
                       title = _("Set levels for Client Requests"),
                       elements = [
                             Integer(title = _("Warning at"), default_value = 600),
                             Integer(title = _("Critical at"), default_value = 800)])
                ),
                ( "client_hits",
                   Tuple(
                       title = _("Set levels for Client Hits"),
                       elements = [
                             Integer(title = _("Warning at"), default_value = 600),
                             Integer(title = _("Critical at"), default_value = 800)])
                ),
                ( "server_reqps",
                   Tuple(
                       title = _("Set levels for Server Requests"),
                       elements = [
                             Integer(title = _("Warning at"), default_value = 600),
                             Integer(title = _("Critical at"), default_value = 800)])
                ),
                ( "dns_time",
                   Tuple(
                       title = _("Set levels for DNS response time in seconds"),
                       elements = [
                             Integer(title = _("Warning at"), default_value = 2),
                             Integer(title = _("Critical at"), default_value = 4)])
                ),
                ( "cpu_time",
                   Tuple(
                       title = _("Set levels for Squid CPU time in percent"),
                       elements = [
                             Integer(title = _("Warning at"), default_value = 60),
                             Integer(title = _("Critical at"), default_value = 80)])
                ),
            ]
        )

    # forth = lambda old: type(old) != dict and { "client_reqps" : old } or old,
# )


rulespec_registry.register(
        CheckParameterRulespecWithItem(
            check_group_name="check_squid",
            group=RulespecGroupCheckParametersApplications,
            item_spec=_item_spec_squid,
            match_type="dict",
            parameter_valuespec=_parameter_valuespec_squid,
            title=lambda: "Squid"
        ))

