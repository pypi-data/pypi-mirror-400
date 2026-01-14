from NaxToModel import N2ModelContent
from NaxToModel import N2LoadCase
from NaxToModel.Classes import N2AdjacencyFunctions
from NaxToModel.Classes import N2FreeEdges
from NaxToModel import EnvelopGroup
from NaxToModel import EnvelopCriteria
from NaxToModel import N2ArithmeticSolver
from NaxToModel import N2Enums
from NaxToModel import N2CoordUserDefined, N2Coord
from NaxToModel.Classes import N2SelectionFunctions

from System.Runtime.CompilerServices import RuntimeHelpers
import System

from NaxToPy.Core.Errors.N2PLog import N2PLog
from NaxToPy.Core.Classes.N2PLoadCase import N2PLoadCase
from NaxToPy.Core.Classes.N2PIncrement import N2PIncrement
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core.Classes.N2PNode import N2PNode
from NaxToPy.Core.Classes.N2PCoord import N2PCoord
from NaxToPy.Core.Classes.N2PConnector import N2PConnector
from NaxToPy.Core.Classes.N2PFreeBody import N2PFreeBody
from NaxToPy.Core.Classes.N2PMaterial import N2PMaterial, N2PMatE, N2PMatMisc, N2PMatI
from NaxToPy.Core.Classes.N2PProperty import N2PProperty, N2PComp, N2PShell, N2PSolid, N2PBeam, N2PRod, N2PBush, N2PFast, N2PMass, N2PElas, N2PGap, N2PWeld, N2PBeamL, N2PPropMisc
from NaxToPy.Core.Classes.N2PSet import N2PSet
from NaxToPy.Core.Classes.N2PNastranInputData import N2PNastranInputData, CONSTRUCTDICT, N2PCard
from NaxToPy.Core.Constants.Constants import BINARY_EXTENSIONS
from NaxToPy.Core.Classes.N2PReport import N2PReport
from NaxToPy.Core.Classes.N2PAbaqusInputData import N2PAbaqusInputData
from NaxToPy.Core._AuxFunc._NetToPython import _numpytonet

import time
import numpy as np
import os
import array
from collections import OrderedDict
from typing import Union, overload, Literal


# Clase Model Content de Python ----------------------------------------------------------------------------------------
class N2PModelContent:
    """Main Class of the NaxToPy package. Keeps almost all the information contained in the output result.

    The method that returns a :class:`N2PModelContent` is :meth:`load_model()`

    Example:
        >>> model1 = n2p.load_model(r"my_model1.op2")
        >>> solver = model1.Solver  # Property of N2PModelContent
        >>> nodes = model1.get_nodes()  # Method of N2PModelContent

        >>> model2 = n2p.load_model(r"my_model2.h5")
        >>> solver2 = model2.Solver  # Property of N2PModelContent
        >>> nodes2 = model2.get_nodes()  # Method of N2PModelContent

    """
    ####################################################################################################################
    # region INIT
    ####################################################################################################################
    def __init__(self, path, parallelprocessing, solver=None, dict_gen: dict = None, filter: Literal['ELEMENTS', 'PROPERTIES', 'PARTS', 'NODES'] = None,
                 n2v: N2ModelContent = None, loadconnectors = True):
        """ Python ModelContent Constructor.

            Args:
                path: str
                parallelprocessing: bool
        """
        # 0 ) Genera el archivo .log y añade los logs de la importación ------------------------------------------------
        # Configura el logger para que escriba automaticamente los logs ------------------------------------------------
        if not N2PLog._N2PLog__fh.immediate:
            N2PLog._N2PLog__fh.write_buffered_records()
            N2PLog._N2PLog__fh.immediate_logging()

        # 1) Extraer Toda la Informacion Principal de NaxTo ------------------------------------------------------------
        # Inicializador de atributos
        self.__LCs_by_ID__: dict[int: N2PLoadCase] = dict()
        self.__LCs_by_Name__: dict[str: N2PLoadCase] = dict()
        self.__load_cases__ = None

        self.__setlist = None

        self.__number_of_load_cases = None
        self.__material_dict = dict()
        self.__property_dict: dict[tuple[int, int]] = dict()
        self.__elements_coord_sys = None
        self.__material_coord_sys = None
        self.__cells_list = None  # Lista con N2PElement y N2PConnector
        self.__connectivity_dict = {}
        self.__element_user_coord_systems = []
        self.__node_user_coord_systems = []

        self.__elementnodal_dict = None
        self.__elemIdInternalToId = dict()

        # Inicializador del modelo
        if n2v:
            self.__vzmodel = n2v
            self.__solver = self.__vzmodel.Solver.ToString()
        else:
            self.__vzmodel = N2ModelContent()

            if not solver:
                if _is_binary(path):
                    self.__vzmodel.Solver = self.__vzmodel.Solver.Unknown

                else:
                    solver = _check_file_extension(path)

            if solver == 'InputFileNastran':
                self.__vzmodel.Solver = self.__vzmodel.Solver.InputFileNastran

            elif solver == "InputFileOptistruct":
                N2PLog.Warning.user("Input files from Optistruct are not fully supported yet. They are loaded as Nastran input files.")
                self.__vzmodel.Solver = self.__vzmodel.Solver.InputFileNastran

            elif solver == 'InputFileAbaqus':
                self.__vzmodel.Solver = self.__vzmodel.Solver.InputFileAbaqus

            elif solver == "Binary":
                self.__vzmodel.Solver = self.__vzmodel.Solver.Unknown

            error = self.__vzmodel.Initialize(path, self.__vzmodel.Solver)

            # Si NaxTo devuelve un numero por debajo de 0 en el inicializador del modelo -> Error al inicializar modelo
            if error < 0:
                if not os.path.exists(path):
                    msg = N2PLog.Critical.C108(path)
                    raise FileNotFoundError(msg)
                else:
                    msg = N2PLog.Critical.C100(path, error)
                    raise RuntimeError(msg)
            else:
                N2PLog.Info.I111(path)

            # Activar banderas de NaxToPy en dll de Naxto
            # Es imprescindible hacer esta llamada para que se carguen los datos necesarios para que
            # el modulo funcione
            self.__vzmodel.Program_Call = self.__vzmodel.Program_Call.NaxToPy

            N2PLog.Debug.D102()

            # Opcion que indica que la lectura de la malla dentro de vizzer se haga en paralelo
            self.__vzmodel.LoadModelInParallel = parallelprocessing  # No siempre es mas rapido

            N2PLog.Debug.D103(parallelprocessing)

            # Option that sets if the connectors should be loaded or not
            self.__vzmodel.LoadConnectorsOption = loadconnectors
            N2PLog.Debug.D104(loadconnectors)

            error = self.__vzmodel.BuildMesh(filter, dict_gen)
            # Si NaxTo devuelve un numero por debajo de 0 en el generador de malla -> Error al generar malla
            if error == -1003:
                msg = N2PLog.Critical.C112()
                raise RuntimeError(msg)
            elif error < 0:
                msg = N2PLog.Critical.C101(error)
                raise RuntimeError(msg)
            else:
                N2PLog.Info.I112()

            self.__solver = self.__vzmodel.Solver.ToString()
            # Generar Informacion Disponible (LCs, Result-Types ...)
            if self.__solver != "InputFileNastran" and self.__solver != "InputFileAbaqus":
                t1 = time.time()
                # Wait for all the process that load the mesh (resultsinfo and setinfo go in the secondary task)
                self.__vzmodel.WaitSecondaryParallelTask()
                # The load cases and all the results tree is loaded here
                self.__vzmodel.LoadInfoResults()
                t2 = time.time()
                N2PLog.Debug.D100("LoadInfoResults()", t2 - t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        ###########################################    N2PLoadCase    ##################################################
        ################################################################################################################
        # 2) Obtener los casos de carga del modelo ---------------------------------------------------------------------
        t1 = time.time()

        self._import_load_cases()

        t2 = time.time()
        N2PLog.Debug.D100("LoadCases", t2 - t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        ##########################################    GENERAL DICTS     ################################################
        ################################################################################################################
        # Diccionarios obtenidos directamente de Vizzer ---------------
        t1 = time.time()

        self.__elementTypeStrtoID = dict(self.__vzmodel.elementTypeID)
        self.__propertiesID = dict(self.__vzmodel.propertiesID)
        self.__StrPartToID = dict(self.__vzmodel.partID)
        self.__materialsID = None
        self.__ConnectorsID = dict(self.__vzmodel.ConnectorsID)
        # --------------------------------------------------------------------------------------------------------------

        # Diccionario de en el que entras con un ID de elemento dado por Vizzer y sacas
        # un string con el tipo de elemento de solver
        self.__elementTypeIDtoStr = {v: k for k, v in self.__elementTypeStrtoID.items()}

        # Diccionario en el que entras con el ID de la parte y te devuelve el nombre.
        self.__partIDtoStr = {v: k for k, v in self.__StrPartToID.items()}

        # Diccionario en el que entras con un Id de propiedad y te devuelve el string.
        self.__propertyIDtoStr = {v: k for k, v in self.__propertiesID.items()}

        # Diccionario en el que entras con un Id de tipo de conector y te devuelve un string con su nombre.
        self.__connectorTypeIDtoStr = {v: k for k, v in self.__ConnectorsID.items()}

        # Diccionario de en el que entras con un material y devuelve una lista de propiedades en las que está incluido
        # Al ser una lista no vale el metodo dict() tal cual. Hay que sacar sus claves y valores y construirlo nosotros
        aux = dict(self.__vzmodel.DictMaterialsProperties)
        self.__DictMaterialsProperties = {key: list(aux[key]) for key in aux}
        del aux
        # --------------------------------------------------------------------------------------------------------------

        # Diccionario de en el que entras con una propiedad y devuelve una lista de materiales que tiene incluido
        # Se construye igual que el diccionario anterior
        aux = dict(self.__vzmodel.DictPropertiesMaterials)
        self.__DictPropertiesMaterials = {key: list(aux[key]) for key in aux}
        del aux

        t2 = time.time()
        N2PLog.Debug.D100("Direct Dictionaries", t2 - t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        #############################################    N2PCoord    ###################################################
        ################################################################################################################
        t1 = time.time()

        # Revisar porque es posible los sistemas de coordenadas nunca tengan partes
        self.__coord_dict = {((coord.ID, coord.PartID) if hasattr(coord, 'PartID') else (coord.ID, 0)):
                                 N2PCoord(coord, self) for coord in self.__vzmodel.coordList.Values}

        t2 = time.time()
        N2PLog.Debug.D100("N2PCoord Dictionary", t2 - t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        #############################################    N2PNode     ###################################################
        ################################################################################################################
        t1 = time.time()

        def __n2pnode_func(listadenodos):
            node_dict = OrderedDict(((nodo.ID, nodo.PartID), N2PNode(nodo, self)) for nodo in listadenodos)
            return node_dict

        self.__node_dict = __n2pnode_func(self.__vzmodel.N2PNodeList)

        t2 = time.time()
        N2PLog.Debug.D100("N2PNode Dictionary", t2 - t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        ############################################    N2PElement     #################################################
        ################################################################################################################
        t1 = time.time()

        def __n2pelement_func(listadeelementos):
            elem_dict = OrderedDict(((elem.ID, elem.partID), N2PElement(elem, self)) for elem in listadeelementos)
            return elem_dict

        self.__element_dict = __n2pelement_func(self.__vzmodel.N2PElementList)
        self.__cells_list = list(self.__element_dict.values())

        t2 = time.time()
        N2PLog.Debug.D100("N2PElement Dictionary", t2 - t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        ###########################################    N2PConnector     ################################################
        ################################################################################################################
        t1 = time.time()

        # Flag to print once the W203
        mpc_warning = False

        self.__connector_dict = OrderedDict()
        for con in self.__vzmodel.connectorList:
            if not (con.ID, con.Part) in self.__connector_dict:
                self.__connector_dict[(con.ID, con.Part)] = N2PConnector(con, self)
            elif isinstance(self.__connector_dict.get((con.ID, con.Part)), list):
                self.__connector_dict[(con.ID, con.Part)].append(N2PConnector(con, self))
            else:
                self.__connector_dict[(con.ID, con.Part)] = \
                    [self.__connector_dict.get((con.ID, con.Part)), (N2PConnector(con, self))]
                
                if not mpc_warning:
                    N2PLog.Warning.W203()
                    mpc_warning = True

        del mpc_warning

        # OJO. EN NASTRAN SE PUEDEN TENER VARIOS MPC CON EL MISMO ID, POR TANTO SE GUARDARAN COMO UNA LISTA DE
        # N2PConnectors
        self.__cells_list += [conn for conn_list in self.__connector_dict.values()
                              for conn in (conn_list if isinstance(conn_list, list) else [conn_list])]
        t2 = time.time()
        N2PLog.Debug.D100("N2PConnector Dictionary", t2 - t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        ########################################    N2PModelInputData     ##############################################
        ################################################################################################################
        t1 = time.time()
        if self.__vzmodel.NasOptInputReader is not None:
            class LazyDict(dict):
                """This class keeps the N2Card as C# instances crated in the reader. Only when they are asked by key,
                the card asked is cast to the proper N2PCard before the value returning"""

                def __init__(self, keys_list: list):
                    super().__init__()
                    self._hash_to_cs = dict()
                    self._collision_counter = {}  # Track collision index per hash
                    
                    for cs_ref in keys_list:
                        if cs_ref.GetN2PCardType() not in CONSTRUCTDICT:
                            continue
                        
                        hash = RuntimeHelpers.GetHashCode(cs_ref)
                        
                        # Create unique key for collisions
                        if hash in self._collision_counter:
                            self._collision_counter[hash] += 1
                            unique_key = (hash, self._collision_counter[hash])
                        else:
                            self._collision_counter[hash] = 0
                            unique_key = (hash, 0)
                        
                        self[unique_key] = None
                        self._hash_to_cs[unique_key] = cs_ref

                def __getitem__(self, key):
                    # Handle both (hash, index) and plain hash lookups
                    if isinstance(key, tuple):
                        hash, index = key
                    else:
                        hash = key
                        index = 0
                        key = (hash, 0)
                    
                    if key not in self or self.get(key) is None:
                        cs_ref = self._hash_to_cs.get(key)
                        
                        if not cs_ref:
                            return None
                        
                        value = CONSTRUCTDICT.get(cs_ref.GetN2PCardType())
                        if value:
                            constructed = value(cs_ref)
                            self[key] = constructed
                            return constructed
                        return None
                    else:
                        return self.get(key)

            cslistbulkdatacards = self.__vzmodel.NasOptInputReader.BulkDataSection.GetCardDataBaseList()
            self.__modelinputdata = N2PNastranInputData(
                LazyDict(cslistbulkdatacards),
                self.__vzmodel.NasOptInputReader
            )
            self.__vzmodel.NasOptInputReader.OperationLogger.Clear() #Necessary so that logs from reading the input file are not saved until the library is fully optimized.
            self.__vzmodel.NasOptInputReader.SetLoggingConfigurationErrors()
        elif self.__vzmodel.AbaqusInfoInputFileData is not None:
            self.__modelinputdata = N2PAbaqusInputData(self.__vzmodel.AbaqusInfoInputFileData)
        else:
            self.__modelinputdata = None
        t2 = time.time() - t1
        N2PLog.Debug.D100("N2PModelInputData", t2)
        # --------------------------------------------------------------------------------------------------------------
    # endregion

    ####################################################################################################################
    # region PROPERTIES
    ####################################################################################################################
    # Metodo para Obtener la Ruta del Modelo ---------------------------------------------------------------------------
    @property
    def FilePath(self) -> str:
        """Path (may be relative or absolute) file where the model was read from."""
        return (str(self.__vzmodel.FilePath))

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para Obtener el Solver del Modelo -------------------------------------------------------------------------
    @property
    def Solver(self) -> str:
        """Solver of the model"""
        return self.__solver

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para Obtener la Version de Abaqus del Modelo --------------------------------------------------------------
    @property
    def AbaqusVersion(self) -> str:
        """ Returns the Abaqus version used in the output result file if the solver is Abaqus
        """
        if (self.__solver == 'Abaqus'):
            return (str(self.__vzmodel.version_abqs_model.ToString()))
        else:
            return None

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el numero de casos de carga en el modelo -----------------------------------------------------
    @property
    def LoadCases(self) -> list[N2PLoadCase]:
        """ Returns a list with all the of N2PLoadCase
        """
        return self.__load_cases__

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el numero de casos de carga en el modelo -----------------------------------------------------
    @property
    def NumberLoadCases(self) -> int:
        """Number of load cases of the model"""
        if self.__number_of_load_cases is None:
            self.__number_of_load_cases = int(self.__vzmodel.LoadCases.Count)
            return int(self.__vzmodel.LoadCases.Count)
        else:
            return int(self.__number_of_load_cases)

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Parts(self) -> list[str]:
        """Returns the list of parts/superelements of the model"""
        return list(self.__partIDtoStr.values())

    @property
    def ElementsDict(self) -> OrderedDict[tuple[int, int], N2PElement]:
        """Returns a dictionary with the :class:`N2PElement` of the model as values. The key is the tuple (id, partid)"""
        return self.__element_dict

    @property
    def NodesDict(self) -> OrderedDict[tuple[int, int], N2PNode]:
        """Returns a dictionary with the :class:`N2PNode` of the model as values. The key is the tuple (id, partid)"""
        return self.__node_dict

    @property
    def ConnectorsDict(self) -> OrderedDict[tuple[int, int], N2PConnector]:
        """Returns a dictionary with the :class:`N2PConnector` of the model as values. The key is the tuple (id, partid)"""
        return self.__connector_dict

    @property
    def SetList(self) -> list[N2PSet]:
        """Returns a list of :class:`N2PSet` kept in the model. It works for Abaqus, Optitruct (*.h3d), Nastran (*.op2, *.h5)
        
        Note:
            The sets in *.op2 Nastran are not saved by default. To keep this information the command `PARAM, POSTEXT, YES` must
            be used in the Bulk Data Section before running the solution.
        
        Warning:
            The type of sets it is not usually saved, so the IDs could be for Nodes or Elements. The user must know if the set was
            defined for Elements or Nodes.
        """
        if not self.__setlist:
            self.__setlist = [N2PSet(_) for _ in list(self.__vzmodel.SetList)]
        return self.__setlist

    @property
    def ModelInputData(self) -> Union[N2PNastranInputData, N2PAbaqusInputData]:
        """Returns a :class:`N2PNastranInputData` or a :class:`N2PAbaqusInputData` with the information of the input data file"""
        if self.__modelinputdata is None:
            N2PLog.Warning.W204()
        return self.__modelinputdata

    ####################################################################################################################
    ###########################################    N2PMaterial     #####################################################
    ####################################################################################################################
    @property
    def MaterialDict(self) -> dict[tuple[Union[int,str], str], N2PMaterial]:
        """
        Dictionary of materials. Key is a tuple that is ID (a int for Nastran/Optistruct or str for Abaqus) and the part (str),
        and value is a :class:`N2PMaterial`
        
        It is not initialized at first, only when it is needed.

        Returns:
            dict[(ID, Part)] = N2PMaterial

        Example:
            >>> # For nastran the first item of the tuple is a int
            >>> nastran_model = n2p.load_model(r".\\nastran.op2")
            >>> my_mat_10 = model.MaterialDict[(10, "0")]
            >>> prop = model.PropertyDict(1000)
            >>> my_mat = model.MaterialDict[(prop.MatID, prop.Part)]

            >>> # For abaqus the first item of the tuple is a str
            >>> abaqus_model = n2p.load_model("abaqus.odb")
            >>> my_mat_Al = model.MaterialDict[("ALUMINIUM", "0")]
            >>> prop = model.PropertyDict(1000)
            >>> my_mat = model.MaterialDict[(prop.MatID, prop.Part)]
        """

        t1 = time.time()

        if not self.__material_dict:

            dictmateriales = dict(self.__vzmodel.N2MatDict)
            if self.Solver == "Abaqus" or self.Solver == "InputFileAbaqus":
                # For Abaqus, the materials are stored as a dict with str keys
                self.__materialsID = list(self.__vzmodel.DictMatToStr)

            for key, value in dictmateriales.items():
                if self.Solver == "Nastran" or self.Solver == "H3DOptistruct" or self.Solver == "InputFileNastran" or self.Solver == "InputFileH3DOptistruct":
                    key = (int(key.Item1), str(key.Item2))
                else:
                    key = (str(key.Item1), str(key.Item2))

                if value.GetType().ToString() == 'NaxToModel.N2MatE':
                    self.__material_dict[key] = N2PMatE(value, self)
                elif value.GetType().ToString() == 'NaxToModel.N2MatI':
                    self.__material_dict[key] = N2PMatI(value, self)
                elif value.GetType().ToString() == 'NaxToModel.N2MatMisc':
                    self.__material_dict[key] = N2PMatMisc(value, self)

        t2 = time.time()
        N2PLog.Debug.D100("N2PMaterial Dictionary", t2 - t1)
        
        return self.__material_dict

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ###########################################    N2PProperty     #####################################################
    ####################################################################################################################
    @property
    def PropertyDict(self) -> dict[int, N2PProperty]:
        """
        Dictionary of properties. Key is a tuple that is ID (a int for Nastran/Optistruct or str for Abaqus) and the part (str),
        and value is a :class:`N2PProperty`
        
        It is not initialized at first, only when it is needed.

        Returns:
            dict[(ID, Part)] = N2PProperty

        Example:
            >>> # For nastran the first item of the tuple is a int
            >>> nastran_model = n2p.load_model(r".\\nastran.op2")
            >>> my_prop_20 = model.PropertyDict[(20, "0")]
            >>> my_prop = model.PropertyDict[(ele.Prop, prop.Part)]

            >>> # For abaqus the first item of the tuple is a str
            >>> abaqus_model = n2p.load_model("abaqus.odb")
            >>> my_prop_shell = model.PropertyDict[("SHELL", "0")]
            >>> my_prop = model.PropertyDict[(ele.Prop, prop.Part)]
        """

        t1 = time.time()

        if not self.__property_dict:

            dictprop = dict(self.__vzmodel.N2PropDict)

            for key, value in dictprop.items():

                if self.Solver == "Nastran" or self.Solver == "H3DOptistruct" or self.Solver == "InputFileNastran" or self.Solver == "InputFileH3DOptistruct":
                    key = (int(key.Item1), str(key.Item2))
                    if key[0] < 0:
                        N2PLog.Error.E227(key)
                else:
                    key = (str(key.Item1), str(key.Item2))

                if value.GetType().ToString() == 'NaxToModel.N2Shell':
                    self.__property_dict[key] = N2PShell(value, self)

                elif value.GetType().ToString() == 'NaxToModel.N2Comp':
                    self.__property_dict[key] = N2PComp(value, self)

                elif value.GetType().ToString() == 'NaxToModel.N2Solid':
                    self.__property_dict[key] = N2PSolid(value, self)

                elif value.GetType().ToString() == 'NaxToModel.N2Beam':
                    self.__property_dict[key] = N2PBeam(value, self)

                elif value.GetType().ToString() == 'NaxToModel.N2Rod':
                    self.__property_dict[key] = N2PRod(value, self)

                elif value.GetType().ToString() == 'NaxToModel.N2Bush':
                    self.__property_dict[key] = N2PBush(value, self)

                elif value.GetType().ToString() == 'NaxToModel.N2Fast':
                    self.__property_dict[key] = N2PFast(value, self)
                
                elif value.GetType().ToString() == 'NaxToModel.N2Mass':
                    self.__property_dict[key] = N2PMass(value, self)

                elif value.GetType().ToString() == 'NaxToModel.N2Elas':
                    self.__property_dict[key] = N2PElas(value, self)
                
                elif value.GetType().ToString() == 'NaxToModel.N2Gap':
                    self.__property_dict[key] = N2PGap(value, self)

                elif value.GetType().ToString() == 'NaxToModel.N2Weld':
                    self.__property_dict[key] = N2PWeld(value, self)

                elif value.GetType().ToString() == 'NaxToModel.N2BeamL':
                    self.__property_dict[key] = N2PBeamL(value, self)
                elif value.GetType().ToString() == 'NaxToModel.N2PropMisc':
                    self.__property_dict[key] = N2PPropMisc(value, self)

        t2 = time.time()
        N2PLog.Debug.D100("N2PProperty Dictionary", t2 - t1)
        return self.__property_dict
    # endregion

    ####################################################################################################################
    # region METHODS
    ####################################################################################################################

    # Metodo para obtener los casos de carga del modelo ----------------------------------------------------------------
    @overload
    def get_load_case(self, id: int) -> Union[N2PLoadCase, None]: ...
    @overload
    def get_load_case(self, name: str) -> Union[N2PLoadCase, None]: ...
    @overload
    def get_load_case(self, id: list[int]) -> Union[list[N2PLoadCase], None]: ...
    @overload
    def get_load_case(self, name: list[str]) -> Union[list[N2PLoadCase], None]: ...

    # Actual implementation
    def get_load_case(self,
                      id: Union[int, None] = None,
                      name: Union[str, None] = None) -> Union[list[N2PLoadCase], N2PLoadCase, None]:
        """Returns a list of :class:`N2PLoadCase` objects with all the load cases contained in the output result file.

        Args:
            id (int|list[int], optional): ID of the load case. Defaults to None.
            name (str|list[int], optional): Name of the load case. Defaults to None.

        Returns:
                N2PLoadCase: a load case
                list[N2PLoadCase]: load cases list

        Example:
            >>> a_loadcase = model.get_load_case(10)
            >>> a_loadcase = model.get_load_case("Mechanical")

            >>> some_loadcases = model.get_load_case([10, 20])
            >>> some_loadcases = model.get_load_case(["Mechanical", "Thermal"])
        """
        # Check if the input ID is a string or a list of strings
        if isinstance(id, str) or (isinstance(id, list) and all(isinstance(item, str) for item in id)):
            name = id
            id = None

        # Check the value of ID as a int
        if id is not None and isinstance(id, int):
            if not self.__LCs_by_ID__:
                self.__LCs_by_ID__ = {loadcase.ID: loadcase for loadcase in self.LoadCases}
                aux = self.__LCs_by_ID__.get(id, None)
            else:
                aux = self.__LCs_by_ID__.get(id, None)

            if aux is None:
                N2PLog.Error.E221(id)
            return aux
        
        # Check the value of ID as list
        if id is not None and isinstance(id, list):
            if not self.__LCs_by_ID__:
                self.__LCs_by_ID__ = {loadcase.ID: loadcase for loadcase in self.LoadCases}
            
            aux = []

            for id_i in id:
                lc = self.__LCs_by_ID__.get(id_i, None)
                aux.append(lc)
                if lc is None:
                    N2PLog.Error.E221(id_i)

            return aux

        # Check the value of Name
        elif name is not None and isinstance(name, str):
            if not self.__LCs_by_Name__:
                self.__LCs_by_Name__ = {loadcase.Name: loadcase for loadcase in self.LoadCases}
            aux = self.__LCs_by_Name__.get(name, None)

            if aux is None:
                N2PLog.Error.E222(name)
            return aux

        # Check the value of name as list
        if name is not None and isinstance(name, list):
            if not self.__LCs_by_Name__:
                self.__LCs_by_Name__ = {loadcase.Name: loadcase for loadcase in self.LoadCases}
            
            aux = []

            for n_i in name:
                lc = self.__LCs_by_Name__.get(n_i, None)
                aux.append(lc)
                if lc is None:
                    N2PLog.Error.E222(n_i)

            return aux
        
        # Return all load cases
        else:
            return self.LoadCases

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo general para elementos ------------------------------------------------------------------------------------
    @overload
    def get_elements(self, ids: int = 0) -> N2PElement: ...
    @overload
    def get_elements(self, ids: tuple[int, str] = 0) -> N2PElement: ...
    @overload
    def get_elements(self, ids: list[int] = 0) -> list[N2PElement]: ...
    @overload
    def get_elements(self, ids: list[tuple[int, str]] = 0) -> list[N2PElement]: ...

    # Actual implementation
    def get_elements(self, ids = 0):
        """ General method for obtain elements.

        If it has no argument or is 0: returns all the elements
        If it has one id as argument: returns one :class:`N2PElement` 
        If it has a list as argument, it returns a list of :class:`N2PElement`
        The ids should be a tuple (id, part_id). If not, part_id = 0 by default

        Args:
            ids: int | list[int] | tuple[int, str] | list[tuple[int, str]]

        Returns:
            object: N2PElement | list[N2PElement]
        """
        try:
            if ids == 0:
                elements = list(self.__element_dict.values())
                return elements

            if ids != 0 and isinstance(ids, int):
                if self.Solver == "Nastran" or self.Solver == "H3DOptistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                    if len(self.__partIDtoStr) > 1:
                        N2PLog.Error.E223()
                        elements = -2
                    else:
                        elements = self.__element_dict.get((ids, 0), -1)
                elif self.Solver == "Abaqus":
                    if len(self.__partIDtoStr) > 2:
                        N2PLog.Error.E223()
                        elements = -2
                    else:
                        elements = self.__element_dict.get((ids, 1), -1)
                if elements == -1:
                    N2PLog.Error.E202(ids)
                return elements

            if isinstance(ids, tuple) and len(ids) == 2:
                if isinstance(ids[1], str):
                    aux = self.__StrPartToID.get(ids[1])
                    elements = self.__element_dict.get((ids[0], aux), -1)
                else:
                    elements = self.__element_dict.get(ids, -1)
                if elements == -1: N2PLog.Error.E202(ids)
                return elements

            if (isinstance(ids, tuple) and len(ids) > 2) or isinstance(ids, list):
                elements = list()
                if isinstance(ids[0], tuple):
                    for id in ids:
                        if isinstance(id[1], str):
                            aux = self.__StrPartToID.get(id[1])
                            elemento = self.__element_dict.get((id[0], aux), -1)
                        else:
                            elemento = self.__element_dict.get(id, -1)
                        if elemento == -1: N2PLog.Error.E202(id)
                        elements.append(elemento)
                    return elements

                if isinstance(ids[0], int):
                    for id in ids:
                        if self.Solver == "Nastran" or self.Solver == "H3DOptistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                            if len(self.__partIDtoStr) > 1:
                                N2PLog.Error.E223()
                                elemento = -2
                            else:
                                elemento = self.__element_dict.get((id, 0), -1)
                        elif self.Solver == "Abaqus":
                            if len(self.__partIDtoStr) > 2:
                                N2PLog.Error.E223()
                                elements = -2
                            else:
                                elemento = self.__element_dict.get((id, 1), -1)
                        if elemento == -1:
                            N2PLog.Error.E202(id)
                        elements.append(elemento)
                    return elements
            return elements

        except:
            elements = -1
            N2PLog.Error.E205(ids)
            return elements


    def get_elements_filtered(self, 
                              materials: Union[str, int, list[Union[str, int]]] = None, 
                              properties: Union[str, int, list[Union[str, int]]] = None, 
                              parts: Union[str, list[str]] = None, 
                              elementType: Union[str, list[str]] = None) -> list[N2PElement]:
        """
        Filters and returns a list of :class:`N2PElement` objects based on the specified criteria.

        This function allows external users to retrieve model elements by applying different filters.
        Materials, properties, parts, and element types can be specified to refine the search.
        
        If multiple filters are provided, the function returns only elements that meet 
        all conditions (AND logic). If no filters are specified, an empty list is returned.

        Args:
            materials (list[str], optional): List of material names to filter elements by material type.
            properties (list[str], optional): List of properties to filter elements based on attributes.
            parts (list[str], optional): List of part names to obtain elements belonging to specific parts.
            elementType (list[str], optional): List of element types to filter elements by type.

        Returns:
            list[N2PElement]: List of elements that meet the applied filters.

        Example:
            >>> model = n2p.load_model(r".\\abaqus_model.odb")
            >>> elements = model.get_elements_filtered(materials=['Steel'], properties=['Steel Shell'])

            >>> model = n2p.load_model(r".\\nastran_model.op2")
            >>> elements = model.get_elements_filtered(materials=[10001])

        Note:
            - If both `materials` and `parts` are provided, elements from the specified materials within the given parts will be filtered.
            - It is recommended to use this function when a specific selection of model elements is needed.
            - This method is faster than making a comprehension list.
        """
        modelContent = self.__vzmodel
        filters = []  # Lista para almacenar los conjuntos de IDs
        
        if isinstance(materials, (str, int)):  
            materials = [materials]
        if isinstance(properties, (str, int)):  
            properties = [properties]
        if isinstance(parts, str):  
            parts = [parts]
        if isinstance(elementType, str):  
            elementType = [elementType]

        if materials and any(isinstance(m, int) for m in materials):
            materials = [str(m) for m in materials]
        
        if properties and any(isinstance(p, int) for p in properties):
            properties = [str(p) for p in properties]

        # Realizamos comprobación de la existencia de los distintos filtros y convertimos los input en variables C#
        if properties is not None:
            csharp_properties = System.Array.CreateInstance(System.String, len(properties))
            for i, property in enumerate(properties):
                csharp_properties[i] = property
            filterIdsByProperties = set(N2SelectionFunctions.FilterIdsByProperties(
                csharp_properties,
                modelContent
            ))
            filters.append(filterIdsByProperties)

        if elementType is not None:
            csharp_elementType = System.Array.CreateInstance(System.String, len(elementType))
            for i, eleType in enumerate(elementType):
                csharp_elementType[i] = eleType
            filterIdsByElementType = set(N2SelectionFunctions.FilterIdsByElementType(
                csharp_elementType,
                modelContent
            ))
            filters.append(filterIdsByElementType)

        if parts is not None:
            csharp_parts = System.Array.CreateInstance(System.String, len(parts))
            for i, part in enumerate(parts):
                csharp_parts[i] = part
            if materials is not None:
                csharp_materials = System.Array.CreateInstance(System.String, len(materials))
                for i, material in enumerate(materials):
                    csharp_materials[i] = material
                filterIdsByMaterials = set(N2SelectionFunctions.FilterIdsByMaterials(
                    csharp_materials,
                    modelContent,
                    csharp_parts
                ))
                filters.append(filterIdsByMaterials)
            else:
                filterIdsByParts = set(N2SelectionFunctions.FilterIdsByParts(
                    csharp_parts,
                    modelContent
                ))
                filters.append(filterIdsByParts)
        else:
            if materials is not None:
                csharp_materials = System.Array.CreateInstance(System.String, len(materials))
                for i, material in enumerate(materials):
                    csharp_materials[i] = material
                filterIdsByMaterials = set(N2SelectionFunctions.FilterIdsByMaterials(
                    csharp_materials,
                    modelContent
                ))
                filters.append(filterIdsByMaterials)

        # Realizar la intersección de todos los filtros existentes
        if filters:
            result_ids = set.intersection(*filters)
        else:
            result_ids = set()  # Si no hay filtros, devuelve un conjunto vacío

        return [self.__cells_list[id] for id in result_ids]
    
    # Método para obtener materiales -----------------------------------------------------------------------------------
    @overload
    def get_materials(self, ids: int = 0) -> N2PMaterial: ...
    @overload
    def get_materials(self, ids: tuple[int, str] = 0) -> N2PMaterial: ...
    @overload
    def get_materials(self, ids: list[int] = 0) -> list[N2PMaterial]: ...
    @overload
    def get_materials(self, ids: list[tuple[int, str]] = 0) -> list[N2PMaterial]: ...
    @overload
    def get_materials(self, ids: str = 0) -> N2PMaterial: ...
    @overload
    def get_materials(self, ids: list[tuple[str, str]] = 0) -> list[N2PMaterial]: ...

    # Actual implementation
    def get_materials(self, ids = 0):
        """ General method for obtain materials.

        If it has no argument or is 0: returns all the materials
        If it has one id as argument: returns one :class:`N2PMaterial` \\
        If it has a list as argument, it returns a list of :class:`N2PMaterial`
        The ids should be a tuple (id, part_id). If not, part_id = 0 by default

        Args:
            ids: int | str | list[int] | tuple[int, str] | list[tuple[int, str]]

        Returns:
            object: N2PMaterial | list[N2PMaterial]
        """
        try:
            if ids == 0:
                materials = list(self.MaterialDict.values())
                return materials
            if ids != 0 and isinstance(ids,(int,str)):
                if self.Solver == "Nastran" or self.Solver == "H3DOptistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                    if len(self.__partIDtoStr) > 1:
                        N2PLog.Error.E223()
                        materials = -2
                    else:
                        part = next(iter(self.__StrPartToID))
                        materials = self.MaterialDict.get((ids,part),-1)
                elif self.Solver == 'Abaqus':
                    materials = self.MaterialDict.get((ids,'ASSEMBLY'),-1) #No necesito mirar si hay más de una parte porque siempre va a ser assembly para materiales
                if materials == -1:
                    N2PLog.Error.E672(ids)
                return materials
            
            if isinstance(ids, tuple) and len(ids) == 2:
                # No necesito mirar si la parte de la tupla es un string porque siempre debe serlo
                materials = self.MaterialDict.get((ids[0],ids[1]),-1)
                if materials == -1: N2PLog.Error.E672(ids)
                return materials
            
            if isinstance(ids, list):
                materials = list()
                if isinstance(ids[0],tuple):
                    for id in ids:
                        material = self.MaterialDict.get((id[0],id[1]),-1)
                        if material == -1: N2PLog.Error.E672(ids)
                        materials.append(material)
                    return materials
                
                if isinstance(ids[0], (int,str)):
                    for id in ids:
                        if self.Solver == "Nastran" or self.Solver == "H3DOptistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                            if len(self.__partIDtoStr) > 1:
                                N2PLog.Error.E223()
                                material = -2
                            else:
                                part = next(iter(self.__StrPartToID))
                                material = self.MaterialDict.get((id,part),-1)
                        elif self.Solver == 'Abaqus':
                            material = self.MaterialDict.get((id,'ASSEMBLY'),-1) #No necesito mirar si hay más de una parte porque siempre va a ser assembly para materiales
                        if material == -1:
                            N2PLog.Error.E672(id)
                        materials.append(material)
                    return materials
            return materials
        except:
            materials = -1
            N2PLog.Error.E205(ids)
            return materials
        
    # Método para obtener propiedades -----------------------------------------------------------------------------------
    @overload
    def get_properties(self, ids: int = 0) -> N2PProperty: ...
    @overload
    def get_properties(self, ids: tuple[int, str] = 0) -> N2PProperty: ...
    @overload
    def get_properties(self, ids: list[int] = 0) -> list[N2PProperty]: ...
    @overload
    def get_properties(self, ids: list[tuple[int, str]] = 0) -> list[N2PProperty]: ...
    @overload
    def get_properties(self, ids: str = 0) -> N2PProperty: ...
    @overload
    def get_properties(self, ids: list[tuple[str, str]] = 0) -> list[N2PProperty]: ...

    # Actual implementation
    def get_properties(self, ids = 0):
        """ General method for obtain properties.

        If it has no argument or is 0: returns all the properties
        If it has one id as argument: returns one :class:`N2PProperty` \\
        If it has a list as argument, it returns a list of :class:`N2PProperty`
        The ids should be a tuple (id, part_id). If not, part_id = 0 by default

        Args:
            ids: int | str | list[int] | tuple[int, str] | list[tuple[int, str]]

        Returns:
            object: N2PProperty | list[N2PProperty]
        """
        try:
            if ids == 0:
                properties = list(self.PropertyDict.values())
                return properties
            if ids != 0 and isinstance(ids,(int,str)):
                if self.Solver == "Nastran" or self.Solver == "H3DOptistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                    if len(self.__partIDtoStr) > 1:
                        N2PLog.Error.E223()
                        properties = -2
                    else:
                        part = next(iter(self.__StrPartToID))
                        properties = self.PropertyDict.get((ids,part),-1)
                elif self.Solver == 'Abaqus':
                    properties = self.PropertyDict.get((ids,'ASSEMBLY'),-1) #No necesito mirar si hay más de una parte porque siempre va a ser assembly para materiales
                if properties == -1:
                    N2PLog.Error.E673(ids)
                return properties
            
            if isinstance(ids, tuple) and len(ids) == 2:
                # No necesito mirar si la parte de la tupla es un string porque siempre debe serlo
                properties = self.PropertyDict.get((ids[0],ids[1]),-1)
                if properties == -1: N2PLog.Error.E673(ids)
                return properties
            
            if isinstance(ids, list):
                properties = list()
                if isinstance(ids[0],tuple):
                    for id in ids:
                        prop = self.PropertyDict.get((id[0],id[1]),-1)
                        if prop == -1: N2PLog.Error.E673(ids)
                        properties.append(prop)
                    return properties
                
                if isinstance(ids[0], (int,str)):
                    for id in ids:
                        if self.Solver == "Nastran" or self.Solver == "H3DOptistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                            if len(self.__partIDtoStr) > 1:
                                N2PLog.Error.E223()
                                prop = -2
                            else:
                                part = next(iter(self.__StrPartToID))
                                prop = self.PropertyDict.get((id,part),-1)
                        elif self.Solver == 'Abaqus':
                            prop = self.PropertyDict.get((id,'ASSEMBLY'),-1) #No necesito mirar si hay más de una parte porque siempre va a ser assembly para materiales
                        if prop == -1:
                            N2PLog.Error.E673(id)
                        properties.append(prop)
                    return properties
            return properties
        except Exception as e:
            properties = -1
            N2PLog.Error.E205(str(e))
            return properties

    # Metodo general para nodos ----------------------------------------------------------------------------------------
    def get_nodes(self, ids=0) -> Union[N2PNode, list[N2PNode]]:
        """ General method for obtain nodes.

        If it has no argument or is 0: returns all the nodes.
        If it has one id as argument: returns one :class:`N2PNode`.
        If it has a list as argument, it returns a list of :class:`N2PNode`.
        The ids should be a tuple (id, part_id). If not, part_id = 0 by default.

        Args:
            ids: int | list[int] | tuple[int, str] | list[tuple[int, str]]

        Returns:
            object: N2PNode | list[N2PNode]
        """
        try:
            if ids == 0:
                nodes = list(self.__node_dict.values())
                return nodes

            if ids != 0 and isinstance(ids, int):
                if self.Solver == "Nastran" or self.Solver == "H3DOptistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                    if len(self.__partIDtoStr) > 1:
                        N2PLog.Error.E224()
                        nodes = -2
                    else:
                        nodes = self.__node_dict.get((ids, 0), -1)

                elif self.Solver == "Abaqus":
                    if len(self.__partIDtoStr) > 2:
                        N2PLog.Error.E224()
                        nodes = -2
                    else:
                        nodes = self.__node_dict.get((ids, 1), -1)

                if nodes == -1:
                    N2PLog.Error.E201(ids)
                return nodes

            if isinstance(ids, tuple) and len(ids) == 2:
                if isinstance(ids[1], str):
                    aux = self.__StrPartToID.get(ids[1])
                    nodes = self.__node_dict.get((ids[0], aux), -1)
                else:
                    nodes = self.__node_dict.get(ids, -1)
                if nodes == -1: N2PLog.Error.E201(ids)
                return nodes

            if (isinstance(ids, tuple) and len(ids) > 2) or isinstance(ids, list):
                nodes = list()
                if isinstance(ids[0], tuple):
                    for id in ids:
                        if isinstance(id[1], str):
                            aux = self.__StrPartToID.get(id[1])
                            nodo = self.__node_dict.get((id[0], aux), -1)
                        else:
                            nodo = self.__node_dict.get(id, -1)
                        if nodo == -1: N2PLog.Error.E201(id)
                        nodes.append(nodo)
                    return nodes

                if isinstance(ids[0], int):
                    for id in ids:
                        if self.Solver == "Nastran" or self.Solver == "H3DOptistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                            if len(self.__partIDtoStr) > 1:
                                N2PLog.Error.E224()
                                nodo = -2
                            else:
                                nodo = self.__node_dict.get((id, 0), -1)
                        elif self.Solver == "Abaqus":
                            if len(self.__partIDtoStr) > 2:
                                N2PLog.Error.E224()
                                nodes = -2
                            else:
                                nodo = self.__node_dict.get((id, 1), -1)
                        if nodo == -1:
                            N2PLog.Error.E201(id)
                        nodes.append(nodo)
                    return nodes
            return nodes

        except:
            nodes = -1
            N2PLog.Error.E205(ids)
            return nodes

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo general para conectores -----------------------------------------------------------------------------------
    def get_connectors(self, ids=0) -> Union[N2PConnector, list[N2PConnector]]:
        """ General method for obtain connectors.

        If it has no argument or is 0: returns all the elements.
        If it has one id as argument: returns one :class:`N2PConnector`.
        If it has a list as argument, it returns a list of :class:`N2PConnector`.
        The ids should be a tuple (id, part_id). If not, part_id = 0 by default.

        Args:
            ids: int | list[int] | tuple[int, str] | list[tuple[int, str]]

        Returns:
            object: N2PConnector | list[N2PConnector]
        """
        try:
            if ids == 0:
                connectors = list(self.__connector_dict.values())
                return connectors

            if ids != 0 and isinstance(ids, int):
                if self.Solver == "Nastran" or self.Solver == "H3DOptistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                    if len(self.__partIDtoStr) > 1:
                        N2PLog.Error.E225()
                        connectors = -2
                    else:
                        connectors = self.__connector_dict.get((ids, 0), -1)

                elif self.Solver == "Abaqus":
                    if len(self.__partIDtoStr) > 2:
                        N2PLog.Error.E225()
                        connectors = -2
                    else:
                        connectors = self.__connector_dict.get((ids, 1), -1)
                if connectors == -1:
                    N2PLog.Error.E204(ids)
                return connectors

            if isinstance(ids, tuple) and len(ids) == 2:
                if isinstance(ids[1], str):
                    aux = self.__StrPartToID.get(ids[1])
                    connectors = self.__connector_dict.get((ids[0], aux), -1)
                else:
                    connectors = self.__connector_dict.get(ids, -1)
                if connectors == -1: N2PLog.Error.E204(ids)
                return connectors

            if (isinstance(ids, tuple) and len(ids) > 2) or isinstance(ids, list):
                connectors = list()
                if isinstance(ids[0], tuple):
                    for id in ids:
                        if isinstance(id[1], str):
                            aux = self.__StrPartToID.get(id[1])
                            conector = self.__connector_dict.get((id[0], aux), -1)
                        else:
                            conector = self.__connector_dict.get(id, -1)
                        if conector == -1: N2PLog.Error.E204(id)
                        connectors.append(conector)
                    return connectors

                if isinstance(ids[0], int):
                    for id in ids:
                        if self.Solver == "Nastran" or self.Solver == "H3DOptistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                            if len(self.__partIDtoStr) > 1:
                                N2PLog.Error.E225()
                                conector = -2
                            else:
                                conector = self.__connector_dict.get((id, 0), -1)

                        elif self.Solver == "Abaqus":
                            if len(self.__partIDtoStr) > 2:
                                N2PLog.Error.E225()
                                connectors = -2
                            else:
                                conector = self.__connector_dict.get((id, 1), -1)

                        if conector == -1: N2PLog.Error.E204(id)
                        connectors.append(conector)
                    return connectors
            return connectors

        except:
            connectors = -1
            N2PLog.Error.E205(ids)
            return connectors
            # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener todos los sistemas de coordenadas (como N2Coord)----------------------------------------------
    def get_coords(self, ids=0) -> Union[N2PCoord, list[N2PCoord]]:
        """General method for obtain coordinate systems.

        If it has no argument or is 0: returns all the coordinate systems
        If it has one id as argument: returns one :class:`N2PCoord`
        If it has a list as argument, it returns a list of :class:`N2PCoord`
        The ids should be a tuple (id, part_id). If not, part_id = 0 by default

        Args:
            ids: int | list[int] | tuple[int, str] | list[tuple[int, str]]

        Returns:
            object: N2PCoord | list[N2PCoord]
        """
        try:
            if ids == 0:
                coords = list(self.__coord_dict.values())
                return coords

            if ids != 0 and isinstance(ids, int):
                coords = self.__coord_dict.get((ids, 0), -1)
                if coords == -1: N2PLog.Error.E203(ids)
                return coords

            if isinstance(ids, tuple) and len(ids) == 2:
                if isinstance(ids[1], str):
                    aux = self.__StrPartToID.get(ids[1])
                    coords = self.__coord_dict.get((ids[0], aux), -1)
                else:
                    coords = self.__coord_dict.get(ids, -1)
                if coords == -1: N2PLog.Error.E203(ids)
                return coords

            if (isinstance(ids, tuple) and len(ids) > 2) or isinstance(ids, list):
                coords = list()
                if isinstance(ids[0], tuple):
                    for id in ids:
                        if isinstance(id[1], str):
                            aux = self.__StrPartToID.get(id[1])
                            coord = self.__coord_dict.get((id[0], aux), -1)
                        else:
                            coord = self.__coord_dict.get(id, -1)
                        if coord == -1: N2PLog.Error.E203(id)
                        coords.append(coord)
                    return coords

                if isinstance(ids[0], int):
                    for id in ids:
                        coord = self.__coord_dict.get((id, 0), -1)
                        if coord == -1: N2PLog.Error.E203(id)
                        coords.append(coord)
                    return coords
            return coords

        except:
            coords = -1
            N2PLog.Error.E205(ids)
            return coords
            # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ########################################    ClearResultStorage     #################################################
    ####################################################################################################################
    def clear_results_memory(self) -> None:
        """Method that deletes the results data store at low level. It is useful when a lot of results are asked and
        kept in Python memory"""
        self.__vzmodel.ClearResultsStorage()

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ##########################################    Element-Nodal     ####################################################
    ####################################################################################################################
    # Metodo oculto para generar el array de nodos descosidos-----------------------------------------------------------
    def elementnodal(self, elements: list[N2PElement] = None) -> dict[int, tuple]:
        """ Method that generates the dictionary for the element-nodal mesh.

        Use the internal id for unsew nodes as key and a tuple (ID_Part_Solver, ID_Node_Solver, ID_Element_Solver) as a
        value. If the dictionary has already created it is pointed instead.

        Args:
            elements: list[N2PElement] (optional)
                If a list of N2PElements is provided it returns a dict for the unsew nodes of those elements

        Returns:
            dict[internal_node_unsew] = (Part_Solver, ID_Node_Solver, ID_Element_Solver)

        Example:
            >>> all_unsew_nodes = model.elementnodal()
            >>> elements = model.get_elements([1001, 1002, 1003])
            >>> some_unsew_nodes = model.elementnodal(elements)
        """
        # Si ya se ha creado no se vuelve a crear, directamente devuelve el valor
        if not elements:
            if self.__elementnodal_dict is not None:
                return self.__elementnodal_dict
            else:

                aux = self.__vzmodel.GetNodosDescosidos()
                aux2 = np.array(aux, dtype=np.int32)

                self.__elementnodal_dict = {i: (self.__partIDtoStr.get(aux2[i][2], None), aux2[i][0], aux2[i][1])
                                            for i in range(aux2.shape[0])}

                return self.__elementnodal_dict
        else:
            elements_id = {ele.ID for ele in elements}
            aux = self.__vzmodel.GetNodosDescosidos()
            aux2 = np.array(aux, dtype=np.int32)
            return {i: (self.__partIDtoStr.get(aux2[i][2], None), aux2[i][0], aux2[i][1]) for i in range(aux2.shape[0]) if aux2[i][1] in elements_id}

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ##########################################     Free Bodies      ####################################################
    ####################################################################################################################
    def create_free_body(self, name: str, loadcase: N2PLoadCase, increment: N2PIncrement = None, nodes: list[N2PNode] =
        None, elements: list[N2PElement] = None, outpoint: tuple[float, ...] = None,
        coordsysout: N2PCoord = None) -> N2PFreeBody:
        """Method that creates a :class:`N2PFreeBody` object, keeps in :meth:`FreeBodiesDict` and returns it.

        A :class:`N2PFreeBody` contains the information of the cross-section defined by the user and the forces and moments
        calculated by NaxToPy durin the instance of the object.

        Args:
            name: str -> Must be unique. If a new FreeBody is name as an old one, the old FreeBody will be deleted.
            loadcase: N2PLoadCase
            increment: N2PIncrement
            nodes: list[N2PNode]
            elements: list[N2PElement]
            outpoint: tuple[float]
            coordsysout: N2PCoord

        Returns:
            N2PFreeBody: freebody

        Example:
            >>> model = load_model("model.op2")
            >>> lc = model.get_load_case(5)
            >>> incr = lc.ActiveN2PIncrement
            >>> node_list = model.get_nodes([1000, 1001, 1002, 1003, 1004, 1005])
            >>> elem_list = model.get_elements([1000, 1001, 1002, 1003, 1004])

        """

        if increment is None:
            increment = loadcase.ActiveN2PIncrement

        return N2PFreeBody(name, loadcase, increment, nodes, elements, self, coordsysout, outpoint)

    # ------------------------------------------------------------------------------------------------------------------

    def _import_load_cases(self):
        lcs = self.__vzmodel.LoadCases
        __number_of_load_cases = int(lcs.Count)

        self.__load_cases__ = [N2PLoadCase(lc.ID,
                                           lc.IDOriginal,
                                           lc.Increments,
                                           lc.IncrementsNumberList,
                                           lc.LCType,
                                           lc.Name,
                                           lc.Results,
                                           lc.SolutionType,
                                           lc.Solver,
                                           self,
                                           lc) for lc in lcs]

    ####################################################################################################################
    ########################################     import_results      ###################################################
    ####################################################################################################################
    def import_results_from_files(self, results_files: list[str]) -> None:
        """Method of :class:`N2PModelContent` that reads an output result file from Nastran, Abaqus, Optistruct or Ansys and
         add the results to the :class:`N2PModelContent` instance.

        Supports .op2, .xdb, .odb, .h5, .h3d and .rst file extensions read from a local filesystem or URL.

        Args:
            results_files: list[str]

        Example:
            >>> model1 = load_model("model1_lc1.odb")
            >>> model1.import_results_from_files(["model1_lc2.odb", "mode1l_lc3.odb"])

            >>> model2 = load_model("model2.dat", "InputFileNastran")
            >>> model2.import_results_from_files(["model2_lc1.op2", "model2_lc2.op2"])
        """
        if isinstance(results_files, str):
            results_files = [results_files]

        for result_file in results_files:
            if os.path.isfile(result_file):
                self.__vzmodel.ImportResults(str(result_file))
                N2PLog.Debug.D201(str(result_file))
            else:
                N2PLog.Error.E232(str(result_file))

        self._import_load_cases()
        self.__LCs_by_ID__ = {lc.ID: lc for lc in self.LoadCases}

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ##################################     get_adjacent_from_elements      #############################################
    ####################################################################################################################
    def get_elements_adjacent(self, cells: list[N2PElement, N2PConnector],
            domain: list[N2PElement, N2PConnector] = None) -> list[N2PElement, N2PConnector]:
        """Method of :class:`N2PModelContent` that returns a list of :class:`N2PElement` and :class:`N2PConnector` that
        are adjacent to selected ones. If a domain is selected, the adjacent elements only will be searched in that domain.

        Args:
            cells: list[N2PElement, N2PConnector, ...]
            domain: list[N2PElement, N2PConnector, ...] -> Optional. Set the domain where to look for the adjacent elements

        Returns:
            list[N2PElement, N2PConnector, ...]

        Example:
            >>> model = load_model("model.odb")
            >>> domain_S4 = [e for e in model.get_elements() if e.TypeElement == "S4"]
            >>> elems_adj = model.get_elements_adjacent(model.get_elements(17500), domain=domain_S4)
            """
        if not isinstance(cells, list):
            cells = [cells]
        inernal_ids = array.array("q", [cell.InternalID for cell in cells])
        if not domain:
            adjacent_ids = N2AdjacencyFunctions.GetAdjacent(self.__vzmodel.UMesh, inernal_ids)
        else:
            csharp_bool_array = System.Array.CreateInstance(System.Boolean,
                                                            len(self.__element_dict) + len(self.__connector_dict))

            for elem in domain:
                csharp_bool_array[elem.InternalID] = True

            adjacent_ids = N2AdjacencyFunctions.GetAdjacent(self.__vzmodel.UMesh, inernal_ids, csharp_bool_array)

        cell_list = self.__cells_list

        return [cell_list[ids] for ids in adjacent_ids]

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ##################################     get_adjacent_from_elements      #############################################
    ####################################################################################################################
    def get_elements_attached(self, cells: list[N2PElement, N2PConnector],
            domain: list[N2PElement, N2PConnector] = None) -> list[N2PElement, N2PConnector]:
        """Method of :class:`N2PModelContent` that returns a list of :class:`N2PElement` and :class:`N2PConnector` that
        are attached to selected ones. If a domain is selected, the attached elements only will be searched in that domain.

        Args:
            cells: list[N2PElement, N2PConnector, ...]
            domain: list[N2PElement, N2PConnector, ...] -> Optional. Set the domain where to look for the adjacent elements

        Returns:
            list[N2PElement, N2PConnector, ...]

        Example:
            >>> model = load_model("model.h3d")
            >>> domain_elems = model.get_elements()
            >>> elems_att = model.get_elements_attached(model.get_elements(17500), domain=domain_elems)
            """
        if not isinstance(cells, list):
            cells = [cells]
        inernal_ids = array.array("q", [cell.InternalID for cell in cells])
        if not domain:
            adjacent_ids = N2AdjacencyFunctions.GetAttached(self.__vzmodel.UMesh, inernal_ids)
        else:
            
            mesh_len = self.__vzmodel.UMesh.GetNumberOfCells()
            bool_array = np.zeros((mesh_len,), bool)
            domain_id = [ele.InternalID for ele in domain]
            bool_array[domain_id] = True
            adjacent_ids = N2AdjacencyFunctions.GetAttached(self.__vzmodel.UMesh, inernal_ids, _numpytonet(bool_array))

        cell_list = self.__cells_list

        return [cell_list[ids] for ids in adjacent_ids]

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    #########################################     get_by_face      #####################################################
    ####################################################################################################################
    def get_elements_by_face(self,
                             cells: list[N2PElement, N2PConnector],
                             tolerance_angle: float = 30,
                             one_element_adjacent: bool = True,
                             domain: list[N2PElement, N2PConnector] = None) -> list[N2PElement, N2PConnector]:
        """ Method of :class:`N2PModelContent` that returns a list of :class:`N2PElement` and :class:`N2PConnector`
        that are in the same face as the selected ones. If a domain is selected, the face elements only will be searched
        in that domain. To be considered in the same face, the adjacent element must share an arist and the angle between
        the elements must be lower than the tolerance angle.

        Args:
            cells: list[N2PElement, N2PConnector, ...]

            tolerance_angle: float -> Optional (30º by default). Max angle[º] between two elements to be considered in the same face

            one_element_adjacent: bool -> Optional (True by default). If true, two elements are connected to edge of a selected element they will not be considered.

            domain: list[N2PElement, N2PConnector, ...] -> Optional. Set the domain where to look for the adjacent elements

        Returns:
            list[N2PElement, N2PConnector, ...]

        Example:
            >>> model = load_model("model.op2")
            >>> elems1 = model.get_elements_by_face(model.get_elements(17500))
            >>> domain_cquad = [e for e in model.get_elements() if e.TypeElement == "CQUAD4"]
            >>> elems2 = model.get_elements_by_face(model.get_elements([17500, 17501]), 25, domain=domain_cquad)
            """
        if not isinstance(cells, list):
            cells = [cells]
        inernal_ids = array.array("q", [cell.InternalID for cell in cells])
        if not domain:
            adjacent_ids = N2AdjacencyFunctions.GetByFace(self.__vzmodel,
                                                          inernal_ids,
                                                          tolerance_angle,
                                                          one_element_adjacent)
        else:
            csharp_bool_array = System.Array.CreateInstance(System.Boolean,
                                                            len(self.__element_dict) + len(self.__connector_dict))

            for elem in domain:
                csharp_bool_array[elem.InternalID] = True

            adjacent_ids = N2AdjacencyFunctions.GetByFace(self.__vzmodel,
                                                          inernal_ids,
                                                          tolerance_angle,
                                                          one_element_adjacent,
                                                          csharp_bool_array)

        cell_list = self.__cells_list

        return [cell_list[ids] for ids in adjacent_ids]

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    #########################################     get_free_edges      ##################################################
    ####################################################################################################################
    def get_free_edges(self, domain: list[N2PElement, N2PConnector] = None) -> list[tuple[N2PElement,
                                                                                         N2PNode, N2PNode]]:

        """ Method of :class:`N2PModelContent` that returns a list of tuples of a :class:`N2PElement` and two :class:`N2PNode`
        of that element. The two nodes define the edge of the element that is contained in the free edge of the mesh If
        a domain is selected, the tuple will only be searched in that domain. Notice that connectors, although they may be
        given in the domain, they are never included in the free edges.

        Args:
            domain: list[N2PElement, N2PConnector, ...] -> Optional. Set the domain where to look for the free edges

        Returns:
            list[tuple[N2PElement, N2PNode, N2PNode], ...]
            """

        mesh_len = self.__vzmodel.UMesh.GetNumberOfCells()
        csharp_bool_array = System.Array.CreateInstance(System.Boolean, mesh_len)

        if not domain:
            for i in range(mesh_len):
                csharp_bool_array[i] = True
        else:
            for elem in domain:
                csharp_bool_array[elem.InternalID] = True

        free_edges_ids = N2FreeEdges.GetFreeEdgesFromVisibleIDs(self.__vzmodel.UMesh,
                                                                csharp_bool_array)

        cell_list = self.__cells_list
        node_list = list(self.__node_dict.values())
        return [(cell_list[id[0]], node_list[id[1]], node_list[id[2]]) for id in free_edges_ids]

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ######################################     Derived Load Case      ##################################################
    ####################################################################################################################
    def new_derived_loadcase(self, name: str, formula: str) -> N2PLoadCase:
        """Generate a new loadcase by linear combination of existing loadcases and frames.
        
        This method creates a :class:`N2PLoadCase` by combining multiple loadcase/frame pairs 
        using linear arithmetic operations. The derived loadcase will have a negative ID and 
        contains only one frame/increment with ID 0.
        
        Parameters
        ----------
        name : ``str``
            Name for the new derived loadcase.
        formula : ``str``
            String defining the linear combination using loadcase/frame pairs and arithmetic 
            operations. Loadcase/frame pairs must follow the structure ``<LCXX:FRYY>`` where 
            XX is the loadcase ID and YY is the frame ID. Examples:
            
            * ``"<LC1:FR1>+2*<LC2:FR1>+0.5*<LC5:FR3>"``
            * ``"0.5*<LC1:FR2>"``
            * ``"5*<LC2:FR3>-2*<LC3:FR3>"``
        
        Returns
        -------
        N2PLoadCase
            Derived loadcase with negative ID containing the linear combination results.
            
        .. note::
        
            The derived loadcase will have only one frame/increment with ID 0. When using 
            a derived loadcase in formulas, reference it as ``<LC-X:FR0>`` where X is the 
            absolute value of the negative ID.
        
        Examples
        --------
        >>> dev_lc1 = new_derived_loadcase(
        ...     "dev_lc1", 
        ...     "<LC1:FR1>+2*<LC2:FR1>+0.5*<LC5:FR3>"
        ... )
        >>> dev_lc2 = new_derived_loadcase("dev_lc2", "0.5*<LC1:FR2>")
        >>> dev_lc3 = new_derived_loadcase(
        ...     "dev_lc3", 
        ...     "5*<LC-1:FR0>+2*<LC3:FR3>"
        ... )
        """
        # Comprobamos que el nombre no se repite:
        i = 0
        while name in [lc.Name for lc in self.LoadCases]:
            i += 1
            name += f"-{i}"

        if i > 0:
            N2PLog.Warning.W301(name)

        # Argumentos para N2LoadCase
        envelopgroup = N2LoadCase

        # Genera una instancia de un N2LoadCase de NaxToModel
        cs_lc = N2LoadCase(self.__vzmodel, name, formula)

        # Método de N2LoadCase que pone todoo en su sitio
        cs_lc.RecalculateLCInfo2Formule()

        # Este metodo de N2ArithmeticSolver en NaxToModel comprueba que la formula introducida es correcta.
        # Devuelve False si está mal y True si está bien.
        err = N2ArithmeticSolver.CheckExpression(cs_lc.Formula, self.__vzmodel,
                                                 N2ArithmeticSolver.ExpressionType.LOAD_CASE)
        if int(err) == 0:
            pass
        else:
            N2PLog.Error.E228(formula, str(N2Enums.GetDescription(err).upper()))  # error
            return "ERROR"

        # Se transforma el caso de carga de NaxToModel en un N2PLoadCase de python
        py_lc = N2PLoadCase(cs_lc.ID, cs_lc.IDOriginal, cs_lc.Increments, cs_lc.IncrementsNumberList,
                            cs_lc.TypeLoadCase, cs_lc.Name, cs_lc.Results, cs_lc.SolutionType, cs_lc.Solver, self,
                            cs_lc)

        # Se añade el caso de carga de csharp a N2ModelContent de Vizzer
        self.__vzmodel.LoadCases.Add(cs_lc)

        # Se añade el case de carga de python a N2PModelContent
        self.__load_cases__.append(py_lc)

        # Se añade al diccionario si este ya existe
        if self.__LCs_by_ID__:
            self.__LCs_by_ID__[py_lc.ID] = py_lc

        return py_lc

    _criteria_typing = Literal['ExtremeMax', 'ExtremeMin', 'Max', 'Min', 'Range']
    _envelg_typing = Literal["ByContour", "ByLoadCaseID", "ByIncrement"]

    def new_envelope_loadcase(self, name: str, formula: str, criteria:_criteria_typing = "ExtremeMax",
                              envelgroup:_envelg_typing = "ByContour") -> N2PLoadCase:
        """Method of :class:`N2PModelContent` that generate a new :class:`N2PLoadCase` that is the envelope of the
        load cases and increments selected.

        The id is automatically generated. It will be negative, starting at -1. If the new load case use a derivated or
        envelope load case use LCD1 in the formula instead of LC-1:

        Args:
            name (`str`):
                Name of the envelope load case. It mustn't be repeated.

            formula (`str`):
                formula that define the loadcases and increments must have this structure: <LCXX:FRYY>. 
                Example: `"<LC1:FR1>,<LCD2:FR1>,<LC2:FR10>"`

            criteria (`str`)
                :Criteria for selecting the results to build the new derived load case. Possible values:
                    - 'ExtremeMax'
                    - 'ExtremeMin'
                    - 'Max'
                    - 'Min'
                    - 'Range'

            envelgroup (`str`):
                Criteria to select the data asociated to the elements/nodes:
                    - 'ByContour': The data will be the actual value (XX stress for example)
                    - 'ByLoadCaseID': The data will be the id of the original load case that is critical (LC 6363 for example)
                    - 'ByIncrement': The data will be the id of the increment that is critical

        Returns:
            N2PLoadCase

        Examples:
            >>> env_lc1 = new_envelope_loadcase("env_lc1", formula="<LC1:FR1>,<LC2:FR1>")
            >>> env_lc2 = new_envelope_loadcase("env_lc2", formula="<LC1:FR1>,<LC2:FR8>,<LC-3:FR0>", criteria="Min", envelgroup="ByLoadCaseID")
        """
        # Comprobamos que el nombre no se repite:
        i = 0
        while name in [lc.Name for lc in self.LoadCases]:
            i += 1
            name += f"-{i}"

        if i > 0:
            N2PLog.Warning.W301(name)

        # Comprobamos que la formula está bien:
        formula = formula.replace("-", "D").replace(" ", "")

        # Arguments for the constructor
        criteria_mapping = {
            'Range': EnvelopCriteria.Range,
            'ExtremeMin': EnvelopCriteria.ExtremeMin,
            'Max': EnvelopCriteria.Max,
            'Min': EnvelopCriteria.Min,
            'ExtremeMax': EnvelopCriteria.ExtremeMax
        }
        envelopcriteria = criteria_mapping.get(criteria, EnvelopCriteria.ExtremeMax)

        envelgroup_maping = {
            'ByContour': EnvelopGroup.ByContour,
            'ByLoadCaseID': EnvelopGroup.ByLoadCaseID,
            'ByIncrement': EnvelopGroup.ByIncrement
        }
        envelopgroup = envelgroup_maping.get(envelgroup, EnvelopGroup.ByContour)

        # Genera una instancia de un N2LoadCase de NaxToModel
        cs_lc = N2LoadCase(self.__vzmodel, name, formula, True, envelopgroup, False, envelopcriteria)

        # Método de N2LoadCase que pone todoo en su sitio
        cs_lc.RecalculateLCInfo2Formule()

        # Este metodo de N2ArithmeticSolver en NaxToModel comprueba que la formula introducida es correcta.
        # Devuelve False si está mal y True si está bien.
        err = N2ArithmeticSolver.CheckExpression(cs_lc.Formula, self.__vzmodel,
                                                 N2ArithmeticSolver.ExpressionType.LOAD_CASE)
        if int(err) == 0:
            pass
        else:
            N2PLog.Error.E229(formula, str(N2ErrorWarnningHandling.GetDescription(err).upper()))  # error
            return "ERROR"

        # Se transforma el caso de carga de NaxToModel en un N2PLoadCase de python
        py_lc = N2PLoadCase(cs_lc.ID, cs_lc.IDOriginal, cs_lc.Increments, cs_lc.IncrementsNumberList,
                            cs_lc.TypeLoadCase, cs_lc.Name, cs_lc.Results, cs_lc.SolutionType, cs_lc.Solver, self,
                            cs_lc)

        # Se añade el caso de carga de csharp a N2ModelContent de Vizzer
        self.__vzmodel.LoadCases.Add(cs_lc)

        # Se añade el case de carga de python a N2PModelContent
        self.__load_cases__.append(py_lc)

        # Se añade al diccionario si este ya existe
        if self.__LCs_by_ID__:
            self.__LCs_by_ID__[py_lc.ID] = py_lc

        return py_lc

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    #####################################     Results by LCs & Incr      ###############################################
    ####################################################################################################################
    def new_report(self, lc_incr: str, allincr: bool, result: str, componentssections: str, ifenvelope: bool,
                   selection: list[N2PNode, N2PElement], sortby: str, aveSections=-1, cornerData=False,
                   aveNodes=-1, variation=100, realPolar=0, coordsys: int = -1000,
                   v1: Union[tuple, np.ndarray] = (1, 0, 0), v2: Union[tuple, np.ndarray] = (0, 1, 0)) -> N2PReport:
        """Generate a report instance for extracting results from specified nodes or elements.
        
        This method creates a :class:`N2PReport` instance containing information about load cases, 
        increments, components and sections for a specific result type. The report can calculate 
        result arrays and export data to CSV format.
        
        Parameters
        ----------
        lc_incr : ``str``
            Formula specifying the loadcase-increment pairs. Each pair must follow the structure 
            ``<LCX:FRY>`` where X is the loadcase ID and Y is the increment/frame ID.
            Example: ``"<LC1:FR1>,<LC1:FR2>,<LC2:FR1>,<LC2:FR2>"``.
        allincr : ``bool``
            Flag to request all increments for the specified load cases.
        result : ``str``
            Name of the result type to extract (e.g., "DISPLACEMENTS", "STRESSES", "STRAINS").
        componentssections : ``str``
            Formula specifying components and sections. Each component can have multiple sections 
            following the structure ``<ComponentName:X#Y#Z#>`` where X, Y, Z are section names.
            Each section name must end with ``#``. Examples:
            
            * With sections: ``"<VONMISES:Z1#Z2#>,<MAX_SHEAR:Z1#Z2#>"``
            * Without sections: ``"<FX:NONE#>,<FY:NONE#>"``
            
        ifenvelope : ``bool``
            Flag to extract only envelope results from the specified load cases.
        selection : ``list[N2PNode] | list[N2PElement]``
            List of nodes or elements where results are requested. Must match the result type:
            
            * Displacements: Use list of ``N2PNode``
            * Stresses: Use list of ``N2PElement``
            
        sortby : ``str``
            Sorting criterion for results:
            
            * "LC": Sort by load cases
            * "IDS": Sort by element/node IDs
            
        aveSections : ``int``, default -1
            Optional. Operation to perform among sections:
            
            * -1: Maximum (default)
            * -2: Minimum
            * -3: Average
            * -4: Extreme
            * -6: Difference
            
        cornerData : ``bool``, default False
            Optional. Flag to control result location:
            
            * True: Results at element nodes
            * False: Results at element centroid (default)
            
        aveNodes : ``int``, default -1
            Optional. Operation among nodes when ``cornerData=True``:
            
            * 0: None
            * -1: Maximum (default)
            * -2: Minimum
            * -3: Average
            * -5: Average with variation parameter
            * -6: Difference
            
        variation : ``int``, default 100
            Optional. Averaging parameter between nodes (0-100):
            
            * 0: No averaging between nodes
            * 100: Total averaging between nodes (default)
            
        realPolar : ``int``, default 0
            Optional. Data type for complex results:
            
            * 1: Real/Imaginary
            * 2: Magnitude/Phase
            
        coordsys : ``int``, default -1000
            Optional. Coordinate system for result representation:
            
            * 0: Global coordinate system
            * -1: Material coordinate system
            * -10: User defined coordinate system
            * -20: Element/Node user defined coordinate system
            * -1000: Analysis coordinate system (default)
            * >0: Solver ID of predefined coordinate system
            
        v1 : ``tuple[float] | numpy.ndarray``, default (1, 0, 0)
            Optional. 3D vector defining the x-axis of the coordinate system.
        v2 : ``tuple[float] | numpy.ndarray``, default (0, 1, 0)
            Optional. 3D vector defining the xy-plane. The coordinate system axes are generated as:
            
            * x = v1
            * z = v1 ^ v2 (cross product)
            * y = z ^ x (cross product)
        
        Returns
        -------
        N2PReport
            Report instance containing the specified result configuration. The report provides methods to:
            
            * Calculate result arrays returning headers and results as ``numpy.ndarray`` (dtype=str)
            * Export data to CSV format
            
        .. note::
        
            Only one result type is available per report. For example, you can extract all 
            DISPLACEMENTS components for all load cases, but cannot include STRESSES in the same report.
        
        Examples
        --------
        >>> report1 = model.new_report(
        ...     "<LC1:FR1>,<LC2:FR1>", 
        ...     False, 
        ...     "DISPLACEMENTS", 
        ...     "<X:NONE#>,<Y:NONE#>", 
        ...     False, 
        ...     list_n2pnodes, 
        ...     "LC"
        ... )
        
        >>> report2 = model.new_report(
        ...     "<LC1:FR1>,<LC1:FR2>,<LC4:FR6>", 
        ...     False, 
        ...     "STRESSES", 
        ...     "<VON_MISES:Z1#Z2#>,<MAX_SHEAR:Z1#Z2#>", 
        ...     False, 
        ...     list_n2pelements, 
        ...     "IDS", 
        ...     aveSections=-4, 
        ...     coordsys=-1
        ... )
        """
        # Here it is checkd if the components, the loadcases and the result exist and the formula is right
        try:
            lcs = [int(lc.split(":")[0][3:]) for lc in lc_incr.split(",")]
            components = [c.split(":")[0][1:] for c in componentssections.split(">,")]
            for lc in lcs:
                all_comps = list(self.get_load_case(lc).get_result(result).Components.keys()) + \
                            list(self.get_load_case(lc).get_result(result).DerivedComponents.keys())
                if not all(c in all_comps for c in components):
                    N2PLog.Error.E312(lc, result)
                    return "ERROR"
        except:
            N2PLog.Error.E313()
            return "ERROR"

        return N2PReport(self.__vzmodel, lc_incr, allincr, result, componentssections, ifenvelope, selection, sortby,
                         aveSections, cornerData, aveNodes, variation, realPolar, coordsys, v1, v2)

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    #####################################     Results by LCs & Incr      ###############################################
    ####################################################################################################################
    @overload
    def get_result_by_LCs_Incr(
        self, 
        list_lc_incr: Union[list[tuple[N2PLoadCase, N2PIncrement]], list[tuple[int, int]]], 
        result: str, 
        component: list[str], # list of components. 
        sections: list = None, 
        aveSections: int = -1,
        cornerData: bool = False, 
        aveNodes: int = -1, 
        variation: int = 100, 
        realPolar: int = 0, 
        coordsys: int = -1000,
        v1: tuple = (1, 0, 0), 
        v2: tuple = (0, 1, 0),
        filter_list: list[Union[N2PElement, N2PNode]] = None
    ) -> dict[tuple[int, int, str], np.ndarray]: ...

    @overload
    def get_result_by_LCs_Incr(
        self, 
        list_lc_incr: Union[list[tuple[N2PLoadCase, N2PIncrement]], list[tuple[int, int]]], 
        result: str, 
        component: str, # Only one component
        sections: list = None, 
        aveSections: int = -1,
        cornerData: bool = False, 
        aveNodes: int = -1, 
        variation: int = 100, 
        realPolar: int = 0, 
        coordsys: int = -1000,
        v1: tuple = (1, 0, 0), 
        v2: tuple = (0, 1, 0),
        filter_list: list[Union[N2PElement, N2PNode]] = None
    ) -> dict[tuple[int, int], np.ndarray]: ...

    def get_result_by_LCs_Incr(
        self, 
        list_lc_incr, 
        result, 
        component, 
        sections: list = None, 
        aveSections: int = -1,
        cornerData: bool = False, 
        aveNodes: int = -1, 
        variation: int = 100, 
        realPolar: int = 0, 
        coordsys: int = -1000,
        v1: tuple = (1, 0, 0), 
        v2: tuple = (0, 1, 0), 
        filter_list = None
    ):
        """Get results of a component for multiple loadcases and increments.
            
        This method uses parallel subprocesses to speed up calculations and returns 
        a dictionary with loadcase/increment tuples as keys and numpy arrays as values.
        
        Parameters
        ----------
        list_lc_incr : ``list[tuple[int]]``
            List of tuples containing (loadcase_id, increment_id) pairs for which 
            to extract results.
        result : ``str``
            Name of the result type to extract (e.g., "STRESSES", "STRAINS", 
            "DISPLACEMENTS", "FORCES").
        component : ``str | list[str]``
            Component name(s) to extract. For stresses: "VON_MISES", "XX", "YY", etc.
            If list is provided, results for all components are returned.
        sections : ``list[str] | list[N2PSection]``
            Optional. Sections on which to perform operations. If None (default), operations 
            are performed on all sections.
        aveSections : ``int``, default -1
            Optional. Operation to perform among sections:
            
            * -1: Maximum (default)
            * -2: Minimum  
            * -3: Average
            * -4: Extreme
            * -6: Difference
            
        cornerData : ``bool``, default False
            Optional. Flag to control result location:
            
            * True: Results at element nodes
            * False: Results at element centroid (default)
            
        aveNodes : ``int``, default -1
            Optional. Operation among nodes when ``cornerData=True``:
            
            * 0: None
            * -1: Maximum (default)
            * -2: Minimum
            * -3: Average
            * -6: Difference
            
        variation : ``int``, default 100
            Optional. Averaging parameter between nodes (0-100):
            
            * 0: No averaging between nodes
            * 100: Total averaging between nodes (default)
            
        realPolar : ``int``, default 0
            Optional. Data type for complex results:
            
            * 1: Real/Imaginary
            * 2: Magnitude/Phase
            
        coordsys : ``int``, default -1000
            Optional. Coordinate system for result representation:
            
            * 0: Global coordinate system
            * -1: Material coordinate system  
            * -10: User defined coordinate system
            * -20: Element/Node user defined coordinate system
            * -1000: Analysis coordinate system (default)
            * >0: Solver ID of predefined coordinate system
            
            .. note::

                By default, results are in the analysis coordinate system. This is 
                usually the element system, but in OP2 from Nastran (version >= 2023.3), 
                it could be the material system if ``PARAM,OMID,YES`` is used.
            
        v1 : ``tuple[float]``, default (1, 0, 0)
            Optional. 3D vector defining the x-axis of the coordinate system.
        v2 : ``tuple[float]``, default (0, 1, 0)
            Optional. 3D vector defining the xy-plane. The coordinate system axes are generated as:
            
            * x = v1
            * z = v1 ^ v2 (cross product)
            * y = z ^ x (cross product)
            
        filter_list : ``list[N2PElement] | list[N2PNode]``
            Optional. Elements or nodes to filter results for. If None, results for all 
            elements/nodes are returned.
            
            .. warning::

                Filtering results can slow down extraction. If results are needed 
                for multiple separate lists, extract all results first and filter afterward.
        
        Returns
        -------
        dict
            Dictionary containing extracted results:
            
            * If **component** is ``str``: ``{(lc_id, incr_id): numpy.ndarray}``
            * If **component** is ``list``: ``{(lc_id, incr_id, component_name): numpy.ndarray}``
        
        Examples
        --------
        **Basic usage with single component:**
        
        >>> vonmises = model.get_result_by_LCs_Incr(
        ...     [(1, 2), (2, 2)], "STRESSES", "VON_MISES"
        ... )
        >>> vonmises_1_2 = vonmises[(1, 2)]  # Results for LC=1, Incr=2
        
        **Using loadcase and increment objects:**
        
        >>> XX = model.get_result_by_LCs_Incr(
        ...     [(loadcase1, increment2), (loadcase2, increment2)], 
        ...     "STRAINS", "XX"
        ... )
        >>> XX_1_2 = XX.get((loadcase2.ID, increment2.ID))
        
        **Filtering by sections:**
        
        >>> YY_Z1 = model.get_result_by_LCs_Incr(
        ...     [(1, 2), (2, 2), (3, 1)], 
        ...     "STRESSES", "YY", 
        ...     sections=["Z1"]
        ... )
        >>> YY_Z1_3_1 = YY_Z1.get((3, 1), None)
        
        **Using custom coordinate system:**
        
        >>> XY_transformed = model.get_result_by_LCs_Incr(
        ...     [(2, 2), (3, 1)], 
        ...     "STRESSES", "XY", 
        ...     v1=(0, -2, 0), 
        ...     v2=(0, 0, -3)
        ... )
        >>> XY_transformed_2_2 = XY_transformed.get((2, 2))
        
        **Filtering by elements and nodes:**
        
        >>> elements_face = model.get_elements_by_face(model.get_elements(100))
        >>> fx_inface = model.get_result_by_LCs_Incr(
        ...     [(1, 2), (3, 1)], 
        ...     "FORCES", "FX", 
        ...     filter_list=elements_face
        ... )
        >>> nodes_face = list({
        ...     node for element in elements_face for node in element.Nodes
        ... })
        >>> x_inface = model.get_result_by_LCs_Incr(
        ...     [(1, 2), (3, 1)], 
        ...     "DISPLACEMENTS", "X", 
        ...     filter_list=nodes_face
        ... )
        
        **Multiple components:**
        
        >>> stresses = model.get_result_by_LCs_Incr(
        ...     [(1, 2), (2, 2)], 
        ...     "STRESSES", 
        ...     ["VON_MISES", "MAXIMUM_PRINCIPAL"]
        ... )
        >>> vonmises_1_2 = stresses[(1, 2, "VON_MISES")]
        >>> maxp_2_2 = stresses[(2, 2, "MAXIMUM_PRINCIPAL")]
        >>> strains = model.get_result_by_LCs_Incr(
        ...     [(loadcase1, increment2), (loadcase2, increment2)], 
        ...     "STRAINS", 
        ...     ["XX", "XY", "YY"]
        ... )
        >>> XX_1_2 = strains.get((loadcase2.ID, increment2.ID, "XX"))
        """

        for lc, _ in list_lc_incr:
            if isinstance(lc, N2PLoadCase):
                aux_lc = lc
                if aux_lc._modelFather != self:
                    N2PLog.Error.E240()
                    return None
            elif isinstance(lc, int):
                aux_lc = self.get_load_case(lc)
                
            else:
                N2PLog.Error.E310()
                return None
            # I break the loop when I find the first load case that contains the result
            if result in aux_lc.Results:
                break
        
        if isinstance(component, list) and isinstance(component[0], str):
            n2_result = aux_lc.get_result(result)
            if not all(comp in n2_result.Components for comp in component) and not all(comp in n2_result.DerivedComponents for comp in component):
                N2PLog.Error.E319()
                return None
            n2pcomp = aux_lc.get_result(result).get_component(component[0])

        elif isinstance(component, str):
            n2pcomp = aux_lc.get_result(result).get_component(component)
            component = None
        else:
            N2PLog.Error.E318()
            return None

        

        # Aqui se llama la funcion de verdad que es un metodo de N2PComponent. Se llama a ella porque hace uso de otras
        # funciones ya definidas (n2paraminputresult) en la clase y es mejor no repetir codigo.
        return n2pcomp._get_result_by_LCs_Incr(list_lc_incr,
                                               component,
                                               sections,
                                               aveSections,
                                               cornerData,
                                               aveNodes,
                                               variation,
                                               realPolar,
                                               coordsys,
                                               v1,
                                               v2,
                                               filter_list)

    ####################################################################################################################
    #####################################     User Coordinate Systems      #############################################
    ####################################################################################################################
    def load_user_coord_sys_from_csv(self, path: str, where: Literal["NODES", "ELEMENTS"]) -> None:
        """Method that loads a coordinate system for each node/element as a user coordinate system from a CSV file.

        The user can define a different system for each element or node and ask for results in that system using the
        optional argument "coordsys=-20"

        The structure of the csv must have the node/element identification, and the coordinates of the vectors v1 and v2
        that generates the system: x = v1; z = v1^v2; y = z^v1. The structure for elements and nodes must be:

            node_id_1,part_id_1,x11,y11,z11,x12,y12,z12

        user_system_elements_example.csv:
            1001,0,1,0,0,0,1,0\n
            1002,0,0.3,0.2,0,0,1,0\n
            1003,0,0,1,0,1,1,0\n
            1004,0,2,0,1,0.4,1,3\n

        Warnings:
            If a CSV is loaded and the another is loaded, the previous information will be deleted.

        Args:
            path: path for a CSV.
            where: "NODES"|"ELEMENTS". The user coordinate systems are for the nodes or the elements.

        Examples:
              >>> N2PModelContent.load_user_coord_sys_from_csv(path="user_system_elements_example.csv", where="ELEMENTS")
              >>> N2PModelContent.load_user_coord_sys_from_csv("node_sys.csv", "NODES")
        """
        if where.upper() == "ELEMENTS":
            self.__vzmodel.ReadCSVUserElementCoordinateSystems(path)
        elif where.upper() == "NODES":
            self.__vzmodel.ReadCSVUserNodeCoordinateSystems(path)
        else:
            msg = N2PLog.Error.E231()
            raise ValueError(msg)

    # ------------------------------------------------------------------------------------------------------------------

    # Sets User Coordinate Systems -------------------------------------------------------------------------------------
    def set_user_coord_sys(self, array2d: Union[list, np.ndarray], where: Literal["NODES", "ELEMENTS"]) -> None:
        """Method that sets a coordinate system for each node/element as a user coordinate system using an array defined
        by the user.

        The user can define a different system for each element or node and ask for results in that system using the
        optional argument "coordsys=-20"

        The structure of the array must have the node/element identification, and the coordinates of the vectors v1 and v2
        that generates the system: x = v1; z = v1^v2; y = z^v1. The structure for elements and nodes must be:

            [ [node_id_1,part_id_1,x11,y11,z11,x12,y12,z12], [node_id_2,part_id_2,x21,y21,z21,x22,y22,z22], ... ]

        user_system_elements_example.csv:

            [ [1001,0,1,0,0,0,1,0], [1002,0,0.3,0.2,0,0,1,0], [1003,0,0,1,0,1,1,0], [1004,0,2,0,1,0.4,1,3] ]

        Warnings:
            If an array is passed to this method and the another is passed, the previous information will be deleted.

        Args:
            array2d: list|np.ndarray. The array can be a list of list or a two dimensional array of numpy with the type float
            where: "NODES"|"ELEMENTS". The user coordinate systems are for the nodes or the elements.

        Examples:
              >>> array_ele = [ [1001,0,1,0,0,0,1,0], [1002,0,0.3,0.2,0,0,1,0], [1003,0,0,1,0,1,1,0],
              >>> ...           [1004,0,2,0,1,0.4,1,3] ]
              >>> array_node = np.array([ [2001,0,1,0,0,0,1,0], [2002,0,0.3,0.2,0,0,1,0], [2003,0,0,1,0,1,1,0],
              >>> ...           [2004,0,2,0,1,0.4,1,3] ], dtype=float)
              >>>
              >>> N2PModelContent.set_user_coord_sys(array2d=array_ele, where="ELEMENTS")
              >>> N2PModelContent.set_user_coord_sys(array_node, "NODES")
        """

        if isinstance(array2d, list):
            array2d = np.array(array2d)

        rows = array2d.shape[0]
        cols = array2d.shape[1]
        cs_array = System.Array.CreateInstance(System.Object, rows, cols)

        for i in range(rows):
            for j in range(cols):
                cs_array[i, j] = array2d[i, j]

        if where.upper() == "ELEMENTS":
            self.__vzmodel.SetElementUserCoordinateSystems(cs_array)
        elif where.upper() == "NODES":
            self.__vzmodel.SetNodeUserCoordinateSystems(cs_array)
        else:
            msg = N2PLog.Error.E231()
            raise ValueError(msg)

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    #######################################     ElementsCoordSys      ##################################################
    ####################################################################################################################
    def _elements_coord_sys(self):
        if not self.__elements_coord_sys:
            self.__elements_coord_sys = self.__vzmodel.ElementCoordSystem
        return self.__elements_coord_sys
    # ------------------------------------------------------------------------------------------------------------------


    def new_coordinate_system(self, name: str, origin: tuple, v1: tuple, v2: tuple,
        type_coord: Literal["RECTANGULAR", "CILINDRICAL", "SPHERICAL"] = "RECTANGULAR") -> N2PCoord:
        """Returns a :class:`N2PCoord` and add it to the coordinate system list.

        Note:
            The ID of the coordinate system will be set automatically to the last ID + 1 .
        
        Args:
            name: str
                Name of the coordinate system.
            origin: tuple
                tuple with the origin coordinates.
            v1: tuple
                tuple with coordinates of the x vector.
            v2: tuple
                tuple with coordinates of the xy plane vector.
            type_coord: str (optional)
                The posible types are "RECTANGULAR", "CILINDRICAL" or "SPHERICAL". Default is "RECTANGULAR".


        Example:
            >>> mycoord = new_coordinate_system(name="MyCoordinate", origin=(0,0,0), v1=(0.5,0.5,0), v2=(0,1,0))

            >>> new_coordinate_system("MatCoord2", (1,0,-1), (0,0.5,0), (0,0,1), "CILINDRICAL")
            >>> coord_mat = model.get_coords()[-1]
        """
        if type_coord == "RECTANGULAR":
            n2type = N2Coord.TypeCoordSystem.RECTANGULAR
        elif type_coord == "CILINDRICAL":
            n2type = N2Coord.TypeCoordSystem.CILINDRICAL
        elif type_coord == "SPHERICAL":
            n2type = N2Coord.TypeCoordSystem.SPHERICAL
        else:
            raise Exception("Incorrect string for type_coord. It must be 'RECTANGULAR', 'CILINDRICAL' or 'SPHERICAL'")

        org = np.array(origin, dtype=np.double)
        x = np.array(v1, dtype=np.double)
        aux = np.array(v2, dtype=np.double)
        z = np.cross(x, aux)
        y = np.cross(z, x)

        n2coord = N2CoordUserDefined(self.__vzmodel, 1, n2type, org, x/np.linalg.norm(x), y/np.linalg.norm(y), z/np.linalg.norm(z), name)

        pedigree = N2ModelContent.TranslateIdsSolverToPedigree(n2coord.ID, 0)
        self.__vzmodel.userCoordList.Add(pedigree, n2coord)

        n2pcoord = N2PCoord(n2coord, self)

        self.__coord_dict[(n2coord.ID, 0)] = n2pcoord

        return n2pcoord
    # endregion

########################################################################################################################
# region FUNCTION
########################################################################################################################
# Metodo para cargar un objeto N2PModelContent desde un archivo de resultados ------------------------------------------
def initialize(path: str, parallelprocessing: bool = False) -> N2PModelContent:
    """ Deprecated function. This funtion has been substituted by load_model() """
    N2PLog.Warning.W205()

    return load_model(path, parallelprocessing, "Binary")
# ----------------------------------------------------------------------------------------------------------------------


# Metodo para cargar un objeto N2PModelContent desde un archivo de resultados o desde un archivo de texto --------------
def load_model(path: str, parallelprocessing: bool = True,
               file_type: Literal["InputFileNastran", "InputFileAbaqus", "Binary"] = None, 
               dict_gen: dict = None, filter: Literal['ELEMENTS', 'PROPERTIES', 'PARTS', 'NODES'] = None,
               loadconnectors = True) -> N2PModelContent:
    """ Read an output result file in binary format from Nastran, Abaqus, Optistruct or Ansys and transform it into a
    N2PModelContent Object. It also can read models from input files in Nastran format.

    Supports .op2, .xdb, .odb, .h5, .h3d and .rst file extensions read from a local filesystem or URL.

    Supports Nastran Input Files (typically .bdf extension) and Abaqus Input File (typically .inp extension)

    Args:
        path: str.
            Mandatory.
        parallelprocessing: bool.
            Optional. If true, the low libraries open the result files in several processes. It is slightly faster.
        file_type: str.
            Optional. It specifies if it is Nastran input file ("InputFileNastran"), Abaqus input file
            ("InputFileAbaqus") or binary result file ("Binary").
        filter: str.
            Optional. It specifies what to load in dict_gen (elements, properties, parts or nodes)
        dict_gen: dict.
            Optional. Dictionary that represents what elements/properties/parts/nodes to load. For 
            elements and nodes, the dictionary is in the form {Part ID (str): [Elements ID/Nodes ID]}. For parts or 
            properties, the dictionary could simply be in the form {Part ID (str) / Property ID (str): []}. 

    Returns:
        N2PModelContent: Instance with all the model data.

    Examples:
        >>> model1 = load_model(r"C:\\MODELS\\FEM\\model1.dat")

        >>> # file_type is not needed. It only helps the program and saves a checking
        >>> model2 = load_model(r"C:\\MODELS\\FEM\\model2.dat", file_type="InputFileNastran")

        >>> # parallelprocessing is only aviable for Binary files. It is helpful in some big files.
        >>> model3 = load_model(r"C:\\MODELS\\RESULTS\\model1.op2", parallelprocessing=True)

        >>> model4 = load_model(r"C:\\MODELS\\RESULTS\\model2.xdb", file_type="Binary")
        >>> model5 = load_model(r"C:\\MODELS\\RESULTS\\model5.h3d")
        >>> model6 = load_model(r"C:\\MODELS\\RESULTS\\model6.odb", True, "Binary")

        """
    if not os.path.exists(path):
        msg = N2PLog.Critical.C108(path)
        raise FileNotFoundError(msg)

    if path.split(".")[-1] in BINARY_EXTENSIONS and file_type == "InputFileNastran":
        N2PLog.Error.E111()

    if dict_gen and not filter:
        N2PLog.Error.E115()

    return N2PModelContent(path, parallelprocessing, file_type, __transform_dict(dict_gen), filter, loadconnectors=loadconnectors)
# ----------------------------------------------------------------------------------------------------------------------

# Metodo...
def OpenFiletoN2P(n2v_instance: N2ModelContent) -> N2PModelContent:
    """
    Read a :class:`N2ModelContent` object and transform it into a :class:`N2PModelContent` object.

    Args:
        n2v_instance: N2ModelContent.
            Mandatory.
    """
    aux = n2v_instance.CreateNodestoN2P()
    if aux == -1:
        return -1
    else:
        n2v_instance.CreateElementstoN2P()

    return  N2PModelContent(n2v_instance.FilePath, parallelprocessing = True, n2v=n2v_instance)



def _is_binary(path) -> str:
    """Function that returns if the file is a binary or text file"""
    count = 0
    with open(path, 'rb') as f:
        for block in f:
            if b'\x00' in block:
                return "Binary"
            elif any(byte < 9 or (13 < byte < 32) for byte in block):
                return "Binary"
            if count > 100:
                break
            count += 1
    return None

def _check_file_extension(path: str) -> str:
    """Function that checks the file extension and returns the type of file"""
    extension = path.split(".")[-1].lower()
    if extension == "dat" or extension == "bdf":
        return "InputFileNastran"
    elif extension == "fem":
        return "InputFileOptistruct"
    elif extension == "inp":
        return "InputFileAbaqus"
    else:
        N2PLog.Error.E114(path)
        return None

def __transform_dict(dict_gen: dict = None): 

    """
    Function that transforms a Python dictionary in the form dict[str, list[int]] to a C# dictionary in the form 
    dict[Str, Array[Int32]]. If the input is None, then None is returned 
    """
    
    if dict_gen is not None: 
        newDict = System.Collections.Generic.Dictionary[str, System.Array[int]]() 
        for i, j in dict_gen.items(): 
            newDict[i] = System.Array[int](j)
        return newDict
    else: 
        return None 
    
# endregion