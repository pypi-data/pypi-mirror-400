from orangecanvas.localization.si import plsi, plsi_sz, z_besedo
from orangecanvas.localization import Translator  # pylint: disable=wrong-import-order
_tr = Translator("orangecontrib.network", "biolab.si", "Orange")
del Translator
from itertools import chain

import numpy as np
from AnyQt.QtWidgets import QFormLayout

from Orange.data import DiscreteVariable, Table
from Orange.widgets import gui
from Orange.widgets.settings import DomainContextHandler, ContextSetting, \
    Setting
from Orange.widgets.utils.itemmodels import VariableListModel
from Orange.widgets.utils.signals import Output, Input
from Orange.widgets.widget import OWWidget, Msg

from orangecontrib.network import Network
from orangecontrib.network.network import twomode


class OWNxSingleMode(OWWidget):
    name = _tr.m[294, "Single Mode"]
    description = _tr.m[295, "Convert multimodal graphs to single modal"]
    icon = "icons/SingleMode.svg"
    priority = 7000

    want_main_area = False
    resizing_enabled = False

    settingsHandler = DomainContextHandler(
        match_values=DomainContextHandler.MATCH_VALUES_ALL)
    variable = ContextSetting(None)
    connect_value = ContextSetting(0)
    connector_value = ContextSetting(0)
    weighting = Setting(0)

    class Inputs:
        network = Input(_tr.m[296, "Network"], Network)

    class Outputs:
        network = Output(_tr.m[297, "Network"], Network)

    class Warning(OWWidget.Warning):
        ignoring_missing = Msg(_tr.m[298, "Nodes with missing data are being ignored."])

    class Error(OWWidget.Error):
        no_data = Msg(_tr.m[299, "Network has additional data."])
        no_categorical = Msg(_tr.m[300, "Data has no categorical features."])
        same_values = Msg(_tr.m[301, "Values for modes cannot be the same."])

    def __init__(self):
        super().__init__()
        self.network = None

        form = QFormLayout()
        form.setFieldGrowthPolicy(form.AllNonFixedFieldsGrow)
        gui.widgetBox(self.controlArea, box=_tr.m[302, "Mode indicator"], orientation=form)
        form.addRow(_tr.m[303, "Feature:"], gui.comboBox(
            None, self, "variable", model=VariableListModel(),
            callback=self.indicator_changed))
        form.addRow(_tr.m[304, "Connect:"], gui.comboBox(
            None, self, "connect_value",
            callback=self.connect_combo_changed))
        form.addRow(_tr.m[305, "by:"], gui.comboBox(
            None, self, "connector_value",
            callback=self.connector_combo_changed))

        gui.comboBox(
            self.controlArea, self, "weighting", box=_tr.m[306, "Edge weights"],
            items=[x.name for x in twomode.Weighting],
            callback=self.update_output)

        self.lbout = gui.widgetLabel(gui.hBox(self.controlArea, _tr.m[307, "Output"]), "")
        self._update_combos()
        self._set_output_msg()

    @Inputs.network
    def set_network(self, network):
        self.closeContext()

        self.Warning.clear()
        self.Error.clear()
        if network is not None:
            if not isinstance(network.nodes, Table):
                network = None
                self.Error.no_data()

        self.network = network
        self._update_combos()
        if self.network is not None:
            self.openContext(network.nodes.domain)
        self.update_output()

    def indicator_changed(self):
        """Called on change of indicator variable"""
        self._update_value_combos()
        self.update_output()

    def connect_combo_changed(self):
        cb_connector = self.controls.connector_value
        if not cb_connector.isEnabled():
            self.connector_value = 2 - self.connect_value
        self.update_output()

    def connector_combo_changed(self):
        self.update_output()

    def _update_combos(self):
        """
        Update all three combos

        Set the combo for indicator variable and call the method to update
        combos for values"""
        model = self.controls.variable.model()
        if self.network is None:
            model.clear()
            self.variable = None
        else:
            domain = self.network.nodes.domain
            model[:] = [
                var for var in chain(domain.variables, domain.metas)
                if isinstance(var, DiscreteVariable) and len(var.values) >= 2]
            if not model.rowCount():
                self.Error.no_categorical()
                self.network = None
                self.variable = None
            else:
                self.variable = model[0]
        self._update_value_combos()

    def _update_value_combos(self):
        """Update combos for values"""
        cb_connect = self.controls.connect_value
        cb_connector = self.controls.connector_value
        variable = self.variable

        cb_connect.clear()
        cb_connector.clear()
        cb_connector.setDisabled(variable is None or len(variable.values) == 2)
        self.connect_value = 0
        self.connector_value = 0
        if variable is not None:
            cb_connect.addItems(variable.values)
            cb_connector.addItems([_tr.m[308, "(all others)"]] + list(variable.values))
            self.connector_value = len(variable.values) == 2 and 2

    def update_output(self):
        """Output the network on the output"""
        self.Warning.ignoring_missing.clear()
        self.Error.same_values.clear()
        new_net = None
        if self.network is not None:
            if self.connect_value == self.connector_value - 1:
                self.Error.same_values()
            else:
                mode_mask, conn_mask = self._mode_masks()
                new_net = twomode.to_single_mode(
                    self.network, mode_mask, conn_mask, self.weighting)

        self.Outputs.network.send(new_net)
        self._set_output_msg(new_net)

    def _mode_masks(self):
        """Return indices of nodes in the two modes"""
        data = self.network.nodes
        col_view = data.get_column(self.variable)
        column = col_view.astype(int)
        # Note: conversion required to handle empty (object) arrays
        missing_mask = np.isnan(col_view.astype(float))
        if np.any(missing_mask):
            column[missing_mask] = -1
            self.Warning.ignoring_missing()

        mode_mask = column == self.connect_value
        if self.connector_value:
            conn_mask = column == self.connector_value - 1
        else:
            conn_mask = np.logical_and(column != self.connect_value, np.logical_not(missing_mask))
        return mode_mask, conn_mask

    def _set_output_msg(self, out_network=None):
        if out_network is None:
            self.lbout.setText(_tr.m[309, "No network on output"])
        else:
            self.lbout.setText(
                (_tr.e(_tr.c(310, f"{out_network.number_of_nodes()} nodes, ")) + _tr.e(_tr.c(311, f"{out_network.number_of_edges()} edges"))))

    def send_report(self):
        if self.network:
            self.report_items("", [
                (_tr.m[312, 'Input network'],
                 _tr.m[313, "{} nodes, {} edges"].format(
                     self.network.number_of_nodes(),
                     self.network.number_of_edges())),
                (_tr.m[314, 'Mode'],
                 self.variable and bool(self.variable.values) and (
                     _tr.m[315, "Select {}={}, connected through {}"].format(
                         self.variable.name,
                         self.variable.values[self.connect_value],
                         _tr.m[316, "any node"] if not self.connector_value
                         else self.variable.values[self.connector_value - 1]
                     ))),
                (_tr.m[317, 'Weighting'],
                 bool(self.weighting)
                 and twomode.Weighting[self.weighting].name),
                (_tr.m[318, "Output network"], self.lbout.text())
            ])


def main():  # pragma: no cover
    import OWNxFile
    from AnyQt.QtWidgets import QApplication
    a = QApplication([])
    ow = OWNxSingleMode()
    ow.show()

    def set_network(data, id=None):
        ow.set_network(data)

    owFile = OWNxFile.OWNxFile()
    owFile.Outputs.network.send = set_network
    owFile.open_net_file("/Users/janez/Downloads/100_petrozavodsk_171_events_no_sqrt.net")
    ow.handleNewSignals()
    a.exec_()
    ow.saveSettings()
    owFile.saveSettings()


if __name__ == "__main__":  # pragma: no cover
    main()
