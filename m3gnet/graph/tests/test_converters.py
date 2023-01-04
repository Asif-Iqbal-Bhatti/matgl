import os
import unittest

import numpy as np
from pymatgen.core import Lattice, Molecule, Structure
from pymatgen.util.testing import PymatgenTest

from m3gnet.graph.converters import Pmg2Graph, get_element_list

module_dir = os.path.dirname(os.path.abspath(__file__))


class Pmg2GraphTest(PymatgenTest):
    def test_get_graph_from_molecule(self):
        coords = [
            [0.000000, 0.000000, 0.000000],
            [0.000000, 0.000000, 1.089000],
            [1.026719, 0.000000, -0.363000],
            [-0.513360, -0.889165, -0.363000],
            [-0.513360, 0.889165, -0.363000],
        ]
        methane = Molecule(["C", "H", "H", "H", "H"], coords)
        element_types = get_element_list([methane])
        p2g = Pmg2Graph(element_types=element_types, cutoff=1.5)
        graph, state = p2g.get_graph_from_molecule(methane)
        # check the number of nodes
        self.assertTrue(np.allclose(graph.num_nodes(), 5))
        # check the number of edges
        self.assertTrue(np.allclose(graph.num_edges(), 8))
        # check the src_ids
        self.assertTrue(np.allclose(graph.edges()[0].numpy(), [0, 0, 0, 0, 1, 2, 3, 4]))
        # check the dst_ids
        self.assertTrue(np.allclose(graph.edges()[1].numpy(), [1, 2, 3, 4, 0, 0, 0, 0]))
        # check the atomic features of atom C
        self.assertTrue(np.allclose(graph.ndata["attr"][0], [0, 1]))
        # check the atomic features of atom H
        self.assertTrue(np.allclose(graph.ndata["attr"][1], [1, 0]))
        # check the shape of state features
        self.assertTrue(np.allclose(len(state), 2))
        # check the value of state features
        self.assertTrue(np.allclose(state, [3.208492, 0.8]))
        # check the position of atom 0
        self.assertTrue(np.allclose(graph.ndata["pos"][0], [0.000000, 0.000000, 0.000000]))
        # check the position vector from atom 0 to atom 1
        self.assertTrue(np.allclose(graph.edata["bond_vec"][0], [0.000000, 0.000000, 1.0890]))

    def test_get_graph_from_structure(self):
        structure_LiFePO4 = self.get_structure("LiFePO4")
        element_types = get_element_list([structure_LiFePO4])
        p2g = Pmg2Graph(element_types=element_types, cutoff=4.0)
        graph, state = p2g.get_graph_from_structure(structure_LiFePO4)
        # check the number of nodes
        self.assertTrue(np.allclose(graph.num_nodes(), structure_LiFePO4.num_sites))
        # check the atomic feature of atom 0
        self.assertTrue(np.allclose(graph.ndata["attr"][0].numpy(), [1, 0, 0, 0]))
        # check the atomic feature of atom 4
        self.assertTrue(np.allclose(graph.ndata["attr"][4].numpy(), [0, 0, 0, 1]))
        # check the number of bonds
        self.assertTrue(np.allclose(graph.num_edges(), 704))
        # check the state features
        self.assertTrue(np.allclose(state, [0.0, 0.0]))
        structure_BaTiO3 = Structure.from_prototype("perovskite", ["Ba", "Ti", "O"], a=4.04)
        element_types = get_element_list([structure_BaTiO3])
        p2g = Pmg2Graph(element_types=element_types, cutoff=4.0)
        graph, state = p2g.get_graph_from_structure(structure_BaTiO3)
        # check the number of nodes
        self.assertTrue(np.allclose(graph.num_nodes(), structure_BaTiO3.num_sites))
        # check the atomic features of atom 0
        self.assertTrue(np.allclose(graph.ndata["attr"][0], [0, 0, 1]))
        # check the atomic features of atom 1
        self.assertTrue(np.allclose(graph.ndata["attr"][1], [0, 1, 0]))
        # check the number of edges
        self.assertTrue(np.allclose(graph.num_edges(), 76))
        # check the state features
        self.assertTrue(np.allclose(state, [0.0, 0.0]))
        # check the position of atom 0
        self.assertTrue(np.allclose(graph.ndata["pos"][0], [0.0, 0.0, 0.0]))
        # check the bond vector from node 0 to image atom 6
        self.assertTrue(np.allclose(graph.edata["bond_vec"][0], [-2.0200, -2.0200, -2.0200]))
        # check the pbc offset from node 0 to image atom 6
        self.assertTrue(np.allclose(graph.edata["pbc_offset"][0], [-1, -1, -1]))
        # cheeck the lattice vector
        self.assertTrue(np.allclose(graph.ndata["lattice"][0], [[4.04, 0.0, 0.0], [0.0, 4.04, 0.0], [0.0, 0.0, 4.04]]))
        # check the volume
        self.assertTrue(np.allclose(graph.ndata["volume"][0], [65.939264]))

    def test_get_element_list(self):
        cscl = Structure.from_spacegroup("Pm-3m", Lattice.cubic(3), ["Cs", "Cl"], [[0, 0, 0], [0.5, 0.5, 0.5]])
        naf = Structure.from_spacegroup("Pm-3m", Lattice.cubic(3), ["Na", "F"], [[0, 0, 0], [0.5, 0.5, 0.5]])
        elem_list = get_element_list([cscl, naf])
        self.assertEqual(elem_list, ("F", "Na", "Cl", "Cs"))


if __name__ == "__main__":
    unittest.main()
