from NaxToPy.Core.Errors.N2PLog import N2PLog
import numpy as np
#
class N2PCoefficientsFinder:
    """
    Class that manages the linear dependencies between different rows of a square matrix (n·n dimensions) or
    of a rectangular matrix (n·m dimensions)
    
    Attributes:
        RelTol: numerical tolerance used for searching exact dependencies (float) (Default = 1e-03)
        SecondFilterMode: 'ACTIVATED' OR 'AUTO' (str) (Default: 'AUTO')
        ErrorThreshold: accepted error [%] that is used to asses DependenciesMatrix (Default = 0.01)
        Matrix: matrix to be analysed in terms of dependencies (np.array)
    """
    __slots__=("_reltol",
               "_second_filter_mode",
               "_matrix",
               "_error_threshold",
               "_dimensions",
               "_dependent_rows",
               "_independent_rows",
               "_rank",
               "_dependencies_matrix",
               "_number_corrected_rows",
               "_data_clean",
               "_tol",
               "_dependencies",             
               "_order",
               "_all_rows",
               "_coefficients_matrix",
               "_growth_factor",
               "_second_filter",
               "_errors")
    
    # N2PCoefficientsFinder constructor -----------------------------------------------------------------------
    def __init__(self):
        """
        The constructor creates an empty N2PCoefficientsFinder instance. Its atributes must be added as properties
        
        Calling example: 
            >>> from NaxToPy.Modules.numericaltools.N2PCoefficientsFinder import N2PCoefficientsFinder
            >>> finder = N2PCoefficientsFinder()
            >>> finder.RelTol = 1.5e-3 # (Optional Input) -> Default = 1.0e-03
            >>> finder.SecondFilterMode = 'AUTO' # (Optional Input) -> Default = 'AUTO'
            >>> finder.ErrorThreshold = 0.05 # (Optional Input) -> Default = 0.01 [which means 1 % of allowable error]
            >>> finder.Matrix = matrix # (Compulsory input)
            >>> finder.calculate()
        """
        # INPUTS <-> SETTERS #
        self._reltol: float = 1e-3
        self._second_filter_mode: str = 'AUTO'
        self._matrix: np.array = None
        self._error_threshold: float = 0.01
        # GETTERS #
        self._dimensions: tuple = None
        self._dependent_rows: list = []
        self._independent_rows: list = []
        self._rank: int = None
        self._dependencies_matrix: np.array = None
        self._number_corrected_rows: int = None
        # CLASS PARAMETERS #
        self._data_clean: np.array = None
        self._tol: float = None
        self._dependencies: dict = {}
        self._order: list = []
        self._all_rows: list = []
        self._coefficients_matrix: np.array = None
        self._growth_factor: list = []
        self._second_filter: bool = False
        self._errors: dict = {}
        #
        N2PLog.set_console_level("CRITICAL")
    #-------------------------------------------------------------------------------------------------------------------

    # Getters ----------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    @property
    def RelTol(self) -> float:
        """
        Property that returns the numerical relative tolerance used for searching dependencies (Default: 1.0e-03).
        """
        return self._reltol
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def SecondFilterMode(self) -> str:
        """
        Property that returns the second filter performance mode (AUTO/ACTIVATED) (Default: AUTO).
        """
        return self._second_filter_mode
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def Matrix(self) -> np.array:
        """
        Matrix being analysed. It is a compulsory input and an error will occur if this is not present.
        """
        return self._matrix
    #-------------------------------------------------------------------------------------------------------------------
    
    @property
    def ErrorThreshold(self) -> float:
        """
        Error threshold to be accepted when performing the final Auto-Check of DependenciesMatrix [Default: 0.01].
        """
        return self._error_threshold
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def Dimensions(self) -> tuple:
        """
        Property that returns the matrix dimensions (number rows, number dofs).
        """
        return self._dimensions
    #-------------------------------------------------------------------------------------------------------------------
    
    @property
    def DependentRows(self) -> list:
        """
        Property that returns a list containing the dependent rows.
        """
        return self._dependent_rows
    #-------------------------------------------------------------------------------------------------------------------
    
    @property
    def IndependentRows(self) -> list:
        """
        Property that returns a list containing the independent rows.
        """
        return self._independent_rows
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def Rank(self) -> int:
        """
        Property that returns the detected rank of the matrix.
        """
        return self._rank
    #-------------------------------------------------------------------------------------------------------------------
    
    @property
    def DependenciesMatrix(self) -> np.array:
        """
        Property that returns the matrix of dependencies.
        """
        return self._dependencies_matrix
    #-------------------------------------------------------------------------------------------------------------------
    
    @property
    def NumberCorrectedRows(self) -> int:
        """
        Property that returns the number of corrected rows inside DependenciesMatrix.
        """
        return self._number_corrected_rows
    # Setters ----------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    
    @RelTol.setter
    def RelTol(self, value: float) -> None:
        
        # "value" must be a positive float between [1.0e-10, 1.0e-03] to be accepted
        if isinstance(value, float):
            if 1.0e-10 <= value <= 1.0e-03:
                self._reltol = value
            else:
                # Error is raised if input value exceeds the limits
                N2PLog.Error.E707('RelTol', 'must be between [1.0e-10, 1.0e-03]')
        else:
            # Error is raised if the input value is not a float data
            N2PLog.Error.E706('RelTol','a float')
    #-------------------------------------------------------------------------------------------------------------------
    
    @SecondFilterMode.setter
    def SecondFilterMode(self, value: str) -> None:
        
        # "value" must be a string ("ACTIVATED" or "AUTO") to be accepted
        if type(value) == str:
            if value == "ACTIVATED" or value == "AUTO":
                self._second_filter_mode = value

                if value == 'ACTIVATED':
                    self._second_filter = True
                elif value == 'AUTO':
                    self._second_filter = False
            else:
                # Error is raised if input value is not appropriate
                N2PLog.Error.E707('SecondFilterMode', "must be 'ACTIVATED' OR 'AUTO'")
        else:
            # Error is raised if the input value is not a string data
            N2PLog.Error.E706('SecondFilterMode','a string')
    #-------------------------------------------------------------------------------------------------------------------
    
    @Matrix.setter
    def Matrix(self, value: np.array) -> None:
        
        # "value" must be a Numpy array
        if isinstance(value, np.ndarray):
            self._matrix = value.copy()
            self._data_clean = value.copy()
        else:
            # The code stops if this condition is not satisfied
            msg = N2PLog.Critical.C706()
            raise Exception(msg)
    #-------------------------------------------------------------------------------------------------------------------
    
    @ErrorThreshold.setter
    def ErrorThreshold(self, value: float) -> None:
        # 'value must be a float
        if isinstance(value, float):
            if value >= 0.01:
                self._error_threshold = value
            else:
                N2PLog.Error.E707('ErrorThreshold', "must be greater or equal to 0.01 [1 %]")
        else:
            # Error is raised if the input value is not a string data
            N2PLog.Error.E706('ErrorThreshold','a float')
    #-------------------------------------------------------------------------------------------------------------------
    def _normalisation(self) -> None:
        """
        Performs both the matrix normalisation and numerical tolerance calculation.

        Args:
            N/A
        
        Return:
            N/A
        """ 
        abs_matrix = np.abs(self._matrix)
        matrix_min_value = np.min(abs_matrix)
        matrix_max_value = np.max(abs_matrix)
        
        # Dependencies Matrix is initiated
        self._dependencies_matrix = np.full((len(self._matrix),len(self._matrix)),0.0, dtype=np.float64)

        if matrix_min_value == 0:
            abs_matrix[abs_matrix == 0] = matrix_max_value
            matrix_min_value = np.min(abs_matrix)

        # Matrix normalisation & Tolerance Calculation
        self._matrix = self._matrix/matrix_max_value
        self._tol = (self._reltol*matrix_min_value)/matrix_max_value
        
        return
    #-------------------------------------------------------------------------------------------------------------------
    def _epsilons(self,iteration) -> None:
        """
        Performs operations between the matrix rows in order to compare values that might be neglectable in
        comparison with the reference row.

        Args:
            iteration: current iteration of the gaussian engine method
        
        Return:
            N/A
        """  
        # Local reference for fastest access:
        matrix = self._matrix
        start = iteration + 1
        
        # Pre-filter stage to delete numerical noise
        matrix[start:][np.abs(matrix[start:]) < self._tol] = 0.0
        
        # Early Exit #-1-#
        if matrix[start:,start:].size == 0 or not matrix[start:,start:].any():
            return
        
        # Definition of the reference row
        reference_row = matrix[iteration,start:]
        non_zero_mask = np.abs(reference_row) > 0 
        
        # Early Exit #-2-#
        if not non_zero_mask.any():
            return
        
        # Modification of the reference row
        ref_abs_min_value = reference_row[non_zero_mask].min()
        
        # Minimal memory allocation - only for safe reference row
        reference_row_safe = np.where(reference_row == 0.0, ref_abs_min_value, reference_row)

        # Epsilons calculation
        epsilons = np.abs(matrix[start:,start:] / reference_row_safe)
        
        # The matrix is corrected based on numerical comparison against absolute tolerance
        matrix[start:,start:][epsilons < self._tol] = 0.0
        
        self._matrix = matrix
        
        return
    #-------------------------------------------------------------------------------------------------------------------
    def _gauss_pivot_method_nxm(self) -> None:
        """
        Performs operations between the matrix rows in order to obtain zeros under the pivot row and
        stores these steps in order to know later the existant dependencies between rows.

        Args:
            N/A
        
        Return:
            N/A
        """
        # Investigation factor
        max_initial_value = np.max(self._matrix)
        
        # Dimensions of the matrix (n,m)
        self._dimensions = self._matrix.shape
        
        # Second filter is activated if the number of rows is greater than the number of columns
        if self._dimensions[0] > self._dimensions[1]:
            self._second_filter = True
        
        # Temporal dependencies
        self._coefficients_matrix = np.identity(self._dimensions[0], dtype=np.float64)

        # Maximum theoretical number of iterations 
        iterations = min((self._dimensions[0] - 1),(self._dimensions[1] - 1))

        # Dependencies dictionary and rows order are initiated
        for i in range(self._dimensions[0]):
            self._dependencies ["R" +str(i+1)] = []
            self._order.append("R" +str(i+1))

        # PIVOT ITERATIONS
        #
        for i in range(iterations):
            # ((i: current iteration of the gauss process))
            #
            # That row with the maximum value inside the pivot column is chosen as the pivot row (numerical stability purposes)
            # Position of maximum value = Position of maximum local value + Pivot Position
            max_pos = np.argmax(np.abs(self._matrix[i:,i])) + i
            pivot_name = self._order[max_pos]
            
            # FIRST ITERATION -> INITIAL PIVOT DEFINITION:
            if i == 0:
                self._dependencies[pivot_name].append("PIVOT")

                # [ If |max_value_first_pivot| <= Tolerance ] ---> ***(Skip iteration)***
                ##..............................................................................#
                if np.max(np.abs(self._matrix[max_pos,0])) <= self._tol:             #
                    # It is registered that the first row becomes PIVOT and the rows under it   #
                    #remain constant                                                            #
                    ## for w in range(dimension):   
                    for w in range(self._dimensions[0]):
                        row_name = self._order[w]                                               #
                        if row_name == pivot_name:                                              #
                            self._dependencies[row_name].append("PIVOT")                        #
                    continue                                                                    #
                ##..............................................................................#

            # Early Exit [Break Type]:
            # --------------------------------------------------------------------------- #
            # If the maximum value of the internal region [i:,i:] == 0.0 the method loop must
            # stop as there is no room for further actions
            maximum_value_iter_i = np.max(np.abs(self._matrix[i:,i:]))
            if maximum_value_iter_i == 0.0:
                break
            # --------------------------------------------------------------------------- #
            # [ If all the values UNDER the pivot <= tolerance ] ---> ***(Skip iteration)***
            ##...............................................................................
            if np.max(np.abs(self._matrix[i:,i])) <= self._tol:
                self._second_filter = True
                continue
            ##...............................................................................
            #
            ##...............................................................................
            # Matrix & Coefficients rows are switched and row order change is registered
            self._matrix[[i,max_pos]] = self._matrix[[max_pos,i]]
            self._coefficients_matrix[[i,max_pos]] = self._coefficients_matrix[[max_pos,i]]
            self._order[i], self._order [max_pos] = self._order[max_pos], self._order[i]
            
            # <<-- GAUSS CORE -->>
            # --------------------------------------------------------------------------------------------------- #
            # --------------------------------------------------------------------------------------------------- #
            # Pivot value
            pivot_coeff = self._matrix[i,i]
            
            # Rows affected -> Those affected non-zero coefficients under pivot value
            affected_column = self._matrix[i+1:,i].copy()
            affected_rows = affected_column != 0
            
            # Internal region of the matrix to be modified
            internal_matrix = self._matrix[(i+1):,i:][affected_rows]
            
            # Vectorial Operations & Matrix Modification
            multipliers = (affected_column[affected_rows] / pivot_coeff).reshape(-1,1)
            self._matrix[(i+1):,i:][affected_rows] = internal_matrix-multipliers*self._matrix[i][i:]
            self._matrix[i+1:,i] = 0.0
  
            # Epsilons Calculation
            self._epsilons(i)
                
            # Vectorial Operations & Coefficients Matrix Modification
            coefficients_affected = self._coefficients_matrix[(i+1):,:][affected_rows]
            self._coefficients_matrix[(i+1):,:][affected_rows] = coefficients_affected - multipliers*self._coefficients_matrix[i]
            
            growth_factor = np.max(np.abs(self._matrix[(i+1):,i:]))/max_initial_value
            self._growth_factor.append(growth_factor)
            # --------------------------------------------------------------------------------------------------- #
            # --------------------------------------------------------------------------------------------------- #

        # Zeros Finder
        # ----------------------------------------------------------- #
        zero_rows_mask = np.all(self._matrix == 0, axis=1)
        if not np.any(zero_rows_mask):
            return
        
        zero_indices = np.flatnonzero(zero_rows_mask).astype(np.int32)
        zero_rows = [self._order[i] for i in zero_indices]

        for row in zero_rows:
            self._dependencies[row].append("dependent")

        self._dependent_rows.extend(zero_rows)
        # ----------------------------------------------------------- #

        return
    #-------------------------------------------------------------------------------------------------------------------
    def _gauss_second_filter_nxm(self) -> None:
        """
        Performs operations in order to find dependencies that weren't found during "gauss_pivot_method" execution.

        Args:
            N/A

        Returns:
            N/A
        """
        # Only non-null rows are studied and first pivot row is ignored
        zero_rows_mask = np.all(self._matrix == 0, axis=1)
        indep_row_indices = np.where(~zero_rows_mask)[0][1:]
        
        # Early exit
        if len(indep_row_indices) < 2:
            return
        
        matrix_subset = self._matrix[indep_row_indices]
        n_rows = len(indep_row_indices)
        
        # Precompute all boolean masks
        zeros_bool = np.abs(matrix_subset) < self._tol
        
        # Use broadcasting to find all pairs with matching zero patterns
        pattern_matches = np.all(zeros_bool[:, None, :] == zeros_bool[None, :, :], axis=2)
        
        # Get upper triangular indices
        upper_tri_mask = np.triu(np.ones((n_rows, n_rows), dtype=bool), k=1)
        z_indices, n_indices = np.where(pattern_matches & upper_tri_mask)
        
        rows_to_remove = set()
        
        # Process all matching pairs
        for z, n in zip(z_indices, n_indices):
            if z in rows_to_remove or n in rows_to_remove:
                continue
                
            z_index = indep_row_indices[z]
            n_index = indep_row_indices[n]
            
            row_data_a = matrix_subset[z]
            row_data_b = matrix_subset[n]
            
            nonzero_mask = (np.abs(row_data_a) > 0.0) & (np.abs(row_data_b) > 0.0)
            
            if not np.any(nonzero_mask):
                continue
            
            ratios = row_data_a[nonzero_mask] / row_data_b[nonzero_mask]
            
            # Check ratio consistency
            if len(ratios) > 1:
                if not np.allclose(ratios, ratios[0], rtol=self._reltol):
                    continue
            
            # Perform row operations
            multiplier = float(ratios[0])
            
            self._matrix[n_index] = multiplier * self._matrix[n_index] - self._matrix[z_index]
            self._coefficients_matrix[n_index] = (
                multiplier * self._coefficients_matrix[n_index] - self._coefficients_matrix[z_index]
            )
            
            # Update tracking
            row_b_name = self._order[n_index]
            self._dependencies[row_b_name].extend(["dependent"])
            self._dependent_rows.append(row_b_name)
            
            rows_to_remove.add(n)
        
        # Apply tolerance zeroing once at the end
        self._matrix[np.abs(self._matrix) < self._tol] = 0.0
        return
    #-------------------------------------------------------------------------------------------------------------------
    def _gauss_constructor_output_nxm (self) -> None:
        """
        Defines the Dependencies Matrix (Output of the class)

        Args:
            N/A
            
        Returns:
            N/A
        """
        # Efficient set-based lookup
        dependent_set = set(self._dependent_rows)

        # Coefficients-Matrix is reorganised
        internal_map = dict(zip(self._order, range(len(self._order))))
        reorder_indices = np.array([internal_map[key] for key in self._all_rows], dtype=np.int32)
        coefficients_reordered = self._coefficients_matrix[reorder_indices]

        # Boolean indexing for handling rows:
        is_dependent = np.array([row in dependent_set for row in self._all_rows], dtype=bool)
        independent_index = np.where(~is_dependent)[0].astype(np.int32)
        dependent_index = np.where(is_dependent)[0].astype(np.int32)

        # Set diagonal to 1.0 for independent rows in one operation
        self._dependencies_matrix[independent_index, independent_index] = 1.0

        # Multipliers Extraction from dependent Rows
        diagonal_vals = coefficients_reordered[dependent_index, dependent_index]
        multipliers = -1.0 / diagonal_vals

        # Multipliers positions are set to 0
        coefficients_reordered[dependent_index,dependent_index] = 0.0

        # Values under tolerance becomes 0
        coefficients_reordered[abs(coefficients_reordered) < self._tol] = 0.0

        # Only dependent rows are going to be multiplied
        affected_data = coefficients_reordered[dependent_index]
        modified_data = multipliers[:, np.newaxis] * affected_data

        # Information assignment
        self._dependencies_matrix[dependent_index] = modified_data
        
        return 
    #-------------------------------------------------------------------------------------------------------------------
    def _parse_row_indices(self, row_names: list[str]) -> np.ndarray:
        """
        Parse row names to indices
        
        Args:
            row_names: list of str (Example: ['R1','R2'])
        Returns:
            indices: list of int (Example: ['R1','R2'] -> [0,1])
        """
        indices = np.empty(len(row_names), dtype=np.int32)
        for i, row_name in enumerate(row_names):
            # Extract number from "R1", "R2", etc.
            indices[i] = int(row_name[1:]) - 1
        return indices
    #-------------------------------------------------------------------------------------------------------------------
    def _reconstructor(self, ind_rows, dep_rows) -> np.array:
        """
        Re-construct the input matrix using both the independent LCs + Dependencies Coefficients

        Args:
            ind_rows: independent rows
            dep_rows: dependent rows
            
        Returns:
            reconstructed_matrix: matrix obtained using the result from the iterative process.
        """
        # Reconstructed matrix is initiated
        n_rows, n_cols = self._dimensions[0], self._dimensions[1]
        reconstructed_matrix = np.zeros((n_rows, n_cols), dtype=np.float64)
        
        # Process independent rows (it copies them directly)
        for idx in ind_rows:
            reconstructed_matrix[idx] = self._data_clean[idx]
        
        # Process dependent rows (it uses DependenciesMatric coefficients)
        for idx in dep_rows:
            coefs = self._dependencies_matrix[idx]
            for j in range(n_rows):
                # This skips zero coefficients
                if coefs[j] != 0.0:
                    reconstructed_matrix[idx] += coefs[j]*self._data_clean[j]
                    
        return reconstructed_matrix
    #-------------------------------------------------------------------------------------------------------------------
    def _relative_errors(self, dep_rows_indx, reconstructed_matrix) -> np.array:
        """
        Re-construct the input matrix using both the independent LCs + Dependencies Coefficients

        Args:
            dep_rows_indx: indixes of dependent rows
            reconstructed_matrix: indixes of independent rows
            
        Returns:
            rel_errors_rows: list containing the relative error [%] of each row of DependenciesMatrix
        """
        
        rel_errors_rows = np.full(len(self._matrix), 0.0)
        
        # ALPHA CHECK:
        for m in dep_rows_indx:
            original_row = self._data_clean[m]

            # Only non-zero values can be compared
            comparison_indexes = np.array(original_row != 0.0)
            
            original_row_nonzero = original_row[comparison_indexes]
            reconstructed_row_nonzero = reconstructed_matrix[m][comparison_indexes]
            
            rel_errors_rows[m] = np.max(100*np.abs((reconstructed_row_nonzero-original_row_nonzero)/abs(original_row_nonzero)))
            
        return rel_errors_rows
    
    def _performance_checker(self) -> None:
        """
        Performance an internal check before delivering the DependenciesMatrix to the user

        Args:
            N/A
            
        Returns:
            N/A
        """
        # Pre-parse all row indices once (avoid repeated string operations)
        independent_rows_indices = self._parse_row_indices(self._independent_rows)
        dependent_rows_indices = self._parse_row_indices(self._dependent_rows)
        
        # Reconstructed matrix is created
        reconstructed_matrix = self._reconstructor(independent_rows_indices,dependent_rows_indices)
        
        # Relative Errors are calculated to determine the applicability of DependenciesMatrix
        self._errors['Before ErrorThreshold'] = self._relative_errors(dependent_rows_indices,reconstructed_matrix)
        
        # If ErrorThreshold is violated, some changes must be applied
        if np.any(self._errors['Before ErrorThreshold'] > (self._error_threshold*100)):
            failed_rows = np.where(self._errors['Before ErrorThreshold'] > (self._error_threshold*100))[0]
            
            # Total number of rows to be corrected
            self._number_corrected_rows = len(failed_rows)
            
            # DependenciesMatrix must be modified
            self._dependencies_matrix [failed_rows] = np.full(len(self._matrix), 0.0)
            self._dependencies_matrix [failed_rows,failed_rows] = 1.0
            
            # Failed rows must be added to independent rows and deleted from dependent rows group:
            for m in failed_rows:
                self._independent_rows.append('R'+str(m+1))
                
                dep_id = self._dependent_rows.index('R'+str(m+1))
                del self._dependent_rows[dep_id]
                
            independent_rows_indices_stage_2 = self._parse_row_indices(self._independent_rows)
            dependent_rows_indices_stage_2 = self._parse_row_indices(self._dependent_rows)
            
            reconstructed_matrix_stage_2 = self._reconstructor(independent_rows_indices_stage_2,dependent_rows_indices_stage_2)
            
            self._errors['After ErrorThreshold'] = self._relative_errors(dependent_rows_indices_stage_2,reconstructed_matrix_stage_2)
            
        else:
            self._errors['After ErrorThreshold'] = self._errors['Before ErrorThreshold']
        
        return
    #-------------------------------------------------------------------------------------------------------------------
    def _output_reorder(self) -> None:
        """
        Reorder self._dependentrows & self._independent_rows
    
        Args:
            N/A
            
        Returns:
            N/A
        """
        new_dependent_list = []
        new_independent_list = []
        
        n_rows = self._dimensions[0]
        
        for i in range(n_rows):
            coef = self._dependencies_matrix[i,i]
            row_name = 'R'+str(i+1)
            # if coefficient = 1, it is an independent row
            if coef == 1.0:
                new_independent_list.append(row_name)
            else:
                new_dependent_list.append(row_name)
                
        self._dependent_rows = new_dependent_list
        self._independent_rows = new_independent_list
        return
    #-------------------------------------------------------------------------------------------------------------------
    def calculate(self) -> None:
        """
        Determines (if applicable) the linear dependencies of a singular matrix
    
        Args:
            N/A
            
        Returns:
            N/A
        """
        # Calculation is aborted if Matrix has not been defined
        if np.all(self._matrix == None):
            msg = N2PLog.Critical.C707()
            raise Exception(msg)
        
        # Calculation is aborted if Matrix has just one row (1 LC)
        # Dimensions of the matrix (n,m)
        self._dimensions = self._matrix.shape
        if len(self._dimensions) == 1:
            msg = N2PLog.Critical.C708()
            raise Exception(msg)
        
        # Calculation is aborted if Matrix is null
        if np.all(self._matrix == 0.0):
            msg = N2PLog.Critical.C709()
            raise Exception(msg)
        
        # Calculation is aborted if Matrix has any Nan value
        if np.any(np.isnan(self._matrix)):
            msg = N2PLog.Critical.C710()
            raise Exception(msg)
        
        # All rows list construction
        self._all_rows = [f"R{i+1}" for i in range(len(self._matrix))]
        
        # Matrix Normalisation
        self._normalisation()

        # Pivot method is called to create zeros as per gauss method
        self._gauss_pivot_method_nxm()

        # Second filter method is called to find direct rows dependencies (row_a) = c*(row_b)
        if self._second_filter:
            self._gauss_second_filter_nxm()
        
        # Independent rows are defined
        # --------------------------------------------------- #
        for j in self._all_rows:
            if j not in self._dependent_rows:
                self._independent_rows.append(j)
        # --------------------------------------------------- #

        if len(self._dependent_rows) > 0:

            # Dependencies matrix construction
            self._gauss_constructor_output_nxm()
            
            # Autocheck -> DependenciesMatrix has to be checked before being delivered
            self._performance_checker()
            
            # Dependent & Independent Rows are re-ordered
            self._output_reorder()

        else:
            # Independentant rows list
            self._independent_rows = self._all_rows
            
        # Rank calculation
        self._rank = len(self._matrix) - len(self._dependent_rows)
        return
    #-------------------------------------------------------------------------------------------------------------------