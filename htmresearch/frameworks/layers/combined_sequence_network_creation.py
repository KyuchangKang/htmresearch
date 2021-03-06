# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2016, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------
"""
The methods here contain a factory to create a network that handles both
temporal sequences as well as sensorimotor sequences.  It contains our
normal L2L4 network with an additional layer that contains a sequence
memory.

The network type supported is called "L4L2TMColumn". It is a single cortical
column containing and L4 and an L2 layer plus a TM layer. L4 gets two inputs and
feeds into L2. The L2 column feeds back to L4. TM gets the sensorInput.


                     L2Column   <-----------------+
                       ^  +                       |
                       |  |                       |
                       +  v                       |
     +------------->  L4Column  <-----------------+
     |                   ^                        |
     |                   |                        |
     |                   |        TMColumn <------+
     |                   |           ^            |
     +                   +           |            +
externalInput        sensorInput +---+          reset


Regions will be named as shown above plus a suffix indicating column number,
such as "externalInput_0", "L2Column_3", etc. The reset signal (from
sensorInput) is sent to all the other regions.

"""
import copy
import json
import numpy

from htmresearch.frameworks.layers.l2_l4_network_creation import enableProfiling

def createL4L2TMColumn(network, networkConfig, suffix=""):
  """
  Create a a single column containing one L4, one L2, and one TM.

  networkConfig is a dict that must contain the following keys (additional keys
  ok):

    {
      "externalInputSize": 1024,
      "sensorInputSize": 1024,
      "L4Params": {
        <constructor parameters for ApicalTMPairRegion>
      },
      "L2Params": {
        <constructor parameters for ColumnPoolerRegion>
      },
      "TMParams": {
        <constructor parameters for ApicalTMSequenceRegion>
      },
    }

  Region names are externalInput, sensorInput, L4Column, L2Column, and TMColumn.
  Each name has an optional string suffix appended to it.
  """

  externalInputName = "externalInput" + suffix
  sensorInputName = "sensorInput" + suffix
  L4ColumnName = "L4Column" + suffix
  L2ColumnName = "L2Column" + suffix
  TMColumnName = "TMColumn" + suffix

  L4Params = copy.deepcopy(networkConfig["L4Params"])
  L4Params["basalInputWidth"] = networkConfig["externalInputSize"]
  L4Params["apicalInputWidth"] = networkConfig["L2Params"]["cellCount"]

  if networkConfig["externalInputSize"] > 0:
      network.addRegion(
        externalInputName, "py.RawSensor",
        json.dumps({"outputWidth": networkConfig["externalInputSize"]}))
  network.addRegion(
    sensorInputName, "py.RawSensor",
    json.dumps({"outputWidth": networkConfig["sensorInputSize"]}))

  network.addRegion(L4ColumnName, "py.ApicalTMPairRegion", json.dumps(L4Params))
  network.addRegion(TMColumnName,
                    "py.ApicalTMSequenceRegion",
                    json.dumps(networkConfig["TMParams"]))
  network.addRegion(L2ColumnName,
                    "py.ColumnPoolerRegion",
                    json.dumps(networkConfig["L2Params"]))

  # Set phases appropriately so regions are executed in the proper sequence
  # This is required for multiple columns - the order of execution is not the
  # same as the order of region creation.
  if networkConfig["externalInputSize"] > 0:
      network.setPhases(externalInputName,[0])
  network.setPhases(sensorInputName,[0])

  # L4 and L2 regions always have phases 2 and 3, respectively
  # TM region has same phase as L4 since they do not interconnect
  network.setPhases(L4ColumnName,[2])
  network.setPhases(TMColumnName,[2])
  network.setPhases(L2ColumnName,[3])

  # Link sensors to L4
  network.link(externalInputName, L4ColumnName, "UniformLink", "",
               srcOutput="dataOut", destInput="basalInput")
  network.link(externalInputName, L4ColumnName, "UniformLink", "",
               srcOutput="dataOut", destInput="basalGrowthCandidates")
  network.link(sensorInputName, L4ColumnName, "UniformLink", "",
               srcOutput="dataOut", destInput="activeColumns")

  # Link main inputs to TM
  network.link(sensorInputName, TMColumnName, "UniformLink", "",
               srcOutput="dataOut", destInput="activeColumns")

  # Link L4 to L2
  network.link(L4ColumnName, L2ColumnName, "UniformLink", "",
               srcOutput="activeCells", destInput="feedforwardInput")
  network.link(L4ColumnName, L2ColumnName, "UniformLink", "",
               srcOutput="predictedActiveCells",
               destInput="feedforwardGrowthCandidates")

  # Link L2 feedback to L4
  network.link(L2ColumnName, L4ColumnName, "UniformLink", "",
               srcOutput="feedForwardOutput", destInput="apicalInput",
               propagationDelay=1)

  # Link reset output to L2, TM, and L4
  network.link(sensorInputName, L2ColumnName, "UniformLink", "",
               srcOutput="resetOut", destInput="resetIn")
  network.link(sensorInputName, TMColumnName, "UniformLink", "",
               srcOutput="resetOut", destInput="resetIn")
  network.link(sensorInputName, L4ColumnName, "UniformLink", "",
               srcOutput="resetOut", destInput="resetIn")

  enableProfiling(network)

  return network
