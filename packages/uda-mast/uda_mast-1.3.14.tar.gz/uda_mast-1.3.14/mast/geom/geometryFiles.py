class GeometryFiles(object):
    """
    Class to return signals that should be read in for top-level groups
    (ie. groups that come from more than one file).
    Also returns the appropriate manipulation classes for the signals requested.
    """

    def __init__(self):
        """
        Init function
        :return:
        """
        self._signal_manip_map = {}
        self._build_map()

    # --------------------------
    def _build_map(self):
        """
        Defines maps
        :return:
        """
        # Map from top-level groups in each file to the appropriate manipulator

        self._signal_manip_map = { 'resistive bolometer': {'file': 'mast.geom.geomBolo', 'class': 'GeomBolo'},
                                   'limiter': {'file': 'mast.geom.geomEfitLimiter', 'class': 'GeomEfitLimiter'},
                                   'diamagnetic loops': {'file': 'mast.geom.geomRog', 'class': 'GeomRog'},
                                   'fluxloops': {'file': 'mast.geom.geomFluxloops', 'class': 'GeomFluxloops'},
                                   'Halo detectors': {'file': 'mast.geom.geomHaloSaddle', 'class': 'GeomHaloSaddle'},
                                   'mirnov': {'file': 'mast.geom.geomPickup', 'class': 'GeomPickup'},
                                   'pfcoils': {'file': 'mast.geom.geomEfitElements',
                                               'class': 'GeomEfitElements'},
                                   'pickup': {'file': 'mast.geom.geomPickup', 'class': 'GeomPickup'},
                                   'rogowskis': {'file': 'mast.geom.geomRog', 'class': 'GeomRog'},
                                   'saddle coils': {'file': 'mast.geom.geomHaloSaddle', 'class': 'GeomHaloSaddle'},
                                   'passive structure': {'file': 'mast.geom.geomEfitElements',
                                                         'class': 'GeomEfitElements'},
                                   'Langmuir Probes': {'file': 'mast.geom.geomLangmuir',
                                                       'class': 'GeomLangmuir'},
                                   'ELM coils': {'file': 'mast.geom.geomElm',
                                                       'class': 'GeomElm'}
                                   }

    # --------------------------
    def get_signals(self, geom_system):
        """
        From overall signal that was asked for, retrieve
        appropriate manipulation classes
        :param signal: Signal user asked for
        :return:
        """
        try:
            manip = self._signal_manip_map[geom_system]
        except KeyError:
            manip = None

        return manip

