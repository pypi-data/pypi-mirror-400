use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};
use pyo3::wrap_pyfunction;

use pycore::{core_add, core_add_batch, core_process_batch};

#[test]
fn invocaciones_python_basicas() {
    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| {
        let m = PyModule::new_bound(py, "pycore").unwrap();
        m.add_function(wrap_pyfunction!(core_add, &m).unwrap())
            .unwrap();
        m.add_function(wrap_pyfunction!(core_add_batch, &m).unwrap())
            .unwrap();

        let suma: i64 = m
            .getattr("core_add")
            .unwrap()
            .call1((3, 4))
            .unwrap()
            .extract()
            .unwrap();
        assert_eq!(suma, 7);

        let pares = PyList::new_bound(
            py,
            vec![
                PyTuple::new_bound(py, &[1.into_py(py), 2.into_py(py)]),
                PyTuple::new_bound(py, &[5.into_py(py), 6.into_py(py)]),
            ],
        );
        let lote: Vec<i64> = m
            .getattr("core_add_batch")
            .unwrap()
            .call1((pares,))
            .unwrap()
            .extract()
            .unwrap();
        assert_eq!(lote, vec![3, 11]);
    });
}

#[test]
fn rechaza_booleanos_en_operandos_desde_python() {
    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| {
        let m = PyModule::new_bound(py, "pycore").unwrap();
        m.add_function(wrap_pyfunction!(core_process_batch, &m).unwrap())
            .unwrap();

        let mensaje =
            "Los operandos de la operación deben ser enteros (int, no bool) en las posiciones 1 y 2";

        let lote_bool_a = PyList::new_bound(
            py,
            vec![PyTuple::new_bound(
                py,
                &["add".into_py(py), true.into_py(py), 2.into_py(py)],
            )],
        );
        let err = m
            .getattr("core_process_batch")
            .unwrap()
            .call1((lote_bool_a,))
            .unwrap_err();
        assert!(err.is_instance_of::<PyValueError>(py));
        assert!(err.to_string().contains(mensaje));

        let lote_bool_b = PyList::new_bound(
            py,
            vec![PyTuple::new_bound(
                py,
                &["subtract".into_py(py), 5.into_py(py), false.into_py(py)],
            )],
        );
        let err = m
            .getattr("core_process_batch")
            .unwrap()
            .call1((lote_bool_b,))
            .unwrap_err();
        assert!(err.is_instance_of::<PyValueError>(py));
        assert!(err.to_string().contains(mensaje));
    });
}

#[test]
fn conversion_de_operaciones_y_error_pyvalueerror() {
    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| {
        let m = PyModule::new_bound(py, "pycore").unwrap();
        m.add_function(wrap_pyfunction!(core_process_batch, &m).unwrap())
            .unwrap();

        let operaciones = PyList::new_bound(
            py,
            vec![
                PyTuple::new_bound(py, &["add".into_py(py), 1.into_py(py), 2.into_py(py)]),
                PyTuple::new_bound(py, &["subtract".into_py(py), 5.into_py(py), 3.into_py(py)]),
            ],
        );
        let resultados: Vec<i64> = m
            .getattr("core_process_batch")
            .unwrap()
            .call1((operaciones,))
            .unwrap()
            .extract()
            .unwrap();
        assert_eq!(resultados, vec![3, 2]);

        let lote_heterogeneo = PyList::new_bound(
            py,
            vec![
                PyTuple::new_bound(py, &["add".into_py(py), 1.into_py(py), 2.into_py(py)]),
                PyTuple::new_bound(
                    py,
                    &["multiplicar".into_py(py), 2.into_py(py), 3.into_py(py)],
                ),
            ],
        );
        let err = m
            .getattr("core_process_batch")
            .unwrap()
            .call1((lote_heterogeneo,))
            .unwrap_err();
        assert!(err.is_instance_of::<PyValueError>(py));
        assert!(err.to_string().contains("Operación no soportada"));

        let operandos_invalidos = PyList::new_bound(
            py,
            vec![PyTuple::new_bound(
                py,
                &["add".into_py(py), "uno".into_py(py), 2.into_py(py)],
            )],
        );
        let err = m
            .getattr("core_process_batch")
            .unwrap()
            .call1((operandos_invalidos,))
            .unwrap_err();
        assert!(err.is_instance_of::<PyValueError>(py));
        assert!(err.to_string().contains("Los operandos deben ser enteros"));
    });
}
