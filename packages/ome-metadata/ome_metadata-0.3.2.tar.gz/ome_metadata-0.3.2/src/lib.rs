#![allow(non_camel_case_types)]
pub mod ome;

pub mod error;
#[cfg(feature = "python")]
mod py;

use crate::error::Error;
pub use ome::Ome;
use quick_xml::de::from_str;
use std::str::FromStr;

impl FromStr for Ome {
    type Err = Error;

    fn from_str(s: &str) -> Result<Self, Error> {
        Ok(from_str(s)?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::read_to_string;

    macro_rules! test_read {
        ($($name:ident: $file:expr $(,)?)*) => {
            $(
                #[test]
                fn $name() -> Result<(), Error> {
                    let file = read_to_string(format!("tests/{}.xml", $file))?;
                    let _ome: Ome = file.parse()?;
                    Ok(())
                }
            )*
        };
    }

    test_read!(
        a: "YTL1849A111_2023_05_04__14_46_19_cellnr_1_track"
        b: "Experiment-2029"
        c: "test"
        d: "4-Pos_001_002"
        e: "YTL1841B2-2-1_1hr_DMSO_galinduction_1"
        f: "1xp53-01-AP1"
        g: "YTL378_JF552"
        h: "MK022_cE9_1-01-Airyscan Processing-01-Scene-2-P1"
        i: "beads_2023_05_04__19_00_22"
        j: "20230511-p53-4x-CMV-1min-4h-01-Airyscan Processing-01"
        k: "YTL1849A131_2023_05_04__13_36_36"
    );
}
