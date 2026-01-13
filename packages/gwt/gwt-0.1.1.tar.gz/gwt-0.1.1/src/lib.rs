//! Git Worktree CLI with better DX
//!
//! This crate is under development.

use pyo3::prelude::*;

#[pyfunction]
fn hello_world() -> String {
    "Hello, World!".to_string()
}

#[pyfunction]
fn main() {
    println!("{}", hello_world());
}

#[pymodule]
fn gwt(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_world, m)?)?;
    m.add_function(wrap_pyfunction!(main, m)?)?;
    Ok(())
}
