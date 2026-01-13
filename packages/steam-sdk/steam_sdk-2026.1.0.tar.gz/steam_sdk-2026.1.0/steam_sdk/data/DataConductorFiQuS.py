from pydantic import BaseModel, Field
from typing import Union, Literal, Optional, List

# ------------------- Jc fits ---------------------------#
class ConstantJc(BaseModel):
    """
    Level 3: Class for setting constant Jc
    """

    type: Literal["Constant Jc"]
    Jc_constant: Optional[float] = None  # [A/m^2]


class Ic_A_NbTi(BaseModel):
    """
    Level 3: Class for setting IcNbTi fit
    """

    type: Literal["Ic_A_NbTi"]
    Jc_5T_4_2K: Optional[float] = None  # [A/m^2]


class Bottura(BaseModel):
    """
    Level 3: Class for setting Bottura fit
    """

    type: Literal["Bottura"]
    Tc0_Bottura: Optional[float] = None  # [K]
    Bc20_Bottura: Optional[float] = None  # [T]
    Jc_ref_Bottura: Optional[float] = None  # [A/m^2]
    C0_Bottura: Optional[float] = None  # [-]
    alpha_Bottura: Optional[float] = None  # [-]
    beta_Bottura: Optional[float] = None  # [-]
    gamma_Bottura: Optional[float] = None  # [-]


class CUDI1(BaseModel):
    """
    Level 3: Class for Nb-Ti fit based on "Fit 1" in CUDI manual
    """

    type: Literal["CUDI1"]
    Tc0_CUDI1: Optional[float] = None  # [K]
    Bc20_CUDI1: Optional[float] = None  # [T]
    C1_CUDI1: Optional[float] = None  # [A]
    C2_CUDI1: Optional[float] = None  # [A/T]


class CUDI3(BaseModel):
    """
    Level 3: Class for Nb-Ti fit based on "Fit 3" in CUDI manual
    """

    type: Literal["CUDI3"]
    Tc0_CUDI3: Optional[float] = None  # [K]
    Bc20_CUDI3: Optional[float] = None  # [T]
    c1_CUDI3: Optional[float] = None  # [-]
    c2_CUDI3: Optional[float] = None  # [-]
    c3_CUDI3: Optional[float] = None  # [-]
    c4_CUDI3: Optional[float] = None  # [-]
    c5_CUDI3: Optional[float] = None  # [-]
    c6_CUDI3: Optional[float] = None  # [-]


class Summers(BaseModel):
    """
    Level 3: Class for cable Summer's Nb3Sn fit
    """

    type: Literal["Summers"]
    Tc0_Summers: Optional[float] = None  # [K]
    Bc20_Summers: Optional[float] = None  # [T]
    Jc0_Summers: Optional[float] = None  # [A*T^0.5/m^2]


class Bordini(BaseModel):
    """
    Level 3: Class for cable Bordini's Nb3Sn fit
    """

    type: Literal["Bordini"]
    Tc0_Bordini: Optional[float] = None  # [K]
    Bc20_Bordini: Optional[float] = None  # [T]
    C0_Bordini: Optional[float] = None  # [A*T/m^2]
    alpha_Bordini: Optional[float] = None  # [-]


class Nb3Sn_HFM(BaseModel):
    """
    Level 3: Class for cable HFM Nb3Sn fit
    """

    type: Literal["Nb3Sn_HFM"]
    Tc0_Nb3Sn_HFM: Optional[float] = None  # [K]
    Bc20_Nb3Sn_HFM: Optional[float] = None  # [T]
    C0_Nb3Sn_HFM: Optional[float] = None  # [A*T/m^2]
    alpha_Nb3Sn_HFM: Optional[float] = None  # [-]
    nu_Nb3Sn_HFM: Optional[float] = None  # [-]
    p_Nb3Sn_HFM: Optional[float] = None  # [-]
    q_Nb3Sn_HFM: Optional[float] = None  # [-]


class ProDefined(BaseModel):
    """
    Level 3: Class for cable Bordini's Nb3Sn fit
    """

    type: Literal["ProDefined"]
    Tc0: Optional[float] = None  # [K]
    Bc20: Optional[float] = None  # [T]
    C0: Optional[float] = None  # [A*T/m^2]
    alpha: Optional[float] = None  # [-]
    p: Optional[float] = None  # [-]
    q: Optional[float] = None  # [-]
    v: Optional[float] = None  # [-]
    B0: Optional[float] = None  # [-]

class Succi_fixed(BaseModel):
    """
    Level 3: Class for cable Succi's YBCO fit
    """

    type: Literal["Succi_fixed"]
    Jc_factor: Optional[float] = Field(gt=0.0,
        default = 1.0,
        description = "This factor multiplies the Jc returned by the function."
    )
    # all other parameters of the Succi fit are hardcoded
class Fujikura(BaseModel):
    """
    Level 3: Class for cable Fujikura's fit
    """

    type: Literal["Fujikura"]
    Jc_factor: Optional[float] = Field(gt=0.0,
        default = 1.0,
        description = "This factor multiplies the Jc returned by the function."
    )

class Zero(BaseModel):
    """
    Level 3: Class for specifying that there is no Jc in the strand (i.e. copper wire used for ESC coil)
    """

    type: Literal["Zero"]


class BSCCO_2212_LBNL(BaseModel):
    """
    Level 3: Class for cable Bi-2212 fit developed in LBNL
    """

    # only ad-hoc fit [T. Shen, D. Davis, E. Ravaioli with LBNL, Berkeley, CA]
    type: Literal["BSCCO_2212_LBNL"]
    f_scaling_Jc_BSCCO2212: Optional[float] = None  # [-] used for the ad-hoc fit


# ------------------- Cable types ---------------------------#
class Mono(BaseModel):
    """
    Mono cable type: This is basically type of cable consisting of one strand - not really a cable
    """

    type: Literal["Mono"]
    bare_cable_width: Optional[float] = None
    bare_cable_height_low: Optional[float] = None
    bare_cable_height_high: Optional[float] = None
    bare_cable_height_mean: Optional[float] = None
    th_insulation_along_width: Optional[float] = None
    th_insulation_along_height: Optional[float] = None
    # Fractions given with respect to the insulated conductor
    f_superconductor: Optional[float] = None
    f_stabilizer: Optional[float] = None  # (related to CuFraction in ProteCCT)
    f_insulation: Optional[float] = None
    f_inner_voids: Optional[float] = None
    f_outer_voids: Optional[float] = None
    # Available materials depend on the component and on the selected program
    material_insulation: Optional[str] = None
    material_inner_voids: Optional[str] = None
    material_outer_voids: Optional[str] = None


class Rutherford(BaseModel):
    """
    Rutherford cable type: for example LHC MB magnet cable
    """

    type: Literal["Rutherford"]
    n_strands: Optional[int] = None
    n_strand_layers: Optional[int] = None
    n_strands_per_layers: Optional[int] = None
    bare_cable_width: Optional[float] = None
    bare_cable_height_low: Optional[float] = None
    bare_cable_height_high: Optional[float] = None
    bare_cable_height_mean: Optional[float] = None
    th_insulation_along_width: Optional[float] = None
    th_insulation_along_height: Optional[float] = None
    width_core: Optional[float] = None
    height_core: Optional[float] = None
    strand_twist_pitch: Optional[float] = None
    strand_twist_pitch_angle: Optional[float] = None
    Rc: Optional[float] = Field(
        default = 0.0,
        desctiption = "Resistance of the contact between crossing strands [Ohm]"
    )
    Ra: Optional[float] = Field(
        default = 0.0,
        desctiption = "Resistance of the contact between adjacent strands over one periodicity length (strand twist pitch divided by the number of strands) [Ohm]"
    )
    gamma_c: Optional[float] = Field(
        default = 0.0,
        description = "DISCC parameter: main crossing scaling parameter that quantifies crossing coupling due to field perpendicular to cable wide face [-]"
    )
    gamma_a: Optional[float] = Field(
        default = 0.0,
        description = "DISCC parameter: main adjacent scaling parameter that quantifies adjacent coupling due to field parallel to cable wide face [-]"
    )
    lambda_a: Optional[float] = Field(
        default = 0.0,
        description = "DISCC parameter: mixing scaling parameter that quantifies adjacent coupling due to field perpendicular to cable wide face [-]"
    )
    n: Optional[float] = Field(
        default = 0.0,
        description = "Power law / Current sharing exponent [-]"
    )
    ec: Optional[float] = Field(
        default = 0.0,
        description = "Power law / Current sharing scale factor [V/m]"
    )
    ks_factor: Optional[float] = Field(
        default = 0.0,
        description = "Parameter for keystone angle handling in DISCC model [-]"
    )
    # Fractions given with respect to the insulated conductor
    f_superconductor: Optional[float] = None
    f_stabilizer: Optional[float] = None  # (related to CuFraction in ProteCCT)
    f_insulation: Optional[float] = None
    f_inner_voids: Optional[float] = None
    f_outer_voids: Optional[float] = None
    f_core: Optional[float] = None
    # Available materials depend on the component and on the selected program
    material_insulation: Optional[str] = None
    material_inner_voids: Optional[str] = None
    material_outer_voids: Optional[str] = None
    material_core: Optional[str] = None


class Ribbon(BaseModel):
    """
    Mono cable type: This is basically type of cable consisting of one strand - not really a cable
    """

    type: Literal["Ribbon"]
    n_strands: Optional[int] = (
        None  # This defines the number of "strands" in the ribbon cable, which are physically glued but electrically in series
    )
    bare_cable_width: Optional[float] = None
    bare_cable_height_low: Optional[float] = None
    bare_cable_height_high: Optional[float] = None
    bare_cable_height_mean: Optional[float] = None
    th_insulation_along_width: Optional[float] = (
        None  # This defines the thickness of the insulation around each strand (DIFFERENT FROM ROXIE CADATA FILE)
    )
    th_insulation_along_height: Optional[float] = (
        None  # This defines the thickness of the insulation around each strand (DIFFERENT FROM ROXIE CADATA FILE)
    )
    # Fractions given with respect to the insulated conductor
    f_superconductor: Optional[float] = None
    f_stabilizer: Optional[float] = None  # (related to CuFraction in ProteCCT)
    f_insulation: Optional[float] = None
    f_inner_voids: Optional[float] = None
    f_outer_voids: Optional[float] = None
    f_core: Optional[float] = None
    # Available materials depend on the component and on the selected program
    material_insulation: Optional[str] = None
    material_inner_voids: Optional[str] = None
    material_outer_voids: Optional[str] = None
    material_core: Optional[str] = None

class TSTC(BaseModel):
    """
    Twisted Stacked-Tape Cable (TSTC) type:
    """
    type: Literal["TSTC"]
    stack_layout: Optional[List[Literal[-1,0,1]]] = Field(default=None,description="2D: Tape stack layout ordered TOP->BOTTOM. The numbers represent: 1 = a CC tape, -1 = a flipped CC tape, 0 = a shunt.")
    nb_tapes: Optional[int] = Field(default=None, description="3D: Number of tapes in the stack")
    tape_width: Optional[float] = Field(default=None, description="3D and 2D: Width of each tape")
    tape_thickness: Optional[float] = Field(default=None, description="3D and 2D: Thickness of each tape")
    twist_pitch: Optional[float] = Field(default=None, description="3D: Length over which tapes are twisted by full rotation")
    pitch_fraction: Optional[float] = Field(default=1.0, description="3D: Fraction of the twist pitch to be modelled (1.0 = full pitch, 0.5 = half pitch, etc.)")
    bare_cable_width: Optional[float] = Field(default=None, description="Cable width, typically the same as CC width")
    bare_cable_height_low: Optional[float] = Field(default=None, description="Narrow end (if applicable) cable height (thickness), typically the same as (CC thickness + Cu stabilizer thickness) * number of tapes.")
    bare_cable_height_high: Optional[float] = Field(default=None, description="Wide end (if applicable) cable height (thickness), typically the same as (CC thickness + Cu stabilizer thickness) * number of tapes.")
    bare_cable_height_mean: Optional[float] = Field(default=None, description="Average (if applicable) cable height (thickness), typically the same as (CC thickness + Cu stabilizer thickness) * number of tapes.")
    th_insulation_along_width: Optional[float] = Field(default=None, description="Insulation thickness along the width ")
    th_insulation_along_height: Optional[float] = Field(default=None, description="Insulation thickness along the height ")
    f_superconductor: Optional[float] = Field(default=None, description="Fraction of superconductor related to the total area of the cable (winding cell)")
    f_stabilizer: Optional[float] = Field(default=None, description="Fraction of stabilizer related to the total area of the cable (winding cell)")
    f_silver: Optional[float] = Field(default=None, description="Fraction of silver related to the total area of the cable (winding cell)")
    f_substrate: Optional[float] = Field(default=None, description="Fraction of substrate (including buffer layers and silver overlay) related to the total area of the cable (winding cell)")
    f_shunt: Optional[float] = Field(default=None, description="Fraction of substrate (including buffer layers and silver overlay) related to the total area of the cable (winding cell)")
    f_insulation: Optional[float] = Field(default=None, description="Fraction of cable insulation related to the total area of the cable (winding cell)")
    f_inner_voids: Optional[float] = Field(default=None, description="Fraction of additional material (typically insulation) related to the total area of the cable (winding cell)")
    f_outer_voids: Optional[float] = Field(default=None, description="Fraction of additional material (typically helium impregnating the windings) related to the total area of the cable (winding cell)")


# ------------------- Conductors ---------------------------#

# class MaterialSuperconductor(BaseModel):
#     """
#     Level 3: Class for strand superconductor material parameters
#     """
#     material: Optional[str] = Field(default=None, description="Material of the superconductor. E.g. NbTi, Nb3Sn, etc.")
#     n_value: Optional[float] = Field(default=None, description="n value of the superconductor (for power law fit).")
#     ec: Optional[float] = Field(default=None, description="Critical electric field of the superconductor.")
#     Cv_material: Optional[Union[str, float]] = Field(default=None, description="Material function for specific heat of the superconductor.")

# class MaterialStabilizer(BaseModel):
#     """
#     Level 3: Class for strand stabilizer material parameters
#     """

#     rho_material: Optional[Union[str, float]] = Field(default=None, description="Material function for resistivity of the stabilizer. Constant resistivity can be given as float.")
#     RRR: Optional[float] = Field(default=None, description="Residual resistivity ratio of the stabilizer.")
#     T_ref_RRR_high: Optional[float] = Field(default=None, description="Upper reference temperature for RRR measurements.")
#     T_ref_RRR_low: Optional[float] = Field(default=None, description="Lower reference temperature for RRR measurements.")
#     k_material: Optional[Union[str, float]] = Field(default=None, description="Thermal conductivity of the stabilizer.")
#     Cv_material: Optional[Union[str, float]] = Field(default=None, description="Material function for specific heat of the stabilizer.")


class Round(BaseModel):
    """
    Level 2: Class for strand parameters
    """

    type: Literal["Round"]
    fil_twist_pitch: Optional[float] = None # Strand twist pitch
    diameter: Optional[float] = None  # ds_inGroup (LEDET), DConductor (BBQ), DStrand (ProteCCT)
    diameter_core:  Optional[float] = None  # dcore_inGroup (LEDET)
    diameter_filamentary: Optional[float] = None  # dfilamentary_inGroup (LEDET)
    filament_diameter: Optional[float] = None  # df_inGroup (LEDET)
    filament_hole_diameter: Optional[float] = Field(default=None, description="Specifies round or hexagonal hole diameter inside the filament. If None or 0.0, no hole is created.")
    number_of_filaments: Optional[int] = None  # nf_inGroup (LEDET)
    f_Rho_effective: Optional[float] = None
    Cu_noCu_in_strand: Optional[float] = None

    # -- Superconductor parameters -- #
    material_superconductor: Optional[str] = Field(default=None, description="Material of the superconductor. E.g. Nb-Ti, Nb3Sn, etc.")
    n_value_superconductor: Optional[float] = Field(default=None, description="n value of the superconductor (for power law fit).")
    ec_superconductor: Optional[float] = Field(default=None, description="Critical electric field of the superconductor in V/m.")
    minimum_jc_fraction: Optional[float] = Field(gt=0, le=1, default=None, description="Fraction of Jc(minimum_jc_field, T) to use as minimum Jc for the power law fit to avoid division by zero when Jc(B_local, T) decreases to zero."
                                                                           "Typical value would be 0.001 (so the Jc_minimum is 0.1% of Jc(minimum_jc_field, T))"
                                                                            "This fraction is only allowed to be greater than 0.0 and less than or equal to 1.0")
    minimum_jc_field: Optional[float] = Field(default=None, description="Magnetic flux density in tesla used for calculation of Jc(minimum_jc_field, T). This gets multiplied by minimum_jc_fraction and used as minimum Jc for the power law")
    k_material_superconductor: Optional[Union[str, float]] = Field(default=None, description="Thermal conductivity of the superconductor.")
    Cv_material_superconductor: Optional[Union[str, float]] = Field(default=None, description="Material function for specific heat of the superconductor.")
    # -- Stabilizer parameters -- #
    material_stabilizer: Optional[str] = Field(default=None, description="Material of the stabilizer.")
    rho_material_stabilizer: Optional[Union[str, float]] = Field(default=None, description="Material function for resistivity of the stabilizer. Constant resistivity can be given as float.")
    rho_material_holes: Optional[Union[str, float]] = Field(default=None, description="Material function for resistivity of the holes in the filaments."
                                                                                     "Constant resistivity can be given as float, material name as a string or None or 0.0 to use 'air' in the holes.")
    RRR: Optional[Union[float, List[float]]] = Field(default=None, description="Residual resistivity ratio of the stabilizer. If a list of RRR is provided it needs to match in length the number of matrix regions in the geometry (typically 3)")
    T_ref_RRR_high: Optional[float] = Field(default=None, description="Upper reference temperature for RRR measurements.")
    T_ref_RRR_low: Optional[float] = Field(default=None, description="Lower reference temperature for RRR measurements.")
    k_material_stabilizer: Optional[Union[str, float]] = Field(default=None, description="Thermal conductivity of the stabilizer.")
    Cv_material_stabilizer: Optional[Union[str, float]] = Field(default=None, description="Material function for specific heat of the stabilizer.")

    # superconductor: MaterialSuperconductor = MaterialSuperconductor()
    # stabilizer: MaterialStabilizer = MaterialStabilizer()


class Rectangular(BaseModel):
    """
    Level 2: Class for strand parameters
    """

    type: Literal["Rectangular"]
    bare_width: Optional[float] = None
    bare_height: Optional[float] = None
    bare_corner_radius: Optional[float] = None
    Cu_noCu_in_strand: Optional[float] = None
    filament_diameter: Optional[float] = None  # df_inGroup (LEDET)
    number_of_filaments: Optional[int] = None
    f_Rho_effective: Optional[float] = None
    fil_twist_pitch: Optional[float] = None

    # -- Superconductor parameters -- #
    material_superconductor: Optional[str] = Field(default=None, description="Material of the superconductor. E.g. NbTi, Nb3Sn, etc.")
    n_value_superconductor: Optional[float] = Field(default=None, description="n value of the superconductor (for power law fit).")
    ec_superconductor: Optional[float] = Field(default=None, description="Critical electric field of the superconductor.")
    minimum_jc_fraction: Optional[float] = Field(gt=0, le=1, default=None, description="Fraction of Jc(minimum_jc_field, T) to use as minimum Jc for the power law"
                                                                                       " fit to avoid division by zero when Jc(B_local, T) decreases to zero."
                                                                           "Typical value would be 0.001 (so the Jc_minimum is 0.1% of Jc(minimum_jc_field, T))"
                                                                            "This fraction is only allowed to be greater than 0.0 and less than or equal to 1.0")
    minimum_jc_field: Optional[float] = Field(default=None, description="Magnetic flux density in tesla used for calculation of Jc(minimum_jc_field, T)."
                                                                        "This gets multiplied by minimum_jc_fraction and used as minimum Jc for the power law")
    k_material_superconductor: Optional[Union[str, float]] = Field(default=None, description="Thermal conductivity of the superconductor.")
    Cv_material_superconductor: Optional[Union[str, float]] = Field(default=None, description="Material function for specific heat of the superconductor.")
    # -- Stabilizer parameters -- #
    material_stabilizer: Optional[str] = Field(default=None, description="Material of the stabilizer.") #TODO this should be removed as is substituted by rho, k and Cv
    k_material_stabilizer: Optional[Union[str, float]] = Field(default=None, description="Thermal conductivity of the stabilizer.")
    Cv_material_stabilizer: Optional[Union[str, float]] = Field(default=None, description="Material function for specific heat of the stabilizer.")
    rho_material_stabilizer: Optional[Union[str, float]] = Field(default=None, description="Material function for resistivity of the stabilizer. Constant resistivity can be given as float.")
    RRR: Optional[Union[float, List[float]]] = Field(default=None, description="Residual resistivity ratio of the stabilizer. If a list of RRR is provided it needs to match in length the number of matrix regions in the geometry (typically 3)")
    T_ref_RRR_high: Optional[float] = Field(default=None, description="Upper reference temperature for RRR measurements.")
    T_ref_RRR_low: Optional[float] = Field(default=None, description="Lower reference temperature for RRR measurements.")


class Copper_thickness(BaseModel):
    left: Optional[float] = Field(default=None, description="On the left side.")
    right: Optional[float] = Field(default=None, description="On the right side.")
    top: Optional[float] = Field(default=None, description="On the top side.")
    bottom: Optional[float] = Field(default=None, description="On the bottom side.")


class Silver_thickness(BaseModel):
    top: Optional[float] = Field(default=None, description="On the top side.")
    bottom: Optional[float] = Field(default=None, description="On the bottom side.")


class CC(BaseModel):
    """
    Level 2: Class for coated conductor parameters
    """
    type: Literal["CC"]

    # Core layer sizes
    HTS_thickness: Optional[float] = Field(default=None, description="HTS thickness in meters.")
    HTS_width: Optional[float] = Field(default=None, description="HTS width in meters.")
    number_of_filaments: Optional[int] = Field(default=1, ge=1, description="Number of HTS filaments. If 1, no striation case")
    gap_between_filaments: Optional[float] = Field(default=None, description="Gap between HTS filaments in meters. Only applies when number_of_filaments > 1.")
    substrate_thickness: Optional[float] = Field(default=None, description="Substrate layer thickness in meters.")

    # Plating/stabilizer
    copper_thickness: Copper_thickness = Field(default=Copper_thickness(), description="Copper thickness in meters")
    silver_thickness: Silver_thickness = Field(default=Silver_thickness(), description="Silver thickness in meters")

    # -- Superconductor parameters -- #
    material_superconductor: Optional[str] = Field(default=None, description="Material of the superconductor. E.g. NbTi, Nb3Sn, etc.")
    n_value_superconductor: Optional[float] = Field(default=None, description="n value of the superconductor (for power law fit).")
    ec_superconductor: Optional[float] = Field(default=None, description="Critical electric field of the superconductor.")
    minimum_jc_fraction: Optional[float] = Field(gt=0, le=1, default=None, description="Fraction of Jc(minimum_jc_field, T) to use as minimum Jc for the power law"
                                                                                       " fit to avoid division by zero when Jc(B_local, T) decreases to zero."
                                                                           "Typical value would be 0.001 (so the Jc_minimum is 0.1% of Jc(minimum_jc_field, T))"
                                                                            "This fraction is only allowed to be greater than 0.0 and less than or equal to 1.0")
    minimum_jc_field: Optional[float] = Field(default=None, description="Magnetic flux density in tesla used for calculation of Jc(minimum_jc_field, T)."
                                                                        "This gets multiplied by minimum_jc_fraction and used as minimum Jc for the power law")
    k_material_superconductor: Optional[Union[str, float]] = Field(default=None, description="Thermal conductivity of the superconductor.")
    Cv_material_superconductor: Optional[Union[str, float]] = Field(default=None, description="Material function for specific heat of the superconductor.")
    k_material_stabilizer: Optional[Union[str, float]] = Field(default=None, description="Thermal conductivity of the stabilizer, typically copper.")
    Cv_material_stabilizer: Optional[Union[str, float]] = Field(default=None, description="Material function for specific heat of the stabilizer, typically copper.")
    rho_material_stabilizer: Optional[Union[str, float]] = Field(default=None, description="Material function for resistivity of the stabilizer. Constant resistivity can be given as float.")
    RRR: Optional[Union[float, List[float]]] = Field(default=None, description="Residual resistivity ratio of the stabilizer. If a list of RRR is provided it needs to match in length the number of matrix regions in the geometry (typically 3)")
    T_ref_RRR_high: Optional[float] = Field(default=None, description="Upper reference temperature for RRR measurements.")
    T_ref_RRR_low: Optional[float] = Field(default=None, description="Lower reference temperature for RRR measurements.")
    k_material_silver: Optional[Union[str, float]] = Field(default=None, description="Thermal conductivity of the silver")
    Cv_material_silver: Optional[Union[str, float]] = Field(default=None, description="Material function for specific heat of the silver")
    rho_material_silver: Optional[Union[str, float]] = Field(default=None, description="Material function for resistivity of the silver. Constant resistivity can be given as float.")
    RRR_silver: Optional[Union[float, List[float]]] = Field(default=None, description="Residual resistivity ratio of the silver. If a list of RRR is provided it needs to match in length the number of matrix regions in the geometry (typically 3)")
    T_ref_RRR_high_silver: Optional[float] = Field(default=None, description="Upper reference temperature for RRR measurements for silver.")
    T_ref_RRR_low_silver: Optional[float] = Field(default=None, description="Lower reference temperature for RRR measurements for silver.")
    rho_material_substrate: Optional[Union[str, float]] = Field(default=None, description="Material function for resistivity of the substrate. Constant resistivity can be given as float.")
    k_material_substrate: Optional[Union[str, float]] = Field(default=None, description="Thermal conductivity of the substrate.")
    Cv_material_substrate: Optional[Union[str, float]] = Field(default=None, description="Material function for specific heat of the substrate.")


class Homogenized(BaseModel):
    """
    Level 2: Class for homogenized strand parameters, to be used in the Rutherford cable model
    """
    type: Literal["Homogenized"]

    # Strand diameter (used in the geometry step)
    diameter: Optional[float] = Field(default=None, description="Undeformed round strand diameter. Used in the geometry step if keep_strand_area==true, the strand is deformed while preserving its surface area. Not used otherwise.")


class Tape(BaseModel):
    """
    Level 2: Class for Cu Tape (do not confuse with HTS coated conductor)
    """

    type: Literal["Tape"]
    bare_width: Optional[float] = None
    bare_height: Optional[float] = None
    bare_corner_radius: Optional[float] = None
    rho_material_shunt: Optional[Union[str, float]] = Field(default=None, description="Material function for resistivity of the shunt. Constant resistivity can be given as float.")
    RRR: Optional[float] = Field(default=None, description="Residual resistivity ratio of the shunt.")
    T_ref_RRR_high: Optional[float] = Field(default=None, description="Upper reference temperature for RRR measurements.")
    T_ref_RRR_low: Optional[float] = Field(default=None, description="Lower reference temperature for RRR measurements.")
    k_material_shunt: Optional[Union[str, float]] = Field(default=None, description="Thermal conductivity of the shunt.")
    Cv_material_shunt: Optional[Union[str, float]] = Field(default=None, description="Material function for specific heat of the shunt.")

class NoShunt(BaseModel):
    """
    Level 2: Class for Cu Tape (do not confuse with HTS coated conductor)
    """

    type: Literal["NoShunt"]

# ------------------- Conductors ---------------------------#


class Conductor(BaseModel):
    """
    Level 1: Class for conductor parameters
    """

    version: Optional[str] = None
    case: Optional[str] = None
    state: Optional[str] = None
    cable: Union[Rutherford, Mono, Ribbon, TSTC] = Rutherford(type="Rutherford") # TODO: Busbar, Rope, Roebel, CORC, CICC
    strand: Union[Round, Rectangular, CC, Homogenized] = Round(type="Round") # TODO: WIC
    shunt: Union[Tape, NoShunt] = NoShunt(type="NoShunt")
    Jc_fit: Union[ConstantJc, Bottura, CUDI1, CUDI3, Summers, Bordini, Nb3Sn_HFM, BSCCO_2212_LBNL, Ic_A_NbTi, ProDefined, Succi_fixed, Zero, Fujikura] = CUDI1(type="CUDI1")  # TODO: CUDI other numbers? , Roxie?
