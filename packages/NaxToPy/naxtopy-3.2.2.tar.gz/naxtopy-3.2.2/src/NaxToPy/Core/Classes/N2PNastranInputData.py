"""Module with the definition of N2PModelInputData"""
import os
import System
from System.Runtime.CompilerServices import RuntimeHelpers
from typing import Union, overload, Literal

from NaxToPy.Core.Errors.N2PLog import N2PLog

class _LazyList(list):
    """
    A lazy list connected to a LazyDict. The items are lazily instantiated
    from the LazyDict when accessed. It is immutable
    """
    def __init__(self, lazy_dict):
        super().__init__([None] * len(lazy_dict))  # Initialize list with placeholders
        self._lazy_dict = lazy_dict
        self.keys = list(lazy_dict.keys())  # Extract keys from the LazyDict

    def __getitem__(self, index: Union[slice, int]):
        if isinstance(index, int):
            if not (0 <= index < len(self.keys)):
                raise IndexError("list index out of range")
        else:
            if index.stop > len(self.keys):
                raise IndexError("list slice stop out of range")
        
        # Get the key corresponding to the index
        key = self.keys[index]
        value = super().__getitem__(index)

        if value is None:
            # Trigger the LazyDict to create the value
            value = self._lazy_dict[key]
            # Update the list with the created value
            super().__setitem__(index, value)

        return value

    def __setitem__(self, index, value):
        raise TypeError("ListBulkDataCards is immutable")

    def append(self, value):
        raise TypeError("ListBulkDataCards is immutable")

    def extend(self, iterable):
        raise TypeError("ListBulkDataCards is immutable")

    def insert(self, index, value):
        raise TypeError("ListBulkDataCards is immutable")

    def pop(self, index=-1):
        raise TypeError("ListBulkDataCards is immutable")

    def remove(self, value):
        raise TypeError("ListBulkDataCards is immutable")

    def clear(self):
        raise TypeError("ListBulkDataCards is immutable")
    
    def __iter__(self):
        for index in range(len(self.keys)):
            yield self[index]  # Trigger lazy evaluation for each item


class IndexTrackingList(list):
    """Class that is used as a list. It is used because it changes the setitem method of the list class to affect the
    csharp list where the information is actually safe"""
    def __init__(self, iterable=None, csobject=None):
        super().__init__(iterable or [])
        self._csobject = csobject

    def __setitem__(self, index, value):
        self._csobject[index] = value
        super().__setitem__(index, value)


class _N2PField:
    """Class defined only for Typing"""
    def ToReal(self):
        """Converts the Field object of a Table of a N2PCard into a float"""
        pass
    def ToCharacter(self):
        """Converts the Field object of a Table of a N2PCard into a str"""
        pass
    def ToInteger(self):
        """Converts the Field object of a Table of a N2PCard into a int"""
        pass


class N2PInputDataNas:
    """General class for the information in an input file of Nastran
    """

    __slots__ = (
        "__inputdata"
    )

    def __init__(self, inputdata):
        self.__inputdata = inputdata

     
    @property
    def BdfFilePath(self) -> str:
        return self.__inputdata.ParentBdfFile.BdfFilePath
    
    @property
    def BdfFile(self) -> str:
        return self.__inputdata.ParentBdfFile
    
    @property
    def RawContent(self) -> str:
        return self.__inputdata.RawContent
    
    @property
    def SectionInfo(self) -> object:
        return self.__inputdata.SecInfo
    
    def last_status_message(self) -> None:
        """Method that checks if the last operation on the model was successful. If not, it raises an error with the
        message of the last operation."""
        if not self.__inputdata.ParentBdfFile.Model.IsLastOperationRead():
            error = self.__inputdata.ParentBdfFile.Model.GetLastOperationStatusStructured() # OperationResult
            self.__inputdata.ParentBdfFile.Model.SetLastOperationAsRead()  # Reset the status
            if error.StatusMessage:
                N2PLog.Error.E100(error.StatusMessage)


class N2PCard(N2PInputDataNas):
    """Class with the information of a bulk data card of an input file of Nastran.
    """

    __slots__ = ("__card")

    def __init__(self, card):
        super().__init__(card)
        self.__card = card

    @property
    def CardType(self) -> str:
        return self.__card.CardType
    
    @property
    def IsDeleted(self) -> bool:
        return self.__card.IsDeleted
    
    @property
    def IsSynthetic(self) -> bool:
        return self.__card.IsSynthetic
    
    @property
    def IsCommented(self) -> bool:
        return self.__card.IsCommented
    
    @property
    def FieldsFormat(self) -> str:
        return self.__card.FieldsFormat

    @property
    def MappingSuccessful(self) -> bool:
        return self.__card.MappingSuccessful

    def comment_card(self) -> None:
        """Comments the card adding a $ when writing the files"""
        self.__card.CommentCard()
        # self.last_status_message()

    def uncomment_card(self) -> None:
        """Uncomment a card previously commented"""
        self.__card.UncommentCard()
        # self.last_status_message()

    def delete_card(self) -> None:
        """Deletes a card. The reference still exists in NaxToPy but it will no be writen"""
        self.__card.DeleteCard()
        # self.last_status_message()

    def restore_card(self) -> None:
        """Restores a card previously deleted"""
        self.__card.RestoreCard()
        self.last_status_message()

    def print_fixed_format_table(self) -> str:
        """Prints a formatted string representation visualizing the *field definitions* (names and indices)"""
        print(self.__card.PrintFixedFormatTable())

    def print_field_definition_table(self) -> str:
        """Prints the value of a specific card field by its position (row, column)
        in the conceptual NASTRAN Fixed Format Table."""
        print(self.__card.PrintFieldDefinitionTable())

    def get_field_value_by_position(self, row:int, column:int) -> object:
        """Gets the value from a card in the desire position. Index start in 1.

        Example:
            >>> # card is GRID, so in the row 1 and column 2 the id is placed
            >>> id_ = card.get_field_value_by_position(1, 2)
        """
        return self.__card.GetFieldValueByPosition(row, column)

    def set_field_value_by_position(self, row:int, column:int, new_value: object) -> None:
        """Sets the value from a card in the desire position. Index start in 1.

        Example:
            >>> # card is GRID, so in the row 1 and column 2 the id is placed
            >>> card.set_field_value_by_position(1, 2, 1001)
        """
        self.__card.SetFieldValueByPosition(row, column, new_value)
        self.last_status_message()

    def get_superelement_id(self) -> int:
        """Gets the part id of the card. If the card is not in a superelement, it returns 0"""
        return self.__card.GetSuperElement()


class N2PNastranInputData:
    """Class with the complete data of a MEF input file (text file).

    Note:
        The property :class:`N2PModelContent.ModelInputData` can be a :class:`N2PNastranInputData` if the input file is from
        Nastran (.bdf) or Opstitruct (.fem), or a :class:`N2PAbaqusInputData` (.inp) if is from Abaqus.

    Example:
        >>> model = n2p.load_model("my_nastran_input_file.bdf")
        >>> inputdata = model.ModelInputData  # This is a N2PNastranInputData
    """
    __slots__ = (
        "__dictcardscston2p",
        "__inputfiledata",
        "__casecontrolinstructions",
        "__executivecontrolinstructions",
        "__listcomments",
        "__lazylist",
        "__bdfFiles"
    )

    def __init__(self, dictcardscston2p: dict, inputfiledata):
        self.__dictcardscston2p = dictcardscston2p
        self.__inputfiledata = inputfiledata
        self.__casecontrolinstructions = []
        self.__executivecontrolinstructions = []
        self.__listcomments = []
        self.__lazylist = None
        self.__bdfFiles = {bdf.BdfFilePath: bdf for bdf in inputfiledata.BdfFiles}

    @property
    def ListBulkDataCards(self) -> list[N2PCard]:
        """List with the N2PCard objects of the input FEM file. It has all bulk data cards of the model"""

        # We actually return a LazyList, conected to the LazyDict of cards. Only when a card is required is instantiated
        if self.__lazylist is None:
            self.__lazylist = _LazyList(self.__dictcardscston2p)

        return self.__lazylist

    @property
    def GetAbsolutePathsOfBdfFiles(self) -> list[str]:
        """List with theabsolute file paths of all BDF files that compose this model"""
        return list(self.__inputfiledata.GetAbsolutePathsOfBdfFiles())

    # @property
    # def TypeOfFile(self) -> str:
    #     """Type of file read. It may be "NASTRAN" or "OPTISTRUCT" ."""
    #     return self.__inputfiledata.TypeOfFile.ToString()

    @property
    def CaseControlInstructions(self) -> list[N2PInputDataNas]:
        """List with the instructions of the model. They are the commands above the BEGIN BULK: Executive Control
        Statements and Control Case Commands"""
        if self.__casecontrolinstructions:
            return self.__casecontrolinstructions
        else:
            self.__casecontrolinstructions = [N2PInputDataNas(i) for i in self.__inputfiledata.CaseControlSection.GetInputDataList()]
            return self.__casecontrolinstructions
        
    @property
    def ExecutiveControlInstructions(self) -> list[N2PInputDataNas]:
        """List with the instructions of the model. They are the commands above the BEGIN BULK: Executive Control
        Statements and Control Case Commands"""
        if self.__executivecontrolinstructions:
            return self.__executivecontrolinstructions
        else:
            self.__executivecontrolinstructions = [N2PInputDataNas(i) for i in self.__inputfiledata.ExecutiveControlSection.GetInputDataList()]
            return self.__executivecontrolinstructions

    @property
    def ListInstructions(self) -> list[N2PInputDataNas]:
        """List with the instructions of the model. They are the commands above the BEGIN BULK: Executive Control
        Statements and Control Case Commands"""
        return self.CaseControlInstructions + self.ExecutiveControlInstructions

    # TODO
    # @property
    # def ListComments(self) -> list[N2PInputDataNas]:
    #     """List with all the comments in the FEM Input File"""
    #     if self.__listcomments:
    #         return self.__listcomments
    #     else:
    #         self.__listcomments = [N2PInputDataNas(i) for i in self.__inputfiledata.StructuredInfo.ModelComments]
    #         return self.__listcomments
        
    def find_cards(self, superElements: int,
                   category: Literal["GRID", "ELEMENT", "CONNECTOR", "PROPERTY", "MATERIAL", "COORDINATESYSTEM", "LOAD", "CONSTRAINT"],
                   cardTypes: list[str] = None, filters: dict[str, object] = None) -> list [N2PCard]:
        """Searches for cards based on specified criteria:
        
            - superElements (mandatory): integer number of 8 bits (1 byte)
            - category (mandatory): Element, property, material, etc
            - cardTypes (optional): Specific type of card: CQUAD4, PBEAM, COORD2R
            - filters (optional): Each category has common fields. It is possible to filter acordinf to those fields.
                - GRID: "ID", "CP", "CD", "PS", "SEID", "X1", "X2", "X3"
                - ELEMENT: "EID,  "PID", "NodeArray"
                - CONNECTOR: 
                - PROPERTY: "PID"
                - MATERIAL: "MID"
                - COORDINATESYSTEM: "CoordinateSystemIds", "ReferenceSystemId"
                - LOAD:
                - CONSTRAINT:

        Example:

            >>> grids = model.ModelInputData.find_cards(0, "GRID")
            >>> cuads = model.ModelInputData.find_cards(0, "ELEMENT", ["CQUAD4"])
            >>> pshell_3 = model.ModelInputData.find_cards(0, "PROPERTY", ["PSHELL"], {"PID": 3})
            >>> grids_cp10 = model.ModelInputData.find_cards(0, "GRID", None, {"CP": 10})
        """
        # Convert superElements (part id) to System.Byte[] (or None)
        if not superElements and superElements != 0:
            part = None
        elif isinstance(superElements, int):
            # Wrap single integer in a byte array
            part = System.Array[System.Byte]([System.Byte(superElements)])
        else:
            # Convert list-like input to byte array
            try:
                byte_list = [System.Byte(e) for e in superElements]
                part = System.Array[System.Byte](byte_list)
            except Exception as ex:
                raise ValueError(f"Invalid element in superElements for byte[]: {ex}")

        if filters:
            try:
                # Convert dictionary keys to string[]
                filter_names = System.Array[System.String](list(filters.keys()))

                # Convert dictionary values to object[] with correct .NET types
                values = []

                type_map = {
                    int: System.Int32,
                    str: System.String,
                    float: System.Single,
                }

                for k, v in filters.items():
                    converter = type_map.get(type(v))
                    if converter:
                        values.append(converter(v))
                    else:
                        raise TypeError(f"Unsupported filter value type: key={k}, value={v} (type={type(v).__name__})")

                filter_values = System.Array[System.Object](values)

            except Exception as ex:
                raise ValueError(f"Error processing filters: {ex}")
        else:
            filter_names = None
            filter_values = None

        cs_result = self.__inputfiledata.BulkDataSection.FindCards(part, category, cardTypes, filter_names, filter_values)

        return [self.__dictcardscston2p[RuntimeHelpers.GetHashCode(i)] for i in cs_result]

        
    def print_include_hierarchy(self) -> None:
        """
        Function that prints in the console the hierarchy of includes of a Nastran input file.
        """

        self.__inputfiledata.PrintIncludeHierarchy()
        return None
        
    def print_model_directory_structure(self) -> None:
        """
        Function that prints in the console the directory structure of a Nastran input file.
        """

        self.__inputfiledata.PrintModelDirectoryStructure()
        return None


    def get_cards_by_field(self, fields: list[str, ], row: int = 0, col: int = 0) -> list[N2PCard, ]:
        """ATTENTION: Deprecated method in version 3.2.0. Use find_cards() instead.
        """
        N2PLog.Warning.W110("get_cards_by_field", "find_cards")

        raise Exception("This method has been removed in version 3.2.0. Use find_cards() instead.")
    

    def rebuild_file(self, folder: str) -> None:
        """Method that writes the solver input file with the same file structure that was read in the folder is specified

        Args:
            folder: str -> Path of the folder where the file or files will be written.
        """
        if os.path.isdir(folder):
            self.__inputfiledata.RebuildModel(folder)
        else:
            N2PLog.Error.E401(folder)

    def get_failed_cards(self) -> list["N2PCard"]:
        """Method that returns a list with the N2PCard objects of the input FEM file that have not been mapped correctly."""
        failed_cards = []
        for card in self.ListBulkDataCards:
            if card is not None and card.MappingSuccessful is False:
                failed_cards.append(card)
                if not self.__inputfiledata.IsLastOperationRead():
                    error = self.__inputfiledata.GetLastOperationStatusStructured() # OperationResult
                    self.__inputfiledata.SetLastOperationAsRead()  # Reset the status
                    N2PLog.Error.E100(error.StatusMessage)
        return failed_cards

    def create_card(self, card_type: str, bdf_file: str, rawContent: str = None, superElemntId:int = 0) -> N2PCard:
        """Method that creates a new card of the type specified. By default, the card is created empty, with small field format.
        
        Example:
            >>> new_cbar = model.ModelInputData.create_card("CBAR", "C:\\bdf\\mesh\\model.bdf")
            >>> # new_cbar is now a N2PCard object of type CBAR empty. You can set its properties:
            >>> new_cbar.EID = 1001
            >>> new_cbar.PID = 2001
            >>> new_cbar.GA = 10
            >>> new_cbar.GB = 20
            >>> new_cbar.X1 = 1.0
            >>> new_cbar.X2 = 0.0
            >>> new_cbar.X3 = 0.0

            >>> # It is also possible to create a card with raw content and specifying the superelement id:
            >>> raw_content = "CBAR        1002    2001      30      40     0.0     1.0     0.0"
            >>> new_cbar2 = model.ModelInputData.create_card("CBAR", "C:\\bdf\\mesh\\model.bdf", rawContent=raw_content, superElemntId=0)

        """
        bdfFileObject = self.__bdfFiles.get(bdf_file, None)
        if bdfFileObject is None:
            N2PLog.Warning.W212(bdf_file)
            bdfFileObject = self.__inputfiledata.BdfFiles[0]
        card = self.__inputfiledata.BulkDataSection.CreateCard(card_type, bdfFileObject, rawContent, superElemntId)
        card.CardType = card_type
        card.FieldsFormat = "SMALL"

        return card

class N2PModelInputData(N2PNastranInputData):
    """Deprecated class. To maintain its functionality it works as the new class N2PNastranInputData"""
    def __init__(self, *args, **kwargs):
        N2PLog.Warning.W207()
        super().__init__(*args, **kwargs)


class CBAR(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Unique element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """ Property identification number of a PBAR or PBARL entry. (Integer > 0 or blank*; Default = EID unless BAROR entry has nonzero entry in field 3.)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def GA(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integer > 0; GA ≠ GB)
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value
        self.last_status_message()

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value
        self.last_status_message()

    @property
    def X1(self) -> float:
        """
           Components of orientation vector v, from GA, in the displacement coordinate system at GA(default), or in the basic coordinate system.See Remark 8. (Real)
           * Remark 8:
           OFFT is a character string code that describes how the offset and orientation vector components are to be interpreted.By default (string input is GGG or
           blank), the offset vectors are measured in the displacement coordinate systems at grid points A and B and the orientation vector is measured in the
           displacement coordinate system of grid point A.At user option, the offset vectors can be measured in an offset coordinate system relative to grid points
           A and B, and the orientation vector can be measured in the basic system as indicated in the following table:
           String    Orientation Vector     End A Offset     End B Offset
           GGG       Global                 Global           Global
           BGG       Basic                  Global           Global
           GGO       Global                 Global           Basic
           BGO       Basic                  Global           Basic
           GOG       Global                 Offset           Global
           BOG       Basic                  Offset           Global
           GOO       Global                 Offset           Basic
           BOO       Basic                  Offset           Basic
        """
        return self.__cardinfo.X1

    @X1.setter
    def X1(self, value: float) -> None:
        self.__cardinfo.X1 = value
        self.last_status_message()

    @property
    def X2(self) -> float:
        """
           X2
        """
        return self.__cardinfo.X2

    @X2.setter
    def X2(self, value: float) -> None:
        self.__cardinfo.X2 = value
        self.last_status_message()

    @property
    def X3(self) -> float:
        """
           X3
        """
        return self.__cardinfo.X3

    @X3.setter
    def X3(self, value: float) -> None:
        self.__cardinfo.X3 = value
        self.last_status_message()

    @property
    def G0(self) -> int:
        """
           Alternate method to supply the orientation vector v using grid point G0.The direction of v is from GA to G0.v is then translated to End A. (Integer > 0; G0 ≠ GA or GB)
        """
        return self.__cardinfo.G0

    @G0.setter
    def G0(self, value: int) -> None:
        self.__cardinfo.G0 = value
        self.last_status_message()

    @property
    def OFFT(self) -> str:
        """
           Offset vector interpretation flag. (character or blank) See Remark 8.
           * Remark 8:
           OFFT is a character string code that describes how the offset and orientation vector components are to be interpreted. By default, (string input is GGG or
           blank), the offset vectors are measured in the displacement coordinate systems at grid points A and B and the orientation vector is measured in the
           displacement coordinate system of grid point A.At user option, the offset vectors can be measured in an offset coordinate system relative to grid points
           A and B, and the orientation vector can be measured in the basic system as indicated in the following table:
           String    Orientation Vector     End A Offset     End B Offset
           GGG       Global                 Global           Global
           BGG       Basic                  Global           Global
           GGO       Global                 Global           Basic
           BGO       Basic                  Global           Basic
           GOG       Global                 Offset           Global
           BOG       Basic                  Offset           Global
           GOO       Global                 Offset           Basic
           BOO       Basic                  Offset           Basic
        """
        return self.__cardinfo.OFFT

    @OFFT.setter
    def OFFT(self, value: str) -> None:
        self.__cardinfo.OFFT = value
        self.last_status_message()

    @property
    def PA(self) -> int:
        """
           Pin flags for bar ends A and B, respectively. Used to remove connections between the grid point and selected degrees-offreedom of the bar.The degrees-of-freedom
           are defined in the element’s coordinate system (see Figure 8-8). The bar must have stiffness associated with the PA and PB degrees-of-freedom to be
           released by the pin flags. For example, if PA = 4 is specified, the PBAR entry must have a value for J, the torsional stiffness. (Up to 5 of the unique
           Integers 1 through 6 anywhere in the field with no embedded blanks; Integer > 0.) Pin flags combined with offsets are not allowed for SOL 600.
        """
        return self.__cardinfo.PA

    @PA.setter
    def PA(self, value: int) -> None:
        self.__cardinfo.PA = value
        self.last_status_message()

    @property
    def PB(self) -> int:
        """
           PB
        """
        return self.__cardinfo.PB

    @PB.setter
    def PB(self, value: int) -> None:
        self.__cardinfo.PB = value
        self.last_status_message()

    @property
    def W1A(self) -> float:
        """
           Components of offset vectors and, respectively (see Figure 8-8) in displacement coordinate systems(or in element system depending upon the content of the OFFT
           field), at points GA and GB, respectively. See Remark 7. and 8. (Real; Default = 0.0)
           * Remark 7:
           Offset vectors are treated like rigid elements and are therefore subject to the same limitations.
           • Offset vectors are not affected by thermal loads.
           • The specification of offset vectors is not recommended in solution sequences that compute differential stiffness because the offset vector
           remains parallel to its original orientation. (Differential stiffness is computed in buckling analysis provided in SOLs 103 and 107 through 112 with the
           STATSUB command; and also in nonlinear analysis provided in SOLs 106, 129, 153, and 159 with PARAM, LGDISP,1.)
           • BAR elements with offsets will give wrong buckling results.
           • Masses are not offset for shells.
           • The nonlinear solution in SOL 106 uses differential stiffness due for the iterations to reduce equilibrium errors.An error in the differential stiffness
           due to offsets may cause the iterations to converge slowly or to diverge. If the solution converges the answer is correct, even though there may be an
           error in the differential stiffness.However, the special capabilities in SOL 106 to get vibration and buckling modes will produce wrong answers if the
           differential stiffness is bad.
           • The internal “rigid elements” for offset BAR/BEAM elements are rotated in the nonlinear force calculations. Thus, if convergence is achieved, BAR/BEAM
           elements may be used in SOL 106 with LGDISP,1.
           * Remark 8:
           OFFT is a character string code that describes how the offset and orientation vector components are to be interpreted.By default (string input is GGG or
           blank), the offset vectors are measured in the displacement coordinate systems at grid points A and B and the orientation vector is measured in the
           displacement coordinate system of grid point A. At user option, the offset vectors can be measured in an offset coordinate system relative to grid points
           A and B, and the orientation vector can be measured in the basic system as indicated in the following table:
           String    Orientation Vector     End A Offset     End B Offset
           GGG       Global                 Global           Global
           BGG       Basic                  Global           Global
           GGO       Global                 Global           Basic
           BGO       Basic                  Global           Basic
           GOG       Global                 Offset           Global
           BOG       Basic                  Offset           Global
           GOO       Global                 Offset           Basic
           BOO       Basic                  Offset           Basic
        """
        return self.__cardinfo.W1A

    @W1A.setter
    def W1A(self, value: float) -> None:
        self.__cardinfo.W1A = value
        self.last_status_message()

    @property
    def W2A(self) -> float:
        """
           W2A
        """
        return self.__cardinfo.W2A

    @W2A.setter
    def W2A(self, value: float) -> None:
        self.__cardinfo.W2A = value
        self.last_status_message()

    @property
    def W3A(self) -> float:
        """
           W3A
        """
        return self.__cardinfo.W3A

    @W3A.setter
    def W3A(self, value: float) -> None:
        self.__cardinfo.W3A = value
        self.last_status_message()

    @property
    def W1B(self) -> float:
        """
           W1B
        """
        return self.__cardinfo.W1B

    @W1B.setter
    def W1B(self, value: float) -> None:
        self.__cardinfo.W1B = value
        self.last_status_message()

    @property
    def W2B(self) -> float:
        """
           W2B
        """
        return self.__cardinfo.W2B

    @W2B.setter
    def W2B(self, value: float) -> None:
        self.__cardinfo.W2B = value
        self.last_status_message()

    @property
    def W3B(self) -> float:
        """
           W3B
        """
        return self.__cardinfo.W3B

    @W3B.setter
    def W3B(self, value: float) -> None:
        self.__cardinfo.W3B = value
        self.last_status_message()


class CBEAM(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Unique element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of PBEAM, PBCOMP or PBEAML entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def GA(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integer > 0; GA ≠ GB)
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value
        self.last_status_message()

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value
        self.last_status_message()

    @property
    def X1(self) -> float:
        """
           Components of orientation vector v, from GA, in the displacement coordinate system at GA(default), or in the basic coordinate system.See Remark 9. (Real)
           * Remark 9:
           If the element is a p-version element, BIT in field 9 contains the value of the built-in-twist measured in radians.Otherwise, OFFT in field 9 is a character
           string code that describes how the offset and orientation vector components are to be interpreted.By default (string input is GGG or blank), the offset
           vectors are measured in the displacement coordinate systems at grid points A and B and the orientation vector is measured in the displacement
           coordinate system of grid point A.At user option, the offset vectors can be measured in an offset system relative to grid points A and B, and the
           orientation vector can be measured in the basic system as indicated in the following table:
           String    Orientation Vector     End A Offset     End B Offset
           GGG       Global                 Global           Global
           BGG       Basic                  Global           Global
           GGO       Global                 Global           Offset
           BGO       Basic                  Global           Offset
           GOG       Global                 Offset           Global
           BOG       Basic                  Offset           Global
           GOO       Global                 Offset           Offset
           BOO       Basic                  Offset           Offset
        """
        return self.__cardinfo.X1

    @X1.setter
    def X1(self, value: float) -> None:
        self.__cardinfo.X1 = value
        self.last_status_message()

    @property
    def X2(self) -> float:
        """
           X2
        """
        return self.__cardinfo.X2

    @X2.setter
    def X2(self, value: float) -> None:
        self.__cardinfo.X2 = value
        self.last_status_message()

    @property
    def X3(self) -> float:
        """
           X3
        """
        return self.__cardinfo.X3

    @X3.setter
    def X3(self, value: float) -> None:
        self.__cardinfo.X3 = value
        self.last_status_message()

    @property
    def G0(self) -> int:
        """
           Alternate method to supply the orientation vector v using grid point G0.The direction of v is from GA to G0.v is then transferred to End A. (Integer > 0; G0 ≠ GA or GB)
        """
        return self.__cardinfo.G0

    @G0.setter
    def G0(self, value: int) -> None:
        self.__cardinfo.G0 = value
        self.last_status_message()

    @property
    def OFFT(self) -> str:
        """
           Offset vector interpretation flag. (character or blank) See Remark 9.
           * Remark 9:
           If the element is a p-version element, BIT in field 9 contains the value of the built-in-twist measured in radians.Otherwise, OFFT in field 9 is a character
           string code that describes how the offset and orientation vector components are to be interpreted.By default (string input is GGG or blank), the offset
           vectors are measured in the displacement coordinate systems at grid points A and B and the orientation vector is measured in the displacement
           coordinate system of grid point A.At user option, the offset vectors can be measured in an offset system relative to grid points A and B, and the
           orientation vector can be measured in the basic system as indicated in the following table:
           String    Orientation Vector     End A Offset     End B Offset
           GGG       Global                 Global           Global
           BGG       Basic                  Global           Global
           GGO       Global                 Global           Offset
           BGO       Basic                  Global           Offset
           GOG       Global                 Offset           Global
           BOG       Basic                  Offset           Global
           GOO       Global                 Offset           Offset
           BOO       Basic                  Offset           Offset
        """
        return self.__cardinfo.OFFT

    @OFFT.setter
    def OFFT(self, value: str) -> None:
        self.__cardinfo.OFFT = value
        self.last_status_message()

    @property
    def PA(self) -> int:
        """
           Pin flags for beam ends A and B, respectively. Used to remove connections between the grid point and selected degrees-offreedom of the bar. The degrees-of-freedom
           are defined in the element’s coordinate system (see Figure 8-12). The beam must have stiffness associated with the PA and PB degrees-of-freedom to be
           released by the pin flags.For example, if PA = 4 is specified, the PBEAM entry must have a value for J, the torsional stiffness. (Up to 5 of the unique
           Integers 1 through 6 anywhere in the field with no embedded blanks; Integer > 0.) Pin flags combined with offsets are not allowed for SOL 600.
        """
        return self.__cardinfo.PA

    @PA.setter
    def PA(self, value: int) -> None:
        self.__cardinfo.PA = value
        self.last_status_message()

    @property
    def PB(self) -> int:
        """
           PB
        """
        return self.__cardinfo.PB

    @PB.setter
    def PB(self, value: int) -> None:
        self.__cardinfo.PB = value
        self.last_status_message()

    @property
    def W1A(self) -> float:
        """
           Components of offset vectors and , respectively (see Figure 8-8) in displacement coordinate systems(or in element system depending upon the content of the OFFT
           field), at points GA and GB, respectively. See Remark 7. and 8. (Real; Default = 0.0)
           * Remark 7:
           Offset vectors are treated like rigid elements and are therefore subject to the same limitations.
           • Offset vectors are not affected by thermal loads.
           • The specification of offset vectors is not recommended in solution sequences that compute differential stiffness because the offset vector
           remains parallel to its original orientation. (Differential stiffness is computed in buckling analysis provided in SOLs 103 and 107 through 112 with the
           STATSUB command; and also in nonlinear analysis provided in SOLs 106, 129, 153, and 159 with PARAM, LGDISP,1.)
           • BAR elements with offsets will give wrong buckling results.
           • Masses are not offset for shells.
           • The nonlinear solution in SOL 106 uses differential stiffness due for the iterations to reduce equilibrium errors.An error in the differential stiffness
           due to offsets may cause the iterations to converge slowly or to diverge. If the solution converges the answer is correct, even though there may be an
           error in the differential stiffness.However, the special capabilities in SOL 106 to get vibration and buckling modes will produce wrong answers if the
           differential stiffness is bad.
           • The internal “rigid elements” for offset BAR/BEAM elements are rotated in the nonlinear force calculations.Thus, if convergence is achieved, BAR/BEAM
           elements may be used in SOL 106 with LGDISP,1.
           * Remark 8:
           OFFT is a character string code that describes how the offset and orientation vector components are to be interpreted.By default (string input is GGG or
           blank), the offset vectors are measured in the displacement coordinate systems at grid points A and B and the orientation vector is measured in the
           displacement coordinate system of grid point A.At user option, the offset vectors can be measured in an offset coordinate system relative to grid points
           A and B, and the orientation vector can be measured in the basic system as indicated in the following table:
           String    Orientation Vector     End A Offset     End B Offset
           GGG       Global                 Global           Global
           BGG       Basic                  Global           Global
           GGO       Global                 Global           Basic
           BGO       Basic                  Global           Basic
           GOG       Global                 Offset           Global
           BOG       Basic                  Offset           Global
           GOO       Global                 Offset           Basic
           BOO       Basic                  Offset           Basic
        """
        return self.__cardinfo.W1A

    @W1A.setter
    def W1A(self, value: float) -> None:
        self.__cardinfo.W1A = value
        self.last_status_message()

    @property
    def W2A(self) -> float:
        """
           W2A
        """
        return self.__cardinfo.W2A

    @W2A.setter
    def W2A(self, value: float) -> None:
        self.__cardinfo.W2A = value
        self.last_status_message()

    @property
    def W3A(self) -> float:
        """
           W3A
        """
        return self.__cardinfo.W3A

    @W3A.setter
    def W3A(self, value: float) -> None:
        self.__cardinfo.W3A = value
        self.last_status_message()

    @property
    def W1B(self) -> float:
        """
           W1B
        """
        return self.__cardinfo.W1B

    @W1B.setter
    def W1B(self, value: float) -> None:
        self.__cardinfo.W1B = value
        self.last_status_message()

    @property
    def W2B(self) -> float:
        """
           W2B
        """
        return self.__cardinfo.W2B

    @W2B.setter
    def W2B(self, value: float) -> None:
        self.__cardinfo.W2B = value
        self.last_status_message()

    @property
    def W3B(self) -> float:
        """
           W3B
        """
        return self.__cardinfo.W3B

    @W3B.setter
    def W3B(self, value: float) -> None:
        self.__cardinfo.W3B = value
        self.last_status_message()

    @property
    def SA(self) -> int:
        """
           Scalar or grid point identification numbers for the ends A and B, respectively.The degrees-of-freedom at these points are the warping variables dθ ⁄ dx.
           SA and SB cannot be specified for beam p-elements. (Integers > 0 or blank)
        """
        return self.__cardinfo.SA

    @SA.setter
    def SA(self, value: int) -> None:
        self.__cardinfo.SA = value
        self.last_status_message()

    @property
    def SB(self) -> int:
        """
           SB
        """
        return self.__cardinfo.SB

    @SB.setter
    def SB(self, value: int) -> None:
        self.__cardinfo.SB = value
        self.last_status_message()


class CBUSH(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PBUSH entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def GA(self) -> int:
        """
           CardGrid point identification number of connection points. See Remark 6. (Integer > 0)
           * Remark 6:
           If the distance between GA and GB is less than .0001, or if GB is blank, then CID must be specified.GB blank implies that B is grounded.
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value
        self.last_status_message()

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value
        self.last_status_message()

    @property
    def X1(self) -> float:
        """
           Components of orientation vector v, from GA, in the displacement coordinate system at GA. (Real)
        """
        return self.__cardinfo.X1

    @X1.setter
    def X1(self, value: float) -> None:
        self.__cardinfo.X1 = value
        self.last_status_message()

    @property
    def X2(self) -> float:
        """
           X2
        """
        return self.__cardinfo.X2

    @X2.setter
    def X2(self, value: float) -> None:
        self.__cardinfo.X2 = value
        self.last_status_message()

    @property
    def X3(self) -> float:
        """
           X3
        """
        return self.__cardinfo.X3

    @X3.setter
    def X3(self, value: float) -> None:
        self.__cardinfo.X3 = value
        self.last_status_message()

    @property
    def G0(self) -> int:
        """
           Alternate method to supply vector v using grid point GO. Direction of v is from GA to GO. v is then transferred to End A.See Remark 3. (Integer > 0)
           * Remark 3:
           CID > 0 overrides GO and Xi. Then the element x-axis is along T1, the element y-axis is along T2, and the element z-axis is along T3 of the CID
           coordinate system.If the CID refers to a cylindrical coordinate system or as pherical coordinate system, then grid GA is used to locate the system. If for
           cylindrical or spherical coordinate, GA falls on the z-axis used to define them, it is recommended that another CID be selectfced to define the element x-axis.
        """
        return self.__cardinfo.G0

    @G0.setter
    def G0(self, value: int) -> None:
        self.__cardinfo.G0 = value
        self.last_status_message()

    @property
    def CID(self) -> int:
        """
           Element coordinate system identification. A 0 means the basic coordinate system.If CID is blank, then the element coordinate system is determined from
           GO or Xi.See Figure 8-19 and Remark 3. (Integer > 0 or blank)
           * Remark 3:
           CID > 0 overrides GO and Xi. Then the element x-axis is along T1, the element y-axis is along T2, and the element z-axis is along T3 of the CID
           coordinate system.If the CID refers to a cylindrical coordinate system or as pherical coordinate system, then grid GA is used to locate the system. If for
           cylindrical or spherical coordinate, GA falls on the z-axis used to define them, it is recommended that another CID be selectfced to define the element x-axis.
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value
        self.last_status_message()

    @property
    def S(self) -> float:
        """
           Location of spring damper. See Figure 8-19. (0.0 < Real < 1.0; Default = 0.5)
        """
        return self.__cardinfo.S

    @S.setter
    def S(self, value: float) -> None:
        self.__cardinfo.S = value
        self.last_status_message()

    @property
    def OCID(self) -> int:
        """
           Coordinate system identification of spring-damper offset. See Remark 9. (Integer > -1; Default = -1, which means the offset point lies on the line
           between GA and GB according to Figure 8-19)
           * Remark 9:
           If OCID = -1 or blank (default) then S is used and S1, S2, S3 are ignored. If OCID > 0, then S is ignored and S1, S2, S3 are used.
        """
        return self.__cardinfo.OCID

    @OCID.setter
    def OCID(self, value: int) -> None:
        self.__cardinfo.OCID = value
        self.last_status_message()

    @property
    def S1(self) -> float:
        """
           Components of spring-damper offset in the OCID coordinate system if OCID > 0. See Figure 8-20 and Remark 9. (Real)
           * Remark 9:
           If OCID = -1 or blank (default) then S is used and S1, S2, S3 are ignored. If OCID > 0, then S is ignored and S1, S2, S3 are used.
        """
        return self.__cardinfo.S1

    @S1.setter
    def S1(self, value: float) -> None:
        self.__cardinfo.S1 = value
        self.last_status_message()

    @property
    def S2(self) -> float:
        """
           S2
        """
        return self.__cardinfo.S2

    @S2.setter
    def S2(self, value: float) -> None:
        self.__cardinfo.S2 = value
        self.last_status_message()

    @property
    def S3(self) -> float:
        """
           S3
        """
        return self.__cardinfo.S3

    @S3.setter
    def S3(self, value: float) -> None:
        self.__cardinfo.S3 = value
        self.last_status_message()


class CELAS1(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Unique element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PELAS entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           Geometric grid point identification number. (Integer >= 0)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()

    @property
    def C1(self) -> int:
        """
           Component number. (0 < Integer < 6; blank or zero if scalar point.)
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: int) -> None:
        self.__cardinfo.C1 = value
        self.last_status_message()

    @property
    def C2(self) -> int:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: int) -> None:
        self.__cardinfo.C2 = value
        self.last_status_message()


class CELAS2(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Unique element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def K(self) -> float:
        """
           Stiffness of the scalar spring. (Real)
        """
        return self.__cardinfo.K

    @K.setter
    def K(self, value: float) -> None:
        self.__cardinfo.K = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           Geometric grid point identification number. (Integer >= 0)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()

    @property
    def C1(self) -> int:
        """
           Component number. (0 < Integer < 6; blank or zero if scalar point.)
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: int) -> None:
        self.__cardinfo.C1 = value
        self.last_status_message()

    @property
    def C2(self) -> int:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: int) -> None:
        self.__cardinfo.C2 = value
        self.last_status_message()

    @property
    def GE(self) -> float:
        """
           Damping coefficient. See Remarks 6. and 8. (Real)
           * Remark 6:
           If PARAM,W4 is not specified, GE is ignored in transient analysis. See “Parameters” on page 631.
           * Remark 8:
           To obtain the damping coefficient GE, multiply the critical damping ratio C ⁄ C0 by 2.0.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value
        self.last_status_message()

    @property
    def S(self) -> float:
        """
           Stress coefficient (Real).
        """
        return self.__cardinfo.S

    @S.setter
    def S(self, value: float) -> None:
        self.__cardinfo.S = value
        self.last_status_message()


class CELAS3(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Unique element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PELAS entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def S1(self) -> int:
        """
           Scalar point identification numbers. (Integer >= 0)
        """
        return self.__cardinfo.S1

    @S1.setter
    def S1(self, value: int) -> None:
        self.__cardinfo.S1 = value
        self.last_status_message()

    @property
    def S2(self) -> int:
        """
           S2
        """
        return self.__cardinfo.S2

    @S2.setter
    def S2(self, value: int) -> None:
        self.__cardinfo.S2 = value
        self.last_status_message()


class CELAS4(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Unique element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def K(self) -> float:
        """
           Stiffness of the scalar spring. (Real)
        """
        return self.__cardinfo.K

    @K.setter
    def K(self, value: float) -> None:
        self.__cardinfo.K = value
        self.last_status_message()

    @property
    def S1(self) -> int:
        """
           Scalar point identification numbers. (Integer >= 0; S1 ≠ S2)
        """
        return self.__cardinfo.S1

    @S1.setter
    def S1(self, value: int) -> None:
        self.__cardinfo.S1 = value
        self.last_status_message()

    @property
    def S2(self) -> int:
        """
           S2
        """
        return self.__cardinfo.S2

    @S2.setter
    def S2(self, value: int) -> None:
        self.__cardinfo.S2 = value
        self.last_status_message()


class CFAST(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PFAST entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def TYPE(self) -> str:
        """
           Specifies the surface patch definition: (Character)
           If TYPE = ‘PROP’, the surface patch connectivity between patch A and patch B is defined with two PSHELL(or PCOMP) properties with property ids given by
           IDA and IDB.See Remark 1. and Figure 8-22.
           If TYPE = ‘ELEM’, the surface patch connectivity between patch A and patch B is defined with two shell element ids given by IDA and IDB.See Remark 1. and
           Figure 8-22.
           * Remark 1:
           The CardCfast defines a flexible connection between two surface patches. Depending on the location for the piercing points GA and GB, and the size of the diameter
           D(see PFAST), the number of unique physical grids per patch ranges from a possibility of 3 to 16 grids. (Currently there is a limitation that there can be only
           a total of 16 unique grids in the upper patch and only a total of 16 unique grids in the lower patch.Thus, for example, a patch can not hook up to
           four CQUAD8 elements with midside nodes and no nodes in common between each CQUAD8 as that would total to 32 unique grids for the patch.)
        """
        return self.__cardinfo.TYPE

    @TYPE.setter
    def TYPE(self, value: str) -> None:
        self.__cardinfo.TYPE = value
        self.last_status_message()

    @property
    def IDA(self) -> int:
        """
           Property id (for PROP option) or Element id (for ELEM option) defining patches A and B. IDA ≠ IDB (Integer > 0)
        """
        return self.__cardinfo.IDA

    @IDA.setter
    def IDA(self, value: int) -> None:
        self.__cardinfo.IDA = value
        self.last_status_message()

    @property
    def IDB(self) -> int:
        """
           IDB
        """
        return self.__cardinfo.IDB

    @IDB.setter
    def IDB(self, value: int) -> None:
        self.__cardinfo.IDB = value
        self.last_status_message()

    @property
    def GS(self) -> int:
        """
           CardGrid point defining the location of the fastener. See Remark 2. (Integer > 0 or blank)
           * Remark 2:
           GS defines the approximate location of the fastener in space. GS is projected onto the surface patches A and B.The resulting piercing points GA and GB
           define the axis of the fastener.GS does not have to lie on the surfaces of the patches.GS must be able to project normals to the two patches. GA can be
           specified in lieu of GS, in which case GS will be ignored. If neither GS nor GA is specified, then (XS, YS, ZS) in basic must be specified.
           If both GA and GB are specified, they must lie on or at least have projections onto surface patches A and B respectively. The locations will then be
           corrected so that they lie on the surface patches A and B within machine precision. The length of the fastener is the final distance between GA and GB.
           If the length is zero, the normal to patch A is used to define the axis of the fastener.
           Diagnostic printouts, checkout runs and control of search and projection parameters are requested on the SWLDPRM Bulk Data entry.
        """
        return self.__cardinfo.GS

    @GS.setter
    def GS(self, value: int) -> None:
        self.__cardinfo.GS = value
        self.last_status_message()

    @property
    def GA(self) -> int:
        """
           CardGrid ids of piecing points on patches A and B. See Remark 2. (Integer > 0 or blank)
           * Remark 2:
           GS defines the approximate location of the fastener in space. GS is projected onto the surface patches A and B.The resulting piercing points GA and GB
           define the axis of the fastener.GS does not have to lie on the surfaces of the patches.GS must be able to project normals to the two patches. GA can be
           specified in lieu of GS, in which case GS will be ignored. If neither GS nor GA is specified, then (XS, YS, ZS) in basic must be specified.
           If both GA and GB are specified, they must lie on or at least have projections onto surface patches A and B respectively. The locations will then be
           corrected so that they lie on the surface patches A and B within machine precision. The length of the fastener is the final distance between GA and GB.
           If the length is zero, the normal to patch A is used to define the axis of the fastener.
           Diagnostic printouts, checkout runs and control of search and projection parameters are requested on the SWLDPRM Bulk Data entry.
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value
        self.last_status_message()

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value
        self.last_status_message()

    @property
    def XS(self) -> float:
        """
           Location of the fastener in basic. Required if neither GS nor GA is defined.See Remark 2. (Real or blank)
           * Remark 2:
           GS defines the approximate location of the fastener in space. GS is projected onto the surface patches A and B.The resulting piercing points GA and GB
           define the axis of the fastener.GS does not have to lie on the surfaces of the patches.GS must be able to project normals to the two patches. GA can be
           specified in lieu of GS, in which case GS will be ignored. If neither GS nor GA is specified, then (XS, YS, ZS) in basic must be specified.
           If both GA and GB are specified, they must lie on or at least have projections onto surface patches A and B respectively. The locations will then be
           corrected so that they lie on the surface patches A and B within machine precision. The length of the fastener is the final distance between GA and GB.
           If the length is zero, the normal to patch A is used to define the axis of the fastener.
           Diagnostic printouts, checkout runs and control of search and projection parameters are requested on the SWLDPRM Bulk Data entry.
        """
        return self.__cardinfo.XS

    @XS.setter
    def XS(self, value: float) -> None:
        self.__cardinfo.XS = value
        self.last_status_message()

    @property
    def YS(self) -> float:
        """
           YS
        """
        return self.__cardinfo.YS

    @YS.setter
    def YS(self, value: float) -> None:
        self.__cardinfo.YS = value
        self.last_status_message()

    @property
    def ZS(self) -> float:
        """
           ZS
        """
        return self.__cardinfo.ZS

    @ZS.setter
    def ZS(self, value: float) -> None:
        self.__cardinfo.ZS = value
        self.last_status_message()

class CGAP(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100000000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()
    
    @property
    def PID(self) -> int:
        """
           Property identification number of a PGAP entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID
    
    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value 
        self.last_status_message()

    @property
    def GA(self) -> int:
        "Connected grid points at ends A and B. (Integers > 0; GA ≠ GB)"
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value
        self.last_status_message()

    @property
    def GB(self) -> int:
        "Connected grid points at ends A and B. (Integers > 0; GA ≠ GB)"
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value
        self.last_status_message()

    @property
    def X1(self) -> float:
        "Components of the orientation vector , from GA, in the displacement coordinate system at GA. (Real)"
        return self.__cardinfo.X1
    
    @X1.setter
    def X1(self, value: float) -> None:
        self.__cardinfo.X1 = value
        self.last_status_message()

    @property
    def X2(self) -> float:
        "Components of the orientation vector , from GA, in the displacement coordinate system at GA. (Real)"
        return self.__cardinfo.X2

    @X2.setter
    def X2(self, value: float) -> None:
        self.__cardinfo.X2 = value
        self.last_status_message()

    @property
    def X3(self) -> float:
        "Components of the orientation vector , from GA, in the displacement coordinate system at GA. (Real)"
        return self.__cardinfo.X3

    @X3.setter
    def X3(self, value: float) -> None:
        self.__cardinfo.X3 = value
        self.last_status_message()

    @property
    def G0(self) -> int:
        "Alternate method to supply the orientation vector using grid point G0. Direction of is from GA to G0. (Integer > 0)"
        return self.__cardinfo.G0

    @G0.setter
    def G0(self, value: int) -> None:
        self.__cardinfo.G0 = value
        self.last_status_message()

    @property
    def CID(self) -> int:
        "Element coordinate system identification number. CID must be specified if GA and GB are coincident (distance from GA to GB < 10-4). (Integer > 0 or blank)"
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value
        self.last_status_message()

class CHEXANAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100000000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSOLID or PLSOLID entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value
        self.last_status_message()

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value
        self.last_status_message()

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value
        self.last_status_message()

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value
        self.last_status_message()

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value
        self.last_status_message()

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value
        self.last_status_message()

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value
        self.last_status_message()

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value
        self.last_status_message()

    @property
    def G11(self) -> int:
        """
           G11
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: int) -> None:
        self.__cardinfo.G11 = value
        self.last_status_message()

    @property
    def G12(self) -> int:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: int) -> None:
        self.__cardinfo.G12 = value
        self.last_status_message()

    @property
    def G13(self) -> int:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: int) -> None:
        self.__cardinfo.G13 = value
        self.last_status_message()

    @property
    def G14(self) -> int:
        """
           G14
        """
        return self.__cardinfo.G14

    @G14.setter
    def G14(self, value: int) -> None:
        self.__cardinfo.G14 = value
        self.last_status_message()

    @property
    def G15(self) -> int:
        """
           G15
        """
        return self.__cardinfo.G15

    @G15.setter
    def G15(self, value: int) -> None:
        self.__cardinfo.G15 = value
        self.last_status_message()

    @property
    def G16(self) -> int:
        """
           G16
        """
        return self.__cardinfo.G16

    @G16.setter
    def G16(self, value: int) -> None:
        self.__cardinfo.G16 = value
        self.last_status_message()

    @property
    def G17(self) -> int:
        """
           G17
        """
        return self.__cardinfo.G17

    @G17.setter
    def G17(self, value: int) -> None:
        self.__cardinfo.G17 = value
        self.last_status_message()

    @property
    def G18(self) -> int:
        """
           G18
        """
        return self.__cardinfo.G18

    @G18.setter
    def G18(self, value: int) -> None:
        self.__cardinfo.G18 = value
        self.last_status_message()

    @property
    def G19(self) -> int:
        """
           G19
        """
        return self.__cardinfo.G19

    @G19.setter
    def G19(self, value: int) -> None:
        self.__cardinfo.G19 = value
        self.last_status_message()

    @property
    def G20(self) -> int:
        """
           G20
        """
        return self.__cardinfo.G20

    @G20.setter
    def G20(self, value: int) -> None:
        self.__cardinfo.G20 = value
        self.last_status_message()


class CHEXAOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardChexaOpt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100000000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSOLID or PLSOLID entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value

    @property
    def G11(self) -> int:
        """
           G11
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: int) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> int:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: int) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> int:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: int) -> None:
        self.__cardinfo.G13 = value

    @property
    def G14(self) -> int:
        """
           G14
        """
        return self.__cardinfo.G14

    @G14.setter
    def G14(self, value: int) -> None:
        self.__cardinfo.G14 = value

    @property
    def G15(self) -> int:
        """
           G15
        """
        return self.__cardinfo.G15

    @G15.setter
    def G15(self, value: int) -> None:
        self.__cardinfo.G15 = value

    @property
    def G16(self) -> int:
        """
           G16
        """
        return self.__cardinfo.G16

    @G16.setter
    def G16(self, value: int) -> None:
        self.__cardinfo.G16 = value

    @property
    def G17(self) -> int:
        """
           G17
        """
        return self.__cardinfo.G17

    @G17.setter
    def G17(self, value: int) -> None:
        self.__cardinfo.G17 = value

    @property
    def G18(self) -> int:
        """
           G18
        """
        return self.__cardinfo.G18

    @G18.setter
    def G18(self, value: int) -> None:
        self.__cardinfo.G18 = value

    @property
    def G19(self) -> int:
        """
           G19
        """
        return self.__cardinfo.G19

    @G19.setter
    def G19(self, value: int) -> None:
        self.__cardinfo.G19 = value

    @property
    def G20(self) -> int:
        """
           G20
        """
        return self.__cardinfo.G20

    @G20.setter
    def G20(self, value: int) -> None:
        self.__cardinfo.G20 = value

    @property
    def CORDM(self) -> str:
        """
           Flag indicating that the following field(s) reference data to determine the material coordinate system.
        """
        return self.__cardinfo.CORDM

    @CORDM.setter
    def CORDM(self, value: str) -> None:
        self.__cardinfo.CORDM = value

    @property
    def CID(self) -> int:
        """
           Material coordinate system identification number. Default = 0 (Integer ≥ -1)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value

    @property
    def THETA(self) -> float:
        """
           Angle of rotation of the elemental X-axis and Y-axis about the elemental Z-axis. The new coordinate system formed after this rotational transformation
           represents the material system (the PHI field can further transform the material system). Note: For positive THETA, the elemental X-axis is rotated
           towards the elemental Y-axis. Default = blank (Real)
        """
        return self.__cardinfo.THETA

    @THETA.setter
    def THETA(self, value: float) -> None:
        self.__cardinfo.THETA = value

    @property
    def PHI(self) -> float:
        """
           This angle is applied on the new coordinate system derived after transformation with THETA. Angle of rotation of the elemental Z-axis and new X-axis
           about the new Y-axis.The new coordinate system formed after this rotational transformation represents the material system.
           Note: For positive PHI, the new X-axis is rotated towards the elemental Z-axis. Default = blank (Real)
        """
        return self.__cardinfo.PHI

    @PHI.setter
    def PHI(self, value: float) -> None:
        self.__cardinfo.PHI = value


class CONM2(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardConm2)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           <para>PID: <see cref="CardConm2"/> does not have an associate property. Returns <see cref="uint.MaxValue"/></para>
           <para>Implemented to use the interface <see cref="ICardElement"/></para>
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G(self) -> int:
        """
           CardGrid point identification number. (Integer > 0)
        """
        return self.__cardinfo.G

    @G.setter
    def G(self, value: int) -> None:
        self.__cardinfo.G = value

    @property
    def CID(self) -> int:
        """
           Coordinate system identification number.For CID of -1; see X1, X2, X3 low. (Integer > -1; Default = 0)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value

    @property
    def M(self) -> float:
        """
           Mass value. (Real)
        """
        return self.__cardinfo.M

    @M.setter
    def M(self, value: float) -> None:
        self.__cardinfo.M = value

    @property
    def X1(self) -> float:
        """
           Offset distances from the grid point to the center of gravity of the mass in the coordinate system defined in field 4, unless CID = -1, in which
           case X1, X2, X3 are the coordinates, not offsets, of the center of gravity of the mass in the basic coordinate system. (Real)
        """
        return self.__cardinfo.X1

    @X1.setter
    def X1(self, value: float) -> None:
        self.__cardinfo.X1 = value

    @property
    def X2(self) -> float:
        """
           X2
        """
        return self.__cardinfo.X2

    @X2.setter
    def X2(self, value: float) -> None:
        self.__cardinfo.X2 = value

    @property
    def X3(self) -> float:
        """
           X3
        """
        return self.__cardinfo.X3

    @X3.setter
    def X3(self, value: float) -> None:
        self.__cardinfo.X3 = value

    @property
    def I11(self) -> float:
        """
           Mass moments of inertia measured at the mass center of gravity in the coordinate system defined by field 4. If CID = -1, the basic coordinate
           system is implied. (For I11, I22, and I33; Real > 0.0; for I21, I31, and I32; Real)
        """
        return self.__cardinfo.I11

    @I11.setter
    def I11(self, value: float) -> None:
        self.__cardinfo.I11 = value

    @property
    def I21(self) -> float:
        """
           I21
        """
        return self.__cardinfo.I21

    @I21.setter
    def I21(self, value: float) -> None:
        self.__cardinfo.I21 = value

    @property
    def I22(self) -> float:
        """
           I22
        """
        return self.__cardinfo.I22

    @I22.setter
    def I22(self, value: float) -> None:
        self.__cardinfo.I22 = value

    @property
    def I31(self) -> float:
        """
           I31
        """
        return self.__cardinfo.I31

    @I31.setter
    def I31(self, value: float) -> None:
        self.__cardinfo.I31 = value

    @property
    def I32(self) -> float:
        """
           I32
        """
        return self.__cardinfo.I32

    @I32.setter
    def I32(self, value: float) -> None:
        self.__cardinfo.I32 = value

    @property
    def I33(self) -> float:
        """
           I33
        """
        return self.__cardinfo.I33

    @I33.setter
    def I33(self, value: float) -> None:
        self.__cardinfo.I33 = value


class CORD1C(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CIDA(self) -> int:
        """
           Coordinate system identification number. (Integer > 0)
        """
        return self.__cardinfo.CIDA

    @CIDA.setter
    def CIDA(self, value: int) -> None:
        self.__cardinfo.CIDA = value
        self.last_status_message()

    @property
    def CIDB(self) -> int:
        """
           CIDB
        """
        return self.__cardinfo.CIDB

    @CIDB.setter
    def CIDB(self, value: int) -> None:
        self.__cardinfo.CIDB = value
        self.last_status_message()

    @property
    def G1A(self) -> int:
        """
           CardGrid point identification numbers. (Integer > 0; G1A ≠ G2A ≠ G3AG1B ≠ G2B ≠ G3B;)
        """
        return self.__cardinfo.G1A

    @G1A.setter
    def G1A(self, value: int) -> None:
        self.__cardinfo.G1A = value
        self.last_status_message()

    @property
    def G2A(self) -> int:
        """
           G2A
        """
        return self.__cardinfo.G2A

    @G2A.setter
    def G2A(self, value: int) -> None:
        self.__cardinfo.G2A = value
        self.last_status_message()

    @property
    def G3A(self) -> int:
        """
           G3A
        """
        return self.__cardinfo.G3A

    @G3A.setter
    def G3A(self, value: int) -> None:
        self.__cardinfo.G3A = value
        self.last_status_message()

    @property
    def G1B(self) -> int:
        """
           G1B
        """
        return self.__cardinfo.G1B

    @G1B.setter
    def G1B(self, value: int) -> None:
        self.__cardinfo.G1B = value
        self.last_status_message()

    @property
    def G2B(self) -> int:
        """
           G2B
        """
        return self.__cardinfo.G2B

    @G2B.setter
    def G2B(self, value: int) -> None:
        self.__cardinfo.G2B = value
        self.last_status_message()

    @property
    def G3B(self) -> int:
        """
           G3B
        """
        return self.__cardinfo.G3B

    @G3B.setter
    def G3B(self, value: int) -> None:
        self.__cardinfo.G3B = value
        self.last_status_message()


class CORD1R(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CIDA(self) -> int:
        """
           Coordinate system identification number. (Integer > 0)
        """
        return self.__cardinfo.CIDA

    @CIDA.setter
    def CIDA(self, value: int) -> None:
        self.__cardinfo.CIDA = value
        self.last_status_message()

    @property
    def CIDB(self) -> int:
        """
           CIDB
        """
        return self.__cardinfo.CIDB

    @CIDB.setter
    def CIDB(self, value: int) -> None:
        self.__cardinfo.CIDB = value
        self.last_status_message()

    @property
    def G1A(self) -> int:
        """
           CardGrid point identification numbers. (Integer > 0; G1A ≠ G2A ≠ G3AG1B ≠ G2B ≠ G3B;)
        """
        return self.__cardinfo.G1A

    @G1A.setter
    def G1A(self, value: int) -> None:
        self.__cardinfo.G1A = value
        self.last_status_message()

    @property
    def G2A(self) -> int:
        """
           G2A
        """
        return self.__cardinfo.G2A

    @G2A.setter
    def G2A(self, value: int) -> None:
        self.__cardinfo.G2A = value
        self.last_status_message()

    @property
    def G3A(self) -> int:
        """
           G3A
        """
        return self.__cardinfo.G3A

    @G3A.setter
    def G3A(self, value: int) -> None:
        self.__cardinfo.G3A = value
        self.last_status_message()

    @property
    def G1B(self) -> int:
        """
           G1B
        """
        return self.__cardinfo.G1B

    @G1B.setter
    def G1B(self, value: int) -> None:
        self.__cardinfo.G1B = value
        self.last_status_message()

    @property
    def G2B(self) -> int:
        """
           G2B
        """
        return self.__cardinfo.G2B

    @G2B.setter
    def G2B(self, value: int) -> None:
        self.__cardinfo.G2B = value
        self.last_status_message()

    @property
    def G3B(self) -> int:
        """
           G3B
        """
        return self.__cardinfo.G3B

    @G3B.setter
    def G3B(self, value: int) -> None:
        self.__cardinfo.G3B = value
        self.last_status_message()


class CORD1S(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CIDA(self) -> int:
        """
           Coordinate system identification number. (Integer > 0)
        """
        return self.__cardinfo.CIDA

    @CIDA.setter
    def CIDA(self, value: int) -> None:
        self.__cardinfo.CIDA = value
        self.last_status_message()

    @property
    def CIDB(self) -> int:
        """
           CIDB
        """
        return self.__cardinfo.CIDB

    @CIDB.setter
    def CIDB(self, value: int) -> None:
        self.__cardinfo.CIDB = value
        self.last_status_message()

    @property
    def G1A(self) -> int:
        """
           CardGrid point identification numbers. (Integer > 0; G1A ≠ G2A ≠ G3AG1B ≠ G2B ≠ G3B;)
        """
        return self.__cardinfo.G1A

    @G1A.setter
    def G1A(self, value: int) -> None:
        self.__cardinfo.G1A = value
        self.last_status_message()

    @property
    def G2A(self) -> int:
        """
           G2A
        """
        return self.__cardinfo.G2A

    @G2A.setter
    def G2A(self, value: int) -> None:
        self.__cardinfo.G2A = value
        self.last_status_message()

    @property
    def G3A(self) -> int:
        """
           G3A
        """
        return self.__cardinfo.G3A

    @G3A.setter
    def G3A(self, value: int) -> None:
        self.__cardinfo.G3A = value
        self.last_status_message()

    @property
    def G1B(self) -> int:
        """
           G1B
        """
        return self.__cardinfo.G1B

    @G1B.setter
    def G1B(self, value: int) -> None:
        self.__cardinfo.G1B = value
        self.last_status_message()

    @property
    def G2B(self) -> int:
        """
           G2B
        """
        return self.__cardinfo.G2B

    @G2B.setter
    def G2B(self, value: int) -> None:
        self.__cardinfo.G2B = value
        self.last_status_message()

    @property
    def G3B(self) -> int:
        """
           G3B
        """
        return self.__cardinfo.G3B

    @G3B.setter
    def G3B(self, value: int) -> None:
        self.__cardinfo.G3B = value
        self.last_status_message()


class CORD2C(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CID(self) -> int:
        """
           Coordinate system identification number. (Integer > 0)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value
        self.last_status_message()

    @property
    def RID(self) -> int:
        """
           Identification number of a coordinate system that is defined independently from this coordinate system. (Integer > 0; Default = 0 is the basic coordinate
           system.)
        """
        return self.__cardinfo.RID

    @RID.setter
    def RID(self, value: int) -> None:
        self.__cardinfo.RID = value
        self.last_status_message()

    @property
    def A1(self) -> float:
        """
           Coordinates of three points in coordinate system defined in field 3. (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value
        self.last_status_message()

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value
        self.last_status_message()

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value
        self.last_status_message()

    @property
    def B1(self) -> float:
        """
           B1
        """
        return self.__cardinfo.B1

    @B1.setter
    def B1(self, value: float) -> None:
        self.__cardinfo.B1 = value
        self.last_status_message()

    @property
    def B2(self) -> float:
        """
           B2
        """
        return self.__cardinfo.B2

    @B2.setter
    def B2(self, value: float) -> None:
        self.__cardinfo.B2 = value
        self.last_status_message()

    @property
    def B3(self) -> float:
        """
           B3
        """
        return self.__cardinfo.B3

    @B3.setter
    def B3(self, value: float) -> None:
        self.__cardinfo.B3 = value
        self.last_status_message()

    @property
    def C1(self) -> float:
        """
           C1
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: float) -> None:
        self.__cardinfo.C1 = value
        self.last_status_message()

    @property
    def C2(self) -> float:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: float) -> None:
        self.__cardinfo.C2 = value
        self.last_status_message()

    @property
    def C3(self) -> float:
        """
           C3
        """
        return self.__cardinfo.C3

    @C3.setter
    def C3(self, value: float) -> None:
        self.__cardinfo.C3 = value
        self.last_status_message()


class CORD2R(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CID(self) -> int:
        """
           Coordinate system identification number. (Integer > 0)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value
        self.last_status_message()

    @property
    def RID(self) -> int:
        """
           Identification number of a coordinate system that is defined independently from this coordinate system. (Integer > 0; Default = 0 is the basic coordinate
           system.)
        """
        return self.__cardinfo.RID

    @RID.setter
    def RID(self, value: int) -> None:
        self.__cardinfo.RID = value
        self.last_status_message()

    @property
    def A1(self) -> float:
        """
           Coordinates of three points in coordinate system defined in field 3. (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value
        self.last_status_message()

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value
        self.last_status_message()

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value
        self.last_status_message()

    @property
    def B1(self) -> float:
        """
           B1
        """
        return self.__cardinfo.B1

    @B1.setter
    def B1(self, value: float) -> None:
        self.__cardinfo.B1 = value
        self.last_status_message()

    @property
    def B2(self) -> float:
        """
           B2
        """
        return self.__cardinfo.B2

    @B2.setter
    def B2(self, value: float) -> None:
        self.__cardinfo.B2 = value
        self.last_status_message()

    @property
    def B3(self) -> float:
        """
           B3
        """
        return self.__cardinfo.B3

    @B3.setter
    def B3(self, value: float) -> None:
        self.__cardinfo.B3 = value
        self.last_status_message()

    @property
    def C1(self) -> float:
        """
           C1
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: float) -> None:
        self.__cardinfo.C1 = value
        self.last_status_message()

    @property
    def C2(self) -> float:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: float) -> None:
        self.__cardinfo.C2 = value
        self.last_status_message()

    @property
    def C3(self) -> float:
        """
           C3
        """
        return self.__cardinfo.C3

    @C3.setter
    def C3(self, value: float) -> None:
        self.__cardinfo.C3 = value
        self.last_status_message()


class CORD2S(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CID(self) -> int:
        """
           Coordinate system identification number. (Integer > 0)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value
        self.last_status_message()

    @property
    def RID(self) -> int:
        """
           Identification number of a coordinate system that is defined independently from this coordinate system. (Integer > 0; Default = 0 is the basic coordinate
           system.)
        """
        return self.__cardinfo.RID

    @RID.setter
    def RID(self, value: int) -> None:
        self.__cardinfo.RID = value
        self.last_status_message()

    @property
    def A1(self) -> float:
        """
           Coordinates of three points in coordinate system defined in field 3. (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value
        self.last_status_message()

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value
        self.last_status_message()

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value
        self.last_status_message()

    @property
    def B1(self) -> float:
        """
           B1
        """
        return self.__cardinfo.B1

    @B1.setter
    def B1(self, value: float) -> None:
        self.__cardinfo.B1 = value
        self.last_status_message()

    @property
    def B2(self) -> float:
        """
           B2
        """
        return self.__cardinfo.B2

    @B2.setter
    def B2(self, value: float) -> None:
        self.__cardinfo.B2 = value
        self.last_status_message()

    @property
    def B3(self) -> float:
        """
           B3
        """
        return self.__cardinfo.B3

    @B3.setter
    def B3(self, value: float) -> None:
        self.__cardinfo.B3 = value
        self.last_status_message()

    @property
    def C1(self) -> float:
        """
           C1
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: float) -> None:
        self.__cardinfo.C1 = value
        self.last_status_message()

    @property
    def C2(self) -> float:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: float) -> None:
        self.__cardinfo.C2 = value
        self.last_status_message()

    @property
    def C3(self) -> float:
        """
           C3
        """
        return self.__cardinfo.C3

    @C3.setter
    def C3(self, value: float) -> None:
        self.__cardinfo.C3 = value
        self.last_status_message()


class CPENTANAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSOLID or PLSOLID entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected grid points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value
        self.last_status_message()

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value
        self.last_status_message()

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value
        self.last_status_message()

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value
        self.last_status_message()

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value
        self.last_status_message()

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value
        self.last_status_message()

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value
        self.last_status_message()

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value
        self.last_status_message()

    @property
    def G11(self) -> int:
        """
           G11
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: int) -> None:
        self.__cardinfo.G11 = value
        self.last_status_message()

    @property
    def G12(self) -> int:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: int) -> None:
        self.__cardinfo.G12 = value
        self.last_status_message()

    @property
    def G13(self) -> int:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: int) -> None:
        self.__cardinfo.G13 = value
        self.last_status_message()

    @property
    def G14(self) -> int:
        """
           G14
        """
        return self.__cardinfo.G14

    @G14.setter
    def G14(self, value: int) -> None:
        self.__cardinfo.G14 = value
        self.last_status_message()

    @property
    def G15(self) -> int:
        """
           G15
        """
        return self.__cardinfo.G15

    @G15.setter
    def G15(self, value: int) -> None:
        self.__cardinfo.G15 = value
        self.last_status_message()


class CPENTAOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCpentaOpt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSOLID or PLSOLID entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected grid points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value

    @property
    def G11(self) -> int:
        """
           G11
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: int) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> int:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: int) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> int:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: int) -> None:
        self.__cardinfo.G13 = value

    @property
    def G14(self) -> int:
        """
           G14
        """
        return self.__cardinfo.G14

    @G14.setter
    def G14(self, value: int) -> None:
        self.__cardinfo.G14 = value

    @property
    def G15(self) -> int:
        """
           G15
        """
        return self.__cardinfo.G15

    @G15.setter
    def G15(self, value: int) -> None:
        self.__cardinfo.G15 = value

    @property
    def CORDM(self) -> str:
        """
           Flag indicating that the following field(s) reference data to determine the material coordinate system.
        """
        return self.__cardinfo.CORDM

    @CORDM.setter
    def CORDM(self, value: str) -> None:
        self.__cardinfo.CORDM = value

    @property
    def CID(self) -> int:
        """
           Material coordinate system identification number. Default = 0 (Integer ≥ -1)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value

    @property
    def THETA(self) -> float:
        """
           Angle of rotation of the elemental X-axis and Y-axis about the elemental Z-axis. The new coordinate system formed after this rotational transformation
           represents the material system (the PHI field can further transform the material system). Note: For positive THETA, the elemental X-axis is rotated
           towards the elemental Y-axis. Default = blank (Real)
        """
        return self.__cardinfo.THETA

    @THETA.setter
    def THETA(self, value: float) -> None:
        self.__cardinfo.THETA = value

    @property
    def PHI(self) -> float:
        """
           This angle is applied on the new coordinate system derived after transformation with THETA. Angle of rotation of the elemental Z-axis and new X-axis
           about the new Y-axis.The new coordinate system formed after this rotational transformation represents the material system.
           Note: For positive PHI, the new X-axis is rotated towards the elemental Z-axis. Default = blank (Real)
        """
        return self.__cardinfo.PHI

    @PHI.setter
    def PHI(self, value: float) -> None:
        self.__cardinfo.PHI = value


class CPYRA(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCpyra)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Unique element identification number. No default (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           A PSOLID property entry identification number. Default = EID (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. Default = blank(Integer ≥ 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value

    @property
    def G11(self) -> int:
        """
           G11
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: int) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> int:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: int) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> int:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: int) -> None:
        self.__cardinfo.G13 = value

    @property
    def CORDM(self) -> str:
        """
           Flag indicating that the following field reference data to determine the material coordinate system.
        """
        return self.__cardinfo.CORDM

    @CORDM.setter
    def CORDM(self, value: str) -> None:
        self.__cardinfo.CORDM = value

    @property
    def CID(self) -> int:
        """
           Material coordinate system identification number. Default = 0 (Integer ≥ -1)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value


class CQUAD4(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSHELL, PCOMP, or PLPLANE entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integers > 0, all unique.)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value
        self.last_status_message()

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value
        self.last_status_message()

    @property
    def THETA(self) -> float:
        """
           Material property orientation angle in degrees. THETA is ignored for hyperelastic elements.See Figure 8-46. (Real; Default = 0.0)
        """
        return self.__cardinfo.Theta

    @THETA.setter
    def THETA(self, value: float) -> None:
        self.__cardinfo.Theta = value
        self.last_status_message()

    @property
    def MCID(self) -> int:
        """
           Material coordinate system identification number. The x-axis of the material coordinate system is determined by projecting the x-axis
           of the MCID coordinate system(defined by the CORDij entry or zero for the basic coordinate system) onto the surface of the element.
           Use DIAG 38 to print the computed THETA values. MCID is ignored for hyperelastic elements. For SOL 600, only CORD2R is allowed.
           (Integer >= 0; If blank, then THETA = 0.0 is assumed.)
        """
        return self.__cardinfo.MCID

    @MCID.setter
    def MCID(self, value: int) -> None:
        self.__cardinfo.MCID = value
        self.last_status_message()

    @property
    def ZOFFS(self) -> float:
        """
           Offset from the surface of grid points to the element reference plane. ZOFFS is ignored for hyperelastic elements.See Remark 6. (Real)
        """
        return self.__cardinfo.ZOFFS

    @ZOFFS.setter
    def ZOFFS(self, value: float) -> None:
        self.__cardinfo.ZOFFS = value
        self.last_status_message()

    @property
    def TFLAG(self) -> int:
        """
           An integer flag, signifying the meaning of the Ti values. (Integer 0, 1, or blank)
        """
        return self.__cardinfo.TFLAG

    @TFLAG.setter
    def TFLAG(self, value: int) -> None:
        self.__cardinfo.TFLAG = value
        self.last_status_message()

    @property
    def T1(self) -> float:
        """
           Membrane thickness of element at grid points G1 through G4.If “TFLAG” is zero or blank, then Ti are actual user specified thicknesses.
           See Remark 4*. for default. (Real >= 0.0 or blank, not all zero.)
           If “TFLAG” is one, then the Ti are fractions relative to the T value of the PSHELL.
           (Real > 0.0 or blank, not all zero.Default = 1.0)
           Ti are ignored for hyperelastic elements.

            *Remark 4: The continuation is optional. If it is not supplied, then T1 through T4 will be set equal to the
            value of T on the PSHELL entry.
        """
        return self.__cardinfo.T1

    @T1.setter
    def T1(self, value: float) -> None:
        self.__cardinfo.T1 = value
        self.last_status_message()

    @property
    def T2(self) -> float:
        """
           T2
        """
        return self.__cardinfo.T2

    @T2.setter
    def T2(self, value: float) -> None:
        self.__cardinfo.T2 = value
        self.last_status_message()

    @property
    def T3(self) -> float:
        """
           T3
        """
        return self.__cardinfo.T3

    @T3.setter
    def T3(self, value: float) -> None:
        self.__cardinfo.T3 = value
        self.last_status_message()

    @property
    def T4(self) -> float:
        """
           T4
        """
        return self.__cardinfo.T4

    @T4.setter
    def T4(self, value: float) -> None:
        self.__cardinfo.T4 = value
        self.last_status_message()


class CQUAD8(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSHELL, PCOMP, or PLPLANE entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected corner grid points.Required data for all four grid points. (Unique Integers > 0)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value
        self.last_status_message()

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value
        self.last_status_message()

    @property
    def G5(self) -> int:
        """
           Identification numbers of connected edge grid points. Optional data for any or all four grid points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value
        self.last_status_message()

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value
        self.last_status_message()

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value
        self.last_status_message()

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value
        self.last_status_message()

    @property
    def T1(self) -> float:
        """
           Membrane thickness of element at grid points G1 through G4.If “TFLAG” is zero or blank, then Ti are actual user specified thicknesses.
           See Remark 4*. for default. (Real >= 0.0 or blank, not all zero.)
           If “TFLAG” is one, then the Ti are fractions relative to the T value of the PSHELL.
           (Real > 0.0 or blank, not all zero.Default = 1.0)
           Ti are ignored for hyperelastic elements.

           *Remark 4: The continuation is optional. If it is not supplied, then T1 through T4 will be set equal to the
           value of T on the PSHELL entry.
        """
        return self.__cardinfo.T1

    @T1.setter
    def T1(self, value: float) -> None:
        self.__cardinfo.T1 = value
        self.last_status_message()

    @property
    def T2(self) -> float:
        """
           T2
        """
        return self.__cardinfo.T2

    @T2.setter
    def T2(self, value: float) -> None:
        self.__cardinfo.T2 = value
        self.last_status_message()

    @property
    def T3(self) -> float:
        """
           T3
        """
        return self.__cardinfo.T3

    @T3.setter
    def T3(self, value: float) -> None:
        self.__cardinfo.T3 = value
        self.last_status_message()

    @property
    def T4(self) -> float:
        """
           T4
        """
        return self.__cardinfo.T4

    @T4.setter
    def T4(self, value: float) -> None:
        self.__cardinfo.T4 = value
        self.last_status_message()

    @property
    def THETA(self) -> float:
        """
           Material property orientation angle in degrees. THETA is ignored for hyperelastic elements.See Figure 8-46. (Real; Default = 0.0)
        """
        return self.__cardinfo.Theta

    @THETA.setter
    def THETA(self, value: float) -> None:
        self.__cardinfo.Theta = value
        self.last_status_message()

    @property
    def MCID(self) -> int:
        """
           Material coordinate system identification number. The x-axis of the material coordinate system is determined by projecting the x-axis
           of the MCID coordinate system(defined by the CORDij entry or zero for the basic coordinate system) onto the surface of the element.
           Use DIAG 38 to print the computed THETA values. MCID is ignored for hyperelastic elements. For SOL 600, only CORD2R is allowed.
           (Integer >= 0; If blank, then THETA = 0.0 is assumed.)
        """
        return self.__cardinfo.MCID

    @MCID.setter
    def MCID(self, value: int) -> None:
        self.__cardinfo.MCID = value
        self.last_status_message()

    @property
    def ZOFFS(self) -> float:
        """
           Offset from the surface of grid points to the element reference plane. ZOFFS is ignored for hyperelastic elements.See Remark 6. (Real)
        """
        return self.__cardinfo.ZOFFS

    @ZOFFS.setter
    def ZOFFS(self, value: float) -> None:
        self.__cardinfo.ZOFFS = value
        self.last_status_message()

    @property
    def TFLAG(self) -> int:
        """
           An integer flag, signifying the meaning of the Ti values. (Integer 0, 1, or blank)
        """
        return self.__cardinfo.TFLAG

    @TFLAG.setter
    def TFLAG(self, value: int) -> None:
        self.__cardinfo.TFLAG = value
        self.last_status_message()


class CROD(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PROD entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           G1: CardGrid point identification numbers of connection points. (Integer > 0 ; G1 ≠ G2)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           G2: CardGrid point identification numbers of connection points. (Integer > 0 ; G1 ≠ G2)
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()


class CSHEAR(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSHEAR entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           G1: Identification numbers of connected grid points. (Integer >= 0 ; G1 ≠ G2 ≠ G3 ≠ G4)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           G2: Identification numbers of connected grid points. (Integer >= 0 ; G1 ≠ G2 ≠ G3 ≠ G4)
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()

    @property
    def G3(self) -> int:
        """
           G3: Identification numbers of connected grid points. (Integer >= 0 ; G1 ≠ G2 ≠ G3 ≠ G4)
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value
        self.last_status_message()

    @property
    def G4(self) -> int:
        """
           G4: Identification numbers of connected grid points. (Integer >= 0 ; G1 ≠ G2 ≠ G3 ≠ G4)
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value
        self.last_status_message()


class CTETRANAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSOLID or PLSOLID entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected grid points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value
        self.last_status_message()

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value
        self.last_status_message()

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value
        self.last_status_message()

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value
        self.last_status_message()

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value
        self.last_status_message()

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value
        self.last_status_message()

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value
        self.last_status_message()

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value
        self.last_status_message()


class CTETRAOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCtetraOpt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSOLID or PLSOLID entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected grid points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value

    @property
    def CORDM(self) -> str:
        """
           Flag indicating that the following field references the material coordinate system.
        """
        return self.__cardinfo.CORDM

    @CORDM.setter
    def CORDM(self, value: str) -> None:
        self.__cardinfo.CORDM = value

    @property
    def CID(self) -> int:
        """
           Material coordinate system identification number. Default = 0 (Integer ≥ -1)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value


class CTRIA3(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSHELL, PCOMP, or PLPLANE entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integers > 0, all unique.)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value
        self.last_status_message()

    @property
    def THETA(self) -> float:
        """
           Material property orientation angle in degrees. THETA is ignored for hyperelastic elements. (Real; Default = 0.0)
        """
        return self.__cardinfo.Theta

    @THETA.setter
    def THETA(self, value: float) -> None:
        self.__cardinfo.Theta = value
        self.last_status_message()

    @property
    def MCID(self) -> int:
        """
           Material coordinate system identification number. The x-axis of the material coordinate system is determined by projecting the x-axis
           of the MCID coordinate system(defined by the CORDij entry or zero for the basic coordinate system) onto the surface of the element.
           Use DIAG 38 to print the computed THETA values. MCID is ignored for hyperelastic elements. For SOL 600, only CORD2R is allowed.
           (Integer >= 0; If blank, then THETA = 0.0 is assumed.)
        """
        return self.__cardinfo.MCID

    @MCID.setter
    def MCID(self, value: int) -> None:
        self.__cardinfo.MCID = value
        self.last_status_message()

    @property
    def ZOFFS(self) -> float:
        """
           Offset from the surface of grid points to the element reference plane. ZOFFS is ignored for hyperelastic elements.See Remark 3. (Real)
        """
        return self.__cardinfo.ZOFFS

    @ZOFFS.setter
    def ZOFFS(self, value: float) -> None:
        self.__cardinfo.ZOFFS = value
        self.last_status_message()

    @property
    def TFLAG(self) -> int:
        """
           An integer flag, signifying the meaning of the Ti values. (Integer 0, 1, or blank)
        """
        return self.__cardinfo.TFLAG

    @TFLAG.setter
    def TFLAG(self, value: int) -> None:
        self.__cardinfo.TFLAG = value
        self.last_status_message()

    @property
    def T1(self) -> float:
        """
           Membrane thickness of element at grid points G1 through G4.If “TFLAG” is zero or blank, then Ti are actual user specified thicknesses.
           See Remark 4*. for default. (Real >= 0.0 or blank, not all zero.)
           If “TFLAG” is one, then the Ti are fractions relative to the T value of the PSHELL.
           (Real > 0.0 or blank, not all zero.Default = 1.0)
           Ti are ignored for hyperelastic elements.
        """
        return self.__cardinfo.T1

    @T1.setter
    def T1(self, value: float) -> None:
        self.__cardinfo.T1 = value
        self.last_status_message()

    @property
    def T2(self) -> float:
        """
           T2
        """
        return self.__cardinfo.T2

    @T2.setter
    def T2(self, value: float) -> None:
        self.__cardinfo.T2 = value
        self.last_status_message()

    @property
    def T3(self) -> float:
        """
           T3
        """
        return self.__cardinfo.T3

    @T3.setter
    def T3(self, value: float) -> None:
        self.__cardinfo.T3 = value
        self.last_status_message()


class CTRIA6(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSHELL, PCOMP, or PLPLANE entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected corner grid points. (Unique Integers > 0)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value
        self.last_status_message()

    @property
    def G4(self) -> int:
        """
           Identification number of connected edge grid points. Optional data for any or all three points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value
        self.last_status_message()

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value
        self.last_status_message()

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value
        self.last_status_message()

    @property
    def THETA(self) -> float:
        """
           Material property orientation angle in degrees. THETA is ignored for hyperelastic elements. (Real; Default = 0.0)
        """
        return self.__cardinfo.Theta

    @THETA.setter
    def THETA(self, value: float) -> None:
        self.__cardinfo.Theta = value
        self.last_status_message()

    @property
    def MCID(self) -> int:
        """
           Material coordinate system identification number. The x-axis of the material coordinate system is determined by projecting the x-axis
           of the MCID coordinate system(defined by the CORDij entry or zero for the basic coordinate system) onto the surface of the element.
           Use DIAG 38 to print the computed THETA values. MCID is ignored for hyperelastic elements. For SOL 600, only CORD2R is allowed.
           (Integer >= 0; If blank, then THETA = 0.0 is assumed.)
        """
        return self.__cardinfo.MCID

    @MCID.setter
    def MCID(self, value: int) -> None:
        self.__cardinfo.MCID = value
        self.last_status_message()

    @property
    def ZOFFS(self) -> float:
        """
           Offset from the surface of grid points to the element reference plane. ZOFFS is ignored for hyperelastic elements.See Remark 3. (Real)
        """
        return self.__cardinfo.ZOFFS

    @ZOFFS.setter
    def ZOFFS(self, value: float) -> None:
        self.__cardinfo.ZOFFS = value
        self.last_status_message()

    @property
    def T1(self) -> float:
        """
           Membrane thickness of element at grid points G1 through G4.If “TFLAG” is zero or blank, then Ti are actual user specified thicknesses.
           See Remark 4*. for default. (Real >= 0.0 or blank, not all zero.)
           If “TFLAG” is one, then the Ti are fractions relative to the T value of the PSHELL.
           (Real > 0.0 or blank, not all zero.Default = 1.0)
           Ti are ignored for hyperelastic elements.
        """
        return self.__cardinfo.T1

    @T1.setter
    def T1(self, value: float) -> None:
        self.__cardinfo.T1 = value
        self.last_status_message()

    @property
    def T2(self) -> float:
        """
           T2
        """
        return self.__cardinfo.T2

    @T2.setter
    def T2(self, value: float) -> None:
        self.__cardinfo.T2 = value
        self.last_status_message()

    @property
    def T3(self) -> float:
        """
           T3
        """
        return self.__cardinfo.T3

    @T3.setter
    def T3(self, value: float) -> None:
        self.__cardinfo.T3 = value
        self.last_status_message()

    @property
    def TFLAG(self) -> int:
        """
           An integer flag, signifying the meaning of the Ti values. (Integer 0, 1, or blank)
        """
        return self.__cardinfo.TFLAG

    @TFLAG.setter
    def TFLAG(self, value: int) -> None:
        self.__cardinfo.TFLAG = value
        self.last_status_message()

class FORCENAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def SID(self) -> int:
        """
        Load set identification number. (Integer > 0)
        """
        return self.__cardinfo.SID
    
    @SID.setter
    def SID(self, value: int) -> None:
        self.__cardinfo.SID = value
        self.last_status_message()
    
    @property
    def G(self) -> int:
        """
        Grid point identification number. (Integer > 0)
        """
        return self.__cardinfo.G
    
    @G.setter
    def G(self, value: int) -> None:
        self.__cardinfo.G = value
        self.last_status_message()
    
    @property
    def CID(self) -> int:
        """
        Coordinate system identification number. (Integer >= 0; Default = 0)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value
        self.last_status_message()

    @property
    def F(self) -> float:
        """
        Scale factor. Real)
        """
        return self.__cardinfo.F

    @F.setter
    def F(self, value: float) -> None:
        self.__cardinfo.F = value
        self.last_status_message()

    @property
    def N1(self) -> float:
        """
        X-component of a vector measured in coordinate system defined by CID. (Real; at least 
        one Ni ≠ 0.0. unless F is zero)
        """
        return self.__cardinfo.N1

    @N1.setter
    def N1(self, value: float) -> None:
        self.__cardinfo.N1 = value
        self.last_status_message()

    @property
    def N2(self) -> float:
        """
        Y-component of a vector measured in coordinate system defined by CID. (Real; at least 
        one Ni ≠ 0.0. unless F is zero)
        """
        return self.__cardinfo.N2

    @N2.setter
    def N2(self, value: float) -> None:
        self.__cardinfo.N2 = value
        self.last_status_message()

    @property
    def N3(self) -> float:
        """
        Z-component of a vector measured in coordinate system defined by CID. (Real; at least
        one Ni ≠ 0.0. unless F is zero)
        """
        return self.__cardinfo.N3

    @N3.setter
    def N3(self, value: float) -> None:
        self.__cardinfo.N3 = value
        self.last_status_message()


class CWELD(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EWID(self) -> int:
        """
           CardCweld element identification number. See Remark 1. (Integer > 0)
           * Remark 1:
           CardCweld defines a flexible connection between two surface patches, between a point and a surface patch, or between two shell vertex grid points.
           See Figure 8-72 through Figure 8-76.
        """
        return self.__cardinfo.EWID

    @EWID.setter
    def EWID(self, value: int) -> None:
        self.__cardinfo.EWID = value
        self.last_status_message()

    @property
    def PWID(self) -> int:
        """
           Property identification number of a PWELD entry. (Integer > 0)
        """
        return self.__cardinfo.PWID

    @PWID.setter
    def PWID(self, value: int) -> None:
        self.__cardinfo.PWID = value
        self.last_status_message()

    @property
    def GS(self) -> int:
        """
           Identification number of a grid point which defines the location of the connector.See Remarks 2. and 3.
           * Remark 2:
           CardGrid point GS defines the approximate location of the connector in space. GS is projected on surface patch A and on surface patch B.The resulting piercing
           points GA and GB define the axis of the connector. GS must have a normal projection on surface patch A and B. GS does not have to lie on the surface
           patches. GS is ignored for format “ALIGN”. GA is used instead of GS if GS is not specified. For the formats “ELPAT” and “PARTPAT,” if GS and GA are
           not specified, then XS, YS, and ZS must be specified.
           * Remark 3:
           The connectivity between grid points on surface patch A and grid points on surface patch B is generated depending on the location of GS and the cross
           sectional area of the connector.Diagnostic print outs, checkout runs and non default settings of search and projection parameters are requested on the
           SWLDPRM Bulk Data entry.It is recommended to start with the default settings.
        """
        return self.__cardinfo.GS

    @GS.setter
    def GS(self, value: int) -> None:
        self.__cardinfo.GS = value
        self.last_status_message()

    @property
    def GA(self) -> int:
        """
           CardGrid point identification numbers of piercing points on surface A and surface B, respectively. See Remark 5. (Integer > 0 or blank)
           * Remark 5:
           The definition of the piercing grid points GA and GB is optional for all formats with the exception of the format “ALIGN”. If GA and GB are given,
           GS is ignored.If GA and GB are not specified, they are generated from the normal projection of GS on surface patches A and B.For the formats
           “ELEMID” and “GRIDID,” internal identification numbers are generated for GA and GB starting with 101e+6 by default. The offset number can be
           changed with PARAM, OSWPPT. If GA and GB are specified, they must lie on or at least have a projection on surface patches A and B, respectively. The
           locations of GA and GB are corrected so that they lie on surface patches A and B within machine precision accuracy.The length of the connector is the
           distance of grid point GA to GB.
           Vertex grid identification number of shell A and B, respectively. (Integer > 0)
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value
        self.last_status_message()

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value
        self.last_status_message()

    @property
    def MCID(self) -> int:
        """
            Specifies the element stiffness coordinate system
        """
        return self.__cardinfo.MCID
    
    @MCID.setter
    def MCID(self, value: int) -> None:
        self.__cardinfo.MCID = value
        self.last_status_message()

    @property
    def PIDA(self) -> int:
        """
           Property identification numbers of PSHELL entries defining surface A and B respectively. (Integer > 0)
        """
        return self.__cardinfo.PIDA

    @PIDA.setter
    def PIDA(self, value: int) -> None:
        self.__cardinfo.PIDA = value
        self.last_status_message()

    @property
    def PIDB(self) -> int:
        """
           PIDB
        """
        return self.__cardinfo.PIDB

    @PIDB.setter
    def PIDB(self, value: int) -> None:
        self.__cardinfo.PIDB = value
        self.last_status_message()

    @property
    def XS(self) -> float:
        """
           Coordinates of spot weld location in basic. See Remark 2. (Real)
           * Remark 2:
           CardGrid point GS defines the approximate location of the connector in space. GS is projected on surface patch A and on surface patch B.The resulting piercing
           points GA and GB define the axis of the connector. GS must have a normal projection on surface patch A and B. GS does not have to lie on the surface
           patches. GS is ignored for format “ALIGN”. GA is used instead of GS if GS is not specified. For the formats “ELPAT” and “PARTPAT,” if GS and GA are
           not specified, then XS, YS, and ZS must be specified.
        """
        return self.__cardinfo.XS

    @XS.setter
    def XS(self, value: float) -> None:
        self.__cardinfo.XS = value
        self.last_status_message()

    @property
    def YS(self) -> float:
        """
           YS
        """
        return self.__cardinfo.YS

    @YS.setter
    def YS(self, value: float) -> None:
        self.__cardinfo.YS = value
        self.last_status_message()

    @property
    def ZS(self) -> float:
        """
           ZS
        """
        return self.__cardinfo.ZS

    @ZS.setter
    def ZS(self, value: float) -> None:
        self.__cardinfo.ZS = value
        self.last_status_message()

    @property
    def SHIDA(self) -> int:
        """
           Shell element identification numbers of elements on patch A and B, respectively. (Integer > 0)
        """
        return self.__cardinfo.SHIDA

    @SHIDA.setter
    def SHIDA(self, value: int) -> None:
        self.__cardinfo.SHIDA = value
        self.last_status_message()

    @property
    def SHIDB(self) -> int:
        """
           SHIDB
        """
        return self.__cardinfo.SHIDB

    @SHIDB.setter
    def SHIDB(self, value: int) -> None:
        self.__cardinfo.SHIDB = value
        self.last_status_message()

    @property
    def SPTYP(self) -> str:
        """
           Character string indicating types of surface patches A and B.SPTYP=”QQ”, “TT”, “QT”, “TQ”, “Q” or “T”. See Remark 9.
           * Remark 9:
           SPTYP defines the type of surface patches to be connected. SPTYP is required for the format "GRIDID" to identify quadrilateral or triangular patches.The
           combinations are:
           SPTYP           Description
           QQ              Connects a quadrilateral surface patch A(Q4 to Q8) with a quadrilateral surface patch B(Q4 to Q8).
           QT              Connects a quadrilateral surface patch A(Q4 to Q8) with a triangular surface patch B(T3 to T6).
           TT              Connects a triangular surface patch A(T3 to T6) with a triangular surface patch B(T3 to T6).
           TQ              Connects a triangular surface patch A(T3 to T6) with a quadrilateral surface patch B(Q4 to Q8).
           Q               Connects the shell vertex grid GS with a quadrilateral surface patch A(Q4 to Q8) if surface patch B is not specified.
           T               Connects the shell vertex grid GS with a triangular surface patch A (T3 to T6) if surface patch B is not specified.
        """
        return self.__cardinfo.SPTYP

    @SPTYP.setter
    def SPTYP(self, value: str) -> None:
        self.__cardinfo.SPTYP = value
        self.last_status_message()

    @property
    def GAI(self) -> list[int]:
        """
           CardGrid identification numbers of surface patch A.GA1 to GA3 are required. See Remark 10. (Integer > 0)
           * Remark 10:
           GAi are required for the format "GRIDID". At least 3 and at most 8 grid IDs may be specified for GAi and GBi, respectively.The rules of the triangular
           and quadrilateral elements apply for the order of GAi and GBi, see Figure 8-75. Missing midside nodes are allowed.
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.GAI), self.__cardinfo.GAI)

    @GAI.setter
    def GAI(self, value: list[int]) -> None:
        self.__cardinfo.GAI = value
        self.last_status_message()

    @property
    def GBI(self) -> list[int]:
        """
           CardGrid identification numbers of surface patch B. See Remark 10. (Integer > 0)
           * Remark 10:
           GAi are required for the format "GRIDID". At least 3 and at most 8 grid IDs may be specified for GAi and GBi, respectively.The rules of the triangular
           and quadrilateral elements apply for the order of GAi and GBi, see Figure 8-75. Missing midside nodes are allowed.
        """
        return self.__cardinfo.GBI

    @GBI.setter
    def GBI(self, value: list[int]) -> None:
        self.__cardinfo.GBI = value
        self.last_status_message()



class GRID(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def ID(self) -> int:
        """
           CardCardGrid point identification number. (0 < Integer < 100000000)
        """
        return self.__cardinfo.ID

    @ID.setter
    def ID(self, value: int) -> None:
        self.__cardinfo.ID = value
        self.last_status_message()
        

    @property
    def CP(self) -> int:
        """
           Identification number of coordinate system in which the location of the grid point is defined. (Integer >= 0 or blank*)
        """
        return self.__cardinfo.CP

    @CP.setter
    def CP(self, value: int) -> None:
        self.__cardinfo.CP = value
        self.last_status_message()

    @property
    def X1(self) -> float:
        """
           Location of the grid point in coordinate system CP. (Real; Default = 0.0)
        """
        return self.__cardinfo.X1

    @X1.setter
    def X1(self, value: float) -> None:
        self.__cardinfo.X1 = value
        self.last_status_message()

    @property
    def X2(self) -> float:
        """
           Location of the grid point in coordinate system CP. (Real; Default = 0.0)
        """
        return self.__cardinfo.X2

    @X2.setter
    def X2(self, value: float) -> None:
        self.__cardinfo.X2 = value
        self.last_status_message()

    @property
    def X3(self) -> float:
        """
           Location of the grid point in coordinate system CP. (Real; Default = 0.0)
        """
        return self.__cardinfo.X3

    @X3.setter
    def X3(self, value: float) -> None:
        self.__cardinfo.X3 = value
        self.last_status_message()

    @property
    def CD(self) -> int:
        """
           Identification number of coordinate system in which the displacements, degrees-of-freedom, constraints,
           and solution vectors are defined at the grid point. (Integer >= -1 or blank)*
        """
        return self.__cardinfo.CD

    @CD.setter
    def CD(self, value: int) -> None:
        self.__cardinfo.CD = value
        self.last_status_message()

    @property
    def PS(self) -> int:
        """
           Permanent single-point constraints associated with the grid point.
           (Any of the Integers 1 through 6 with no embedded blanks, or blank*.)
        """
        return self.__cardinfo.PS

    @PS.setter
    def PS(self, value: int) -> None:
        self.__cardinfo.PS = value
        self.last_status_message()

    @property
    def SEID(self) -> int:
        """
           Superelement identification number. (Integer >= 0; Default = 0)
        """
        return self.__cardinfo.SEID

    @SEID.setter
    def SEID(self, value: int) -> None:
        self.__cardinfo.SEID = value
        self.last_status_message()


class LOAD(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def SID(self) -> int:
        """
           Load set identification number. (Integer > 0)
        """
        return self.__cardinfo.SID
    
    @SID.setter
    def SID(self, value: int) -> None:
        self.__cardinfo.SID = value
        self.last_status_message()
    
    @property
    def S(self) -> float:
        """
        Overall scale factor. (Real)
        """
        return self.__cardinfo.S
    
    @S.setter
    def S(self, value: float) -> None:
        self.__cardinfo.S = value
        self.last_status_message()

    def get_all_scale_factors(self) -> list[float]:
        """
        Returns a list of all scale factors associated with each Load set.
        """
        return self.__cardinfo.GetAllScaleFactors()
    
    def set_scale_factor(self, index: int, scale_factor: float) -> None:
        """
        Sets the scale factor for a specific Load set by index.
        """
        self.__cardinfo.SetScaleFactor(index, scale_factor)
        self.last_status_message()

    def get_all_load_set_ids(self) -> list[int]:
        """
        Load set identification numbers defined on entry types listed above. (Integer > 0)
        """
        return self.__cardinfo.GetAllLoadSetIDs()
    
    def set_load_set_id(self, index: int, load_set_id: int) -> None:
        """
        Sets the load set ID for a specific Load set by index.
        """
        self.__cardinfo.SetLoadSetID(index, load_set_id)
        self.last_status_message()
    


class MAT10NAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat10Nas)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def BULK(self) -> float:
        """
           Bulk modulus. (Real > 0.0)
        """
        return self.__cardinfo.BULK

    @BULK.setter
    def BULK(self, value: float) -> None:
        self.__cardinfo.BULK = value

    @property
    def RHO(self) -> float:
        """
           Mass density. (Real > 0.0)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def C(self) -> float:
        """
           Speed of sound. (Real > 0.0)
        """
        return self.__cardinfo.C

    @C.setter
    def C(self, value: float) -> None:
        self.__cardinfo.C = value

    @property
    def GE(self) -> float:
        """
           Fluid element damping coefficient. (Real)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value


class MAT10OPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat10Opt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Unique material identification. No default (Integer > 0 or <String>)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def BULK(self) -> float:
        """
           Bulk modulus. No default (Real > 0.0)
        """
        return self.__cardinfo.BULK

    @BULK.setter
    def BULK(self, value: float) -> None:
        self.__cardinfo.BULK = value

    @property
    def RHO(self) -> float:
        """
           Mass density. Automatically computes the mass. No default (Real > 0.0)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def C(self) -> float:
        """
           Speed of sound. No default (Real > 0.0)
        """
        return self.__cardinfo.C

    @C.setter
    def C(self, value: float) -> None:
        self.__cardinfo.C = value

    @property
    def GE(self) -> float:
        """
           Fluid element damping coefficient. No default (Real)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def ALPHA(self) -> float:
        """
           Normalized porous material damping coefficient. Since the admittance is a function of frequency, the value of ALPHA should be chosen for the frequency range
           of interest for the analysis. No default (Real)
        """
        return self.__cardinfo.ALPHA

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA = value


class MAT1NAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value
        self.last_status_message()

    @property
    def E(self) -> float:
        """
           Young’s modulus. (Real > 0.0 or blank)
        """
        return self.__cardinfo.E

    @E.setter
    def E(self, value: float) -> None:
        self.__cardinfo.E = value
        self.last_status_message()

    @property
    def G(self) -> float:
        """
           Shear modulus. (Real > 0.0 or blank)
        """
        return self.__cardinfo.G

    @G.setter
    def G(self, value: float) -> None:
        self.__cardinfo.G = value
        self.last_status_message()

    @property
    def NU(self) -> float:
        """
           Poisson’s ratio. (-1.0 < Real < 0.5 or blank)
        """
        return self.__cardinfo.NU

    @NU.setter
    def NU(self, value: float) -> None:
        self.__cardinfo.NU = value
        self.last_status_message()

    @property
    def RHO(self) -> float:
        """
           Mass density. See Remark 5. (Real)
           * Remark 5:
           The mass density RHO will be used to compute mass for all structural elements automatically.
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value
        self.last_status_message()

    @property
    def A(self) -> float:
        """
           Thermal expansion coefficient. (Real)
        """
        return self.__cardinfo.A

    @A.setter
    def A(self, value: float) -> None:
        self.__cardinfo.A = value
        self.last_status_message()

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation of thermal loads, or a temperature-dependent thermal expansion coefficient. See Remarks 9. and 10.
           (Real; Default = 0.0 if A is specified.)
           * Remark 9:
           TREF and GE are ignored if the MAT1 entry is referenced by a PCOMP entry.
           * Remark 10:
           TREF is used in two different ways:
           • In nonlinear static analysis(SOL 106), TREF is used only for the calculation of a temperature-dependent thermal expansion coefficient.
           The reference temperature for the calculation of thermal loads is obtained from the TEMPERATURE(INITIAL) set selection.
           • In all SOLs except 106, TREF is used only as the reference temperature for the calculation of thermal loads.TEMPERATURE(INITIAL) may
           be used for this purpose, but TREF must be blank.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value
        self.last_status_message()

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. See Remarks 8., 9., and 4. (Real)
           * Remark 8:
           To obtain the damping coefficient GE, multiply the critical damping ratio C ⁄ C0, by 2.0.
           * Remark 9:
           TREF and GE are ignored if the MAT1 entry is referenced by a PCOMP entry.
           * Remark 4:
           MAT1 materials may be made temperature-dependent by use of the MATT1 entry.In SOL 106, linear and nonlinear elastic material properties in the
           residual structure will be updated as prescribed under the TEMPERATURE Case Control command.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value
        self.last_status_message()

    @property
    def ST(self) -> float:
        """
           Stress limits for tension, compression, and shear are optionally supplied, used only to compute margins of safety in certain elements;
           and have no effect on the computational procedures.See “Beam Element (CBEAM)” in Chapter 3 of the MSC.Nastran Reference Guide. (Real > 0.0 or blank)
        """
        return self.__cardinfo.ST

    @ST.setter
    def ST(self, value: float) -> None:
        self.__cardinfo.ST = value
        self.last_status_message()

    @property
    def SC(self) -> float:
        """
           SC
        """
        return self.__cardinfo.SC

    @SC.setter
    def SC(self, value: float) -> None:
        self.__cardinfo.SC = value
        self.last_status_message()

    @property
    def SS(self) -> float:
        """
           SS
        """
        return self.__cardinfo.SS

    @SS.setter
    def SS(self, value: float) -> None:
        self.__cardinfo.SS = value
        self.last_status_message()

    @property
    def MCSID(self) -> int:
        """
           Material coordinate system identification number. Used only for PARAM,CURV processing.See “Parameters” on page 631. (Integer > 0 or blank)
        """
        return self.__cardinfo.MCSID

    @MCSID.setter
    def MCSID(self, value: int) -> None:
        self.__cardinfo.MCSID = value
        self.last_status_message()


class MAT1OPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat1Opt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def E(self) -> float:
        """
           Young’s modulus. (Real > 0.0 or blank)
        """
        return self.__cardinfo.E

    @E.setter
    def E(self, value: float) -> None:
        self.__cardinfo.E = value

    @property
    def G(self) -> float:
        """
           Shear modulus. (Real > 0.0 or blank)
        """
        return self.__cardinfo.G

    @G.setter
    def G(self, value: float) -> None:
        self.__cardinfo.G = value

    @property
    def NU(self) -> float:
        """
           Poisson’s ratio. If < 0.0, a warning is issued. (-1.0 < Real < 0.5 or blank)
        """
        return self.__cardinfo.NU

    @NU.setter
    def NU(self, value: float) -> None:
        self.__cardinfo.NU = value

    @property
    def RHO(self) -> float:
        """
           Mass density. Used to automatically compute mass for all structural elements. No default (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def A(self) -> float:
        """
           Thermal expansion coefficient. No default (Real)
        """
        return self.__cardinfo.A

    @A.setter
    def A(self, value: float) -> None:
        self.__cardinfo.A = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for thermal loading. Default = 0.0 (Real)
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. No default (Real)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def ST(self) -> float:
        """
           Stress limits in tension, compression and shear. Used for composite ply failure calculations. No default (Real)
        """
        return self.__cardinfo.ST

    @ST.setter
    def ST(self, value: float) -> None:
        self.__cardinfo.ST = value

    @property
    def SC(self) -> float:
        """
           SC
        """
        return self.__cardinfo.SC

    @SC.setter
    def SC(self, value: float) -> None:
        self.__cardinfo.SC = value

    @property
    def SS(self) -> float:
        """
           SS
        """
        return self.__cardinfo.SS

    @SS.setter
    def SS(self, value: float) -> None:
        self.__cardinfo.SS = value

    @property
    def MODULI(self) -> str:
        """
           Continuation line flag for moduli temporal property.
        """
        return self.__cardinfo.MODULI

    @MODULI.setter
    def MODULI(self, value: str) -> None:
        self.__cardinfo.MODULI = value

    @property
    def MTIME(self) -> str:
        """
           Material temporal property. This field controls the interpretation of the input material property for viscoelasticity.
           INSTANT
           This material property is considered as the Instantaneous material input for viscoelasticity on the MATVE entry.
           LONG(Default)
           This material property is considered as the Long-term relaxed material input for viscoelasticity on the MATVE entry.
        """
        return self.__cardinfo.MTIME

    @MTIME.setter
    def MTIME(self, value: str) -> None:
        self.__cardinfo.MTIME = value


class MAT2NAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def MID(self) -> int:
        """
           Material identification number. See Remark 13. (Integer > 0)
           * Remark 13:
           PCOMP entries generate MAT2 entries equal to 100,000,000 plus the PCOMP PID.Explicitly specified MAT2 IDs must not conflict with internally
           generated MAT2 IDs.Furthermore, if MID is greater than 400,000,000 then A1, A2, and A3 are a special format. They are [G4] ⋅ [α4] not [α4]. If MIDs
           larger than 99999999 are used, PARAM, NOCOMPS,-1 must be specified to obtain stress output.
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value
        self.last_status_message()

    @property
    def G11(self) -> float:
        """
           The material property matrix. (Real)
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: float) -> None:
        self.__cardinfo.G11 = value
        self.last_status_message()

    @property
    def G12(self) -> float:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: float) -> None:
        self.__cardinfo.G12 = value
        self.last_status_message()

    @property
    def G13(self) -> float:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: float) -> None:
        self.__cardinfo.G13 = value
        self.last_status_message()

    @property
    def G22(self) -> float:
        """
           G22
        """
        return self.__cardinfo.G22

    @G22.setter
    def G22(self, value: float) -> None:
        self.__cardinfo.G22 = value
        self.last_status_message()

    @property
    def G23(self) -> float:
        """
           G23
        """
        return self.__cardinfo.G23

    @G23.setter
    def G23(self, value: float) -> None:
        self.__cardinfo.G23 = value
        self.last_status_message()

    @property
    def G33(self) -> float:
        """
           G33
        """
        return self.__cardinfo.G33

    @G33.setter
    def G33(self, value: float) -> None:
        self.__cardinfo.G33 = value
        self.last_status_message()

    @property
    def RHO(self) -> float:
        """
           Mass density. (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value
        self.last_status_message()

    @property
    def A1(self) -> float:
        """
           Thermal expansion coefficient vector. (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value
        self.last_status_message()

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value
        self.last_status_message()

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value
        self.last_status_message()

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation of thermal loads, or a temperature-dependent thermal expansion coefficient. See Remarks 10 and 11.
           (Real or blank)
           * Remark 10:
           TREF and GE are ignored if this entry is referenced by a PCOMP entry.
           * Remark 11:
           TREF is used in two different ways:
           • In nonlinear static analysis(SOL 106), TREF is used only for the calculation of a temperature-dependent thermal expansion coefficient.
           The reference temperature for the calculation of thermal loads is obtained from the TEMPERATURE(INITIAL) set selection.
           • In all SOLs except 106, TREF is used only as the reference temperature for the calculation of thermal loads.TEMPERATURE(INITIAL) may
           be used for this purpose, but TREF must be blank.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value
        self.last_status_message()

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. See Remarks 7., 10., and 12. (Real)
           * Remark 7:
           To obtain the damping coefficient GE, multiply the critical damping ratio C ⁄ C0, by 2.0.
           * Remark 10:
           TREF and GE are ignored if the MAT1 entry is referenced by a PCOMP entry.
           * Remark 12:
           If PARAM,W4 is not specified, GE is ignored in transient analysis. See “Parameters” on page 631.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value
        self.last_status_message()

    @property
    def ST(self) -> float:
        """
           Stress limits for tension, compression, and shear are optionally supplied, used only to compute margins of safety in certain elements;
           and have no effect on the computational procedures.See “Beam Element (CBEAM)” in Chapter 3 of the MSC.Nastran Reference Guide. (Real or blank)
        """
        return self.__cardinfo.ST

    @ST.setter
    def ST(self, value: float) -> None:
        self.__cardinfo.ST = value
        self.last_status_message()

    @property
    def SC(self) -> float:
        """
           SC
        """
        return self.__cardinfo.SC

    @SC.setter
    def SC(self, value: float) -> None:
        self.__cardinfo.SC = value
        self.last_status_message()

    @property
    def SS(self) -> float:
        """
           SS
        """
        return self.__cardinfo.SS

    @SS.setter
    def SS(self, value: float) -> None:
        self.__cardinfo.SS = value
        self.last_status_message()

    @property
    def MCSID(self) -> int:
        """
           Material coordinate system identification number. Used only for PARAM,CURV processing.See “Parameters” on page 631. (Integer >= 0 or blank)
        """
        return self.__cardinfo.MCSID

    @MCSID.setter
    def MCSID(self, value: int) -> None:
        self.__cardinfo.MCSID = value
        self.last_status_message()

    @property
    def GE11(self) -> float:
        """
           Structural damping matrix
        """
        return self.__cardinfo.GE11

    @GE11.setter
    def GE11(self, value: float) -> None:
        self.__cardinfo.GE11 = value
        self.last_status_message()

    @property
    def GE12(self) -> float:
        """
           GE12
        """
        return self.__cardinfo.GE12

    @GE12.setter
    def GE12(self, value: float) -> None:
        self.__cardinfo.GE12 = value
        self.last_status_message()

    @property
    def GE13(self) -> float:
        """
           GE13
        """
        return self.__cardinfo.GE13

    @GE13.setter
    def GE13(self, value: float) -> None:
        self.__cardinfo.GE13 = value
        self.last_status_message()

    @property
    def GE22(self) -> float:
        """
           GE22
        """
        return self.__cardinfo.GE22

    @GE22.setter
    def GE22(self, value: float) -> None:
        self.__cardinfo.GE22 = value
        self.last_status_message()

    @property
    def GE23(self) -> float:
        """
           GE23
        """
        return self.__cardinfo.GE23

    @GE23.setter
    def GE23(self, value: float) -> None:
        self.__cardinfo.GE23 = value
        self.last_status_message()

    @property
    def GE33(self) -> float:
        """
           GE33
        """
        return self.__cardinfo.GE33

    @GE33.setter
    def G33(self, value: float) -> None:
        self.__cardinfo.GE33 = value
        self.last_status_message()


class MAT2OPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat2Opt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def G11(self) -> float:
        """
           The material property matrix. No default. (Real)
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: float) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> float:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: float) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> float:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: float) -> None:
        self.__cardinfo.G13 = value

    @property
    def G22(self) -> float:
        """
           G22
        """
        return self.__cardinfo.G22

    @G22.setter
    def G22(self, value: float) -> None:
        self.__cardinfo.G22 = value

    @property
    def G23(self) -> float:
        """
           G23
        """
        return self.__cardinfo.G23

    @G23.setter
    def G23(self, value: float) -> None:
        self.__cardinfo.G23 = value

    @property
    def G33(self) -> float:
        """
           G33
        """
        return self.__cardinfo.G33

    @G33.setter
    def G33(self, value: float) -> None:
        self.__cardinfo.G33 = value

    @property
    def RHO(self) -> float:
        """
           Mass density. Used to automatically compute mass for all structural elements. No default (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def A1(self) -> float:
        """
           Thermal expansion coefficient vector. No default (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation of thermal loads. Data from the MAT2 entry is used directly, without adjustment of equivalent E, G, or NU values.
           Default = blank(Real or blank)
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. No default (Real)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def ST(self) -> float:
        """
           Stress limits in tension, compression and shear. Used for composite ply failure calculations. No default (Real)
        """
        return self.__cardinfo.ST

    @ST.setter
    def ST(self, value: float) -> None:
        self.__cardinfo.ST = value

    @property
    def SC(self) -> float:
        """
           SC
        """
        return self.__cardinfo.SC

    @SC.setter
    def SC(self, value: float) -> None:
        self.__cardinfo.SC = value

    @property
    def SS(self) -> float:
        """
           SS
        """
        return self.__cardinfo.SS

    @SS.setter
    def SS(self, value: float) -> None:
        self.__cardinfo.SS = value


class MAT3(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat3)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def EX(self) -> float:
        """
           Young’s moduli in the x, , and z directions, respectively. (Real > 0.0)
        """
        return self.__cardinfo.EX

    @EX.setter
    def EX(self, value: float) -> None:
        self.__cardinfo.EX = value

    @property
    def ETH(self) -> float:
        """
           ETH
        """
        return self.__cardinfo.ETH

    @ETH.setter
    def ETH(self, value: float) -> None:
        self.__cardinfo.ETH = value

    @property
    def EZ(self) -> float:
        """
           EZ
        """
        return self.__cardinfo.EZ

    @EZ.setter
    def EZ(self, value: float) -> None:
        self.__cardinfo.EZ = value

    @property
    def NUXTH(self) -> float:
        """
           Poisson’s ratios (coupled strain ratios in the x , z , and zx directions, respectively). (Real)
        """
        return self.__cardinfo.NUXTH

    @NUXTH.setter
    def NUXTH(self, value: float) -> None:
        self.__cardinfo.NUXTH = value

    @property
    def NUTHZ(self) -> float:
        """
           NUTHZ
        """
        return self.__cardinfo.NUTHZ

    @NUTHZ.setter
    def NUTHZ(self, value: float) -> None:
        self.__cardinfo.NUTHZ = value

    @property
    def NUZX(self) -> float:
        """
           NUZX
        """
        return self.__cardinfo.NUZX

    @NUZX.setter
    def NUZX(self, value: float) -> None:
        self.__cardinfo.NUZX = value

    @property
    def RHO(self) -> float:
        """
           Mass density. (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def GZX(self) -> float:
        """
           Shear modulus. (Real > 0.0)
        """
        return self.__cardinfo.GZX

    @GZX.setter
    def GZX(self, value: float) -> None:
        self.__cardinfo.GZX = value

    @property
    def AX(self) -> float:
        """
           Thermal expansion coefficients. (Real)
        """
        return self.__cardinfo.AX

    @AX.setter
    def AX(self, value: float) -> None:
        self.__cardinfo.AX = value

    @property
    def ATH(self) -> float:
        """
           ATH
        """
        return self.__cardinfo.ATH

    @ATH.setter
    def ATH(self, value: float) -> None:
        self.__cardinfo.ATH = value

    @property
    def AZ(self) -> float:
        """
           AZ
        """
        return self.__cardinfo.AZ

    @AZ.setter
    def AZ(self, value: float) -> None:
        self.__cardinfo.AZ = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation of thermal loads or a temperature-dependent thermal expansion coefficient. See Remark 10. (Real or blank)
           * Remark 10:
           TREF is used for two different purposes:
           • In nonlinear static analysis(SOL 106), TREF is used only for the calculation of a temperature-dependent thermal expansion
           coefficient.The reference temperature for the calculation of thermal loads is obtained from the TEMPERATURE(INITIAL) set selection. See Remark 10.
           under the MAT1 description.
           • In all SOLs except 106, TREF is used only as the reference temperature for the calculation of thermal loads.TEMPERATURE(INITIAL) may
           be used for this purpose, but TREF must be blank.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. See Remarks 9. and 11. (Real)
           * Remark 9:
           To obtain the damping coefficient GE, multiply the critical damping ratio C ⁄ C0 by 2.0.
           * Remark 11:
           If PARAM,W4 is not specified, GE is ignored in transient analysis. See “Parameters” on page 631.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value


class MAT4(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat4)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def K(self) -> float:
        """
           Thermal conductivity. (Blank or Real > 0.0)
        """
        return self.__cardinfo.K

    @K.setter
    def K(self, value: float) -> None:
        self.__cardinfo.K = value

    @property
    def CP(self) -> float:
        """
           Heat capacity per unit mass at constant pressure (specific heat). (Blank or Real > 0.0)
        """
        return self.__cardinfo.CP

    @CP.setter
    def CP(self, value: float) -> None:
        self.__cardinfo.CP = value

    @property
    def p(self) -> float:
        """
           Density. (Real > 0.0; Default = 1.0)
        """
        return self.__cardinfo.p

    @p.setter
    def p(self, value: float) -> None:
        self.__cardinfo.p = value

    @property
    def H(self) -> float:
        """
           Free convection heat transfer coefficient. (Real or blank)
        """
        return self.__cardinfo.H

    @H.setter
    def H(self, value: float) -> None:
        self.__cardinfo.H = value

    @property
    def u(self) -> float:
        """
           Dynamic viscosity. See Remark 2. (Real > 0.0 or blank)
        """
        return self.__cardinfo.u

    @u.setter
    def u(self, value: float) -> None:
        self.__cardinfo.u = value

    @property
    def HGEN(self) -> float:
        """
           Heat generation capability used with QVOL entries. (Real > 0.0; Default = 1.0)
        """
        return self.__cardinfo.HGEN

    @HGEN.setter
    def HGEN(self, value: float) -> None:
        self.__cardinfo.HGEN = value

    @property
    def REFENTH(self) -> float:
        """
           Reference enthalpy. (Real or blank)
        """
        return self.__cardinfo.REFENTH

    @REFENTH.setter
    def REFENTH(self, value: float) -> None:
        self.__cardinfo.REFENTH = value

    @property
    def TCH(self) -> float:
        """
           Lower temperature limit at which phase change region is to occur. (Real or blank)
        """
        return self.__cardinfo.TCH

    @TCH.setter
    def TCH(self, value: float) -> None:
        self.__cardinfo.TCH = value

    @property
    def TDELTA(self) -> float:
        """
           Total temperature change range within which a phase change is to occur. (Real > 0.0 or blank)
        """
        return self.__cardinfo.TDELTA

    @TDELTA.setter
    def TDELTA(self, value: float) -> None:
        self.__cardinfo.TDELTA = value

    @property
    def QLAT(self) -> float:
        """
           Latent heat of fusion per unit mass associated with the phase change. (Real > 0.0 or blank)
        """
        return self.__cardinfo.QLAT

    @QLAT.setter
    def QLAT(self, value: float) -> None:
        self.__cardinfo.QLAT = value


class MAT5(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat5)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def KXX(self) -> float:
        """
           Thermal conductivity. (Real)
        """
        return self.__cardinfo.KXX

    @KXX.setter
    def KXX(self, value: float) -> None:
        self.__cardinfo.KXX = value

    @property
    def KXY(self) -> float:
        """
           KXY
        """
        return self.__cardinfo.KXY

    @KXY.setter
    def KXY(self, value: float) -> None:
        self.__cardinfo.KXY = value

    @property
    def KXZ(self) -> float:
        """
           KXZ
        """
        return self.__cardinfo.KXZ

    @KXZ.setter
    def KXZ(self, value: float) -> None:
        self.__cardinfo.KXZ = value

    @property
    def KYY(self) -> float:
        """
           KYY
        """
        return self.__cardinfo.KYY

    @KYY.setter
    def KYY(self, value: float) -> None:
        self.__cardinfo.KYY = value

    @property
    def KYZ(self) -> float:
        """
           KYZ
        """
        return self.__cardinfo.KYZ

    @KYZ.setter
    def KYZ(self, value: float) -> None:
        self.__cardinfo.KYZ = value

    @property
    def KZZ(self) -> float:
        """
           KZZ
        """
        return self.__cardinfo.KZZ

    @KZZ.setter
    def KZZ(self, value: float) -> None:
        self.__cardinfo.KZZ = value

    @property
    def CP(self) -> float:
        """
           Heat capacity per unit mass. (Real > 0.0 or blank)
        """
        return self.__cardinfo.CP

    @CP.setter
    def CP(self, value: float) -> None:
        self.__cardinfo.CP = value

    @property
    def RHO(self) -> float:
        """
           Density. (Real>0.0; Default=1.0)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def HGEN(self) -> float:
        """
           Heat generation capability used with QVOL entries. (Real > 0.0; Default = 1.0)
        """
        return self.__cardinfo.HGEN

    @HGEN.setter
    def HGEN(self, value: float) -> None:
        self.__cardinfo.HGEN = value


class MAT8(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def MID(self) -> int:
        """
           Material identification number. Referenced on a PSHELL or PCOMP entry only. (0 < Integer< 100,000,000)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value
        self.last_status_message()

    @property
    def E1(self) -> float:
        """
           Modulus of elasticity in longitudinal direction, also defined as the fiber direction or 1-direction. (Real ≠ 0.0)
        """
        return self.__cardinfo.E1

    @E1.setter
    def E1(self, value: float) -> None:
        self.__cardinfo.E1 = value
        self.last_status_message()

    @property
    def E2(self) -> float:
        """
           Modulus of elasticity in lateral direction, also defined as the matrix direction or 2-direction. (Real ≠ 0.0)
        """
        return self.__cardinfo.E2

    @E2.setter
    def E2(self, value: float) -> None:
        self.__cardinfo.E2 = value
        self.last_status_message()

    @property
    def NU12(self) -> float:
        """
           Poisson’s ratio (ε2 ⁄ ε1 for uniaxial loading in 1-direction). Note that υ21 = ε1 ⁄ ε2 for uniaxial loading in 2-direction is related to 12, E1, and E2
           by the relation υ12E2 = υ21E1. (Real)
        """
        return self.__cardinfo.NU12

    @NU12.setter
    def NU12(self, value: float) -> None:
        self.__cardinfo.NU12 = value
        self.last_status_message()

    @property
    def G12(self) -> float:
        """
           In-plane shear modulus. (Real > 0.0; Default = 0.0)
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: float) -> None:
        self.__cardinfo.G12 = value
        self.last_status_message()

    @property
    def G1Z(self) -> float:
        """
           Transverse shear modulus for shear in 1-Z plane. (Real > 0.0; Default implies infinite shear modulus.)
        """
        return self.__cardinfo.G1Z

    @G1Z.setter
    def G1Z(self, value: float) -> None:
        self.__cardinfo.G1Z = value
        self.last_status_message()

    @property
    def G2Z(self) -> float:
        """
           Transverse shear modulus for shear in 2-Z plane. (Real > 0.0; Default implies infinite shear modulus.)
        """
        return self.__cardinfo.G2Z

    @G2Z.setter
    def G2Z(self, value: float) -> None:
        self.__cardinfo.G2Z = value
        self.last_status_message()

    @property
    def RHO(self) -> float:
        """
           Mass density. (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value
        self.last_status_message()

    @property
    def A1(self) -> float:
        """
           Thermal expansion coefficient in i-direction. (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value
        self.last_status_message()

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value
        self.last_status_message()

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation of thermal loads, or a temperature-dependent thermal expansion coefficient.See Remarks 4. and 5. (Real or blank)
           * Remark 4:
           Xt, Yt, and S are required for composite element failure calculations when requested in the FT field of the PCOMP entry.Xc and Yc are also used but
           not required.
           * Remark 5:
           TREF and GE are ignored if this entry is referenced by a PCOMP entry.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value
        self.last_status_message()

    @property
    def Xt(self) -> float:
        """
           Allowable stresses or strains in tension and compression, respectively, in the longitudinal direction.Required if failure index is desired. See
           the FT field on the PCOMP entry. (Real > 0.0; Default value for Xc is Xt.)
        """
        return self.__cardinfo.Xt

    @Xt.setter
    def Xt(self, value: float) -> None:
        self.__cardinfo.Xt = value
        self.last_status_message()

    @property
    def Xc(self) -> float:
        """
           Xc
        """
        return self.__cardinfo.Xc

    @Xc.setter
    def Xc(self, value: float) -> None:
        self.__cardinfo.Xc = value
        self.last_status_message()

    @property
    def Yt(self) -> float:
        """
           Allowable stresses or strains in tension and compression, respectively, in the lateral direction.Required if failure index is desired. (Real > 0.0;
           Default value for Yc is Yt.)
        """
        return self.__cardinfo.Yt

    @Yt.setter
    def Yt(self, value: float) -> None:
        self.__cardinfo.Yt = value
        self.last_status_message()

    @property
    def Yc(self) -> float:
        """
           Yc
        """
        return self.__cardinfo.Yc

    @Yc.setter
    def Yc(self, value: float) -> None:
        self.__cardinfo.Yc = value
        self.last_status_message()

    @property
    def S(self) -> float:
        """
           Allowable stress or strain for in-plane shear. See the FT field on the PCOMP entry. (Real > 0.0)
        """
        return self.__cardinfo.S

    @S.setter
    def S(self, value: float) -> None:
        self.__cardinfo.S = value
        self.last_status_message()

    @property
    def GE(self) -> float:
        """
           Structural damping coefficient. See Remarks 4. and 6. (Real)
           * Remark 4:
           Xt, Yt, and S are required for composite element failure calculations when requested in the FT field of the PCOMP entry.Xc and Yc are also used but
           not required.
           * Remark 6:
           TREF is used in two different ways:
           • In nonlinear static analysis(SOL 106), TREF is used only for the calculation of a temperature-dependent thermal expansion
           coefficient.The reference temperature for the calculation of thermal loads is obtained from the TEMPERATURE(INITIAL) set selection.
           See Figure 8-94 in Remark 10. in the MAT1 description.
           • In all SOLs except 106, TREF is used only as the reference temperature for the calculation of thermal loads.TEMPERATURE(INITIAL) may
           be used for this purpose, but TREF must then be blank.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value
        self.last_status_message()

    @property
    def F12(self) -> float:
        """
           Interaction term in the tensor polynomial theory of Tsai-Wu. Required if failure index by Tsai-Wu theory is desired and if value of F12 is
           different from 0.0. See the FT field on the PCOMP entry. (Real)
        """
        return self.__cardinfo.F12

    @F12.setter
    def F12(self, value: float) -> None:
        self.__cardinfo.F12 = value
        self.last_status_message()

    @property
    def STRN(self) -> float:
        """
           For the maximum strain theory only (see STRN in PCOMP entry). Indicates whether Xt, Xc, Yt, Yc, and S are stress or strain allowables.
           [Real = 1.0 for strain allowables; blank(Default) for stress allowables.]
        """
        return self.__cardinfo.STRN

    @STRN.setter
    def STRN(self, value: float) -> None:
        self.__cardinfo.STRN = value
        self.last_status_message()


class MAT9NAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat9Nas)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def G11(self) -> float:
        """
           Elements of the 6 x 6 symmetric material property matrix in the material coordinate system. (Real)
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: float) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> float:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: float) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> float:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: float) -> None:
        self.__cardinfo.G13 = value

    @property
    def G14(self) -> float:
        """
           G14
        """
        return self.__cardinfo.G14

    @G14.setter
    def G14(self, value: float) -> None:
        self.__cardinfo.G14 = value

    @property
    def G15(self) -> float:
        """
           G15
        """
        return self.__cardinfo.G15

    @G15.setter
    def G15(self, value: float) -> None:
        self.__cardinfo.G15 = value

    @property
    def G16(self) -> float:
        """
           G16
        """
        return self.__cardinfo.G16

    @G16.setter
    def G16(self, value: float) -> None:
        self.__cardinfo.G16 = value

    @property
    def G22(self) -> float:
        """
           G22
        """
        return self.__cardinfo.G22

    @G22.setter
    def G22(self, value: float) -> None:
        self.__cardinfo.G22 = value

    @property
    def G23(self) -> float:
        """
           G23
        """
        return self.__cardinfo.G23

    @G23.setter
    def G23(self, value: float) -> None:
        self.__cardinfo.G23 = value

    @property
    def G24(self) -> float:
        """
           G24
        """
        return self.__cardinfo.G24

    @G24.setter
    def G24(self, value: float) -> None:
        self.__cardinfo.G24 = value

    @property
    def G25(self) -> float:
        """
           G25
        """
        return self.__cardinfo.G25

    @G25.setter
    def G25(self, value: float) -> None:
        self.__cardinfo.G25 = value

    @property
    def G26(self) -> float:
        """
           G26
        """
        return self.__cardinfo.G26

    @G26.setter
    def G26(self, value: float) -> None:
        self.__cardinfo.G26 = value

    @property
    def G33(self) -> float:
        """
           G33
        """
        return self.__cardinfo.G33

    @G33.setter
    def G33(self, value: float) -> None:
        self.__cardinfo.G33 = value

    @property
    def G34(self) -> float:
        """
           G34
        """
        return self.__cardinfo.G34

    @G34.setter
    def G34(self, value: float) -> None:
        self.__cardinfo.G34 = value

    @property
    def G35(self) -> float:
        """
           G35
        """
        return self.__cardinfo.G35

    @G35.setter
    def G35(self, value: float) -> None:
        self.__cardinfo.G35 = value

    @property
    def G36(self) -> float:
        """
           G36
        """
        return self.__cardinfo.G36

    @G36.setter
    def G36(self, value: float) -> None:
        self.__cardinfo.G36 = value

    @property
    def G44(self) -> float:
        """
           G44
        """
        return self.__cardinfo.G44

    @G44.setter
    def G44(self, value: float) -> None:
        self.__cardinfo.G44 = value

    @property
    def G45(self) -> float:
        """
           G45
        """
        return self.__cardinfo.G45

    @G45.setter
    def G45(self, value: float) -> None:
        self.__cardinfo.G45 = value

    @property
    def G46(self) -> float:
        """
           G46
        """
        return self.__cardinfo.G46

    @G46.setter
    def G46(self, value: float) -> None:
        self.__cardinfo.G46 = value

    @property
    def G55(self) -> float:
        """
           G55
        """
        return self.__cardinfo.G55

    @G55.setter
    def G55(self, value: float) -> None:
        self.__cardinfo.G55 = value

    @property
    def G56(self) -> float:
        """
           G56
        """
        return self.__cardinfo.G56

    @G56.setter
    def G56(self, value: float) -> None:
        self.__cardinfo.G56 = value

    @property
    def G66(self) -> float:
        """
           G66
        """
        return self.__cardinfo.G66

    @G66.setter
    def G66(self, value: float) -> None:
        self.__cardinfo.G66 = value

    @property
    def RHO(self) -> float:
        """
           Mass density. (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def A1(self) -> float:
        """
           Thermal expansion coefficient. (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value

    @property
    def A4(self) -> float:
        """
           A4
        """
        return self.__cardinfo.A4

    @A4.setter
    def A4(self, value: float) -> None:
        self.__cardinfo.A4 = value

    @property
    def A5(self) -> float:
        """
           A5
        """
        return self.__cardinfo.A5

    @A5.setter
    def A5(self, value: float) -> None:
        self.__cardinfo.A5 = value

    @property
    def A6(self) -> float:
        """
           A6
        """
        return self.__cardinfo.A6

    @A6.setter
    def A6(self, value: float) -> None:
        self.__cardinfo.A6 = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation thermal loads, or a temperature-dependent thermal expansion coefficient.See Remark 7. (Real or blank)
           * Remark 7:
           TREF is used in two different ways:
           • In nonlinear static analysis(e.g., SOL 106), TREF is used only for the calculation of a temperature-dependent thermal expansion
           coefficient.The reference temperature for the calculation of thermal loads is obtained from the TEMPERATURE(INITIAL) set selection.
           See Figure 5-91 in Remark 10. in the MAT1 description.
           • In all solutions except nonlinear static analysis, TREF is used only as the reference temperature for the calculation of thermal loads.
           TEMPERATURE(INITIAL) may be used for this purpose, but TREF must then be blank.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. See Remarks 6. and 8. (Real)
           * Remark 6:
           The damping coefficient GE is given by GE = 2.0 * C / Co
           * Remark 8:
           If PARAM,W4 is not specified, GE is ignored in transient analysis. See “Parameters” on page 631.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value


class MAT9OPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat9Opt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Unique material identification. No default (Integer > 0 or <String>)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def G11(self) -> float:
        """
           The material property matrix. No default (Real)
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: float) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> float:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: float) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> float:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: float) -> None:
        self.__cardinfo.G13 = value

    @property
    def G14(self) -> float:
        """
           G14
        """
        return self.__cardinfo.G14

    @G14.setter
    def G14(self, value: float) -> None:
        self.__cardinfo.G14 = value

    @property
    def G15(self) -> float:
        """
           G15
        """
        return self.__cardinfo.G15

    @G15.setter
    def G15(self, value: float) -> None:
        self.__cardinfo.G15 = value

    @property
    def G16(self) -> float:
        """
           G16
        """
        return self.__cardinfo.G16

    @G16.setter
    def G16(self, value: float) -> None:
        self.__cardinfo.G16 = value

    @property
    def G22(self) -> float:
        """
           G22
        """
        return self.__cardinfo.G22

    @G22.setter
    def G22(self, value: float) -> None:
        self.__cardinfo.G22 = value

    @property
    def G23(self) -> float:
        """
           G23
        """
        return self.__cardinfo.G23

    @G23.setter
    def G23(self, value: float) -> None:
        self.__cardinfo.G23 = value

    @property
    def G24(self) -> float:
        """
           G24
        """
        return self.__cardinfo.G24

    @G24.setter
    def G24(self, value: float) -> None:
        self.__cardinfo.G24 = value

    @property
    def G25(self) -> float:
        """
           G25
        """
        return self.__cardinfo.G25

    @G25.setter
    def G25(self, value: float) -> None:
        self.__cardinfo.G25 = value

    @property
    def G26(self) -> float:
        """
           G26
        """
        return self.__cardinfo.G26

    @G26.setter
    def G26(self, value: float) -> None:
        self.__cardinfo.G26 = value

    @property
    def G33(self) -> float:
        """
           G33
        """
        return self.__cardinfo.G33

    @G33.setter
    def G33(self, value: float) -> None:
        self.__cardinfo.G33 = value

    @property
    def G34(self) -> float:
        """
           G34
        """
        return self.__cardinfo.G34

    @G34.setter
    def G34(self, value: float) -> None:
        self.__cardinfo.G34 = value

    @property
    def G35(self) -> float:
        """
           G35
        """
        return self.__cardinfo.G35

    @G35.setter
    def G35(self, value: float) -> None:
        self.__cardinfo.G35 = value

    @property
    def G36(self) -> float:
        """
           G36
        """
        return self.__cardinfo.G36

    @G36.setter
    def G36(self, value: float) -> None:
        self.__cardinfo.G36 = value

    @property
    def G44(self) -> float:
        """
           G44
        """
        return self.__cardinfo.G44

    @G44.setter
    def G44(self, value: float) -> None:
        self.__cardinfo.G44 = value

    @property
    def G45(self) -> float:
        """
           G45
        """
        return self.__cardinfo.G45

    @G45.setter
    def G45(self, value: float) -> None:
        self.__cardinfo.G45 = value

    @property
    def G46(self) -> float:
        """
           G46
        """
        return self.__cardinfo.G46

    @G46.setter
    def G46(self, value: float) -> None:
        self.__cardinfo.G46 = value

    @property
    def G55(self) -> float:
        """
           G55
        """
        return self.__cardinfo.G55

    @G55.setter
    def G55(self, value: float) -> None:
        self.__cardinfo.G55 = value

    @property
    def G56(self) -> float:
        """
           G56
        """
        return self.__cardinfo.G56

    @G56.setter
    def G56(self, value: float) -> None:
        self.__cardinfo.G56 = value

    @property
    def G66(self) -> float:
        """
           G66
        """
        return self.__cardinfo.G66

    @G66.setter
    def G66(self, value: float) -> None:
        self.__cardinfo.G66 = value

    @property
    def RHO(self) -> float:
        """
           Mass density. Used to automatically compute mass for all structural elements. No default (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def A1(self) -> float:
        """
           Thermal expansion coefficient vector. No default (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value

    @property
    def A4(self) -> float:
        """
           A4
        """
        return self.__cardinfo.A4

    @A4.setter
    def A4(self, value: float) -> None:
        self.__cardinfo.A4 = value

    @property
    def A5(self) -> float:
        """
           A5
        """
        return self.__cardinfo.A5

    @A5.setter
    def A5(self, value: float) -> None:
        self.__cardinfo.A5 = value

    @property
    def A6(self) -> float:
        """
           A6
        """
        return self.__cardinfo.A6

    @A6.setter
    def A6(self, value: float) -> None:
        self.__cardinfo.A6 = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation of thermal loads. Default = blank(Real or blank)
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. No default (Real)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def MODULI(self) -> str:
        """
           Continuation line flag for moduli temporal property.
        """
        return self.__cardinfo.MODULI

    @MODULI.setter
    def MODULI(self, value: str) -> None:
        self.__cardinfo.MODULI = value

    @property
    def MTIME(self) -> str:
        """
           Material temporal property. This field controls the interpretation of the input material property for viscoelasticity.
           INSTANT
           This material property is considered as the Instantaneous material input for viscoelasticity on the MATVE entry.
           LONG(Default)
           This material property is considered as the Long-term relaxed material input for viscoelasticity on the MATVE entry.
        """
        return self.__cardinfo.MTIME

    @MTIME.setter
    def MTIME(self, value: str) -> None:
        self.__cardinfo.MTIME = value


class MOMENTNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def SID(self) -> int:
        """
           Load set identification number. (Integer > 0)
        """
        return self.__cardinfo.SID

    @SID.setter
    def SID(self, value: int) -> None:  
        self.__cardinfo.SID = value
        self.last_status_message()
    
    @property
    def G(self) -> int:
        """
              Grid point identification number at which the moment is applied. (Integer > 0)
        """
        return self.__cardinfo.G
    
    @G.setter
    def G(self, value: int) -> None:
        self.__cardinfo.G = value
        self.last_status_message()

    @property
    def CID(self) -> int:
        """
        Coordinate system identification number. (Integer > 0 or blank)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value
        self.last_status_message()

    @property
    def M(self) -> float:
        """
           Scale factor. (Real)
        """
        return self.__cardinfo.M
    
    @M.setter
    def M(self, value: float) -> None:
        self.__cardinfo.M = value
        self.last_status_message()

    @property
    def N1(self) -> float:
        """
        X-component of a vector measured in coordinate system defined by CID. (Real; at least 
        one Ni ≠ 0.0. unless M is zero)
        """
        return self.__cardinfo.N1

    @N1.setter
    def N1(self, value: float) -> None:
        self.__cardinfo.N1 = value
        self.last_status_message()

    @property
    def N2(self) -> float:
        """
        Y-component of a vector measured in coordinate system defined by CID. (Real; at least 
        one Ni ≠ 0.0. unless M is zero)
        """
        return self.__cardinfo.N2

    @N2.setter
    def N2(self, value: float) -> None:
        self.__cardinfo.N2 = value
        self.last_status_message()

    @property
    def N3(self) -> float:
        """
        Z-component of a vector measured in coordinate system defined by CID. (Real; at least
        one Ni ≠ 0.0. unless M is zero)
        """
        return self.__cardinfo.N3

    @N3.setter
    def N3(self, value: float) -> None:
        self.__cardinfo.N3 = value
        self.last_status_message()

    

    

    
class MPC(N2PCard):
    """Nastran/Optistruct Multi Point Constriction Card"""

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def SID(self) -> int:
        """Set identification number. (Integer > 0)"""
        return self.__cardinfo.SID

    @SID.setter
    def SID(self, value: int) -> None:
        self.__cardinfo.SID = value
        self.last_status_message()

    def get_all_grid_points(self) -> list[int]:
        """Returns a list of all grid points in the MPC definition."""
        return self.__cardinfo.GetAllGridPoints()
    
    def set_grid_point(self, index: int, value: int) -> None:
        """Sets the grid point at the specified index (1-based)."""
        self.__cardinfo.SetConstraintGridPoint(index, value)
        self.last_status_message()

    def get_all_components(self) -> list[int]:
        """Returns a list of all components in the MPC definition."""
        return self.__cardinfo.GetAllComponents()
    
    def set_component(self, index: int, value: int) -> None:
        """Sets the component at the specified index (1-based)."""
        self.__cardinfo.SetConstraintComponent(index, value)
        self.last_status_message()

    def get_all_coefficients(self) -> list[float]:
        """Returns a list of all coefficients in the MPC definition."""
        return self.__cardinfo.GetAllCoefficients()
    
    def set_coefficient(self, index: int, value: float) -> None:
        """Sets the coefficient at the specified index (1-based)."""
        self.__cardinfo.SetConstraintCoefficient(index, value)
        self.last_status_message()

class MPCADD(N2PCard):
    """Nastran/Optistruct Multi Point Constriction Card"""

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def SID(self) -> int:
        """Set identification number. (Integer > 0)"""
        return self.__cardinfo.SID

    @SID.setter
    def SID(self, value: int) -> None:
        self.__cardinfo.SID = value
        self.last_status_message()
    
    def get_all_components_set_ids(self) -> list[int]:
        """Returns a list of all component set IDs in the MPCADD definition."""
        return self.__cardinfo.GetAllComponentSetIDs()
    
    def set_component_set_id(self, index: int, componentSetID: int) -> None:
        """Sets the component set ID at the specified index (1-based)."""
        self.__cardinfo.SetComponentSetIDAt(index, componentSetID)
        self.last_status_message()

class PBAR(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def MID(self) -> int:
        """
           Identification number of a MATHP entry. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value
        self.last_status_message()

    @property
    def A(self) -> float:
        """
           Area of bar cross section. (Real; Default = 0.0)
        """
        return self.__cardinfo.A

    @A.setter
    def A(self, value: float) -> None:
        self.__cardinfo.A = value
        self.last_status_message()

    @property
    def I1(self) -> float:
        """
           I1, I2:
           Area moments of inertia.See Figure 8-177. (Real; I1 > 0.0, I2 > 0.0, I1* I2 > ; Default = 0.0)
        """
        return self.__cardinfo.I1

    @I1.setter
    def I1(self, value: float) -> None:
        self.__cardinfo.I1 = value
        self.last_status_message()

    @property
    def I2(self) -> float:
        """
           I2
        """
        return self.__cardinfo.I2

    @I2.setter
    def I2(self, value: float) -> None:
        self.__cardinfo.I2 = value
        self.last_status_message()

    @property
    def I12(self) -> float:
        """
           I12
        """
        return self.__cardinfo.I12

    @I12.setter
    def I12(self, value: float) -> None:
        self.__cardinfo.I12 = value
        self.last_status_message()

    @property
    def J(self) -> float:
        """
           Torsional constant. See Figure 8-177. (Real; Default = for SOL 600 and 0.0 for all other solution sequences)
        """
        return self.__cardinfo.J

    @J.setter
    def J(self, value: float) -> None:
        self.__cardinfo.J = value
        self.last_status_message()

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit length. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value
        self.last_status_message()

    @property
    def C1(self) -> float:
        """
           C1, C2, D1, D2, E1, E2, F1, F2:
           Stress recovery coefficients. (Real; Default = 0.0)
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: float) -> None:
        self.__cardinfo.C1 = value
        self.last_status_message()

    @property
    def C2(self) -> float:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: float) -> None:
        self.__cardinfo.C2 = value
        self.last_status_message()

    @property
    def D1(self) -> float:
        """
           D1
        """
        return self.__cardinfo.D1

    @D1.setter
    def D1(self, value: float) -> None:
        self.__cardinfo.D1 = value
        self.last_status_message()

    @property
    def D2(self) -> float:
        """
           D2
        """
        return self.__cardinfo.D2

    @D2.setter
    def D2(self, value: float) -> None:
        self.__cardinfo.D2 = value
        self.last_status_message()

    @property
    def E1(self) -> float:
        """
           E1
        """
        return self.__cardinfo.E1

    @E1.setter
    def E1(self, value: float) -> None:
        self.__cardinfo.E1 = value
        self.last_status_message()

    @property
    def E2(self) -> float:
        """
           E2
        """
        return self.__cardinfo.E2

    @E2.setter
    def E2(self, value: float) -> None:
        self.__cardinfo.E2 = value
        self.last_status_message()

    @property
    def F1(self) -> float:
        """
           F1
        """
        return self.__cardinfo.F1

    @F1.setter
    def F1(self, value: float) -> None:
        self.__cardinfo.F1 = value
        self.last_status_message()

    @property
    def F2(self) -> float:
        """
           F2
        """
        return self.__cardinfo.F2

    @F2.setter
    def F2(self, value: float) -> None:
        self.__cardinfo.F2 = value
        self.last_status_message()

    @property
    def K1(self) -> float:
        """
           Area factor for shear. See Remark 5. (Real or blank)
        """
        return self.__cardinfo.K1

    @K1.setter
    def K1(self, value: float) -> None:
        self.__cardinfo.K1 = value
        self.last_status_message()

    @property
    def K2(self) -> float:
        """
           K2
        """
        return self.__cardinfo.K2

    @K2.setter
    def K2(self, value: float) -> None:
        self.__cardinfo.K2 = value
        self.last_status_message()


class PBARL(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PMASS)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Material identification number (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def GROUP(self) -> str:
        """
           Cross-section group.See Remarks 6. and 8. (Character;
           Default = “MSCBML0")
        """
        return self.__cardinfo.GROUP

    @GROUP.setter
    def GROUP(self, value: str) -> None:
        self.__cardinfo.GROUP = value

    @property
    def TYPE(self) -> str:
        """
           Cross-section type.See Remarks 6. and 8. and Figure 8-112. (Character:
           “ROD”, “TUBE”, “I”, “CHAN”, “T”, “BOX”, “BAR”, “CROSS”, “H”,
           “T1", “I1", “CHAN1", “Z”, “CHAN2", “T2", “BOX1", “HEXA”, “HAT”,
           “HAT1”, “DBOX” for GROUP=“MSCBML0")
        """
        return self.__cardinfo.TYPE

    @TYPE.setter
    def TYPE(self, value: str) -> None:
        self.__cardinfo.TYPE = value

    @property
    def DIM(self) -> list[float]:
        """
           DIM
           PBARL	PID		MID		GROUP	TYPE
           DIM1	DIM2    DIM3	DIM4    DIM5	DIM6    DIM7	DIM8
           DIM9	-etc.	NSM
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.DIM), self.__cardinfo.DIM)

    @DIM.setter
    def DIM(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.DIM[i] = val

    @property
    def NSM(self) -> float:
        """
           NSM
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value


class PBEAMNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0 or string)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value
        self.last_status_message()

    @property
    def A(self) -> list[float]:
        """
           Area of the beam cross section at end A. (Real > 0.0)
           Fixed-size array: [0..10] representing A values at up to 11 stations.
        """
        return self.__cardinfo._A

    @A.setter
    def A(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def I1(self) -> list[float]:
        """
           Area moment of inertia at end A for bending in plane 1 about the neutral axis.See Remark 10. (Real > 0.0)
           Fixed-size array: [0..10] representing I1 values at up to 11 stations.
        """
        return self.__cardinfo._I1

    @I1.setter
    def I1(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def I2(self) -> list[float]:
        """
           Area moment of inertia at end A for bending in plane 2 about the neutral axis.See Remark 10. (Real > 0.0)
           Fixed-size array: [0..10] representing I2 values at up to 11 stations.
        """
        return self.__cardinfo._I2

    @I2.setter
    def I2(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def I12(self) -> list[float]:
        """
           Area product of inertia at end A. See Remark 10. (Real, but I1*I2 - I12^2 > 0.00)
           Fixed-size array: [0..10] representing I12 values at up to 11 stations.
        """
        return self.__cardinfo._I12

    @I12.setter
    def I12(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def J(self) -> list[float]:
        """
           Torsional stiffness parameter at end A. See Remark 10. (Real >= 0.0 but > 0.0 if warping is present)
           Fixed-size array: [0..10] representing J values at up to 11 stations.
        """
        return self.__cardinfo._J

    @J.setter
    def J(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def NSM(self) -> list[float]:
        """
              Nonstructural mass per unit length (Real)
              Fixed-size array: [0..10] representing NSM values at up to 11 stations.
        """
        return self.__cardinfo._NSM

    @NSM.setter
    def NSM(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def C1(self) -> list[float]:
        """
           Y-coordinate of stress recovery point C at each station.
           Fixed-size array: [0..10] representing C1 (y_C) values at up to 11 stations.
        """
        return self.__cardinfo._C1

    @C1.setter
    def C1(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def C2(self) -> list[float]:
        """
           Z-coordinate of stress recovery point C at each station.
           Follows identical rules to C1 but for z-direction.
           Fixed-size array: [0..10] representing C2 (z_C) values at up to 11 stations.
        """
        return self.__cardinfo._C2

    @C2.setter
    def C2(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def D1(self) -> list[float]:
        """
           Y-coordinate of stress recovery point D at each station.
           Follows identical rules to C1.
           Fixed-size array: [0..10] representing D1 (y_D) values at up to 11 stations.
        """
        return self.__cardinfo._D1

    @D1.setter
    def D1(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def D2(self) -> list[float]:
        """
           Z-coordinate of stress recovery point D at each station.
           Follows identical rules to C1 but for z-direction.
           Fixed-size array: [0..10] representing D2 (z_D) values at up to 11 stations.
        """
        return self.__cardinfo._D2

    @D2.setter
    def D2(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def E1(self) -> list[float]:
        """
           Y-coordinate of stress recovery point E at each station.
           Follows identical rules to C1.
           Fixed-size array: [0..10] representing E1 (y_E) values at up to 11 stations.
        """
        return self.__cardinfo._E1

    @E1.setter
    def E1(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def E2(self) -> list[float]:
        """
           Z-coordinate of stress recovery point E at each station.
           Follows identical rules to C1.
           Fixed-size array: [0..10] representing E2 (z_E) values at up to 11 stations.
        """
        return self.__cardinfo._E2

    @E2.setter
    def E2(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def F1(self) -> list[float]:
        """
           Y-coordinate of stress recovery point F at each station.
           Follows identical rules to C1.
           Fixed-size array: [0..10] representing F1 (y_F) values at up to 11 stations.
        """
        return self.__cardinfo._F1

    @F1.setter
    def F1(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def F2(self) -> list[float]:
        """
           Z-coordinate of stress recovery point F at each station.
           Follows identical rules to C1 but for z-direction.
           Fixed-size array: [0..10] representing F2 (z_F) values at up to 11 stations.
        """
        return self.__cardinfo._F2

    @F2.setter
    def F2(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def SO(self) -> list[int]:
        """
           Stress output request option.
           (Character)
           Required*
           “YES” Stresses recovered at points Ci, Di, Ei, and
           Fi on the next continuation.
           “YESA” Stresses recovered at points with the same
           y and z location as end A.
           “NO” No stresses or forces are recovered.

           The parser converts the string value from the file to an enum:
           • "YES" in file → StressOutputOption.YES = 0
           • "YESA" in file → StressOutputOption.YESA = 1
           • "NO" in file → StressOutputOption.NO = 2

           Fixed-size array: [0..10] representing values at up to 11 stations. 
        """
        return self.__cardinfo._SO

    @SO.setter
    def SO(self, value: list[int]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def X_XB(self) -> list[float]:
        """
           Distance from end A in the element coordinate
           system divided by the length of the element. (Real, 0.0 < x/xb ≤ 1.0)
        """
        return self.__cardinfo._xXB

    @X_XB.setter
    def X_XB(self, value: list[float]) -> None:
        print("At the moment, this PBEAM setter cannot be used.")

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit length at each station.
           Fixed-size array: [0..10] representing NSM values at up to 11 stations.
        """
        return self.__cardinfo._NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo._NSM = value
        self.last_status_message()

    @property
    def K1(self) -> float:
        """
           Shear stiffness factor K in K* A*G for plane 1. (Real)
        """
        return self.__cardinfo.K1

    @K1.setter
    def K1(self, value: float) -> None:
        self.__cardinfo.K1 = value
        self.last_status_message()

    @property
    def K2(self) -> float:
        """
           Shear stiffness factor K in K* A*G for plane 2. (Real)
        """
        return self.__cardinfo.K2

    @K2.setter
    def K2(self, value: float) -> None:
        self.__cardinfo.K2 = value
        self.last_status_message()

    @property
    def S1(self) -> float:
        """
           Shear relief coefficient due to taper for plane 1.Ignored for beam p-elements. (Real)
        """
        return self.__cardinfo.S1

    @S1.setter
    def S1(self, value: float) -> None:
        self.__cardinfo.S1 = value
        self.last_status_message()

    @property
    def S2(self) -> float:
        """
           Shear relief coefficient due to taper for plane 2.Ignored for beam p-elements. (Real)
        """
        return self.__cardinfo.S2

    @S2.setter
    def S2(self, value: float) -> None:
        self.__cardinfo.S2 = value
        self.last_status_message()

    @property
    def NSI_A(self) -> float:
        """
           Nonstructural mass moment of inertia per unit length about nonstructural mass center of gravity at end A. (Real)
        """
        return self.__cardinfo.NSI_A

    @NSI_A.setter
    def NSI_A(self, value: float) -> None:
        self.__cardinfo.NSI_A = value
        self.last_status_message()

    @property
    def NSI_B(self) -> float:
        """
           Nonstructural mass moment of inertia per unit length about nonstructural mass center of gravity at end B. (Real)
        """
        return self.__cardinfo.NSI_B

    @NSI_B.setter
    def NSI_B(self, value: float) -> None:
        self.__cardinfo.NSI_B = value
        self.last_status_message()

    @property
    def CW_A(self) -> float:
        """
           Warping coefficient for end A. (Real)
        """
        return self.__cardinfo.CW_A

    @CW_A.setter
    def CW_A(self, value: float) -> None:
        self.__cardinfo.CW_A = value
        self.last_status_message()

    @property
    def CW_B(self) -> float:
        """
           Warping coefficient for end A
        """
        return self.__cardinfo.CW_B

    @CW_B.setter
    def CW_B(self, value: float) -> None:
        self.__cardinfo.CW_B = value
        self.last_status_message()

    @property
    def M1_A(self) -> float:
        """
           Y coordinate of center of gravity of nonstructural mass for end A. (Real)
        """
        return self.__cardinfo.M1_A

    @M1_A.setter
    def M1_A(self, value: float) -> None:
        self.__cardinfo.M1_A = value
        self.last_status_message()

    @property
    def M2_A(self) -> float:
        """
           Z coordinate of center of gravity of nonstructural mass for end A. (Real)
        """
        return self.__cardinfo.M2_A

    @M2_A.setter
    def M2_A(self, value: float) -> None:
        self.__cardinfo.M2_A = value
        self.last_status_message()

    @property
    def M1_B(self) -> float:
        """
           Y coordinate of center of gravity of nonstructural mass for end B. (Real)
        """
        return self.__cardinfo.M1_B

    @M1_B.setter
    def M1_B(self, value: float) -> None:
        self.__cardinfo.M1_B = value
        self.last_status_message()

    @property
    def M2_B(self) -> float:
        """
           Z coordinate of center of gravity of nonstructural mass for end B. (Real)
        """
        return self.__cardinfo.M2_B

    @M2_B.setter
    def M2_B(self, value: float) -> None:
        self.__cardinfo.M2_B = value
        self.last_status_message()

    @property
    def N1_A(self) -> float:
        """
           Y coordinate of neutral axis for end A. (Real)
        """
        return self.__cardinfo.N1_A

    @N1_A.setter
    def N1_A(self, value: float) -> None:
        self.__cardinfo.N1_A = value
        self.last_status_message()

    @property
    def N2_A(self) -> float:
        """
           Z coordinate of neutral axis for end A. (Real)
        """
        return self.__cardinfo.N2_A

    @N2_A.setter
    def N2_A(self, value: float) -> None:
        self.__cardinfo.N2_A = value
        self.last_status_message()

    @property
    def N1_B(self) -> float:
        """
           Y coordinate of neutral axis for end B. (Real)
        """
        return self.__cardinfo.N1_B

    @N1_B.setter
    def N1_B(self, value: float) -> None:
        self.__cardinfo.N1_B = value
        self.last_status_message()

    @property
    def N2_B(self) -> float:
        """
           Z coordinate of neutral axis for end B. (Real)
        """
        return self.__cardinfo.N2_B

    @N2_B.setter
    def N2_B(self, value: float) -> None:
        self.__cardinfo.N2_B = value
        self.last_status_message()


class PBEAML(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PMASS)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Material identification number (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def GROUP(self) -> str:
        """
           Cross-section group. (Character; Default = “MSCBML0")
        """
        return self.__cardinfo.GROUP

    @GROUP.setter
    def GROUP(self, value: str) -> None:
        self.__cardinfo.GROUP = value

    @property
    def TYPE(self) -> str:
        """
           Cross-section shape.See Remark 4. (Character: “ROD”, “TUBE”, “L”,
           “I”, “CHAN”, “T”, “BOX”, “BAR”, “CROSS”, “H”, “T1", “I1",
           “CHAN1", “Z”, “CHAN2", “T2", “BOX1", “HEXA”, “HAT”, “HAT1”,
           “DBOX” for GROUP = “MSCBML0")
        """
        return self.__cardinfo.TYPE

    @TYPE.setter
    def TYPE(self, value: str) -> None:
        self.__cardinfo.TYPE = value

    @property
    def DIM_A(self) -> list[float]:
        """
           Cross-section dimensions at end A
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.DIM_A), self.__cardinfo.DIM_A)

    @DIM_A.setter
    def DIM_A(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.DIM_A[i] = val

    @property
    def DIM_B(self) -> list[float]:
        """
           Cross-section dimensions at end B
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.DIM_B), self.__cardinfo.DIM_B)

    @DIM_B.setter
    def DIM_B(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.DIM_B[i] = val

    @property
    def DIM(self) -> float:
        """
           <para>
           Cross-section dimensions at intermediate stations. (Real > 0.0 for GROUP = “MSCBML0")
           </para>
           <para>
           1-N sections, NOT including <see cref="DIM_A"/> nor <see cref="DIM_B"/>
           </para>
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.DIM), self.__cardinfo.DIM)

    @DIM.setter
    def DIM(self, value: float) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.DIM[i] = val

    @property
    def NSM(self) -> list[float]:
        """
           <para>
           Nonstructural mass per unit length. (Default = 0.0)
           </para>
           <para>
           1-N sections, NOT including <see cref="NSM_A"/> nor <see cref="NSM_B"/>
           </para>
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.NSM), self.__cardinfo.NSM)

    @NSM.setter
    def NSM(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.NSM[i] = val

    @property
    def NSM_A(self) -> float:
        """
           Nonstructural mass per unit length in section A. (Default = 0.0)
        """
        return self.__cardinfo.NSM_A

    @NSM_A.setter
    def NSM_A(self, value: float) -> None:
        self.__cardinfo.NSM_A = value

    @property
    def NSM_B(self) -> float:
        """
           Nonstructural mass per unit length in section B. (Default = 0.0)
        """
        return self.__cardinfo.NSM_B

    @NSM_B.setter
    def NSM_B(self, value: float) -> None:
        self.__cardinfo.NSM_B = value

    @property
    def SO(self) -> list[str]:
        """
           <para>
           Stress output request option for intermediate station j. (Character; Default = “YES”)
           </para>
           <para>
           YES: Stresses recovered at all points on next continuation and
           shown in Figure 8-116 as C, D, E, and F.
           </para>
           <para>
           NO: No stresses or forces are recovered.
           </para>
           <para>
           Section B NOT included, see <see cref="SO_B"/>
           </para>
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.SO), self.__cardinfo.SO)

    @SO.setter
    def SO(self, value: list[str]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.SO[i] = val

    @property
    def SO_B(self) -> str:
        """
           <para>
           Stress output request option for section B. (Character; Default = “YES”)
           </para>
           <para>
           YES: Stresses recovered at all points on next continuation and
           shown in Figure 8-116 as C, D, E, and F.
           </para>
           <para>
           NO: No stresses or forces are recovered.
           </para>
        """
        return self.__cardinfo.SO_B

    @SO_B.setter
    def SO_B(self, value: str) -> None:
        self.__cardinfo.SO_B = value

    @property
    def X_XB(self) -> list[float]:
        """
           Distance from end A to intermediate station j in the element
           coordinate system divided by the length of the element. (Real>0.0;
           Default = 1.0)
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.X_XB), self.__cardinfo.X_XB)

    @X_XB.setter
    def X_XB(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.X_XB[i] = val


class PBUSHNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def K1(self) -> float:
        """
           Ki: Nominal stiffness values in directions 1 through 6. See Remarks 2. and 3.
           (Real; Default = 0.0)
        """
        return self.__cardinfo.K1

    @K1.setter
    def K1(self, value: float) -> None:
        self.__cardinfo.K1 = value
        self.last_status_message()

    @property
    def K2(self) -> float:
        """
           K2
        """
        return self.__cardinfo.K2

    @K2.setter
    def K2(self, value: float) -> None:
        self.__cardinfo.K2 = value
        self.last_status_message()

    @property
    def K3(self) -> float:
        """
           K3
        """
        return self.__cardinfo.K3

    @K3.setter
    def K3(self, value: float) -> None:
        self.__cardinfo.K3 = value
        self.last_status_message()

    @property
    def K4(self) -> float:
        """
           K4
        """
        return self.__cardinfo.K4

    @K4.setter
    def K4(self, value: float) -> None:
        self.__cardinfo.K4 = value
        self.last_status_message()

    @property
    def K5(self) -> float:
        """
           K5
        """
        return self.__cardinfo.K5

    @K5.setter
    def K5(self, value: float) -> None:
        self.__cardinfo.K5 = value
        self.last_status_message()

    @property
    def K6(self) -> float:
        """
           K6
        """
        return self.__cardinfo.K6

    @K6.setter
    def K6(self, value: float) -> None:
        self.__cardinfo.K6 = value
        self.last_status_message()

    @property
    def B1(self) -> float:
        """
           Bi: Nominal damping coefficients in direction 1 through 6 in units of force per unit velocity.See Remarks 2., 3., and 9. (Real; Default = 0.0)
        """
        return self.__cardinfo.B1

    @B1.setter
    def B1(self, value: float) -> None:
        self.__cardinfo.B1 = value
        self.last_status_message()

    @property
    def B2(self) -> float:
        """
           B2
        """
        return self.__cardinfo.B2

    @B2.setter
    def B2(self, value: float) -> None:
        self.__cardinfo.B2 = value
        self.last_status_message()

    @property
    def B3(self) -> float:
        """
           B3
        """
        return self.__cardinfo.B3

    @B3.setter
    def B3(self, value: float) -> None:
        self.__cardinfo.B3 = value
        self.last_status_message()

    @property
    def B4(self) -> float:
        """
           B4
        """
        return self.__cardinfo.B4

    @B4.setter
    def B4(self, value: float) -> None:
        self.__cardinfo.B4 = value
        self.last_status_message()

    @property
    def B5(self) -> float:
        """
           B5
        """
        return self.__cardinfo.B5

    @B5.setter
    def B5(self, value: float) -> None:
        self.__cardinfo.B5 = value
        self.last_status_message()

    @property
    def B6(self) -> float:
        """
           B6
        """
        return self.__cardinfo.B6

    @B6.setter
    def B6(self, value: float) -> None:
        self.__cardinfo.B6 = value
        self.last_status_message()

    @property
    def GE1(self) -> float:
        """
           Nominal stiffness values in directions 1 through 6. See Remarks 2. and 3.
           (Real; Default = 0.0)
        """
        return self.__cardinfo.GE1

    @GE1.setter
    def GE1(self, value: float) -> None:
        self.__cardinfo.GE1 = value
        self.last_status_message()

    @property
    def GE2(self) -> float:
        """
           GE2
        """
        return self.__cardinfo.GE2

    @GE2.setter
    def GE2(self, value: float) -> None:
        self.__cardinfo.GE2 = value
        self.last_status_message()

    @property
    def GE3(self) -> float:
        """
           GE3
        """
        return self.__cardinfo.GE3

    @GE3.setter
    def GE3(self, value: float) -> None:
        self.__cardinfo.GE3 = value
        self.last_status_message()

    @property
    def GE4(self) -> float:
        """
           GE4
        """
        return self.__cardinfo.GE4

    @GE4.setter
    def GE4(self, value: float) -> None:
        self.__cardinfo.GE4 = value
        self.last_status_message()

    @property
    def GE5(self) -> float:
        """
           GE5
        """
        return self.__cardinfo.GE5

    @GE5.setter
    def GE5(self, value: float) -> None:
        self.__cardinfo.GE5 = value
        self.last_status_message()

    @property
    def GE6(self) -> float:
        """
           GE6
        """
        return self.__cardinfo.GE6

    @GE6.setter
    def GE6(self, value: float) -> None:
        self.__cardinfo.GE6 = value
        self.last_status_message()

    @property
    def SA(self) -> float:
        """
           Nominal stiffness values in directions 1 through 6. See Remarks 2. and 3.
           (Real; Default = 0.0)
        """
        return self.__cardinfo.SA

    @SA.setter
    def SA(self, value: float) -> None:
        self.__cardinfo.SA = value
        self.last_status_message()

    @property
    def ST(self) -> float:
        """
           ST
        """
        return self.__cardinfo.ST

    @ST.setter
    def ST(self, value: float) -> None:
        self.__cardinfo.ST = value
        self.last_status_message()

    @property
    def EA(self) -> float:
        """
           EA
        """
        return self.__cardinfo.EA

    @EA.setter
    def EA(self, value: float) -> None:
        self.__cardinfo.EA = value
        self.last_status_message()

    @property
    def ET(self) -> float:
        """
           ET
        """
        return self.__cardinfo.ET

    @ET.setter
    def ET(self, value: float) -> None:
        self.__cardinfo.ET = value
        self.last_status_message()

    @property
    def M(self) -> float:
        """
           Lumped mass of the CBUSH. (Real≥0.0; Default=0.0)
        """
        return self.__cardinfo.M

    @M.setter
    def M(self, value: float) -> None:
        self.__cardinfo.M = value
        self.last_status_message()

    @property
    def ALPHA(self) -> float:
        """
           Thermal expansion coefficient for the CBUSH.(Real; Default=0.0)
        """
        return self.__cardinfo.ALPHA

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA = value
        self.last_status_message()

    @property
    def TREF(self) -> float:
        """
        Reference temperature for the calculation of thermal loads. (Real; Default=0.0)
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value
        self.last_status_message()

    @property
    def COINL(self) -> float:
        """
            Length of a CBUSH with coincident grids. (Real; Default=0.0, COINL ≥ 0.0)
        """
        return self.__cardinfo.COINL
    
    @COINL.setter
    def COINL(self, value: float) -> None:
        self.__cardinfo.COINL = value
        self.last_status_message()
    



class PBUSHOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PLPLANE)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           <para>PID: <see cref="CardPbushNas"/> does not have an associate property. Returns <see cref="uint.MaxValue"/></para>
           <para>Implemented to use the interface <see cref="ICardProperty"/></para>
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def K(self) -> str:
        """
           Flag indicating that the next 1 to 6 fields are stiffness values in the element
           coordinate system. (Character)
        """
        return self.__cardinfo.K

    @K.setter
    def K(self, value: str) -> None:
        self.__cardinfo.K = value

    @property
    def K1(self) -> float:
        """
           Ki: Nominal stiffness values in directions 1 through 6. See Remarks 2. and 3.
           (Real; Default = 0.0)
        """
        return self.__cardinfo.K1

    @K1.setter
    def K1(self, value: float) -> None:
        self.__cardinfo.K1 = value

    @property
    def K2(self) -> float:
        """
           K2
        """
        return self.__cardinfo.K2

    @K2.setter
    def K2(self, value: float) -> None:
        self.__cardinfo.K2 = value

    @property
    def K3(self) -> float:
        """
           K3
        """
        return self.__cardinfo.K3

    @K3.setter
    def K3(self, value: float) -> None:
        self.__cardinfo.K3 = value

    @property
    def K4(self) -> float:
        """
           K4
        """
        return self.__cardinfo.K4

    @K4.setter
    def K4(self, value: float) -> None:
        self.__cardinfo.K4 = value

    @property
    def K5(self) -> float:
        """
           K5
        """
        return self.__cardinfo.K5

    @K5.setter
    def K5(self, value: float) -> None:
        self.__cardinfo.K5 = value

    @property
    def K6(self) -> float:
        """
           K6
        """
        return self.__cardinfo.K6

    @K6.setter
    def K6(self, value: float) -> None:
        self.__cardinfo.K6 = value

    @property
    def KMAG(self) -> str:
        """
           Flag indicating that the next 1 to 6 fields are stiffness magnitude(K*) values. 4
           No default (Character)
        """
        return self.__cardinfo.KMAG

    @KMAG.setter
    def KMAG(self, value: str) -> None:
        self.__cardinfo.KMAG = value

    @property
    def KMAG1(self) -> float:
        """
           Nominal stiffness magnitude(K*) values in directions 1 through 6. 4 6 8 9
           Default = 0.0 (Real)
        """
        return self.__cardinfo.KMAG1

    @KMAG1.setter
    def KMAG1(self, value: float) -> None:
        self.__cardinfo.KMAG1 = value

    @property
    def KMAG3(self) -> float:
        """
           KMAG3
        """
        return self.__cardinfo.KMAG3

    @KMAG3.setter
    def KMAG3(self, value: float) -> None:
        self.__cardinfo.KMAG3 = value

    @property
    def KMAG4(self) -> float:
        """
           KMAG4
        """
        return self.__cardinfo.KMAG4

    @KMAG4.setter
    def KMAG4(self, value: float) -> None:
        self.__cardinfo.KMAG4 = value

    @property
    def KMAG5(self) -> float:
        """
           KMAG5
        """
        return self.__cardinfo.KMAG5

    @KMAG5.setter
    def KMAG5(self, value: float) -> None:
        self.__cardinfo.KMAG5 = value

    @property
    def KMAG6(self) -> float:
        """
           KMAG6
        """
        return self.__cardinfo.KMAG6

    @KMAG6.setter
    def KMAG6(self, value: float) -> None:
        self.__cardinfo.KMAG6 = value

    @property
    def B(self) -> str:
        """
           Flag indicating that the next 1 to 6 fields are force-per-velocity damping.
           (Character)
        """
        return self.__cardinfo.B

    @B.setter
    def B(self, value: str) -> None:
        self.__cardinfo.B = value

    @property
    def B1(self) -> float:
        """
           Bi: Nominal damping coefficients in direction 1 through 6 in units of force per unit velocity.See Remarks 2., 3., and 9. (Real; Default = 0.0)
        """
        return self.__cardinfo.B1

    @B1.setter
    def B1(self, value: float) -> None:
        self.__cardinfo.B1 = value

    @property
    def B2(self) -> float:
        """
           B2
        """
        return self.__cardinfo.B2

    @B2.setter
    def B2(self, value: float) -> None:
        self.__cardinfo.B2 = value

    @property
    def B3(self) -> float:
        """
           B3
        """
        return self.__cardinfo.B3

    @B3.setter
    def B3(self, value: float) -> None:
        self.__cardinfo.B3 = value

    @property
    def B4(self) -> float:
        """
           B4
        """
        return self.__cardinfo.B4

    @B4.setter
    def B4(self, value: float) -> None:
        self.__cardinfo.B4 = value

    @property
    def B5(self) -> float:
        """
           B5
        """
        return self.__cardinfo.B5

    @B5.setter
    def B5(self, value: float) -> None:
        self.__cardinfo.B5 = value

    @property
    def B6(self) -> float:
        """
           B6
        """
        return self.__cardinfo.B6

    @B6.setter
    def B6(self, value: float) -> None:
        self.__cardinfo.B6 = value

    @property
    def GE(self) -> str:
        """
           Flag indicating that the next fields, 1 through 6 are structural damping
           constants.See Remark 7. (Character)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: str) -> None:
        self.__cardinfo.GE = value

    @property
    def GE1(self) -> float:
        """
           Nominal stiffness values in directions 1 through 6. See Remarks 2. and 3.
           (Real; Default = 0.0)
        """
        return self.__cardinfo.GE1

    @GE1.setter
    def GE1(self, value: float) -> None:
        self.__cardinfo.GE1 = value

    @property
    def GE2(self) -> float:
        """
           GE2
        """
        return self.__cardinfo.GE2

    @GE2.setter
    def GE2(self, value: float) -> None:
        self.__cardinfo.GE2 = value

    @property
    def GE3(self) -> float:
        """
           GE3
        """
        return self.__cardinfo.GE3

    @GE3.setter
    def GE3(self, value: float) -> None:
        self.__cardinfo.GE3 = value

    @property
    def GE4(self) -> float:
        """
           GE4
        """
        return self.__cardinfo.GE4

    @GE4.setter
    def GE4(self, value: float) -> None:
        self.__cardinfo.GE4 = value

    @property
    def GE5(self) -> float:
        """
           GE5
        """
        return self.__cardinfo.GE5

    @GE5.setter
    def GE5(self, value: float) -> None:
        self.__cardinfo.GE5 = value

    @property
    def GE6(self) -> float:
        """
           GE6
        """
        return self.__cardinfo.GE6

    @GE6.setter
    def GE6(self, value: float) -> None:
        self.__cardinfo.GE6 = value

    @property
    def ANGLE(self) -> str:
        """
           Flag indicating that the next 1 to 6 fields are Loss angles defined in degrees. 9
        """
        return self.__cardinfo.ANGLE

    @ANGLE.setter
    def ANGLE(self, value: str) -> None:
        self.__cardinfo.ANGLE = value

    @property
    def ANGLE1(self) -> float:
        """
           Nominal angle values in directions 1 through 6 in degrees.
        """
        return self.__cardinfo.ANGLE1

    @ANGLE1.setter
    def ANGLE1(self, value: float) -> None:
        self.__cardinfo.ANGLE1 = value

    @property
    def ANGLE2(self) -> float:
        """
           ANGLE2
        """
        return self.__cardinfo.ANGLE2

    @ANGLE2.setter
    def ANGLE2(self, value: float) -> None:
        self.__cardinfo.ANGLE2 = value

    @property
    def ANGLE3(self) -> float:
        """
           ANGLE3
        """
        return self.__cardinfo.ANGLE3

    @ANGLE3.setter
    def ANGLE3(self, value: float) -> None:
        self.__cardinfo.ANGLE3 = value

    @property
    def ANGLE4(self) -> float:
        """
           ANGLE4
        """
        return self.__cardinfo.ANGLE4

    @ANGLE4.setter
    def ANGLE4(self, value: float) -> None:
        self.__cardinfo.ANGLE4 = value

    @property
    def ANGLE5(self) -> float:
        """
           ANGLE5
        """
        return self.__cardinfo.ANGLE5

    @ANGLE5.setter
    def ANGLE5(self, value: float) -> None:
        self.__cardinfo.ANGLE5 = value

    @property
    def ANGLE6(self) -> float:
        """
           ANGLE6
        """
        return self.__cardinfo.ANGLE6

    @ANGLE6.setter
    def ANGLE6(self, value: float) -> None:
        self.__cardinfo.ANGLE6 = value

    @property
    def M(self) -> str:
        """
           Flag indicating that the next 1 to 6 fields are directional masses.
        """
        return self.__cardinfo.M

    @M.setter
    def M(self, value: str) -> None:
        self.__cardinfo.M = value

    @property
    def M1(self) -> float:
        """
           Mi: Nominal mass values in directions 1 through 6.
           In case of implicit analysis: 10
           M1
           For translational mass calculation.
           Default = 0.0(Real)
           M2, M3
           If defined, they must be same as M1.
           Default = blank(Real)
           M4, M5, M6
           For inertia calculation.
           In this case, Inertia = max. (M4, M5, M6).
           Default = blank(Real)
           In case of explicit analysis:
           M1
           Required for translational mass calculation.
           No default (Real)
           M2, M3
           If defined, they must be same as M1.
           Default = blank(Real)
           M4
           For inertia calculation.
           For zero length CBUSH elements:
           M4
           Required. No default (Real)
           For non-zero length CBUSH elements:
           M4
           Optional. Default = blank(Real)
           M5, M6
           These are currently ignored.
           Default = blank(Real)
        """
        return self.__cardinfo.M1

    @M1.setter
    def M1(self, value: float) -> None:
        self.__cardinfo.M1 = value

    @property
    def M2(self) -> float:
        """
           M2
        """
        return self.__cardinfo.M2

    @M2.setter
    def M2(self, value: float) -> None:
        self.__cardinfo.M2 = value

    @property
    def M3(self) -> float:
        """
           M3
        """
        return self.__cardinfo.M3

    @M3.setter
    def M3(self, value: float) -> None:
        self.__cardinfo.M3 = value

    @property
    def M4(self) -> float:
        """
           M4
        """
        return self.__cardinfo.M4

    @M4.setter
    def M4(self, value: float) -> None:
        self.__cardinfo.M4 = value

    @property
    def M5(self) -> float:
        """
           M5
        """
        return self.__cardinfo.M5

    @M5.setter
    def M5(self, value: float) -> None:
        self.__cardinfo.M5 = value

    @property
    def M6(self) -> float:
        """
           M6
        """
        return self.__cardinfo.M6

    @M6.setter
    def M6(self, value: float) -> None:
        self.__cardinfo.M6 = value


class PCOMPNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def PID(self) -> int:
        """
           Property identification number. (0 < Integer < 10000000)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def Z0(self) -> float:
        """
           Distance from the reference plane to the bottom surface. See Remark 10. (Real; Default = -0.5 times the element thickness.)
           * Remark 10:
           If the value specified for Z0 is not equal to -0.5 times the thickness of the element and PARAM,NOCOMPS,-1 is specified, then the homogeneous
           element stresses are incorrect, while element forces and strains are correct. For correct homogeneous stresses, use ZOFFS on the corresponding
           connection entry.
        """
        return self.__cardinfo.Z0

    @Z0.setter
    def Z0(self, value: float) -> None:
        self.__cardinfo.Z0 = value
        self.last_status_message()

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit area. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value
        self.last_status_message()

    @property
    def SB(self) -> float:
        """
           Allowable shear stress of the bonding material (allowable interlaminar shear stress). Required if FT is also specified. (Real > 0.0)
        """
        return self.__cardinfo.SB

    @SB.setter
    def SB(self, value: float) -> None:
        self.__cardinfo.SB = value
        self.last_status_message()

    @property
    def FT(self) -> str:
        """
           Failure theory. The following theories are allowed (Character or blank. If blank, then no failure calculation will be performed) See Remark 7.
           “HILL” for the Hill theory.
           “HOFF” for the Hoffman theory.
           “TSAI” for the Tsai-Wu theory.
           “STRN” for the Maximum Strain theory.
           * Remark 7:
           In order to get failure index output the following must be present:
           a.ELSTRESS or ELSTRAIN Case Control commands,
           b. SB, FT, and SOUTi on the PCOMP Bulk Data entry,
           c. Xt, Xc, Yt, Yc, and S on all referenced MAT8 Bulk Data entries if stress allowables are used, or Xt, Xc, Yt, S, and STRN = 1.0 if strain allowables are used.
        """
        return self.__cardinfo.FT

    @FT.setter
    def FT(self, value: str) -> None:
        self.__cardinfo.FT = value
        self.last_status_message()

    @property
    def TREF(self) -> float:
        """
           Reference temperature. See Remark 3. (Real; Default = 0.0)
           * Remark 3:
           The TREF specified on the material entries referenced by plies are not used.
           Instead TREF on the PCOMP entry is used for all plies of the element.If not specified, it defaults to “0.0.”
           If the PCOMP references temperature dependent material properties, then the TREF given on the PCOMP will be used as the temperature to determine
           material properties.
           TEMPERATURE Case Control commands are ignored for deriving the equivalent PSHELL and MAT2 entries used to describe the composite element.
           If for a nonlinear static analysis the parameter COMPMATT is set to YES, the temperature at the current load step will be used to determine temperature dependent
           material properties for the plies and the equivalent PSHELL and MAT2 entries for the composite element.The TREF on the PCOMP entry will
           be used for the initial thermal strain on the composite element and the stresses on the individual plies.If the parameter EPSILONT is also set to
           INTEGRAL,TREF is not applicable.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value
        self.last_status_message()

    @property
    def GE(self) -> float:
        """
           Damping coefficient. See Remarks 4. and 12. (Real; Default = 0.0)
           * Remark 4:
           GE given on the PCOMP entry will be used for the element and the values supplied on material entries for individual plies are ignored.The user is
           responsible for supplying the equivalent damping value on the PCOMP entry.If PARAM, W4 is not specified GE is ignored in transient analysis. See
           “Parameters” on page 631.
           * Remark 12:
           To obtain the damping coefficient GE, multiply the critical damping ratio C ⁄ C0 by 2.0.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value
        self.last_status_message()

    @property
    def LAM(self) -> str:
        """
           Laminate Options. (Character or blank, Default = blank). See Remarks 13. and 14.
           “Blank” All plies must be specified and all stiffness terms are developed.
           “SYM” Only plies on one side of the element centerline are specified. The plies are numbered starting with 1 for the bottom layer.If an odd number of plies
           are desired, the center ply thickness (T1) should be half the actual thickness.
           “MEM” All plies must be specified, but only membrane terms (MID1 on the derived PSHELL entry) are computed.
           “BEND” All plies must be specified, but only bending terms (MID2 on the derived PSHELL entry) are computed.
           “SMEAR” All plies must be specified, stacking sequence is ignored MID1 = MID2 on the derived PSHELL entry and MID3, MID4 and TS/T and 12I/T**3 terms are
           set as blanks).
           “SMCORE”All plies must be specified, with the last ply specifying core properties and the previous plies specifying face sheet properties.
           The stiffness matrix is computed by placing half the face sheet thicknesses above the core and the other half below with the result that the laminate is
           symmetric about the midplane of the core.Stacking sequence is ignored in calculating the face sheet stiffness.
           * Remark 13:
           The SYM option for the LAM option computes the complete stiffness properties while specifying half the plies.The MEM, BEND, SMEAR and
           SMCORE options provide special purpose stiffness calculations.SMEAR ignores stacking sequence and is intended for cases where this sequence is
           not yet known, stiffness properties are smeared. SMCORE allows simplified modeling of a sandwich panel with equal face sheets and a central core.
           * Remark 14:
           Element output for the SMEAR and SMCORE options is produced using the PARAM NOCOMPS -1 methodology that suppresses ply stress/strain
           results and prints results for the equivalent homogeneous element.
        """
        return self.__cardinfo.LAM

    @LAM.setter
    def LAM(self, value: str) -> None:
        self.__cardinfo.LAM = value
        self.last_status_message()

    def GetPlyMaterialId(self, plyIndex: int) -> int:
        """
           Gets the Material ID (MIDi) for the specified ply.
           According to the PCOMP Documentation, MID1 must be specified, while subsequent MIDs can be blank.
           When blank, a ply's material ID defaults to the last explicitly defined material ID.
           1-based index of the ply (1 = first ply at bottom of laminate).
           The material ID as a nullable integer. Returns null if the ply's MID is blank.
           Returns null if the ply index is invalid or ply arrays haven't been initialized.
        """
        return self.__cardinfo.GetPlyMaterialId(plyIndex)

    def SetPlyMaterialId(self, plyIndex: int, midValue: int) -> None:
        """
            Sets only the Material ID (MIDi) for a specific ply.
            According to the PCOMP Documentation, MID1 must be specified (not null),
            while subsequent MIDs can be blank (in which case they inherit from the last defined MID).
            1-based index of the ply (1 = first ply at bottom of laminate)
            Material ID value to set, or null to indicate blank (inheritance from previous ply).
            Must refer to a valid MAT1, MAT2, MAT8, or MATDIGI entry.
        """
        self.__cardinfo.SetPlyMid(plyIndex, midValue)
        self.last_status_message()
        return None

    def GetPlyThickness(self, plyIndex: int) -> float:
        """
            Gets the Thickness (Ti) for the specified ply.
            According to the PCOMP Documentation, T1 must be specified, while subsequent thicknesses can be blank.
            When blank, a ply's thickness defaults to the last explicitly defined thickness.
            1-based index of the ply (1 = first ply at bottom of laminate).
            The thickness as a nullable float. Returns null if the ply's thickness is blank.
            Returns null if the ply index is invalid or ply arrays haven't been initialized.
        """
        return self.__cardinfo.GetPlyThickness(plyIndex)

    def SetPlyThickness(self, plyIndex: int, thicknessValue: float) -> None:
        """
            Sets only the Thickness (Ti) for a specific ply.
            According to the PCOMP Documentation, T1 must be specified (not null) and > 0.0,
            while subsequent thicknesses can be blank (in which case they inherit from the last defined T).
            1-based index of the ply (1 = first ply at bottom of laminate).
            Thickness value to set, or null to indicate blank (inheritance from previous ply).
            When specified, must be greater than 0.0.
        """
        self.__cardinfo.SetPlyT(plyIndex, thicknessValue)  
        self.last_status_message()
        return None
    
    def GetPlyOrientation(self, plyIndex: int) -> float:
        """
            Gets the Orientation Angle (THETAi) for the specified ply.
            According to the PCOMP Documentation, this field can be blank for any ply, defaulting to 0.0.
            The angle defines the orientation of the ply's longitudinal direction relative to the element's material axis.
            1-based index of the ply (1 = first ply at bottom of laminate).
            The orientation angle as a nullable float in degrees. Returns null if the ply's angle is blank (default 0.0).
            Returns null if the ply index is invalid or ply arrays haven't been initialized.
        """
        return self.__cardinfo.GetPlyOrientation(plyIndex)
    
    def SetPlyOrientation(self, plyIndex: int, thetaValue: float) -> None:
        """
            Sets only the Orientation Angle (THETAi) for a specific ply.
            According to the PCOMP Documentation, this field can be blank for any ply, defaulting to 0.0.
            The angle is measured in degrees and defines the orientation of the ply's longitudinal direction 
            relative to the element's material axis.
            1-based index of the ply (1 = first ply at bottom of laminate).
            Orientation angle to set in degrees, or null to indicate blank/default (0.0).
        """
        self.__cardinfo.SetPlyTheta(plyIndex, thetaValue)
        self.last_status_message()
        return None
    
    def GetPlyOutputRequest(self, plyIndex: int) -> str:
        """
            Gets the Stress/Strain Output Request (SOUTi) for the specified ply.
            According to the PCOMP Documentation, this field can be "YES", "NO", or blank (defaulting to "NO").
            This controls whether stress/strain results are calculated and made available for output for this ply.
            1-based index of the ply (1 = first ply at bottom of laminate).
            The output request as a string "YES", "NO", or null if blank. 
            Returns null if the ply index is invalid or ply arrays haven't been initialized.
        """
        return self.__cardinfo.GetPlyOutputRequest(plyIndex)
    
    def SetPlyOutputRequest(self, plyIndex: int, soutValue: str) -> bool:
        """
            Sets only the Stress/Strain Output Request (SOUTi) for a specific ply.
            According to the PCOMP Documentation, this field can be "YES", "NO", or blank (defaulting to "NO").
            This controls whether stress/strain results are calculated and available for output for this ply.
            1-based index of the ply (1 = first ply at bottom of laminate).
            Boolean value indicating output request: true for "YES", false for "NO", or null to indicate blank (default "NO").
        """
        self.__cardinfo.SetPlyOutputRequest(plyIndex, soutValue)
        self.last_status_message()
        return None

    def GetNumberOfPlies(self) -> int:
        """
            Gets the number of plies that make up this composite laminate, accounting for symmetric effects.
            For standard laminates: Returns a positive integer representing the number of plies defined in the card.
            For symmetric laminates (LAM=SYM): Returns a negative integer whose absolute value equals the number 
            of plies defined in the card. This negative value indicates that the actual physical laminate 
            has twice as many plies, since the solver mirrors the defined plies.
            Returns 0 if no plies have been defined or if the ply arrays haven't been initialized.
        """
        return self.__cardinfo.GetNumberOfPlies()



class PCOMPOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPcompOpt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (0 < Integer < 10000000)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def Z0(self) -> float:
        """
           Distance from the reference plane to the bottom surface. See Remark 10. (Real; Default = -0.5 times the element thickness.)
           * Remark 10:
           If the value specified for Z0 is not equal to -0.5 times the thickness of the element and PARAM,NOCOMPS,-1 is specified, then the homogeneous
           element stresses are incorrect, while element forces and strains are correct. For correct homogeneous stresses, use ZOFFS on the corresponding
           connection entry.
        """
        return self.__cardinfo.Z0

    @Z0.setter
    def Z0(self, value: float) -> None:
        self.__cardinfo.Z0 = value

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit area. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value

    @property
    def SB(self) -> float:
        """
           Allowable shear stress of the bonding material (allowable interlaminar shear stress). Required if FT is also specified. (Real > 0.0)
        """
        return self.__cardinfo.SB

    @SB.setter
    def SB(self, value: float) -> None:
        self.__cardinfo.SB = value

    @property
    def FT(self) -> str:
        """
           Failure theory. The following theories are allowed (Character or blank. If blank, then no failure calculation will be performed) See Remark 7.
           “HILL” for the Hill theory.
           “HOFF” for the Hoffman theory.
           “TSAI” for the Tsai-Wu theory.
           “STRN” for the Maximum Strain theory.
           * Remark 7:
           In order to get failure index output the following must be present:
           a.ELSTRESS or ELSTRAIN Case Control commands,
           b. SB, FT, and SOUTi on the PCOMP Bulk Data entry,
           c. Xt, Xc, Yt, Yc, and S on all referenced MAT8 Bulk Data entries if stress allowables are used, or Xt, Xc, Yt, S, and STRN = 1.0 if strain allowables are used.
        """
        return self.__cardinfo.FT

    @FT.setter
    def FT(self, value: str) -> None:
        self.__cardinfo.FT = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature. See Remark 3. (Real; Default = 0.0)
           * Remark 3:
           The TREF specified on the material entries referenced by plies are not used.
           Instead TREF on the PCOMP entry is used for all plies of the element.If not specified, it defaults to “0.0.”
           If the PCOMP references temperature dependent material properties, then the TREF given on the PCOMP will be used as the temperature to determine
           material properties.
           TEMPERATURE Case Control commands are ignored for deriving the equivalent PSHELL and MAT2 entries used to describe the composite element.
           If for a nonlinear static analysis the parameter COMPMATT is set to YES, the temperature at the current load step will be used to determine temperature dependent
           material properties for the plies and the equivalent PSHELL and MAT2 entries for the composite element.The TREF on the PCOMP entry will
           be used for the initial thermal strain on the composite element and the stresses on the individual plies.If the parameter EPSILONT is also set to
           INTEGRAL,TREF is not applicable.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Damping coefficient. See Remarks 4. and 12. (Real; Default = 0.0)
           * Remark 4:
           GE given on the PCOMP entry will be used for the element and the values supplied on material entries for individual plies are ignored.The user is
           responsible for supplying the equivalent damping value on the PCOMP entry.If PARAM, W4 is not specified GE is ignored in transient analysis. See
           “Parameters” on page 631.
           * Remark 12:
           To obtain the damping coefficient GE, multiply the critical damping ratio C ⁄ C0 by 2.0.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def LAM(self) -> str:
        """
           Laminate Options. (Character or blank, Default = blank). See Remarks 13. and 14.
           “Blank” All plies must be specified and all stiffness terms are developed.
           “SYM” Only plies on one side of the element centerline are specified. The plies are numbered starting with 1 for the bottom layer.If an odd number of plies
           are desired, the center ply thickness (T1) should be half the actual thickness.
           “MEM” All plies must be specified, but only membrane terms (MID1 on the derived PSHELL entry) are computed.
           “BEND” All plies must be specified, but only bending terms (MID2 on the derived PSHELL entry) are computed.
           “SMEAR” All plies must be specified, stacking sequence is ignored MID1 = MID2 on the derived PSHELL entry and MID3, MID4 and TS/T and 12I/T**3 terms are
           set as blanks).
           “SMCORE”All plies must be specified, with the last ply specifying core properties and the previous plies specifying face sheet properties.
           The stiffness matrix is computed by placing half the face sheet thicknesses above the core and the other half below with the result that the laminate is
           symmetric about the midplane of the core.Stacking sequence is ignored in calculating the face sheet stiffness.
           * Remark 13:
           The SYM option for the LAM option computes the complete stiffness properties while specifying half the plies.The MEM, BEND, SMEAR and
           SMCORE options provide special purpose stiffness calculations.SMEAR ignores stacking sequence and is intended for cases where this sequence is
           not yet known, stiffness properties are smeared. SMCORE allows simplified modeling of a sandwich panel with equal face sheets and a central core.
           * Remark 14:
           Element output for the SMEAR and SMCORE options is produced using the PARAM NOCOMPS -1 methodology that suppresses ply stress/strain
           results and prints results for the equivalent homogeneous element.
        """
        return self.__cardinfo.LAM

    @LAM.setter
    def LAM(self, value: str) -> None:
        self.__cardinfo.LAM = value

    @property
    def MIDi(self) -> list[int]:
        """
           Material ID of the various plies.The plies are identified by serially numbering them from 1 at the bottom layer. The MIDs must refer to MAT1,
           MAT2, or MAT8 Bulk Data entries.See Remarks 1. and 15. (Integer > 0 or blank, except MID1 must be specified.)
           * Remark 1:
           The default for MID2, ..., MIDn is the last defined MIDi. In the example above, MID1 is the default for MID2, MID3, and MID4.The same logic applies to Ti.
           * Remark 15:
           Temperature-dependent ply properties only available in SOL 106. See PARAM,COMPMATT for details.
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.MIDi), self.__cardinfo.MIDi)

    @MIDi.setter
    def MIDi(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.MIDi[i] = val

    @property
    def Ti(self) -> list[float]:
        """
           Thicknesses of the various plies. See Remarks 1. (Real or blank, except T1 must be specified.)
           * Remark 1:
           The default for MID2, ..., MIDn is the last defined MIDi. In the example above, MID1 is the default for MID2, MID3, and MID4.The same logic applies to Ti.
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.Ti), self.__cardinfo.Ti)

    @Ti.setter
    def Ti(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.Ti[i] = val

    @property
    def THETAi(self) -> list[float]:
        """
           Thicknesses of the various plies. See Remarks 1. (Real or blank, except T1 must be specified.)
           * Remark 1:
           The default for MID2, ..., MIDn is the last defined MIDi. In the example above, MID1 is the default for MID2, MID3, and MID4.The same logic applies to Ti.
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.THETAi), self.__cardinfo.THETAi)

    @THETAi.setter
    def THETAi(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.THETAi[i] = val

    @property
    def SOUTi(self) -> list[str]:
        """
           Stress or strain output request. See Remarks 5. and 6. (Character: “YES” or “NO”; Default = “NO”)
           * Remark 5:
           Stress and strain output for individual plies are available in all superelement static and normal modes analysis and requested by the STRESS and STRAIN
           Case Control commands.
           * Remark 6:
           If PARAM,NOCOMPS is set to -1, stress and strain output for individual plies will be suppressed and the homogeneous stress and strain output will be printed.
           See also Remark 10.
           * Remark 10:
           If the value specified for Z0 is not equal to -0.5 times the thickness of the element and PARAM,NOCOMPS,-1 is specified, then the homogeneous
           element stresses are incorrect, while element forces and strains are correct. For correct homogeneous stresses, use ZOFFS on the corresponding
           connection entry.
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.SOUTi), self.__cardinfo.SOUTi)

    @SOUTi.setter
    def SOUTi(self, value: list[str]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.SOUTi[i] = val

    @property
    def DS(self) -> float:
        """
           Design switch. If non-zero (1.0), the elements associated with this PCOMP data are included in the topology design volume or space. Default = blank
           (Real = 1.0 or blank)
        """
        return self.__cardinfo.DS

    @DS.setter
    def DS(self, value: float) -> None:
        self.__cardinfo.DS = value

    @property
    def NRPT(self) -> int:
        """
           Number of repeat laminates 20. Default = blank(Integer > 0 or blank)
        """
        return self.__cardinfo.NRPT

    @NRPT.setter
    def NRPT(self, value: int) -> None:
        self.__cardinfo.NRPT = value

    @property
    def EXPLICIT(self) -> str:
        """
           Flag indicating that parameters for Explicit Analysis are to follow.
        """
        return self.__cardinfo.EXPLICIT

    @EXPLICIT.setter
    def EXPLICIT(self, value: str) -> None:
        self.__cardinfo.EXPLICIT = value

    @property
    def ISOPE(self) -> str:
        """
           Element formulation flag for Explicit Analysis. 21 22 23
           BT                                                                       Belytschko-Tsay.
           BWC(Default for four-noded CQUAD4 elements in explicit analysis)          Belytschko-Wong-Chiang with full projection.
           blank
        """
        return self.__cardinfo.ISOPE

    @ISOPE.setter
    def ISOPE(self, value: str) -> None:
        self.__cardinfo.ISOPE = value

    @property
    def HGID(self) -> int:
        """
           Identification number of the hourglass control (HOURGLS) entry. Default = Blank(Integer > 0)
        """
        return self.__cardinfo.HGID

    @HGID.setter
    def HGID(self, value: int) -> None:
        self.__cardinfo.HGID = value

    @property
    def NIP(self) -> int:
        """
           Number of Gauss points through thickness. Default = 3 (1 ≤ Integer ≤ 10)
        """
        return self.__cardinfo.NIP

    @NIP.setter
    def NIP(self, value: int) -> None:
        self.__cardinfo.NIP = value


class PELAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def PID1(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID1

    @PID1.setter
    def PID1(self, value: int) -> None:
        self.__cardinfo.PID1 = value
        self.last_status_message()

    @property
    def K1(self) -> float:
        """
           Elastic property value. (Real)
        """
        return self.__cardinfo.K1

    @K1.setter
    def K1(self, value: float) -> None:
        self.__cardinfo.K1 = value
        self.last_status_message()

    @property
    def GE1(self) -> float:
        """
           Damping coefficient, . See Remarks 5. and 6. (Real)
        """
        return self.__cardinfo.GE1

    @GE1.setter
    def GE1(self, value: float) -> None:
        self.__cardinfo.GE1 = value
        self.last_status_message()

    @property
    def S1(self) -> float:
        """
           Stress coefficient. (Real)
        """
        return self.__cardinfo.S1

    @S1.setter
    def S1(self, value: float) -> None:
        self.__cardinfo.S1 = value
        self.last_status_message()

    @property
    def PID2(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID2

    @PID2.setter
    def PID2(self, value: int) -> None:
        self.__cardinfo.PID2 = value
        self.last_status_message()

    @property
    def K2(self) -> float:
        """
           Elastic property value. (Real)
        """
        return self.__cardinfo.K2

    @K2.setter
    def K2(self, value: float) -> None:
        self.__cardinfo.K2 = value
        self.last_status_message()

    @property
    def GE2(self) -> float:
        """
           Damping coefficient, . See Remarks 5. and 6. (Real)
        """
        return self.__cardinfo.GE2

    @GE2.setter
    def GE2(self, value: float) -> None:
        self.__cardinfo.GE2 = value
        self.last_status_message()

    @property
    def S2(self) -> float:
        """
           Stress coefficient. (Real)
        """
        return self.__cardinfo.S2

    @S2.setter
    def S2(self, value: float) -> None:
        self.__cardinfo.S2 = value
        self.last_status_message()


class PFAST(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def D(self) -> float:
        """
           D
        """
        return self.__cardinfo.D

    @D.setter
    def D(self, value: float) -> None:
        self.__cardinfo.D = value
        self.last_status_message()

    @property
    def MCID(self) -> int:
        """
           MCID
        """
        return self.__cardinfo.MCID if self.__cardinfo.MCID is not None else -1

    @MCID.setter
    def MCID(self, value: int) -> None:
        self.__cardinfo.MCID = value
        self.last_status_message()

    @property
    def MFLAG(self) -> int:
        """
           MCID
        """
        return self.__cardinfo.MFLAG

    @MFLAG.setter
    def MFLAG(self, value: int) -> None:
        self.__cardinfo.MFLAG = value
        self.last_status_message()

    @property
    def KT1(self) -> float:
        """
           KT1
        """
        return self.__cardinfo.KT1

    @KT1.setter
    def KT1(self, value: float) -> None:
        self.__cardinfo.KT1 = value
        self.last_status_message()

    @property
    def KT2(self) -> float:
        """
           KT2
        """
        return self.__cardinfo.KT2

    @KT2.setter
    def KT2(self, value: float) -> None:
        self.__cardinfo.KT2 = value
        self.last_status_message()

    @property
    def KT3(self) -> float:
        """
           KT3
        """
        return self.__cardinfo.KT3

    @KT3.setter
    def KT3(self, value: float) -> None:
        self.__cardinfo.KT3 = value
        self.last_status_message()

    @property
    def KR1(self) -> float:
        """
           KR1
        """
        return self.__cardinfo.KR1

    @KR1.setter
    def KR1(self, value: float) -> None:
        self.__cardinfo.KR1 = value
        self.last_status_message()

    @property
    def KR2(self) -> float:
        """
           KR2
        """
        return self.__cardinfo.KR2

    @KR2.setter
    def KR2(self, value: float) -> None:
        self.__cardinfo.KR2 = value
        self.last_status_message()

    @property
    def KR3(self) -> float:
        """
           KR3
        """
        return self.__cardinfo.KR3

    @KR3.setter
    def KR3(self, value: float) -> None:
        self.__cardinfo.KR3 = value
        self.last_status_message()

    @property
    def MASS(self) -> float:
        """
           MASS
        """
        return self.__cardinfo.MASS

    @MASS.setter
    def MASS(self, value: float) -> None:
        self.__cardinfo.MASS = value
        self.last_status_message()

    @property
    def GE(self) -> float:
        """
           Structural damping
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value
        self.last_status_message()

    @property
    def ALPHA(self) -> float:
        """
           Thermal expansion coefficient for the CFAST.(Real; Default=0.0)
        """
        return self.__cardinfo.ALPHA

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA = value
        self.last_status_message()

    @property
    def TREF(self) -> float:
        """
        Reference temperature for the calculation of thermal loads. (Real; Default=0.0)
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value
        self.last_status_message()

    @property
    def COINL(self) -> float:
        """
            Length of a CFAST with coincident grids. (Real; Default=0.0, COINL ≥ 0.0)
        """
        return self.__cardinfo.COINL
    
    @COINL.setter
    def COINL(self, value: float) -> None:
        self.__cardinfo.COINL = value
        self.last_status_message()

class PLOAD4NAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo
    
    @property
    def SID(self) -> int:
        """
            Load set identification number. (Integer > 0)
        """
        return self.__cardinfo.SID
    
    @SID.setter
    def SID(self, value: int) -> None:
        self.__cardinfo.SID = value
        self.last_status_message()
    
    @property
    def EID(self) -> int:
        """
            Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def EID1(self) -> int:
        """
            Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID1

    @EID1.setter
    def EID1(self, value: int) -> None:
        self.__cardinfo.EID1 = value
        self.last_status_message()

    @property
    def EID2(self) -> int:
        """
            Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID2

    @EID2.setter
    def EID2(self, value: int) -> None:
        self.__cardinfo.EID2 = value
        self.last_status_message()

    @property
    def P1(self) -> float:
        """
        Load per unit surface area (pressure) at the corners of the face of the element. (Real or 
        blank; Default for P2, P3, and P4 is P1.)
        """
        return self.__cardinfo.P1

    @P1.setter
    def P1(self, value: float) -> None:
        self.__cardinfo.P1 = value
        self.last_status_message()
    
    @property
    def P2(self) -> float:
        """
        Load per unit surface area (pressure) at the corners of the face of the element. (Real or
        blank; Default for P2, P3, and P4 is P1.)
        """
        return self.__cardinfo.P2
    
    @P2.setter
    def P2(self, value: float) -> None:
        self.__cardinfo.P2 = value
        self.last_status_message()

    @property
    def P3(self) -> float:
        """
        Load per unit surface area (pressure) at the corners of the face of the element. (Real or
        blank; Default for P2, P3, and P4 is P1.)
        """
        return self.__cardinfo.P3

    @P3.setter
    def P3(self, value: float) -> None:
        self.__cardinfo.P3 = value
        self.last_status_message()

    @property
    def P4(self) -> float:
        """
        Load per unit surface area (pressure) at the corners of the face of the element. (Real or
        blank; Default for P2, P3, and P4 is P1.)
        """
        return self.__cardinfo.P4
    
    @P4.setter
    def P4(self, value: float) -> None:
        self.__cardinfo.P4 = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
        Identification number of a grid point connected to a corner of the face. Required data 
        for solid elements only. (Integer > 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def G3_or_G4(self) -> int:
        """
        Identification number of a grid point
        """
        return self.__cardinfo.G3_or_G4

    @G3_or_G4.setter
    def G3_or_G4(self, value: int) -> None:
        self.__cardinfo.G3_or_G4 = value
        self.last_status_message()

    @property
    def CID(self) -> int:
        """
        Coordinate system identification number. (Integer >= 0; Default = 0)
        """
        return self.__cardinfo.CID
    
    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value
        self.last_status_message()

    @property
    def N1(self) -> float:
        """
        Identification number of a grid point connected to a corner of the face. Required data
        for solid elements only. (Integer > 0 or blank)
        """
        return self.__cardinfo.N1

    @N1.setter
    def N1(self, value: int) -> None:
        self.__cardinfo.N1 = value
        self.last_status_message()

    @property
    def N2(self) -> float:
        """
        Identification number of a grid point connected to a corner of the face. Required data
        for solid elements only. (Integer > 0 or blank)
        """
        return self.__cardinfo.N2

    @N2.setter
    def N2(self, value: int) -> None:
        self.__cardinfo.N2 = value
        self.last_status_message()

    @property
    def N3(self) -> float:
        """
        Identification number of a grid point connected to a corner of the face. Required data
        for solid elements only. (Integer > 0 or blank)
        """
        return self.__cardinfo.N3

    @N3.setter
    def N3(self, value: int) -> None:
        self.__cardinfo.N3 = value
        self.last_status_message()

    @property
    def SORL(self) -> str:
        """
        The character string SURF or LINE. SURF means the surface load acting on the 
        surface of the element and LINE means the consistent edge loads acting on the edges 
        of the element. The default is SURF. 
        """
        return self.__cardinfo.SORL
    
    @SORL.setter
    def SORL(self, value: str) -> None:
        self.__cardinfo.SORL = value
        self.last_status_message()

    @property
    def LDIR(self) -> str:
        """
        Denote the direction of the line load (SORL=LINE), character string X, Y, Z, TANG, 
        or NORM. The default is NORM.
        """
        return self.__cardinfo.LDIR

    @LDIR.setter
    def LDIR(self, value: str) -> None:
        self.__cardinfo.LDIR = value
        self.last_status_message()


class PGAPNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID  
    
    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def U0(self) -> float:
        """
              Initial gap opening. (Real)
        """
        return self.__cardinfo.U0
    
    @U0.setter
    def U0(self, value: float) -> None:
        self.__cardinfo.U0 = value
        self.last_status_message()

    @property
    def F0(self) -> float:
        """
        Preload
        """
        return self.__cardinfo.F0

    @F0.setter
    def F0(self, value: float) -> None:
        self.__cardinfo.F0 = value
        self.last_status_message()

    @property
    def KA(self) -> float:
        """
        Axial stiffness for the closed gap; i.e., Ua - Ub > U0 (Real > 0.0)
        """
        return self.__cardinfo.KA

    @KA.setter
    def KA(self, value: float) -> None:
        self.__cardinfo.KA = value
        self.last_status_message()

    @property
    def KB(self) -> float:
        """
        Axial stiffness for the opening gap. Ua - Ub < U0 (Real > 0.0; Default = 10^-14 * KA)
        """
        return self.__cardinfo.KB
    
    @KB.setter
    def KB(self, value: float) -> None:
        self.__cardinfo.KB = value
        self.last_status_message()

    @property
    def KT(self) -> float:
        """
        Transverse stiffness when the gap is closed. It is recommended that KT >= 0.1 * KA. (Real > 0.0; Default = MU1 * KA)
        """
        return self.__cardinfo.KT

    @KT.setter
    def KT(self, value: float) -> None:
        self.__cardinfo.KT = value
        self.last_status_message()

    @property
    def MU1(self) -> float:
        """
        Coefficient of static friction for the adaptive gap element or coefficient of friction 
        in the y transverse direction for the nonadaptive gap element (Real >= 0.0; Default = 0.0)
        """
        return self.__cardinfo.MU1

    @MU1.setter
    def MU1(self, value: float) -> None:
        self.__cardinfo.MU1 = value
        self.last_status_message()

    @property
    def MU2(self) -> float:
        """
        Coefficient of kinetic friction for the adaptive gap element or coefficient of friction 
        in the z transverse direction for the nonadaptive gap element. (Real >= 0.0 for the adaptive gap element, MU2 <= MU1; Default = MU1)
        """
        return self.__cardinfo.MU2

    @MU2.setter
    def MU2(self, value: float) -> None:
        self.__cardinfo.MU2 = value
        self.last_status_message()

    @property
    def TMAX(self) -> float:
        """
        Maximum allowable penetration used in the adjustment of penalty values. The positive 
        value activates the penalty value adjustment. (Real; Default = 0.0)
        """
        return self.__cardinfo.TMAX

    @TMAX.setter
    def TMAX(self, value: float) -> None:
        self.__cardinfo.TMAX = value
        self.last_status_message()

    @property
    def MAR(self) -> float:
        """
        Maximum allowable adjustment ratio for adaptive penalty values KA and KT.(Real; Default = 0.0)
        """
        return self.__cardinfo.MAR
    
    @MAR.setter
    def MAR(self, value: float) -> None:
        self.__cardinfo.MAR = value
        self.last_status_message()

    @property
    def TRMIN(self) -> float:
        """
        Fraction of TMAX defining the lower bound for the allowable penetration. (0.0 < Real < 1.0; Default = 0.001)
        """
        return self.__cardinfo.TRMIN
    
    @TRMIN.setter
    def TRMIN(self, value: float) -> None:
        self.__cardinfo.TRMIN = value
        self.last_status_message()

      
class PLOTEL(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPlotel)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           <para>PID: <see cref="CardPlotel"/> does not have an associate property. Returns <see cref="uint.MaxValue"/></para>
           <para>Implemented to use the interface <see cref="ICardElement"/></para>
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integer > 0 ; G1 ≠ G2)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value


class PLPLANE(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPlplane)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Identification number of a MATHP entry. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def CID(self) -> int:
        """
           Identification number of a coordinate system defining the plane of deformation.See Remarks 2. and 3. (Integer >= 0; Default = 0)
           * Remark 2:
           Plane strain hyperelastic elements must lie on the x-y plane of the CID coordinate system.Stresses and strains are output in the CID coordinate system.
           * Remark 3:
           Axisymmetric hyperelastic elements must lie on the x-y plane of the basic coordinate system.CID may not be specified and stresses and strains are
           output in the basic coordinate system.
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value

    @property
    def STR(self) -> str:
        """
           Location of stress and strain output. (Character: “GAUS” or “GRID”, Default = “GRID”)
        """
        return self.__cardinfo.STR

    @STR.setter
    def STR(self, value: str) -> None:
        self.__cardinfo.STR = value


class PMASS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPmass)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID1(self) -> int:
        """
           PIDi Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID1

    @PID1.setter
    def PID1(self, value: int) -> None:
        self.__cardinfo.PID1 = value

    @property
    def M1(self) -> float:
        """
           Mi Value of scalar mass. (Real)
        """
        return self.__cardinfo.M1

    @M1.setter
    def M1(self, value: float) -> None:
        self.__cardinfo.M1 = value

    @property
    def PID2(self) -> int:
        """
           PID2
        """
        return self.__cardinfo.PID2

    @PID2.setter
    def PID2(self, value: int) -> None:
        self.__cardinfo.PID2 = value

    @property
    def M2(self) -> float:
        """
           M2
        """
        return self.__cardinfo.M2

    @M2.setter
    def M2(self, value: float) -> None:
        self.__cardinfo.M2 = value

    @property
    def PID3(self) -> int:
        """
           PID3
        """
        return self.__cardinfo.PID3

    @PID3.setter
    def PID3(self, value: int) -> None:
        self.__cardinfo.PID3 = value

    @property
    def M3(self) -> float:
        """
           M3
        """
        return self.__cardinfo.M3

    @M3.setter
    def M3(self, value: float) -> None:
        self.__cardinfo.M3 = value

    @property
    def PID4(self) -> int:
        """
           PID4
        """
        return self.__cardinfo.PID4

    @PID4.setter
    def PID4(self, value: int) -> None:
        self.__cardinfo.PID4 = value

    @property
    def M4(self) -> float:
        """
           M4
        """
        return self.__cardinfo.M4

    @M4.setter
    def M4(self, value: float) -> None:
        self.__cardinfo.M4 = value


class PROD(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value
        self.last_status_message()

    @property
    def A(self) -> float:
        """
           Area of bar cross section. (Real)
        """
        return self.__cardinfo.A

    @A.setter
    def A(self, value: float) -> None:
        self.__cardinfo.A = value
        self.last_status_message()

    @property
    def J(self) -> float:
        """
           Torsional constant.
        """
        return self.__cardinfo.J

    @J.setter
    def J(self, value: float) -> None:
        self.__cardinfo.J = value
        self.last_status_message()

    @property
    def C(self) -> float:
        """
           Coefficient to determine torsional stress. (Real; Default = 0.0)
        """
        return self.__cardinfo.C

    @C.setter
    def C(self, value: float) -> None:
        self.__cardinfo.C = value
        self.last_status_message()

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit length. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value
        self.last_status_message()


class PSHEAR(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PLPLANE)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Material identification number
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def T(self) -> float:
        """
           Thickness of shear panel. (Real 0.0)
        """
        return self.__cardinfo.T

    @T.setter
    def T(self, value: float) -> None:
        self.__cardinfo.T = value

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit length. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value

    @property
    def F1(self) -> float:
        """
           F1
        """
        return self.__cardinfo.F1

    @F1.setter
    def F1(self, value: float) -> None:
        self.__cardinfo.F1 = value

    @property
    def F2(self) -> float:
        """
           F2
        """
        return self.__cardinfo.F2

    @F2.setter
    def F2(self, value: float) -> None:
        self.__cardinfo.F2 = value


class PSHELLNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def MID1(self) -> int:
        """
           Material identification number for the membrane. (Integer >= 0 or blank)
        """
        return self.__cardinfo.MID1

    @MID1.setter
    def MID1(self, value: int) -> None:
        self.__cardinfo.MID1 = value
        self.last_status_message()

    @property
    def T(self) -> float:
        """
           Default membrane thickness for Ti on the connection entry. If T is blank then the thickness must be specified for Ti on the CQUAD4, CTRIA3,
           CQUAD8, and CTRIA6 entries. (Real or blank)
        """
        return self.__cardinfo.T

    @T.setter
    def T(self, value: float) -> None:
        self.__cardinfo.T = value
        self.last_status_message()

    @property
    def MID2(self) -> int:
        """
           Material identification number for bending. (Integer >= -1 or blank)
        """
        return self.__cardinfo.MID2

    @MID2.setter
    def MID2(self, value: int) -> None:
        self.__cardinfo.MID2 = value
        self.last_status_message()

    @property
    def INERTIA(self) -> float:
        """
           Bending moment of inertia ratio, 12I T⁄ 3. Ratio of the actual bending moment inertia of the shell, I, to the bending moment of inertia of a
           homogeneous shell, T3 ⁄ 12. The default value is for a homogeneous shell. (Real > 0.0; Default = 1.0)
        """
        return self.__cardinfo.BenStiffPar

    @INERTIA.setter
    def INERTIA(self, value: float) -> None:
        self.__cardinfo.BenStiffPar = value
        self.last_status_message()

    @property
    def MID3(self) -> int:
        """
           Material identification number for transverse shear. (Integer > 0 or blank; unless MID2 > 0, must be blank.)
        """
        return self.__cardinfo.MID3

    @MID3.setter
    def MID3(self, value: int) -> None:
        self.__cardinfo.MID3 = value
        self.last_status_message()

    @property
    def TsT(self) -> float:
        """
           Transverse shear thickness ratio, . Ratio of the shear thickness, to the membrane thickness of the shell, T.The default value is for a
           homogeneous shell. (Real > 0.0; Default = .833333)
        """
        return self.__cardinfo.TsT

    @TsT.setter
    def TsT(self, value: float) -> None:
        self.__cardinfo.TsT = value
        self.last_status_message()

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit area. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value
        self.last_status_message()

    @property
    def Z1(self) -> float:
        """
           Fiber distances for stress calculations. The positive direction is determined by the right-hand rule, and the order in which the grid
           points are listed on the connection entry.See Remark 11. for defaults. (Real or blank)
           * Remark 11:
           The default for Z1 is -T/2, and for Z2 is +T/2. T is the local plate thickness defined either by T on this entry or by membrane thicknesses at connected
           grid points, if they are input on connection entries.
        """
        return self.__cardinfo.Z1

    @Z1.setter
    def Z1(self, value: float) -> None:
        self.__cardinfo.Z1 = value
        self.last_status_message()

    @property
    def Z2(self) -> float:
        """
           Z2
        """
        return self.__cardinfo.Z2

    @Z2.setter
    def Z2(self, value: float) -> None:
        self.__cardinfo.Z2 = value
        self.last_status_message()

    @property
    def MID4(self) -> int:
        """
           Material identification number for membrane-bending coupling. See Remarks 6. and 13. (Integer > 0 or blank, must be blank unless MID1 > 0 and MID2 > 0,
           may not equal MID1 or MID2.)
           * Remark 6:
           The following should be considered when using MID4.
           The MID4 field should be left blank if the material properties are symmetric with respect to the middle surface of the shell.If the element centerline
           is offset from the plane of the grid points but the material properties are symmetric, the preferred method for modeling the offset is by use
           of the ZOFFS field on the connection entry. Although the MID4 field may be used for this purpose, it may produce ill-conditioned stiffness matrices
           (negative terms on factor diagonal) if done incorrectly.
           Only one of the options MID4 or ZOFFS should be used; if both methods are specified the effects are cumulative.Since this is probably not what the user
           intented, unexpected answers will result. Note that the mass properties are not modified to reflect the existence of the offset when the ZOFFS and MID4
           methods are used.If the weight or mass properties of an offset plate are to be used in ananalysis, the RBAR method must be used to represent the offset. See
           “Shell Elements (CTRIA3, CTRIA6, CTRIAR, CQUAD4, CQUAD8, CQUADR)” on page 131 of the MSC.Nastran Reference Guide.
           The effects of MID4 are not considered in the calculation of differential stiffness.Therefore, it is recommended that MID4 be left blank in buckling analysis.
           * Remark 13:
           For the CQUADR and CTRIAR elements, the MID4 field should be left blankbecause their formulation does not include membrane-bending coupling.
        """
        return self.__cardinfo.MID4

    @MID4.setter
    def MID4(self, value: int) -> None:
        self.__cardinfo.MID4 = value
        self.last_status_message()


class PSHELLOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPshellOpt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID1(self) -> int:
        """
           Material identification number for the membrane. (Integer >= 0 or blank)
        """
        return self.__cardinfo.MID1

    @MID1.setter
    def MID1(self, value: int) -> None:
        self.__cardinfo.MID1 = value

    @property
    def T(self) -> float:
        """
           Default membrane thickness for Ti on the connection entry. If T is blank then the thickness must be specified for Ti on the CQUAD4, CTRIA3,
           CQUAD8, and CTRIA6 entries. (Real or blank)
        """
        return self.__cardinfo.T

    @T.setter
    def T(self, value: float) -> None:
        self.__cardinfo.T = value

    @property
    def MID2(self) -> int:
        """
           Material identification number for bending. (Integer >= -1 or blank)
        """
        return self.__cardinfo.MID2

    @MID2.setter
    def MID2(self, value: int) -> None:
        self.__cardinfo.MID2 = value

    @property
    def INERTIA(self) -> float:
        """
           Bending moment of inertia ratio, 12I T⁄ 3. Ratio of the actual bending moment inertia of the shell, I, to the bending moment of inertia of a
           homogeneous shell, T3 ⁄ 12. The default value is for a homogeneous shell. (Real > 0.0; Default = 1.0)
        """
        return self.__cardinfo.INERTIA

    @INERTIA.setter
    def INERTIA(self, value: float) -> None:
        self.__cardinfo.INERTIA = value

    @property
    def MID3(self) -> int:
        """
           Material identification number for transverse shear. (Integer > 0 or blank; unless MID2 > 0, must be blank.)
        """
        return self.__cardinfo.MID3

    @MID3.setter
    def MID3(self, value: int) -> None:
        self.__cardinfo.MID3 = value

    @property
    def TST(self) -> float:
        """
           Transverse shear thickness ratio, . Ratio of the shear thickness, to the membrane thickness of the shell, T.The default value is for a
           homogeneous shell. (Real > 0.0; Default = .833333)
        """
        return self.__cardinfo.TST

    @TST.setter
    def TST(self, value: float) -> None:
        self.__cardinfo.TST = value

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit area. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value

    @property
    def Z1(self) -> float:
        """
           Fiber distances for stress calculations. The positive direction is determined by the right-hand rule, and the order in which the grid
           points are listed on the connection entry.See Remark 11. for defaults. (Real or blank)
           * Remark 11:
           The default for Z1 is -T/2, and for Z2 is +T/2. T is the local plate thickness defined either by T on this entry or by membrane thicknesses at connected
           grid points, if they are input on connection entries.
        """
        return self.__cardinfo.Z1

    @Z1.setter
    def Z1(self, value: float) -> None:
        self.__cardinfo.Z1 = value

    @property
    def Z2(self) -> float:
        """
           Z2
        """
        return self.__cardinfo.Z2

    @Z2.setter
    def Z2(self, value: float) -> None:
        self.__cardinfo.Z2 = value

    @property
    def MID4(self) -> int:
        """
           Material identification number for membrane-bending coupling. See Remarks 6. and 13. (Integer > 0 or blank, must be blank unless MID1 > 0 and MID2 > 0,
           may not equal MID1 or MID2.)
           * Remark 6:
           The following should be considered when using MID4.
           The MID4 field should be left blank if the material properties are symmetric with respect to the middle surface of the shell.If the element centerline
           is offset from the plane of the grid points but the material properties are symmetric, the preferred method for modeling the offset is by use
           of the ZOFFS field on the connection entry. Although the MID4 field may be used for this purpose, it may produce ill-conditioned stiffness matrices
           (negative terms on factor diagonal) if done incorrectly.
           Only one of the options MID4 or ZOFFS should be used; if both methods are specified the effects are cumulative.Since this is probably not what the user
           intented, unexpected answers will result. Note that the mass properties are not modified to reflect the existence of the offset when the ZOFFS and MID4
           methods are used.If the weight or mass properties of an offset plate are to be used in ananalysis, the RBAR method must be used to represent the offset. See
           “Shell Elements (CTRIA3, CTRIA6, CTRIAR, CQUAD4, CQUAD8, CQUADR)” on page 131 of the MSC.Nastran Reference Guide.
           The effects of MID4 are not considered in the calculation of differential stiffness.Therefore, it is recommended that MID4 be left blank in buckling analysis.
           * Remark 13:
           For the CQUADR and CTRIAR elements, the MID4 field should be left blankbecause their formulation does not include membrane-bending coupling.
        """
        return self.__cardinfo.MID4

    @MID4.setter
    def MID4(self, value: int) -> None:
        self.__cardinfo.MID4 = value

    @property
    def T0(self) -> float:
        """
           The base thickness of the elements in topology and free-size optimization. Only for MAT1, T0 can be > 0.0. (Real ≥ 0.0 or blank for MAT1,
           Real = 0.0 or blank for MAT2, MAT8)
        """
        return self.__cardinfo.T0

    @T0.setter
    def T0(self, value: float) -> None:
        self.__cardinfo.T0 = value

    @property
    def ZOFFS(self) -> float:
        """
           Offset from the plane defined by element grid points to the shell reference plane. Real or Character Input(Top/Bottom)
        """
        return self.__cardinfo.ZOFFS

    @ZOFFS.setter
    def ZOFFS(self, value: float) -> None:
        self.__cardinfo.ZOFFS = value

    @property
    def EXPLICIT(self) -> str:
        """
           Flag indicating that parameters for Explicit Analysis are to follow.
        """
        return self.__cardinfo.EXPLICIT

    @EXPLICIT.setter
    def EXPLICIT(self, value: str) -> None:
        self.__cardinfo.EXPLICIT = value

    @property
    def ISOPE(self) -> int:
        """
           Element formulation flag for Explicit Analysis.
           BT                           Belytschko-Tsay.
           BWC                          Belytschko-Wong-Chiang with full projection. 4
           Blank
           Default = BWC for four-noded CQUAD4 elements in explicit analysis.
        """
        return self.__cardinfo.ISOPE

    @ISOPE.setter
    def ISOPE(self, value: int) -> None:
        self.__cardinfo.ISOPE = value

    @property
    def HGID(self) -> int:
        """
           Identification number of an hourglass control (HOURGLS) entry. Default = Blank(Integer > 0 or blank)
        """
        return self.__cardinfo.HGID

    @HGID.setter
    def HGID(self, value: int) -> None:
        self.__cardinfo.HGID = value

    @property
    def NIP(self) -> int:
        """
           Number of through thickness Gauss points. Default = 3 (1 ≤ Integer ≤ 10)
        """
        return self.__cardinfo.NIP

    @NIP.setter
    def NIP(self, value: int) -> None:
        self.__cardinfo.NIP = value


class PSOLIDNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def MID(self) -> int:
        """
           Identification number of a MAT1, MAT4, MAT5, MAT9, or MAT10 entry. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value
        self.last_status_message()

    @property
    def CORDM(self) -> int:
        """
           Identification number of a MAT1, MAT4, MAT5, MAT9, or MAT10 entry. (Integer > 0)
        """
        return self.__cardinfo.CORDM

    @CORDM.setter
    def CORDM(self, value: int) -> None:
        self.__cardinfo.CORDM = value
        self.last_status_message()

    @property
    def IN(self) -> str:
        """
           Integration network. See Remarks 5., 6., 7., and 9. (Integer, Character, or blank)
        """
        return self.__cardinfo.IN

    @IN.setter
    def IN(self, value: str) -> None:
        self.__cardinfo.IN = value
        self.last_status_message()

    @property
    def STRESS(self) -> str:
        """
           Location selection for stress output. See Remarks 8. and 9. (Integer, Character, or blank)
        """
        return self.__cardinfo.STRESS

    @STRESS.setter
    def STRESS(self, value: str) -> None:
        self.__cardinfo.STRESS = value
        self.last_status_message()

    @property
    def ISOP(self) -> str:
        """
           Integration scheme. See Remarks 5., 6., 7., and 9. (Integer, Character, or blank)
        """
        return self.__cardinfo.ISOP

    @ISOP.setter
    def ISOP(self, value: str) -> None:
        self.__cardinfo.ISOP = value
        self.last_status_message()

    @property
    def FCTN(self) -> str:
        """
           Fluid element flag. (Character: “PFLUID” indicates a fluid element, “SMECH” indicates a structural element; Default = “SMECH.”)
        """
        return self.__cardinfo.FCTN

    @FCTN.setter
    def FCTN(self, value: str) -> None:
        self.__cardinfo.FCTN = value
        self.last_status_message()


class PSOLIDOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PSOLID_NASTRAN)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0 or string)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Identification number of a MAT1, MAT4, MAT5, MAT9, or MAT10 entry. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def CORDM(self) -> int:
        """
           Identification number of a MAT1, MAT4, MAT5, MAT9, or MAT10 entry. (Integer > 0)
        """
        return self.__cardinfo.CORDM

    @CORDM.setter
    def CORDM(self, value: int) -> None:
        self.__cardinfo.CORDM = value

    @property
    def ISOP(self) -> str:
        """
           Integration scheme. See Remarks 5., 6., 7., and 9. (Integer, Character, or blank)
        """
        return self.__cardinfo.ISOP

    @ISOP.setter
    def ISOP(self, value: str) -> None:
        self.__cardinfo.ISOP = value

    @property
    def FCTN(self) -> str:
        """
           Fluid element flag. (Character: “PFLUID” indicates a fluid element, “SMECH” indicates a structural element; Default = “SMECH.”)
        """
        return self.__cardinfo.FCTN

    @FCTN.setter
    def FCTN(self, value: str) -> None:
        self.__cardinfo.FCTN = value

    @property
    def EXPLICIT(self) -> str:
        """
           Flag indicating that parameters for Explicit Analysis are to follow.
        """
        return self.__cardinfo.EXPLICIT

    @EXPLICIT.setter
    def EXPLICIT(self, value: str) -> None:
        self.__cardinfo.EXPLICIT = value

    @property
    def ISOPE(self) -> str:
        """
           sri: Selective reduced integration for eight-noded CHEXA and six-noded CPENTA elements in explicit analysis.Full integration for deviatoric term and one-point integration for bulk term.
           URI: Uniform reduced integration for eight-noded CHEXA elements in explicit analysis.One-point integration is used.
           AURI: Average uniform reduced integration for eight-noded CHEXA elements in explicit analysis.B matrix is a volume average over the element.
           AVE: Nodal pressure averaged formulation. 10
           Defaults:
           AURI for eight-noded CHEXA elements in explicit analysis.
           AVE for four-noded CTETRA elements in explicit analysis.
        """
        return self.__cardinfo.ISOPE

    @ISOPE.setter
    def ISOPE(self, value: str) -> None:
        self.__cardinfo.ISOPE = value

    @property
    def HGID(self) -> int:
        """
           Identification number of the hourglass control (HOURGLS) Bulk Data Entry. No default
        """
        return self.__cardinfo.HGID

    @HGID.setter
    def HGID(self, value: int) -> None:
        self.__cardinfo.HGID = value

    @property
    def HGHOR(self) -> str:
        """
           Specifies the element formulation for ten-noded CTETRA elements in explicit analysis.
        """
        return self.__cardinfo.HGHOR

    @HGHOR.setter
    def HGHOR(self, value: str) -> None:
        self.__cardinfo.HGHOR = value


class PWELD(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value
        self.last_status_message()

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value
        self.last_status_message()

    @property
    def D(self) -> float:
        """
           Diameter of the connector. (Real > 0.0)
        """
        return self.__cardinfo.D

    @D.setter
    def D(self, value: float) -> None:
        self.__cardinfo.D = value
        self.last_status_message()

    @property
    def MSET(self) -> str:
        """
           Active ONLY for "PARAM,OLDWELD,YES".
           Flag to eliminate m-set degrees-of-freedom
           (DOFs). The MSET parameter has no effect in a
           nonlinear SOL 400 analysis.
           =OFF m-set DOFs are eliminated, constraints are
           incorporated in the stiffness, see Remark 2.
           =ON m-set DOFs are not eliminated, constraints
           are generated.
        """
        return self.__cardinfo.MSET

    @MSET.setter
    def MSET(self, value: str) -> None:
        self.__cardinfo.MSET = value
        self.last_status_message()

    @property
    def TYPE(self) -> str:
        """
           Character string indicating the type of connection,
           see Remarks 3. and 4.
           =blank general connector
           = “SPOT” spot weld connector
        """
        return self.__cardinfo.TYPE

    @TYPE.setter
    def TYPE(self, value: str) -> None:
        self.__cardinfo.TYPE = value
        self.last_status_message()

    @property
    def LDMIN(self) -> float:
        """
           Active ONLY for "PARAM,OLDWELD,YES".
           Smallest ratio of length to diameter for stiffness
           calculation, see Remark 4.
        """
        return self.__cardinfo.LDMIN

    @LDMIN.setter
    def LDMIN(self, value: float) -> None:
        self.__cardinfo.LDMIN = value
        self.last_status_message()

    @property
    def LDMAX(self) -> float:
        """
           Active ONLY for "PARAM,OLDWELD,YES".
           Largest ratio of length to diameter for stiffness
           calculation, see Remark 4.
        """
        return self.__cardinfo.LDMAX

    @LDMAX.setter
    def LDMAX(self, value: float) -> None:
        self.__cardinfo.LDMAX = value
        self.last_status_message()


class RBAR(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def GA(self) -> int:
        """
           Grid point identification number of connection points. (Integer > 0)
           GA
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value
        self.last_status_message()

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value
        self.last_status_message()

    @property
    def CNA(self) -> [int]:
        """
            Component numbers of independent degrees-of-freedom in the global coordinate 
            system for the element at grid points GA and GB. (Integers 1 through 
            6 with no embedded blanks, or zero or blank.)
        """
        return self.__cardinfo.CNA

    @CNA.setter
    def CNA(self, value: int) -> None:
        self.__cardinfo.CNA = value
        self.last_status_message()

    @property
    def CNB(self) -> int:
        """
            Component numbers of independent degrees-of-freedom in the global coordinate 
            system for the element at grid points GA and GB. (Integers 1 through 
            6 with no embedded blanks, or zero or blank.)
        """
        return self.__cardinfo.CNB

    @CNB.setter
    def CNB(self, value: int) -> None:
        self.__cardinfo.CNB = value
        self.last_status_message()

    @property
    def CMA(self) -> int:
        """
            Component numbers of dependent degrees-of-freedom in the global coordinate 
            system assigned by the element at grid points GA and GB. 
            (Integers 1 through 6 with no embedded blanks, or zero or blank.)
        """
        return self.__cardinfo.CMA

    @CMA.setter
    def CMA(self, value: int) -> None:
        self.__cardinfo.CMA = value
        self.last_status_message()

    @property
    def CMB(self) -> int:
        """
           Component numbers of dependent degrees-of-freedom in the global coordinate 
            system assigned by the element at grid points GA and GB. 
            (Integers 1 through 6 with no embedded blanks, or zero or blank.)
        """
        return self.__cardinfo.CMB

    @CMB.setter
    def CMB(self, value: int) -> None:
        self.__cardinfo.CMB = value
        self.last_status_message()

    @property
    def ALPHA(self) -> float:
        """
           Thermal expansion coefficient.(Real > 0.0 or blank)
        """
        return self.__cardinfo.ALPHA

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA = value
        self.last_status_message()

    @property
    def TREF(self) -> float:
        """
            Reference temperature for the calculation of thermal loads. (Real; Default=0.0)
        """
        return self.__cardinfo.TREF
    
    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value
        self.last_status_message()


class RBAR1(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (RBAR1)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def GA(self) -> int:
        """
           Grid point identification number of connection points. (Integer > 0)
           GA
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value

    @property
    def CB(self) -> list[int]:
        """
           Component numbers in the global coordinate system at GB, which are constrained to move as the rigid bar.
           See Remark 4. (Integers 1 through6 with no embedded blanks or blank.)
           * Remark 4:
           When CB = “123456” or blank, the grid point GB is constrained to move with GA as a rigid bar.For default CB = “123456”.
           Any number of degrees-offreedom at grid point GB can be released not to move with the rigid body.
        """
        return list(self.__cardinfo.CB)

    @CB.setter
    def CB(self, value: list[int]) -> None:
        self.__cardinfo.CB = value

    @property
    def ALPHA(self) -> float:
        """
           Thermal expansion coefficient. See Remark 8. (Real > 0.0 or blank)
           * Remark 8:
           Rigid elements are ignored in heat transfer problems.
        """
        return self.__cardinfo.ALPHA

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA = value


class RBE1(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def GNI(self) -> list[int]:
        """
           Grid points at which independent degrees-of-freedom for the element are assigned. (Integer > 0)
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.GNI), self.__cardinfo.GNI)

    @GNI.setter
    def GNI(self, value: list[int]) -> None:
        self.__cardinfo.GNI = value
        self.last_status_message()

    @property
    def CNI(self) -> list[int]:
        """
           Independent degrees-of-freedom in the global coordinate system for the rigid element at grid point(s) GNi.
           See Remark 1. (Integers 1 through 6 with no embedded blanks.)
           * Remark 1:
           Two methods are available to process rigid elements: equation elimination or Lagrange multipliers.
           The Case Control command, RIGID, selects the method.
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.CNI), self.__cardinfo.CNI)

    @CNI.setter
    def CNI(self, value: list[int]) -> None:
        self.__cardinfo.CNI = value
        self.last_status_message()

    @property
    def GMI(self) -> list[int]:
        """
           Grid points at which dependent degrees-of-freedom are assigned. (Integer > 0)
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.GMI), self.__cardinfo.GMI)

    @GMI.setter
    def GMI(self, value: list[int]) -> None:
        self.__cardinfo.GMI = value
        self.last_status_message()

    @property
    def CMI(self) -> list[int]:
        """
           Dependent degrees-of-freedom in the global coordinate system at grid point(s) GMj. (Integers 1 through 6 with no embedded blanks.)
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.CMI), self.__cardinfo.CMI)

    @CMI.setter
    def CMI(self, value: list[int]) -> None:
        self.__cardinfo.CMI = value
        self.last_status_message()

    @property
    def ALPHA(self) -> float:
        """
           Thermal expansion coefficient. See Remark 13. (Real > 0.0 or blank)
           * Remark 13:
           For the Lagrange method, the thermal expansion effect will be computed, if user supplies the thermal expansion coefficient ALPHA, and the thermal
           load is requested by the TEMPERATURE(INITIAL) and TEMPERATURE(LOAD) Case Control commands.The temperature of the
           element is taken as follows: the temperature of the bar connecting the grid point GN1 and any dependent grid point are taken as the average
           temperature of the two connected grid points.
        """
        return self.__cardinfo.ALPHA

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA = value
        self.last_status_message()


    @property
    def TREF(self) -> float:
        """
            Reference temperature for the calculation of thermal loads. (Real; Default=0.0)
        """
        return self.__cardinfo.TREF
    
    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value
        self.last_status_message()

class RBE2(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def GN(self) -> int:
        """
           Identification number of grid point to which all six independent degrees-of-freedom for the element are assigned. (Integer > 0)
        """
        return self.__cardinfo.GN

    @GN.setter
    def GN(self, value: int) -> None:
        self.__cardinfo.GN = value
        self.last_status_message()

    @property
    def CM(self) -> int:
        """
           Component numbers of the dependent degrees-of-freedom in the global coordinate system at grid points GMi.
           (Integers 1 through 6 with no embedded blanks.)
        """
        return self.__cardinfo.CM

    @CM.setter
    def CM(self, value: int) -> None:
        self.__cardinfo.CM = value
        self.last_status_message()

    @property
    def GMI(self) -> list[int]:
        """
           Grid point identification numbers at which dependent degrees-offreedom are assigned. (Integer > 0)
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.GMI), self.__cardinfo.GMI)

    @GMI.setter
    def GMI(self, value: list[int]) -> None:
        self.__cardinfo.GMI = value
        self.last_status_message()

    @property
    def ALPHA(self) -> float:
        """
           Thermal expansion coefficient. See Remark 11. (Real > 0.0 or blank)
           * Remark 11:
           For the Lagrange method, the thermal expansion effect will be computed, if user supplies the thermal expansion coefficient ALPHA, and the thermal
           load is requested by the TEMPERATURE(INITIAL) and TEMPERATURE(LOAD) Case Control commands.The temperature of the element is taken as follows:
           the temperature of the bar connecting the grid point GN and any dependent grid point are taken as the average temperature of the two
           connected grid points.
        """
        return self.__cardinfo.ALPHA

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA = value
        self.last_status_message()

    @property
    def TREF(self) -> float:
        """
            Reference temperature for the calculation of thermal loads. (Real; Default=0.0)
        """
        return self.__cardinfo.TREF
    
    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value
        self.last_status_message()
        

class RBE3(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. Unique with respect to all elements. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def REFGRID(self) -> int:
        """
           Reference grid point identification number. (Integer > 0)
        """
        return self.__cardinfo.REFGRID

    @REFGRID.setter
    def REFGRID(self, value: int) -> None:
        self.__cardinfo.REFGRID = value
        self.last_status_message()

    @property
    def REFC(self) -> int:
        """
           Component numbers at the reference grid point. (Any of the integers 1 through 6 with no embedded blanks.)
        """
        return self.__cardinfo.REFC

    @REFC.setter
    def REFC(self, value: int) -> None:
        self.__cardinfo.REFC = value
        self.last_status_message()

    @property
    def WeightFactors(self) -> list[float]:
        """
           Weighting factor for components of motion on the following entry at grid points Gi,j. (Real)
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.WeightFactors), self.__cardinfo.WeightFactors)

    @WeightFactors.setter
    def WeightFactors(self, value: list[float]) -> None:
        for i, val in enumerate(value):
            self.__cardinfo.SetWeightFactor(i+1,val)
            self.last_status_message()

    @property
    def ComponentSpecifications(self) -> list[int]:
        """
           Component numbers with weighting factor WTi at grid points Gi,j. (Any of the integers 1 through 6 with no embedded blanks.)
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.ComponentSpecifications), self.__cardinfo.ComponentSpecifications)

    @ComponentSpecifications.setter
    def ComponentSpecifications(self, value: list[int]) -> None:
        for i, val in enumerate(value):
            self.__cardinfo.SetComponentSpecification(i+1,val)
            self.last_status_message()

    @property
    def GridPointsByGroup(self) -> list[list[int]]:
        """
           Grid points with components Ci that have weighting factor WTi in the averaging equations. (Integer > 0)
        """
        return IndexTrackingList([IndexTrackingList((item for item in sublist), sublist) for sublist in self.__cardinfo.GridPointsByGroup], self.__cardinfo.GridPointsByGroup)

    @GridPointsByGroup.setter
    def GridPointsByGroup(self, value: list[list[int]]) -> None:
        for i, val in enumerate(value):
            for j, val2 in enumerate(val):
                self.__cardinfo.SetGridPoint(i+1,j+1,val2)
                self.last_status_message()

    @property
    def GMI(self) -> list[int]:
        """
           Identification numbers of grid points with degrees-of-freedom in the m-set. (Integer > 0)
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.GMI), self.__cardinfo.GMI)

    @GMI.setter
    def GMI(self, value: list[int]) -> None:
        self.__cardinfo.GMI = value
        self.last_status_message()

    @property
    def CMI(self) -> list[int]:
        """
           Component numbers of GMi to be assigned to the m-set. (Any of the Integers 1 through 6 with no embedded blanks.)
        """
        return IndexTrackingList((ite for ite in self.__cardinfo.CMI), self.__cardinfo.CMI)

    @CMI.setter
    def CMI(self, value: list[int]) -> None:
        self.__cardinfo.CMI = value
        self.last_status_message()

    @property
    def ALPHA(self) -> float:
        """
           Thermal expansion coefficient. See Remark 14. (Real > 0.0 or blank)
           * Remark 13:
           For the Lagrange method, the thermal expansion effect will be computed, if user supplies the thermal expansion coefficient ALPHA, and the thermal
           load is requested by the TEMPERATURE(INITIAL) and TEMPERATURE(LOAD) Case Control commands.The temperature of the element is taken as follows:
           the temperature of the bar connecting the reference grid point REFGRID and any other grid point Gij are taken as the
           average temperature of the two connected grid points.
        """
        return self.__cardinfo.ALPHA

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA = value
        self.last_status_message()

    @property
    def TREF(self) -> float:
        """
            Reference temperature for the calculation of thermal loads. (Real; Default=0.0)
        """
        return self.__cardinfo.TREF
    
    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value
        self.last_status_message()


class RSPLINE(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value
        self.last_status_message()

    @property
    def DiameterToLengthRatio(self) -> float:
        """
           Ratio of the diameter of the elastic tube to the sum of the lengths of all segments. (Real > 0.0; Default = 0.1)
        """
        return self.__cardinfo.DiameterToLengthRatio

    @DiameterToLengthRatio.setter
    def DiameterToLengthRatio(self, value: float) -> None:
        self.__cardinfo.DiameterToLengthRatio = value
        self.last_status_message()

    def get_all_grid_points(self) -> list[int]:
        """
           Returns a list of all grid points identification number.
        """
        return self.__cardinfo.GetAllGridPoints()

    def set_grid_point_id(self, index: int, value: int) -> None:
        """
           Sets the grid point identification number at the specified index.
        """
        self.__cardinfo.SetGridPointId(index, value)
        self.last_status_message()

    def get_all_component_constrainsts(self) -> list[int]:
        """
              Returns a list of all component constraints.
        """
        return self.__cardinfo.GetAllComponentConstraints()

    def set_grid_point_constraint(self, index: int, value: int) -> None:
        """
              Sets the component constraint at the specified index.
        """
        self.__cardinfo.UpdateGridPointConstraint(index, value)
        self.last_status_message()


class SPCNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def SID(self) -> int:
        """
           Identification number of the single-point constraint set
        """
        return self.__cardinfo.SID

    @SID.setter
    def SID(self, value: int) -> None:
        self.__cardinfo.SID = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           Grid point identification number of connection points. (Integer > 0)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def C1(self) -> int:
        """
           C1
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: int) -> None:
        self.__cardinfo.C1 = value
        self.last_status_message()


    @property
    def D1(self) -> float:
        """
           D1: enforced motion for components C1 at G1
        """
        return self.__cardinfo.D1

    @D1.setter
    def D1(self, value: float) -> None:
        self.__cardinfo.D1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           Grid point identification number of connection points. (Integer > 0)
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()

    @property
    def C2(self) -> int:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: int) -> None:
        self.__cardinfo.C2 = value
        self.last_status_message()


    @property
    def D2(self) -> float:
        """
           D2: enforced motion for components C2 at G2
        """
        return self.__cardinfo.D2

    @D2.setter
    def D2(self, value: float) -> None:
        self.__cardinfo.D2 = value
        self.last_status_message()


class SPCDNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def SID(self) -> int:
        """
           Identification number of the single-point constraint set
        """
        return self.__cardinfo.SID

    @SID.setter
    def SID(self, value: int) -> None:
        self.__cardinfo.SID = value
        self.last_status_message()

    @property
    def G1(self) -> int:
        """
           Grid point identification number of connection points. (Integer > 0)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value
        self.last_status_message()

    @property
    def C1(self) -> int:
        """
           C1
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: int) -> None:
        self.__cardinfo.C1 = value
        self.last_status_message()


    @property
    def D1(self) -> float:
        """
           D1: enforced motion for components C1 at G1
        """
        return self.__cardinfo.D1

    @D1.setter
    def D1(self, value: float) -> None:
        self.__cardinfo.D1 = value
        self.last_status_message()

    @property
    def G2(self) -> int:
        """
           Grid point identification number of connection points. (Integer > 0)
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value
        self.last_status_message()

    @property
    def C2(self) -> int:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: int) -> None:
        self.__cardinfo.C2 = value
        self.last_status_message()


    @property
    def D2(self) -> float:
        """
           D2: enforced motion for components C2 at G2
        """
        return self.__cardinfo.D2

    @D2.setter
    def D2(self, value: float) -> None:
        self.__cardinfo.D2 = value
        self.last_status_message()


class SPC1(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def SID(self) -> int:
        """
           Identification number of the single-point constraint set. (Integer > 0)
        """
        return self.__cardinfo.SID

    @SID.setter
    def SID(self, value: int) -> None:
        self.__cardinfo.SID = value
        self.last_status_message()

    @property
    def C(self) -> int:
        """
            Component numbers. (Any unique combination of the Integers 1 
            through 6 with no embedded blanks for grid points. This number must be Integer 0, 1 
            or blank for scalar points.)
        """
        return self.__cardinfo.C

    @C.setter
    def C(self, value: int) -> None:
        self.__cardinfo.C = value
        self.last_status_message()

    def get_all_grid_points(self) -> list[int]:
        """
           Returns a list of all grid point identification numbers.
        """
        return self.__cardinfo.GetAllGridPoints()

    def set_grid_point(self, index: int, value: int) -> None:
        """Sets the grid point at the specified index (1-based)."""
        self.__cardinfo.SetGridPointAT(index, value)
        self.last_status_message()

class SPCADD(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo
    
    @property
    def SID(self) -> int:
        """
           Identification number of the single-point constraint set. (Integer > 0)
        """
        return self.__cardinfo.SID

    @SID.setter
    def SID(self, value: int) -> None:
        self.__cardinfo.SID = value
        self.last_status_message()

    def get_all_component_set_ids(self) -> list[int]:
        """
        Identification numbers of single-point constraint sets defined via SPC or by SPC1 
        entries. (Integer > 0)
        """
        return self.__cardinfo.GetAllComponentSetIDs()
    
    def set_component_set_id(self, index: int, value: int) -> None:
        """Sets the component set ID at the specified index (1-based)."""
        self.__cardinfo.SetComponentSetIDAt(index, value)
        self.last_status_message()


# Diccionario con todas clases.
CONSTRUCTDICT = {
    "CBAR": CBAR,
    "CBEAM": CBEAM,
    "CBUSH": CBUSH,
    "CELAS1": CELAS1,
    "CELAS2": CELAS2,
    "CELAS3": CELAS3,
    "CELAS4": CELAS4,
    "CFAST": CFAST,
    "CGAP": CGAP,
    "CHEXA_NASTRAN": CHEXANAS,
    "CHEXA_OPTISTRUCT": CHEXAOPT,
    "CONM2": CONM2,
    "CORD1C": CORD1C,
    "CORD1R": CORD1R,
    "CORD1S": CORD1S,
    "CORD2C": CORD2C,
    "CORD2R": CORD2R,
    "CORD2S": CORD2S,
    "CPENTA_NASTRAN": CPENTANAS,
    "CPENTA_OPTISTRUCT": CPENTAOPT,
    "CPYRA": CPYRA,
    "CQUAD4": CQUAD4,
    "CQUAD8": CQUAD8,
    "CROD": CROD,
    "CSHEAR": CSHEAR,
    "CTETRA_NASTRAN": CTETRANAS,
    "CTETRA_OPTISTRUCT": CTETRAOPT,
    "CTRIA3": CTRIA3,
    "CTRIA6": CTRIA6,
    "CWELD": CWELD,
    "FORCE_NASTRAN": FORCENAS,
    "GRID": GRID,
    "LOAD": LOAD,
    "MAT10_NASTRAN": MAT10NAS,
    "MAT10_OPTISTRUCT": MAT10OPT,
    "MAT1_NASTRAN": MAT1NAS,
    "MAT1_OPTISTRUCT": MAT1OPT,
    "MAT2_NASTRAN": MAT2NAS,
    "MAT2_OPTISTRUCT": MAT2OPT,
    "MAT3": MAT3,
    "MAT4": MAT4,
    "MAT5": MAT5,
    "MAT8": MAT8,
    "MAT9_NASTRAN": MAT9NAS,
    "MAT9_OPTISTRUCT": MAT9OPT,
    "MOMENT_NASTRAN": MOMENTNAS,
    "MPC": MPC,
    "MPCADD": MPCADD,
    "PBAR": PBAR,
    "PBARL": PBARL,
    "PBEAM_NASTRAN": PBEAMNAS,
    "PBEAML": PBEAML,
    "PBUSH_NASTRAN": PBUSHNAS,
    "PBUSH_OPTISTRUCT": PBUSHOPT,
    "PCOMP_NASTRAN": PCOMPNAS,
    "PCOMP_OPTISTRUCT": PCOMPOPT,
    "PELAS": PELAS,
    "PFAST": PFAST,
    "PGAP_NASTRAN": PGAPNAS,
    "PLOAD4_NASTRAN": PLOAD4NAS,
    "PLOTEL": PLOTEL,
    "PLPLANE": PLPLANE,
    "PMASS": PMASS,
    "PROD": PROD,
    "PSHEAR": PSHEAR,
    "PSHELL_NASTRAN": PSHELLNAS,
    "PSHELL_OPTISTRUCT": PSHELLOPT,
    "PSOLID_NASTRAN": PSOLIDNAS,
    "PSOLID_OPTISTRUCT": PSOLIDOPT,
    "PWELD": PWELD,
    "RBAR": RBAR,
    "RBAR1": RBAR1,
    "RBE1": RBE1,
    "RBE2": RBE2,
    "RBE3": RBE3,
    "RSPLINE": RSPLINE,
    "SPC_NASTRAN": SPCNAS,
    "SPCD_NASTRAN": SPCDNAS,
    "SPC1": SPC1,
    "SPCADD": SPCADD,
    "UNSUPPORTED": N2PCard
}