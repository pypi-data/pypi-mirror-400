from .geometry import GeometryData

class GeomEfitLimiter(GeometryData):
    """
    Sub-class for efit limiter

    Implements:
    - plot:    Plot the limiting surface (2D only atm)
    """

    def _plot_elements(self, data, ax_2d, color=None):
        """
        Recursively loop over tree, and retrieve EFIT limiting surface.
        :param data: data tree (instance of StructuredWritable, with EFIT limiter tree structure)
        :return:
        """
        if hasattr(data, "R"):
            R = data.R
            Z = data.Z

            ax_2d.plot(R, Z, color=color, linewidth=1)
        else:
            for child in data.children:
                self._plot_elements(child, ax_2d, color=color)


    def plot(self, ax_2d=None, show=True, color=None):
        """
        Plot EFIT limiting surface in 2D
        :param ax_2d: matplotlib.axes._subplots.AxesSubplot for R-Z plot
        :param show: display plot
        :param color: color for bolometry lines of sight
        :return:
        """

        # Create axes if necessary
        import matplotlib.pyplot as plt

        data = self.data

        if ax_2d is None:
            fig = plt.figure()
            if ax_2d is None:
                ax_2d = fig.add_subplot(111)

        if color is None:
            color = "black"

        # Plot
        if ax_2d is not None:
            self._plot_elements(data, ax_2d, color=color)

            ax_2d.set_xlabel('R [m]')
            ax_2d.set_ylabel('Z [m]')
            ax_2d.set_aspect('equal', 'datalim')

        if show:
            plt.show()