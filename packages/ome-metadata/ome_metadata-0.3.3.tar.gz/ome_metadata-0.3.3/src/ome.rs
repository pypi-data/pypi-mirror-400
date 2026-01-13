use crate::error::Error;
use enum_utils::{FromStr, IterVariants};
#[cfg(feature = "python")]
use pyo3::types::{PyDict, PyInt, PyString};
#[cfg(feature = "python")]
use pyo3::{Bound, IntoPyObject, PyErr, PyResult, Python};
use serde::{Deserialize, Serialize};
use std::cmp::PartialEq;

#[cfg(feature = "python")]
macro_rules! impl_enum_into_py_object {
    ($($t:ty $(,)?)*) => {
        $(
            impl<'py> IntoPyObject<'py> for $t {
                type Target = PyString;
                type Output = Bound<'py, Self::Target>;
                type Error = PyErr;

                fn into_pyobject(self, py: Python<'py>) -> PyResult<Self::Output> {
                    Ok(format!("{:?}", self).into_pyobject(py)?)
                }
            }
        )*
    };
}

#[cfg(feature = "python")]
macro_rules! impl_empty_struct_into_py_object {
    ($($t:ty $(,)?)*) => {
        $(
            impl<'py> IntoPyObject<'py> for $t {
                type Target = PyInt;
                type Output = Bound<'py, Self::Target>;
                type Error = PyErr;

                fn into_pyobject(self, py: Python<'py>) -> PyResult<Self::Output> {
                    Ok(0usize.into_pyobject(py)?)
                }
            }
        )*
    };
}

#[cfg(feature = "python")]
macro_rules! impl_boxed_struct_into_py_object {
    ($($t:ty $(,)?)*) => {
        $(
            impl<'py> IntoPyObject<'py> for Box<$t> {
                type Target = PyDict;
                type Output = Bound<'py, Self::Target>;
                type Error = PyErr;

                fn into_pyobject(self, py: Python<'py>) -> PyResult<Self::Output> {
                    (*self).into_pyobject(py)
                }
            }
        )*
    };
}

#[cfg(feature = "python")]
impl_enum_into_py_object!(
    ArcType,
    BinDataCompressionType,
    BinningType,
    ChannelIlluminationType,
    ChannelAcquisitionModeType,
    ChannelContrastMethodType,
    DetectorType,
    ExperimentItemType,
    FilamentType,
    FilterType,
    FontFamilyType,
    LaserType,
    LaserLaserMediumType,
    LaserPulseType,
    MarkerType,
    MicrobeamManipulationItemType,
    MicroscopeType,
    NamingConventionType,
    ObjectiveCorrectionType,
    ObjectiveImmersionType,
    ObjectiveSettingsMediumType,
    PixelsDimensionOrderType,
    PixelType,
    ShapeFillRuleType,
    ShapeFontStyleType
);

#[cfg(feature = "python")]
impl_empty_struct_into_py_object!(MetadataOnly, XmlAnnotationValue);
#[cfg(feature = "python")]
impl_boxed_struct_into_py_object!(Channel, Image);

#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AffineTransform {
    #[serde(rename = "@A00")]
    pub a00: f32,
    #[serde(rename = "@A10")]
    pub a10: f32,
    #[serde(rename = "@A01")]
    pub a01: f32,
    #[serde(rename = "@A11")]
    pub a11: f32,
    #[serde(rename = "@A02")]
    pub a02: f32,
    #[serde(rename = "@A12")]
    pub a12: f32,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Annotation {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Namespace")]
    pub namespace: Option<String>,
    #[serde(default, rename = "@Annotator")]
    pub annotator: Option<String>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AnnotationRef {
    #[serde(rename = "@ID")]
    pub id: String,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Arc {
    #[serde(default, rename = "@Manufacturer")]
    pub manufacturer: Option<String>,
    #[serde(default, rename = "@Model")]
    pub model: Option<String>,
    #[serde(default, rename = "@SerialNumber")]
    pub serial_number: Option<String>,
    #[serde(default, rename = "@LotNumber")]
    pub lot_number: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Power")]
    pub power: Option<f32>,
    #[serde(default = "Arc::default_power_unit", rename = "@PowerUnit")]
    pub power_unit: UnitsPower,
    #[serde(default, rename = "@Type")]
    pub r#type: Option<ArcType>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl Arc {
    pub fn default_power_unit() -> UnitsPower {
        UnitsPower::W
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ArcType {
    #[serde(rename = "Hg")]
    Hg,
    #[serde(rename = "Xe")]
    Xe,
    #[serde(rename = "HgXe")]
    HgXe,
    #[serde(rename = "Other")]
    Other,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BinData {
    #[serde(default = "BinData::default_compression", rename = "@Compression")]
    pub compression: BinDataCompressionType,
    #[serde(rename = "@BigEndian")]
    pub big_endian: bool,
    #[serde(rename = "@Length")]
    pub length: i64,
    #[serde(rename = "$text")]
    pub content: String,
}
impl BinData {
    pub fn default_compression() -> BinDataCompressionType {
        BinDataCompressionType::None
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum BinDataCompressionType {
    #[serde(rename = "zlib")]
    Zlib,
    #[serde(rename = "bzip2")]
    Bzip2,
    #[serde(rename = "none")]
    None,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BinaryFile {
    #[serde(rename = "@FileName")]
    pub file_name: String,
    #[serde(rename = "@Size")]
    pub size: i64,
    #[serde(default, rename = "@MIMEType")]
    pub mime_type: Option<String>,
    #[serde(rename = "$value")]
    pub content: BinaryFileContent,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum BinaryFileContent {
    #[serde(rename = "External")]
    External(External),
    #[serde(rename = "BinData")]
    BinData(BinData),
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum BinningType {
    #[serde(rename = "1x1")]
    _1X1,
    #[serde(rename = "2x2")]
    _2X2,
    #[serde(rename = "4x4")]
    _4X4,
    #[serde(rename = "8x8")]
    _8X8,
    #[serde(rename = "Other")]
    Other,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BooleanAnnotation {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Namespace")]
    pub namespace: Option<String>,
    #[serde(default, rename = "@Annotator")]
    pub annotator: Option<String>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
    #[serde(rename = "Value")]
    pub value: bool,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Channel {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Name")]
    pub name: Option<String>,
    #[serde(default, rename = "@SamplesPerPixel")]
    pub samples_per_pixel: Option<i32>,
    #[serde(default, rename = "@IlluminationType")]
    pub illumination_type: Option<ChannelIlluminationType>,
    #[serde(default, rename = "@PinholeSize")]
    pub pinhole_size: Option<f32>,
    #[serde(
        default = "Channel::default_pinhole_size_unit",
        rename = "@PinholeSizeUnit"
    )]
    pub pinhole_size_unit: UnitsLength,
    #[serde(default, rename = "@AcquisitionMode")]
    pub acquisition_mode: Option<ChannelAcquisitionModeType>,
    #[serde(default, rename = "@ContrastMethod")]
    pub contrast_method: Option<ChannelContrastMethodType>,
    #[serde(default, rename = "@ExcitationWavelength")]
    pub excitation_wavelength: Option<f32>,
    #[serde(
        default = "Channel::default_excitation_wavelength_unit",
        rename = "@ExcitationWavelengthUnit"
    )]
    pub excitation_wavelength_unit: UnitsLength,
    #[serde(default, rename = "@EmissionWavelength")]
    pub emission_wavelength: Option<f32>,
    #[serde(
        default = "Channel::default_emission_wavelength_unit",
        rename = "@EmissionWavelengthUnit"
    )]
    pub emission_wavelength_unit: UnitsLength,
    #[serde(default, rename = "@Fluor")]
    pub fluor: Option<String>,
    #[serde(default, rename = "@NDFilter")]
    pub nd_filter: Option<f32>,
    #[serde(default, rename = "@PockelCellSetting")]
    pub pockel_cell_setting: Option<i32>,
    #[serde(default = "Channel::default_color", rename = "@Color")]
    pub color: i32,
    #[serde(default, rename = "LightSourceSettings")]
    pub light_source_settings: Option<LightSourceSettings>,
    #[serde(default, rename = "DetectorSettings")]
    pub detector_settings: Option<DetectorSettings>,
    #[serde(default, rename = "FilterSetRef")]
    pub filter_set_ref: Option<AnnotationRef>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "LightPath")]
    pub light_path: Option<LightPath>,
}
impl Channel {
    pub fn default_pinhole_size_unit() -> UnitsLength {
        UnitsLength::um
    }
    pub fn default_color() -> i32 {
        0
    }
    pub fn default_excitation_wavelength_unit() -> UnitsLength {
        UnitsLength::nm
    }
    pub fn default_emission_wavelength_unit() -> UnitsLength {
        UnitsLength::nm
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ChannelAcquisitionModeType {
    #[serde(rename = "WideField")]
    WideField,
    #[serde(rename = "LaserScanningConfocalMicroscopy")]
    LaserScanningConfocalMicroscopy,
    #[serde(rename = "SpinningDiskConfocal")]
    SpinningDiskConfocal,
    #[serde(rename = "SlitScanConfocal")]
    SlitScanConfocal,
    #[serde(rename = "MultiPhotonMicroscopy")]
    MultiPhotonMicroscopy,
    #[serde(rename = "StructuredIllumination")]
    StructuredIllumination,
    #[serde(rename = "SingleMoleculeImaging")]
    SingleMoleculeImaging,
    #[serde(rename = "TotalInternalReflection")]
    TotalInternalReflection,
    #[serde(rename = "FluorescenceLifetime")]
    FluorescenceLifetime,
    #[serde(rename = "SpectralImaging")]
    SpectralImaging,
    #[serde(rename = "FluorescenceCorrelationSpectroscopy")]
    FluorescenceCorrelationSpectroscopy,
    #[serde(rename = "NearFieldScanningOpticalMicroscopy")]
    NearFieldScanningOpticalMicroscopy,
    #[serde(rename = "SecondHarmonicGenerationImaging")]
    SecondHarmonicGenerationImaging,
    #[serde(rename = "PALM")]
    Palm,
    #[serde(rename = "STORM")]
    Storm,
    #[serde(rename = "STED")]
    Sted,
    #[serde(rename = "TIRF")]
    Tirf,
    #[serde(rename = "FSM")]
    Fsm,
    #[serde(rename = "LCM")]
    Lcm,
    #[serde(rename = "Other")]
    Other,
    #[serde(rename = "BrightField")]
    BrightField,
    #[serde(rename = "SweptFieldConfocal")]
    SweptFieldConfocal,
    #[serde(rename = "SPIM")]
    Spim,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ChannelContrastMethodType {
    #[serde(rename = "Brightfield")]
    Brightfield,
    #[serde(rename = "Phase")]
    Phase,
    #[serde(rename = "DIC")]
    Dic,
    #[serde(rename = "HoffmanModulation")]
    HoffmanModulation,
    #[serde(rename = "ObliqueIllumination")]
    ObliqueIllumination,
    #[serde(rename = "PolarizedLight")]
    PolarizedLight,
    #[serde(rename = "Darkfield")]
    Darkfield,
    #[serde(rename = "Fluorescence")]
    Fluorescence,
    #[serde(rename = "Other")]
    Other,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ChannelIlluminationType {
    #[serde(rename = "Transmitted")]
    Transmitted,
    #[serde(rename = "Epifluorescence")]
    Epifluorescence,
    #[serde(rename = "Oblique")]
    Oblique,
    #[serde(rename = "NonLinear")]
    NonLinear,
    #[serde(rename = "Other")]
    Other,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CommentAnnotation {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Namespace")]
    pub namespace: Option<String>,
    #[serde(default, rename = "@Annotator")]
    pub annotator: Option<String>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
    #[serde(rename = "Value")]
    pub value: String,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Dataset {
    #[serde(default, rename = "@Name")]
    pub name: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "ExperimenterRef")]
    pub experimenter_ref: Option<AnnotationRef>,
    #[serde(default, rename = "ExperimenterGroupRef")]
    pub experimenter_group_ref: Option<AnnotationRef>,
    #[serde(default, rename = "ImageRef")]
    pub image_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Detector {
    #[serde(default, rename = "@Manufacturer")]
    pub manufacturer: Option<String>,
    #[serde(default, rename = "@Model")]
    pub model: Option<String>,
    #[serde(default, rename = "@SerialNumber")]
    pub serial_number: Option<String>,
    #[serde(default, rename = "@LotNumber")]
    pub lot_number: Option<String>,
    #[serde(default, rename = "@Gain")]
    pub gain: Option<f32>,
    #[serde(default, rename = "@Voltage")]
    pub voltage: Option<f32>,
    #[serde(default = "Detector::default_voltage_unit", rename = "@VoltageUnit")]
    pub voltage_unit: UnitsElectricPotential,
    #[serde(default, rename = "@Offset")]
    pub offset: Option<f32>,
    #[serde(default, rename = "@Zoom")]
    pub zoom: Option<f32>,
    #[serde(default, rename = "@AmplificationGain")]
    pub amplification_gain: Option<f32>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Type")]
    pub r#type: Option<DetectorType>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl Detector {
    pub fn default_voltage_unit() -> UnitsElectricPotential {
        UnitsElectricPotential::V
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DetectorSettings {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Offset")]
    pub offset: Option<f32>,
    #[serde(default, rename = "@Gain")]
    pub gain: Option<f32>,
    #[serde(default, rename = "@Voltage")]
    pub voltage: Option<f32>,
    #[serde(
        default = "DetectorSettings::default_voltage_unit",
        rename = "@VoltageUnit"
    )]
    pub voltage_unit: UnitsElectricPotential,
    #[serde(default, rename = "@Zoom")]
    pub zoom: Option<f32>,
    #[serde(default, rename = "@ReadOutRate")]
    pub read_out_rate: Option<f32>,
    #[serde(
        default = "DetectorSettings::default_read_out_rate_unit",
        rename = "@ReadOutRateUnit"
    )]
    pub read_out_rate_unit: UnitsFrequency,
    #[serde(default, rename = "@Binning")]
    pub binning: Option<BinningType>,
    #[serde(default, rename = "@Integration")]
    pub integration: Option<i32>,
}
impl DetectorSettings {
    pub fn default_voltage_unit() -> UnitsElectricPotential {
        UnitsElectricPotential::V
    }
    pub fn default_read_out_rate_unit() -> UnitsFrequency {
        UnitsFrequency::Hz
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum DetectorType {
    #[serde(rename = "CCD")]
    Ccd,
    #[serde(rename = "IntensifiedCCD")]
    IntensifiedCcd,
    #[serde(rename = "AnalogVideo")]
    AnalogVideo,
    #[serde(rename = "PMT")]
    Pmt,
    #[serde(rename = "Photodiode")]
    Photodiode,
    #[serde(rename = "Spectroscopy")]
    Spectroscopy,
    #[serde(rename = "LifetimeImaging")]
    LifetimeImaging,
    #[serde(rename = "CorrelationSpectroscopy")]
    CorrelationSpectroscopy,
    #[serde(rename = "FTIR")]
    Ftir,
    #[serde(rename = "EMCCD")]
    Emccd,
    #[serde(rename = "APD")]
    Apd,
    #[serde(rename = "CMOS")]
    Cmos,
    #[serde(rename = "EBCCD")]
    Ebccd,
    #[serde(rename = "Other")]
    Other,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Dichroic {
    #[serde(default, rename = "@Manufacturer")]
    pub manufacturer: Option<String>,
    #[serde(default, rename = "@Model")]
    pub model: Option<String>,
    #[serde(default, rename = "@SerialNumber")]
    pub serial_number: Option<String>,
    #[serde(default, rename = "@LotNumber")]
    pub lot_number: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DoubleAnnotation {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Namespace")]
    pub namespace: Option<String>,
    #[serde(default, rename = "@Annotator")]
    pub annotator: Option<String>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
    #[serde(rename = "Value")]
    pub value: f64,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Ellipse {
    #[serde(default, rename = "@FillColor")]
    pub fill_color: Option<i32>,
    #[serde(default, rename = "@FillRule")]
    pub fill_rule: Option<ShapeFillRuleType>,
    #[serde(default, rename = "@StrokeColor")]
    pub stroke_color: Option<i32>,
    #[serde(default, rename = "@StrokeWidth")]
    pub stroke_width: Option<f32>,
    #[serde(
        default = "Ellipse::default_stroke_width_unit",
        rename = "@StrokeWidthUnit"
    )]
    pub stroke_width_unit: UnitsLength,
    #[serde(default, rename = "@StrokeDashArray")]
    pub stroke_dash_array: Option<String>,
    #[serde(default, rename = "@Text")]
    pub text: Option<String>,
    #[serde(default, rename = "@FontFamily")]
    pub font_family: Option<FontFamilyType>,
    #[serde(default, rename = "@FontSize")]
    pub font_size: Option<i32>,
    #[serde(default = "Ellipse::default_font_size_unit", rename = "@FontSizeUnit")]
    pub font_size_unit: UnitsLength,
    #[serde(default, rename = "@FontStyle")]
    pub font_style: Option<ShapeFontStyleType>,
    #[serde(default, rename = "@Locked")]
    pub locked: Option<bool>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@TheZ")]
    pub the_z: Option<i32>,
    #[serde(default, rename = "@TheT")]
    pub the_t: Option<i32>,
    #[serde(default, rename = "@TheC")]
    pub the_c: Option<i32>,
    #[serde(rename = "@X")]
    pub x: f32,
    #[serde(rename = "@Y")]
    pub y: f32,
    #[serde(rename = "@RadiusX")]
    pub radius_x: f32,
    #[serde(rename = "@RadiusY")]
    pub radius_y: f32,
    #[serde(default, rename = "Transform")]
    pub transform: Option<AffineTransform>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl Ellipse {
    pub fn default_stroke_width_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
    pub fn default_font_size_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Experiment {
    #[serde(default, rename = "@Type")]
    pub r#type: Option<ExperimentType>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "ExperimenterRef")]
    pub experimenter_ref: Option<AnnotationRef>,
    #[serde(default, rename = "MicrobeamManipulation")]
    pub microbeam_manipulation: Vec<MicrobeamManipulation>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ExperimentItemType {
    #[serde(rename = "FP")]
    Fp,
    #[serde(rename = "FRET")]
    Fret,
    #[serde(rename = "TimeLapse")]
    TimeLapse,
    #[serde(rename = "FourDPlus")]
    FourDPlus,
    #[serde(rename = "Screen")]
    Screen,
    #[serde(rename = "Immunocytochemistry")]
    Immunocytochemistry,
    #[serde(rename = "Immunofluorescence")]
    Immunofluorescence,
    #[serde(rename = "FISH")]
    Fish,
    #[serde(rename = "Electrophysiology")]
    Electrophysiology,
    #[serde(rename = "IonImaging")]
    IonImaging,
    #[serde(rename = "Colocalization")]
    Colocalization,
    #[serde(rename = "PGIDocumentation")]
    PgiDocumentation,
    #[serde(rename = "FluorescenceLifetime")]
    FluorescenceLifetime,
    #[serde(rename = "SpectralImaging")]
    SpectralImaging,
    #[serde(rename = "Photobleaching")]
    Photobleaching,
    #[serde(rename = "SPIM")]
    Spim,
    #[serde(rename = "Other")]
    Other,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize, Default)]
pub struct ExperimentType(pub Vec<ExperimentItemType>);
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Experimenter {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@FirstName")]
    pub first_name: Option<String>,
    #[serde(default, rename = "@MiddleName")]
    pub middle_name: Option<String>,
    #[serde(default, rename = "@LastName")]
    pub last_name: Option<String>,
    #[serde(default, rename = "@Email")]
    pub email: Option<String>,
    #[serde(default, rename = "@Institution")]
    pub institution: Option<String>,
    #[serde(default, rename = "@UserName")]
    pub user_name: Option<String>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ExperimenterGroup {
    #[serde(default, rename = "@Name")]
    pub name: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "ExperimenterRef")]
    pub experimenter_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "Leader")]
    pub leader: Vec<AnnotationRef>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct External {
    #[serde(rename = "@href")]
    pub href: String,
    #[serde(rename = "@SHA1")]
    pub sha_1: String,
    #[serde(default = "External::default_compression", rename = "@Compression")]
    pub compression: BinDataCompressionType,
}
impl External {
    pub fn default_compression() -> BinDataCompressionType {
        BinDataCompressionType::None
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Filament {
    #[serde(default, rename = "@Manufacturer")]
    pub manufacturer: Option<String>,
    #[serde(default, rename = "@Model")]
    pub model: Option<String>,
    #[serde(default, rename = "@SerialNumber")]
    pub serial_number: Option<String>,
    #[serde(default, rename = "@LotNumber")]
    pub lot_number: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Power")]
    pub power: Option<f32>,
    #[serde(default = "Filament::default_power_unit", rename = "@PowerUnit")]
    pub power_unit: UnitsPower,
    #[serde(default, rename = "@Type")]
    pub r#type: Option<FilamentType>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl Filament {
    pub fn default_power_unit() -> UnitsPower {
        UnitsPower::W
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum FilamentType {
    #[serde(rename = "Incandescent")]
    Incandescent,
    #[serde(rename = "Halogen")]
    Halogen,
    #[serde(rename = "Other")]
    Other,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FileAnnotation {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Namespace")]
    pub namespace: Option<String>,
    #[serde(default, rename = "@Annotator")]
    pub annotator: Option<String>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
    #[serde(rename = "BinaryFile")]
    pub binary_file: BinaryFile,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Filter {
    #[serde(default, rename = "@Manufacturer")]
    pub manufacturer: Option<String>,
    #[serde(default, rename = "@Model")]
    pub model: Option<String>,
    #[serde(default, rename = "@SerialNumber")]
    pub serial_number: Option<String>,
    #[serde(default, rename = "@LotNumber")]
    pub lot_number: Option<String>,
    #[serde(default, rename = "@Type")]
    pub r#type: Option<FilterType>,
    #[serde(default, rename = "@FilterWheel")]
    pub filter_wheel: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "TransmittanceRange")]
    pub transmittance_range: Option<TransmittanceRange>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FilterSet {
    #[serde(default, rename = "@Manufacturer")]
    pub manufacturer: Option<String>,
    #[serde(default, rename = "@Model")]
    pub model: Option<String>,
    #[serde(default, rename = "@SerialNumber")]
    pub serial_number: Option<String>,
    #[serde(default, rename = "@LotNumber")]
    pub lot_number: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "ExcitationFilterRef")]
    pub excitation_filter_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "DichroicRef")]
    pub dichroic_ref: Option<AnnotationRef>,
    #[serde(default, rename = "EmissionFilterRef")]
    pub emission_filter_ref: Vec<AnnotationRef>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum FilterType {
    #[serde(rename = "Dichroic")]
    Dichroic,
    #[serde(rename = "LongPass")]
    LongPass,
    #[serde(rename = "ShortPass")]
    ShortPass,
    #[serde(rename = "BandPass")]
    BandPass,
    #[serde(rename = "MultiPass")]
    MultiPass,
    #[serde(rename = "NeutralDensity")]
    NeutralDensity,
    #[serde(rename = "Tuneable")]
    Tuneable,
    #[serde(rename = "Other")]
    Other,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Folder {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Name")]
    pub name: Option<String>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "FolderRef")]
    pub folder_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "ImageRef")]
    pub image_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "ROIRef")]
    pub roi_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum FontFamilyType {
    #[serde(rename = "serif")]
    Serif,
    #[serde(rename = "sans-serif")]
    SansSerif,
    #[serde(rename = "cursive")]
    Cursive,
    #[serde(rename = "fantasy")]
    Fantasy,
    #[serde(rename = "monospace")]
    Monospace,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GenericExcitationSource {
    #[serde(default, rename = "@Manufacturer")]
    pub manufacturer: Option<String>,
    #[serde(default, rename = "@Model")]
    pub model: Option<String>,
    #[serde(default, rename = "@SerialNumber")]
    pub serial_number: Option<String>,
    #[serde(default, rename = "@LotNumber")]
    pub lot_number: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Power")]
    pub power: Option<f32>,
    #[serde(
        default = "GenericExcitationSource::default_power_unit",
        rename = "@PowerUnit"
    )]
    pub power_unit: UnitsPower,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "Map")]
    pub map: Option<MapType>,
}
impl GenericExcitationSource {
    pub fn default_power_unit() -> UnitsPower {
        UnitsPower::W
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Image {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Name")]
    pub name: Option<String>,
    #[serde(default, rename = "AcquisitionDate")]
    pub acquisition_date: Option<String>,
    #[serde(default, rename = "ExperimenterRef")]
    pub experimenter_ref: Option<AnnotationRef>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "ExperimentRef")]
    pub experiment_ref: Option<AnnotationRef>,
    #[serde(default, rename = "ExperimenterGroupRef")]
    pub experimenter_group_ref: Option<AnnotationRef>,
    #[serde(default, rename = "InstrumentRef")]
    pub instrument_ref: Option<AnnotationRef>,
    #[serde(default, rename = "ObjectiveSettings")]
    pub objective_settings: Option<ObjectiveSettings>,
    #[serde(default, rename = "ImagingEnvironment")]
    pub imaging_environment: Option<ImagingEnvironment>,
    #[serde(default, rename = "StageLabel")]
    pub stage_label: Option<StageLabel>,
    #[serde(rename = "Pixels")]
    pub pixels: Pixels,
    #[serde(default, rename = "ROIRef")]
    pub roi_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "MicrobeamManipulationRef")]
    pub microbeam_manipulation_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ImagingEnvironment {
    #[serde(default, rename = "@Temperature")]
    pub temperature: Option<f32>,
    #[serde(
        default = "ImagingEnvironment::default_temperature_unit",
        rename = "@TemperatureUnit"
    )]
    pub temperature_unit: UnitsTemperature,
    #[serde(default, rename = "@AirPressure")]
    pub air_pressure: Option<f32>,
    #[serde(
        default = "ImagingEnvironment::default_air_pressure_unit",
        rename = "@AirPressureUnit"
    )]
    pub air_pressure_unit: UnitsPressure,
    #[serde(default, rename = "@Humidity")]
    pub humidity: Option<f32>,
    #[serde(default, rename = "@CO2Percent")]
    pub co_2_percent: Option<f32>,
    #[serde(default, rename = "Map")]
    pub map: Option<MapType>,
}
impl ImagingEnvironment {
    pub fn default_temperature_unit() -> UnitsTemperature {
        UnitsTemperature::C
    }
    pub fn default_air_pressure_unit() -> UnitsPressure {
        UnitsPressure::atm
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Instrument {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "Microscope")]
    pub microscope: Option<Microscope>,
    #[serde(default, rename = "LightSourceGroup")]
    pub light_source_group: Vec<LightSourceGroup>,
    #[serde(default, rename = "Detector")]
    pub detector: Vec<Detector>,
    #[serde(default, rename = "Objective")]
    pub objective: Vec<Objective>,
    #[serde(default, rename = "FilterSet")]
    pub filter_set: Vec<FilterSet>,
    #[serde(default, rename = "Filter")]
    pub filter: Vec<Filter>,
    #[serde(default, rename = "Dichroic")]
    pub dichroic: Vec<Dichroic>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Label {
    #[serde(default, rename = "@FillColor")]
    pub fill_color: Option<i32>,
    #[serde(default, rename = "@FillRule")]
    pub fill_rule: Option<ShapeFillRuleType>,
    #[serde(default, rename = "@StrokeColor")]
    pub stroke_color: Option<i32>,
    #[serde(default, rename = "@StrokeWidth")]
    pub stroke_width: Option<f32>,
    #[serde(
        default = "Label::default_stroke_width_unit",
        rename = "@StrokeWidthUnit"
    )]
    pub stroke_width_unit: UnitsLength,
    #[serde(default, rename = "@StrokeDashArray")]
    pub stroke_dash_array: Option<String>,
    #[serde(default, rename = "@Text")]
    pub text: Option<String>,
    #[serde(default, rename = "@FontFamily")]
    pub font_family: Option<FontFamilyType>,
    #[serde(default, rename = "@FontSize")]
    pub font_size: Option<i32>,
    #[serde(default = "Label::default_font_size_unit", rename = "@FontSizeUnit")]
    pub font_size_unit: UnitsLength,
    #[serde(default, rename = "@FontStyle")]
    pub font_style: Option<ShapeFontStyleType>,
    #[serde(default, rename = "@Locked")]
    pub locked: Option<bool>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@TheZ")]
    pub the_z: Option<i32>,
    #[serde(default, rename = "@TheT")]
    pub the_t: Option<i32>,
    #[serde(default, rename = "@TheC")]
    pub the_c: Option<i32>,
    #[serde(rename = "@X")]
    pub x: f32,
    #[serde(rename = "@Y")]
    pub y: f32,
    #[serde(default, rename = "Transform")]
    pub transform: Option<AffineTransform>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl Label {
    pub fn default_stroke_width_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
    pub fn default_font_size_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Laser {
    #[serde(default, rename = "@Manufacturer")]
    pub manufacturer: Option<String>,
    #[serde(default, rename = "@Model")]
    pub model: Option<String>,
    #[serde(default, rename = "@SerialNumber")]
    pub serial_number: Option<String>,
    #[serde(default, rename = "@LotNumber")]
    pub lot_number: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Power")]
    pub power: Option<f32>,
    #[serde(default = "Laser::default_power_unit", rename = "@PowerUnit")]
    pub power_unit: UnitsPower,
    #[serde(default, rename = "@Type")]
    pub r#type: Option<LaserType>,
    #[serde(default, rename = "@LaserMedium")]
    pub laser_medium: Option<LaserLaserMediumType>,
    #[serde(default, rename = "@Wavelength")]
    pub wavelength: Option<f32>,
    #[serde(default = "Laser::default_wavelength_unit", rename = "@WavelengthUnit")]
    pub wavelength_unit: UnitsLength,
    #[serde(default, rename = "@FrequencyMultiplication")]
    pub frequency_multiplication: Option<i32>,
    #[serde(default, rename = "@Tuneable")]
    pub tuneable: Option<bool>,
    #[serde(default, rename = "@Pulse")]
    pub pulse: Option<LaserPulseType>,
    #[serde(default, rename = "@PockelCell")]
    pub pockel_cell: Option<bool>,
    #[serde(default, rename = "@RepetitionRate")]
    pub repetition_rate: Option<f32>,
    #[serde(
        default = "Laser::default_repetition_rate_unit",
        rename = "@RepetitionRateUnit"
    )]
    pub repetition_rate_unit: UnitsFrequency,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "Pump")]
    pub pump: Option<AnnotationRef>,
}
impl Laser {
    pub fn default_power_unit() -> UnitsPower {
        UnitsPower::mW
    }
    pub fn default_wavelength_unit() -> UnitsLength {
        UnitsLength::nm
    }
    pub fn default_repetition_rate_unit() -> UnitsFrequency {
        UnitsFrequency::Hz
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum LaserLaserMediumType {
    #[serde(rename = "Cu")]
    Cu,
    #[serde(rename = "Ag")]
    Ag,
    #[serde(rename = "ArFl")]
    ArFl,
    #[serde(rename = "ArCl")]
    ArCl,
    #[serde(rename = "KrFl")]
    KrFl,
    #[serde(rename = "KrCl")]
    KrCl,
    #[serde(rename = "XeFl")]
    XeFl,
    #[serde(rename = "XeCl")]
    XeCl,
    #[serde(rename = "XeBr")]
    XeBr,
    #[serde(rename = "N")]
    N,
    #[serde(rename = "Ar")]
    Ar,
    #[serde(rename = "Kr")]
    Kr,
    #[serde(rename = "Xe")]
    Xe,
    #[serde(rename = "HeNe")]
    HeNe,
    #[serde(rename = "HeCd")]
    HeCd,
    #[serde(rename = "CO")]
    Co,
    #[serde(rename = "CO2")]
    Co2,
    #[serde(rename = "H2O")]
    H2O,
    #[serde(rename = "HFl")]
    Hfl,
    #[serde(rename = "NdGlass")]
    NdGlass,
    #[serde(rename = "NdYAG")]
    NdYag,
    #[serde(rename = "ErGlass")]
    ErGlass,
    #[serde(rename = "ErYAG")]
    ErYag,
    #[serde(rename = "HoYLF")]
    HoYlf,
    #[serde(rename = "HoYAG")]
    HoYag,
    #[serde(rename = "Ruby")]
    Ruby,
    #[serde(rename = "TiSapphire")]
    TiSapphire,
    #[serde(rename = "Alexandrite")]
    Alexandrite,
    #[serde(rename = "Rhodamine6G")]
    Rhodamine6G,
    #[serde(rename = "CoumarinC30")]
    CoumarinC30,
    #[serde(rename = "GaAs")]
    GaAs,
    #[serde(rename = "GaAlAs")]
    GaAlAs,
    #[serde(rename = "EMinus")]
    Eminus,
    #[serde(rename = "Other")]
    Other,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum LaserPulseType {
    #[serde(rename = "CW")]
    Cw,
    #[serde(rename = "Single")]
    Single,
    #[serde(rename = "QSwitched")]
    Qswitched,
    #[serde(rename = "Repetitive")]
    Repetitive,
    #[serde(rename = "ModeLocked")]
    ModeLocked,
    #[serde(rename = "Other")]
    Other,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum LaserType {
    #[serde(rename = "Excimer")]
    Excimer,
    #[serde(rename = "Gas")]
    Gas,
    #[serde(rename = "MetalVapor")]
    MetalVapor,
    #[serde(rename = "SolidState")]
    SolidState,
    #[serde(rename = "Dye")]
    Dye,
    #[serde(rename = "Semiconductor")]
    Semiconductor,
    #[serde(rename = "FreeElectron")]
    FreeElectron,
    #[serde(rename = "Other")]
    Other,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LightEmittingDiode {
    #[serde(default, rename = "@Manufacturer")]
    pub manufacturer: Option<String>,
    #[serde(default, rename = "@Model")]
    pub model: Option<String>,
    #[serde(default, rename = "@SerialNumber")]
    pub serial_number: Option<String>,
    #[serde(default, rename = "@LotNumber")]
    pub lot_number: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Power")]
    pub power: Option<f32>,
    #[serde(
        default = "LightEmittingDiode::default_power_unit",
        rename = "@PowerUnit"
    )]
    pub power_unit: UnitsPower,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl LightEmittingDiode {
    pub fn default_power_unit() -> UnitsPower {
        UnitsPower::mW
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LightPath {
    #[serde(default, rename = "ExcitationFilterRef")]
    pub excitation_filter_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "DichroicRef")]
    pub dichroic_ref: Option<AnnotationRef>,
    #[serde(default, rename = "EmissionFilterRef")]
    pub emission_filter_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LightSourceType {
    #[serde(default, rename = "@Manufacturer")]
    pub manufacturer: Option<String>,
    #[serde(default, rename = "@Model")]
    pub model: Option<String>,
    #[serde(default, rename = "@SerialNumber")]
    pub serial_number: Option<String>,
    #[serde(default, rename = "@LotNumber")]
    pub lot_number: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Power")]
    pub power: Option<f32>,
    #[serde(default = "LightSourceType::default_power_unit", rename = "@PowerUnit")]
    pub power_unit: UnitsPower,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl LightSourceType {
    pub fn default_power_unit() -> UnitsPower {
        UnitsPower::mW
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum LightSourceGroup {
    #[serde(rename = "Laser")]
    Laser(Laser),
    #[serde(rename = "Arc")]
    Arc(Arc),
    #[serde(rename = "Filament")]
    Filament(Filament),
    #[serde(rename = "LightEmittingDiode")]
    LightEmittingDiode(LightEmittingDiode),
    #[serde(rename = "GenericExcitationSource")]
    GenericExcitationSource(GenericExcitationSource),
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LightSourceSettings {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Attenuation")]
    pub attenuation: Option<f32>,
    #[serde(default, rename = "@Wavelength")]
    pub wavelength: Option<f32>,
    #[serde(
        default = "LightSourceSettings::default_wavelength_unit",
        rename = "@WavelengthUnit"
    )]
    pub wavelength_unit: UnitsLength,
}
impl LightSourceSettings {
    pub fn default_wavelength_unit() -> UnitsLength {
        UnitsLength::nm
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Line {
    #[serde(default, rename = "@FillColor")]
    pub fill_color: Option<i32>,
    #[serde(default, rename = "@FillRule")]
    pub fill_rule: Option<ShapeFillRuleType>,
    #[serde(default, rename = "@StrokeColor")]
    pub stroke_color: Option<i32>,
    #[serde(default, rename = "@StrokeWidth")]
    pub stroke_width: Option<f32>,
    #[serde(
        default = "Line::default_stroke_width_unit",
        rename = "@StrokeWidthUnit"
    )]
    pub stroke_width_unit: UnitsLength,
    #[serde(default, rename = "@StrokeDashArray")]
    pub stroke_dash_array: Option<String>,
    #[serde(default, rename = "@Text")]
    pub text: Option<String>,
    #[serde(default, rename = "@FontFamily")]
    pub font_family: Option<FontFamilyType>,
    #[serde(default, rename = "@FontSize")]
    pub font_size: Option<i32>,
    #[serde(default = "Line::default_font_size_unit", rename = "@FontSizeUnit")]
    pub font_size_unit: UnitsLength,
    #[serde(default, rename = "@FontStyle")]
    pub font_style: Option<ShapeFontStyleType>,
    #[serde(default, rename = "@Locked")]
    pub locked: Option<bool>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@TheZ")]
    pub the_z: Option<i32>,
    #[serde(default, rename = "@TheT")]
    pub the_t: Option<i32>,
    #[serde(default, rename = "@TheC")]
    pub the_c: Option<i32>,
    #[serde(rename = "@X1")]
    pub x1: f32,
    #[serde(rename = "@Y1")]
    pub y1: f32,
    #[serde(rename = "@X2")]
    pub x2: f32,
    #[serde(rename = "@Y2")]
    pub y2: f32,
    #[serde(default, rename = "@MarkerStart")]
    pub marker_start: Option<MarkerType>,
    #[serde(default, rename = "@MarkerEnd")]
    pub marker_end: Option<MarkerType>,
    #[serde(default, rename = "Transform")]
    pub transform: Option<AffineTransform>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl Line {
    pub fn default_stroke_width_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
    pub fn default_font_size_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LongAnnotation {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Namespace")]
    pub namespace: Option<String>,
    #[serde(default, rename = "@Annotator")]
    pub annotator: Option<String>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
    #[serde(rename = "Value")]
    pub value: i64,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MapType {
    #[serde(default, rename = "M")]
    pub m: Vec<MapM>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MapAnnotation {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Namespace")]
    pub namespace: Option<String>,
    #[serde(default, rename = "@Annotator")]
    pub annotator: Option<String>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
    #[serde(rename = "Value")]
    pub value: MapType,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MapM {
    #[serde(default, rename = "@K")]
    pub k: Option<String>,
    #[serde(rename = "$text")]
    pub content: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum MarkerType {
    #[serde(rename = "Arrow")]
    Arrow,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Mask {
    #[serde(default, rename = "@FillColor")]
    pub fill_color: Option<i32>,
    #[serde(default, rename = "@FillRule")]
    pub fill_rule: Option<ShapeFillRuleType>,
    #[serde(default, rename = "@StrokeColor")]
    pub stroke_color: Option<i32>,
    #[serde(default, rename = "@StrokeWidth")]
    pub stroke_width: Option<f32>,
    #[serde(
        default = "Mask::default_stroke_width_unit",
        rename = "@StrokeWidthUnit"
    )]
    pub stroke_width_unit: UnitsLength,
    #[serde(default, rename = "@StrokeDashArray")]
    pub stroke_dash_array: Option<String>,
    #[serde(default, rename = "@Text")]
    pub text: Option<String>,
    #[serde(default, rename = "@FontFamily")]
    pub font_family: Option<FontFamilyType>,
    #[serde(default, rename = "@FontSize")]
    pub font_size: Option<i32>,
    #[serde(default = "Mask::default_font_size_unit", rename = "@FontSizeUnit")]
    pub font_size_unit: UnitsLength,
    #[serde(default, rename = "@FontStyle")]
    pub font_style: Option<ShapeFontStyleType>,
    #[serde(default, rename = "@Locked")]
    pub locked: Option<bool>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@TheZ")]
    pub the_z: Option<i32>,
    #[serde(default, rename = "@TheT")]
    pub the_t: Option<i32>,
    #[serde(default, rename = "@TheC")]
    pub the_c: Option<i32>,
    #[serde(rename = "@X")]
    pub x: f32,
    #[serde(rename = "@Y")]
    pub y: f32,
    #[serde(rename = "@Width")]
    pub width: f32,
    #[serde(rename = "@Height")]
    pub height: f32,
    #[serde(default, rename = "Transform")]
    pub transform: Option<AffineTransform>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
    #[serde(rename = "BinData")]
    pub bin_data: BinData,
}
impl Mask {
    pub fn default_stroke_width_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
    pub fn default_font_size_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MetadataOnly;
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MicrobeamManipulation {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Type")]
    pub r#type: Option<MicrobeamManipulationType>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "ROIRef")]
    pub roi_ref: Vec<AnnotationRef>,
    #[serde(rename = "ExperimenterRef")]
    pub experimenter_ref: AnnotationRef,
    #[serde(default, rename = "LightSourceSettings")]
    pub light_source_settings: Vec<LightSourceSettings>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum MicrobeamManipulationItemType {
    #[serde(rename = "FRAP")]
    Frap,
    #[serde(rename = "FLIP")]
    Flip,
    #[serde(rename = "InverseFRAP")]
    InverseFrap,
    #[serde(rename = "Photoablation")]
    Photoablation,
    #[serde(rename = "Photoactivation")]
    Photoactivation,
    #[serde(rename = "Uncaging")]
    Uncaging,
    #[serde(rename = "OpticalTrapping")]
    OpticalTrapping,
    #[serde(rename = "Other")]
    Other,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize, Default)]
pub struct MicrobeamManipulationType(pub Vec<MicrobeamManipulationItemType>);
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Microscope {
    #[serde(default, rename = "@Manufacturer")]
    pub manufacturer: Option<String>,
    #[serde(default, rename = "@Model")]
    pub model: Option<String>,
    #[serde(default, rename = "@SerialNumber")]
    pub serial_number: Option<String>,
    #[serde(default, rename = "@LotNumber")]
    pub lot_number: Option<String>,
    #[serde(default, rename = "@Type")]
    pub r#type: Option<MicroscopeType>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum MicroscopeType {
    #[serde(rename = "Upright")]
    Upright,
    #[serde(rename = "Inverted")]
    Inverted,
    #[serde(rename = "Dissection")]
    Dissection,
    #[serde(rename = "Electrophysiology")]
    Electrophysiology,
    #[serde(rename = "Other")]
    Other,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum NamingConventionType {
    #[serde(rename = "letter")]
    Letter,
    #[serde(rename = "number")]
    Number,
}

/// The root of the metadata, create this by parsing an XML string.
/// ```
/// use ome_metadata::Ome;
///
/// let xml = r#"<OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06 http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd">
///   <Image ID="Image:0" Name="test.tif">
///     <AcquisitionDate>2025-01-29T14:42:42</AcquisitionDate>
///     <Description/>
///     <Pixels ID="Pixels:0" DimensionOrder="XYCZT" Type="int8" SignificantBits="8" Interleaved="false" BigEndian="false" SizeX="2" SizeY="2" SizeZ="1" SizeC="1" SizeT="1">
///       <Channel ID="Channel:0:0" SamplesPerPixel="1">
///         <LightPath/>
///       </Channel>
///       <MetadataOnly/>
///     </Pixels>
///   </Image>
/// </OME>"#;
///
/// let ome: Ome = xml.parse().unwrap();
/// let image = &ome.image.unwrap()[0];
/// println!("acquisition date: {:#?}", image.acquisition_date);
/// ```
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Ome {
    #[serde(default, rename = "@UUID")]
    pub uuid: Option<String>,
    #[serde(default, rename = "@Creator")]
    pub creator: Option<String>,
    #[serde(rename = "Rights")]
    pub rights: Option<Rights>,
    #[serde(rename = "Project")]
    pub project: Option<Vec<Project>>,
    #[serde(rename = "Dataset")]
    pub dataset: Option<Vec<Dataset>>,
    #[serde(rename = "Folder")]
    pub folder: Option<Vec<Folder>>,
    #[serde(rename = "Experiment")]
    pub experiment: Option<Vec<Experiment>>,
    #[serde(rename = "Plate")]
    pub plate: Option<Vec<Plate>>,
    #[serde(rename = "Screen")]
    pub screen: Option<Vec<Screen>>,
    #[serde(rename = "Experimenter")]
    pub experimenter: Option<Vec<Experimenter>>,
    #[serde(rename = "ExperimenterGroup")]
    pub experimenter_group: Option<Vec<ExperimenterGroup>>,
    #[serde(rename = "Instrument")]
    pub instrument: Option<Vec<Instrument>>,
    #[serde(rename = "Image")]
    pub image: Option<Vec<Image>>,
    #[serde(rename = "StructuredAnnotations")]
    pub structured_annotations: Option<StructuredAnnotations>,
    #[serde(rename = "ROI")]
    pub roi: Option<Vec<Roi>>,
    #[serde(rename = "BinaryOnly")]
    pub binary_only: Option<OmeBinaryOnly>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Objective {
    #[serde(default, rename = "@Manufacturer")]
    pub manufacturer: Option<String>,
    #[serde(default, rename = "@Model")]
    pub model: Option<String>,
    #[serde(default, rename = "@SerialNumber")]
    pub serial_number: Option<String>,
    #[serde(default, rename = "@LotNumber")]
    pub lot_number: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Correction")]
    pub correction: Option<ObjectiveCorrectionType>,
    #[serde(default, rename = "@Immersion")]
    pub immersion: Option<ObjectiveImmersionType>,
    #[serde(default, rename = "@LensNA")]
    pub lens_na: Option<f32>,
    #[serde(default, rename = "@NominalMagnification")]
    pub nominal_magnification: Option<f32>,
    #[serde(default, rename = "@CalibratedMagnification")]
    pub calibrated_magnification: Option<f32>,
    #[serde(default, rename = "@WorkingDistance")]
    pub working_distance: Option<f32>,
    #[serde(
        default = "Objective::default_working_distance_unit",
        rename = "@WorkingDistanceUnit"
    )]
    pub working_distance_unit: UnitsLength,
    #[serde(default, rename = "@Iris")]
    pub iris: Option<bool>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl Objective {
    pub fn default_working_distance_unit() -> UnitsLength {
        UnitsLength::um
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ObjectiveCorrectionType {
    #[serde(rename = "UV")]
    Uv,
    #[serde(rename = "PlanApo")]
    PlanApo,
    #[serde(rename = "PlanFluor")]
    PlanFluor,
    #[serde(rename = "SuperFluor")]
    SuperFluor,
    #[serde(rename = "VioletCorrected")]
    VioletCorrected,
    #[serde(rename = "Achro")]
    Achro,
    #[serde(rename = "Achromat")]
    Achromat,
    #[serde(rename = "Fluor")]
    Fluor,
    #[serde(rename = "Fl")]
    Fl,
    #[serde(rename = "Fluar")]
    Fluar,
    #[serde(rename = "Neofluar")]
    Neofluar,
    #[serde(rename = "Fluotar")]
    Fluotar,
    #[serde(rename = "Apo")]
    Apo,
    #[serde(rename = "PlanNeofluar")]
    PlanNeofluar,
    #[serde(rename = "Other")]
    Other,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ObjectiveImmersionType {
    #[serde(rename = "Oil")]
    Oil,
    #[serde(rename = "Water")]
    Water,
    #[serde(rename = "WaterDipping")]
    WaterDipping,
    #[serde(rename = "Air")]
    Air,
    #[serde(rename = "Multi")]
    Multi,
    #[serde(rename = "Glycerol")]
    Glycerol,
    #[serde(rename = "Other")]
    Other,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ObjectiveSettings {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@CorrectionCollar")]
    pub correction_collar: Option<f32>,
    #[serde(default, rename = "@Medium")]
    pub medium: Option<ObjectiveSettingsMediumType>,
    #[serde(default, rename = "@RefractiveIndex")]
    pub refractive_index: Option<f32>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ObjectiveSettingsMediumType {
    #[serde(rename = "Air")]
    Air,
    #[serde(rename = "Oil")]
    Oil,
    #[serde(rename = "Water")]
    Water,
    #[serde(rename = "Glycerol")]
    Glycerol,
    #[serde(rename = "Other")]
    Other,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct OmeBinaryOnly {
    #[serde(rename = "@MetadataFile")]
    pub metadata_file: String,
    #[serde(rename = "@UUID")]
    pub uuid: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum PixelType {
    #[serde(rename = "int8")]
    Int8,
    #[serde(rename = "int16")]
    Int16,
    #[serde(rename = "int32")]
    Int32,
    #[serde(rename = "uint8")]
    Uint8,
    #[serde(rename = "uint16")]
    Uint16,
    #[serde(rename = "uint32")]
    Uint32,
    #[serde(rename = "float")]
    Float,
    #[serde(rename = "double")]
    Double,
    #[serde(rename = "complex")]
    Complex,
    #[serde(rename = "double-complex")]
    DoubleComplex,
    #[serde(rename = "bit")]
    Bit,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Pixels {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(rename = "@DimensionOrder")]
    pub dimension_order: PixelsDimensionOrderType,
    #[serde(rename = "@Type")]
    pub r#type: PixelType,
    #[serde(default, rename = "@SignificantBits")]
    pub significant_bits: Option<i32>,
    #[serde(default, rename = "@Interleaved")]
    pub interleaved: Option<bool>,
    #[serde(default, rename = "@BigEndian")]
    pub big_endian: Option<bool>,
    #[serde(rename = "@SizeX")]
    pub size_x: i32,
    #[serde(rename = "@SizeY")]
    pub size_y: i32,
    #[serde(rename = "@SizeZ")]
    pub size_z: i32,
    #[serde(rename = "@SizeC")]
    pub size_c: i32,
    #[serde(rename = "@SizeT")]
    pub size_t: i32,
    #[serde(default, rename = "@PhysicalSizeX")]
    pub physical_size_x: Option<f32>,
    #[serde(
        default = "Pixels::default_physical_size_x_unit",
        rename = "@PhysicalSizeXUnit"
    )]
    pub physical_size_x_unit: UnitsLength,
    #[serde(default, rename = "@PhysicalSizeY")]
    pub physical_size_y: Option<f32>,
    #[serde(
        default = "Pixels::default_physical_size_y_unit",
        rename = "@PhysicalSizeYUnit"
    )]
    pub physical_size_y_unit: UnitsLength,
    #[serde(default, rename = "@PhysicalSizeZ")]
    pub physical_size_z: Option<f32>,
    #[serde(
        default = "Pixels::default_physical_size_z_unit",
        rename = "@PhysicalSizeZUnit"
    )]
    pub physical_size_z_unit: UnitsLength,
    #[serde(default, rename = "@TimeIncrement")]
    pub time_increment: Option<f32>,
    #[serde(
        default = "Pixels::default_time_increment_unit",
        rename = "@TimeIncrementUnit"
    )]
    pub time_increment_unit: UnitsTime,
    #[serde(rename = "Channel")]
    pub channel: Option<Vec<Channel>>,
    #[serde(rename = "BinData")]
    pub bin_data: Option<Vec<BinData>>,
    #[serde(rename = "TiffData")]
    pub tiff_data: Option<Vec<TiffData>>,
    #[serde(rename = "MetadataOnly")]
    pub metadata_only: Option<MetadataOnly>,
    #[serde(rename = "Plane")]
    pub plane: Option<Vec<Plane>>,
}
impl Pixels {
    pub fn default_physical_size_x_unit() -> UnitsLength {
        UnitsLength::um
    }
    pub fn default_physical_size_y_unit() -> UnitsLength {
        UnitsLength::um
    }
    pub fn default_physical_size_z_unit() -> UnitsLength {
        UnitsLength::um
    }
    pub fn default_time_increment_unit() -> UnitsTime {
        UnitsTime::s
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum PixelsDimensionOrderType {
    #[serde(rename = "XYZCT")]
    Xyzct,
    #[serde(rename = "XYZTC")]
    Xyztc,
    #[serde(rename = "XYCTZ")]
    Xyctz,
    #[serde(rename = "XYCZT")]
    Xyczt,
    #[serde(rename = "XYTCZ")]
    Xytcz,
    #[serde(rename = "XYTZC")]
    Xytzc,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Plane {
    #[serde(rename = "@TheZ")]
    pub the_z: i32,
    #[serde(rename = "@TheT")]
    pub the_t: i32,
    #[serde(rename = "@TheC")]
    pub the_c: i32,
    #[serde(default, rename = "@DeltaT")]
    pub delta_t: Option<f32>,
    #[serde(default = "Plane::default_delta_t_unit", rename = "@DeltaTUnit")]
    pub delta_t_unit: UnitsTime,
    #[serde(default, rename = "@ExposureTime")]
    pub exposure_time: Option<f32>,
    #[serde(
        default = "Plane::default_exposure_time_unit",
        rename = "@ExposureTimeUnit"
    )]
    pub exposure_time_unit: UnitsTime,
    #[serde(default, rename = "@PositionX")]
    pub position_x: Option<f32>,
    #[serde(default = "Plane::default_position_x_unit", rename = "@PositionXUnit")]
    pub position_x_unit: UnitsLength,
    #[serde(default, rename = "@PositionY")]
    pub position_y: Option<f32>,
    #[serde(default = "Plane::default_position_y_unit", rename = "@PositionYUnit")]
    pub position_y_unit: UnitsLength,
    #[serde(default, rename = "@PositionZ")]
    pub position_z: Option<f32>,
    #[serde(default = "Plane::default_position_z_unit", rename = "@PositionZUnit")]
    pub position_z_unit: UnitsLength,
    #[serde(rename = "HashSHA1")]
    pub hash_sha1: Option<String>,
    #[serde(rename = "AnnotationRef")]
    pub annotation_ref: Option<AnnotationRef>,
}
impl Plane {
    pub fn default_delta_t_unit() -> UnitsTime {
        UnitsTime::s
    }
    pub fn default_exposure_time_unit() -> UnitsTime {
        UnitsTime::s
    }
    pub fn default_position_x_unit() -> UnitsLength {
        UnitsLength::um
    }
    pub fn default_position_y_unit() -> UnitsLength {
        UnitsLength::um
    }
    pub fn default_position_z_unit() -> UnitsLength {
        UnitsLength::um
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Plate {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Name")]
    pub name: Option<String>,
    #[serde(default, rename = "@Status")]
    pub status: Option<String>,
    #[serde(default, rename = "@ExternalIdentifier")]
    pub external_identifier: Option<String>,
    #[serde(default, rename = "@ColumnNamingConvention")]
    pub column_naming_convention: Option<NamingConventionType>,
    #[serde(default, rename = "@RowNamingConvention")]
    pub row_naming_convention: Option<NamingConventionType>,
    #[serde(default, rename = "@WellOriginX")]
    pub well_origin_x: Option<f32>,
    #[serde(
        default = "Plate::default_well_origin_x_unit",
        rename = "@WellOriginXUnit"
    )]
    pub well_origin_x_unit: UnitsLength,
    #[serde(default, rename = "@WellOriginY")]
    pub well_origin_y: Option<f32>,
    #[serde(
        default = "Plate::default_well_origin_y_unit",
        rename = "@WellOriginYUnit"
    )]
    pub well_origin_y_unit: UnitsLength,
    #[serde(default, rename = "@Rows")]
    pub rows: Option<i32>,
    #[serde(default, rename = "@Columns")]
    pub columns: Option<i32>,
    #[serde(default, rename = "@FieldIndex")]
    pub field_index: Option<i32>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "Well")]
    pub well: Vec<Well>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "PlateAcquisition")]
    pub plate_acquisition: Vec<PlateAcquisition>,
}
impl Plate {
    pub fn default_well_origin_x_unit() -> UnitsLength {
        UnitsLength::um
    }
    pub fn default_well_origin_y_unit() -> UnitsLength {
        UnitsLength::um
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PlateAcquisition {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Name")]
    pub name: Option<String>,
    #[serde(default, rename = "@EndTime")]
    pub end_time: Option<String>,
    #[serde(default, rename = "@StartTime")]
    pub start_time: Option<String>,
    #[serde(default, rename = "@MaximumFieldCount")]
    pub maximum_field_count: Option<i32>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "WellSampleRef")]
    pub well_sample_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Polygon {
    #[serde(default, rename = "@FillColor")]
    pub fill_color: Option<i32>,
    #[serde(default, rename = "@FillRule")]
    pub fill_rule: Option<ShapeFillRuleType>,
    #[serde(default, rename = "@StrokeColor")]
    pub stroke_color: Option<i32>,
    #[serde(default, rename = "@StrokeWidth")]
    pub stroke_width: Option<f32>,
    #[serde(
        default = "Polygon::default_stroke_width_unit",
        rename = "@StrokeWidthUnit"
    )]
    pub stroke_width_unit: UnitsLength,
    #[serde(default, rename = "@StrokeDashArray")]
    pub stroke_dash_array: Option<String>,
    #[serde(default, rename = "@Text")]
    pub text: Option<String>,
    #[serde(default, rename = "@FontFamily")]
    pub font_family: Option<FontFamilyType>,
    #[serde(default, rename = "@FontSize")]
    pub font_size: Option<i32>,
    #[serde(default = "Polygon::default_font_size_unit", rename = "@FontSizeUnit")]
    pub font_size_unit: UnitsLength,
    #[serde(default, rename = "@FontStyle")]
    pub font_style: Option<ShapeFontStyleType>,
    #[serde(default, rename = "@Locked")]
    pub locked: Option<bool>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@TheZ")]
    pub the_z: Option<i32>,
    #[serde(default, rename = "@TheT")]
    pub the_t: Option<i32>,
    #[serde(default, rename = "@TheC")]
    pub the_c: Option<i32>,
    #[serde(rename = "@Points")]
    pub points: String,
    #[serde(default, rename = "Transform")]
    pub transform: Option<AffineTransform>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl Polygon {
    pub fn default_stroke_width_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
    pub fn default_font_size_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Polyline {
    #[serde(default, rename = "@FillColor")]
    pub fill_color: Option<i32>,
    #[serde(default, rename = "@FillRule")]
    pub fill_rule: Option<ShapeFillRuleType>,
    #[serde(default, rename = "@StrokeColor")]
    pub stroke_color: Option<i32>,
    #[serde(default, rename = "@StrokeWidth")]
    pub stroke_width: Option<f32>,
    #[serde(
        default = "Polyline::default_stroke_width_unit",
        rename = "@StrokeWidthUnit"
    )]
    pub stroke_width_unit: UnitsLength,
    #[serde(default, rename = "@StrokeDashArray")]
    pub stroke_dash_array: Option<String>,
    #[serde(default, rename = "@Text")]
    pub text: Option<String>,
    #[serde(default, rename = "@FontFamily")]
    pub font_family: Option<FontFamilyType>,
    #[serde(default, rename = "@FontSize")]
    pub font_size: Option<i32>,
    #[serde(default = "Polyline::default_font_size_unit", rename = "@FontSizeUnit")]
    pub font_size_unit: UnitsLength,
    #[serde(default, rename = "@FontStyle")]
    pub font_style: Option<ShapeFontStyleType>,
    #[serde(default, rename = "@Locked")]
    pub locked: Option<bool>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@TheZ")]
    pub the_z: Option<i32>,
    #[serde(default, rename = "@TheT")]
    pub the_t: Option<i32>,
    #[serde(default, rename = "@TheC")]
    pub the_c: Option<i32>,
    #[serde(rename = "@Points")]
    pub points: String,
    #[serde(default, rename = "@MarkerStart")]
    pub marker_start: Option<MarkerType>,
    #[serde(default, rename = "@MarkerEnd")]
    pub marker_end: Option<MarkerType>,
    #[serde(default, rename = "Transform")]
    pub transform: Option<AffineTransform>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl Polyline {
    pub fn default_stroke_width_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
    pub fn default_font_size_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Project {
    #[serde(default, rename = "@Name")]
    pub name: Option<String>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "ExperimenterRef")]
    pub experimenter_ref: Option<AnnotationRef>,
    #[serde(default, rename = "ExperimenterGroupRef")]
    pub experimenter_group_ref: Option<AnnotationRef>,
    #[serde(default, rename = "DatasetRef")]
    pub dataset_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Roi {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Name")]
    pub name: Option<String>,
    #[serde(rename = "Union")]
    pub union: Option<RoiUnion>,
    #[serde(rename = "AnnotationRef")]
    pub annotation_ref: Option<AnnotationRef>,
    #[serde(rename = "Description")]
    pub description: Option<String>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Reagent {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Name")]
    pub name: Option<String>,
    #[serde(default, rename = "@ReagentIdentifier")]
    pub reagent_identifier: Option<String>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Rectangle {
    #[serde(default, rename = "@FillColor")]
    pub fill_color: Option<i32>,
    #[serde(default, rename = "@FillRule")]
    pub fill_rule: Option<ShapeFillRuleType>,
    #[serde(default, rename = "@StrokeColor")]
    pub stroke_color: Option<i32>,
    #[serde(default, rename = "@StrokeWidth")]
    pub stroke_width: Option<f32>,
    #[serde(
        default = "Rectangle::default_stroke_width_unit",
        rename = "@StrokeWidthUnit"
    )]
    pub stroke_width_unit: UnitsLength,
    #[serde(default, rename = "@StrokeDashArray")]
    pub stroke_dash_array: Option<String>,
    #[serde(default, rename = "@Text")]
    pub text: Option<String>,
    #[serde(default, rename = "@FontFamily")]
    pub font_family: Option<FontFamilyType>,
    #[serde(default, rename = "@FontSize")]
    pub font_size: Option<i32>,
    #[serde(
        default = "Rectangle::default_font_size_unit",
        rename = "@FontSizeUnit"
    )]
    pub font_size_unit: UnitsLength,
    #[serde(default, rename = "@FontStyle")]
    pub font_style: Option<ShapeFontStyleType>,
    #[serde(default, rename = "@Locked")]
    pub locked: Option<bool>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@TheZ")]
    pub the_z: Option<i32>,
    #[serde(default, rename = "@TheT")]
    pub the_t: Option<i32>,
    #[serde(default, rename = "@TheC")]
    pub the_c: Option<i32>,
    #[serde(rename = "@X")]
    pub x: f32,
    #[serde(rename = "@Y")]
    pub y: f32,
    #[serde(rename = "@Width")]
    pub width: f32,
    #[serde(rename = "@Height")]
    pub height: f32,
    #[serde(default, rename = "Transform")]
    pub transform: Option<AffineTransform>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl Rectangle {
    pub fn default_stroke_width_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
    pub fn default_font_size_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Rights {
    #[serde(default, rename = "RightsHolder")]
    pub rights_holder: Option<String>,
    #[serde(default, rename = "RightsHeld")]
    pub rights_held: Option<String>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RoiUnion {
    #[serde(default, rename = "ShapeGroup")]
    pub shape_group: Vec<ShapeGroup>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Screen {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Name")]
    pub name: Option<String>,
    #[serde(default, rename = "@ProtocolIdentifier")]
    pub protocol_identifier: Option<String>,
    #[serde(default, rename = "@ProtocolDescription")]
    pub protocol_description: Option<String>,
    #[serde(default, rename = "@ReagentSetDescription")]
    pub reagent_set_description: Option<String>,
    #[serde(default, rename = "@ReagentSetIdentifier")]
    pub reagent_set_identifier: Option<String>,
    #[serde(default, rename = "@Type")]
    pub r#type: Option<String>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "Reagent")]
    pub reagent: Vec<Reagent>,
    #[serde(default, rename = "PlateRef")]
    pub plate_ref: Vec<AnnotationRef>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ShapeType {
    #[serde(default, rename = "@FillColor")]
    pub fill_color: Option<i32>,
    #[serde(default, rename = "@FillRule")]
    pub fill_rule: Option<ShapeFillRuleType>,
    #[serde(default, rename = "@StrokeColor")]
    pub stroke_color: Option<i32>,
    #[serde(default, rename = "@StrokeWidth")]
    pub stroke_width: Option<f32>,
    #[serde(
        default = "ShapeType::default_stroke_width_unit",
        rename = "@StrokeWidthUnit"
    )]
    pub stroke_width_unit: UnitsLength,
    #[serde(default, rename = "@StrokeDashArray")]
    pub stroke_dash_array: Option<String>,
    #[serde(default, rename = "@Text")]
    pub text: Option<String>,
    #[serde(default, rename = "@FontFamily")]
    pub font_family: Option<FontFamilyType>,
    #[serde(default, rename = "@FontSize")]
    pub font_size: Option<i32>,
    #[serde(
        default = "ShapeType::default_font_size_unit",
        rename = "@FontSizeUnit"
    )]
    pub font_size_unit: UnitsLength,
    #[serde(default, rename = "@FontStyle")]
    pub font_style: Option<ShapeFontStyleType>,
    #[serde(default, rename = "@Locked")]
    pub locked: Option<bool>,
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@TheZ")]
    pub the_z: Option<i32>,
    #[serde(default, rename = "@TheT")]
    pub the_t: Option<i32>,
    #[serde(default, rename = "@TheC")]
    pub the_c: Option<i32>,
    #[serde(default, rename = "Transform")]
    pub transform: Option<AffineTransform>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl ShapeType {
    pub fn default_stroke_width_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
    pub fn default_font_size_unit() -> UnitsLength {
        UnitsLength::Pixel
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ShapeFillRuleType {
    #[serde(rename = "EvenOdd")]
    EvenOdd,
    #[serde(rename = "NonZero")]
    NonZero,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ShapeFontStyleType {
    #[serde(rename = "Bold")]
    Bold,
    #[serde(rename = "BoldItalic")]
    BoldItalic,
    #[serde(rename = "Italic")]
    Italic,
    #[serde(rename = "Normal")]
    Normal,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ShapeGroup {
    #[serde(rename = "Rectangle")]
    Rectangle(Rectangle),
    #[serde(rename = "Mask")]
    Mask(Mask),
    #[serde(rename = "Point")]
    Point(Label),
    #[serde(rename = "Ellipse")]
    Ellipse(Ellipse),
    #[serde(rename = "Line")]
    Line(Line),
    #[serde(rename = "Polyline")]
    Polyline(Polyline),
    #[serde(rename = "Polygon")]
    Polygon(Polygon),
    #[serde(rename = "Label")]
    Label(Label),
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct StageLabel {
    #[serde(rename = "@Name")]
    pub name: String,
    #[serde(default, rename = "@X")]
    pub x: Option<f32>,
    #[serde(default = "StageLabel::default_x_unit", rename = "@XUnit")]
    pub x_unit: UnitsLength,
    #[serde(default, rename = "@Y")]
    pub y: Option<f32>,
    #[serde(default = "StageLabel::default_y_unit", rename = "@YUnit")]
    pub y_unit: UnitsLength,
    #[serde(default, rename = "@Z")]
    pub z: Option<f32>,
    #[serde(default = "StageLabel::default_z_unit", rename = "@ZUnit")]
    pub z_unit: UnitsLength,
}
impl StageLabel {
    pub fn default_x_unit() -> UnitsLength {
        UnitsLength::um
    }
    pub fn default_y_unit() -> UnitsLength {
        UnitsLength::um
    }
    pub fn default_z_unit() -> UnitsLength {
        UnitsLength::um
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct StructuredAnnotations {
    #[serde(default, rename = "$value")]
    pub content: Option<StructuredAnnotationsContent>,
}
#[allow(clippy::enum_variant_names)]
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum StructuredAnnotationsContent {
    #[serde(rename = "XMLAnnotation")]
    XmlAnnotation(XmlAnnotation),
    #[serde(rename = "FileAnnotation")]
    FileAnnotation(FileAnnotation),
    #[serde(rename = "ListAnnotation")]
    ListAnnotation(Annotation),
    #[serde(rename = "LongAnnotation")]
    LongAnnotation(LongAnnotation),
    #[serde(rename = "DoubleAnnotation")]
    DoubleAnnotation(DoubleAnnotation),
    #[serde(rename = "CommentAnnotation")]
    CommentAnnotation(CommentAnnotation),
    #[serde(rename = "BooleanAnnotation")]
    BooleanAnnotation(BooleanAnnotation),
    #[serde(rename = "TimestampAnnotation")]
    TimestampAnnotation(CommentAnnotation),
    #[serde(rename = "TagAnnotation")]
    TagAnnotation(CommentAnnotation),
    #[serde(rename = "TermAnnotation")]
    TermAnnotation(CommentAnnotation),
    #[serde(rename = "MapAnnotation")]
    MapAnnotation(MapAnnotation),
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TiffData {
    #[serde(default = "TiffData::default_ifd", rename = "@IFD")]
    pub ifd: i32,
    #[serde(default = "TiffData::default_first_z", rename = "@FirstZ")]
    pub first_z: i32,
    #[serde(default = "TiffData::default_first_t", rename = "@FirstT")]
    pub first_t: i32,
    #[serde(default = "TiffData::default_first_c", rename = "@FirstC")]
    pub first_c: i32,
    #[serde(default, rename = "@PlaneCount")]
    pub plane_count: Option<i32>,
    #[serde(default, rename = "UUID")]
    pub uuid: Option<TiffDataUuid>,
}
impl TiffData {
    pub fn default_ifd() -> i32 {
        0
    }
    pub fn default_first_z() -> i32 {
        0
    }
    pub fn default_first_t() -> i32 {
        0
    }
    pub fn default_first_c() -> i32 {
        0
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TiffDataUuid {
    #[serde(default, rename = "@FileName")]
    pub file_name: Option<String>,
    #[serde(rename = "$text")]
    pub content: String,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TransmittanceRange {
    #[serde(default, rename = "@CutIn")]
    pub cut_in: Option<f32>,
    #[serde(
        default = "TransmittanceRange::default_cut_in_unit",
        rename = "@CutInUnit"
    )]
    pub cut_in_unit: UnitsLength,
    #[serde(default, rename = "@CutOut")]
    pub cut_out: Option<f32>,
    #[serde(
        default = "TransmittanceRange::default_cut_out_unit",
        rename = "@CutOutUnit"
    )]
    pub cut_out_unit: UnitsLength,
    #[serde(default, rename = "@CutInTolerance")]
    pub cut_in_tolerance: Option<f32>,
    #[serde(
        default = "TransmittanceRange::default_cut_in_tolerance_unit",
        rename = "@CutInToleranceUnit"
    )]
    pub cut_in_tolerance_unit: UnitsLength,
    #[serde(default, rename = "@CutOutTolerance")]
    pub cut_out_tolerance: Option<f32>,
    #[serde(
        default = "TransmittanceRange::default_cut_out_tolerance_unit",
        rename = "@CutOutToleranceUnit"
    )]
    pub cut_out_tolerance_unit: UnitsLength,
    #[serde(default, rename = "@Transmittance")]
    pub transmittance: Option<f32>,
}
impl TransmittanceRange {
    pub fn default_cut_in_unit() -> UnitsLength {
        UnitsLength::m
    }
    pub fn default_cut_out_unit() -> UnitsLength {
        UnitsLength::m
    }
    pub fn default_cut_in_tolerance_unit() -> UnitsLength {
        UnitsLength::m
    }
    pub fn default_cut_out_tolerance_unit() -> UnitsLength {
        UnitsLength::m
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, FromStr, IterVariants)]
pub enum UnitsElectricPotential {
    YV,
    ZV,
    EV,
    PV,
    TV,
    GV,
    MV,
    kV,
    hV,
    daV,
    V,
    dV,
    cV,
    mV,
    #[serde(rename = "µV")]
    uV,
    nV,
    pV,
    fV,
    aV,
    zV,
    yV,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, FromStr, IterVariants)]
pub enum UnitsFrequency {
    YHz,
    ZHz,
    EHz,
    PHz,
    THz,
    GHz,
    MHz,
    kHz,
    hHz,
    daHz,
    Hz,
    dHz,
    cHz,
    mHz,
    #[serde(rename = "µHz")]
    uHz,
    nHz,
    pHz,
    fHz,
    aHz,
    zHz,
    yHz,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, FromStr, IterVariants)]
pub enum UnitsLength {
    Ym,
    Zm,
    Em,
    Pm,
    Tm,
    Gm,
    Mm,
    km,
    hm,
    dam,
    m,
    dm,
    cm,
    mm,
    #[serde(rename = "µm")]
    um,
    nm,
    pm,
    fm,
    am,
    zm,
    ym,
    #[serde(rename = "Å")]
    A,
    #[serde(rename = "thou")]
    Thou,
    #[serde(rename = "li")]
    Li,
    #[serde(rename = "in")]
    In,
    #[serde(rename = "ft")]
    Ft,
    #[serde(rename = "yd")]
    Yd,
    #[serde(rename = "mi")]
    Mi,
    #[serde(rename = "ua")]
    Ua,
    #[serde(rename = "ly")]
    Ly,
    #[serde(rename = "pc")]
    Pc,
    #[serde(rename = "pt")]
    Pt,
    #[serde(rename = "pixel")]
    Pixel,
    #[serde(rename = "reference frame")]
    ReferenceFrame,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, FromStr, IterVariants)]
pub enum UnitsPower {
    YW,
    ZW,
    EW,
    PW,
    TW,
    GW,
    MW,
    kW,
    hW,
    daW,
    W,
    dW,
    cW,
    mW,
    #[serde(rename = "µW")]
    uW,
    nW,
    pW,
    fW,
    aW,
    zW,
    yW,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, FromStr, IterVariants)]
pub enum UnitsPressure {
    YPa,
    ZPa,
    EPa,
    PPa,
    TPa,
    GPa,
    MPa,
    kPa,
    hPa,
    daPa,
    Pa,
    dPa,
    cPa,
    mPa,
    #[serde(rename = "µPa")]
    uPa,
    nPa,
    pPa,
    fPa,
    aPa,
    zPa,
    yPa,
    bar,
    Mbar,
    kbar,
    dbar,
    cbar,
    mbar,
    atm,
    psi,
    Torr,
    mTorr,
    #[serde(rename = "mm Hg")]
    mmHg,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, FromStr, IterVariants)]
pub enum UnitsTemperature {
    #[serde(rename = "°C")]
    C,
    #[serde(rename = "°F")]
    F,
    #[serde(rename = "K")]
    K,
    #[serde(rename = "°R")]
    R,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, FromStr, IterVariants)]
pub enum UnitsTime {
    Ys,
    Zs,
    Es,
    Ps,
    Ts,
    Gs,
    Ms,
    ks,
    hs,
    das,
    s,
    ds,
    cs,
    ms,
    #[serde(rename = "µs")]
    us,
    ns,
    ps,
    fs,
    r#as,
    zs,
    ys,
    min,
    h,
    d,
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Well {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(rename = "@Column")]
    pub column: i32,
    #[serde(rename = "@Row")]
    pub row: i32,
    #[serde(default, rename = "@ExternalDescription")]
    pub external_description: Option<String>,
    #[serde(default, rename = "@ExternalIdentifier")]
    pub external_identifier: Option<String>,
    #[serde(default, rename = "@Type")]
    pub r#type: Option<String>,
    #[serde(default = "Well::default_color", rename = "@Color")]
    pub color: i32,
    #[serde(default, rename = "WellSample")]
    pub well_sample: Vec<WellSample>,
    #[serde(default, rename = "ReagentRef")]
    pub reagent_ref: Option<AnnotationRef>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
}
impl Well {
    pub fn default_color() -> i32 {
        0
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct WellSample {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@PositionX")]
    pub position_x: Option<f32>,
    #[serde(
        default = "WellSample::default_position_x_unit",
        rename = "@PositionXUnit"
    )]
    pub position_x_unit: UnitsLength,
    #[serde(default, rename = "@PositionY")]
    pub position_y: Option<f32>,
    #[serde(
        default = "WellSample::default_position_y_unit",
        rename = "@PositionYUnit"
    )]
    pub position_y_unit: UnitsLength,
    #[serde(default, rename = "@Timepoint")]
    pub timepoint: Option<String>,
    #[serde(rename = "@Index")]
    pub index: i32,
    #[serde(default, rename = "ImageRef")]
    pub image_ref: Option<AnnotationRef>,
}
impl WellSample {
    pub fn default_position_x_unit() -> UnitsLength {
        UnitsLength::um
    }
    pub fn default_position_y_unit() -> UnitsLength {
        UnitsLength::um
    }
}
#[cfg_attr(feature = "python", derive(IntoPyObject))]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct XmlAnnotation {
    #[serde(rename = "@ID")]
    pub id: String,
    #[serde(default, rename = "@Namespace")]
    pub namespace: Option<String>,
    #[serde(default, rename = "@Annotator")]
    pub annotator: Option<String>,
    #[serde(default, rename = "Description")]
    pub description: Option<String>,
    #[serde(default, rename = "AnnotationRef")]
    pub annotation_ref: Vec<AnnotationRef>,
    #[serde(rename = "Value")]
    pub value: XmlAnnotationValue,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct XmlAnnotationValue;

pub trait Convert: PartialEq {
    /// conversion factor between this and SI value
    fn as_si(&self) -> Result<f64, Error>;

    /// convert a value with this unit into another unit
    fn convert(&self, unit: &Self, value: f64) -> Result<f64, Error> {
        if self == unit {
            Ok(value)
        } else {
            Ok(value * self.as_si()? / unit.as_si()?)
        }
    }
}

macro_rules! impl_enum_variants {
    ($($t:ty $(,)?)*) => {
        $(
            impl $t {
                /// all possible variants of this enum that can be constructed or converted into
                pub fn variants() -> Vec<Self> {
                    Self::iter().collect::<Vec<_>>()
                }
            }
        )*
    };
}

impl_enum_variants!(
    UnitsElectricPotential,
    UnitsFrequency,
    UnitsLength,
    UnitsPower,
    UnitsPressure,
    UnitsTemperature,
    UnitsTime,
);

impl Convert for UnitsElectricPotential {
    fn as_si(&self) -> Result<f64, Error> {
        match self {
            UnitsElectricPotential::YV => Ok(1e24),
            UnitsElectricPotential::ZV => Ok(1e21),
            UnitsElectricPotential::EV => Ok(1e18),
            UnitsElectricPotential::PV => Ok(1e15),
            UnitsElectricPotential::TV => Ok(1e12),
            UnitsElectricPotential::GV => Ok(1e9),
            UnitsElectricPotential::MV => Ok(1e6),
            UnitsElectricPotential::kV => Ok(1e3),
            UnitsElectricPotential::hV => Ok(1e2),
            UnitsElectricPotential::daV => Ok(1e1),
            UnitsElectricPotential::V => Ok(1e0),
            UnitsElectricPotential::dV => Ok(1e-1),
            UnitsElectricPotential::cV => Ok(1e-2),
            UnitsElectricPotential::mV => Ok(1e-3),
            UnitsElectricPotential::uV => Ok(1e-6),
            UnitsElectricPotential::nV => Ok(1e-9),
            UnitsElectricPotential::pV => Ok(1e-12),
            UnitsElectricPotential::fV => Ok(1e-15),
            UnitsElectricPotential::aV => Ok(1e-18),
            UnitsElectricPotential::zV => Ok(1e-21),
            UnitsElectricPotential::yV => Ok(1e-24),
        }
    }
}

impl Convert for UnitsFrequency {
    fn as_si(&self) -> Result<f64, Error> {
        match self {
            UnitsFrequency::YHz => Ok(1e24),
            UnitsFrequency::ZHz => Ok(1e21),
            UnitsFrequency::EHz => Ok(1e18),
            UnitsFrequency::PHz => Ok(1e15),
            UnitsFrequency::THz => Ok(1e12),
            UnitsFrequency::GHz => Ok(1e9),
            UnitsFrequency::MHz => Ok(1e6),
            UnitsFrequency::kHz => Ok(1e3),
            UnitsFrequency::hHz => Ok(1e2),
            UnitsFrequency::daHz => Ok(1e1),
            UnitsFrequency::Hz => Ok(1e0),
            UnitsFrequency::dHz => Ok(1e-1),
            UnitsFrequency::cHz => Ok(1e-2),
            UnitsFrequency::mHz => Ok(1e-3),
            UnitsFrequency::uHz => Ok(1e-6),
            UnitsFrequency::nHz => Ok(1e-9),
            UnitsFrequency::pHz => Ok(1e-12),
            UnitsFrequency::fHz => Ok(1e-15),
            UnitsFrequency::aHz => Ok(1e-18),
            UnitsFrequency::zHz => Ok(1e-21),
            UnitsFrequency::yHz => Ok(1e-24),
        }
    }
}

impl Convert for UnitsLength {
    fn as_si(&self) -> Result<f64, Error> {
        match self {
            UnitsLength::Ym => Ok(1e24),
            UnitsLength::Zm => Ok(1e21),
            UnitsLength::Em => Ok(1e18),
            UnitsLength::Pm => Ok(1e15),
            UnitsLength::Tm => Ok(1e12),
            UnitsLength::Gm => Ok(1e9),
            UnitsLength::Mm => Ok(1e6),
            UnitsLength::km => Ok(1e3),
            UnitsLength::hm => Ok(1e2),
            UnitsLength::dam => Ok(1e1),
            UnitsLength::m => Ok(1e0),
            UnitsLength::dm => Ok(1e-1),
            UnitsLength::cm => Ok(1e-2),
            UnitsLength::mm => Ok(1e-3),
            UnitsLength::um => Ok(1e-6),
            UnitsLength::nm => Ok(1e-9),
            UnitsLength::pm => Ok(1e-12),
            UnitsLength::fm => Ok(1e-15),
            UnitsLength::am => Ok(1e-18),
            UnitsLength::zm => Ok(1e-21),
            UnitsLength::ym => Ok(1e-24),
            UnitsLength::A => Ok(1e-10),
            UnitsLength::Thou => Ok(2.54e-5),
            UnitsLength::Li => Ok(5e2),
            UnitsLength::In => Ok(2.54e-2),
            UnitsLength::Ft => Ok(3.05e-1),
            UnitsLength::Yd => Ok(9.14e-1),
            UnitsLength::Mi => Ok(1.609344e3),
            UnitsLength::Ua => Ok(1.496e11),
            UnitsLength::Ly => Ok(9.461e15),
            UnitsLength::Pc => Ok(3.086e16),
            UnitsLength::Pt => Ok(3.52778e-4),
            UnitsLength::Pixel => Err(Error::SizeOfUnknown("pixel".to_string())),
            UnitsLength::ReferenceFrame => Err(Error::SizeOfUnknown("reference frame".to_string())),
        }
    }
}

impl Convert for UnitsPower {
    fn as_si(&self) -> Result<f64, Error> {
        match self {
            UnitsPower::YW => Ok(1e24),
            UnitsPower::ZW => Ok(1e21),
            UnitsPower::EW => Ok(1e18),
            UnitsPower::PW => Ok(1e15),
            UnitsPower::TW => Ok(1e12),
            UnitsPower::GW => Ok(1e9),
            UnitsPower::MW => Ok(1e6),
            UnitsPower::kW => Ok(1e3),
            UnitsPower::hW => Ok(1e2),
            UnitsPower::daW => Ok(1e1),
            UnitsPower::W => Ok(1e0),
            UnitsPower::dW => Ok(1e-1),
            UnitsPower::cW => Ok(1e-2),
            UnitsPower::mW => Ok(1e-3),
            UnitsPower::uW => Ok(1e-6),
            UnitsPower::nW => Ok(1e-9),
            UnitsPower::pW => Ok(1e-12),
            UnitsPower::fW => Ok(1e-15),
            UnitsPower::aW => Ok(1e-18),
            UnitsPower::zW => Ok(1e-21),
            UnitsPower::yW => Ok(1e-24),
        }
    }
}

impl Convert for UnitsPressure {
    fn as_si(&self) -> Result<f64, Error> {
        match self {
            UnitsPressure::YPa => Ok(1e24),
            UnitsPressure::ZPa => Ok(1e21),
            UnitsPressure::EPa => Ok(1e18),
            UnitsPressure::PPa => Ok(1e15),
            UnitsPressure::TPa => Ok(1e12),
            UnitsPressure::GPa => Ok(1e9),
            UnitsPressure::MPa => Ok(1e6),
            UnitsPressure::kPa => Ok(1e3),
            UnitsPressure::hPa => Ok(1e2),
            UnitsPressure::daPa => Ok(1e1),
            UnitsPressure::Pa => Ok(1e0),
            UnitsPressure::dPa => Ok(1e-1),
            UnitsPressure::cPa => Ok(1e-2),
            UnitsPressure::mPa => Ok(1e-3),
            UnitsPressure::uPa => Ok(1e-6),
            UnitsPressure::nPa => Ok(1e-9),
            UnitsPressure::pPa => Ok(1e-12),
            UnitsPressure::fPa => Ok(1e-15),
            UnitsPressure::aPa => Ok(1e-18),
            UnitsPressure::zPa => Ok(1e-21),
            UnitsPressure::yPa => Ok(1e-24),
            UnitsPressure::bar => Ok(1e5),
            UnitsPressure::Mbar => Ok(1e11),
            UnitsPressure::kbar => Ok(1e8),
            UnitsPressure::dbar => Ok(1e4),
            UnitsPressure::cbar => Ok(1e3),
            UnitsPressure::mbar => Ok(1e2),
            UnitsPressure::atm => Ok(1.01325e5),
            UnitsPressure::psi => Ok(6.89476e3),
            UnitsPressure::Torr => Ok(1.33322e3),
            UnitsPressure::mTorr => Ok(1.33322),
            UnitsPressure::mmHg => Ok(1.33322e2),
        }
    }
}

impl Convert for UnitsTemperature {
    fn as_si(&self) -> Result<f64, Error> {
        match self {
            UnitsTemperature::C => Err(Error::TemparatureConversion),
            UnitsTemperature::F => Err(Error::TemparatureConversion),
            UnitsTemperature::K => Ok(1e1),
            UnitsTemperature::R => Ok(5f64 / 9f64),
        }
    }

    fn convert(&self, unit: &Self, value: f64) -> Result<f64, Error> {
        match (self, unit) {
            (UnitsTemperature::F, UnitsTemperature::C) => Ok((value - 32.) * 5. / 9.),
            (UnitsTemperature::K, UnitsTemperature::C) => Ok(value - 273.15),
            (UnitsTemperature::R, UnitsTemperature::C) => Ok((value * 5. / 9.) - 273.15),
            (UnitsTemperature::C, UnitsTemperature::F) => Ok((value * 9. / 5.) + 32.),
            (UnitsTemperature::K, UnitsTemperature::F) => Ok((value * 9. / 5.) - 459.67),
            (UnitsTemperature::R, UnitsTemperature::F) => Ok(value - 459.67),
            (UnitsTemperature::C, UnitsTemperature::K) => Ok(value + 273.15),
            (UnitsTemperature::F, UnitsTemperature::K) => Ok((value + 459.67) * 5. / 9.),
            (UnitsTemperature::R, UnitsTemperature::K) => Ok(value * 5. / 9.),
            (UnitsTemperature::C, UnitsTemperature::R) => Ok((value + 273.15) * 9. / 5.),
            (UnitsTemperature::F, UnitsTemperature::R) => Ok(value + 459.67),
            (UnitsTemperature::K, UnitsTemperature::R) => Ok(value * 9. / 5.),
            _ => Ok(value),
        }
    }
}

impl Convert for UnitsTime {
    fn as_si(&self) -> Result<f64, Error> {
        match self {
            UnitsTime::Ys => Ok(1e24),
            UnitsTime::Zs => Ok(1e21),
            UnitsTime::Es => Ok(1e18),
            UnitsTime::Ps => Ok(1e15),
            UnitsTime::Ts => Ok(1e12),
            UnitsTime::Gs => Ok(1e9),
            UnitsTime::Ms => Ok(1e6),
            UnitsTime::ks => Ok(1e3),
            UnitsTime::hs => Ok(1e2),
            UnitsTime::das => Ok(1e1),
            UnitsTime::s => Ok(1e0),
            UnitsTime::ds => Ok(1e-1),
            UnitsTime::cs => Ok(1e-2),
            UnitsTime::ms => Ok(1e-3),
            UnitsTime::us => Ok(1e-6),
            UnitsTime::ns => Ok(1e-9),
            UnitsTime::ps => Ok(1e-12),
            UnitsTime::fs => Ok(1e-15),
            UnitsTime::r#as => Ok(1e-18),
            UnitsTime::zs => Ok(1e-21),
            UnitsTime::ys => Ok(1e-24),
            UnitsTime::min => Ok(6e1),
            UnitsTime::h => Ok(3.6e2),
            UnitsTime::d => Ok(8.64e4),
        }
    }
}
