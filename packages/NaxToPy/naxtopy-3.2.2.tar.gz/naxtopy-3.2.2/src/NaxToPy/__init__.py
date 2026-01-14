import h5py  # Ensure h5py is loaded first to avoid issues with other libraries
from NaxToPy.Core.Errors.N2PLog import N2PLog
from NaxToPy.Core.N2PModelContent import initialize, load_model, OpenFiletoN2P
from NaxToPy.Modules.envelope.N2PEnvelope import envelope_list, envelope_ndarray
from NaxToPy.Core.Constants.Constants import VERSION
from NaxToPy.Core.Classes import AllClasses
from NaxToPy.Modules.n2ptoexe.N2PtoEXE import n2ptoexe


__all__ = ['N2PLog', 'initialize', 'load_model', 'OpenFiletoN2P', 'n2ptoexe', 'envelope_list', 'envelope_ndarray', 'VERSION', 'AllClasses']

__version__ = VERSION

import sys

# Warn that python 3.9 support will be dropped in future releases
if sys.version_info[:2] == (3, 9):
    N2PLog.Warning.W108()