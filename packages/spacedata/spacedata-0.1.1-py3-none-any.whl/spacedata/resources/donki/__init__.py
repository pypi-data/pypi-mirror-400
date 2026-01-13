from spacedata.resources.base import BaseResource
from spacedata.resources.donki.cme import cme
from spacedata.resources.donki.cme_analysis import cme_analysis
from spacedata.resources.donki.flr import flr
from spacedata.resources.donki.gst import gst
from spacedata.resources.donki.hss import hss
from spacedata.resources.donki.ips import ips
from spacedata.resources.donki.mpc import mpc
from spacedata.resources.donki.notifications import notifications
from spacedata.resources.donki.rbe import rbe
from spacedata.resources.donki.sep import sep
from spacedata.resources.donki.wsa import wsa


class DONKIResource(BaseResource):
    cme = cme
    cme_analysis = cme_analysis
    gst = gst
    ips = ips
    flr = flr
    sep = sep
    mpc = mpc
    rbe = rbe
    hss = hss
    wsa = wsa
    notifications = notifications


__all__ = ["DONKIResource"]
