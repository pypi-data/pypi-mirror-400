from orangecanvas.localization.si import plsi, plsi_sz, z_besedo
from orangecanvas.localization import Translator  # pylint: disable=wrong-import-order
_tr = Translator("orangecontrib.network", "biolab.si", "Orange")
del Translator
from Orange.data import Table
from Orange.data.util import get_unique_names
from Orange.widgets import gui, widget, settings
from Orange.widgets.widget import Input, Output
from orangecontrib.network import Network
from orangecontrib.network.network import community as cd
from orangewidget.settings import rename_setting


class OWNxClustering(widget.OWWidget):
    name = _tr.m[40, 'Network Clustering']
    description = _tr.m[41, 'Orange widget for community detection in networks.']
    icon = "icons/NetworkClustering.svg"
    priority = 6430

    class Inputs:
        network = Input(_tr.m[42, "Network"], Network, default=True)

    class Outputs:
        network = Output(_tr.m[43, "Network"], Network)
        items = Output(_tr.m[44, "Items"], Table)

    resizing_enabled = False
    want_main_area = False

    settings_version = 2
    attenuate = settings.Setting(False)
    iterations = settings.Setting(1000)
    use_random_state = settings.Setting(False)
    hop_attenuation = settings.Setting(0.1)
    auto_apply = settings.Setting(True)

    def __init__(self):
        super().__init__()
        self.net = None
        self.cluster_feature = None

        box = gui.vBox(self.controlArea, _tr.m[45, "Label Propagation"])
        gui.spin(
            box, self, "iterations", 1, 100000, 1,
            label=_tr.m[46, "Max. iterations: "], callback=self.commit)
        gui.doubleSpin(box, self, "hop_attenuation", 0, 1, 0.01,
                       label=_tr.m[47, "Apply hop attenuation: "],
                       checked="attenuate", callback=self.commit)
        self.random_state = gui.checkBox(
            box, self, "use_random_state",
            label=_tr.m[48, "Replicable clustering"], callback=self.commit)

        gui.auto_apply(self.controlArea, self)

    @Inputs.network
    def set_network(self, net):
        self.net = net
        self.commit()

    def commit(self):
        kwargs = {'iterations': self.iterations}
        if self.attenuate:
            alg = cd.label_propagation_hop_attenuation
            kwargs['delta'] = self.hop_attenuation
        else:
            alg = cd.label_propagation

        if self.net is None:
            self.Outputs.items.send(None)
            self.Outputs.network.send(None)
            self.cluster_feature = None
            return

        if self.use_random_state:
            kwargs['seed'] = 0

        labels = alg(self.net, **kwargs)
        domain = self.net.nodes.domain
        # Tie a name for presenting clustering results to the widget instance
        if self.cluster_feature is None:
            self.cluster_feature = get_unique_names(domain, _tr.m[49, 'Cluster'])

        net = self.net.copy()
        cd.add_results_to_items(net, labels, self.cluster_feature)

        self.Outputs.items.send(net.nodes)
        self.Outputs.network.send(net)

        nclusters = len(set(labels.values()))

    @classmethod
    def migrate_settings(cls, settings, version):
        if version < 2:
            rename_setting(settings, "autoApply", "auto_apply")
            if hasattr(settings, "method"):
                rename_setting(settings, "method", "attenuate")


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    from orangecontrib.network.network.readwrite \
        import read_pajek, transform_data_to_orange_table
    from os.path import join, dirname

    fname = join(dirname(dirname(__file__)), 'networks', 'leu_by_genesets.net')
    network = read_pajek(fname)
    transform_data_to_orange_table(network)
    WidgetPreview(OWNxClustering).run(set_network=network)
