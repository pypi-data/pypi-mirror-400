use opentelemetry::propagation::Extractor;
use pyo3::prelude::*;
use pyo3::types::PyDict;

pub struct PyDictCarrier<'a, 'py>(pub &'a Bound<'py, PyDict>);

impl<'a, 'py> Extractor for PyDictCarrier<'a, 'py> {
    fn get(&self, key: &str) -> Option<&str> {
        for (k, v) in self.0.iter() {
            let Ok(k_str) = k.extract::<String>() else {
                continue;
            };
            if !k_str.eq_ignore_ascii_case(key) {
                continue;
            }
            let Ok(v_str) = v.extract::<String>() else {
                continue;
            };
            return Some(Box::leak(v_str.into_boxed_str()));
        }
        None
    }

    fn keys(&self) -> Vec<&str> {
        vec![] // not usually needed
    }
}
