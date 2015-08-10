# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2015, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------


SWARM_CONFIG = {
  "includedFields": [
    {
      "fieldName": "timestamp",
      "fieldType": "datetime"
    },
    {
      "fieldName": "kw_energy_consumption",
      "fieldType": "float",
      "maxValue": 53.0,
      "minValue": 0.0
    }
  ],
  "streamDef": {
    "info": "kw_energy_consumption",
    "version": 1,
    "streams": [
      {
        "info": "Rec Center",
        "source": "file://data/rec-center-hourly.csv",
        "columns": [
          "*"
        ]
      }
    ],
  },

  "inferenceType": "TemporalMultiStep",
  "inferenceArgs": {
    "predictionSteps": [
      1
    ],
    "predictedField": "kw_energy_consumption"
  },
  "iterationCount": -1,
  "swarmSize": "medium"
}