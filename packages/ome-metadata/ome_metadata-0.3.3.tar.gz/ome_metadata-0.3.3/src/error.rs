use thiserror::Error;

#[derive(Debug, Error)]
pub enum Error {
    #[error(transparent)]
    IO(#[from] std::io::Error),
    #[error(transparent)]
    SerdeXml(#[from] quick_xml::DeError),
    #[error("size of {0} is unknown")]
    SizeOfUnknown(String),
    #[error("no conversion to K by multiplication only")]
    TemparatureConversion,
}
