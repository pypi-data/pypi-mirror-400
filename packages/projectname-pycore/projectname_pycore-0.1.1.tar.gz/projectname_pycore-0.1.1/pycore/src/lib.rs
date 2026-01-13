#![deny(
    clippy::disallowed_methods,
    clippy::disallowed_types,
    clippy::disallowed_macros
)]

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

use pyo3::exceptions::{PyOverflowError, PyTypeError, PyValueError};
use pyo3::types::{PyBool, PyByteArray, PyBytes, PyList, PyLong, PySequence, PyString, PyTuple};

#[cfg(test)]
use std::sync::atomic::{AtomicUsize, Ordering};

/// Operaciones soportadas por `core_process_batch`.
///
/// Se aceptan desde Python como tuplas de tres elementos con la forma
/// `(operacion, a, b)`, donde `operacion` es una cadena (`"add"`, `"subtract"`,
/// etc.) y `a`/`b` son enteros.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Operation {
    Add(i64, i64),
    Subtract(i64, i64),
}

const SUPPORTED_OPERATIONS: [&str; 7] = ["+", "-", "add", "resta", "sub", "subtract", "sum"];

#[cfg(test)]
static OPERATION_EVALS: AtomicUsize = AtomicUsize::new(0);

impl Operation {
    fn evaluate(self) -> PyResult<i64> {
        #[cfg(test)]
        OPERATION_EVALS.fetch_add(1, Ordering::SeqCst);

        match self {
            Self::Add(a, b) => a
                .checked_add(b)
                .ok_or_else(|| PyOverflowError::new_err("Overflow en suma")),
            Self::Subtract(a, b) => a
                .checked_sub(b)
                .ok_or_else(|| PyOverflowError::new_err("Overflow en resta")),
        }
    }
}

impl<'a> FromPyObject<'a> for Operation {
    fn extract(obj: &'a PyAny) -> PyResult<Self> {
        let seq = obj.downcast::<PySequence>()?;

        if seq.len()? != 3 {
            return Err(PyValueError::new_err(
                "La operación debe ser una tupla (operacion, a, b)",
            ));
        }

        let operation = seq
            .get_item(0)?
            .downcast::<pyo3::types::PyString>()
            .map_err(|_| PyValueError::new_err("La operación debe ser una cadena"))?
            .to_str()?;
        // Los booleanos no son operandos válidos para mantener la coherencia con
        // `materialize_and_validate_batch`, donde también se excluyen.
        let raw_a = seq.get_item(1)?;
        if raw_a.downcast::<PyBool>().is_ok() {
            return Err(PyValueError::new_err(
                "Los operandos de la operación deben ser enteros (int, no bool) en las posiciones 1 y 2",
            ));
        }
        let a: i64 = raw_a
            .extract()
            .map_err(|_| PyValueError::new_err("Los operandos deben ser enteros"))?;

        let raw_b = seq.get_item(2)?;
        if raw_b.downcast::<PyBool>().is_ok() {
            return Err(PyValueError::new_err(
                "Los operandos de la operación deben ser enteros (int, no bool) en las posiciones 1 y 2",
            ));
        }
        let b: i64 = raw_b
            .extract()
            .map_err(|_| PyValueError::new_err("Los operandos deben ser enteros"))?;

        match operation {
            "add" | "sum" | "+" => Ok(Self::Add(a, b)),
            "subtract" | "sub" | "resta" | "-" => Ok(Self::Subtract(a, b)),
            _ => Err(PyValueError::new_err(format!(
                "Operación no soportada: {operation}"
            ))),
        }
    }
}

fn resolve_operation_alias(op_name: &str) -> PyResult<&'static str> {
    match op_name.to_lowercase().as_str() {
        "add" | "sum" | "+" => Ok("add"),
        "subtract" | "sub" | "resta" | "-" => Ok("subtract"),
        _ => Err(PyValueError::new_err(format!(
            "Operación no soportada. Usa una de: {}",
            SUPPORTED_OPERATIONS.join(", ")
        ))),
    }
}

fn normalize_alias_tuple(operation: &Bound<'_, PyAny>) -> PyResult<(String, i64, i64)> {
    let seq = operation.downcast::<PySequence>()?;

    let op_name_item = seq.get_item(0)?;
    let op_name = op_name_item
        .downcast::<pyo3::types::PyString>()
        .map_err(|_| PyValueError::new_err("La operación debe ser una cadena"))?
        .to_str()?;

    let canonical = resolve_operation_alias(op_name)?;

    let a: i64 = seq
        .get_item(1)?
        .extract()
        .map_err(|_| PyValueError::new_err("Los operandos deben ser enteros"))?;
    let b: i64 = seq
        .get_item(2)?
        .extract()
        .map_err(|_| PyValueError::new_err("Los operandos deben ser enteros"))?;

    Ok((canonical.to_string(), a, b))
}

fn call_executor_with_chunk(
    py: Python<'_>,
    executor: &Bound<'_, PyAny>,
    chunk: &[(String, i64, i64)],
) -> PyResult<Vec<i64>> {
    let py_chunk = PyList::new_bound(
        py,
        chunk
            .iter()
            .map(|(op, a, b)| {
                PyTuple::new_bound(
                    py,
                    [
                        op.as_str().into_py(py),
                        (*a).into_py(py),
                        (*b).into_py(py),
                    ],
                )
            }),
    );

    executor.call1((py_chunk,))?.extract()
}

fn normalize_operation_from_py(operation: &Bound<'_, PyAny>) -> PyResult<Operation> {
    let seq = operation.downcast::<PySequence>()?;

    let op_name = seq
        .get_item(0)?
        .downcast::<pyo3::types::PyString>()
        .map_err(|_| PyValueError::new_err("La operación debe ser una cadena"))?
        .to_str()?
        .to_lowercase();

    let raw_a = seq.get_item(1)?;
    if raw_a.downcast::<PyBool>().is_ok() {
        return Err(PyValueError::new_err(
            "Los operandos de la operación deben ser enteros (int, no bool) en las posiciones 1 y 2",
        ));
    }
    let a: i64 = raw_a
        .extract()
        .map_err(|_| PyValueError::new_err("Los operandos deben ser enteros"))?;

    let raw_b = seq.get_item(2)?;
    if raw_b.downcast::<PyBool>().is_ok() {
        return Err(PyValueError::new_err(
            "Los operandos de la operación deben ser enteros (int, no bool) en las posiciones 1 y 2",
        ));
    }
    let b: i64 = raw_b
        .extract()
        .map_err(|_| PyValueError::new_err("Los operandos deben ser enteros"))?;

    match op_name.as_str() {
        "add" | "sum" | "+" => Ok(Operation::Add(a, b)),
        "subtract" | "sub" | "resta" | "-" => Ok(Operation::Subtract(a, b)),
        _ => Err(PyValueError::new_err(format!(
            "Operación no soportada. Usa una de: {}",
            SUPPORTED_OPERATIONS.join(", ")
        ))),
    }
}

/// Suma dos enteros como función de ejemplo de PyCore y PyO3.
///
/// Este es el recorrido mínimo del roadmap: dos `i64` entran y se
/// devuelve su suma para exponerla fácilmente a Python. Se devuelve un
/// `PyOverflowError` si la operación desborda.
#[pyfunction]
// Primer núcleo expuesto a Python: sirve como referencia para la fase 2
// del roadmap y para futuros núcleos.
pub fn core_add(a: i64, b: i64) -> PyResult<i64> {
    a.checked_add(b)
        .ok_or_else(|| PyOverflowError::new_err("Overflow en suma"))
}

/// Suma una lista de pares de enteros en una sola llamada.
///
/// Igual que en `core_add`, se devuelve un `PyOverflowError` si alguna suma
/// desborda.
pub fn core_add_batch_into(pairs: &[(i64, i64)], resultados: &mut Vec<i64>) -> PyResult<()> {
    resultados.clear();
    resultados.reserve(pairs.len());

    for (a, b) in pairs {
        resultados.push(
            a.checked_add(*b)
                .ok_or_else(|| PyOverflowError::new_err("Overflow en suma"))?,
        );
    }

    Ok(())
}

#[pyfunction]
pub fn core_add_batch(pairs: Vec<(i64, i64)>) -> PyResult<Vec<i64>> {
    let mut resultados = Vec::with_capacity(pairs.len());
    core_add_batch_into(&pairs, &mut resultados)?;
    Ok(resultados)
}

/// Procesa un lote mixto de operaciones en un solo recorrido.
///
/// Cada operación se evalúa en el orden de entrada y se devuelve un vector con
/// los resultados correspondientes.
pub fn core_process_batch_into(
    operations: &[Operation],
    resultados: &mut Vec<i64>,
) -> PyResult<()> {
    resultados.clear();
    resultados.reserve(operations.len());

    for operation in operations {
        resultados.push(operation.evaluate()?);
    }

    Ok(())
}

#[pyfunction]
pub fn core_process_batch(operations: Vec<Operation>) -> PyResult<Vec<i64>> {
    let mut resultados = Vec::with_capacity(operations.len());
    core_process_batch_into(&operations, &mut resultados)?;
    Ok(resultados)
}

#[pyfunction]
pub fn normalize_and_process_batch(
    py: Python<'_>,
    validated_batch: Vec<PyObject>,
    batch_size: Option<usize>,
) -> PyResult<Vec<i64>> {
    if let Some(0) = batch_size {
        return Err(PyValueError::new_err(
            "batch_size debe ser un entero positivo o None",
        ));
    }

    if validated_batch.is_empty() {
        return Ok(Vec::new());
    }

    let mut operations = Vec::with_capacity(validated_batch.len());
    for operation in validated_batch {
        let bound = operation.bind(py);
        operations.push(normalize_operation_from_py(&bound)?);
    }

    let chunk_size = batch_size.unwrap_or(operations.len());
    let mut buffer = Vec::new();
    let mut resultados = Vec::with_capacity(operations.len());

    if chunk_size >= operations.len() {
        core_process_batch_into(&operations, &mut resultados)?;
        return Ok(resultados);
    }

    for chunk in operations.chunks(chunk_size) {
        core_process_batch_into(chunk, &mut buffer)?;
        resultados.extend_from_slice(&buffer);
    }

    Ok(resultados)
}

#[pyfunction]
#[pyo3(signature = (validated_batch, executor, batch_size=None))]
pub fn normalize_and_process_batch_with_executor(
    py: Python<'_>,
    validated_batch: &Bound<'_, PyAny>,
    executor: &Bound<'_, PyAny>,
    batch_size: Option<usize>,
) -> PyResult<Vec<i64>> {
    if let Some(0) = batch_size {
        return Err(PyValueError::new_err(
            "batch_size debe ser un entero positivo o None",
        ));
    }

    if validated_batch.is_instance_of::<PyString>()
        || validated_batch.is_instance_of::<PyBytes>()
        || validated_batch.is_instance_of::<PyByteArray>()
    {
        return Err(PyTypeError::new_err(
            "Los datos brutos deben ser un iterable de operaciones, no una cadena",
        ));
    }

    let iterator = validated_batch
        .iter()
        .map_err(|_| PyTypeError::new_err("Los datos brutos deben ser un iterable"))?;

    let mut normalized_batch: Vec<(String, i64, i64)> = Vec::new();
    for operation in iterator {
        normalized_batch.push(normalize_alias_tuple(&operation?)?);
    }

    if normalized_batch.is_empty() {
        return Ok(Vec::new());
    }

    let chunk_size = batch_size.unwrap_or(normalized_batch.len());
    if chunk_size >= normalized_batch.len() {
        return call_executor_with_chunk(py, executor, &normalized_batch);
    }

    let mut resultados: Vec<i64> = Vec::with_capacity(normalized_batch.len());
    for chunk in normalized_batch.chunks(chunk_size) {
        resultados.extend(call_executor_with_chunk(py, executor, chunk)?);
    }

    Ok(resultados)
}

#[pyfunction]
pub fn materialize_and_validate_pairs(raw_pairs: &Bound<'_, PyAny>) -> PyResult<Vec<(i64, i64)>> {
    if raw_pairs.is_instance_of::<PyString>()
        || raw_pairs.is_instance_of::<PyBytes>()
        || raw_pairs.is_instance_of::<PyByteArray>()
    {
        return Err(PyTypeError::new_err(
            "Los pares deben venir en un iterable, no en una cadena",
        ));
    }

    let iterator = raw_pairs
        .iter()
        .map_err(|_| PyTypeError::new_err("Los pares deben ser un iterable"))?;

    let mut pairs: Vec<Bound<'_, PyAny>> = Vec::new();
    for pair in iterator {
        pairs.push(pair?);
    }

    if pairs.is_empty() {
        return Ok(Vec::new());
    }

    let mut validated_pairs: Vec<(i64, i64)> = Vec::with_capacity(pairs.len());

    for pair in pairs {
        if pair.is_instance_of::<PyString>()
            || pair.is_instance_of::<PyBytes>()
            || pair.is_instance_of::<PyByteArray>()
        {
            return Err(PyTypeError::new_err(
                "Cada elemento debe ser una secuencia de dos enteros",
            ));
        }

        let seq = pair.downcast::<PySequence>().map_err(|_| {
            PyTypeError::new_err("Cada elemento debe ser una secuencia de dos enteros")
        })?;

        if seq.len()? != 2 {
            return Err(PyValueError::new_err(
                "Cada elemento debe contener exactamente dos enteros",
            ));
        }

        for idx in [0, 1] {
            let value = seq.get_item(idx)?;
            if value.is_instance_of::<PyBool>() {
                return Err(PyTypeError::new_err(
                    "Los valores de cada par deben ser enteros (int, no bool)",
                ));
            }

            if value.downcast::<PyLong>().is_err() {
                return Err(PyTypeError::new_err(
                    "Los valores de cada par deben ser enteros (int, no bool)",
                ));
            }
        }

        validated_pairs.push((seq.get_item(0)?.extract()?, seq.get_item(1)?.extract()?));
    }

    Ok(validated_pairs)
}

#[pyfunction]
pub fn materialize_and_validate_batch(raw_data: &Bound<'_, PyAny>) -> PyResult<Vec<PyObject>> {
    if raw_data.is_instance_of::<PyString>()
        || raw_data.is_instance_of::<PyBytes>()
        || raw_data.is_instance_of::<PyByteArray>()
    {
        return Err(PyTypeError::new_err(
            "Los datos brutos deben ser un iterable de operaciones, no una cadena",
        ));
    }

    let iterator = raw_data
        .iter()
        .map_err(|_| PyTypeError::new_err("Los datos brutos deben ser un iterable"))?;

    let mut batch: Vec<Bound<'_, PyAny>> = Vec::new();
    for item in iterator {
        batch.push(item?);
    }

    if batch.is_empty() {
        return Ok(Vec::new());
    }

    let first_container = batch[0].get_type();

    for operation in &batch {
        if operation.is_instance_of::<PyString>()
            || operation.is_instance_of::<PyBytes>()
            || operation.is_instance_of::<PyByteArray>()
        {
            return Err(PyTypeError::new_err(
                "Cada operación debe ser una secuencia de tres elementos: (operacion, a, b)",
            ));
        }

        let seq = operation.downcast::<PySequence>().map_err(|_| {
            PyTypeError::new_err(
                "Cada operación debe ser una secuencia de tres elementos: (operacion, a, b)",
            )
        })?;

        if !operation.get_type().is(&first_container) {
            return Err(PyValueError::new_err(
                "Todas las operaciones del lote deben compartir el mismo tipo contenedor",
            ));
        }

        if seq.len()? != 3 {
            return Err(PyValueError::new_err(
                "Cada operación debe tener exactamente tres elementos: (operacion, a, b)",
            ));
        }

        let operation_name = seq.get_item(0)?;
        if operation_name.downcast::<PyString>().is_err() {
            return Err(PyTypeError::new_err(
                "La operación debe comenzar con una cadena que identifique la acción",
            ));
        }

        for idx in [1, 2] {
            let operand = seq.get_item(idx)?;
            if operand.is_instance_of::<PyBool>() {
                return Err(PyTypeError::new_err(
                    "Los operandos de la operación deben ser enteros (int, no bool) en las posiciones 1 y 2",
                ));
            }

            if operand.downcast::<PyLong>().is_err() {
                return Err(PyTypeError::new_err(
                    "Los operandos de la operación deben ser enteros (int, no bool) en las posiciones 1 y 2",
                ));
            }
        }
    }

    let py = raw_data.py();
    Ok(batch
        .into_iter()
        .map(|operation| operation.unbind().into_py(py))
        .collect())
}

/// Módulo Python generado por PyO3.
#[pymodule]
pub fn pycore(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Registro explícito del primer núcleo (referencia de la fase 2):
    // `core_add` se expone al intérprete de Python mediante `wrap_pyfunction!`.
    m.add_function(wrap_pyfunction!(core_add, m)?)?;
    m.add_function(wrap_pyfunction!(core_add_batch, m)?)?;
    m.add_function(wrap_pyfunction!(core_process_batch, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_and_process_batch, m)?)?;
    m.add_function(wrap_pyfunction!(
        normalize_and_process_batch_with_executor,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(materialize_and_validate_pairs, m)?)?;
    m.add_function(wrap_pyfunction!(materialize_and_validate_batch, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{
        core_add, core_add_batch, core_add_batch_into, core_process_batch, core_process_batch_into,
        Operation, OPERATION_EVALS,
    };
    use pyo3::exceptions::{PyOverflowError, PyValueError};
    use pyo3::prelude::*;
    use pyo3::types::PyTuple;

    fn reset_counter() {
        OPERATION_EVALS.store(0, std::sync::atomic::Ordering::SeqCst);
    }

    #[test]
    fn suma_positivos() {
        assert_eq!(core_add(2, 3).unwrap(), 5);
        assert_eq!(core_add(10, 20).unwrap(), 30);
        assert_eq!(core_add(100, 250).unwrap(), 350);
    }

    #[test]
    fn suma_negativos() {
        assert_eq!(core_add(-2, -3).unwrap(), -5);
        assert_eq!(core_add(-10, -5).unwrap(), -15);
        assert_eq!(core_add(-1, -99).unwrap(), -100);
    }

    #[test]
    fn suma_mixta() {
        assert_eq!(core_add(-10, 5).unwrap(), -5);
        assert_eq!(core_add(10, -3).unwrap(), 7);
        assert_eq!(core_add(-7, 7).unwrap(), 0);
    }

    #[test]
    fn overflow_controlado() {
        assert_eq!(core_add(i64::MAX - 1, 1).unwrap(), i64::MAX);
        assert_eq!(core_add(i64::MIN + 1, -1).unwrap(), i64::MIN);
        assert_eq!(core_add(i64::MAX - 5, -5).unwrap(), i64::MAX - 10);
        assert_eq!(core_add(i64::MIN + 5, 5).unwrap(), i64::MIN + 10);
    }

    #[test]
    fn overflow_en_core_add_devuelve_error() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let err = core_add(i64::MAX, 1).unwrap_err();
            assert!(err.is_instance_of::<PyOverflowError>(py));
            let msg: String = err
                .value(py)
                .getattr("args")
                .unwrap()
                .get_item(0)
                .unwrap()
                .extract()
                .unwrap();
            assert_eq!(msg, "Overflow en suma");
        });
    }

    #[test]
    fn suma_ceros() {
        assert_eq!(core_add(0, 0).unwrap(), 0);
        assert_eq!(core_add(5, 0).unwrap(), 5);
        assert_eq!(core_add(0, -12).unwrap(), -12);
    }

    #[test]
    fn suma_valores_grandes() {
        assert_eq!(core_add(i64::MAX - 10, 10).unwrap(), i64::MAX);
        assert_eq!(core_add(i64::MIN + 25, -25).unwrap(), i64::MIN);
        assert_eq!(core_add(i64::MAX / 2, i64::MAX / 2).unwrap(), i64::MAX - 1);
    }

    #[test]
    fn core_add_batch_cerca_de_los_limites() {
        let valores = vec![
            (i64::MAX - 2, 2),
            (i64::MIN + 3, -3),
            (i64::MAX / 3, i64::MAX / 3),
            (i64::MIN + 10, 10),
        ];
        let resultado = core_add_batch(valores).unwrap();

        assert_eq!(
            resultado,
            vec![i64::MAX, i64::MIN, (i64::MAX / 3) * 2, i64::MIN + 20]
        );
    }

    #[test]
    fn overflow_controlado_en_batch_cercano_a_los_limites() {
        let valores = vec![
            (i64::MAX - 1, -1),
            (i64::MIN + 1, 1),
            (i64::MAX - 100, 50),
            (i64::MIN + 100, -50),
        ];

        let resultado = core_add_batch(valores).unwrap();

        assert_eq!(
            resultado,
            vec![i64::MAX - 2, i64::MIN + 2, i64::MAX - 50, i64::MIN + 50]
        );
    }

    #[test]
    fn core_add_batch_into_reutiliza_buffer() {
        let valores = vec![(1, 2), (3, 4), (5, 6)];
        let mut buffer = Vec::with_capacity(valores.len());
        buffer.extend([100, 200, 300]);

        core_add_batch_into(&valores, &mut buffer).unwrap();

        assert_eq!(buffer, vec![3, 7, 11]);
        assert!(buffer.capacity() >= valores.len());

        core_add_batch_into(&[(10, -10)], &mut buffer).unwrap();
        assert_eq!(buffer, vec![0]);
    }

    #[test]
    fn overflow_en_core_add_batch_devuelve_error() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let err = core_add_batch(vec![(i64::MAX, 1)]).unwrap_err();
            assert!(err.is_instance_of::<PyOverflowError>(py));
            let msg: String = err
                .value(py)
                .getattr("args")
                .unwrap()
                .get_item(0)
                .unwrap()
                .extract()
                .unwrap();
            assert_eq!(msg, "Overflow en suma");
        });
    }

    #[test]
    fn procesa_lote_mixto_en_orden() {
        let batch = vec![
            Operation::Add(1, 2),
            Operation::Subtract(10, 4),
            Operation::Add(-3, -7),
            Operation::Subtract(-5, -5),
        ];

        let resultado = core_process_batch(batch).unwrap();

        assert_eq!(resultado, vec![3, 6, -10, 0]);
    }

    #[test]
    fn procesa_en_una_sola_pasada() {
        let batch = vec![
            Operation::Add(100, 23),
            Operation::Subtract(50, 1),
            Operation::Add(-10, 10),
            Operation::Subtract(0, 0),
        ];

        reset_counter();

        let resultado = core_process_batch(batch.clone()).unwrap();

        assert_eq!(resultado.len(), batch.len());
        assert_eq!(
            OPERATION_EVALS.load(std::sync::atomic::Ordering::SeqCst),
            batch.len()
        );
    }

    #[test]
    fn procesa_lote_grande_una_vez_por_elemento() {
        let batch: Vec<Operation> = (0..10_000).map(|i| Operation::Add(i, i + 1)).collect();

        reset_counter();
        let resultado = core_process_batch(batch.clone()).unwrap();

        assert_eq!(resultado.len(), batch.len());
        assert!(resultado
            .iter()
            .enumerate()
            .all(|(i, v)| *v == (i as i64) + (i as i64) + 1));
        assert_eq!(
            OPERATION_EVALS.load(std::sync::atomic::Ordering::SeqCst),
            batch.len()
        );
    }

    #[test]
    fn core_process_batch_into_reutiliza_buffer() {
        let batch = vec![Operation::Add(1, 2), Operation::Subtract(10, 5)];
        let mut buffer = Vec::with_capacity(batch.len());
        buffer.extend([0, 0]);

        core_process_batch_into(&batch, &mut buffer).unwrap();
        assert_eq!(buffer, vec![3, 5]);

        core_process_batch_into(&[Operation::Add(2, 2)], &mut buffer).unwrap();
        assert_eq!(buffer, vec![4]);
    }

    #[test]
    fn overflow_en_core_process_batch_devuelve_error() {
        pyo3::prepare_freethreaded_python();
        let batch = vec![Operation::Add(i64::MAX, 1), Operation::Subtract(1, 1)];

        Python::with_gil(|py| {
            let err = core_process_batch(batch).unwrap_err();
            assert!(err.is_instance_of::<PyOverflowError>(py));
            let msg: String = err
                .value(py)
                .getattr("args")
                .unwrap()
                .get_item(0)
                .unwrap()
                .extract()
                .unwrap();
            assert_eq!(msg, "Overflow en suma");
        });
    }

    #[test]
    fn overflow_en_resta_devuelve_error() {
        pyo3::prepare_freethreaded_python();
        let batch = vec![Operation::Subtract(i64::MIN, 1)];

        Python::with_gil(|py| {
            let err = core_process_batch(batch).unwrap_err();
            assert!(err.is_instance_of::<PyOverflowError>(py));
            let msg: String = err
                .value(py)
                .getattr("args")
                .unwrap()
                .get_item(0)
                .unwrap()
                .extract()
                .unwrap();
            assert_eq!(msg, "Overflow en resta");
        });
    }

    #[test]
    fn rechaza_tuplas_con_tamanos_invalidos() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let tupla_incorrecta = PyTuple::new(py, &["add".into_py(py), 1.into_py(py)]);

            let err = Operation::extract(tupla_incorrecta).unwrap_err();
            assert!(err.is_instance_of::<PyValueError>(py));
            let msg: String = err
                .value(py)
                .getattr("args")
                .unwrap()
                .get_item(0)
                .unwrap()
                .extract()
                .unwrap();
            assert_eq!(msg, "La operación debe ser una tupla (operacion, a, b)");
        });
    }

    #[test]
    fn rechaza_operaciones_invalidas_o_no_soportadas() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let operacion_no_cadena =
                PyTuple::new(py, &[1.into_py(py), 1.into_py(py), 2.into_py(py)]);
            let err = Operation::extract(operacion_no_cadena).unwrap_err();
            assert!(err.is_instance_of::<PyValueError>(py));
            let msg: String = err
                .value(py)
                .getattr("args")
                .unwrap()
                .get_item(0)
                .unwrap()
                .extract()
                .unwrap();
            assert_eq!(msg, "La operación debe ser una cadena");

            let operacion_no_valida = PyTuple::new(
                py,
                &["multiplicar".into_py(py), 1.into_py(py), 2.into_py(py)],
            );
            let err = Operation::extract(operacion_no_valida).unwrap_err();
            assert!(err.is_instance_of::<PyValueError>(py));
            let msg: String = err
                .value(py)
                .getattr("args")
                .unwrap()
                .get_item(0)
                .unwrap()
                .extract()
                .unwrap();
            assert_eq!(msg, "Operación no soportada: multiplicar");
        });
    }

    #[test]
    fn rechaza_operandos_no_enteros() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let operando_erroneo =
                PyTuple::new(py, &["add".into_py(py), "uno".into_py(py), 2.into_py(py)]);

            let err = Operation::extract(operando_erroneo).unwrap_err();
            assert!(err.is_instance_of::<PyValueError>(py));
            let msg: String = err
                .value(py)
                .getattr("args")
                .unwrap()
                .get_item(0)
                .unwrap()
                .extract()
                .unwrap();
            assert_eq!(msg, "Los operandos deben ser enteros");
        });
    }
}
