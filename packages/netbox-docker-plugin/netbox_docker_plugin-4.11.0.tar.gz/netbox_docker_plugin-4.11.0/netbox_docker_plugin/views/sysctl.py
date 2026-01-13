"""Sysctl views definitions"""

from netbox.views import generic
from .. import tables, filtersets
from ..forms.sysctl import SysctlForm
from ..models.container import Sysctl


class SysctlListView(generic.ObjectListView):
    """Sysctl list view definition"""

    queryset = Sysctl.objects.all()
    table = tables.SysctlTable
    filterset = filtersets.SysctlFilterSet


class SysctlEditView(generic.ObjectEditView):
    """Sysctl edition view definition"""

    queryset = Sysctl.objects.all()
    form = SysctlForm


class SysctlDeleteView(generic.ObjectDeleteView):
    """Sysctl delete view definition"""

    queryset = Sysctl.objects.all()
