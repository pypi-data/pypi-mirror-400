mod reverse;

use pyo3::prelude::*;
use pyo3::types::PyType;
use crate::reverse::compress::Compressor;

#[pyclass]
struct CloudFlareEncrypt {
    #[pyo3(get, set)]
    key: String,
    compress: Compressor,
}

#[pymethods]
impl CloudFlareEncrypt {
    #[new]
    fn new(key: String) -> Self {
        let compress = Compressor::new(key.clone());
        CloudFlareEncrypt {
            key,
            compress
        }
    }


    fn encrypt(&mut self, data: String) -> PyResult<String> {

        Ok(self.compress.compress(&data))
    }


}

/// 计算两个数的和并返回字符串
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}
/// 这个模块是用 Rust 实现的 Python 模块
#[pymodule]
fn cloudflare_encrypt(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_class::<CloudFlareEncrypt>()?;
    Ok(())
}

