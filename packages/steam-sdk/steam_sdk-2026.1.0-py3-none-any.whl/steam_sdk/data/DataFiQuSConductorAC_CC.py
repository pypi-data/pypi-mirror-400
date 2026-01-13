
"""DataFiQuSConductorAC_CC.py"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, List




class CACCCGeometry(BaseModel):
    """
    Level 2: Geometry for CACCC.
    """
    air_radius: Optional[float] = Field(
        default=None, 
        description = "Radius of air region."
    )


class CACCCGeneralparameters(BaseModel):
    """
    Level 3: Class for general parameters
    """
    temperature: float = Field(
        default=1.9, 
        description = "Temperature (K)."
    )
    noOfMPITasks: Optional[Union[bool, int]] = Field(
        default=False, title = "No. of tasks for MPI parallel run of GetDP",
        description = "If integer, GetDP will be run in parallel using MPI. This is only valid"
                      " if MPI is installed on the system and an MPI-enabled GetDP is used." 
                      " If False, GetDP will be run in serial without invoking mpiexec."
    )



class CACCCSolveInitialconditions(BaseModel):
    """
    Level 3: Class for initial conditions
    """
    init_type: Optional[Literal['virgin', 'pos_file', 'uniform_field']] = Field(
        default='virgin', 
        description = "Type of initialization for the simulation. (i) 'virgin' is the default type, the initial magnetic field is zero,"
                      "(ii) 'pos_file' is to initialize from the solution of another solution, given by the solution_to_init_from entry,"
        " and (iii) 'uniform_field' is to initialize at a uniform field, which will be the applied field at the initial time of the simulation."
        " Note that the uniform_field option does not allow any non-zero transport current (initialization from pos_file is needed for this)."
    )
    solution_to_init_from: Optional[Union[int, str]] = Field(
        default=None,
        description = "Name xxx of the solution from which the simulation should be initialized. " 
                      "The file last_magnetic_field.pos of folder Solution_xxx will be used for the initial solution."
                      "It must be in the Geometry_.../Mesh_.../ folder in which the Solution_xxx will be saved.",
    )



class CACCCSolveSourceparametersSine(BaseModel):
    """
    Level 4: Class for Sine source parameters
    """
    frequency: Optional[float] = Field(
        default=None, 
        description = "Frequency of the sine source (Hz)."
    )
    field_amplitude: Optional[float] = Field(
        default=None, 
        description = "Amplitude of the sine field (T)."
    )
    current_amplitude: Optional[float] = Field(
        default=None, 
        description = "Amplitude of the sine current (A)."
    )



class CACCCSolveSourceparametersPiecewise(BaseModel):
    """
    Level 4: Class for piecewise (linear) source parameters
    """
    source_csv_file: Optional[str] = Field(
        default=None, 
        description = "File name for the from_file source type defining the time evolution of current and field (in-phase)."
                      "Multipliers are used for each of them." 
                      "The file should contain two columns: 'time' (s) and 'value' (field/current (T/A)), with these headers."
                      "If this field is set, times, applied_fields_relative and transport_currents_relative are ignored."
    )
    times: Optional[List[float]] = Field(
        default=None, 
        description = "Time instants (s) defining the piecewise linear sources." 
                      "Used only if source_csv_file is not set." 
                      "Can be scaled by time_multiplier."
    )
    applied_fields_relative: Optional[List[float]] = Field(
        default=None, 
        description = "Applied fields relative to multiplier applied_field_multiplier at the time instants 'times'."
                      "Used only if source_csv_file is not set."
    )
    transport_currents_relative: Optional[List[float]] = Field(
        default=None, 
        description = "Transport currents relative to multiplier transport_current_multiplier at the time instants 'times'." 
                      "Used only if source_csv_file is not set."
    )
    time_multiplier: Optional[float] = Field(
        default=None, 
        description = "Multiplier for the time values in times (scales the time values)." 
                      "Also used for the time values in the source_csv_file."
    )
    applied_field_multiplier: Optional[float] = Field(
        default=None, 
        description = "Multiplier for the applied fields in applied_fields_relative."
                      "Also used for the values in the source_csv_file."
    )
    transport_current_multiplier: Optional[float] = Field(
        default=None, 
        description = "Multiplier for the transport currents in transport_currents_relative."
                      "Also used for the values in the source_csv_file."
    )



class CACCCSolveSourceparameters(BaseModel):
    """
    Level 3: Class for material properties
    """
    source_type: Literal['sine', 'piecewise'] = Field(
        default='sine',
        description = "Time evolution of applied current and magnetic field. " 
                      "Supported options are: sine, piecewise."
    )
    sine: CACCCSolveSourceparametersSine = CACCCSolveSourceparametersSine()
    piecewise: CACCCSolveSourceparametersPiecewise = CACCCSolveSourceparametersPiecewise()
    field_angle_with_respect_to_normal_direction: Optional[float] = Field(
        default=None, 
        description = "Angle of the source magnetic field with respect to the y-axis (normal to the tape) (degrees)."
    )



class CACCCSolveNumericalparametersSine(BaseModel):
    """ 
    Level 4: Numerical parameters corresponding to the sine source
    """
    timesteps_per_period: Optional[float] = Field(
        default=None, 
        description = "Initial value for number of time steps (-) per period for the sine source." 
                      "Determines the initial time step size."
    )
    number_of_periods_to_simulate: Optional[float] = Field(
        default=None, 
        description = "Number of periods (-) to simulate for the sine source."
    )



class CACCCSolveNumericalparametersPiecewise(BaseModel):
    """
    Level 4: Numerical parameters corresponding to the piecewise source
    """
    time_to_simulate: Optional[float] = Field(
        default=None, 
        description = "Total time to simulate (s). Used for the piecewise source."
    )
    timesteps_per_time_to_simulate: Optional[float] = Field(
        default=None, 
        description = "If variable_max_timestep is False. Number of time steps (-) per period for the piecewise source."
    )
    force_stepping_at_times_piecewise_linear: bool = Field(
        default=False, 
        description = "If True, time-stepping will contain exactly the time instants that are in" 
                      "the times_source_piecewise_linear list (to avoid truncation maximum applied field/current values)."
    )
    variable_max_timestep: bool = Field(
        default=False, 
        description = "If False, the maximum time step is kept constant through the simulation. " 
                      "If True, it varies according to the piecewise definition."
    )
    times_max_timestep_piecewise_linear: Optional[List[float]] = Field(
        default=None, 
        description = "Time instants (s) defining the piecewise linear maximum time step."
    )
    max_timestep_piecewise_linear: Optional[List[float]] = Field(
        default=None, 
        description = "Maximum time steps (s) at the times_max_timestep_piecewise_linear. " 
                      "Above the limits, linear extrapolation of the last two values."
    )



class CACCCSolveNumericalparameters(BaseModel):
    """
    Level 3: Class for numerical parameters
    """
    relative_tolerance: Optional[float] = Field(default=1e-6, description="Tolerance on the relative change of the power indicator for the convergence criterion (1e-6 is usually a safe choice).")
    voltage_per_meter_stopping_criterion: Optional[float] = Field(default=None, description="If a non-zero value is given, the simulation will stop if the transport voltage per meter reaches this value (in absolute value).")
    relaxation_factors: Optional[bool] = Field(default=True, description="Use of relaxation factors to help convergence (automatic selection based on the lowest residual).")
    sine: CACCCSolveNumericalparametersSine = CACCCSolveNumericalparametersSine()
    piecewise: CACCCSolveNumericalparametersPiecewise = CACCCSolveNumericalparametersPiecewise()



class CACCCSolve(BaseModel):
    """
    Level 2: Solve block for CACCC
    """
    pro_template: Optional[str] = Field(
        default='CAC_CC_template.pro', 
        description = "Name of the .pro template file."
    )
    conductor_name: Optional[str] = Field(
        default=None, 
        description = "Name of the conductor. Must match a conductor name in "
                      "the conductors section of the input YAML-file."
    )
    general_parameters: CACCCGeneralparameters = (
        CACCCGeneralparameters()
    )
    initial_conditions: CACCCSolveInitialconditions = (
        CACCCSolveInitialconditions()
    )
    source_parameters: CACCCSolveSourceparameters = (
        CACCCSolveSourceparameters()
    )
    numerical_parameters: CACCCSolveNumericalparameters = (
        CACCCSolveNumericalparameters()
    )



class CACCCMesh(BaseModel):
    """
    Level 2: Mesh parameters for CACCC.
    """
    HTS_n_elem_width: Optional[int] = Field(
        default=None,
        description = "Number of elements along HTS width (x-direction)."
    )
    HTS_n_elem_thickness: Optional[int] = Field(
        default=None,
        description = "Number of elements through HTS thickness (y-direction)."
    )
    substrate_elem_scale: Optional[float] = Field(
        default=None,
        description = "Element-count scale factor for substrate layer."
    )
    substrate_side_progression: Optional[float] = Field(
        default=None,
        description = "Progression factor for substrate vertical sides near the HTS side."
    )
    silver_elem_scale: Optional[float] = Field(
        default=None,
        description = "Element-count scale factor for silver layers."
    )
    copper_elem_scale: Optional[float] = Field(
        default=None,
        description = "Element-count scale factor for copper layers."
    )
    air_boundary_mesh_size_ratio: Optional[float] = Field(
        default=None,
        description = "Ratio of air outer-boundary mesh size to the HTS base size."
    )
    scaling_global: Optional[float] = Field(
        default=None,
        description = "Global refinement factor."
    )
    bump_coef: Optional[float] = Field(
        default=None,
        description = "Unified bump coefficient for transfinite horizontal edges. "
                      "Used for both HTS and SilverTop when applying 'Bump' distributions. "
                      "Values < 1 cluster nodes toward the edges; values > 1 cluster toward the center."
    )




class CACCCPostprocPosFiles(BaseModel):
    """
    Level 3: Class for post-pro .pos file requests
    """
    quantities: Optional[List[str]] = Field(
        default=None, description = "List of GetDP postprocessing quantities to write to .pos file. "
                                    "Examples of valid entry is: phi, h, b, j, jz, power"
    )
    regions: Optional[List[str]] = Field(
        default=None, 
        description = "List of GetDP regions to write to .pos file postprocessing for. " 
                      "Examples of a valid entry is: " 
                      "Matrix, Filaments, Omega (full domain), OmegaC (conducting domain), OmegaCC (non conducting domain)"
    )


class CWSStrandPostprocCleanup(BaseModel):
    """
    Level 3: Class for cleanup settings
    """
    remove_pre_file: bool = Field(
        default=False,
        description = "Set True to remove the .pre-file after post-processing, to save disk space."
    )
    remove_res_file: bool = Field(
        default=False,
        description = "Set True to remove the .res-file after post-processing, to save disk space."
    )
    remove_msh_file: bool = Field(
        default=False,
        description = "Set True to remove the .msh-file after post-processing, to save disk space."
    )



class CACCCPostproc(BaseModel):
    """
    Post-processing options for CACCC
    """
    pos_files: CACCCPostprocPosFiles = Field(
        default=CACCCPostprocPosFiles(),
        description = "Entries controlling output of .pos files." 
                      "If None or empty lists are given, no .pos files are written." 
                      "Note that not all combinations of quantities and regions make sense."
    )
    cleanup: CWSStrandPostprocCleanup = CWSStrandPostprocCleanup()


class CACCC(BaseModel):
    """
    Level 1: Class for FiQuS CACCC (Conductor AC Coated Conductor)
    """
    type: Literal["CACCC"]
    geometry: CACCCGeometry = CACCCGeometry()
    mesh: CACCCMesh = CACCCMesh()
    solve: CACCCSolve = CACCCSolve()
    postproc: CACCCPostproc = CACCCPostproc()

