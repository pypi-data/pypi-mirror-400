# Benchmarks de PyCore

Este directorio agrupa los benchmarks de fase 8 para los núcleos expuestos en `lib.rs`. Se basan en Criterion, con `sample_size` aumentado para obtener distribuciones más estables.

## Cómo ejecutarlos

```bash
cargo bench
```

Criterion generará los resultados en `target/criterion` y, gracias a la opción `html_reports`, también dejará un informe navegable en `target/criterion/report/index.html`.

## Cómo interpretar las métricas en relación con la fase 8

* **Tiempo medio y desviación estándar**: orientan sobre el costo de procesar lotes de distintos tamaños. Fase 8 busca optimizar estos recorridos; compara los escenarios de `core_add_batch` (vectores crecientes) para detectar si hay regresiones en la suma masiva.
* **Comparativa entre patrones de operaciones**: los escenarios de `core_process_batch` miden mezclas de sumas/restas, ráfagas en bloques y patrones pequeños repetidos. Úsalos para contrastar optimizaciones en la fase 8 que afecten al orden o a la variedad de operaciones.
* **Gráficos de regresión**: el informe HTML muestra tendencias frente a ejecuciones previas. Si tras ajustes de fase 8 los gráficos suben o el `change` porcentual es positivo, revisa posibles regresiones en los núcleos.
