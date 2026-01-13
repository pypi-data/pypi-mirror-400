
from .geometry import GeometryData


class GeomRog(GeometryData):
    """
    Manipulation class for rogowskis & diamagnetic loops.

    Implements:
    - plot : plot rogowskis & diamagnetic loops in 2D R-Z

    """

    def _walk_tree_plot_2d(self, data, ax_2d, color="magenta"):
        """
        Walk tree to plot rogowskis & diamagnetic loops
        :param data: data structure to walk
        :param ax_2d: matplotlib.axes._subplots.AxesSubplot for R-Z plot
        :param color: colour of loops for plotting
        :return:
        """

        try:
            path1_r = data["data/path_seg1"].R
            path1_z = data["data/path_seg1"].Z
            ax_2d.plot(path1_r, path1_z, linestyle="-", color=color)

            path2_r = data["data/path_seg2"].R
            path2_z = data["data/path_seg2"].Z
            ax_2d.plot(path2_r, path2_z, linestyle="-", color=color)

            path3_r = data["data/path_seg3"].R
            path3_z = data["data/path_seg3"].Z
            ax_2d.plot(path3_r, path3_z, linestyle="-", color=color)

            path4_r = data["data/path_seg4"].R
            path4_z = data["data/path_seg4"].Z
            ax_2d.plot(path4_r, path4_z, linestyle="-", color=color)
        except KeyError:
            # Continue down the tree
            for child in data.children:
                self._walk_tree_plot_2d(child, ax_2d, color=color)


    def plot(self, ax_2d=None, show=True, color="magenta"):
        """
        Plot rogowskis and diamagnetic loops data
        :param ax_2d: matplotlib.axes._subplots.AxesSubplot for R-Z plot
        :param show: display plot
        :return:
        """

        import matplotlib.pyplot as plt

        # Create axes if necessary
        if ax_2d is None:
            fig = plt.figure()
            ax_2d = fig.add_subplot(121)

        self._walk_tree_plot_2d(self.data, ax_2d, color=color)

        if show:
            plt.show()