use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};
use pyo3::wrap_pyfunction;
use pyo3::PyObject;

use pycore::core_process_batch;

#[test]
fn conversion_de_operaciones_desde_objetos_python() {
    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| {
        let m = PyModule::new_bound(py, "pycore").unwrap();
        m.add_function(wrap_pyfunction!(core_process_batch, &m).unwrap())
            .unwrap();

        let lotes: Vec<PyObject> = vec![
            PyTuple::new_bound(py, &["+".into_py(py), 1.into_py(py), 2.into_py(py)]).into_py(py),
            PyList::new_bound(
                py,
                vec!["subtract".into_py(py), 5.into_py(py), 3.into_py(py)],
            )
            .into_py(py),
        ];
        let lotes = PyList::new_bound(py, lotes);

        let resultado: Vec<i64> = m
            .getattr("core_process_batch")
            .unwrap()
            .call1((lotes,))
            .unwrap()
            .extract()
            .unwrap();

        assert_eq!(resultado, vec![3, 2]);
    });
}

#[test]
fn secuencias_heterogeneas_fallan_con_pyvalueerror() {
    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| {
        let m = PyModule::new_bound(py, "pycore").unwrap();
        m.add_function(wrap_pyfunction!(core_process_batch, &m).unwrap())
            .unwrap();

        let lote_invalido: Vec<PyObject> = vec![
            PyTuple::new_bound(py, &["add".into_py(py), 1.into_py(py), 2.into_py(py)]).into_py(py),
            PyList::new_bound(py, vec!["add".into_py(py), 1.into_py(py)]).into_py(py),
        ];
        let lote_invalido = PyList::new_bound(py, lote_invalido);

        let err = m
            .getattr("core_process_batch")
            .unwrap()
            .call1((lote_invalido,))
            .unwrap_err();

        assert!(err.is_instance_of::<PyValueError>(py));
        assert!(err
            .to_string()
            .contains("La operación debe ser una tupla (operacion, a, b)"));

        let lote_con_tipos_mixtos: Vec<PyObject> = vec![
            PyTuple::new_bound(py, &["add".into_py(py), 1.into_py(py), 2.into_py(py)]).into_py(py),
            PyTuple::new_bound(py, &["add".into_py(py), 1.5.into_py(py), 2.into_py(py)])
                .into_py(py),
        ];
        let lote_con_tipos_mixtos = PyList::new_bound(py, lote_con_tipos_mixtos);

        let err = m
            .getattr("core_process_batch")
            .unwrap()
            .call1((lote_con_tipos_mixtos,))
            .unwrap_err();

        assert!(err.is_instance_of::<PyValueError>(py));
        assert!(err.to_string().contains("Los operandos deben ser enteros"));
    });
}
